"""
测试商品评论排序算法模块

该模块测试createsort.py中的排序算法：
1. 评分排序测试
2. 时间排序测试
3. 综合排序测试(评分*70%+新近度*30%)
4. 日期范围过滤测试
"""

import unittest
from datetime import datetime, timedelta
import json
from createsort import (
    sort_by_rating, 
    sort_by_time, 
    sort_by_composite,
    filter_comments_by_date_range,
    sort_comments,
    calculate_recency_score
)

class TestCommentSorting(unittest.TestCase):
    def setUp(self):
        """
        设置测试数据
        """
        # 创建测试用的评论数据
        now = datetime.now()
        self.comments = [
            {
                "id": "1",
                "rating": 5,
                "content": "非常好用的产品！",
                "usefulness": 10,
                "createTime": (now - timedelta(days=5)).isoformat()
            },
            {
                "id": "2",
                "rating": 2,
                "content": "质量一般",
                "usefulness": 5,
                "createTime": (now - timedelta(days=20)).isoformat()
            },
            {
                "id": "3",
                "rating": 4,
                "content": "还不错，但有改进空间",
                "usefulness": 15,
                "createTime": (now - timedelta(days=1)).isoformat()
            },
            {
                "id": "4",
                "rating": 1,
                "content": "非常失望",
                "usefulness": 20,
                "createTime": (now - timedelta(days=100)).isoformat()
            },
            {
                "id": "5",
                "rating": 3,
                "content": "一般般",
                "usefulness": 3,
                "createTime": (now - timedelta(days=50)).isoformat()
            }
        ]
    
    def test_sort_by_rating_desc(self):
        """测试按评分降序排序"""
        sorted_comments = sort_by_rating(self.comments, 'desc')
        ratings = [comment["rating"] for comment in sorted_comments]
        self.assertEqual(ratings, [5, 4, 3, 2, 1])
    
    def test_sort_by_rating_asc(self):
        """测试按评分升序排序"""
        sorted_comments = sort_by_rating(self.comments, 'asc')
        ratings = [comment["rating"] for comment in sorted_comments]
        self.assertEqual(ratings, [1, 2, 3, 4, 5])
    
    def test_sort_by_time_desc(self):
        """测试按时间降序排序（最新的排在前面）"""
        sorted_comments = sort_by_time(self.comments, 'desc')
        ids = [comment["id"] for comment in sorted_comments]
        self.assertEqual(ids, ["3", "1", "2", "5", "4"])
    
    def test_sort_by_time_asc(self):
        """测试按时间升序排序（最早的排在前面）"""
        sorted_comments = sort_by_time(self.comments, 'asc')
        ids = [comment["id"] for comment in sorted_comments]
        self.assertEqual(ids, ["4", "5", "2", "1", "3"])
    
    def test_sort_by_usefulness(self):
        """测试按有用性（点赞数）排序"""
        sorted_comments = sort_comments(self.comments, 'usefulness', 'desc')
        usefulness = [comment["usefulness"] for comment in sorted_comments]
        self.assertEqual(usefulness, [20, 15, 10, 5, 3])
    
    def test_filter_by_date_range(self):
        """测试日期范围过滤"""
        filtered_comments = filter_comments_by_date_range(self.comments, days=30)
        self.assertEqual(len(filtered_comments), 3)
        ids = set([comment["id"] for comment in filtered_comments])
        self.assertEqual(ids, {"1", "2", "3"})
        
        # 测试90天过滤
        filtered_comments = filter_comments_by_date_range(self.comments, days=90)
        self.assertEqual(len(filtered_comments), 4)
        
        # 测试全部过滤
        filtered_comments = filter_comments_by_date_range(self.comments, days=365)
        self.assertEqual(len(filtered_comments), 5)
    
    def test_recency_score(self):
        """测试新近度得分计算"""
        now = datetime.now()
        
        # 测试不同日期的新近度得分
        comments = [
            {"createTime": now.isoformat()},  # 当前，应该接近1
            {"createTime": (now - timedelta(days=30)).isoformat()},  # 30天前，应该约为0.5
            {"createTime": (now - timedelta(days=90)).isoformat()}   # 90天前，应该很小
        ]
        
        scores = [calculate_recency_score(comment, now) for comment in comments]
        
        # 验证分数递减
        self.assertTrue(scores[0] > scores[1] > scores[2])
        
        # 验证新评论接近1
        self.assertAlmostEqual(scores[0], 1.0, delta=0.1)
        
        # 验证30天前评论约为0.5 (e^-1 ≈ 0.368)
        self.assertAlmostEqual(scores[1], 0.368, delta=0.1)
    
    def test_composite_sorting(self):
        """测试综合排序"""
        # 将评分和时间都设为极端值以便测试
        test_comments = [
            {
                "id": "A",
                "rating": 5,  # 最高评分
                "createTime": (datetime.now() - timedelta(days=60)).isoformat()  # 较旧
            },
            {
                "id": "B",
                "rating": 3,  # 中等评分
                "createTime": datetime.now().isoformat()  # 最新
            },
            {
                "id": "C", 
                "rating": 1,  # 最低评分
                "createTime": (datetime.now() - timedelta(days=10)).isoformat()  # 较新
            }
        ]
        
        # 使用默认权重排序（评分70%，新近度30%）
        sorted_comments = sort_by_composite(test_comments)
        ids = [comment["id"] for comment in sorted_comments]
        
        # 验证排序结果：高评分但较旧的应该仍排第一（因为评分权重大）
        self.assertEqual(ids[0], "A")
        
        # 增加新近度权重，现在较新的评论应该排名更靠前
        sorted_comments = sort_by_composite(test_comments, rating_weight=0.3, recency_weight=0.7)
        ids = [comment["id"] for comment in sorted_comments]
        
        # 验证权重变化后的排序结果：最新的中等评分应该排第一
        self.assertEqual(ids[0], "B")
    
    def test_general_sort_comments(self):
        """测试通用排序接口"""
        # 测试默认排序（综合排序）
        default_sorted = sort_comments(self.comments)
        self.assertTrue(len(default_sorted) == len(self.comments))
        
        # 测试评分排序
        rating_sorted = sort_comments(self.comments, 'rating')
        self.assertEqual(rating_sorted[0]["rating"], 5)
        
        # 测试时间排序
        time_sorted = sort_comments(self.comments, 'time')
        newest_id = time_sorted[0]["id"]
        self.assertEqual(newest_id, "3")  # ID为3的是最新的评论
        
        # 测试处理空列表
        empty_sorted = sort_comments([])
        self.assertEqual(empty_sorted, [])

if __name__ == '__main__':
    unittest.main()