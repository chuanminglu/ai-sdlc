"""
示例脚本 - 展示如何使用需求冲突检测模块
"""

from requirements_conflict_detector import RequirementConflictDetector
from enhanced_requirements import ECOMMERCE_REQUIREMENTS

def main():
    print("需求冲突检测演示\n" + "=" * 50)
    
    # 初始化冲突检测器
    print("\n1. 初始化需求冲突检测器...")
    detector = RequirementConflictDetector(model="zh_core_web_sm")
    
    # 加载需求数据
    print("\n2. 加载需求数据...")
    detector.load_requirements(ECOMMERCE_REQUIREMENTS)
    print(f"   已加载 {len(detector.requirements)} 个需求")
    
    # 运行分析
    print("\n3. 进行单维度分析示例...")
    
    print("\n3.1 实体识别分析...")
    entity_results = detector.analyze_entity_recognition()
    print(f"   识别出 {len(entity_results)} 个实体")
    
    print("\n3.2 名词短语分析(使用自定义方法)...")
    chunk_results = detector.analyze_noun_chunks()
    print(f"   识别出 {len(chunk_results)} 个名词短语")
    
    # 打印前5个名词短语示例
    if chunk_results:
        print("   名词短语示例:")
        for i, (text, req_ids) in enumerate(list(chunk_results.items())[:5]):
            print(f"     - {text}: 在需求 {', '.join(req_ids)} 中出现")
    
    print("\n3.3 术语一致性检查...")
    consistency_results = detector.analyze_terminology_consistency()
    print(f"   发现 {len(consistency_results['issues'])} 个术语一致性问题")
    
    print("\n3.4 规则匹配分析...")
    rule_results = detector.analyze_rule_matching()
    print(f"   发现 {len(rule_results['matches'])} 个规则匹配")
    
    # 冲突检测
    print("\n4. 执行完整冲突检测分析...")
    conflicts = detector.detect_conflicts()
    print(f"   检测到 {len(conflicts)} 个潜在冲突")
    
    # 生成报告
    print("\n5. 生成冲突报告...")
    report = detector.generate_report(conflicts)
    
    # 输出报告
    print("\n" + "=" * 50)
    print("冲突检测报告")
    print("=" * 50 + "\n")
    print(report)
    
    # 示例：如何扩展分析维度
    print("\n6. 扩展分析维度示例...")
    
    def custom_analyzer(requirements, nlp):
        """示例自定义分析器 - 分析模态动词使用"""
        modal_verbs = ["可以", "应该", "必须", "能够", "需要", "可能"]
        results = {}
        
        for req in requirements:
            doc = req["doc"]
            modals = []
            
            for token in doc:
                if token.text in modal_verbs:
                    modals.append({
                        "text": token.text,
                        "sentence": token.sent.text
                    })
            
            if modals:
                results[req["id"]] = modals
        
        return results
    
    modal_results = detector.extend_analysis(custom_analyzer, "modal_verb_analysis")
    print(f"   自定义模态动词分析发现 {len(modal_results)} 个需求包含模态动词")

if __name__ == "__main__":
    main()
