# AI-SDLC 用户故事开发助手

<div align="center">
    <img src="docs/images/ai-sdlc-logo.png" alt="AI-SDLC Logo" width="200"/>
    <br>
    <p><strong>人工智能辅助软件开发生命周期工具</strong></p>
</div>

## 📖 项目概述

AI-SDLC 是一款集成了人工智能能力的软件开发生命周期工具，专注于用户故事解析、API 规范自动生成以及约束条件管理。该工具通过深度学习技术自动分析用户需求，快速转化为规范的 API 文档，大幅提高软件开发效率。

## ⭐️ 主要功能

1. **💡 智能用户故事生成与解析**
   - 基于业务领域和角色自动生成用户故事
   - 精确提取角色、目标和验收标准
   - 支持中文语音输入，提高效率

2. **📊 API规范自动生成**
   - 符合OpenAPI 3.0标准
   - 支持Swagger和Redoc文档界面
   - 自动生成接口定义和示例

3. **🔍 约束条件智能提取**
   - 自动识别性能、安全等约束
   - 生成结构化约束清单
   - 支持导出和共享

## 🚀 快速开始

### 软件安装

```bash
# 克隆仓库
git clone https://github.com/windlu/ai-sdlc.git
cd ai-sdlc

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config.ini.template config.ini
# 编辑config.ini，填入您的API密钥
```

### 使用流程

#### 1. 启动程序
```bash
python mainui.py
```

<div align="center">
    <img src="docs/images/main-ui.png" alt="主界面" width="800"/>
    <p><em>AI-SDLC 主界面</em></p>
</div>

#### 2. 用户故事生成与解析

<div align="center">
    <img src="docs/images/story-parsing.png" alt="故事解析" width="800"/>
    <p><em>用户故事解析界面</em></p>
</div>

- **输入方式**：
  - 文本输入：直接在界面输入
  - 语音输入：支持中文语音识别
  - 默认模板：常见场景快速填充

- **操作步骤**：
  1. 填写业务领域、用户角色和功能特性
  2. 点击"生成用户故事"（约15秒）
  3. 点击"解析用户故事"查看结果

#### 3. API规范生成

<div align="center">
    <img src="docs/images/api-spec.png" alt="API规范" width="800"/>
    <p><em>API规范生成界面</em></p>
</div>

- **主要功能**：
  - 自动生成RESTful API定义
  - 支持请求/响应示例
  - 生成Swagger文档

- **操作步骤**：
  1. 确保已完成故事解析
  2. 点击"创建API规范"
  3. 等待生成完成（约15秒）
  4. 查看生成的API文档

#### 4. 约束条件管理

<div align="center">
    <img src="docs/images/constraints.png" alt="约束条件" width="800"/>
    <p><em>约束条件管理界面</em></p>
</div>

- **约束类型**：
  - 性能约束：响应时间、并发数
  - 安全约束：访问控制、数据保护
  - 可靠性约束：服务可用性、数据一致性
  - 其他业务约束

- **操作步骤**：
  1. 点击"生成约束检查清单"
  2. 等待AI分析（约15秒）
  3. 查看生成的约束清单
  4. 可选择保存为Markdown文件

## 🎯 使用场景

1. **需求分析阶段**
   - 快速生成标准用户故事
   - 自动提取关键信息
   - 确保需求完整性

2. **API设计阶段**
   - 自动生成API文档
   - 统一接口规范
   - 提高开发效率

3. **质量管理阶段**
   - 识别关键约束
   - 生成检查清单
   - 确保实现质量

## 📋 开发计划

- [x] 中文语音输入支持
- [x] API文档自动生成
- [x] 约束条件提取
- [ ] 批量故事处理
- [ ] 测试用例生成
- [ ] 多语言支持

## 📞 联系方式

- 作者：windlu
- 邮箱：windlu@Itlead.com.cn
- Issues：[GitHub Issues](https://github.com/windlu/ai-sdlc/issues)

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

<div align="center">
    <p>由 windlu ❤️ 和 AI 共同打造</p>
</div>