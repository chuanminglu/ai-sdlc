"""示例PRD文档生成器"""

def generate_sample_prd(template_type: str = 'missing_background') -> str:
    """
    生成一个有特定缺陷的PRD文档
    
    Args:
        template_type: 文档模板类型，可选值：
            - missing_background: 缺少业务背景
            - missing_value: 缺少价值描述
            - missing_goal: 缺少明确目标
            - missing_flow: 缺少业务流程
            - missing_criteria: 缺少验收标准
            - incomplete: 多项缺失
    """
    templates = {
        'missing_background': {
            'title': '商品评论排序功能需求',
            'version': '1.0.0',
            'author': '张三',
            'date': '2025-05-07',
            'content': '''
# 商品评论排序功能需求说明书

## 1. 需求描述
实现商品评论的智能排序功能，支持多种排序方式。

## 2. 功能特性
1. 支持按评分高低排序
2. 支持按时间新旧排序
3. 支持按点赞数排序
4. 支持综合排序（评分权重70%，时间权重30%）

## 3. 交互设计
- 在评论区顶部添加排序下拉菜单
- 切换排序方式时实时更新评论列表
- 支持正序和倒序切换

## 4. 验收标准
1. 所有排序方式功能正常
2. 排序响应时间<500ms
3. 支持100万级评论数据
4. 需兼容主流浏览器'''
        },
        'missing_value': {
            'title': '商品评论排序功能需求',
            'version': '1.0.0',
            'author': '张三',
            'date': '2025-05-07',
            'content': '''
# 商品评论排序功能需求说明书

## 1. 业务背景
当前商品评论展示采用简单的时间倒序，用户难以快速找到有价值的评论。

## 2. 功能特性
1. 支持按评分高低排序
2. 支持按时间新旧排序
3. 支持按点赞数排序
4. 支持综合排序（评分权重70%，时间权重30%）

## 3. 交互设计
- 在评论区顶部添加排序下拉菜单
- 切换排序方式时实时更新评论列表
- 支持正序和倒序切换

## 4. 验收标准
1. 所有排序方式功能正常
2. 排序响应时间<500ms
3. 支持100万级评论数据
4. 需兼容主流浏览器'''
        },
        'incomplete': {
            'title': '商品评论排序功能需求',
            'version': '1.0.0',
            'author': '张三',
            'date': '2025-05-07',
            'content': '''
# 商品评论排序功能需求说明书

## 1. 功能特性
1. 支持按评分排序
2. 支持按时间排序
3. 支持按点赞数排序

## 2. 交互设计
- 添加排序下拉菜单
- 支持排序方式切换'''
        }
    }
    
    template = templates.get(template_type, templates['incomplete'])
    return template['content']