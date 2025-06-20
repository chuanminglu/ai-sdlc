# DevOps部署和CI/CD提示词

## 项目概述
设计和实现完整的DevOps流水线，包括持续集成、持续部署、基础设施即代码、监控告警等。

## 技术要求

### 技术栈
- Docker容器化
- Kubernetes集群管理
- GitHub Actions / GitLab CI
- Terraform基础设施即代码
- Prometheus + Grafana监控
- ELK日志收集分析
- Nginx负载均衡

### 核心功能
1. **容器化**: Docker镜像构建和优化
2. **持续集成**: 自动化测试和构建
3. **持续部署**: 自动化部署和回滚
4. **基础设施**: 云资源自动化管理
5. **监控告警**: 全方位监控和告警
6. **日志管理**: 集中化日志收集和分析

### 项目结构
```
devops/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── monitoring/
│   ├── prometheus.yml
│   └── grafana-dashboard.json
└── scripts/
    ├── deploy.sh
    └── backup.sh
```

## 代码生成指导

### 请帮我生成以下配置：

#### 1. Docker容器化配置
要求：
- 多阶段构建Dockerfile
- Docker Compose编排
- 镜像体积优化
- 安全基础镜像选择
- 健康检查配置

#### 2. Kubernetes部署配置
要求：
- Deployment和Service配置
- ConfigMap和Secret管理
- Ingress路由配置
- HPA自动扩缩容
- 资源限制和请求

#### 3. CI/CD流水线配置
要求：
- GitHub Actions工作流
- 自动化测试集成
- 镜像构建和推送
- 多环境部署策略
- 回滚机制

#### 4. 基础设施即代码
要求：
- Terraform配置文件
- 云资源定义
- 状态管理
- 模块化设计
- 环境隔离

#### 5. 监控和告警配置
要求：
- Prometheus配置
- Grafana仪表板
- 告警规则设置
- 服务发现配置
- 指标收集

#### 6. 日志管理配置
要求：
- ELK堆栈配置
- 日志收集规则
- 日志格式标准化
- 日志分析仪表板
- 日志轮转策略

#### 7. 安全配置
要求：
- 镜像安全扫描
- 密钥管理
- 网络安全策略
- RBAC权限控制
- 安全监控

#### 8. 备份和恢复
要求：
- 数据备份策略
- 自动化备份脚本
- 灾难恢复计划
- 备份验证机制
- 恢复测试流程

## 配置模板和最佳实践

### Dockerfile最佳实践
```dockerfile
# 多阶段构建
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

USER nextjs
EXPOSE 3000
CMD ["npm", "start"]
```

### Kubernetes部署配置
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### GitHub Actions工作流
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    - run: npm ci
    - run: npm test
    - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Build and push Docker image
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker build -t myapp:${{ github.sha }} .
        docker push myapp:${{ github.sha }}
```

## 示例提示

### 生成Docker配置示例：
"请生成一个Node.js应用的完整Docker配置，包括多阶段构建的Dockerfile、docker-compose.yml编排文件、nginx反向代理配置。要求镜像体积小、安全性高、支持开发和生产环境。"

### 生成Kubernetes部署示例：
"请生成完整的Kubernetes部署配置，包括Deployment、Service、Ingress、ConfigMap等。应用是一个React前端+Node.js后端+PostgreSQL数据库。要求支持自动扩缩容、健康检查、配置管理。"

### 生成CI/CD流水线示例：
"请生成GitHub Actions工作流，实现自动化测试、构建Docker镜像、部署到Kubernetes集群。要求支持多环境部署（开发、测试、生产），包含安全扫描和回滚机制。"

### 生成监控配置示例：
"请生成Prometheus和Grafana监控配置，监控Kubernetes集群和应用性能。包含CPU、内存、网络、应用指标的收集，以及告警规则配置。"

### 生成基础设施代码示例：
"请使用Terraform生成AWS基础设施配置，包括EKS集群、RDS数据库、Redis缓存、负载均衡器、VPC网络。要求模块化设计、多环境支持。"

## 监控指标定义

### 应用监控指标
- 响应时间和吞吐量
- 错误率和成功率
- 资源使用率
- 业务核心指标
- 用户体验指标

### 基础设施监控
- CPU和内存使用率
- 磁盘I/O和网络流量
- 服务可用性
- 容器状态
- 集群健康状态

### 告警规则配置
```yaml
groups:
- name: application
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} for {{ $labels.instance }}"
```

## 安全最佳实践
- 镜像漏洞扫描
- 最小权限原则
- 密钥轮换策略
- 网络隔离
- 安全审计日志

## 输出格式要求
- 完整的配置文件
- 详细的部署文档
- 运维操作手册
- 故障排查指南
- 性能调优建议
- 安全配置检查清单
