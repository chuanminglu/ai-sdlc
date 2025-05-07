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
        standards = []
        with open('docs/需求评审标准.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # 解析markdown文件中的评审标准
            lines = content.split('\n')
            current_standard = None
            for line in lines:
                if line.startswith('##'):  # 章节标题
                    continue
                elif line.startswith(str(len(standards) + 1) + '.'):  # 新标准项
                    if current_standard:
                        standards.append(current_standard)
                    title = line.split('​**')[1].split('**​')[0]
                    description = line.split('  ')[1].strip()
                    current_standard = {
                        'id': len(standards) + 1,
                        'title': title,
                        'description': description,
                        'weight': 1.0  # 默认权重
                    }
            if current_standard:  # 添加最后一个标准
                standards.append(current_standard)
        return standards
    
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