# 数据库设计和优化提示词

## 项目概述
设计高效、可扩展的数据库架构，包括表结构设计、索引优化、查询性能调优等。

## 技术要求

### 技术栈
- PostgreSQL / MySQL
- SQLAlchemy ORM
- Redis缓存
- 数据库迁移工具
- 监控和性能分析工具

### 核心需求
1. **数据建模**: 实体关系设计和规范化
2. **性能优化**: 索引策略和查询优化
3. **数据完整性**: 约束和验证规则
4. **扩展性**: 分区和分片策略
5. **备份恢复**: 数据安全和灾难恢复
6. **监控分析**: 性能监控和分析

## 数据库设计指导

### 请帮我生成以下设计：

#### 1. 实体关系模型(ERD)
要求：
- 完整的实体定义
- 关系类型和基数
- 主键和外键设计
- 业务规则约束
- 数据字典说明

#### 2. 表结构设计
要求：
- 标准化设计（第三范式）
- 适当的反规范化
- 字段类型选择
- 默认值和约束
- 软删除支持

#### 3. 索引策略设计
要求：
- 主键和唯一索引
- 复合索引设计
- 查询性能优化
- 索引维护成本考虑
- 覆盖索引使用

#### 4. 查询优化
要求：
- 常用查询模式分析
- 执行计划优化
- JOIN策略选择
- 子查询优化
- 分页查询优化

#### 5. 数据分区策略
要求：
- 水平分区设计
- 垂直分区考虑
- 分区键选择
- 分区管理策略
- 跨分区查询处理

#### 6. 缓存策略
要求：
- Redis缓存设计
- 缓存失效策略
- 缓存穿透防护
- 热点数据识别
- 缓存一致性保证

## 设计模式和最佳实践

### 表设计模式
```sql
-- 基础表结构模板
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    CONSTRAINT chk_username_length CHECK (length(username) >= 3),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 索引设计
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_status ON users(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

### 关系设计模式
```sql
-- 一对多关系
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 多对多关系
CREATE TABLE user_roles (
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by BIGINT REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);
```

### 查询优化模式
```sql
-- 高效分页查询
SELECT * FROM posts 
WHERE id > :last_seen_id 
ORDER BY id 
LIMIT :page_size;

-- 复杂查询优化
SELECT u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id AND p.deleted_at IS NULL
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.username
HAVING COUNT(p.id) > 5
ORDER BY post_count DESC;
```

## 示例提示

### 生成用户管理系统数据库设计：
"请设计一个完整的用户管理系统数据库，包括用户表、角色表、权限表、用户角色关联表。要求支持软删除、审计日志、分层权限控制。使用PostgreSQL，包含完整的DDL语句、索引设计和约束。"

### 生成电商系统数据库设计：
"请设计电商系统的核心数据库表结构，包括商品、订单、用户、库存、支付等模块。要求考虑高并发场景、数据一致性、性能优化。包含分区策略和索引设计。"

### 生成查询优化方案：
"请分析并优化以下查询性能：用户订单统计查询，包含订单数量、总金额、按时间分组等。要求提供执行计划分析、索引建议、查询重写方案。"

### 生成数据迁移脚本：
"请生成数据库迁移脚本，将现有用户表增加新的字段（手机号、地址信息），同时保证数据完整性和业务连续性。包含回滚方案。"

## 性能监控指标

### 关键指标
- 查询响应时间
- 吞吐量（QPS/TPS）
- 连接池使用率
- 缓存命中率
- 磁盘I/O使用率
- 锁等待时间

### 监控查询
```sql
-- 慢查询分析
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 索引使用情况
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- 表大小分析
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 备份和恢复策略

### 备份策略
- 全量备份：每日凌晨执行
- 增量备份：每小时执行
- 事务日志备份：实时备份
- 异地备份：每日同步到远程存储

### 恢复测试
- 定期恢复测试验证
- RTO和RPO指标监控
- 灾难恢复演练
- 数据一致性验证

## 输出格式要求
- 完整的DDL脚本
- 详细的设计说明文档
- 性能测试结果
- 监控和报警配置
- 维护操作手册
- 容量规划建议
