"""
用户故事生成和解析模块 (User Story Generator and Parser)

该模块提供以下主要功能：
1. 使用 DeepSeek API 生成符合敏捷开发规范的用户故事
2. 解析用户故事文本，提取角色、目标和验收标准
3. 生成标准的 API 规范文档

技术特点：
- 使用 spacy 进行自然语言处理
- 支持中文用户故事解析
- 集成 DeepSeek API 进行智能生成
- 包含完整的日志记录

主要类和函数：
- generate_user_story: 生成单个用户故事
- generate_multiple_user_stories: 批量生成用户故事
- parse_user_story: 解析用户故事文本
- generate_and_save_api_spec: 生成并保存API规范
"""

# 安装依赖：pip install spacy requests jieba
import spacy
from datetime import datetime, timedelta
import requests
import json
import configparser
import os
from typing import List, Dict
from apispec_generator import APISpecGenerator
from logger import logger

nlp = spacy.load("zh_core_web_sm")

def get_api_key():
    """
    从配置文件读取 DeepSeek API 密钥
    
    读取流程：
    1. 检查配置文件是否存在
    2. 验证配置文件格式
    3. 验证API密钥是否已设置
    
    返回：
        str: API 密钥字符串
    
    异常：
        FileNotFoundError: 配置文件不存在时抛出
        KeyError: 配置文件格式错误时抛出
        ValueError: API密钥未正确设置时抛出
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    logger.debug(f"尝试从 {config_path} 读取配置")
    
    if not os.path.exists(config_path):
        logger.error("配置文件不存在")
        raise FileNotFoundError("配置文件 'config.ini' 不存在")
    
    config.read(config_path, encoding='utf-8')
    
    try:
        api_key = config['deepseek']['api_key']
        if api_key == 'your_api_key_here':
            logger.error("API密钥未设置")
            raise ValueError("请在 config.ini 文件中设置有效的 API 密钥")
        logger.debug("成功读取 API 密钥")
        return api_key
    except KeyError:
        logger.error("配置文件格式错误")
        raise KeyError("配置文件中缺少 deepseek 部分或 api_key 配置项")

def clean_story_text(text: str) -> str:
    """
    清理文本中的特殊字符
    
    参数：
        text (str): 原始文本
    
    返回：
        str: 清理后的文本
    """
    import re
    
    # 保留中文、英文、数字、基本标点符号
    cleaned_text = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\s,.，。、：；？！（）()[\]【】\-]+', '', text)
    
    # 规范化标点符号
    cleaned_text = re.sub(r'[【\[（(]', '（', cleaned_text)
    cleaned_text = re.sub(r'[】\]）)]', '）', cleaned_text)
    cleaned_text = re.sub(r'["""]', '"', cleaned_text)
    
    # 删除多余的空白字符
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def generate_user_story(domain, role, feature):
    """生成用户故事"""
    logger.info(f"开始生成用户故事 - 领域: {domain}, 角色: {role}")
    
    API_KEY = get_api_key()
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # 构造更丰富的提示文本
    prompts = [
        f"""请用中文编写一个功能型用户故事，描述以下需求：
领域：{domain}
角色：{role}
功能：{feature}

按照以下格式：
作为{role}，我希望[具体功能描述]，以便[价值/目的]。

验收标准：
- [验收标准1]
- [验收标准2]
- [验收标准3]
- [验收标准4]"""
    ]
    
    # 随机选择一个提示模板
    import random
    prompt = random.choice(prompts)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,  # 增加多样性
        "max_tokens": 800
    }
    
    try:
        logger.debug("发送 API 请求")
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        generated_story = result['choices'][0]['message']['content'].strip()
        cleaned_story = clean_story_text(generated_story)
        logger.info("成功生成用户故事")
        return cleaned_story
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API 调用失败: {str(e)}")
        return None

