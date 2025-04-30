# AI User Story Generator

这是一个基于 AI 的用户故事生成和解析工具，能够自动生成符合敏捷开发规范的用户故事，并自动生成相应的 API 规范。

## 功能特点

- 使用 DeepSeek API 生成用户故事
- 支持中文用户故事的解析
- 自动提取用户角色、目标和验收标准
- 生成标准的 API 规范文档

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `config.ini.template` 到 `config.ini`
2. 在 `config.ini` 中填入您的 DeepSeek API 密钥

## 使用方法

```python
python parseuserstory.py
```

## 项目结构

- `parseuserstory.py`: 主程序文件
- `apispec_generator/`: API 规范生成器模块
- `config.ini`: 配置文件
- `uml/`: UML 图表目录

## 依赖项

- Python 3.6+
- spaCy
- requests
- apispec_generator