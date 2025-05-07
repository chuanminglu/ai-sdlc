"""LLM接口类"""
import json
import requests
import configparser
import os
from typing import Dict, Optional

def get_api_key():
    """
    从配置文件读取 API 密钥
    :return: API 密钥字符串
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError("配置文件 'config.ini' 不存在")
    
    config.read(config_path, encoding='utf-8')
    
    try:
        api_key = config['deepseek']['api_key']
        if api_key == 'your_api_key_here':
            raise ValueError("请在 config.ini 文件中设置有效的 API 密钥")
        return api_key
    except KeyError:
        raise KeyError("配置文件中缺少 deepseek 部分或 api_key 配置项")

class LLMInterface:
    """LLM通用接口"""
    
    def __init__(self):
        """初始化LLM接口"""
        self.API_KEY = get_api_key()
        self.API_URL = "https://api.deepseek.com/v1/chat/completions"
        
    def complete(self, prompt: str, **kwargs) -> str:
        """
        调用模型API进行补全
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            模型返回的文本
        """
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
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"调用模型API时发生错误: {str(e)}")
            
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
        
        # 调用模型
        try:
            response = self.complete(prompt)
            # 尝试解析JSON响应
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # 如果返回不是JSON格式，进行后处理
                return self._post_process_response(response)
        except Exception as e:
            raise Exception(f"分析PRD时发生错误: {str(e)}")
            
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
            
    def _post_process_response(self, response: str) -> Dict:
        """处理非JSON格式的响应"""
        # 如果响应不是JSON格式，返回一个基本的结构
        return {
            'missing_items': ['[解析错误]无法解析模型返回的评审结果'],
            'improvement_suggestions': ['请重试评审或联系技术支持'],
            'details': {}
        }