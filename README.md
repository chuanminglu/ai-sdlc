# AI-SDLC 用户故事开发助手

<div align="center">
    <img src="docs/images/ai-sdlc-logo.png" alt="AI-SDLC Logo" width="200"/>
    <br>
    <p><strong>人工智能辅助软件开发生命周期工具</strong></p>
</div>

## 📖 项目概述

AI-SDLC 是一款集成了人工智能能力的软件开发生命周期工具，专注于用户故事解析、API 规范自动生成以及约束条件管理。该工具通过深度学习技术自动分析用户需求，快速转化为规范的 API 文档，大幅提高软件开发效率。
这是一个完全用AI写的项目，探索如何用AI打通软件开发生命周期中的各个环节，从需求分析到API设计，再到约束条件管理。

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

4. **📋 PRD文档质量评审**
   - 基于19条专业评审标准进行评估
   - 自动识别文档缺失项
   - 提供具体改进建议

## 🔧 系统架构

项目采用模块化设计，主要包含以下核心组件：

1. **主界面模块 (mainui.py)**
   - 提供统一的用户界面入口
   - 整合各功能模块

2. **用户故事处理模块**
   - 用户故事解析 (parseuserstory.py)
   - 用户故事分割 (splituserstory.py)

3. **API规范生成模块**
   - API标准创建 (createAPIstd.py)
   - 排序功能实现 (createsort.py)

4. **约束条件管理模块**
   - 约束条件生成 (createconstraints.py)

5. **PRD文档评审模块**
   - 评审界面 (prd_check_ui.py)
   - 评审逻辑 (prd_checker.py)
   - 示例PRD生成 (sample_prd.py)

6. **LLM接口模块**
   - 统一大模型接口 (llm_interface.py)

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

#### 5. PRD文档评审

- **评审标准**：
  - 基于19条专业评审标准
  - 涵盖变更记录、业务背景、需求价值等方面
  - 评分范围：0-100

- **操作步骤**：
  1. 加载PRD文档
  2. 点击"评审文档"
  3. 查看详细评审结果和改进建议

## 💡 提示词模板库

AI-SDLC 内置了多个精心设计的提示词模板，用于不同的功能模块。以下是主要的提示词模板：

### 1. PRD文档评审提示词

```
作为一名专业的需求评审专家，请基于以下评审标准对PRD文档进行分析：

{评审标准列表}

需要评审的PRD文档内容如下：

{PRD文档内容}

请提供一个结构化的JSON评审报告，包含以下内容：
1. missing_items: 文档中缺失的关键要素列表
2. improvement_suggestions: 具体的改进建议列表
3. details: 每个评审标准的详细评分（0-100）和评分理由

注意：
- 评分应该客观公正，有充分理由
- 改进建议应具体且可执行
- 返回的必须是合法的JSON格式
```

### 2. 约束清单生成提示词

```
请你作为软件工程质量专家，为以下用户故事生成系统约束检查清单。
用户故事包含以下信息：
- 领域：{domain}
- 角色：{role}
- 目标：{goal}
- 价值：{value}
- 验收标准：
{criteria_str}

请生成一个全面的约束检查清单，包含以下类型的约束（但不限于这些类型）：
1. 性能约束
2. 安全性约束
3. 可靠性约束
4. 可扩展性约束
5. 兼容性约束
6. 合规性约束
7. 可用性约束
8. 可维护性约束

对于每一项约束，请提供以下信息：
- 约束类型
- 度量指标
- 要求值
- 约束描述

请以JSON格式输出结果。
```

### 3. API规范生成提示词

```
作为一名RESTful API设计专家，请根据以下用户故事为{domain}系统设计API规范：

角色：{role}
目标：{goal}
验收标准：
{criteria}

请设计符合OpenAPI 3.0规范的API定义，包括：
1. 路径和HTTP方法
2. 请求参数和响应模式
3. 示例请求和响应
4. 错误处理
5. 认证方法

返回完整的OpenAPI JSON规范。
```

### 4. 用户故事解析提示词

```
请分析以下用户故事文本，提取关键信息：

{story_text}

请以JSON格式返回以下信息：
1. domain：业务领域
2. role：用户角色
3. goal：用户目标
4. value：业务价值
5. criteria：验收标准（数组形式）

确保提取的信息准确完整，特别是验收标准应该包含所有可衡量的条件。
```

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

4. **文档评审阶段**
   - 自动化需求文档评审
   - 识别文档缺失项
   - 提供专业改进建议

## 📋 开发计划

- [x] 中文语音输入支持
- [x] API文档自动生成
- [x] 约束条件提取
- [x] PRD文档评审
- [ ] 批量故事处理
- [ ] 测试用例生成
- [ ] 多语言支持
- [ ] 离线模型支持

## 📞 联系方式

- 作者：windlu
- 邮箱：windlu@Itlead.com.cn
- Issues：[GitHub Issues](https://github.com/windlu/ai-sdlc/issues)

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

<div align="center">
    <p>由 windlu ❤️ 和 AI 共同打造</p>
    <p>最后更新: 2025年5月7日</p>
</div>
