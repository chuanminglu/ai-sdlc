import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import datetime
import threading
import time
import os
from pathlib import Path
import configparser
import re
from llm_interface import LLMInterface

class ConstraintsDialog:
    """约束检查清单对话框类"""
    
    def __init__(self, parent, parsed_data):
        """初始化对话框
        
        Args:
            parent: 父窗口
            parsed_data: 解析后的用户故事数据
        """
        self.parent = parent
        self.parsed_data = parsed_data
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("约束检查清单生成")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        
        # 使对话框模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中对话框
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # 创建UI组件
        self.create_widgets()
        
        # 约束清单数据
        self.constraints_list = []
        self.processing = False
        self.llm = LLMInterface()  # 使用统一的LLM接口
    
    def create_widgets(self):
        """创建UI组件"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="约束检查清单生成", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # 解析结果显示区域
        ttk.Label(main_frame, text="解析结果:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        parsed_frame = ttk.Frame(main_frame)
        parsed_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.parsed_text = tk.Text(parsed_frame, height=8, wrap=tk.WORD)
        self.parsed_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parsed_frame, command=self.parsed_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.parsed_text.configure(yscrollcommand=scrollbar.set)
        
        # 显示解析结果
        self.show_parsed_data()
        
        # 约束清单生成区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.generate_button = ttk.Button(button_frame, text="生成约束清单", 
                                         command=self.generate_constraints)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(button_frame, text="保存约束清单", 
                                     command=self.save_constraints,
                                     state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(button_frame, text="关闭", 
                                      command=self.dialog.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)
        
        # 进度条
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        
        # 约束清单显示区域
        ttk.Label(main_frame, text="约束清单:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        constraints_frame = ttk.Frame(main_frame)
        constraints_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建约束清单文本框
        self.constraints_text = tk.Text(constraints_frame, wrap=tk.WORD)
        self.constraints_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(constraints_frame, command=self.constraints_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.constraints_text.configure(yscrollcommand=scrollbar.set)
        
    def show_parsed_data(self):
        """显示解析后的用户故事数据"""
        formatted_result = (
            f"领域: {self.parsed_data.get('domain', '')}\n"
            f"角色: {self.parsed_data.get('role', '')}\n"
            f"目标: {self.parsed_data.get('goal', '')}\n"
            f"价值: {self.parsed_data.get('value', '')}\n\n"
            f"验收标准:\n"
        )
        
        for i, criterion in enumerate(self.parsed_data.get('criteria', []), 1):
            formatted_result += f"{i}. {criterion}\n"
        
        self.parsed_text.delete('1.0', tk.END)
        self.parsed_text.insert('1.0', formatted_result)
    
    def show_progress(self, show=True, message=""):
        """显示或隐藏进度条"""
        if show:
            self.progress_bar.pack(fill=tk.X, pady=5)
            self.progress_bar.start(10)
            self.progress_var.set(message)
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_var.set(message if message else "")
    
    def generate_constraints(self):
        """生成约束清单"""
        if self.processing:
            return
        
        self.processing = True
        self.generate_button.configure(state=tk.DISABLED)
        self.save_button.configure(state=tk.DISABLED)
        self.constraints_text.delete('1.0', tk.END)
        self.show_progress(True, "正在生成约束清单...")
        
        # 启动生成线程
        threading.Thread(target=self._generate_constraints_thread, daemon=True).start()
    
    def _generate_constraints_thread(self):
        """在新线程中生成约束清单"""
        try:
            # 生成约束清单提示词
            prompt = self._generate_prompt()
            
            # 调用API获取生成内容
            constraints_text = self.llm.complete(prompt)
            
            # 在主线程中更新UI
            self.dialog.after(0, lambda: self._update_constraints(constraints_text))
            
        except Exception as e:
            self.dialog.after(0, lambda: self._show_error(str(e)))
        finally:
            self.dialog.after(0, self._finish_processing)
    
    def _generate_prompt(self):
        """生成约束清单提示词"""
        domain = self.parsed_data.get('domain', '')
        role = self.parsed_data.get('role', '')
        goal = self.parsed_data.get('goal', '')
        value = self.parsed_data.get('value', '')
        criteria = self.parsed_data.get('criteria', [])
        
        criteria_str = "\n".join([f"- {criterion}" for criterion in criteria])
        
        prompt = f"""
请你作为软件工程质量专家，为以下用户故事生成系统约束检查清单。
用户故事包含以下信息：
- 领域：{domain}
- 角色：{role}
- 目标：{goal}
- 价值：{value}
- 验收标准：
{criteria_str}

请生成一个全面的约束检查清单，包含以下类型的约束（但不限于这些类型）：
1. 性能约束
2. 安全性约束
3. 可靠性约束
4. 可扩展性约束
5. 兼容性约束
6. 合规性约束
7. 可用性约束
8. 可维护性约束

对于每一项约束，请提供以下信息：
- 约束类型（例如：性能、安全性等）
- 度量指标（例如：响应时间、并发用户数等）
- 要求值（例如：500毫秒、99.9%等）
- 约束描述（简短说明这个约束的必要性和意义）

请以JSON格式输出，格式如下：
[
  {{
    "type": "约束类型",
    "metric": "度量指标",
    "value": "要求值",
    "description": "约束描述"
  }},
  ...
]
"""
        return prompt
    
    def _update_constraints(self, content):
        """更新约束清单文本框"""
        self.constraints_text.delete('1.0', tk.END)
        self.constraints_text.insert('1.0', content)
    
    def _finish_processing(self):
        """完成生成约束清单"""
        self.processing = False
        self.generate_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.NORMAL)
        self.show_progress(False, "约束清单生成完成")
    
    def _show_error(self, message):
        """显示错误消息"""
        messagebox.showerror("错误", f"生成约束清单时发生错误: {message}")
    
    def save_constraints(self):
        """保存约束清单为Markdown文件"""
        if not self.constraints_list:
            messagebox.showwarning("警告", "没有可保存的约束清单，请先生成约束清单")
            return
        
        # 获取保存文件路径
        domain = self.parsed_data.get('domain', '未指定领域')
        default_filename = f"{domain}_约束清单_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        
        file_path = filedialog.asksaveasfilename(
            parent=self.dialog,
            title="保存约束清单",
            initialfile=default_filename,
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return  # 用户取消了保存
        
        try:
            # 获取当前显示的内容
            content = self.constraints_text.get('1.0', tk.END)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("成功", f"约束清单已保存到: {file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存约束清单时发生错误: {str(e)}")
    
    def show(self):
        """显示对话框"""
        self.dialog.mainloop()


if __name__ == "__main__":
    # 测试代码
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 模拟解析数据
    parsed_data = {
        'domain': '电商平台',
        'role': '会员',
        'goal': '通过商品评论排序筛选商品',
        'value': '提升购物决策效率',
        'criteria': [
            '支持按照评分(1-5星)降序排列',
            '允许选择近3个月的评论',
            '默认显示综合排序(评分*70%+新近度*30%)'
        ]
    }
    
    dialog = ConstraintsDialog(root, parsed_data)
    dialog.show()