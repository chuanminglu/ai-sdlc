#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于SpaCy的NLP需求冲突检测GUI应用
使用PyQt5创建图形用户界面，集成需求冲突检测功能
"""

import sys
import os
import json
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QTextEdit, QFileDialog, QTabWidget,
                            QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox,
                            QGroupBox, QMessageBox, QProgressBar, QCheckBox, QRadioButton)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor

# 导入需求冲突检测模块
from requirements_conflict_detector import RequirementConflictDetector
from enhanced_requirements import ECOMMERCE_REQUIREMENTS

class ConflictDetectionThread(QThread):
    """
    冲突检测线程，用于在后台执行需求冲突检测
    避免在执行长时间任务时冻结GUI
    """
    progress_signal = pyqtSignal(int)  # 进度更新信号
    finished_signal = pyqtSignal(dict)  # 完成信号，返回结果字典
    error_signal = pyqtSignal(str)  # 错误信号
    
    def __init__(self, requirements_data, model_name="zh_core_web_sm"):
        super().__init__()
        self.requirements_data = requirements_data
        self.model_name = model_name
        
    def run(self):
        try:
            # 初始化检测器
            self.progress_signal.emit(10)
            detector = RequirementConflictDetector(model=self.model_name)
            
            # 加载需求
            self.progress_signal.emit(20)
            detector.load_requirements(self.requirements_data)
            
            # 执行各类分析
            self.progress_signal.emit(30)
            entity_results = detector.analyze_entity_recognition()
            self.progress_signal.emit(40)
            chunk_results = detector.analyze_noun_chunks()
            self.progress_signal.emit(50)
            detector.analyze_semantic_roles()
            self.progress_signal.emit(60)
            detector.analyze_terminology_consistency()
            self.progress_signal.emit(70)
            detector.analyze_rule_matching()
            
            # 检测冲突
            self.progress_signal.emit(80)
            conflicts = detector.detect_conflicts()
            
            # 生成报告
            self.progress_signal.emit(90)
            report = detector.generate_report(conflicts)
            
            # 完成并返回结果
            self.progress_signal.emit(100)
            results = {
                "conflicts": conflicts,
                "report": report,
                "entity_results": entity_results,
                "chunk_results": chunk_results,
                "detector": detector
            }
            self.finished_signal.emit(results)
            
        except Exception as e:
            self.error_signal.emit(str(e))


class NLPConflictDetectorGUI(QMainWindow):
    """
    基于SpaCy的NLP需求冲突检测GUI应用主窗口
    """
    def __init__(self):
        super().__init__()
        
        # 窗口标题和大小
        self.setWindowTitle("基于SpaCy的需求冲突检测")
        self.setMinimumSize(1200, 800)
        
        # 保存当前加载的需求数据和分析结果
        self.requirements_data = None
        self.detection_results = None
        self.detector = None
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央窗口部件和主布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部控制区
        control_layout = QHBoxLayout()
        
        # 左侧数据加载控制
        data_group = QGroupBox("数据加载")
        data_layout = QVBoxLayout(data_group)
        
        load_layout = QHBoxLayout()
        self.load_sample_btn = QPushButton("加载示例需求")
        self.load_json_btn = QPushButton("加载JSON文件")
        load_layout.addWidget(self.load_sample_btn)
        load_layout.addWidget(self.load_json_btn)
        data_layout.addLayout(load_layout)
        
        self.data_source_label = QLabel("未加载数据")
        self.data_source_label.setStyleSheet("font-style: italic;")
        data_layout.addWidget(self.data_source_label)
        
        control_layout.addWidget(data_group)
        
        # 中间分析控制
        analysis_group = QGroupBox("分析控制")
        analysis_layout = QVBoxLayout(analysis_group)
        
        model_layout = QHBoxLayout()
        model_label = QLabel("SpaCy模型:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["zh_core_web_sm", "zh_core_web_md", "zh_core_web_lg"])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        analysis_layout.addLayout(model_layout)
        
        analysis_options_layout = QHBoxLayout()
        self.detect_btn = QPushButton("执行冲突检测")
        self.detect_btn.setEnabled(False)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        analysis_options_layout.addWidget(self.detect_btn)
        analysis_options_layout.addWidget(self.cancel_btn)
        analysis_layout.addLayout(analysis_options_layout)
        
        control_layout.addWidget(analysis_group)
        
        # 右侧分析维度选择
        dimensions_group = QGroupBox("分析维度")
        dimensions_layout = QVBoxLayout(dimensions_group)
        
        self.entity_check = QCheckBox("实体识别分析")
        self.entity_check.setChecked(True)
        self.noun_check = QCheckBox("名词短语分析")
        self.noun_check.setChecked(True)
        self.semantic_check = QCheckBox("语义角色标注")
        self.semantic_check.setChecked(True)
        self.term_check = QCheckBox("术语一致性检查")
        self.term_check.setChecked(True)
        self.rule_check = QCheckBox("规则匹配分析") 
        self.rule_check.setChecked(True)
        
        dimensions_layout.addWidget(self.entity_check)
        dimensions_layout.addWidget(self.noun_check)
        dimensions_layout.addWidget(self.semantic_check)
        dimensions_layout.addWidget(self.term_check)
        dimensions_layout.addWidget(self.rule_check)
        
        control_layout.addWidget(dimensions_group)
        
        main_layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 创建分割窗口
        splitter = QSplitter(Qt.Vertical)
        
        # 创建选项卡窗口
        self.tab_widget = QTabWidget()
        
        # 需求列表选项卡
        self.requirements_tab = QWidget()
        requirements_layout = QVBoxLayout(self.requirements_tab)
        self.requirements_tree = QTreeWidget()
        self.requirements_tree.setHeaderLabels(["ID", "标题", "类型", "优先级", "状态"])
        self.requirements_tree.setColumnWidth(0, 80)
        self.requirements_tree.setColumnWidth(1, 300)
        self.requirements_tree.setColumnWidth(2, 100)
        self.requirements_tree.setColumnWidth(3, 80)
        requirements_layout.addWidget(self.requirements_tree)
        self.tab_widget.addTab(self.requirements_tab, "需求列表")
        
        # 需求详情选项卡
        self.req_detail_tab = QWidget()
        req_detail_layout = QVBoxLayout(self.req_detail_tab)
        self.req_detail_text = QTextEdit()
        self.req_detail_text.setReadOnly(True)
        req_detail_layout.addWidget(self.req_detail_text)
        self.tab_widget.addTab(self.req_detail_tab, "需求详情")
        
        # 实体识别选项卡
        self.entity_tab = QWidget()
        entity_layout = QVBoxLayout(self.entity_tab)
        self.entity_tree = QTreeWidget()
        self.entity_tree.setHeaderLabels(["实体", "类型", "关联需求"])
        self.entity_tree.setColumnWidth(0, 200)
        self.entity_tree.setColumnWidth(1, 100)
        entity_layout.addWidget(self.entity_tree)
        self.tab_widget.addTab(self.entity_tab, "实体识别")
        
        # 名词短语选项卡
        self.chunks_tab = QWidget()
        chunks_layout = QVBoxLayout(self.chunks_tab)
        self.chunks_tree = QTreeWidget()
        self.chunks_tree.setHeaderLabels(["名词短语", "根词", "关联需求"])
        self.chunks_tree.setColumnWidth(0, 200)
        self.chunks_tree.setColumnWidth(1, 100)
        chunks_layout.addWidget(self.chunks_tree)
        self.tab_widget.addTab(self.chunks_tab, "名词短语")
        
        # 术语一致性选项卡
        self.term_tab = QWidget()
        term_layout = QVBoxLayout(self.term_tab)
        self.term_tree = QTreeWidget()
        self.term_tree.setHeaderLabels(["术语1", "术语2", "关联需求"])
        self.term_tree.setColumnWidth(0, 150)
        self.term_tree.setColumnWidth(1, 150)
        term_layout.addWidget(self.term_tree)
        self.tab_widget.addTab(self.term_tab, "术语一致性")
        
        splitter.addWidget(self.tab_widget)
        
        # 冲突列表和报告区域
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # 冲突列表
        conflicts_group = QGroupBox("冲突列表")
        conflicts_layout = QVBoxLayout(conflicts_group)
        self.conflicts_tree = QTreeWidget()
        self.conflicts_tree.setHeaderLabels(["类型", "需求1", "需求2", "详情"])
        self.conflicts_tree.setColumnWidth(0, 150)
        self.conflicts_tree.setColumnWidth(1, 150)
        self.conflicts_tree.setColumnWidth(2, 150)
        conflicts_layout.addWidget(self.conflicts_tree)
        
        # 报告区域
        report_group = QGroupBox("冲突报告")
        report_layout = QVBoxLayout(report_group)
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        report_layout.addWidget(self.report_text)
        
        # 导出报告按钮
        export_layout = QHBoxLayout()
        self.export_report_btn = QPushButton("导出报告")
        self.export_report_btn.setEnabled(False)
        export_layout.addStretch()
        export_layout.addWidget(self.export_report_btn)
        report_layout.addLayout(export_layout)
        
        # 添加冲突列表和报告区域到底部布局
        bottom_layout.addWidget(conflicts_group, 1)
        bottom_layout.addWidget(report_group, 1)
        
        splitter.addWidget(bottom_widget)
        
        # 设置分割窗口比例
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # 连接信号与槽
        self.connect_signals()
        
    def connect_signals(self):
        """连接信号与槽函数"""
        # 数据加载按钮
        self.load_sample_btn.clicked.connect(self.load_sample_requirements)
        self.load_json_btn.clicked.connect(self.load_json_requirements)
        
        # 需求树项目点击
        self.requirements_tree.itemClicked.connect(self.show_requirement_detail)
        
        # 冲突检测按钮
        self.detect_btn.clicked.connect(self.start_conflict_detection)
        self.cancel_btn.clicked.connect(self.cancel_detection)
        
        # 冲突树项目点击
        self.conflicts_tree.itemClicked.connect(self.show_conflict_detail)
        
        # 导出报告按钮
        self.export_report_btn.clicked.connect(self.export_report)
    
    def load_sample_requirements(self):
        """加载示例需求数据"""
        self.requirements_data = ECOMMERCE_REQUIREMENTS
        self.data_source_label.setText("使用示例数据 (电商平台需求)")
        self.update_requirements_tree()
        self.detect_btn.setEnabled(True)
        
        # 清空以前的结果
        self.clear_results()
        
        QMessageBox.information(self, "数据加载", "已成功加载示例需求数据")
    
    def load_json_requirements(self):
        """从JSON文件加载需求数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择需求JSON文件", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.requirements_data = json.load(f)
                
                self.data_source_label.setText(f"从文件加载: {os.path.basename(file_path)}")
                self.update_requirements_tree()
                self.detect_btn.setEnabled(True)
                
                # 清空以前的结果
                self.clear_results()
                
                QMessageBox.information(self, "数据加载", "已成功加载需求数据")
            except Exception as e:
                QMessageBox.critical(self, "加载错误", f"无法加载需求数据: {str(e)}")
    
    def update_requirements_tree(self):
        """更新需求树视图"""
        self.requirements_tree.clear()
        
        if not self.requirements_data:
            return
        
        # 功能需求组
        func_req_group = QTreeWidgetItem(self.requirements_tree)
        func_req_group.setText(0, "功能需求")
        func_req_group.setExpanded(True)
        
        # 添加功能需求
        for req in self.requirements_data.get("功能需求", []):
            item = QTreeWidgetItem(func_req_group)
            item.setText(0, req["id"])
            item.setText(1, req["title"])
            item.setText(2, "功能需求")
            item.setText(3, req["priority"])
            item.setText(4, req["status"])
            item.setData(0, Qt.UserRole, req)  # 存储整个需求对象
        
        # 非功能需求组
        non_func_req_group = QTreeWidgetItem(self.requirements_tree)
        non_func_req_group.setText(0, "非功能需求")
        non_func_req_group.setExpanded(True)
        
        # 添加非功能需求
        for req in self.requirements_data.get("非功能需求", []):
            item = QTreeWidgetItem(non_func_req_group)
            item.setText(0, req["id"])
            item.setText(1, req["title"])
            item.setText(2, "非功能需求")
            item.setText(3, req["priority"])
            item.setText(4, req["status"])
            item.setData(0, Qt.UserRole, req)  # 存储整个需求对象
    
    def show_requirement_detail(self, item):
        """显示选中需求的详细信息"""
        # 获取存储的需求对象
        req = item.data(0, Qt.UserRole)
        if not req:
            return
        
        # 构建详情文本
        detail = f"<h2>{req['id']}: {req['title']}</h2>\n"
        detail += f"<p><b>优先级:</b> {req['priority']}</p>\n"
        detail += f"<p><b>负责人:</b> {req['owner']}</p>\n"
        detail += f"<p><b>状态:</b> {req['status']}</p>\n"
        detail += f"<p><b>类型:</b> {'功能需求' if 'FR' in req['id'] else '非功能需求'}</p>\n"
        detail += f"<h3>描述:</h3>\n<p>{req['description']}</p>\n"
        
        # 显示详情
        self.req_detail_text.setHtml(detail)
        
        # 切换到详情标签
        self.tab_widget.setCurrentWidget(self.req_detail_tab)
    
    def clear_results(self):
        """清空分析结果"""
        self.entity_tree.clear()
        self.chunks_tree.clear()
        self.term_tree.clear()
        self.conflicts_tree.clear()
        self.report_text.clear()
        self.detection_results = None
        self.export_report_btn.setEnabled(False)
    
    def start_conflict_detection(self):
        """开始冲突检测过程"""
        if not self.requirements_data:
            QMessageBox.warning(self, "无数据", "请先加载需求数据")
            return
        
        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 设置按钮状态
        self.detect_btn.setEnabled(False)
        self.load_sample_btn.setEnabled(False)
        self.load_json_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # 清空之前的结果
        self.clear_results()
        
        # 创建并启动检测线程
        model_name = self.model_combo.currentText()
        self.detection_thread = ConflictDetectionThread(self.requirements_data, model_name)
        self.detection_thread.progress_signal.connect(self.update_progress)
        self.detection_thread.finished_signal.connect(self.detection_finished)
        self.detection_thread.error_signal.connect(self.detection_error)
        self.detection_thread.start()
    
    def cancel_detection(self):
        """取消冲突检测过程"""
        if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
            self.detection_thread.terminate()
            self.detection_thread.wait()
            
            # 重置UI状态
            self.progress_bar.setVisible(False)
            self.detect_btn.setEnabled(True)
            self.load_sample_btn.setEnabled(True)
            self.load_json_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            
            QMessageBox.information(self, "已取消", "冲突检测已取消")
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def detection_finished(self, results):
        """冲突检测完成后的处理"""
        # 保存结果
        self.detection_results = results
        self.detector = results.get("detector")
        
        # 更新UI
        self.update_entity_tree(results.get("entity_results", {}))
        self.update_chunks_tree(results.get("chunk_results", {}))
        self.update_term_tree(self.detector.analysis_results.get("terminology_consistency", {}))
        self.update_conflicts_tree(results.get("conflicts", []))
        self.update_report(results.get("report", ""))
        
        # 重置UI状态
        self.progress_bar.setVisible(False)
        self.detect_btn.setEnabled(True)
        self.load_sample_btn.setEnabled(True)
        self.load_json_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.export_report_btn.setEnabled(True)
        
        QMessageBox.information(self, "分析完成", f"需求冲突检测完成，发现 {len(results.get('conflicts', []))} 个潜在冲突")
    
    def detection_error(self, error_msg):
        """冲突检测过程中的错误处理"""
        # 重置UI状态
        self.progress_bar.setVisible(False)
        self.detect_btn.setEnabled(True)
        self.load_sample_btn.setEnabled(True)
        self.load_json_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        QMessageBox.critical(self, "检测错误", f"冲突检测过程中发生错误:\n{error_msg}")
    
    def update_entity_tree(self, entity_results):
        """更新实体树"""
        self.entity_tree.clear()
        
        for entity_key, req_ids in entity_results.items():
            item = QTreeWidgetItem(self.entity_tree)
            
            # 解析实体和类型
            if ":" in entity_key:
                entity, entity_type = entity_key.split(":", 1)
            else:
                entity, entity_type = entity_key, "未知"
                
            item.setText(0, entity)
            item.setText(1, entity_type)
            item.setText(2, ", ".join(req_ids))
    
    def update_chunks_tree(self, chunk_results):
        """更新名词短语树"""
        self.chunks_tree.clear()
        
        for chunk_text, req_ids in chunk_results.items():
            item = QTreeWidgetItem(self.chunks_tree)
            item.setText(0, chunk_text)
            
            # 简单地使用最后一个词作为根词
            root = chunk_text.split()[-1] if " " in chunk_text else chunk_text
            item.setText(1, root)
            
            item.setText(2, ", ".join(req_ids))
    
    def update_term_tree(self, term_results):
        """更新术语一致性树"""
        self.term_tree.clear()
        
        issues = term_results.get("issues", [])
        for issue in issues:
            item = QTreeWidgetItem(self.term_tree)
            item.setText(0, issue.get("term1", ""))
            item.setText(1, issue.get("term2", ""))
            
            # 合并两个术语的关联需求ID
            req_ids1 = issue.get("req_ids1", [])
            req_ids2 = issue.get("req_ids2", [])
            all_req_ids = list(set(req_ids1 + req_ids2))
            
            item.setText(2, ", ".join(all_req_ids))
    
    def update_conflicts_tree(self, conflicts):
        """更新冲突树"""
        self.conflicts_tree.clear()
        
        # 按冲突类型分组
        conflict_types = {}
        for conflict in conflicts:
            conflict_type = conflict.get("conflict_type", "未知")
            if conflict_type not in conflict_types:
                conflict_types[conflict_type] = []
            conflict_types[conflict_type].append(conflict)
        
        # 添加到树中
        for conflict_type, type_conflicts in conflict_types.items():
            type_item = QTreeWidgetItem(self.conflicts_tree)
            type_item.setText(0, conflict_type)
            type_item.setText(3, f"{len(type_conflicts)} 个冲突")
            type_item.setExpanded(True)
            
            # 添加此类型的所有冲突
            for conflict in type_conflicts:
                item = QTreeWidgetItem(type_item)
                item.setText(0, conflict_type)
                item.setText(1, conflict.get("req_id1", ""))
                item.setText(2, conflict.get("req_id2", ""))
                
                # 存储完整的冲突信息
                item.setData(0, Qt.UserRole, conflict)
    
    def update_report(self, report):
        """更新报告文本区域"""
        # 将纯文本报告转换为HTML格式以便更好地显示
        html_report = report.replace("\n", "<br>")
        html_report = html_report.replace("==================================================", "<hr>")
        html_report = html_report.replace("## ", "<h3>") + "</h3>"
        
        # 替换标题
        for i in range(10):  # 最多支持10级标题
            html_report = html_report.replace(f"<h3>{i+1}. ", f"<h3>{i+1}. ")
        
        self.report_text.setHtml(html_report)
    
    def _highlight_conflict_keywords(self, text, conflict):
        """对文本中的冲突关键词进行高亮处理"""
        highlighted_text = text
        
        # 根据冲突类型查找关键词
        keywords = []
        details = conflict.get("details", {})
        
        # 不同类型的冲突关键词识别
        if conflict["conflict_type"] == "术语不一致":
            if "term1" in details:
                keywords.append(details["term1"])
            if "term2" in details:
                keywords.append(details["term2"])
        
        elif conflict["conflict_type"] == "规则匹配冲突":
            if "text1" in details:
                keywords.append(details["text1"])
            if "text2" in details:
                keywords.append(details["text2"])
            if "rule" in details:
                # 提取规则名中的关键部分
                rule_name = details["rule"]
                if isinstance(rule_name, str) and "CONFLICT_PATTERN_" in rule_name:
                    pattern_index = rule_name.replace("CONFLICT_PATTERN_", "")
                    pattern_keywords = {
                        "0": ["时间", "天", "小时", "分钟", "秒"],
                        "1": ["%", "百分比", "比例"],
                        "2": ["不能", "禁止", "不得", "不应", "不可以"],
                        "3": ["必须", "应该", "需要", "要求"]
                    }
                    if pattern_index in pattern_keywords:
                        # 查找这些关键词在文本中是否存在
                        for keyword in pattern_keywords[pattern_index]:
                            if keyword in text:
                                keywords.append(keyword)
        
        elif conflict["conflict_type"] == "时间约束潜在冲突":
            if "time1" in details and isinstance(details["time1"], list):
                for time_item in details["time1"]:
                    if isinstance(time_item, dict) and "text" in time_item:
                        keywords.append(time_item["text"])
            if "time2" in details and isinstance(details["time2"], list):
                for time_item in details["time2"]:
                    if isinstance(time_item, dict) and "text" in time_item:
                        keywords.append(time_item["text"])
            
            # 添加更多时间相关的关键词
            time_keywords = ["每天", "小时", "分钟", "秒", "工作日", "周", "月", "年"]
            for keyword in time_keywords:
                if keyword in text:
                    keywords.append(keyword)
        
        elif conflict["conflict_type"] == "功能重叠潜在冲突":
            if "resource" in details:
                keywords.append(details["resource"])
            
            # 查找共享资源的相关词
            resource = details.get("resource", "")
            if resource:
                # 如果资源词在文本中有前后缀修饰词，也将其高亮
                # 例如"用户数据"、"数据库"中的"数据"
                resource_pattern = r'(\w{0,5}' + re.escape(resource) + r'\w{0,5})'
                for match in re.finditer(resource_pattern, text):
                    if match.group() != resource:  # 避免重复添加
                        keywords.append(match.group())
        
        elif conflict["conflict_type"] == "安全隐私潜在冲突":
            # 高亮安全隐私相关术语
            security_terms = ["安全", "加密", "保护", "隐私", "认证", "授权", "数据", "用户", "信息"]
            for term in security_terms:
                if term in text:
                    keywords.append(term)
        
        # 对关键词进行高亮，处理可能的嵌套情况
        sorted_keywords = sorted(set(keywords), key=len, reverse=True)  # 确保先处理较长的关键词
        
        for keyword in sorted_keywords:
            if keyword and keyword in highlighted_text:
                highlighted_text = highlighted_text.replace(
                    keyword, f'<span class="highlight">{keyword}</span>'
                )
        
        return highlighted_text
    
    def show_conflict_detail(self, item):
        """显示选中冲突的详细信息"""
        # 检查是否是叶子节点（具体冲突项）
        if item.childCount() > 0:
            return
            
        # 获取完整的冲突信息
        conflict = item.data(0, Qt.UserRole)
        if not conflict:
            return
        
        # 查找关联的需求
        req1 = None
        req2 = None
        for req in self.requirements_data.get("功能需求", []) + self.requirements_data.get("非功能需求", []):
            if req["id"] == conflict["req_id1"]:
                req1 = req
            if req["id"] == conflict["req_id2"]:
                req2 = req
            if req1 and req2:
                break
        
        if not req1 or not req2:
            return
            
        # 构建详情文本，使用CSS美化显示
        detail = """
        <style>
            .conflict-header { background-color: #f8d7da; padding: 10px; border-radius: 5px; }
            .requirement { background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }
            .conflict-point { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .conflict-details { margin-top: 15px; }
            .conflict-item { margin-bottom: 8px; }
            .highlight { background-color: #ffecb3; padding: 2px 4px; font-weight: bold; }
            .req-meta { color: #6c757d; margin-bottom: 5px; }
        </style>
        """
        
        detail += f'<div class="conflict-header"><h2>冲突类型: {conflict["conflict_type"]}</h2></div>\n'
        
        # 显示涉及的需求
        detail += '<h3>涉及需求:</h3>\n'
        detail += f'<div class="requirement">'
        detail += f'<div class="req-meta"><b>需求ID:</b> {req1["id"]} | <b>优先级:</b> {req1["priority"]} | <b>状态:</b> {req1["status"]}</div>'
        detail += f'<h4>{req1["title"]}</h4>'
        detail += f'<p>{self._highlight_conflict_keywords(req1["description"], conflict)}</p>'
        detail += '</div>\n'
        
        detail += f'<div class="requirement">'
        detail += f'<div class="req-meta"><b>需求ID:</b> {req2["id"]} | <b>优先级:</b> {req2["priority"]} | <b>状态:</b> {req2["status"]}</div>'
        detail += f'<h4>{req2["title"]}</h4>'
        detail += f'<p>{self._highlight_conflict_keywords(req2["description"], conflict)}</p>'
        detail += '</div>\n'
        
        # 显示冲突详细说明
        detail += '<div class="conflict-point">'
        detail += '<h3>冲突分析:</h3>\n'
        
        # 根据冲突类型提供不同的说明
        conflict_explanation = self._generate_conflict_explanation(conflict, req1, req2)
        detail += conflict_explanation
        
        # 显示冲突的具体细节
        if "details" in conflict:
            detail += '<div class="conflict-details">'
            detail += '<h4>冲突细节:</h4>'
            
            for key, value in conflict["details"].items():
                if key not in ["type"]:  # 排除已显示的信息
                    detail += f'<div class="conflict-item"><b>{self._format_detail_key(key)}:</b> '
                    
                    # 根据不同类型的值进行格式化显示
                    if isinstance(value, dict):
                        detail += self._format_dict_detail(value)
                    elif isinstance(value, list):
                        detail += self._format_list_detail(value)
                    else:
                        detail += f'{value}'
                    
                    detail += '</div>\n'
            
            detail += '</div>'  # close conflict-details
        
        detail += '</div>'  # close conflict-point
        
        # 显示在需求详情区域
        self.req_detail_text.setHtml(detail)
        
        # 切换到详情标签
        self.tab_widget.setCurrentWidget(self.req_detail_tab)
    
    def _generate_conflict_explanation(self, conflict, req1, req2):
        """根据冲突类型生成对应的解释"""
        conflict_type = conflict.get("conflict_type", "")
        details = conflict.get("details", {})
        
        explanation = ""
        
        if conflict_type == "术语不一致":
            term1 = details.get("term1", "")
            term2 = details.get("term2", "")
            explanation = f'<p>在需求 <b>{req1["id"]}</b> 和 <b>{req2["id"]}</b> 中发现术语不一致。'
            explanation += f'术语 "<span class="highlight">{term1}</span>" 和 '
            explanation += f'"<span class="highlight">{term2}</span>" 可能表达相同的概念，但使用了不同的术语。'
            explanation += f'这可能导致开发人员理解混淆或实现不一致。</p>'
        
        elif conflict_type == "规则匹配冲突":
            rule = details.get("rule", "")
            text1 = details.get("text1", "")
            text2 = details.get("text2", "")
            explanation = f'<p>在需求 <b>{req1["id"]}</b> 和 <b>{req2["id"]}</b> 中发现规则匹配冲突。'
            explanation += f'两个需求中都使用了强制性或约束性表达 "<span class="highlight">{text1}</span>" 和 '
            explanation += f'"<span class="highlight">{text2}</span>"，可能存在实现上的矛盾或冲突。</p>'
        
        elif conflict_type == "时间约束潜在冲突":
            time1_texts = []
            time2_texts = []
            
            if "time1" in details and isinstance(details["time1"], list):
                for time_item in details["time1"]:
                    if isinstance(time_item, dict) and "text" in time_item:
                        time1_texts.append(time_item["text"])
            
            if "time2" in details and isinstance(details["time2"], list):
                for time_item in details["time2"]:
                    if isinstance(time_item, dict) and "text" in time_item:
                        time2_texts.append(time_item["text"])
            
            explanation = f'<p>在需求 <b>{req1["id"]}</b> 和 <b>{req2["id"]}</b> 中发现时间约束潜在冲突。'
            explanation += f'需求 {req1["id"]} 中的时间约束 "<span class="highlight">{", ".join(time1_texts)}</span>" 与 '
            explanation += f'需求 {req2["id"]} 中的时间约束 "<span class="highlight">{", ".join(time2_texts)}</span>" 可能存在冲突。'
            explanation += f'请确认这些时间约束是否兼容，是否会影响系统的实现或用户体验。</p>'
        
        elif conflict_type == "安全隐私潜在冲突":
            reason = details.get("reason", "")
            explanation = f'<p>需求 <b>{req1["id"]}</b> 和需求 <b>{req2["id"]}</b> 之间存在安全隐私潜在冲突。'
            explanation += f'{reason}。'
            explanation += f'功能需求的实现可能会与安全或隐私需求产生矛盾，需要仔细评估和平衡。</p>'
        
        elif conflict_type == "功能重叠潜在冲突":
            resource = details.get("resource", "")
            explanation = f'<p>需求 <b>{req1["id"]}</b> 和需求 <b>{req2["id"]}</b> 之间存在功能重叠潜在冲突。'
            explanation += f'两个需求都涉及到资源 "<span class="highlight">{resource}</span>"，'
            explanation += f'可能存在功能重叠或实现冲突。建议进一步明确各需求的边界，避免功能重复或冲突。</p>'
        
        else:
            explanation = f'<p>需求 <b>{req1["id"]}</b> 和需求 <b>{req2["id"]}</b> 之间存在 {conflict_type}。'
            explanation += f'请进一步分析这些需求之间的关系和可能的冲突点。</p>'
        
        explanation += '<p><b>建议:</b> 在需求评审会议中讨论这一冲突，明确需求间的关系，并确保最终实现的一致性。</p>'
        
        return explanation
    
    def _format_detail_key(self, key):
        """格式化细节键名为更友好的显示名称"""
        key_mapping = {
            "rule": "规则",
            "text1": "文本1",
            "text2": "文本2",
            "term1": "术语1",
            "term2": "术语2",
            "resource": "资源",
            "reason": "原因",
            "time1": "时间约束1",
            "time2": "时间约束2"
        }
        return key_mapping.get(key, key)
    
    def _format_dict_detail(self, dict_value):
        """格式化字典类型的细节值"""
        result = "<ul>"
        for k, v in dict_value.items():
            result += f"<li><b>{k}:</b> {v}</li>"
        result += "</ul>"
        return result
    
    def _format_list_detail(self, list_value):
        """格式化列表类型的细节值"""
        if not list_value:
            return "[]"
        
        # 如果是简单值的列表
        if all(not isinstance(item, (dict, list)) for item in list_value):
            return ", ".join(str(item) for item in list_value)
        
        # 如果是复杂对象的列表
        result = "<ul>"
        for item in list_value:
            if isinstance(item, dict):
                result += "<li>" + self._format_dict_detail(item) + "</li>"
            else:
                result += f"<li>{item}</li>"
        result += "</ul>"
        return result
    
    def export_report(self):
        """导出冲突报告到文件"""
        if not self.detection_results:
            QMessageBox.warning(self, "无数据", "没有可导出的报告数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出冲突报告", "", "Text Files (*.txt);;Markdown Files (*.md);;HTML Files (*.html)"
        )
        
        if not file_path:
            return
            
        try:
            format_type = "text"
            if file_path.endswith(".html"):
                format_type = "html"
            elif file_path.endswith(".md"):
                format_type = "markdown"
                
            # 根据类型生成报告
            report = self.detection_results.get("report", "")
            
            if format_type == "html":
                # 简单转换为HTML
                html_report = "<html><body>"
                html_report += "<h1>需求冲突分析报告</h1>"
                html_report += "<hr>"
                
                # 转换普通文本为HTML
                report_lines = report.split("\n")
                for line in report_lines:
                    if line.startswith("##"):
                        html_report += f"<h2>{line[3:]}</h2>\n"
                    elif line.startswith("="):
                        html_report += "<hr>\n"
                    else:
                        html_report += f"{line}<br>\n"
                        
                html_report += "</body></html>"
                content = html_report
            elif format_type == "markdown":
                # Markdown就是原始文本，稍作调整
                content = "# 需求冲突分析报告\n\n"
                content += report.replace("==", "---")
            else:
                # 纯文本
                content = report
                
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            QMessageBox.information(self, "导出成功", f"报告已成功导出到: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出报告时发生错误: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = NLPConflictDetectorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
