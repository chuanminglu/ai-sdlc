# 安装依赖：pip install spacy requests
import spacy
from datetime import datetime, timedelta
import requests
import json
import configparser
import os
from apispec_generator import APISpecGenerator

nlp = spacy.load("zh_core_web_sm")

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

def generate_user_story(domain, role, feature):
    """
    使用 DeepSeek API 生成用户故事
    :param domain: 业务领域
    :param role: 用户角色
    :param feature: 要实现的功能特性
    :return: 生成的用户故事文本
    """
    # 从配置文件获取 API 密钥
    API_KEY = get_api_key()
    
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # 构造提示文本
    prompt = f"""请用中文编写一个用户故事，描述以下需求：
领域：{domain}
角色：{role}
功能：{feature}

要求按照以下格式：
作为[角色]，
我希望[具体功能]，
以便[价值/目的]。

验收标准：
- [具体标准1]
- [具体标准2]
- [具体标准3]

请确保内容完整、清晰、具体。
"""
    
    # 准备请求数据
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        # 发送请求
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        generated_story = result['choices'][0]['message']['content'].strip()
        return generated_story
        
    except requests.exceptions.RequestException as e:
        print(f"API 调用出错: {str(e)}")
        return None

def parse_user_story(story):
    doc = nlp(story)
    
    # 提取角色（只获取"作为"之后到逗号或句号之前的内容）
    role = ""
    for sent in doc.sents:
        if "作为" in sent.text:
            role_text = sent.text.split("作为")[1]
            role = role_text.split("，")[0].split("。")[0].strip()
            break
    
    # 提取目标（获取"我希望"之后到逗号之前的内容）
    goal = ""
    for sent in doc.sents:
        if "我希望" in sent.text:
            goal_text = sent.text.split("我希望")[1]
            goal = goal_text.split("，")[0].split("。")[0].strip()
            break
    
    # 提取价值（获取"以便"之后到逗号或句号之前的内容）
    value = ""
    for sent in doc.sents:
        if "以便" in sent.text:
            value_text = sent.text.split("以便")[1]
            value = value_text.split("，")[0].split("。")[0].strip()
            break
    
    # 解析验收标准
    criteria = [line.strip("- ").strip() for line in story.split("\n") if line.strip().startswith("-")]
    
    return {
        "role": role,
        "goal": goal,
        "value": value,  # 添加价值字段
        "criteria": criteria,
        "timestamp": datetime.now().isoformat()
    }

def split_user_story(story, domain, role, count=3):
    """
    将一个大的用户故事拆分成多个小的、更具体的用户故事
    
    参数：
        story (str): 原始用户故事
        domain (str): 业务领域
        role (str): 用户角色
        count (int): 期望拆分的故事数量，默认3
        
    返回：
        list: 拆分后的用户故事列表
    """
    # 从配置文件获取 API 密钥
    API_KEY = get_api_key()
    
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # 构造提示文本
    prompt = f"""请将以下用户故事拆分成{count}个更小的、更具体的用户故事，每个故事聚焦于一个明确的功能点：

原始用户故事:
{story}

要求：
1. 输出{count}个独立的用户故事
2. 每个故事都要按照"作为[角色]，我希望[具体功能]，以便[价值/目的]。"的格式
3. 每个故事都需要包含2-3条具体的验收标准
4. 每个故事应该聚焦于原始故事中的一个功能点
5. 确保所有拆分后的故事加起来涵盖了原始故事的所有功能

请按照以下格式输出，用"---"分隔每个故事：

用户故事1:
作为[角色]，我希望[具体功能1]，以便[价值/目的]。

验收标准:
- [标准1]
- [标准2]
- [标准3]

---

用户故事2:
作为[角色]，我希望[具体功能2]，以便[价值/目的]。

验收标准:
- [标准1]
- [标准2]
- [标准3]

---

...以此类推，确保输出正好{count}个用户故事
"""
    
    # 准备请求数据
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    try:
        # 发送请求
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        generated_text = result['choices'][0]['message']['content'].strip()
        
        # 拆分多个故事
        stories = []
        parts = generated_text.split("---")
        
        for part in parts:
            part = part.strip()
            if part:
                stories.append(part)
                
        return stories
        
    except requests.exceptions.RequestException as e:
        print(f"API 调用出错: {str(e)}")
        return None

def generate_and_save_api_spec(user_story_data: dict, output_path: str) -> None:
    """
    生成并保存 API 规范
    :param user_story_data: 用户故事解析结果
    :param output_path: 输出文件路径
    """
    api_spec = APISpecGenerator.generate_api_spec(user_story_data)
    APISpecGenerator.save_api_spec(api_spec, output_path)

if __name__ == "__main__":
    # 测试生成和解析用户故事
    domain = "电商平台"
    role = "普通购物用户"
    feature = "商品评价功能"
    
    print("正在生成用户故事...")
    generated_story = generate_user_story(domain, role, feature)
    
    if generated_story:
        print("\n生成的用户故事：")
        print(generated_story)
        parsed_result = parse_user_story(generated_story)
        print("\n解析结果：")
        print(parsed_result)
        
        # 生成并保存 API 规范
        output_path = os.path.join(os.path.dirname(__file__), 'api_spec.json')
        generate_and_save_api_spec(parsed_result, output_path)
        print(f"\nAPI 规范已生成并保存到：{output_path}")
    else:
        print("生成用户故事失败，请检查 API 配置和网络连接。")