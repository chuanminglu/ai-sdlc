import unittest
from datetime import datetime, timedelta
import json
from unittest.mock import patch, MagicMock

class TestCommentSystem(unittest.TestCase):
    def setUp(self):
        # 模拟评论数据
        self.test_comments = [
            {
                "id": "1",
                "productId": "P001",
                "userId": "U001",
                "nickname": "测试用户1",
                "rating": 5,
                "content": "非常好用的产品",
                "images": ["http://example.com/img1.jpg"],
                "usefulness": 10,
                "status": "approved",
                "createTime": (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                "id": "2",
                "productId": "P001",
                "userId": "U002",
                "nickname": "测试用户2",
                "rating": 3,
                "content": "一般般",
                "usefulness": 5,
                "status": "approved",
                "createTime": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "id": "3",
                "productId": "P001",
                "userId": "U003",
                "nickname": "测试用户3",
                "rating": 4,
                "content": "还不错",
                "usefulness": 8,
                "status": "approved",
                "createTime": datetime.now().isoformat()
            }
        ]
        
        # 模拟订单数据
        self.test_orders = {
            "O001": {
                "userId": "U001",
                "productId": "P001",
                "status": "delivered",
                "deliveryTime": (datetime.now() - timedelta(days=5)).isoformat()
            },
            "O002": {
                "userId": "U002",
                "productId": "P002",
                "status": "pending",
                "deliveryTime": None
            }
        }

    def test_get_comments_sort_by_time(self):
        """测试按时间排序"""
        sorted_comments = sorted(
            self.test_comments,
            key=lambda x: x["createTime"],
            reverse=True
        )
        self.assertEqual(
            [c["id"] for c in sorted_comments],
            ["3", "2", "1"]
        )

    def test_get_comments_sort_by_rating(self):
        """测试按评分排序"""
        sorted_comments = sorted(
            self.test_comments,
            key=lambda x: x["rating"],
            reverse=True
        )
        self.assertEqual(
            [c["id"] for c in sorted_comments],
            ["1", "3", "2"]
        )

    def test_get_comments_sort_by_usefulness(self):
        """测试按有用度排序"""
        sorted_comments = sorted(
            self.test_comments,
            key=lambda x: x["usefulness"],
            reverse=True
        )
        self.assertEqual(
            [c["id"] for c in sorted_comments],
            ["1", "3", "2"]
        )

    def test_create_comment_check_eligibility(self):
        """测试创建评论的资格检查"""
        # 模拟已收货用户
        self.assertTrue(self._check_comment_eligibility("U001", "P001"))
        
        # 模拟未收货用户
        self.assertFalse(self._check_comment_eligibility("U002", "P002"))
        
        # 模拟无订单用户
        self.assertFalse(self._check_comment_eligibility("U003", "P003"))

    def test_modify_comment_time_limit(self):
        """测试评论修改的时间限制"""
        # 2天前的评论可以修改
        self.assertTrue(
            self._check_modification_allowed(
                datetime.now() - timedelta(days=2)
            )
        )
        
        # 8天前的评论不能修改
        self.assertFalse(
            self._check_modification_allowed(
                datetime.now() - timedelta(days=8)
            )
        )

    def test_delete_comment_time_limit(self):
        """测试评论删除的时间限制"""
        # 2天前的评论可以删除
        self.assertTrue(
            self._check_deletion_allowed(
                datetime.now() - timedelta(days=2)
            )
        )
        
        # 8天前的评论不能删除
        self.assertFalse(
            self._check_deletion_allowed(
                datetime.now() - timedelta(days=8)
            )
        )

    def test_comment_validation(self):
        """测试评论内容验证"""
        # 有效的评论
        valid_comment = {
            "productId": "P001",
            "rating": 5,
            "content": "这是一个有效的评论",
            "images": ["http://example.com/img1.jpg"]
        }
        self.assertTrue(self._validate_comment(valid_comment))
        
        # 无效评论：缺少必需字段
        invalid_comment1 = {
            "productId": "P001",
            "content": "缺少评分"
        }
        self.assertFalse(self._validate_comment(invalid_comment1))
        
        # 无效评论：评分超出范围
        invalid_comment2 = {
            "productId": "P001",
            "rating": 6,
            "content": "评分超出范围"
        }
        self.assertFalse(self._validate_comment(invalid_comment2))

    def _check_comment_eligibility(self, user_id, product_id):
        """检查用户是否有资格评论"""
        for order in self.test_orders.values():
            if (order["userId"] == user_id and 
                order["productId"] == product_id and 
                order["status"] == "delivered"):
                return True
        return False

    def _check_modification_allowed(self, create_time):
        """检查是否允许修改评论"""
        time_diff = datetime.now() - datetime.fromisoformat(create_time.isoformat())
        return time_diff.days < 7

    def _check_deletion_allowed(self, create_time):
        """检查是否允许删除评论"""
        time_diff = datetime.now() - datetime.fromisoformat(create_time.isoformat())
        return time_diff.days < 7

    def _validate_comment(self, comment):
        """验证评论数据"""
        required_fields = ["productId", "rating", "content"]
        
        # 检查必需字段
        if not all(field in comment for field in required_fields):
            return False
            
        # 验证评分范围
        if not (1 <= comment["rating"] <= 5):
            return False
            
        return True

class TestResourceNameRecognition(unittest.TestCase):
    """测试API资源名称识别功能"""
    
    def setUp(self):
        from apispec_generator.api_generator import APISpecGenerator
        self.generator = APISpecGenerator()

    def test_article_recognition(self):
        """测试文章资源识别"""
        story_data = {
            "role": "内容编辑",
            "goal": "创建和管理文章内容",
            "value": "方便内容管理",
            "criteria": [
                "支持创建新文章",
                "可以编辑文章内容",
                "必填字段：标题、内容、分类"
            ]
        }
        resource_info = self.generator._analyze_resource_and_actions(story_data['goal'], story_data['criteria'])
        self.assertEqual(resource_info['resource_name'], "Article")
        self.assertEqual(resource_info['resource_chinese'], "文章")

    def test_product_recognition(self):
        """测试商品资源识别"""
        story_data = {
            "role": "商家",
            "goal": "管理商品信息",
            "value": "及时更新商品状态",
            "criteria": [
                "可以添加新商品",
                "修改商品价格和库存",
                "必填字段：名称、价格、描述"
            ]
        }
        resource_info = self.generator._analyze_resource_and_actions(story_data['goal'], story_data['criteria'])
        self.assertEqual(resource_info['resource_name'], "Product")
        self.assertEqual(resource_info['resource_chinese'], "商品")

    def test_comment_recognition(self):
        """测试评论资源识别"""
        story_data = {
            "role": "用户",
            "goal": "发表商品评论",
            "value": "分享使用体验",
            "criteria": [
                "可以添加评论内容",
                "上传评论图片",
                "必填字段：评分、内容"
            ]
        }
        resource_info = self.generator._analyze_resource_and_actions(story_data['goal'], story_data['criteria'])
        self.assertEqual(resource_info['resource_name'], "Comment")
        self.assertEqual(resource_info['resource_chinese'], "评论")

    def test_domain_specific_recognition(self):
        """测试特定领域资源识别"""
        story_data = {
            "role": "餐厅经理",
            "goal": "管理餐厅菜单",
            "value": "及时更新菜品信息",
            "criteria": [
                "添加新的菜品",
                "更新菜品价格",
                "必填字段：菜品名称、价格、描述"
            ]
        }
        resource_info = self.generator._analyze_resource_and_actions(story_data['goal'], story_data['criteria'])
        self.assertEqual(resource_info['resource_name'], "Dish")
        self.assertEqual(resource_info['resource_chinese'], "菜品")
        self.assertEqual(resource_info['domain_type'], "餐饮")

if __name__ == '__main__':
    unittest.main()