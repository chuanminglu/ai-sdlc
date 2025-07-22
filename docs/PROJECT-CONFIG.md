# AI-SDLC 项目配置

本项目使用以下配置文件来规范开发和部署流程：

## 📋 配置文件位置

- **项目运行时配置**: `.github/.aidevrc`
- **代码生成指导**: `.github-copilot-instructions.md`
- **详细说明文档**: `项目配置文件对比说明.md`

## 🚀 快速开始

### 初始化项目环境
```bash
# 读取 .github/.aidevrc 配置并初始化环境
python scripts/setup.py --config .github/.aidevrc
```

### 验证环境配置
```bash
# 验证虚拟环境和依赖
python scripts/verify.py --config .github/.aidevrc
```

## 📁 为什么放在 .github 目录？

1. **项目规范性**: 与 GitHub Actions、Copilot 指令等统一管理
2. **语义清晰**: 明确表示这是项目自动化和协作配置
3. **专业化**: 符合现代开源项目最佳实践
4. **集中管理**: 所有项目配置文件统一位置

## 🔗 相关文件

- `.github/workflows/`: GitHub Actions 工作流
- `.github/copilot-instructions-*.md`: 各技术栈的 Copilot 指令
- `requirements.txt`: Python 依赖列表
- `config.ini`: 应用程序配置

## 📖 更多信息

详细的配置文件说明请参考 `项目配置文件对比说明.md`。
