"""
商品评论排序算法模块

该模块提供多种评论排序算法:
1. 按评分（1-5星）排序
2. 按时间新近度排序
3. 综合排序（评分*70%+新近度*30%）
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional
import math

def sort_by_rating(comments: List[Dict[Any, Any]], order: str = 'desc') -> List[Dict[Any, Any]]:
    """
    按评分对评论进行排序
    
    参数:
        comments: 评论列表，每个评论是一个字典
        order: 排序方式，'desc'表示降序（默认），'asc'表示升序
        
    返回:
        排序后的评论列表
    """
    reverse = (order.lower() != 'asc')  # 默认降序
    return sorted(comments, key=lambda x: x.get('rating', 0), reverse=reverse)

def sort_by_time(comments: List[Dict[Any, Any]], order: str = 'desc') -> List[Dict[Any, Any]]:
    """
    按发布时间对评论进行排序
    
    参数:
        comments: 评论列表，每个评论是一个字典
        order: 排序方式，'desc'表示降序（默认），'asc'表示升序
        
    返回:
        排序后的评论列表
    """
    def get_datetime(comment):
        create_time = comment.get('createTime')
        # 如果是字符串格式的日期时间，转换为datetime对象
        if isinstance(create_time, str):
            try:
                return datetime.fromisoformat(create_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # 尝试其他常见格式
                    return datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return datetime.min
        # 如果已经是datetime对象
        elif isinstance(create_time, datetime):
            return create_time
        # 默认值
        return datetime.min
    
    reverse = (order.lower() != 'asc')  # 默认降序
    return sorted(comments, key=get_datetime, reverse=reverse)

def calculate_recency_score(comment: Dict[Any, Any], now: Optional[datetime] = None) -> float:
    """
    计算评论的新近度得分（0-1之间）
    
    参数:
        comment: 评论字典
        now: 当前时间，默认为None表示使用当前系统时间
        
    返回:
        新近度得分，1表示最新，0表示最旧
    """
    if now is None:
        now = datetime.now()
    
    # 获取评论时间
    create_time = comment.get('createTime')
    if isinstance(create_time, str):
        try:
            create_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
        except ValueError:
            try:
                create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return 0
    elif not isinstance(create_time, datetime):
        return 0
    
    # 计算评论距离现在的时间（天数）
    days_diff = (now - create_time).days
    
    # 使用指数衰减计算新近度得分
    # 90天（3个月）为参考期，超过90天的评论新近度接近0
    recency_score = math.exp(-days_diff / 30)  # 30天为半衰期
    
    # 限制得分在0-1之间
    return max(0, min(1, recency_score))

def sort_by_composite(comments: List[Dict[Any, Any]], 
                     rating_weight: float = 0.7, 
                     recency_weight: float = 0.3, 
                     order: str = 'desc') -> List[Dict[Any, Any]]:
    """
    使用综合排序算法（评分权重 + 新近度权重）
    
    参数:
        comments: 评论列表
        rating_weight: 评分权重，默认0.7
        recency_weight: 新近度权重，默认0.3
        order: 排序方式，'desc'表示降序（默认），'asc'表示升序
        
    返回:
        排序后的评论列表
    """
    now = datetime.now()
    
    def composite_score(comment):
        # 评分得分（标准化到0-1之间）
        rating = comment.get('rating', 0)
        rating_score = (rating - 1) / 4 if 1 <= rating <= 5 else 0
        
        # 新近度得分
        recency_score = calculate_recency_score(comment, now)
        
        # 综合得分
        return (rating_score * rating_weight) + (recency_score * recency_weight)
    
    reverse = (order.lower() != 'asc')  # 默认降序
    return sorted(comments, key=composite_score, reverse=reverse)

def sort_comments(comments: List[Dict[Any, Any]], 
                 sort_by: str = 'composite', 
                 order: str = 'desc') -> List[Dict[Any, Any]]:
    """
    根据指定的排序方式对评论进行排序
    
    参数:
        comments: 评论列表
        sort_by: 排序字段，可选值为'rating'（评分）、'time'（时间）、
                'composite'（综合排序，默认）、'usefulness'（有用度）
        order: 排序方向，'desc'表示降序（默认），'asc'表示升序
        
    返回:
        排序后的评论列表
    """
    # 参数验证
    if not comments:
        return []
    
    if sort_by == 'rating':
        return sort_by_rating(comments, order)
    elif sort_by == 'time':
        return sort_by_time(comments, order)
    elif sort_by == 'usefulness':
        # 按点赞数（usefulness）排序
        reverse = (order.lower() != 'asc')  # 默认降序
        return sorted(comments, key=lambda x: x.get('usefulness', 0), reverse=reverse)
    else:  # 默认使用综合排序
        return sort_by_composite(comments, order=order)

def filter_comments_by_date_range(comments: List[Dict[Any, Any]], 
                                 days: int = 90) -> List[Dict[Any, Any]]:
    """
    筛选指定时间范围内的评论
    
    参数:
        comments: 评论列表
        days: 天数，默认90天（3个月）
        
    返回:
        筛选后的评论列表
    """
    now = datetime.now()
    start_date = now - timedelta(days=days)
    
    filtered = []
    for comment in comments:
        create_time = comment.get('createTime')
        if isinstance(create_time, str):
            try:
                create_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
        elif not isinstance(create_time, datetime):
            continue
        
        if create_time >= start_date:
            filtered.append(comment)
    
    return filtered