# Chrome扩展开发提示词

## 项目概述
创建一个Chrome浏览器扩展，用于读取网页表单控件并提供双向数据同步功能。

## 开发要求

### 技术栈
- Manifest V3
- TypeScript
- HTML5/CSS3
- Chrome Extension APIs

### 核心功能
1. **表单控件扫描**: 检测当前页面的所有表单元素
2. **数据提取**: 获取控件的类型、值、标签等信息
3. **Popup界面**: 在扩展弹窗中显示表单控件
4. **双向同步**: 支持popup与原页面的数据同步
5. **数据存储**: 保存和恢复表单数据

### 项目结构
```
chrome-extension/
├── manifest.json
├── src/
│   ├── content/
│   │   ├── content.ts
│   │   └── formScanner.ts
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.ts
│   │   └── popup.css
│   ├── background/
│   │   └── background.ts
│   └── types/
│       └── index.ts
└── assets/
    └── icons/
```

## 代码生成指导

### 请帮我生成以下代码：

#### 1. manifest.json配置文件
要求：
- 使用Manifest V3格式
- 配置必要的权限（activeTab, scripting, storage）
- 设置popup和content script
- 包含适当的CSP设置

#### 2. TypeScript类型定义
要求：
- 定义FormControl接口
- 定义消息传递的类型
- 定义存储数据的类型
- 使用严格的类型检查

#### 3. Content Script (content.ts)
要求：
- 扫描页面中的表单控件
- 提取控件信息（类型、值、标签、ID等）
- 监听DOM变化（MutationObserver）
- 实现消息接收和处理
- 支持动态更新控件值

#### 4. Popup界面 (popup.html/ts/css)
要求：
- 响应式设计，适配400x600px
- 显示表单控件列表
- 支持搜索和过滤
- 实现双向数据绑定
- 包含加载状态和错误处理

#### 5. 消息传递机制
要求：
- 定义清晰的消息类型
- 实现content script到popup的通信
- 实现popup到content script的命令发送
- 添加错误处理和超时机制

#### 6. 数据存储功能
要求：
- 使用Chrome Storage API
- 实现表单数据的保存和恢复
- 支持多个保存状态
- 数据版本管理

## 开发规范

### 代码质量要求
- 使用TypeScript严格模式
- 遵循Chrome Extension最佳实践
- 实现完整的错误处理
- 添加详细的注释和文档
- 性能优化（避免内存泄漏）

### 安全考虑
- 输入验证和消毒
- CSP策略配置
- 权限最小化原则
- 避免XSS攻击

### 测试要求
- 单元测试覆盖核心逻辑
- 集成测试验证消息传递
- 在不同网站上测试兼容性
- 性能测试和内存监控

## 示例提示

### 生成Content Script示例：
"请生成一个Chrome扩展的content script，能够扫描当前页面的所有表单控件（input、select、textarea等），提取控件信息并通过消息传递发送到popup界面。要求使用TypeScript，包含完整的类型定义和错误处理。"

### 生成Popup界面示例：
"请生成Chrome扩展的popup界面，包括HTML、CSS和TypeScript代码。界面需要显示从content script接收到的表单控件列表，支持编辑控件值并同步回原页面。要求响应式设计和良好的用户体验。"

### 生成消息传递机制示例：
"请实现Chrome扩展中content script和popup之间的消息传递机制，包括消息类型定义、发送和接收处理，以及错误处理和超时机制。使用TypeScript编写。"

## 输出格式要求
- 每个文件单独生成，包含完整代码
- 添加详细注释说明关键逻辑
- 包含使用示例和测试用例
- 提供部署和调试指导
