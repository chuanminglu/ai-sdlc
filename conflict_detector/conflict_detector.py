"""
基于Deepseek V3的需求冲突检测器核心实现
"""
import json
import logging
import os
import configparser
import requests
import codecs
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

try:
    # 导入Deepseek API
    from deepseek_api import DeepseekAPI, DeepseekAPIException
except ImportError:
    # 自定义Deepseek API调用类
    class DeepseekAPI:
        def __init__(self, api_key: str = None, model_version: str = "v3", api_base: str = None):
            self.api_key = api_key
            self.model_version = model_version
            self.api_base = api_base or "https://api.deepseek.com/v1"
            self.model = "deepseek-chat"  # 默认模型名称
        
        def chat_completion(self, messages: List[Dict], **kwargs):
            """调用Deepseek API获取回复"""
            if not self.api_key:
                raise DeepseekAPIException("未设置API密钥，无法访问Deepseek API")
            
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                data = {
                    "model": self.model,
                    "messages": messages,
                    **kwargs
                }
                
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=kwargs.get("timeout", 60)
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise DeepseekAPIException(
                        f"API调用失败，状态码：{response.status_code}，响应：{response.text}"
                    )
            
            except requests.exceptions.RequestException as e:
                raise DeepseekAPIException(f"网络请求错误: {str(e)}")
            except Exception as e:
                raise DeepseekAPIException(f"调用Deepseek API时出错: {str(e)}")
    
    class DeepseekAPIException(Exception):
        pass

# 配置日志
log_file = "conflict_detector.log"
# 先清空日志文件并使用UTF-8编码重新创建
with codecs.open(log_file, 'w', encoding='utf-8') as f:
    pass
    
# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),  # 明确指定UTF-8编码
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger("ConflictDetector")

def load_config(config_file: str = None) -> dict:
    """
    从配置文件加载配置
    
    Args:
        config_file: 配置文件路径，如果为None则使用默认路径
    
    Returns:
        配置字典
    """
    config = {}
    
    # 默认配置文件路径
    if config_file is None:
        # 查找项目根目录的config.ini
        project_root = Path(__file__).parent.parent
        config_file = project_root / "config.ini"
    
    logger.info(f"尝试从 {config_file} 加载配置")
    
    # 检查配置文件是否存在
    if Path(config_file).exists():
        try:
            parser = configparser.ConfigParser()
            # 使用UTF-8编码读取配置文件
            with open(config_file, 'r', encoding='utf-8') as f:
                parser.read_file(f)
            
            # 读取Deepseek配置
            if 'deepseek' in parser:
                deepseek_config = parser['deepseek']
                config['api_key'] = deepseek_config.get('api_key', None)
                config['api_base'] = deepseek_config.get('api_base', "https://api.deepseek.com/v1")
                config['model'] = deepseek_config.get('model', "deepseek-chat")
                config['timeout'] = int(deepseek_config.get('timeout', "60"))
                config['max_retries'] = int(deepseek_config.get('max_retries', "3"))
                config['retry_delay'] = int(deepseek_config.get('retry_delay', "5"))
                
                logger.info(f"从配置文件加载API设置: api_base={config['api_base']}, model={config['model']}")
                if config['api_key']:
                    logger.info(f"成功加载API密钥: {config['api_key'][:5]}...")
                else:
                    logger.warning("配置文件中未找到API密钥")
            else:
                logger.warning("配置文件中未找到 [deepseek] 部分")
        
        except Exception as e:
            logger.error(f"读取配置文件 {config_file} 出错: {e}")
    else:
        logger.warning(f"配置文件 {config_file} 不存在")
    
    return config

