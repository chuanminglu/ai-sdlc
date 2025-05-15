#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI-SDLC应用主菜单GUI
整合了mainui、conflict_detector_gui和nlp_conflict_detector_gui应用
"""

import sys
import os
from pathlib import Path
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class MainMenuGUI(QMainWindow):
    """
    主菜单GUI类，整合多个应用的启动入口
    """
    def __init__(self):
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("AI-SDLC 工具套件")
        self.setMinimumSize(600, 450)
        
        # 设置窗口居中
        self._center_window()
        
        # 初始化GUI
        self.init_ui()
        
    def _center_window(self):
        """将窗口居中显示"""
        screen_geometry = QApplication.desktop().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def init_ui(self):
        """初始化用户界面"""
        # 创建中央窗口部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel("AI-SDLC 工具套件")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 添加副标题
        subtitle_label = QLabel("选择要启动的应用")
        subtitle_font = QFont("Arial", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # 添加应用启动按钮
        self.add_app_button(main_layout, "用户故事管理工具", 
                          "启动用户故事解析、生成、拆分和约束管理工具",
                          self.launch_mainui)
        
        self.add_app_button(main_layout, "传统需求冲突检测", 
                          "启动基于规则的需求冲突检测工具",
                          self.launch_conflict_detector)
                          
        self.add_app_button(main_layout, "NLP需求冲突检测", 
                          "启动基于自然语言处理的需求冲突检测工具",
                          self.launch_nlp_conflict_detector)
        
        # 添加退出按钮
        exit_button = QPushButton("退出")
        exit_button.setMinimumHeight(40)
        exit_button.clicked.connect(self.close)
        main_layout.addWidget(exit_button)
        
        # 添加状态栏
        self.statusBar().showMessage("就绪")
        
    def add_app_button(self, layout, title, description, callback):
        """添加应用启动按钮"""
        button = QPushButton(f"{title}\n{description}")
        button.setMinimumHeight(80)
        font = QFont("Arial", 10)
        button.setFont(font)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def launch_mainui(self):
        """启动用户故事管理工具"""
        self.statusBar().showMessage("正在启动用户故事管理工具...")
        try:
            # 使用subprocess启动主UI应用
            subprocess.Popen([sys.executable, os.path.join(get_project_root(), "mainui.py")])
            self.statusBar().showMessage("已启动用户故事管理工具")
        except Exception as e:
            self.statusBar().showMessage(f"启动失败: {str(e)}")
            QMessageBox.critical(self, "启动错误", f"无法启动用户故事管理工具: {str(e)}")
    
    def launch_conflict_detector(self):
        """启动传统需求冲突检测工具"""
        self.statusBar().showMessage("正在启动传统需求冲突检测工具...")
        try:
            # 使用subprocess启动冲突检测器GUI
            subprocess.Popen([sys.executable, os.path.join(get_project_root(), "conflict_detector", "conflict_detector_gui.py")])
            self.statusBar().showMessage("已启动传统需求冲突检测工具")
        except Exception as e:
            self.statusBar().showMessage(f"启动失败: {str(e)}")
            QMessageBox.critical(self, "启动错误", f"无法启动传统需求冲突检测工具: {str(e)}")
    
    def launch_nlp_conflict_detector(self):
        """启动NLP需求冲突检测工具"""
        self.statusBar().showMessage("正在启动NLP需求冲突检测工具...")
        try:
            # 使用subprocess启动NLP冲突检测器GUI
            subprocess.Popen([sys.executable, os.path.join(get_project_root(), "conflict_detector", "nlp_conflict_detector_gui.py")])
            self.statusBar().showMessage("已启动NLP需求冲突检测工具")
        except Exception as e:
            self.statusBar().showMessage(f"启动失败: {str(e)}")
            QMessageBox.critical(self, "启动错误", f"无法启动NLP需求冲突检测工具: {str(e)}")


def get_project_root():
    """获取项目根目录路径"""
    # 假设当前脚本在项目根目录下
    return str(Path(__file__).parent)


def main():
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    main_window = MainMenuGUI()
    main_window.show()
    
    # 启动应用事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
