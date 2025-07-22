---
applyTo: "**/*"
priority: 1
---
# AI-SDLC 项目主指令文件
# 适用于整个项目的通用开发规范

## 项目概述
本项目是 AI-SDLC (软件开发生命周期智能助手)，主要技术栈包括：
- Python 3.12+ (主要开发语言)
- GUI 开发 (mainui.py, mainmenu_gui.py)
- NLP 处理 (SpaCy 中文模型)
- API 开发和文档生成

## 开发环境要求

### 虚拟环境 (强制要求)
- 项目必须在 `.venv` 虚拟环境中运行
- Windows: `.venv\Scripts\activate`
- Unix/Linux: `source .venv/bin/activate`
- 配合 `.github/.aidevrc` 文件确保环境一致性

### 依赖管理
- 使用 `requirements.txt` 管理依赖
- 核心依赖固定版本，辅助依赖使用 `>=`
- 特别注意 SpaCy 中文模型: `zh_core_web_sm`

## Agent 模式规范
- 优先在当前终端执行命令
- 避免创建新的终端窗口  
- 最大终端数限制为 1
- 保持终端会话持久化

## 项目结构约定
- **主要模块**: `mainui.py` (主界面), `mainmenu_gui.py` (菜单)
- **测试文件**: `test_*.py` 格式
- **配置文件**: `.github/.aidevrc` (运行时), `config.ini` (应用)
- **文档**: Markdown 格式，中文说明

## 代码质量要求
- 遵循 PEP 8 规范
- 使用类型提示
- 完整的文档字符串
- 结构化错误处理
- 中文注释，简洁明了

## 技术栈特定规范
详细的技术栈指导请参考对应的专项指令文件：
- Python: `copilot-instructions-python.md`
- API: `copilot-instructions-api.md`  
- React: `copilot-instructions-react.md`
- 通用: `copilot-instructions-general.md`

## 与 .aidevrc 的协作
此指令文件专注于代码生成规范，`.github/.aidevrc` 负责运行时环境控制：
- 指令文件: 代码编写时的规范指导
- .aidevrc: 项目运行时的环境强制要求

---
注意: 此文件具有最高优先级，会覆盖全局 Copilot 设置
