"""
需求冲突检测模块 - 基于SpaCy的NLP技术

该模块用于分析需求文档，识别潜在的需求冲突。
支持多种分析维度：
- 实体识别分析
- 名词短语(Noun Chunks)分析
- 语义角色标注
- 术语一致性检查
- 规则匹配分析
"""

import spacy
from spacy.matcher import Matcher, PhraseMatcher, DependencyMatcher
from spacy.tokens import Doc, Span
import networkx as nx
from collections import defaultdict, Counter
import re


class RequirementConflictDetector:
    """需求冲突检测器类，使用SpaCy实现NLP分析功能"""
    
    def __init__(self, model="zh_core_web_sm"):
        """
        初始化冲突检测器
        
        参数:
            model (str): 要加载的SpaCy模型名称
        """
        # 加载SpaCy模型
        self.nlp = spacy.load(model)
        # 初始化匹配器
        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab)
        self.dependency_matcher = DependencyMatcher(self.nlp.vocab)
        # 用于术语一致性检查的字典
        self.terminology_dict = {}
        # 保存需求文档
        self.requirements = []
        # 保存分析结果
        self.analysis_results = {}
        # 图形表示，用于冲突分析
        self.requirement_graph = nx.Graph()
    
    def load_requirements(self, requirements_data):
        """
        加载需求数据
        
        参数:
            requirements_data (dict): 包含功能需求和非功能需求的字典
        """
        self.requirements = []
        # 处理功能需求
        for req in requirements_data.get("功能需求", []):
            req_text = f"{req['id']}: {req['title']} - {req['description']}"
            req_doc = self.nlp(req_text)
            self.requirements.append({
                "id": req["id"],
                "title": req["title"],
                "description": req["description"],
                "priority": req["priority"],
                "owner": req["owner"],
                "status": req["status"],
                "type": "功能需求",
                "doc": req_doc
            })
            # 构建需求图
            self.requirement_graph.add_node(req["id"], 
                                           title=req["title"],
                                           type="功能需求",
                                           priority=req["priority"])
            
        # 处理非功能需求
        for req in requirements_data.get("非功能需求", []):
            req_text = f"{req['id']}: {req['title']} - {req['description']}"
            req_doc = self.nlp(req_text)
            self.requirements.append({
                "id": req["id"],
                "title": req["title"],
                "description": req["description"],
                "priority": req["priority"],
                "owner": req["owner"],
                "status": req["status"],
                "type": "非功能需求",
                "doc": req_doc
            })
            # 构建需求图
            self.requirement_graph.add_node(req["id"], 
                                           title=req["title"],
                                           type="非功能需求",
                                           priority=req["priority"])
    
    def build_terminology_dict(self):
        """从需求中构建术语字典，用于术语一致性检查"""
        terminology = defaultdict(list)
        
        # 提取所有名词短语作为潜在术语
        for req in self.requirements:
            doc = req["doc"]
            # 使用自定义方法提取名词短语
            noun_phrases = self._extract_custom_noun_phrases(doc)
            
            for phrase_text, phrase_data in noun_phrases.items():
                # 忽略过短的名词短语和常见词
                if len(phrase_text) > 1:
                    # 规范化术语（转为小写）
                    normalized_term = phrase_text.lower()
                    terminology[normalized_term].append({
                        "req_id": req["id"],
                        "original_text": phrase_text
                    })
        
        # 过滤出现在多个需求中的术语
        self.terminology_dict = {term: refs for term, refs in terminology.items() 
                                if len(refs) > 1}
    
    def analyze_entity_recognition(self):
        """进行实体识别分析，识别需求中的关键实体"""
        entity_results = defaultdict(list)
        
        for req in self.requirements:
            doc = req["doc"]
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
                
                # 建立实体与需求之间的关联
                entity_key = f"{ent.text}:{ent.label_}"
                entity_results[entity_key].append(req["id"])
        
        self.analysis_results["entity_recognition"] = dict(entity_results)
        return entity_results
    
    def analyze_noun_chunks(self):
        """分析名词短语，识别需求中的关键概念
        
        注意：由于SpaCy的中文模型不支持noun_chunks，这里使用自定义方法模拟名词短语提取
        """
        chunk_results = defaultdict(list)
        
        for req in self.requirements:
            doc = req["doc"]
            chunks = []
            
            # 自定义方法提取名词短语（中文）
            # 方法1：使用依存句法分析，提取名词及其修饰词
            noun_phrases = self._extract_custom_noun_phrases(doc)
            
            for phrase_text, phrase_data in noun_phrases.items():
                if len(phrase_text) > 1:  # 忽略单个字的名词短语
                    chunks.append({
                        "text": phrase_text,
                        "root": phrase_data["root"],
                        "start": phrase_data["start"],
                        "end": phrase_data["end"]
                    })
                    
                    # 建立名词短语与需求之间的关联
                    chunk_results[phrase_text].append(req["id"])
        
        self.analysis_results["noun_chunks"] = dict(chunk_results)
        return chunk_results
        
    def _extract_custom_noun_phrases(self, doc):
        """自定义方法，从中文文本中提取名词短语
        
        参数:
            doc: SpaCy处理后的文档
            
        返回:
            dict: 提取的名词短语与其信息
        """
        noun_phrases = {}
        
        # 方法1：基于依存关系提取名词及其修饰词
        for token in doc:
            # 如果找到名词
            if token.pos_ in ["NOUN", "PROPN"]:
                # 收集名词及其所有依存词
                phrase_tokens = [token]
                for child in token.children:
                    if child.dep_ in ["amod", "compound", "nummod", "det"]:
                        phrase_tokens.append(child)
                
                # 如果有多于一个词，构建名词短语
                if len(phrase_tokens) > 1:
                    # 按照原文本顺序排序词语
                    phrase_tokens.sort(key=lambda x: x.i)
                    
                    # 构建短语文本
                    phrase_text = "".join([t.text for t in phrase_tokens])
                    start = min(t.idx for t in phrase_tokens)
                    end = max(t.idx + len(t.text) for t in phrase_tokens)
                    
                    # 保存短语信息
                    noun_phrases[phrase_text] = {
                        "root": token.text,
                        "start": start,
                        "end": end
                    }
            
        # 方法2：使用词性标注模式提取名词短语
        # 例如：形容词+名词，数词+量词+名词等
        adj_noun_pattern = []
        i = 0
        while i < len(doc) - 1:
            # 形容词+名词模式
            if doc[i].pos_ == "ADJ" and doc[i+1].pos_ in ["NOUN", "PROPN"]:
                phrase_text = doc[i].text + doc[i+1].text
                noun_phrases[phrase_text] = {
                    "root": doc[i+1].text,
                    "start": doc[i].idx,
                    "end": doc[i+1].idx + len(doc[i+1].text)
                }
            # 数词+量词+名词模式
            elif (i < len(doc) - 2 and doc[i].pos_ == "NUM" and 
                  doc[i+1].pos_ == "NOUN" and doc[i+2].pos_ in ["NOUN", "PROPN"]):
                phrase_text = doc[i].text + doc[i+1].text + doc[i+2].text
                noun_phrases[phrase_text] = {
                    "root": doc[i+2].text,
                    "start": doc[i].idx,
                    "end": doc[i+2].idx + len(doc[i+2].text)
                }
            i += 1
                
        return noun_phrases
    
    def analyze_semantic_roles(self):
        """语义角色标注分析，识别需求中的行为主体、行为和接受者"""
        semantic_results = defaultdict(list)
        
        for req in self.requirements:
            doc = req["doc"]
            
            # 识别主谓宾结构
            for token in doc:
                if token.dep_ == "ROOT" and token.pos_ == "VERB":
                    # 找到主语
                    subjects = [child for child in token.children 
                               if child.dep_ in ["nsubj", "nsubjpass"]]
                    
                    # 找到宾语
                    objects = [child for child in token.children 
                              if child.dep_ in ["dobj", "pobj", "attr"]]
                    
                    for subj in subjects:
                        for obj in objects:
                            semantic_key = f"{subj.text}:{token.text}:{obj.text}"
                            semantic_results[semantic_key].append(req["id"])
        
        self.analysis_results["semantic_roles"] = dict(semantic_results)
        return semantic_results
    
    def analyze_terminology_consistency(self):
        """检查术语一致性，识别术语不一致的情况"""
        # 先构建术语字典
        self.build_terminology_dict()
        
        consistency_issues = []
        similar_terms = defaultdict(list)
        
        # 寻找相似但不完全相同的术语
        terms = list(self.terminology_dict.keys())
        for i, term1 in enumerate(terms):
            for term2 in terms[i+1:]:
                # 如果两个术语有重叠但不完全相同
                if (term1 in term2 or term2 in term1) and term1 != term2:
                    similar_terms[term1].append(term2)
                    similar_terms[term2].append(term1)
                    
                    # 记录不一致的术语和涉及的需求
                    consistency_issues.append({
                        "term1": term1,
                        "term2": term2,
                        "req_ids1": [ref["req_id"] for ref in self.terminology_dict[term1]],
                        "req_ids2": [ref["req_id"] for ref in self.terminology_dict[term2]]
                    })
                    
                    # 在需求图中添加边，表示潜在冲突
                    for req_id1 in [ref["req_id"] for ref in self.terminology_dict[term1]]:
                        for req_id2 in [ref["req_id"] for ref in self.terminology_dict[term2]]:
                            if req_id1 != req_id2:
                                self.requirement_graph.add_edge(
                                    req_id1, req_id2, 
                                    type="术语不一致",
                                    term1=term1,
                                    term2=term2
                                )
        
        self.analysis_results["terminology_consistency"] = {
            "issues": consistency_issues,
            "similar_terms": dict(similar_terms)
        }
        return self.analysis_results["terminology_consistency"]
    
    def analyze_rule_matching(self):
        """使用规则匹配分析需求中的特定模式"""
        # 定义一些规则模式
        conflict_patterns = [
            # 时间冲突规则
            [{"LOWER": {"IN": ["每天", "天", "小时", "分钟", "秒"]}},
             {"IS_DIGIT": True},
             {"LOWER": {"IN": ["次", "小时", "分钟", "秒"]}}],
            
            # 数字冲突规则
            [{"IS_DIGIT": True},
             {"IS_PUNCT": True, "OP": "?"},
             {"IS_DIGIT": True, "OP": "?"},
             {"LOWER": {"IN": ["%", "百分比", "比例"]}}],
            
            # 否定规则
            [{"LOWER": {"IN": ["不能", "禁止", "不得", "不应", "不可以"]}}],
            
            # 必须规则
            [{"LOWER": {"IN": ["必须", "应该", "需要", "要求"]}}]
        ]
        
        # 添加规则到匹配器
        for i, pattern in enumerate(conflict_patterns):
            self.matcher.add(f"CONFLICT_PATTERN_{i}", [pattern])
        
        rule_matches = []
        
        for req in self.requirements:
            doc = req["doc"]
            matches = self.matcher(doc)
            
            for match_id, start, end in matches:
                rule_name = self.nlp.vocab.strings[match_id]
                span = doc[start:end]
                
                rule_matches.append({
                    "req_id": req["id"],
                    "rule": rule_name,
                    "text": span.text,
                    "start": span.start_char,
                    "end": span.end_char
                })
        
        # 分析匹配规则在不同需求间的潜在冲突
        conflict_groups = defaultdict(list)
        for match in rule_matches:
            conflict_groups[match["rule"]].append(match)
        
        # 在需求图中添加规则匹配导致的潜在冲突
        for rule, matches in conflict_groups.items():
            if len(matches) > 1:
                for i, match1 in enumerate(matches):
                    for match2 in matches[i+1:]:
                        if match1["req_id"] != match2["req_id"]:
                            self.requirement_graph.add_edge(
                                match1["req_id"], match2["req_id"],
                                type="规则匹配冲突",
                                rule=rule,
                                text1=match1["text"],
                                text2=match2["text"]
                            )
        
        self.analysis_results["rule_matching"] = {
            "matches": rule_matches,
            "conflict_groups": dict(conflict_groups)
        }
        return self.analysis_results["rule_matching"]
    
    def detect_conflicts(self):
        """检测需求之间的潜在冲突"""
        # 运行所有分析
        self.analyze_entity_recognition()
        self.analyze_noun_chunks()  # 使用自定义的名词短语提取方法
        self.analyze_semantic_roles()
        self.analyze_terminology_consistency()
        self.analyze_rule_matching()
        
        # 分析图中的边，识别潜在冲突
        conflicts = []
        
        for u, v, data in self.requirement_graph.edges(data=True):
            conflicts.append({
                "req_id1": u,
                "req_id2": v,
                "conflict_type": data["type"],
                "details": data
            })
        
        # 添加自定义冲突检测逻辑
        self._detect_time_conflicts(conflicts)
        self._detect_security_privacy_conflicts(conflicts)
        self._detect_functionality_conflicts(conflicts)
        
        return conflicts
    
    def _detect_time_conflicts(self, conflicts):
        """检测涉及时间约束的冲突"""
        time_patterns = [
            r'(\d+)\s*(分钟|小时|天|周|月)',
            r'(\d+)\s*秒',
            r'每(天|周|月|年)',
            r'(\d+)\s*个工作日'
        ]
        
        time_requirements = {}
        
        for req in self.requirements:
            for pattern in time_patterns:
                matches = re.finditer(pattern, req["description"])
                for match in matches:
                    if req["id"] not in time_requirements:
                        time_requirements[req["id"]] = []
                    
                    time_requirements[req["id"]].append({
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end()
                    })
        
        # 比较不同需求中的时间约束是否存在冲突
        time_req_ids = list(time_requirements.keys())
        for i, req_id1 in enumerate(time_req_ids):
            for req_id2 in time_req_ids[i+1:]:
                # 如果两个需求都有时间约束，可能存在冲突
                if req_id1 != req_id2:
                    if not self.requirement_graph.has_edge(req_id1, req_id2):
                        self.requirement_graph.add_edge(
                            req_id1, req_id2,
                            type="时间约束潜在冲突",
                            time1=time_requirements[req_id1],
                            time2=time_requirements[req_id2]
                        )
                    
                    conflicts.append({
                        "req_id1": req_id1,
                        "req_id2": req_id2,
                        "conflict_type": "时间约束潜在冲突",
                        "details": {
                            "time1": time_requirements[req_id1],
                            "time2": time_requirements[req_id2]
                        }
                    })
    
    def _detect_security_privacy_conflicts(self, conflicts):
        """检测涉及安全和隐私的潜在冲突"""
        security_terms = ["安全", "加密", "保护", "隐私", "认证", "授权"]
        security_reqs = []
        
        for req in self.requirements:
            for term in security_terms:
                if term in req["description"]:
                    security_reqs.append(req["id"])
                    break
        
        # 检查功能需求是否与安全需求存在潜在冲突
        for req in self.requirements:
            if req["id"] not in security_reqs and req["type"] == "功能需求":
                for sec_req_id in security_reqs:
                    # 检查是否已经存在边
                    if not self.requirement_graph.has_edge(req["id"], sec_req_id):
                        self.requirement_graph.add_edge(
                            req["id"], sec_req_id,
                            type="安全隐私潜在冲突",
                            reason="功能需求可能与安全需求冲突"
                        )
                    
                    conflicts.append({
                        "req_id1": req["id"],
                        "req_id2": sec_req_id,
                        "conflict_type": "安全隐私潜在冲突",
                        "details": {
                            "reason": "功能需求可能与安全需求冲突"
                        }
                    })
    
    def _detect_functionality_conflicts(self, conflicts):
        """检测功能之间的潜在冲突"""
        # 通过共享资源或术语来检测功能冲突
        shared_resources = defaultdict(list)
        
        for req in self.requirements:
            if req["type"] == "功能需求":
                doc = req["doc"]
                
                # 提取关键资源术语
                for token in doc:
                    if token.pos_ in ["NOUN", "PROPN"]:
                        shared_resources[token.text].append(req["id"])
        
        # 如果多个功能需求共享同一资源，可能存在冲突
        for resource, req_ids in shared_resources.items():
            if len(req_ids) > 1:
                for i, req_id1 in enumerate(req_ids):
                    for req_id2 in req_ids[i+1:]:
                        if req_id1 != req_id2:
                            # 检查是否已经存在边
                            if not self.requirement_graph.has_edge(req_id1, req_id2):
                                self.requirement_graph.add_edge(
                                    req_id1, req_id2,
                                    type="功能重叠潜在冲突",
                                    resource=resource
                                )
                            
                            conflicts.append({
                                "req_id1": req_id1,
                                "req_id2": req_id2,
                                "conflict_type": "功能重叠潜在冲突",
                                "details": {
                                    "resource": resource
                                }
                            })
    
    def generate_report(self, conflicts, output_format="text"):
        """生成冲突分析报告"""
        if output_format == "text":
            report = "需求冲突分析报告\n"
            report += "=" * 50 + "\n\n"
            
            report += f"总计发现 {len(conflicts)} 个潜在冲突\n\n"
            
            # 按冲突类型分组
            conflict_types = defaultdict(list)
            for conflict in conflicts:
                conflict_types[conflict["conflict_type"]].append(conflict)
            
            for conflict_type, type_conflicts in conflict_types.items():
                report += f"\n## {conflict_type} (共 {len(type_conflicts)} 个)\n"
                
                for i, conflict in enumerate(type_conflicts):
                    req1 = next(r for r in self.requirements if r["id"] == conflict["req_id1"])
                    req2 = next(r for r in self.requirements if r["id"] == conflict["req_id2"])
                    
                    report += f"\n{i+1}. 冲突: {req1['id']} 与 {req2['id']}\n"
                    report += f"   - {req1['id']}: {req1['title']}\n"
                    report += f"   - {req2['id']}: {req2['title']}\n"
                    
                    # 添加冲突详情
                    if "details" in conflict:
                        report += "   详情:\n"
                        for key, value in conflict["details"].items():
                            report += f"   - {key}: {value}\n"
                    
                    report += "\n"
            
            return report
        else:
            # 可以扩展支持其他格式，如HTML或JSON
            return {"conflicts": conflicts}
    
    def extend_analysis(self, custom_analyzer_func, analyzer_name):
        """扩展分析维度的接口"""
        results = custom_analyzer_func(self.requirements, self.nlp)
        self.analysis_results[analyzer_name] = results
        return results
