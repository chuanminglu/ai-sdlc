# 测试自动化开发提示词

## 项目概述
构建完整的测试自动化框架，包括单元测试、集成测试、端到端测试、性能测试等。

## 技术要求

### 技术栈
- **单元测试**: Jest, Vitest, PyTest
- **前端测试**: React Testing Library, Cypress
- **API测试**: Postman, Newman, Rest Assured
- **E2E测试**: Playwright, Selenium
- **性能测试**: K6, JMeter
- **移动测试**: Appium, Detox

### 核心功能
1. **单元测试**: 函数和组件级别测试
2. **集成测试**: 模块间交互测试
3. **API测试**: 接口功能和性能测试
4. **UI测试**: 用户界面自动化测试
5. **性能测试**: 负载和压力测试
6. **数据测试**: 数据质量和一致性测试

### 测试结构
```
tests/
├── unit/                 # 单元测试
│   ├── components/
│   ├── utils/
│   └── services/
├── integration/          # 集成测试
│   ├── api/
│   └── database/
├── e2e/                 # 端到端测试
│   ├── specs/
│   ├── pages/
│   └── fixtures/
├── performance/         # 性能测试
│   ├── load/
│   └── stress/
├── utils/              # 测试工具
│   ├── helpers/
│   ├── fixtures/
│   └── mocks/
└── config/             # 测试配置
    ├── jest.config.js
    ├── playwright.config.ts
    └── cypress.config.js
```

## 代码生成指导

### 请帮我生成以下测试代码：

#### 1. 单元测试套件
要求：
- React组件测试
- Hook测试
- 工具函数测试
- 服务层测试
- Mock和Stub使用

#### 2. 集成测试套件
要求：
- API集成测试
- 数据库集成测试
- 第三方服务集成
- 组件间交互测试
- 错误场景测试

#### 3. E2E测试套件
要求：
- 用户流程测试
- 页面对象模式
- 数据驱动测试
- 跨浏览器测试
- 移动端适配测试

#### 4. API测试套件
要求：
- RESTful API测试
- GraphQL测试
- 认证和授权测试
- 数据验证测试
- 性能边界测试

#### 5. 性能测试套件
要求：
- 负载测试脚本
- 压力测试场景
- 容量测试计划
- 性能监控集成
- 报告生成

#### 6. 测试数据管理
要求：
- 测试数据工厂
- 数据清理策略
- 测试环境隔离
- 敏感数据处理
- 数据版本控制

#### 7. 测试报告和分析
要求：
- 测试结果统计
- 覆盖率报告
- 趋势分析
- 失败分析
- 质量门禁

#### 8. CI/CD集成
要求：
- 流水线集成
- 并行测试执行
- 测试结果通知
- 自动化部署验证
- 回归测试策略

## 测试模式和最佳实践

### React组件测试
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserForm } from './UserForm';

