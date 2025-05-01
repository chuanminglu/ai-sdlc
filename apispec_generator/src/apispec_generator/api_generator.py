"""
API 规范生成器模块

该模块负责:
1. 根据用户故事生成标准的 OpenAPI 规范
2. 验证生成的 API 规范的完整性和正确性
3. 提供错误处理和数据校验机制
"""

from typing import Dict, List, Optional, Any
import json
import re
from enum import Enum
from datetime import datetime
import sys
import os

# 添加父目录到路径，以便能够导入父目录中的模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from logger import logger
from config_manager import ConfigManager

# 创建配置管理器实例
config_manager = ConfigManager()

class ValidationError(Exception):
    """API 规范验证错误"""
    pass

class ResourceAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"
    VERIFY = "verify"
    PROCESS = "process"

class APISpecGenerator:
    """API 规范生成器"""
    
    DOMAIN_RESOURCES = {
        "新闻": {
            "article": "文章",
            "category": "分类",
            "tag": "标签",
            "comment": "评论"
        },
        "电商": {
            "product": "商品",
            "order": "订单",
            "cart": "购物车",
            "review": "评价"
        },
        "用户": {
            "user": "用户",
            "profile": "个人资料",
            "account": "账户"
        },
        "博客": {
            "post": "博文",
            "category": "分类",
            "tag": "标签",
            "comment": "评论"
        },
        "餐饮": {
            "dish": "菜品",
            "menu": "菜单",
            "order": "订单",
            "review": "评价"
        }
    }

    @staticmethod
    def validate_api_spec(api_spec: Dict, criteria: List[str]) -> Dict:
        """
        验证生成的API规范是否满足验收标准和技术约束
        :param api_spec: API规范字典
        :param criteria: 验收标准列表
        :return: 验证结果字典
        :raises: ValidationError 当验证失败时
        """
        logger.info("开始验证 API 规范")
        validation_results = {
            'isValid': True,
            'errors': [],
            'warnings': [],
            'validationTime': datetime.now().isoformat()
        }

        try:
            # 1. 验证 API 规范基本结构
            APISpecGenerator._validate_spec_structure(api_spec, validation_results)
            
            # 2. 验证 API 端点
            APISpecGenerator._validate_endpoints(api_spec, validation_results)
            
            # 3. 验证数据模型
            APISpecGenerator._validate_data_models(api_spec, validation_results)
            
            # 4. 验证验收标准
            APISpecGenerator._validate_acceptance_criteria(api_spec, criteria, validation_results)
            
            # 5. 验证技术约束
            APISpecGenerator._validate_technical_constraints(api_spec, validation_results)

            if validation_results['errors']:
                validation_results['isValid'] = False
                error_msg = "API 规范验证失败:\n" + "\n".join(validation_results['errors'])
                logger.error(error_msg)
                raise ValidationError(error_msg)

            logger.info("API 规范验证通过")
            
        except Exception as e:
            logger.error(f"API 规范验证过程出错: {str(e)}")
            validation_results['isValid'] = False
            validation_results['errors'].append(str(e))

        return validation_results

    @staticmethod
    def _validate_spec_structure(api_spec: Dict, results: Dict):
        """验证 API 规范的基本结构"""
        required_fields = ['openapi', 'info', 'paths', 'components']
        for field in required_fields:
            if field not in api_spec:
                results['errors'].append(f"API规范缺少必需的 {field} 字段")
                results['isValid'] = False
                return

        # 验证版本号
        if not api_spec['openapi'].startswith('3.'):
            results['errors'].append("API规范必须使用 OpenAPI 3.x 版本")
            results['isValid'] = False

        # 验证信息字段
        info = api_spec['info']
        if 'title' not in info or 'version' not in info:
            results['errors'].append("API规范的 info 字段必须包含 title 和 version")
            results['isValid'] = False

    @staticmethod
    def _validate_endpoints(api_spec: Dict, results: Dict):
        """验证 API 端点的完整性和一致性"""
        if 'paths' not in api_spec:
            results['errors'].append("API规范缺少paths定义")
            results['isValid'] = False
            return

        paths = api_spec['paths']
        seen_operations = set()  # 用于检测重复的操作ID

        for path, methods in paths.items():
            # 检查路径格式
            if not path.startswith('/'):
                results['errors'].append(f"路径 '{path}' 必须以/开头")
                results['isValid'] = False

            # 检查路径参数格式
            path_params = re.findall(r'{([^}]+)}', path)
            declared_params = set()

            # 检查 HTTP 方法
            for method, operation in methods.items():
                if method not in ['get', 'post', 'put', 'delete', 'patch']:
                    results['warnings'].append(f"路径 '{path}' 使用了不常见的HTTP方法 '{method}'")

                # 验证操作 ID 唯一性
                if 'operationId' in operation:
                    op_id = operation['operationId']
                    if op_id in seen_operations:
                        results['errors'].append(f"重复的操作ID: {op_id}")
                        results['isValid'] = False
                    seen_operations.add(op_id)

                # 验证必需字段
                required_op_fields = ['responses', 'summary']
                for field in required_op_fields:
                    if field not in operation:
                        results['errors'].append(f"路径 '{path}' 的 {method} 方法缺少 {field}")
                        results['isValid'] = False

                # 验证参数定义
                if 'parameters' in operation:
                    for param in operation['parameters']:
                        if param['in'] == 'path':
                            declared_params.add(param['name'])
                        
                        # 检查必需的参数字段
                        required_param_fields = ['name', 'in', 'schema']
                        for field in required_param_fields:
                            if field not in param:
                                results['errors'].append(
                                    f"路径 '{path}' 的 {method} 方法的参数缺少 {field} 字段"
                                )
                                results['isValid'] = False

                # 检查请求体格式
                if method in ['post', 'put', 'patch'] and 'requestBody' not in operation:
                    results['warnings'].append(
                        f"路径 '{path}' 的 {method} 方法可能需要请求体定义"
                    )

            # 确保所有路径参数都有对应的参数定义
            for param in path_params:
                if param not in declared_params:
                    results['errors'].append(f"路径 '{path}' 中的参数 '{param}' 缺少参数定义")
                    results['isValid'] = False

    @staticmethod
    def _validate_data_models(api_spec: Dict, results: Dict):
        """验证数据模型的完整性和一致性"""
        if 'components' not in api_spec or 'schemas' not in api_spec['components']:
            results['errors'].append("API规范缺少数据模型定义")
            results['isValid'] = False
            return

        schemas = api_spec['components']['schemas']
        for schema_name, schema in schemas.items():
            # 检查模型命名规范
            if not schema_name[0].isupper():
                results['warnings'].append(f"模型名称 '{schema_name}' 应使用大驼峰命名法")

            # 检查必需字段
            if 'type' not in schema:
                results['errors'].append(f"模型 '{schema_name}' 缺少type定义")
                results['isValid'] = False

            if schema.get('type') == 'object' and 'properties' not in schema:
                results['errors'].append(f"对象模型 '{schema_name}' 缺少properties定义")
                results['isValid'] = False
                continue

            # 检查属性定义
            if 'properties' in schema:
                for prop_name, prop in schema['properties'].items():
                    # 属性命名规范
                    if not prop_name[0].islower():
                        results['warnings'].append(
                            f"模型 '{schema_name}' 的属性 '{prop_name}' 应使用小驼峰命名法"
                        )

                    # 检查属性类型
                    if 'type' not in prop:
                        results['errors'].append(
                            f"模型 '{schema_name}' 的属性 '{prop_name}' 缺少type定义"
                        )
                        results['isValid'] = False

                    # 检查字符串类型的格式
                    if prop.get('type') == 'string' and 'format' in prop:
                        valid_formats = ['date-time', 'date', 'email', 'uri', 'uuid']
                        if prop['format'] not in valid_formats:
                            results['warnings'].append(
                                f"模型 '{schema_name}' 的属性 '{prop_name}' 使用了不标准的字符串格式 '{prop['format']}'"
                            )

                    # 检查数值类型的范围约束
                    if prop.get('type') in ['integer', 'number']:
                        if 'minimum' in prop and 'maximum' in prop:
                            if prop['minimum'] > prop['maximum']:
                                results['errors'].append(
                                    f"模型 '{schema_name}' 的属性 '{prop_name}' 的最小值大于最大值"
                                )
                                results['isValid'] = False

            # 检查必需属性定义
            if 'required' in schema:
                props = schema.get('properties', {})
                for required_prop in schema['required']:
                    if required_prop not in props:
                        results['errors'].append(
                            f"模型 '{schema_name}' 将不存在的属性 '{required_prop}' 标记为必需"
                        )
                        results['isValid'] = False

    @staticmethod
    def _validate_acceptance_criteria(api_spec: Dict, criteria: List[str], results: Dict):
        """验证 API 是否满足所有验收标准"""
        paths = api_spec.get('paths', {})
        schemas = api_spec.get('components', {}).get('schemas', {})
        
        for criterion in criteria:
            criterion = criterion.lower()
            
            # 检查 CRUD 操作要求
            if any(word in criterion for word in ['创建', '新建', '添加']):
                if not any("/create" in path or "post" in methods for path, methods in paths.items()):
                    results['errors'].append("验收标准要求创建功能，但API中未定义相关端点")
                    results['isValid'] = False
            
            if any(word in criterion for word in ['查询', '获取', '查看']):
                if not any("get" in methods for methods in paths.values()):
                    results['errors'].append("验收标准要求查询功能，但API中未定义相关端点")
                    results['isValid'] = False
            
            if any(word in criterion for word in ['更新', '修改', '编辑']):
                if not any("put" in methods or "patch" in methods for methods in paths.values()):
                    results['errors'].append("验收标准要求更新功能，但API中未定义相关端点")
                    results['isValid'] = False
            
            if any(word in criterion for word in ['删除', '移除']):
                if not any("delete" in methods for methods in paths.values()):
                    results['errors'].append("验收标准要求删除功能，但API中未定义相关端点")
                    results['isValid'] = False
            
            # 检查分页要求
            if "分页" in criterion:
                list_endpoints = [
                    methods['get'] for path, methods in paths.items() 
                    if 'get' in methods and ('list' in path or path.endswith('s'))
                ]
                for endpoint in list_endpoints:
                    params = endpoint.get('parameters', [])
                    if not any(p['name'] in ['page', 'pageSize', 'limit', 'offset'] for p in params):
                        results['errors'].append("验收标准要求分页功能，但列表接口未定义分页参数")
                        results['isValid'] = False
            
            # 检查排序要求
            if "排序" in criterion:
                list_endpoints = [
                    methods['get'] for path, methods in paths.items()
                    if 'get' in methods and ('list' in path or path.endswith('s'))
                ]
                for endpoint in list_endpoints:
                    params = endpoint.get('parameters', [])
                    if not any(p['name'] in ['sortBy', 'orderBy', 'sort', 'order'] for p in params):
                        results['errors'].append("验收标准要求排序功能，但列表接口未定义排序参数")
                        results['isValid'] = False
            
            # 检查搜索要求
            if "搜索" in criterion:
                if not any("/search" in path or 
                          any('q' in param.get('name', '') or 'keyword' in param.get('name', '')
                              for methods in paths.values()
                              for method in methods.values()
                              for param in method.get('parameters', []))
                          for path in paths):
                    results['errors'].append("验收标准要求搜索功能，但API中未定义搜索相关端点或参数")
                    results['isValid'] = False

            # 检查状态管理要求
            if "状态" in criterion or "审核" in criterion:
                for schema in schemas.values():
                    if 'properties' in schema:
                        has_status = any(
                            prop_name in ['status', 'state'] 
                            for prop_name in schema['properties']
                        )
                        if not has_status:
                            results['warnings'].append(
                                "验收标准涉及状态管理，建议在相关模型中添加状态字段"
                            )

    @staticmethod
    def _validate_technical_constraints(api_spec: Dict, results: Dict):
        """验证API是否满足技术约束"""
        # 1. 验证 API 版本兼容性
        openapi_version = api_spec.get('openapi', '')
        if not openapi_version.startswith('3.'):
            results['errors'].append("API规范必须使用OpenAPI 3.x版本")
            results['isValid'] = False
        elif openapi_version == '3.0.0':
            results['warnings'].append("建议使用最新的OpenAPI 3.1.0版本")

        # 2. 验证安全定义
        if 'security' not in api_spec and 'securitySchemes' not in api_spec.get('components', {}):
            results['warnings'].append("API规范未定义安全机制")

        # 3. 验证响应格式
        paths = api_spec.get('paths', {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                responses = operation.get('responses', {})
                
                # 检查是否定义了成功响应
                if '200' not in responses and '201' not in responses:
                    results['warnings'].append(
                        f"路径 '{path}' 的 {method} 方法未定义成功响应"
                    )

                # 检查响应格式
                for status, response in responses.items():
                    if 'content' in response:
                        content_types = response['content'].keys()
                        if 'application/json' not in content_types:
                            results['warnings'].append(
                                f"路径 '{path}' 的 {method} 方法的 {status} 响应未使用JSON格式"
                            )

                    # 检查错误响应的错误码格式
                    if status.startswith('4') or status.startswith('5'):
                        if 'content' not in response:
                            results['warnings'].append(
                                f"路径 '{path}' 的 {method} 方法的错误响应 {status} 应该包含错误详情"
                            )

        # 4. 验证数据一致性
        components = api_spec.get('components', {})
        schemas = components.get('schemas', {})
        
        # 检查模型引用的有效性
        for schema_name, schema in schemas.items():
            APISpecGenerator._validate_schema_references(
                schema, schemas, f"模型 '{schema_name}'", results
            )

        # 5. 验证API命名规范
        path_pattern = re.compile(r'^/[a-z0-9-]+(/[a-z0-9-{}]+)*$')
        for path in paths:
            if not path_pattern.match(path):
                results['warnings'].append(
                    f"路径 '{path}' 应该使用小写字母、数字和连字符，以/开头"
                )

    @staticmethod
    def _validate_schema_references(schema: Dict, all_schemas: Dict, context: str, results: Dict):
        """递归验证模型引用的有效性"""
        if isinstance(schema, dict):
            # 检查直接引用
            if '$ref' in schema:
                ref = schema['$ref']
                if ref.startswith('#/components/schemas/'):
                    schema_name = ref.split('/')[-1]
                    if schema_name not in all_schemas:
                        results['errors'].append(
                            f"{context} 引用了不存在的模型 '{schema_name}'"
                        )
                        results['isValid'] = False
            
            # 递归检查所有属性
            for value in schema.values():
                APISpecGenerator._validate_schema_references(
                    value, all_schemas, context, results
                )
        elif isinstance(schema, list):
            # 递归检查数组中的每个元素
            for item in schema:
                APISpecGenerator._validate_schema_references(
                    item, all_schemas, context, results
                )

    @staticmethod
    def generate_api_spec(user_story_data: Dict) -> Dict:
        """
        根据用户故事数据生成 API 规范
        :param user_story_data: 包含角色、目标和验收标准的用户故事数据字典
        :return: API 规范字典
        """
        role = user_story_data.get('role', '')
        goal = user_story_data.get('goal', '')
        value = user_story_data.get('value', '')
        criteria = user_story_data.get('criteria', [])
        
        # 从目标和验收标准中提取资源名称和操作
        resource_info = APISpecGenerator._analyze_resource_and_actions(goal, criteria)
        resource_name = resource_info['resource_name']
        resource_chinese = resource_info['resource_chinese']
        actions = resource_info['actions']
        domain_type = resource_info['domain_type']
        
        # 生成 API 端点
        endpoints = APISpecGenerator._generate_endpoints(resource_name, resource_chinese, actions, criteria)
        
        # 生成数据模型
        data_model = APISpecGenerator._generate_data_model(resource_name, resource_chinese, criteria)
        
        # 构建完整的 API 规范
        api_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{resource_name} API",
                "description": f"为{role}提供{resource_chinese}管理的 API，目的是{value}",
                "version": "1.0.0"
            },
            "paths": endpoints,
            "components": {
                "schemas": data_model
            }
        }
        
        # 验证生成的API规范
        validation_results = APISpecGenerator.validate_api_spec(api_spec, criteria)
        if not validation_results['isValid']:
            print("API规范验证失败:")
            for error in validation_results['errors']:
                print(f"- 错误: {error}")
            for warning in validation_results['warnings']:
                print(f"- 警告: {warning}")
        
        return api_spec

    @staticmethod
    def save_api_spec(api_spec: Dict, output_path: str):
        """
        将 API 规范保存为 JSON 文件
        :param api_spec: API 规范字典
        :param output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(api_spec, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _analyze_resource_and_actions(goal: str, criteria: List[str]) -> Dict:
        """
        分析目标和验收标准，提取资源名称和操作
        :param goal: 用户故事目标
        :param criteria: 验收标准列表
        :return: 包含资源信息的字典
        """
        # 初始化结果
        result = {
            'resource_name': '',
            'resource_chinese': '',
            'actions': set(),
            'domain_type': ''
        }
        
        # 分析资源名称
        for domain, resources in APISpecGenerator.DOMAIN_RESOURCES.items():
            for eng, chn in resources.items():
                if chn in goal:
                    result['resource_name'] = eng
                    result['resource_chinese'] = chn
                    result['domain_type'] = domain
                    break
            if result['resource_name']:
                break
                
        # 如果没找到匹配的资源，使用默认值
        if not result['resource_name']:
            # 提取第一个名词作为资源名
            nouns = [word for word in goal.split() if len(word) >= 2]
            if nouns:
                result['resource_chinese'] = nouns[0]
                result['resource_name'] = 'resource'  # 默认英文名
                result['domain_type'] = '通用'
        
        # 分析操作类型
        action_keywords = {
            'create': ['创建', '新建', '添加'],
            'read': ['查看', '获取', '读取'],
            'update': ['更新', '修改', '编辑'],
            'delete': ['删除', '移除'],
            'list': ['列表', '查询'],
            'search': ['搜索'],
            'verify': ['验证', '审核'],
            'process': ['处理', '发布']
        }
        
        # 从目标中提取操作
        for action, keywords in action_keywords.items():
            if any(keyword in goal for keyword in keywords):
                result['actions'].add(action)
                
        # 从验收标准中提取补充操作
        for criterion in criteria:
            for action, keywords in action_keywords.items():
                if any(keyword in criterion for keyword in keywords):
                    result['actions'].add(action)
        
        # 如果没有检测到任何操作，添加默认的CRUD操作
        if not result['actions']:
            result['actions'].update(['create', 'read', 'update', 'delete'])
            
        # 将集合转换为列表以便JSON序列化
        result['actions'] = list(result['actions'])
        
        return result

    @staticmethod
    def _generate_endpoints(resource_name: str, resource_chinese: str, actions: List[str], criteria: List[str]) -> Dict:
        """
        生成API端点定义
        :param resource_name: 资源英文名称
        :param resource_chinese: 资源中文名称
        :param actions: 操作列表
        :param criteria: 验收标准列表
        :return: API端点定义字典
        """
        endpoints = {}
        base_path = f"/{resource_name}s"  # 使用复数形式作为基础路径
        
        # 分析验收标准中的特殊要求
        needs_pagination = any("分页" in criterion for criterion in criteria)
        needs_sorting = any("排序" in criterion for criterion in criteria)
        needs_search = any("搜索" in criterion for criterion in criteria)
        needs_status = any("状态" in criterion or "审核" in criterion for criterion in criteria)
        
        # 生成端点定义
        if 'create' in actions:
            endpoints[f"{base_path}/create"] = {
                "post": {
                    "tags": [resource_chinese],
                    "summary": f"创建{resource_chinese}",
                    "operationId": f"create{resource_name.capitalize()}",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{resource_name.capitalize()}Create"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": f"成功创建{resource_chinese}",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{resource_name.capitalize()}"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "请求参数错误",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
            
        if 'read' in actions:
            endpoints[f"{base_path}/{{id}}"] = {
                "get": {
                    "tags": [resource_chinese],
                    "summary": f"获取{resource_chinese}详情",
                    "operationId": f"get{resource_name.capitalize()}ById",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": f"成功获取{resource_chinese}详情",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{resource_name.capitalize()}"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": f"{resource_chinese}不存在",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
            
        if 'update' in actions:
            endpoints[f"{base_path}/{{id}}"]["put"] = {
                "tags": [resource_chinese],
                "summary": f"更新{resource_chinese}",
                "operationId": f"update{resource_name.capitalize()}",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{resource_name.capitalize()}Update"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": f"成功更新{resource_chinese}",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{resource_name.capitalize()}"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": f"{resource_chinese}不存在",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
            
        if 'delete' in actions:
            endpoints[f"{base_path}/{{id}}"]["delete"] = {
                "tags": [resource_chinese],
                "summary": f"删除{resource_chinese}",
                "operationId": f"delete{resource_name.capitalize()}",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "204": {
                        "description": f"成功删除{resource_chinese}"
                    },
                    "404": {
                        "description": f"{resource_chinese}不存在",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
            
        if 'list' in actions or needs_pagination:
            list_parameters = [
                {
                    "name": "page",
                    "in": "query",
                    "description": "页码",
                    "schema": {"type": "integer", "default": 1}
                },
                {
                    "name": "pageSize",
                    "in": "query",
                    "description": "每页数量",
                    "schema": {"type": "integer", "default": 10}
                }
            ]
            
            if needs_sorting:
                list_parameters.extend([
                    {
                        "name": "sortBy",
                        "in": "query",
                        "description": "排序字段",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "order",
                        "in": "query",
                        "description": "排序方向(asc/desc)",
                        "schema": {"type": "string", "enum": ["asc", "desc"]}
                    }
                ])
                
            endpoints[base_path] = {
                "get": {
                    "tags": [resource_chinese],
                    "summary": f"获取{resource_chinese}列表",
                    "operationId": f"list{resource_name.capitalize()}s",
                    "parameters": list_parameters,
                    "responses": {
                        "200": {
                            "description": f"成功获取{resource_chinese}列表",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "total": {"type": "integer"},
                                            "items": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": f"#/components/schemas/{resource_name.capitalize()}"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
        if needs_search or 'search' in actions:
            endpoints[f"{base_path}/search"] = {
                "get": {
                    "tags": [resource_chinese],
                    "summary": f"搜索{resource_chinese}",
                    "operationId": f"search{resource_name.capitalize()}s",
                    "parameters": [
                        {
                            "name": "keyword",
                            "in": "query",
                            "description": "搜索关键词",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": f"成功搜索{resource_chinese}",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": f"#/components/schemas/{resource_name.capitalize()}"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
        if needs_status:
            endpoints[f"{base_path}/{{id}}/status"] = {
                "put": {
                    "tags": [resource_chinese],
                    "summary": f"更新{resource_chinese}状态",
                    "operationId": f"update{resource_name.capitalize()}Status",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["status"],
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "enum": ["draft", "published", "archived"]
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": f"成功更新{resource_chinese}状态",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{resource_name.capitalize()}"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
        return endpoints

    @staticmethod
    def _generate_data_model(resource_name: str, resource_chinese: str, criteria: List[str]) -> Dict:
        """
        生成数据模型定义
        :param resource_name: 资源英文名称
        :param resource_chinese: 资源中文名称
        :param criteria: 验收标准列表
        :return: 数据模型定义字典
        """
        # 分析验收标准中的字段要求
        required_fields = []
        optional_fields = []
        needs_status = False
        
        for criterion in criteria:
            # 提取必填字段
            if "必填" in criterion or "必需" in criterion:
                fields = criterion.split("：")[-1].split("、")
                required_fields.extend(fields)
            # 提取可选字段
            elif "可选" in criterion:
                fields = criterion.split("：")[-1].split("、")
                optional_fields.extend(fields)
            # 检查是否需要状态字段
            if "状态" in criterion or "审核" in criterion:
                needs_status = True
                
        # 基础模型
        base_model = {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "唯一标识符"
                },
                "createdAt": {
                    "type": "string",
                    "format": "date-time",
                    "description": "创建时间"
                },
                "updatedAt": {
                    "type": "string",
                    "format": "date-time",
                    "description": "更新时间"
                }
            }
        }
        
        # 处理必填字段
        for field in required_fields:
            field_name = field.strip()
            if field_name:
                base_model["properties"][field_name] = {
                    "type": "string",
                    "description": f"{field_name}内容"
                }
                
        # 处理可选字段
        for field in optional_fields:
            field_name = field.strip()
            if field_name:
                base_model["properties"][field_name] = {
                    "type": "string",
                    "description": f"{field_name}内容"
                }
                
        # 添加状态字段
        if needs_status:
            base_model["properties"]["status"] = {
                "type": "string",
                "enum": ["draft", "published", "archived"],
                "default": "draft",
                "description": "资源状态"
            }
            
        # 设置必需属性
        base_model["required"] = ["id"] + [field.strip() for field in required_fields if field.strip()]
        
        # 生成错误模型
        error_model = {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {
                    "type": "string",
                    "description": "错误代码"
                },
                "message": {
                    "type": "string",
                    "description": "错误信息"
                }
            }
        }
        
        # 返回所有模型定义
        return {
            resource_name.capitalize(): base_model,
            f"{resource_name.capitalize()}Create": {
                "type": "object",
                "required": [field.strip() for field in required_fields if field.strip()],
                "properties": {
                    field.strip(): base_model["properties"][field.strip()]
                    for field in (required_fields + optional_fields)
                    if field.strip() in base_model["properties"]
                }
            },
            f"{resource_name.capitalize()}Update": {
                "type": "object",
                "properties": {
                    field.strip(): base_model["properties"][field.strip()]
                    for field in (required_fields + optional_fields)
                    if field.strip() in base_model["properties"]
                }
            },
            "Error": error_model
        }