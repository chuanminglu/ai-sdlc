"""
需求冲突检测CLI工具
"""
import os
import sys
import json
import argparse
import logging
from pathlib import Path

# 确保能够导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入冲突检测器和样例需求
from conflict_detector.conflict_detector import RequirementConflictDetector
from conflict_detector.geek_bookstore_requirements import GEEK_BOOKSTORE_REQUIREMENTS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ConflictDetectorCLI")

def load_requirements_from_file(filepath: str) -> dict:
    """
    从JSON文件中加载需求
    
    Args:
        filepath: 需求JSON文件路径
    
    Returns:
        需求字典
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载需求文件失败: {e}")
        raise

def main():
    """CLI入口函数"""
    parser = argparse.ArgumentParser(description="基于Deepseek V3的需求冲突检测工具")
    
    # 定义命令行参数
    parser.add_argument(
        "--requirements", "-r",
        help="需求JSON文件路径。如果未提供，将使用内置的极客书店需求样例"
    )
    parser.add_argument(
        "--dimension", "-d",
        choices=[
            "功能一致性", "用户权限逻辑", "业务流程完整性", 
            "用户体验一致性", "数据一致性", "安全合规性", "全部"
        ],
        default="全部",
        help="分析维度，默认分析全部维度"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径，默认为当前目录下的conflict_report.{format}"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="markdown",
        help="输出格式，默认为markdown"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Deepseek API密钥，如未提供将尝试从配置文件或环境变量读取"
    )
    parser.add_argument(
        "--config", "-c",
        help="配置文件路径，默认使用项目根目录下的config.ini"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 加载需求
        if args.requirements:
            print(f"从文件加载需求: {args.requirements}")
            requirements = load_requirements_from_file(args.requirements)
        else:
            print("使用内置的极客书店需求样例")
            requirements = GEEK_BOOKSTORE_REQUIREMENTS
        
        # 创建冲突检测器实例
        # API密钥的优先级：命令行参数 > 配置文件 > 环境变量
        detector = RequirementConflictDetector(
            api_key=args.api_key,
            config_file=args.config
        )
        
        # 检测冲突
        dimension = None if args.dimension == "全部" else args.dimension
        print(f"开始检测需求冲突，分析维度: {args.dimension}")
        
        conflicts = detector.detect_conflicts(
            requirements=requirements,
            dimension=dimension
        )
        
        # 生成报告
        report = detector.generate_conflict_report(conflicts, format=args.format)
        
        # 确定输出路径
        if args.output:
            output_path = args.output
        else:
            output_path = f"conflict_report.{args.format}"
        
        # 保存报告
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n检测完成! 发现 {conflicts['metadata']['total_conflicts']} 个潜在冲突")
        print(f"按严重级别统计:")
        for level in detector.SEVERITY_LEVELS:
            count = conflicts["metadata"]["conflicts_by_severity"].get(level, 0)
            print(f"- {level}级: {count}个")
        
        print(f"\n报告已保存至: {output_path}")
    
    except Exception as e:
        logger.error(f"执行过程中出错: {e}", exc_info=True)
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()