describe('UserForm', () => {
  const mockOnSubmit = jest.fn();
  
  beforeEach(() => {
    mockOnSubmit.mockClear();
  });
  
  it('should render form fields', () => {
    render(<UserForm onSubmit={mockOnSubmit} />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });
  
  it('should show validation errors for empty fields', async () => {
    render(<UserForm onSubmit={mockOnSubmit} />);
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
  
  it('should submit form with valid data', async () => {
    render(<UserForm onSubmit={mockOnSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@example.com' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com'
      });
    });
  });
});
```

### API测试模式
```typescript
import request from 'supertest';
import app from '../src/app';
import { createTestUser, cleanupTestData } from './helpers/testData';

describe('User API', () => {
  let testUser: any;
  
  beforeEach(async () => {
    testUser = await createTestUser();
  });
  
  afterEach(async () => {
    await cleanupTestData();
  });
  
  describe('GET /api/users/:id', () => {
    it('should return user data for valid id', async () => {
      const response = await request(app)
        .get(`/api/users/${testUser.id}`)
        .set('Authorization', `Bearer ${testUser.token}`)
        .expect(200);
        
      expect(response.body).toMatchObject({
        id: testUser.id,
        name: testUser.name,
        email: testUser.email
      });
      expect(response.body).not.toHaveProperty('password');
    });
    
    it('should return 404 for non-existent user', async () => {
      await request(app)
        .get('/api/users/999999')
        .set('Authorization', `Bearer ${testUser.token}`)
        .expect(404);
    });
    
    it('should return 401 for unauthorized request', async () => {
      await request(app)
        .get(`/api/users/${testUser.id}`)
        .expect(401);
    });
  });
});
```

### E2E测试模式 (Playwright)
```typescript
import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test('should complete user registration successfully', async ({ page }) => {
    // 导航到注册页面
    await page.goto('/register');
    
    // 填写表单
    await page.fill('[data-testid="name-input"]', 'John Doe');
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'SecurePassword123!');
    await page.fill('[data-testid="confirm-password-input"]', 'SecurePassword123!');
    
    // 提交表单
    await page.click('[data-testid="submit-button"]');
    
    // 验证成功消息
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Registration successful');
    
    // 验证重定向到登录页面
    await expect(page).toHaveURL('/login');
  });
  
  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/register');
    
    // 提交空表单
    await page.click('[data-testid="submit-button"]');
    
    // 验证错误消息
    await expect(page.locator('[data-testid="name-error"]')).toContainText('Name is required');
    await expect(page.locator('[data-testid="email-error"]')).toContainText('Email is required');
    await expect(page.locator('[data-testid="password-error"]')).toContainText('Password is required');
  });
});
```

### 性能测试模式 (K6)
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // 2分钟内增加到100用户
    { duration: '5m', target: 100 }, // 保持100用户5分钟
    { duration: '2m', target: 200 }, // 2分钟内增加到200用户
    { duration: '5m', target: 200 }, // 保持200用户5分钟
    { duration: '2m', target: 0 },   // 2分钟内减少到0用户
  ],
  thresholds: {
    http_req_duration: ['p(99)<1500'], // 99%的请求在1.5秒内完成
    errors: ['rate<0.1'],              // 错误率低于10%
  },
};

export default function () {
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  // 登录请求
  const loginResponse = http.post(
    'https://api.example.com/auth/login',
    JSON.stringify({
      email: 'test@example.com',
      password: 'password123'
    }),
    params
  );
  
  check(loginResponse, {
    'login status is 200': (r) => r.status === 200,
    'login response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);
  
  if (loginResponse.status === 200) {
    const token = loginResponse.json('token');
    
    // 获取用户数据
    const userResponse = http.get(
      'https://api.example.com/api/users/me',
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    check(userResponse, {
      'user data status is 200': (r) => r.status === 200,
      'user data response time < 300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);
  }
  
  sleep(1);
}
```

## 示例提示

### 生成单元测试示例：
"请生成React组件的完整单元测试套件，包括组件渲染测试、事件处理测试、状态变化测试、错误边界测试。使用React Testing Library和Jest，要求高覆盖率和边界场景测试。"

### 生成API测试示例：
"请生成RESTful API的完整测试套件，包括CRUD操作、认证授权、数据验证、错误处理、边界条件测试。使用Jest和Supertest，要求包含测试数据管理和清理策略。"

### 生成E2E测试示例：
"请生成电商应用的端到端测试，包括用户注册登录、商品浏览购买、订单管理等完整流程。使用Playwright，要求页面对象模式、数据驱动测试、跨浏览器支持。"

### 生成性能测试示例：
"请生成API性能测试脚本，模拟高并发用户访问场景。使用K6工具，要求包含负载测试、压力测试、容量测试，以及详细的性能指标监控和报告。"

## 测试策略和规范

### 测试金字塔原则
- 70% 单元测试
- 20% 集成测试
- 10% E2E测试

### 测试命名规范
- 描述性测试名称
- Given-When-Then模式
- 边界条件明确标识
- 错误场景清晰描述

### 测试数据管理
- 独立的测试数据
- 自动化数据清理
- 敏感数据脱敏
- 数据版本控制

## 输出格式要求
- 完整的测试代码
- 详细的测试计划文档
- 测试配置文件
- CI/CD集成脚本
- 测试报告模板
- 故障排查指南