def split_feature_into_subfeatures(feature: str) -> List[str]:
    """
    将功能特性拆分为多个子功能
    
    参数：
        feature (str): 主功能特性描述
        
    返回：
        List[str]: 子功能列表
    """
    # 基于功能关键词进行拆分
    feature_keywords = {
        '创建': ['新建', '创建', '添加', '录入', '输入'],
        '编辑': ['编辑', '修改', '更新', '维护'],
        '查询': ['查看', '搜索', '检索', '浏览', '列表'],
        '删除': ['删除', '移除', '清理', '归档'],
        '审核': ['审核', '审批', '验证', '检查'],
        '发布': ['发布', '上线', '启用', '生效'],
        '管理': ['管理', '分类', '标签', '状态', '配置'],
        '导入导出': ['导入', '导出', '备份', '恢复'],
        '统计': ['统计', '分析', '报表', '汇总']
    }
    
    import re
    subfeatures = []
    
    # 1. 首先尝试从原始文本中提取明确的功能点
    for category, keywords in feature_keywords.items():
        for keyword in keywords:
            if keyword in feature:
                # 提取包含关键词的完整短语
                matches = re.finditer(f"[^，。、；]+{keyword}[^，。、；]+", feature)
                for match in matches:
                    subfeature = match.group().strip()
                    if len(subfeature) > 2 and subfeature not in subfeatures:
                        subfeatures.append(subfeature)
    
    # 2. 如果提取的子功能太少，根据常见场景补充
    if len(subfeatures) < 3:
        domain_specific_features = {
            '新闻管理系统': [
                '创建新文章草稿',
                '编辑文章内容和格式',
                '设置文章分类和标签',
                '发布已审核的文章',
                '管理文章版本历史',
                '归档过期文章',
                '设置文章访问权限',
                '导出文章数据报表'
            ],
            '用户管理系统': [
                '创建新用户账号',
                '修改用户信息',
                '分配用户角色权限',
                '重置用户密码',
                '禁用违规账号',
                '查看用户操作日志'
            ],
            # 可以继续添加其他领域的特定功能
        }
        
        # 根据领域补充子功能
        domain_features = domain_specific_features.get(domain, [])
        if domain_features:
            for feat in domain_features:
                if any(keyword in feat for keyword in sum(feature_keywords.values(), [])):
                    if feat not in subfeatures:
                        subfeatures.append(feat)
    
    # 3. 确保至少有3个子功能
    if len(subfeatures) < 3:
        base_features = ['创建', '编辑', '查询', '删除']
        for base in base_features:
            if base not in ' '.join(subfeatures):
                subfeatures.append(f"{base}{feature}")
    
    return subfeatures[:5]  # 最多返回5个子功能

