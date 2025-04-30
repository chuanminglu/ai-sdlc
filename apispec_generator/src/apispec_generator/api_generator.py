from typing import Dict, List, Optional
import json

class APISpecGenerator:
    """API 规范生成器"""
    
    @staticmethod
    def generate_api_spec(user_story_data: Dict) -> Dict:
        """
        根据用户故事数据生成 API 规范
        :param user_story_data: 包含角色、目标和验收标准的用户故事数据字典
        :return: API 规范字典
        """
        role = user_story_data.get('role', '')
        goal = user_story_data.get('goal', '')
        criteria = user_story_data.get('criteria', [])
        
        # 从目标中提取资源名称
        resource_name = "Product Review"
        
        # 生成 API 端点
        endpoints = APISpecGenerator._generate_endpoints(resource_name, goal, criteria)
        
        # 生成数据模型
        data_model = APISpecGenerator._generate_data_model(resource_name, criteria)
        
        # 构建完整的 API 规范
        api_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{resource_name} API",
                "description": f"为{role}提供{goal}的 API",
                "version": "1.0.0"
            },
            "paths": endpoints,
            "components": {
                "schemas": data_model
            }
        }
        
        return api_spec

    @staticmethod
    def _generate_endpoints(resource_name: str, goal: str, criteria: List[str]) -> Dict:
        """
        生成 API 端点
        """
        endpoints = {}
        base_path = "/comments"
        
        # 获取评论列表接口
        endpoints[base_path] = {
            "get": {
                "summary": "获取商品评论列表",
                "description": "获取商品的评论列表，支持多种排序方式",
                "parameters": [
                    {
                        "name": "productId",
                        "in": "query",
                        "required": True,
                        "description": "商品ID",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "sortBy",
                        "in": "query",
                        "description": "排序字段：time（时间）、rating（评分）、usefulness（有用度）",
                        "schema": {
                            "type": "string",
                            "enum": ["time", "rating", "usefulness"],
                            "default": "time"
                        }
                    },
                    {
                        "name": "order",
                        "in": "query",
                        "description": "排序方向",
                        "schema": {
                            "type": "string",
                            "enum": ["desc", "asc"],
                            "default": "desc"
                        }
                    },
                    {
                        "name": "page",
                        "in": "query",
                        "description": "页码",
                        "schema": {
                            "type": "integer",
                            "default": 1,
                            "minimum": 1
                        }
                    },
                    {
                        "name": "pageSize",
                        "in": "query",
                        "description": "每页条数",
                        "schema": {
                            "type": "integer",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功获取评论列表",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total": {
                                            "type": "integer",
                                            "description": "总评论数"
                                        },
                                        "items": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Comment"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "创建商品评论",
                "description": "为已购买的商品创建评论",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "productId": {
                                        "type": "string",
                                        "description": "商品ID"
                                    },
                                    "rating": {
                                        "type": "number",
                                        "description": "评分",
                                        "minimum": 1,
                                        "maximum": 5
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "评价内容"
                                    },
                                    "images": {
                                        "type": "array",
                                        "description": "评价图片",
                                        "items": {
                                            "type": "string",
                                            "format": "uri"
                                        }
                                    },
                                    "videos": {
                                        "type": "array",
                                        "description": "评价视频",
                                        "items": {
                                            "type": "string",
                                            "format": "uri"
                                        }
                                    }
                                },
                                "required": ["productId", "rating", "content"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "评论创建成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Comment"
                                }
                            }
                        }
                    },
                    "403": {
                        "description": "未满足评论条件（如未购买或未收货）"
                    }
                }
            }
        }

        # 评论状态检查接口
        endpoints[f"{base_path}/status"] = {
            "get": {
                "summary": "检查评论资格",
                "description": "检查用户是否可以对指定商品进行评论",
                "parameters": [
                    {
                        "name": "productId",
                        "in": "query",
                        "required": True,
                        "description": "商品ID",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功获取评论资格状态",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "canComment": {
                                            "type": "boolean",
                                            "description": "是否可以评论"
                                        },
                                        "reason": {
                                            "type": "string",
                                            "description": "如果不能评论，说明原因"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # 单个评论操作接口
        endpoints[f"{base_path}/{{id}}"] = {
            "put": {
                "summary": "修改评论",
                "description": "修改已发布的评论（仅支持7天内修改）",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "description": "评论ID",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "rating": {
                                        "type": "number",
                                        "description": "评分",
                                        "minimum": 1,
                                        "maximum": 5
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "评价内容"
                                    },
                                    "images": {
                                        "type": "array",
                                        "description": "评价图片",
                                        "items": {
                                            "type": "string",
                                            "format": "uri"
                                        }
                                    },
                                    "videos": {
                                        "type": "array",
                                        "description": "评价视频",
                                        "items": {
                                            "type": "string",
                                            "format": "uri"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "评论修改成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Comment"
                                }
                            }
                        }
                    },
                    "403": {
                        "description": "评论已超过7天，不能修改"
                    },
                    "404": {
                        "description": "评论不存在"
                    }
                }
            },
            "delete": {
                "summary": "删除评论",
                "description": "删除已发布的评论（仅支持7天内删除）",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "description": "评论ID",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "204": {
                        "description": "评论删除成功"
                    },
                    "403": {
                        "description": "评论已超过7天，不能删除"
                    },
                    "404": {
                        "description": "评论不存在"
                    }
                }
            }
        }
        
        return endpoints

    @staticmethod
    def _generate_data_model(resource_name: str, criteria: List[str]) -> Dict:
        """
        生成数据模型
        """
        return {
            "Comment": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "评论ID"
                    },
                    "productId": {
                        "type": "string",
                        "description": "商品ID"
                    },
                    "userId": {
                        "type": "string",
                        "description": "用户ID"
                    },
                    "nickname": {
                        "type": "string",
                        "description": "用户昵称"
                    },
                    "rating": {
                        "type": "number",
                        "description": "评分",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "content": {
                        "type": "string",
                        "description": "评价内容"
                    },
                    "images": {
                        "type": "array",
                        "description": "评价图片",
                        "items": {
                            "type": "string",
                            "format": "uri"
                        }
                    },
                    "videos": {
                        "type": "array",
                        "description": "评价视频",
                        "items": {
                            "type": "string",
                            "format": "uri"
                        }
                    },
                    "usefulness": {
                        "type": "integer",
                        "description": "点赞数量",
                        "minimum": 0
                    },
                    "reply": {
                        "type": "string",
                        "description": "商家回复"
                    },
                    "status": {
                        "type": "string",
                        "description": "评论状态",
                        "enum": ["pending", "approved", "rejected"]
                    },
                    "createTime": {
                        "type": "string",
                        "format": "date-time",
                        "description": "评价时间"
                    },
                    "updateTime": {
                        "type": "string",
                        "format": "date-time",
                        "description": "更新时间"
                    }
                },
                "required": [
                    "id",
                    "productId",
                    "userId",
                    "rating",
                    "content",
                    "createTime"
                ]
            }
        }

    @staticmethod
    def save_api_spec(api_spec: Dict, output_path: str):
        """
        将 API 规范保存为 JSON 文件
        :param api_spec: API 规范字典
        :param output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(api_spec, f, ensure_ascii=False, indent=2)