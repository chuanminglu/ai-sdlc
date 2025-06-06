"""
极客书店需求样例 - 用于演示需求冲突检测功能
"""

# 极客书店需求样例
GEEK_BOOKSTORE_REQUIREMENTS = {
    "功能需求": [
        {
            "id": "F001",
            "title": "用户注册登录",
            "description": "用户可以通过邮箱注册账号，注册时需要设置密码并同意用户协议。已注册用户可以使用邮箱和密码登录系统。",
            "priority": "高",
            "owner": "用户管理团队",
        },
        {
            "id": "F002",
            "title": "社交账号一键登录",
            "description": "用户可以使用微信、QQ等社交账号直接登录系统，无需额外注册。首次使用社交账号登录时自动创建账号。",
            "priority": "中",
            "owner": "用户管理团队",
        },
        {
            "id": "F003",
            "title": "图书浏览与搜索",
            "description": "用户可以浏览全部图书，支持按分类、上架时间、热度等方式筛选。用户可以通过关键词搜索图书标题、作者、出版社等信息。",
            "priority": "高", 
            "owner": "商品团队",
        },
        {
            "id": "F004",
            "title": "会员专享内容",
            "description": "会员用户可以查看和下载电子书样章。会员分为初级、中级和高级，不同级别可以查看的样章数量不同。",
            "priority": "中",
            "owner": "会员团队",
        },
        {
            "id": "F005",
            "title": "免费用户内容访问",
            "description": "免费用户可以查看所有电子书样章，但每月仅限下载5章。",
            "priority": "中",
            "owner": "内容团队",
        },
        {
            "id": "F006", 
            "title": "用户购买图书",
            "description": "用户选择图书后可以添加到购物车，在购物车中可以调整购买数量，并使用优惠券。结算时需支持多种支付方式。",
            "priority": "高",
            "owner": "交易团队",
        },
        {
            "id": "F007",
            "title": "在线客服",
            "description": "用户在浏览图书或购买过程中可以随时联系在线客服获取帮助。仅工作时间（9:00-18:00）提供人工客服服务。",
            "priority": "低",
            "owner": "客服团队",
        },
        {
            "id": "F008",
            "title": "7天无理由退货",
            "description": "用户购买的实体图书支持7天无理由退货，但电子书购买后不支持退款。",
            "priority": "中",
            "owner": "交易团队",
        },
        {
            "id": "F009",
            "title": "用户权限管理",
            "description": "系统管理员可以设置和调整不同角色的操作权限，包括普通用户、会员用户、店员和管理员等角色。",
            "priority": "高",
            "owner": "系统管理团队",
        },
        {
            "id": "F010", 
            "title": "退款流程",
            "description": "所有商品不论实体还是电子商品，购买后15天内均可申请退款，需人工审核通过。",
            "priority": "高",
            "owner": "交易团队",
        }
    ],
    "非功能需求": [
        {
            "id": "NF001",
            "title": "系统响应时间",
            "description": "系统页面加载时间不超过3秒，搜索结果返回时间不超过1秒。",
            "priority": "高",
            "owner": "技术团队",
        },
        {
            "id": "NF002", 
            "title": "系统可用性",
            "description": "系统全年可用性达到99.9%，计划内维护时间除外。",
            "priority": "高",
            "owner": "运维团队",
        }
    ]
}