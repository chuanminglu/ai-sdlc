"""
基于PyQt5实现的需求冲突检测GUI界面
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# 确保能够导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QGroupBox, QCheckBox, QPushButton, QMessageBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox, QFileDialog,
    QStatusBar, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# 导入极客书店需求样例和冲突检测器
from conflict_detector.geek_bookstore_requirements import GEEK_BOOKSTORE_REQUIREMENTS
from conflict_detector.conflict_detector import RequirementConflictDetector

class ConflictDetectionThread(QThread):
    """
    需求冲突检测线程，用于在后台进行冲突检测，避免阻塞UI
    """
    # 定义信号
    finished = pyqtSignal(object)  # 检测完成信号，传递结果
    progress = pyqtSignal(int)     # 进度更新信号
    error = pyqtSignal(str)        # 错误信号
    
    def __init__(self, detector, requirements, dimensions):
        """
        初始化检测线程
        
        Args:
            detector: 需求冲突检测器实例
            requirements: 需求字典
            dimensions: 要分析的维度列表，如果为空则分析所有维度
        """
        super().__init__()
        self.detector = detector
        self.requirements = requirements
        self.dimensions = dimensions
    
    def run(self):
        """执行需求冲突检测"""
        try:
            from datetime import datetime
            
            results = {
                "conflicts": [],
                "metadata": {
                    "total_requirements": sum(len(reqs) for reqs in self.requirements.values()),
                    "dimensions_analyzed": self.dimensions if self.dimensions else ["全部维度"],
                    "total_conflicts": 0,
                    "timestamp": datetime.now().isoformat()  # 添加时间戳
                }
            }
            
            total_dimensions = len(self.dimensions) if self.dimensions else len(self.detector.CONFLICT_DIMENSIONS)
            for i, dimension in enumerate(self.dimensions if self.dimensions else [None]):
                # 更新进度
                progress_value = int((i / total_dimensions) * 100)
                self.progress.emit(progress_value)
                
                # 调用检测器进行分析
                result = self.detector.detect_conflicts(self.requirements, dimension)
                results["conflicts"].extend(result["conflicts"])
                
                # 稍作暂停，避免过快的API调用
                self.msleep(100)
            
            # 更新元数据
            results["metadata"]["total_conflicts"] = len(results["conflicts"])
            results["metadata"]["conflicts_by_severity"] = {
                level: len([c for c in results["conflicts"] if c["severity"] == level])
                for level in self.detector.SEVERITY_LEVELS
            }
            
            # 发送完成信号
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))

class ConflictDetectorGUI(QMainWindow):
    """需求冲突检测GUI界面"""
    
    def __init__(self):
        """初始化GUI界面"""
        super().__init__()
        
        # 创建冲突检测器实例
        self.detector = RequirementConflictDetector()
        
        # 默认使用极客书店需求样例
        self.requirements = GEEK_BOOKSTORE_REQUIREMENTS
        
        # 初始化UI
        self.init_ui()
        
        # 设置窗口属性
        self.setWindowTitle("需求冲突检测工具")
        self.setGeometry(100, 100, 1200, 800)
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板 - 控制和需求显示
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 1. 控制区域
        control_group = QGroupBox("控制面板")
        control_layout = QVBoxLayout()
        
        # 分析维度选择
        dimensions_group = QGroupBox("选择分析维度")
        dimensions_layout = QVBoxLayout()
        
        self.dimension_checkboxes = {}
        for dimension in self.detector.CONFLICT_DIMENSIONS.keys():
            checkbox = QCheckBox(dimension)
            self.dimension_checkboxes[dimension] = checkbox
            dimensions_layout.addWidget(checkbox)
        
        # 全选/取消全选按钮
        select_buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        deselect_all_btn = QPushButton("取消全选")
        select_all_btn.clicked.connect(self.select_all_dimensions)
        deselect_all_btn.clicked.connect(self.deselect_all_dimensions)
        select_buttons_layout.addWidget(select_all_btn)
        select_buttons_layout.addWidget(deselect_all_btn)
        
        dimensions_layout.addLayout(select_buttons_layout)
        dimensions_group.setLayout(dimensions_layout)
        control_layout.addWidget(dimensions_group)
        
        # 加载需求和运行检测的按钮
        buttons_layout = QHBoxLayout()
        load_btn = QPushButton("加载需求")
        run_btn = QPushButton("开始检测")
        load_btn.clicked.connect(self.load_requirements)
        run_btn.clicked.connect(self.run_detection)
        buttons_layout.addWidget(load_btn)
        buttons_layout.addWidget(run_btn)
        control_layout.addLayout(buttons_layout)
        
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        # 2. 需求显示区域
        requirements_group = QGroupBox("原始需求")
        requirements_layout = QVBoxLayout()
        
        self.requirements_display = QTextEdit()
        self.requirements_display.setReadOnly(True)
        self.update_requirements_display()
        
        requirements_layout.addWidget(self.requirements_display)
        requirements_group.setLayout(requirements_layout)
        left_layout.addWidget(requirements_group)
        
        # 右侧面板 - 检测结果
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        results_group = QGroupBox("检测结果")
        results_layout = QVBoxLayout()
        
        # 添加结果显示选择器
        view_layout = QHBoxLayout()
        view_label = QLabel("查看方式:")
        self.view_selector = QComboBox()
        self.view_selector.addItems(["树形视图", "详细信息"])
        self.view_selector.currentIndexChanged.connect(self.switch_view)
        view_layout.addWidget(view_label)
        view_layout.addWidget(self.view_selector)
        view_layout.addStretch()
        
        # 添加导出按钮
        export_btn = QPushButton("导出报告")
        export_btn.clicked.connect(self.export_report)
        view_layout.addWidget(export_btn)
        
        results_layout.addLayout(view_layout)
        
        # 树形视图
        self.tree_view = QTreeWidget()
        self.tree_view.setHeaderLabels(["冲突信息", "详情"])
        self.tree_view.setColumnWidth(0, 300)
        
        # 详细视图
        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        
        # 初始显示树形视图
        results_layout.addWidget(self.tree_view)
        self.detail_view.hide()
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # 添加面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        # 添加状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 添加进度条到状态栏
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.hide()
        self.statusBar.addPermanentWidget(self.progress_bar)
        
        # 显示初始状态
        self.statusBar.showMessage("就绪")
    
    def select_all_dimensions(self):
        """全选所有维度"""
        for checkbox in self.dimension_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_dimensions(self):
        """取消全选所有维度"""
        for checkbox in self.dimension_checkboxes.values():
            checkbox.setChecked(False)
    
    def update_requirements_display(self):
        """更新需求显示区域"""
        # 将需求字典格式化为易读的文本
        requirements_text = ""
        
        for category, reqs in self.requirements.items():
            requirements_text += f"=== {category} ===\n\n"
            
            for req in reqs:
                requirements_text += f"ID: {req['id']}\n"
                requirements_text += f"标题: {req['title']}\n"
                requirements_text += f"描述: {req['description']}\n"
                requirements_text += f"优先级: {req['priority']}\n"
                requirements_text += f"负责团队: {req['owner']}\n\n"
        
        self.requirements_display.setText(requirements_text)
    
    def load_requirements(self):
        """加载需求文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择需求JSON文件", "", "JSON文件 (*.json)"
            )
            
            if not file_path:
                return  # 用户取消了选择
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.requirements = json.load(f)
            
            self.update_requirements_display()
            self.statusBar.showMessage(f"已加载需求文件: {Path(file_path).name}")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载需求文件失败: {str(e)}")
            self.statusBar.showMessage("加载需求失败")
    
    def run_detection(self):
        """运行需求冲突检测"""
        # 获取选中的维度
        selected_dimensions = [
            dimension for dimension, checkbox in self.dimension_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        if not selected_dimensions:
            QMessageBox.warning(self, "警告", "请至少选择一个分析维度")
            return
        
        # 更新状态
        self.statusBar.showMessage("正在分析需求冲突...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        # 禁用控制区域
        for checkbox in self.dimension_checkboxes.values():
            checkbox.setEnabled(False)
        
        # 创建并启动检测线程
        self.detection_thread = ConflictDetectionThread(
            self.detector, self.requirements, selected_dimensions
        )
        self.detection_thread.finished.connect(self.update_results)
        self.detection_thread.progress.connect(self.update_progress)
        self.detection_thread.error.connect(self.show_error)
        self.detection_thread.start()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def show_error(self, error_msg):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", f"冲突检测失败: {error_msg}")
        self.statusBar.showMessage("检测失败")
        self.progress_bar.hide()
        
        # 重新启用控制区域
        for checkbox in self.dimension_checkboxes.values():
            checkbox.setEnabled(True)
    
    def update_results(self, results):
        """更新检测结果"""
        self.detection_results = results
        
        # 清空当前视图
        self.tree_view.clear()
        self.detail_view.clear()
        
        # 更新树形视图
        if results["conflicts"]:
            # 按维度分组
            conflicts_by_dimension = {}
            for conflict in results["conflicts"]:
                dim = conflict["dimension"]
                if dim not in conflicts_by_dimension:
                    conflicts_by_dimension[dim] = []
                conflicts_by_dimension[dim].append(conflict)
            
            # 添加到树形视图
            for dim, conflicts in conflicts_by_dimension.items():
                dim_item = QTreeWidgetItem(self.tree_view, [dim, f"{len(conflicts)}个冲突"])
                dim_item.setExpanded(True)
                
                for conflict in conflicts:
                    conflict_item = QTreeWidgetItem(dim_item, [
                        conflict["conflict_type"], 
                        f"严重度: {conflict['severity']} | 需求: {', '.join(conflict['requirements'])}"
                    ])
                    
                    QTreeWidgetItem(conflict_item, ["描述", conflict["description"]])
                    QTreeWidgetItem(conflict_item, ["影响", conflict["impact"]])
                    QTreeWidgetItem(conflict_item, ["建议", conflict["suggestion"]])
        else:
            # 无冲突
            QTreeWidgetItem(self.tree_view, ["无检测结果", "未发现需求冲突"])
        
        # 更新详细视图
        self.update_detail_view()
        
        # 更新状态
        count = len(results["conflicts"])
        self.statusBar.showMessage(f"检测完成，共发现 {count} 个冲突")
        self.progress_bar.hide()
        
        # 重新启用控制区域
        for checkbox in self.dimension_checkboxes.values():
            checkbox.setEnabled(True)
    
    def update_detail_view(self):
        """更新详细视图"""
        if not hasattr(self, 'detection_results'):
            return
        
        # 生成Markdown格式的报告
        report = self.detector.generate_conflict_report(
            self.detection_results, format="markdown"
        )
        
        # 在详细视图中显示
        self.detail_view.setMarkdown(report)
    
    def switch_view(self, index):
        """切换视图模式"""
        if index == 0:  # 树形视图
            self.tree_view.show()
            self.detail_view.hide()
        else:  # 详细信息
            self.tree_view.hide()
            self.detail_view.show()
    
    def export_report(self):
        """导出冲突报告"""
        if not hasattr(self, 'detection_results') or not self.detection_results["conflicts"]:
            QMessageBox.warning(self, "警告", "没有可导出的检测结果")
            return
        
        try:
            file_path, file_filter = QFileDialog.getSaveFileName(
                self, "保存冲突报告", "", 
                "Markdown文档 (*.md);;JSON文件 (*.json)"
            )
            
            if not file_path:
                return  # 用户取消了保存
            
            # 根据选择的过滤器确定格式
            format_type = "markdown" if ".md" in file_filter else "json"
            
            # 生成报告
            report = self.detector.generate_conflict_report(
                self.detection_results, format=format_type
            )
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.statusBar.showMessage(f"报告已导出到: {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出报告失败: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ConflictDetectorGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()