def generate_multiple_user_stories(domain: str, role: str, feature: str, count: int = 3) -> List[Dict]:
    """
    批量生成多个用户故事
    
    参数：
        domain (str): 业务领域
        role (str): 用户角色
        feature (str): 功能特性
        count (int, optional): 要生成的故事数量，默认为3
    
    返回：
        List[Dict]: 用户故事列表，每个故事包含:
            - title: 故事标题
            - content: 完整故事内容
            - parsed: 解析后的结构化数据
    """
    logger.info(f"开始批量生成用户故事 - 数量: {count}")
    stories = []
    
    # 1. 拆分子功能
    subfeatures = split_feature_into_subfeatures(feature)
    logger.debug(f"拆分得到的子功能: {subfeatures}")
    
    # 2. 确保有足够的子功能
    while len(subfeatures) < count:
        subfeatures.extend(subfeatures)
    subfeatures = subfeatures[:count]
    
    # 3. 为每个子功能生成故事
    for i, subfeature in enumerate(subfeatures[:count]):
        logger.debug(f"生成第 {i+1}/{count} 个故事，子功能: {subfeature}")
        story = generate_user_story(domain, role, subfeature)
        if story:
            # 使用parse_user_story函数解析用户故事
            parsed_data = parse_user_story(story, domain)
            stories.append({
                'title': parsed_data['goal'] or subfeature,
                'content': story,
                'parsed': parsed_data,
                'subfeature': subfeature  # 记录对应的子功能
            })
        else:
            logger.warning(f"第 {i+1} 个故事生成失败")
    
    # 4. 验证故事的差异性
    def calculate_similarity(story1: str, story2: str) -> float:
        """计算两个故事的相似度"""
        import difflib
        return difflib.SequenceMatcher(None, story1, story2).ratio()
    
    # 检查并重新生成过于相似的故事
    MAX_SIMILARITY = 0.7  # 最大允许的相似度
    for i in range(len(stories)):
        for j in range(i + 1, len(stories)):
            similarity = calculate_similarity(stories[i]['content'], stories[j]['content'])
            if similarity > MAX_SIMILARITY:
                logger.warning(f"故事 {i+1} 和 {j+1} 相似度过高 ({similarity:.2f})，重新生成")
                new_story = generate_user_story(domain, role, stories[j]['subfeature'])
                if new_story:
                    parsed_data = parse_user_story(new_story, domain)
                    stories[j] = {
                        'title': parsed_data['goal'] or stories[j]['subfeature'],
                        'content': new_story,
                        'parsed': parsed_data,
                        'subfeature': stories[j]['subfeature']
                    }
    
    logger.info(f"完成批量生成，成功生成 {len(stories)} 个故事")
    return stories

def parse_user_story(story, domain: str = ""):
    """解析用户故事文本，提取关键信息"""
    logger.info("开始解析用户故事")
    
    # 清理输入的故事文本
    story = clean_story_text(story)
    logger.debug(f"清理后的故事文本: {story}")
    
    # 初始化结果字典
    result = {
        "domain": domain,
        "role": "",
        "goal": "",
        "value": "",
        "criteria": []
    }
    
    # 分离用户故事主体和验收标准
    story_lines = []
    criteria = []
    lines = story.strip().split('\n')
    in_criteria = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测验收标准部分的多种可能开始标记
        if any(line.startswith(mark) for mark in ['验收标准', '验收准则', 'AC:', '验收：']) or line.startswith('-'):
            in_criteria = True
            if not line.startswith('-'):
                continue
            criteria.append(line.lstrip('- ').strip())
        else:
            if not in_criteria:
                story_lines.append(line)
    
    story_body = ' '.join(story_lines)
    
    # 使用更灵活的正则表达式提取主要部分
    import re
    
    # 提取角色（支持多种格式）
    role_patterns = [
        r'作为(.*?)(?:，|,)',
        r'身为(.*?)(?:，|,)',
        r'(?:我是|我为)(.*?)(?:，|,)',
    ]
    
    for pattern in role_patterns:
        role_match = re.search(pattern, story_body)
        if role_match:
            result['role'] = role_match.group(1).strip()
            break
    
    # 提取目标（支持多种格式）
    goal_patterns = [
        r'我希望(.*?)(?:，|,)',
        r'我需要(.*?)(?:，|,)',
        r'期望能够(.*?)(?:，|,)',
        r'我想要(.*?)(?:，|,)',
    ]
    
    for pattern in goal_patterns:
        goal_match = re.search(pattern, story_body)
        if goal_match:
            result['goal'] = goal_match.group(1).strip()
            break
    
    # 提取价值（支持多种格式）
    value_patterns = [
        r'以便(.*?)(?:。|\.)',
        r'从而(.*?)(?:。|\.)',
        r'这样可以(.*?)(?:。|\.)',
        r'(?:目的是|为了)(.*?)(?:。|\.)',
    ]
    
    for pattern in value_patterns:
        value_match = re.search(pattern, story_body)
        if value_match:
            result['value'] = value_match.group(1).strip()
            break
    
    # 如果没有找到标准格式的内容，尝试根据句子位置提取
    if not all([result['role'], result['goal'], result['value']]):
        sentences = re.split(r'[。，,.]', story_body)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 3 and not result['role']:
            result['role'] = sentences[0].replace('作为', '').replace('身为', '').strip()
        if len(sentences) >= 3 and not result['goal']:
            result['goal'] = sentences[1].replace('我希望', '').replace('我需要', '').strip()
        if len(sentences) >= 3 and not result['value']:
            result['value'] = sentences[2].replace('以便', '').replace('从而', '').strip()
    
    # 保存验收标准
    result['criteria'] = criteria
    
    # 使用spacy提取领域概念
    doc = nlp(story_body)
    domain_concepts = []
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 1:
            domain_concepts.append(token.text)
    
    # 去重并保存领域概念
    result['domain_concepts'] = list(set(domain_concepts))
    
    # 分析故事的优先级和复杂度
    priority_keywords = {
        'high': ['必须', '急需', '立即', '重要', '优先', '关键'],
        'low': ['可选', '未来', '待定', '次要', '一般', '普通']
    }
    
    complexity_keywords = {
        'high': ['复杂', '系统性', '集成', '架构', '依赖多', '全局'],
        'low': ['简单', '基础', '单一', '独立', '局部']
    }
    
    # 设置优先级
    story_text = story_body + ' ' + ' '.join(criteria)
    for level, keywords in priority_keywords.items():
        if any(keyword in story_text for keyword in keywords):
            result['priority'] = level
            break
    
    # 设置复杂度
    for level, keywords in complexity_keywords.items():
        if any(keyword in story_text for keyword in keywords):
            result['complexity'] = level
            break
    
    # 识别依赖关系
    dependency_keywords = ['依赖', '需要', '基于', '使用', '关联', '配合']
    for criterion in criteria:
        for keyword in dependency_keywords:
            if keyword in criterion:
                result['dependencies'].append(criterion)
                break
    
    # 验证解析结果的完整性
    if not all([result['role'], result['goal'], result['value']]):
        logger.warning("部分关键信息未能提取")
    
    logger.debug(f"解析结果: {result}")
    logger.info("完成用户故事解析")
    return result

