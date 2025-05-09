"""
需求冲突检测模块集成指南

本文档介绍如何将需求冲突检测模块与现有的需求分析工具集成。
"""

## 集成概述

需求冲突检测模块(`requirements_conflict_detector.py`)旨在识别和分析需求文档中的潜在冲突。
它可以与现有的需求分析工具(如`parseuserstory.py`)集成，为需求管理过程增加冲突检测功能。

## 集成方式

可以通过以下几种方式将冲突检测模块集成到现有系统中：

### 1. 作为独立工具使用

最简单的方式是将冲突检测器作为独立的分析工具，在需求生成后进行冲突分析。
参见`example_usage.py`中的示例。

### 2. 与parseuserstory.py集成

可以修改`parseuserstory.py`，在生成用户故事后自动进行冲突检测：

```python
# 在parseuserstory.py中添加以下导入
from conflict_detector.requirements_conflict_detector import RequirementConflictDetector

# 添加冲突检测函数
def check_conflicts_in_user_stories(user_stories):
    """
    检测用户故事中的潜在冲突
    
    参数:
        user_stories (list): 用户故事列表
    
    返回:
        dict: 冲突检测结果
    """
    # 将用户故事转换为需求格式
    requirements_data = {
        "功能需求": [
            {
                "id": f"US{i+1}",
                "title": story.get("goal", "未指定目标"),
                "description": f"作为{story.get('role', '用户')}，我希望{story.get('goal', '未指定目标')}，以便{story.get('value', '未指定价值')}。",
                "priority": "中",
                "owner": "需求团队",
                "status": "已确认"
            }
            for i, story in enumerate(user_stories)
        ]
    }
    
    # 初始化冲突检测器
    detector = RequirementConflictDetector()
    
    # 加载需求
    detector.load_requirements(requirements_data)
    
    # 检测冲突
    conflicts = detector.detect_conflicts()
    
    # 生成报告
    report = detector.generate_report(conflicts)
    
    return {
        "conflicts": conflicts,
        "report": report
    }
```

然后在生成用户故事后调用此函数：

```python
# 原有代码
user_stories = [parse_user_story(story) for story in generated_stories]

# 添加冲突检测
conflict_results = check_conflicts_in_user_stories(user_stories)
print("冲突检测报告:")
print(conflict_results["report"])
```

### 3. 创建REST API接口

可以创建一个Flask或FastAPI应用，提供REST API接口，使其他系统可以调用冲突检测功能：

```python
# api_server.py示例
from flask import Flask, request, jsonify
from conflict_detector.requirements_conflict_detector import RequirementConflictDetector

app = Flask(__name__)

@app.route("/api/detect-conflicts", methods=["POST"])
def detect_conflicts():
    data = request.json
    
    if not data or "requirements" not in data:
        return jsonify({"error": "No requirements data provided"}), 400
    
    detector = RequirementConflictDetector()
    detector.load_requirements(data["requirements"])
    conflicts = detector.detect_conflicts()
    report = detector.generate_report(conflicts)
    
    return jsonify({
        "conflicts": conflicts,
        "report": report
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## 扩展冲突检测功能

冲突检测模块设计为可扩展的，可以通过以下方式添加新的分析维度：

1. 使用内置的`extend_analysis`方法添加自定义分析器
2. 继承`RequirementConflictDetector`类并添加新方法
3. 修改现有的分析方法以增强功能

例如，添加一个依赖性分析器：

```python
def dependency_analyzer(requirements, nlp):
    """分析需求之间的依赖关系"""
    # 分析逻辑...
    return results

# 使用内置扩展方法
detector = RequirementConflictDetector()
detector.load_requirements(requirements_data)
dependency_results = detector.extend_analysis(dependency_analyzer, "dependency_analysis")
```

## 最佳实践建议

1. 在需求早期阶段进行冲突检测，以便尽早发现问题
2. 结合需求评审会议使用冲突检测报告
3. 定期对所有需求运行冲突检测，而不仅是新增需求
4. 根据实际项目特点调整和扩展分析维度
5. 将冲突检测作为CI/CD流程的一部分，自动化检测
