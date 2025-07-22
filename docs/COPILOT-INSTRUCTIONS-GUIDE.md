# GitHub Copilot 指令文件组织说明

## 📁 文件结构

```
.github/
├── copilot-instructions.md           # 主指令文件 (最高优先级)
├── copilot-instructions-aidev.md     # AI-SDLC 项目详细规范
├── copilot-instructions-python.md    # Python 开发规范
├── copilot-instructions-api.md       # API 开发规范
├── copilot-instructions-react.md     # React 开发规范
├── copilot-instructions-general.md   # 通用开发规范
└── copilot-instructions-*.md         # 其他技术栈规范
```

## 🎯 文件作用说明

### 1. **主指令文件** (`copilot-instructions.md`)
- **优先级**: 最高 (priority: 1)
- **作用范围**: 整个项目 (`applyTo: "**/*"`)
- **主要内容**: 项目核心规范、环境要求、Agent模式配置
- **与 .aidevrc 协作**: 代码生成 + 运行时控制

### 2. **项目详细规范** (`copilot-instructions-aidev.md`)
- **内容**: 完整的项目开发指导原则
- **用途**: 作为项目文档和参考资料
- **维护**: 包含所有最佳实践和规范细节

### 3. **技术栈特定指令**
- **Python**: 代码风格、包管理、测试规范
- **API**: RESTful 设计、文档生成、验证规范
- **React**: 组件开发、状态管理、性能优化
- **General**: 跨技术栈的通用规范

## 🔄 GitHub Copilot 识别优先级

1. **项目级主指令** (`.github/copilot-instructions.md`)
2. **技术栈特定指令** (根据文件类型匹配)
3. **用户全局指令** (`~/.github-copilot-instructions.md`)

## ✅ 迁移完成的优势

### 🏗️ 组织优势
- **集中管理**: 所有 Copilot 指令统一在 .github 目录
- **模块化**: 按技术栈分离，便于维护
- **层次清晰**: 主指令 + 专项指令的层次结构

### 🎛️ 功能优势  
- **优先级控制**: 使用 `priority` 元数据精确控制
- **范围限定**: 使用 `applyTo` 精确匹配文件类型
- **无冲突**: 避免根目录与 .github 目录的指令冲突

### 🤝 协作优势
- **与 .aidevrc 完美配合**: 代码生成 + 运行时控制
- **开发者友好**: 在 .github 目录查看完整的项目配置
- **CI/CD 集成**: 与 workflows 等自动化配置统一管理

## 📋 使用建议

1. **日常开发**: GitHub Copilot 自动应用主指令文件
2. **特定技术栈**: 对应的专项指令自动生效
3. **新功能开发**: 参考详细规范文件 (`copilot-instructions-aidev.md`)
4. **团队协作**: 所有配置文件都在 .github 目录，便于查看和维护

这样的组织方式既保持了指令的有效性，又提升了项目的专业性和可维护性！