def generate_and_save_api_spec(parsed_data: Dict, output_path: str) -> Dict:
    """
    根据解析后的用户故事生成API规范并保存
    
    参数：
        parsed_data (Dict): 解析后的用户故事数据
        output_path (str): API规范文件保存路径
    
    返回：
        Dict: API规范验证结果，包含：
            - 是否满足所有验收标准
            - 技术约束检查结果
            - 潜在问题提示
    
    输出格式：
    生成的API规范将保存为JSON文件，包含：
    - OpenAPI 3.0规范
    - 接口定义
    - 数据模型
    - 验证规则
    """
    logger.info(f"开始生成 API 规范 - 输出路径: {output_path}")
    
    # 生成API规范
    api_spec = APISpecGenerator.generate_api_spec(parsed_data)
    logger.debug("API规范生成完成")
    
    # 验证API规范是否满足验收标准和技术约束
    validation_results = APISpecGenerator.validate_api_spec(api_spec, parsed_data.get('criteria', []))
    logger.debug(f"验证结果: {validation_results}")
    
    # 保存API规范
    APISpecGenerator.save_api_spec(api_spec, output_path)
    logger.info("API规范已保存")
    
    return validation_results

if __name__ == "__main__":
    # 测试代码
    story = """作为内容编辑，我希望能够创建新的文章，以便快速发布内容。
- 必填字段：标题、内容、分类
- 可选字段：标签、摘要、封面图
- 支持文章预览功能
- 可以保存为草稿
- 支持定时发布设置"""
    
    logger.info("开始测试")
    result = parse_user_story(story, "新闻管理系统")
    api_spec = generate_and_save_api_spec(result, "api_spec.json")
    logger.info("测试完成")