class RequirementConflictDetector:
    """需求冲突检测器类"""
    
    # 冲突分析维度定义
    CONFLICT_DIMENSIONS = {
        "功能一致性": ["功能逻辑矛盾", "业务规则冲突", "数据定义不一致"],
        "用户权限逻辑": ["角色权限边界", "特权操作控制", "访问控制漏洞"],
        "业务流程完整性": ["流程断点检测", "异常场景覆盖", "状态转换冲突"],
        "用户体验一致性": ["交互逻辑矛盾", "界面元素冲突", "操作流程断裂"],
        "数据一致性": ["数据生命周期管理", "存储策略冲突", "格式/来源矛盾"],
        "安全合规性": ["隐私保护漏洞", "加密要求冲突", "审计日志缺失"]
    }
    
    # 严重等级定义
    SEVERITY_LEVELS = ["高", "中", "低"]
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model_version: str = "v3",
        config_file: Optional[str] = None
    ):
        """
        初始化需求冲突检测器
        
        Args:
            api_key: Deepseek API密钥，如果为None则从配置文件或环境变量读取
            model_version: 使用的模型版本，默认v3
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        # 加载配置
        config = load_config(config_file)
        
        # 设置API密钥（按优先级：直接传入 > 配置文件 > 环境变量）
        if api_key is None:
            api_key = config.get('api_key')
            
            # 如果配置文件中也没有，尝试从环境变量获取
            if api_key is None:
                api_key = os.environ.get("DEEPSEEK_API_KEY")
                if api_key:
                    logger.info("从环境变量加载API密钥")
        
        # 检查是否有API密钥
        if not api_key:
            logger.warning("未设置Deepseek API密钥，将使用模拟模式")
        
        # 创建API客户端
        self.api = DeepseekAPI(
            api_key=api_key, 
            model_version=model_version,
            api_base=config.get('api_base')
        )
        
        # 保存配置
        self.config = config
        logger.info(f"初始化需求冲突检测器，使用模型: {config.get('model', 'deepseek-chat')}")
    
    def detect_conflicts(
        self, 
        requirements: Dict[str, List[Dict]],
        dimension: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检测需求中的冲突
        
        Args:
            requirements: 需求字典，格式为 {"类别": [需求列表]}
            dimension: 指定分析维度，如果为None则分析所有维度
        
        Returns:
            包含冲突信息的字典
        """
        # 如果没有指定分析维度，则分析所有维度
        dimensions = [dimension] if dimension else list(self.CONFLICT_DIMENSIONS.keys())
        
        logger.info(f"开始检测需求冲突，分析维度: {dimensions}")
        
        # 构建检测结果
        results = {
            "conflicts": [],
            "metadata": {
                "total_requirements": sum(len(reqs) for reqs in requirements.values()),
                "dimensions_analyzed": dimensions,
                "timestamp": None  # 将在处理完成后填充
            }
        }
        
        # 按维度分析冲突
        for dim in dimensions:
            logger.info(f"分析维度: {dim}")
            dim_conflicts = self._analyze_dimension(requirements, dim)
            results["conflicts"].extend(dim_conflicts)
        
        # 按严重等级排序
        results["conflicts"] = sorted(
            results["conflicts"], 
            key=lambda x: self.SEVERITY_LEVELS.index(x["severity"])
        )
        
        # 添加统计信息
        results["metadata"]["total_conflicts"] = len(results["conflicts"])
        results["metadata"]["conflicts_by_severity"] = {
            level: len([c for c in results["conflicts"] if c["severity"] == level])
            for level in self.SEVERITY_LEVELS
        }
        
        from datetime import datetime
        results["metadata"]["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"需求冲突检测完成，共发现 {len(results['conflicts'])} 个冲突")
        return results
    
    def _analyze_dimension(
        self, 
        requirements: Dict[str, List[Dict]], 
        dimension: str
    ) -> List[Dict]:
        """
        分析特定维度的冲突
        
        Args:
            requirements: 需求字典
            dimension: 分析维度
        
        Returns:
            该维度下的冲突列表
        """
        conflicts = []
        
        # 将所有需求展平为单一列表
        all_requirements = []
        for category, reqs in requirements.items():
            for req in reqs:
                req_copy = req.copy()
                req_copy["category"] = category
                all_requirements.append(req_copy)
        
        # 构建与Deepseek V3模型的对话提示
        system_prompt = self._build_system_prompt(dimension)
        
        # 将需求序列化为JSON
        requirements_json = json.dumps(all_requirements, ensure_ascii=False, indent=2)
        
        # 用户消息
        user_message = f"""
请分析以下需求列表，识别在"{dimension}"维度的冲突：

{requirements_json}

请按照以下格式输出每个冲突：
{{
  "conflict_type": "冲突类型",
  "requirements": ["需求ID1", "需求ID2"],
  "severity": "严重度(高/中/低)",
  "description": "冲突描述",
  "impact": "影响范围",
  "suggestion": "修改建议"
}}

多个冲突请组织为JSON数组。如果没有检测到冲突，请返回空数组[]。
"""
        
        # 构建完整对话
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            logger.info(f"向Deepseek API发送请求，分析维度: {dimension}")
            
            # 设置API调用参数
            api_params = {
                "temperature": 0.1,  # 使用低温度以获取更确定性的结果
                "max_tokens": 4000,
                "timeout": self.config.get("timeout", 60)
            }
            
            # 调用Deepseek API
            response = self.api.chat_completion(
                messages=messages,
                **api_params
            )
            
            # 解析响应内容
            content = response["choices"][0]["message"]["content"]
            logger.debug(f"Deepseek API响应: {content}")
            
            # 解析JSON响应
            try:
                # 提取JSON部分
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    content = json_match.group()
                
                dim_conflicts = json.loads(content)
                
                # 确保是列表类型
                if not isinstance(dim_conflicts, list):
                    dim_conflicts = [dim_conflicts]
                
                # 为每个冲突添加维度信息
                for conflict in dim_conflicts:
                    conflict["dimension"] = dimension
                
                conflicts.extend(dim_conflicts)
                logger.info(f"在'{dimension}'维度下发现 {len(dim_conflicts)} 个冲突")
            
            except json.JSONDecodeError as e:
                logger.error(f"解析模型响应时出错: {e}")
                logger.error(f"原始响应: {content}")
        
        except DeepseekAPIException as e:
            logger.error(f"调用Deepseek API时出错: {e}")
            logger.exception(e)
        except Exception as e:
            logger.error(f"出现未预期的错误: {e}")
            logger.exception(e)
        
        return conflicts
    
    def _build_system_prompt(self, dimension: str) -> str:
        """
        构建系统提示，指导模型进行特定维度的分析
        
        Args:
            dimension: 分析维度
        
        Returns:
            系统提示字符串
        """
        # 获取维度相关的子类别
        subcategories = self.CONFLICT_DIMENSIONS.get(dimension, [])
        subcategories_str = "、".join(subcategories)
        
        system_prompt = f"""你是一个资深软件架构师，专注于识别软件需求中的潜在冲突。
现在你需要分析"{dimension}"维度下的需求冲突，具体关注点包括：{subcategories_str}。

分析时请遵循以下原则：
1. 深入分析需求间的逻辑关系，识别显式和隐式冲突
2. 关注需求间的互斥条件和约束条件
3. 考虑不同角色、场景和操作流程的一致性
4. 为每个冲突标注严重等级（高/中/低）
5. 提供具体、可执行的修改建议

输出格式必须为标准JSON，包含冲突类型、涉及需求ID、严重程度、描述、影响和建议。
"""
        return system_prompt
    
    def generate_conflict_report(
        self, 
        conflicts: Dict[str, Any],
        format: str = "json"
    ) -> str:
        """
        生成冲突报告
        
        Args:
            conflicts: 检测到的冲突信息
            format: 报告格式，支持"json"、"markdown"
        
        Returns:
            格式化的冲突报告
        """
        if format.lower() == "json":
            return json.dumps(conflicts, ensure_ascii=False, indent=2)
        
        elif format.lower() == "markdown":
            # 构建Markdown报告
            md_lines = ["# 需求冲突检测报告\n"]
            
            # 添加元数据
            md_lines.append("## 检测概览")
            md_lines.append(f"- 总需求数：{conflicts['metadata']['total_requirements']}")
            md_lines.append(f"- 检测到的冲突总数：{conflicts['metadata']['total_conflicts']}")
            md_lines.append(f"- 检测时间：{conflicts['metadata']['timestamp']}")
            md_lines.append(f"- 分析维度：{', '.join(conflicts['metadata']['dimensions_analyzed'])}")
            
            # 按严重等级统计
            md_lines.append("\n### 按严重等级统计")
            for level in self.SEVERITY_LEVELS:
                count = conflicts['metadata']['conflicts_by_severity'].get(level, 0)
                md_lines.append(f"- {level}级冲突：{count}个")
            
            # 冲突详情
            md_lines.append("\n## 冲突详情")
            
            # 按维度分组
            conflicts_by_dimension = {}
            for conflict in conflicts['conflicts']:
                dim = conflict['dimension']
                if dim not in conflicts_by_dimension:
                    conflicts_by_dimension[dim] = []
                conflicts_by_dimension[dim].append(conflict)
            
            # 按维度输出冲突
            for dim, dim_conflicts in conflicts_by_dimension.items():
                md_lines.append(f"\n### {dim}")
                
                for i, conflict in enumerate(dim_conflicts, 1):
                    md_lines.append(f"\n#### {i}. {conflict['conflict_type']}")
                    md_lines.append(f"- **严重度**: {conflict['severity']}")
                    md_lines.append(f"- **涉及需求**: {', '.join(conflict['requirements'])}")
                    md_lines.append(f"- **冲突描述**: {conflict['description']}")
                    md_lines.append(f"- **影响范围**: {conflict['impact']}")
                    md_lines.append(f"- **修改建议**: {conflict['suggestion']}")
            
            return "\n".join(md_lines)
        
        else:
            raise ValueError(f"不支持的报告格式: {format}")