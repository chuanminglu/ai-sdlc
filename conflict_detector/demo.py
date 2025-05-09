"""
需求冲突检测演示脚本
"""
import os
import sys
import json
import logging
from pathlib import Path

# 确保能够导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入极客书店需求样例
from conflict_detector.geek_bookstore_requirements import GEEK_BOOKSTORE_REQUIREMENTS
from conflict_detector.conflict_detector import RequirementConflictDetector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ConflictDetectorDemo")

def main():
    """演示需求冲突检测功能"""
    
    # 创建冲突检测器实例，会自动从config.ini读取API密钥
    # 如果配置文件中没有，会尝试从环境变量DEEPSEEK_API_KEY读取
    detector = RequirementConflictDetector()
    
    print("=== 需求冲突检测演示 ===")
    print(f"加载了 {sum(len(reqs) for reqs in GEEK_BOOKSTORE_REQUIREMENTS.values())} 条需求")
    
    # 选择要分析的维度
    available_dimensions = list(detector.CONFLICT_DIMENSIONS.keys())
    print("\n可选分析维度:")
    for i, dim in enumerate(available_dimensions, 1):
        print(f"{i}. {dim}")
    
    try:
        # 在实际应用中，可以让用户选择分析维度
        # 这里默认选择"功能一致性"进行演示
        selected_dimension = "功能一致性"  # available_dimensions[0]
        print(f"\n选择分析维度: {selected_dimension}")
        
        print("\n开始检测需求冲突...")
        conflicts = detector.detect_conflicts(
            requirements=GEEK_BOOKSTORE_REQUIREMENTS,
            dimension=selected_dimension
        )
        
        # 生成冲突报告（Markdown格式）
        report = detector.generate_conflict_report(conflicts, format="markdown")
        
        # 保存报告到文件
        report_file = Path(__file__).parent / "conflict_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n检测完成! 发现 {conflicts['metadata']['total_conflicts']} 个潜在冲突")
        print(f"冲突报告已保存至: {report_file}")
        
        # 展示一些冲突示例
        print("\n冲突示例:")
        for i, conflict in enumerate(conflicts.get("conflicts", [])[:3], 1):
            print(f"\n{i}. {conflict.get('conflict_type', '未命名冲突')}")
            print(f"   严重度: {conflict.get('severity', '未知')}")
            print(f"   涉及需求: {', '.join(conflict.get('requirements', []))}")
            print(f"   描述: {conflict.get('description', '无描述')[:100]}...")
        
        # 如果有更多冲突
        if len(conflicts.get("conflicts", [])) > 3:
            print(f"\n...以及其他 {len(conflicts['conflicts']) - 3} 个冲突。详见报告文件。")
    
    except Exception as e:
        logger.error(f"演示过程中出错: {e}", exc_info=True)
        print(f"\n出错了: {e}")
    
if __name__ == "__main__":
    main()