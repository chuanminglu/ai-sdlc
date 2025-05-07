from typing import Dict, List
import configparser
import os
from llm_interface import LLMInterface

class PRDChecker:
    """PRD文档检查器"""
    
    def __init__(self):
        """初始化PRD检查器"""
        # 初始化LLM接口
        self.llm = LLMInterface()
        
        # 加载评审标准
        self.standards = self._load_review_standards()
        
    def _load_review_standards(self) -> List[Dict]:
        """加载需求评审标准"""
        try:
            standards = []
            with open('docs/需求评审标准.md', 'r', encoding='utf-8') as f:
                content = f.read()
                # 直接使用默认标准，避免复杂的解析逻辑
                return self._create_default_standards()
        except Exception as e:
            print(f"加载评审标准时出错: {str(e)}，将使用默认标准")
            return self._create_default_standards()
    
    def _create_default_standards(self) -> List[Dict]:
        """创建默认评审标准"""
        return [
            {'id': 1, 'title': '变更记录', 'description': '记录每次需求变更的原因和影响', 'weight': 1.0},
            {'id': 2, 'title': '业务背景', 'description': '介绍业务背景、目标和需求', 'weight': 1.0},
            {'id': 3, 'title': '需求价值描述', 'description': '清晰地描述需求的价值和影响', 'weight': 1.0},
            {'id': 4, 'title': '期望目标（可量化）', 'description': '描述期望的目标，例如产品功能、性能、用户满意度等', 'weight': 1.0},
            {'id': 5, 'title': '期望发布时间', 'description': '描述期望的发布时间', 'weight': 1.0},
            {'id': 6, 'title': '名词解释', 'description': '解释名词的含义', 'weight': 1.0},
            {'id': 7, 'title': '业务流程图', 'description': '清晰地描述业务流程', 'weight': 1.0},
            {'id': 8, 'title': '功能列表优先级', 'description': '列出所有功能列表的优先级', 'weight': 1.0},
            {'id': 9, 'title': '用户角色覆盖', 'description': '描述不同用户角色在需求覆盖方面的情况', 'weight': 1.0},
            {'id': 10, 'title': '特殊/异常场景处理', 'description': '描述特殊场景、异常情况和容错处理', 'weight': 1.0},
            {'id': 11, 'title': '运营策略', 'description': '描述运营策略', 'weight': 1.0},
            {'id': 12, 'title': '埋点', 'description': '描述如何使用埋点来收集用户反馈和数据', 'weight': 1.0},
            {'id': 13, 'title': '数据报表', 'description': '描述如何使用数据报表展示用户行为和业务数据', 'weight': 1.0},
            {'id': 14, 'title': '多语言', 'description': '描述该需求是否支持多语言', 'weight': 1.0},
            {'id': 15, 'title': '资损/风险', 'description': '描述可能带来的资损和风险', 'weight': 1.0},
            {'id': 16, 'title': '性能', 'description': '描述产品或服务的性能要求', 'weight': 1.0},
            {'id': 17, 'title': '需求上下游信息', 'description': '描述该需求上下游的信息', 'weight': 1.0},
            {'id': 18, 'title': '安全/合规/隐私', 'description': '描述可能涉及到的安全、合规和隐私要求', 'weight': 1.0},
            {'id': 19, 'title': '交互/视觉文档', 'description': '描述交互和视觉文档', 'weight': 1.0}
        ]
    
    def check_prd(self, prd_content: str) -> Dict:
        """
        检查PRD文档内容
        
        Args:
            prd_content: PRD文档内容
            
        Returns:
            包含检查结果的字典
        """
        # 调用LLM进行分析
        result = self.llm.analyze_prd(prd_content, self.standards)
        
        # 计算总分
        score = self._calculate_score(result)
        result['score'] = score
        
        return result
    
    def _calculate_score(self, result: Dict) -> float:
        """计算总体评分"""
        if not result.get('details'):
            return 0.0
            
        total_weight = sum(std['weight'] for std in self.standards)
        total_score = 0.0
        
        for std in self.standards:
            score = result['details'].get(str(std['id']), {}).get('score', 0)
            total_score += score * std['weight']
            
        return round(total_score / total_weight, 2)