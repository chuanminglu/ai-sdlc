# React前端应用开发提示词

## 项目概述
开发一个现代化的React前端应用，提供用户友好的界面和良好的用户体验。

## 技术要求

### 技术栈
- React 18+ (函数组件 + Hooks)
- TypeScript
- Vite构建工具
- React Router v6
- React Query (TanStack Query)
- Tailwind CSS / Styled Components
- React Hook Form + Yup
- Zustand状态管理

### 核心功能
1. **用户界面**: 响应式设计和现代UI组件
2. **路由管理**: 单页应用导航和权限控制
3. **状态管理**: 全局状态和本地状态管理
4. **数据获取**: API调用和缓存机制
5. **表单处理**: 表单验证和提交
6. **用户认证**: 登录状态管理和权限控制

### 项目结构
```
react-frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # 基础UI组件
│   │   ├── forms/        # 表单组件
│   │   └── layout/       # 布局组件
│   ├── pages/            # 页面组件
│   ├── hooks/            # 自定义Hooks
│   ├── services/         # API服务
│   ├── stores/           # 状态管理
│   ├── utils/            # 工具函数
│   ├── types/            # TypeScript类型
│   └── styles/           # 样式文件
├── public/
├── tests/
└── package.json
```

## 代码生成指导

### 请帮我生成以下代码：

#### 1. 项目基础配置
要求：
- Vite配置文件
- TypeScript配置
- ESLint和Prettier配置
- 路径别名设置
- 环境变量管理

#### 2. 基础UI组件库
要求：
- Button、Input、Modal等基础组件
- 使用TypeScript严格类型
- 支持主题定制
- 无障碍访问支持
- 组件文档和故事书

#### 3. 路由系统配置
要求：
- React Router v6配置
- 路由守卫和权限控制
- 懒加载和代码分割
- 404页面处理
- 面包屑导航

#### 4. 状态管理系统
要求：
- Zustand全局状态
- 用户认证状态
- 主题和偏好设置
- 数据缓存管理
- 持久化存储

#### 5. API服务层
要求：
- Axios HTTP客户端配置
- 请求/响应拦截器
- 错误处理机制
- 重试和超时配置
- TypeScript类型定义

#### 6. 数据获取和缓存
要求：
- React Query配置
- 自定义查询Hooks
- 缓存策略
- 乐观更新
- 离线支持

#### 7. 表单处理系统
要求：
- React Hook Form集成
- Yup验证规则
- 自定义表单组件
- 动态表单生成
- 文件上传处理

#### 8. 认证和授权
要求：
- JWT token管理
- 登录/登出功能
- 权限检查组件
- 路由保护
- 自动刷新token

## 开发规范

### 代码质量要求
- TypeScript严格模式
- 函数组件和Hooks
- 组件职责单一
- 可复用和可测试
- 性能优化

### UI/UX要求
- 响应式设计
- 移动端适配
- 无障碍访问
- 加载状态
- 错误处理界面

### 性能要求
- 组件懒加载
- 代码分割
- 图片优化
- 缓存策略
- 性能监控

## 示例提示

### 生成基础组件示例：
"请生成一套React基础UI组件，包括Button、Input、Modal、Card等。使用TypeScript，支持主题定制，包含完整的props类型定义和使用示例。使用Tailwind CSS进行样式设计。"

### 生成数据获取Hook示例：
"请生成使用React Query的自定义Hook，用于获取用户列表数据。要求包含加载状态、错误处理、缓存配置和类型安全。支持分页和搜索功能。"

### 生成表单组件示例：
"请生成一个用户注册表单组件，使用React Hook Form和Yup验证。包含姓名、邮箱、密码字段，实时验证，错误提示，提交处理和加载状态。"

### 生成路由配置示例：
"请生成React Router v6的路由配置，包括公开路由、受保护路由、懒加载组件、路由守卫和404页面。支持嵌套路由和权限控制。"

### 生成状态管理示例：
"请使用Zustand创建全局状态管理，包括用户认证状态、主题设置、通知系统。要求TypeScript类型安全，持久化存储，和相关的Hook。"

## 组件设计原则

### 组件结构
```typescript
interface ComponentProps {
  // props定义
}

export const Component: React.FC<ComponentProps> = ({
  // 解构props
}) => {
  // hooks
  // 事件处理
  // 渲染逻辑
  
  return (
    // JSX
  );
};
```

### 自定义Hook模式
```typescript
interface UseFeatureResult {
  // 返回值类型
}

export const useFeature = (params: FeatureParams): UseFeatureResult => {
  // hook逻辑
  return {
    // 返回值
  };
};
```

### 服务层模式
```typescript
class ApiService {
  private baseURL: string;
  
  constructor() {
    this.baseURL = process.env.VITE_API_URL || '';
  }
  
  async getData<T>(endpoint: string): Promise<T> {
    // API调用逻辑
  }
}
```

## 测试要求
- 组件单元测试 (React Testing Library)
- Hook测试
- 集成测试
- E2E测试 (Playwright)
- 视觉回归测试

## 输出格式要求
- 完整的TypeScript组件代码
- 详细的props和类型定义
- 使用示例和文档
- 单元测试用例
- CSS样式代码
- 性能优化建议
