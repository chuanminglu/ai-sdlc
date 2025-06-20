# API后端开发提示词

## 项目概述
开发一个RESTful API后端服务，用于管理用户数据和业务逻辑处理。

## 技术要求

### 技术栈
- Python 3.9+
- FastAPI框架
- SQLAlchemy ORM
- PostgreSQL数据库
- Redis缓存
- JWT认证

### 核心功能
1. **用户管理**: 注册、登录、权限管理
2. **数据CRUD**: 资源的增删改查操作
3. **认证授权**: JWT token和权限控制
4. **数据验证**: 请求参数验证和响应格式化
5. **缓存机制**: Redis缓存优化性能
6. **日志监控**: 完整的日志记录和监控

### 项目结构
```
api-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── items.py
│   ├── models/
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── item.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── user_service.py
│   └── utils/
│       ├── dependencies.py
│       └── helpers.py
├── tests/
├── requirements.txt
└── docker-compose.yml
```

## 代码生成指导

### 请帮我生成以下代码：

#### 1. 项目配置和设置
要求：
- FastAPI应用配置
- 数据库连接设置
- 环境变量管理
- CORS和中间件配置
- 日志配置

#### 2. 数据模型定义
要求：
- SQLAlchemy模型类
- 数据库表关系定义
- 字段验证和约束
- 时间戳和软删除支持
- 索引优化

#### 3. Pydantic数据模式
要求：
- 请求/响应模型
- 数据验证规则
- 序列化/反序列化
- 错误处理模式
- 分页响应模式

#### 4. API路由和端点
要求：
- RESTful API设计
- 路径参数和查询参数
- 请求体验证
- 响应状态码
- API文档注释

#### 5. 认证和授权系统
要求：
- JWT token生成和验证
- 密码哈希和验证
- 权限装饰器
- 用户登录/注册
- 刷新token机制

#### 6. 业务逻辑服务层
要求：
- 业务逻辑封装
- 数据处理和转换
- 外部服务集成
- 缓存策略
- 异常处理

#### 7. 数据库操作
要求：
- CRUD操作封装
- 查询优化
- 事务处理
- 连接池管理
- 数据迁移

#### 8. 测试代码
要求：
- 单元测试
- 集成测试
- API测试
- 测试数据fixture
- 覆盖率报告

## 开发规范

### 代码质量要求
- 遵循PEP 8规范
- 使用类型注解
- 完整的文档字符串
- 错误处理和日志记录
- 代码复用和模块化

### 安全要求
- 输入验证和清理
- SQL注入防护
- XSS防护
- 率限制
- 敏感数据加密

### 性能要求
- 数据库查询优化
- 缓存策略
- 异步处理
- 连接池配置
- 监控和性能分析

## 示例提示

### 生成用户管理API示例：
"请生成一个完整的用户管理API，包括用户注册、登录、获取用户信息和更新用户信息的端点。使用FastAPI、SQLAlchemy和JWT认证。要求包含完整的数据验证、错误处理和API文档。"

### 生成数据模型示例：
"请生成SQLAlchemy数据模型，包括User和Item两个实体，User可以拥有多个Item。要求包含适当的字段类型、约束、关系定义和索引。使用PostgreSQL数据库。"

### 生成认证系统示例：
"请实现基于JWT的认证系统，包括用户注册、登录、token验证、权限检查等功能。要求安全的密码处理、token刷新机制和权限装饰器。"

### 生成服务层示例：
"请生成业务逻辑服务层代码，包括用户服务和商品服务。要求封装CRUD操作、业务逻辑处理、缓存集成和异常处理。使用依赖注入模式。"

## API设计规范

### 端点命名
- GET /api/v1/users - 获取用户列表
- POST /api/v1/users - 创建用户
- GET /api/v1/users/{id} - 获取单个用户
- PUT /api/v1/users/{id} - 更新用户
- DELETE /api/v1/users/{id} - 删除用户

### 响应格式
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2025-06-20T10:00:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {...},
  "timestamp": "2025-06-20T10:00:00Z"
}
```

## 输出格式要求
- 完整的Python代码文件
- 详细的类型注解
- 完整的文档字符串
- 单元测试用例
- 部署配置文件
- API文档说明
