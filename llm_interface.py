"""LLM接口类"""
import json
import requests
import configparser
import os
import time
import logging
from typing import Dict, Optional
from requests.exceptions import Timeout, RequestException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("llm_interface.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LLMInterface")

def get_config():
    """
    从配置文件读取配置信息
    :return: 配置字典
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        raise FileNotFoundError("配置文件 'config.ini' 不存在")
    
    config.read(config_path, encoding='utf-8')
    
    try:
        api_key = config['deepseek']['api_key']
        if api_key == 'your_api_key_here':
            logger.error("API密钥未设置")
            raise ValueError("请在 config.ini 文件中设置有效的 API 密钥")
            
        return {
            'api_key': api_key,
            'timeout': config.getint('deepseek', 'timeout', fallback=60),
            'max_retries': config.getint('deepseek', 'max_retries', fallback=3),
            'retry_delay': config.getint('deepseek', 'retry_delay', fallback=5)
        }
    except KeyError:
        logger.error("配置文件缺少必要的配置项")
        raise KeyError("配置文件中缺少 deepseek 部分或必要的配置项")

class LLMInterface:
    """LLM通用接口"""
    
    def __init__(self):
        """初始化LLM接口"""
        config = get_config()
        self.API_KEY = config['api_key']
        self.API_URL = "https://api.deepseek.com/v1/chat/completions"  # 修正为完整的API端点路径
        self.TIMEOUT = config['timeout']
        self.MAX_RETRIES = config['max_retries']
        self.RETRY_DELAY = config['retry_delay']
        
    def complete(self, prompt: str, **kwargs) -> str:
        """
        调用模型API进行补全，支持重试机制
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            模型返回的文本
        """
        retries = 0
        last_error = None
        
        while retries < self.MAX_RETRIES:
            try:
                headers = {
                    'Authorization': f'Bearer {self.API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'deepseek-chat',
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': kwargs.get('max_tokens', 2000),
                    'temperature': kwargs.get('temperature', 0.7)
                }
                
                logger.info(f"调用API，提示词: {prompt}")
                
                response = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=data,
                    timeout=self.TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("API调用成功")
                    return result['choices'][0]['message']['content']
                elif response.status_code == 429:  # 速率限制
                    logger.warning("API调用次数超限，请稍后重试")
                    raise Exception("API调用次数超限，请稍后重试")
                else:
                    logger.error(f"API调用失败: {response.status_code} - {response.text}")
                    raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                    
            except Timeout:
                last_error = f"API调用超时（已等待{self.TIMEOUT}秒）"
                logger.error(last_error)
            except RequestException as e:
                last_error = f"网络请求错误: {str(e)}"
                logger.error(last_error)
            except Exception as e:
                last_error = f"调用模型API时发生错误: {str(e)}"
                logger.error(last_error)
            
            retries += 1
            if retries < self.MAX_RETRIES:
                logger.info(f"第{retries}次重试（共{self.MAX_RETRIES}次）...")
                time.sleep(self.RETRY_DELAY)
        
        logger.error(f"达到最大重试次数({self.MAX_RETRIES})。最后一次错误: {last_error}")
        raise Exception(f"达到最大重试次数({self.MAX_RETRIES})。最后一次错误: {last_error}")
            
    def analyze_prd(self, prd_content: str, standards: list) -> Dict:
        """
        分析PRD文档
        
        Args:
            prd_content: PRD文档内容
            standards: 评审标准列表
            
        Returns:
            分析结果字典
        """
        # 构建提示词
        prompt = self._build_analysis_prompt(prd_content, standards)
        logger.info("构建分析提示词完成")
        
        # 调用模型
        try:
            response = self.complete(prompt)
            logger.info("收到模型响应，开始解析")
            
            # 尝试直接解析整个响应
            try:
                parsed_result = json.loads(response)
                logger.info("JSON直接解析成功")
                return parsed_result
            except json.JSONDecodeError:
                # 尝试从响应中提取JSON部分
                logger.warning("直接解析JSON失败，尝试提取JSON部分")
                extracted_json = self._extract_json_from_text(response)
                if extracted_json:
                    logger.info("成功从文本中提取JSON")
                    return extracted_json
                else:
                    # 如果还是失败，进行后处理
                    logger.error("无法从响应中提取有效JSON")
                    return self._post_process_response(response)
                    
        except Exception as e:
            logger.error(f"分析PRD时发生错误: {str(e)}")
            raise Exception(f"分析PRD时发生错误: {str(e)}")
            
    def _extract_json_from_text(self, text: str) -> Dict:
        """从文本中提取JSON部分"""
        import re
        
        # 尝试几种常见的JSON模式
        # 1. 查找完整的JSON对象 {...}
        json_pattern = r'(\{[\s\S]*\})'
        matches = re.search(json_pattern, text)
        if matches:
            try:
                json_str = matches.group(1)
                logger.info(f"找到可能的JSON字符串: {json_str[:100]}...")
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("第一次JSON提取尝试失败")
                pass
        
        # 2. 尝试寻找JSON代码块（Markdown格式）
        code_block_pattern = r'```(?:json)?([\s\S]*?)```'
        matches = re.search(code_block_pattern, text)
        if matches:
            try:
                json_str = matches.group(1).strip()
                logger.info(f"从代码块中提取JSON: {json_str[:100]}...")
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("从代码块提取JSON失败")
                pass
        
        # 3. 尝试从文本中整理JSON结构
        try:
            # 尝试修复常见JSON格式错误
            cleaned_text = text
            # 替换单引号为双引号
            cleaned_text = re.sub(r"'([^']*)':\s*", r'"\1": ', cleaned_text)
            # 替换不带引号的键
            cleaned_text = re.sub(r'(\w+):\s*', r'"\1": ', cleaned_text)
            # 查找修复后的JSON对象
            matches = re.search(r'(\{[\s\S]*\})', cleaned_text)
            if matches:
                json_str = matches.group(1)
                logger.info(f"尝试修复后的JSON: {json_str[:100]}...")
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"修复JSON格式失败: {str(e)}")
            
        # 所有尝试都失败
        return None
        
    def _post_process_response(self, response: str) -> Dict:
        """处理非JSON格式的响应"""
        logger.warning("模型返回的响应无法解析为JSON")
        
        # 尝试提取部分有用信息
        missing_items = []
        improvement_suggestions = []
        details = {}
        
        # 尝试提取缺失项
        if "缺失" in response or "missing" in response.lower():
            missing_pattern = r'(?:缺失项|missing items)[^\n]*?[:：]([^\n]*)'
            matches = re.findall(missing_pattern, response, re.IGNORECASE)
            if matches:
                for match in matches:
                    items = re.split(r'[,，、]', match)
                    missing_items.extend([item.strip() for item in items if item.strip()])
        
        # 尝试提取改进建议
        if "建议" in response or "suggestion" in response.lower():
            suggestion_pattern = r'(?:建议|改进|suggestions)[^\n]*?[:：]([^\n]*)'
            matches = re.findall(suggestion_pattern, response, re.IGNORECASE)
            if matches:
                for match in matches:
                    items = re.split(r'[,，、]', match)
                    improvement_suggestions.extend([item.strip() for item in items if item.strip()])
        
        # 如果没有提取到任何信息，使用默认的错误消息
        if not missing_items:
            missing_items = ['[解析错误]无法解析模型返回的评审结果']
        if not improvement_suggestions:
            improvement_suggestions = ['请重试评审或联系技术支持']
            
        # 记录原始响应，以便调试
        logger.info(f"原始响应内容: {response}")
            
        return {
            'missing_items': missing_items,
            'improvement_suggestions': improvement_suggestions,
            'details': details,
            'raw_response': response  # 保存原始响应以便调试
        }
            
    def _build_analysis_prompt(self, prd_content: str, standards: list) -> str:
        """构建分析提示词"""
        standards_text = "\n".join(
            f"{std['id']}. {std['title']}: {std['description']}"
            for std in standards
        )
        
        return f"""作为一名专业的需求评审专家，请基于以下评审标准对PRD文档进行分析：

{standards_text}

需要评审的PRD文档内容如下：

{prd_content}

请提供一个结构化的JSON评审报告，包含以下内容：
1. missing_items: 文档中缺失的关键要素列表
2. improvement_suggestions: 具体的改进建议列表
3. details: 每个评审标准的详细评分（0-100）和评分理由，格式如下：
   {{"1": {{"score": 85, "title": "标准标题", "reason": "评分理由"}}}}

注意：
- 评分应该客观公正，有充分理由
- 改进建议应具体且可执行
- 返回的必须是合法的JSON格式

请确保返回的JSON可以被解析。例如：
{{
    "missing_items": ["缺少业务背景说明", "缺少期望发布时间"],
    "improvement_suggestions": ["建议在文档开始部分添加业务背景章节", "明确说明项目的期望发布时间"],
    "details": {{
        "1": {{"score": 85, "title": "变更记录", "reason": "文档包含了版本信息，但缺少具体的变更说明"}}
    }}
}}
"""