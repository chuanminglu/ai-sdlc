# 基于SpaCy的需求冲突检测模块

这个模块使用自然语言处理(NLP)技术来分析需求文档，识别潜在冲突点。通过对需求文本的多维度分析，帮助项目团队在早期发现和解决需求间的矛盾和不一致，提高需求质量和软件开发效率。

![版本](https://img.shields.io/badge/版本-1.0.0-blue)
![SpaCy](https://img.shields.io/badge/SpaCy-3.0+-green)
![Python](https://img.shields.io/badge/Python-3.7+-yellow)
![更新日期](https://img.shields.io/badge/更新日期-2025.05.09-orange)

## 功能特点

- **多维度分析**：结合多种NLP技术全面分析需求文档
  - 实体识别分析：识别需求中的关键实体
  - 名词短语(Noun Chunks)分析：识别关键概念和业务对象
  - 语义角色标注：分析需求中的动作主体、动作和接受者
  - 术语一致性检查：发现术语不一致问题
  - 规则匹配分析：基于特定规则识别潜在冲突点

- **可扩展架构**：支持自定义分析器和冲突检测规则
- **图形表示**：使用图理论表示需求间的关系和冲突
- **详细报告生成**：自动生成结构化冲突报告

## 安装

### 前提条件

- Python 3.7+
- SpaCy 3.0+
- NetworkX 2.5+

### 安装步骤

1. 安装必要的依赖：

```bash
pip install spacy networkx
```

2. 安装SpaCy中文语言模型：

```bash
python -m spacy download zh_core_web_sm
```

3. 将模块文件复制到你的项目中

## 使用方法

### 基本用法

```python
from requirements_conflict_detector import RequirementConflictDetector
from enhanced_requirements import ECOMMERCE_REQUIREMENTS

# 初始化检测器
detector = RequirementConflictDetector()

# 加载需求数据
detector.load_requirements(ECOMMERCE_REQUIREMENTS)

# 执行冲突检测
conflicts = detector.detect_conflicts()

# 生成报告
report = detector.generate_report(conflicts)
print(report)
```

### 自定义分析器

```python
# 定义自定义分析器
def custom_analyzer(requirements, nlp):
    """示例自定义分析器 - 分析条件语句"""
    results = {}
    condition_keywords = ["如果", "当", "一旦", "除非"]
    
    for req in requirements:
        doc = req["doc"]
        conditions = []
        
        for sent in doc.sents:
            for keyword in condition_keywords:
                if keyword in sent.text:
                    conditions.append(sent.text)
                    break
        
        if conditions:
            results[req["id"]] = conditions
    
    return results

# 使用自定义分析器
condition_results = detector.extend_analysis(custom_analyzer, "condition_analysis")
```

## 输入数据格式

该模块期望的需求数据格式为：

```python
requirements_data = {
    "功能需求": [
        {
            "id": "FR001",
            "title": "需求标题",
            "description": "详细需求描述",
            "priority": "高/中/低",
            "owner": "负责团队",
            "status": "状态"
        },
        # 更多功能需求...
    ],
    "非功能需求": [
        {
            "id": "NFR001",
            "title": "需求标题",
            "description": "详细需求描述",
            "priority": "高/中/低",
            "owner": "负责团队",
            "status": "状态"
        },
        # 更多非功能需求...
    ]
}
```

## 冲突类型

该模块目前可检测的冲突类型包括：

1. **术语不一致**：在不同需求中使用不同术语表达相同概念
2. **规则匹配冲突**：基于预定义规则匹配的冲突
3. **时间约束潜在冲突**：涉及时间约束的矛盾
4. **安全隐私潜在冲突**：功能需求与安全/隐私需求之间的潜在冲突
5. **功能重叠潜在冲突**：多个功能之间的重叠或矛盾

## 集成

详细的集成指南请参见 [integration_guide.md](integration_guide.md)。

## 测试

运行测试脚本以验证模块功能：

```bash
python test_conflict_detector.py
```

## 示例

运行示例脚本以查看模块的工作方式：

```bash
python example_usage.py
```

## 许可

[MIT License](LICENSE)
