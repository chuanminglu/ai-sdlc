"""
用户故事拆分对话框模块

此模块提供了用户故事拆分的界面和功能，允许用户将大型用户故事拆分为多个较小的、更具体的故事。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

class SplitStoryDialog:
    def __init__(self, parent, story):
        """
        初始化拆分用户故事对话框
        
        参数:
            parent: 父窗口对象
            story: 要拆分的用户故事文本
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("拆分用户故事")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # 保存原始故事
        self.story = story
        self.parent = parent
        
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
        
        # 结果变量
        self.result = None
        self.story_count = tk.IntVar(value=3)
        
        # 存储拆分后的故事
        self.split_stories = []
        
        # 创建界面
        self.setup_ui()
    
    def setup_ui(self):
        """创建对话框界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部分 - 原始故事和拆分选项
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 显示原始故事摘要
        ttk.Label(top_frame, text="原始故事摘要:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        summary_frame = ttk.Frame(top_frame)
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 创建滚动条
        summary_scroll = ttk.Scrollbar(summary_frame)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 增大摘要文本框，并添加滚动条
        self.summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD, 
                                   yscrollcommand=summary_scroll.set)
        self.summary_text.pack(fill=tk.X, expand=True)
        
        # 设置滚动条的命令
        summary_scroll.config(command=self.summary_text.yview)
        
        # 显示原始故事的完整内容
        self.summary_text.insert('1.0', self.story)
        self.summary_text.configure(state='disabled')
        
        # 拆分选项
        options_frame = ttk.Frame(top_frame)
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(options_frame, text="拆分数量:").pack(side=tk.LEFT, padx=(0, 10))
        
        # 数量选择器
        count_spinner = ttk.Spinbox(options_frame, from_=2, to=5, width=5, textvariable=self.story_count)
        count_spinner.pack(side=tk.LEFT, padx=(0, 20))
        
        # 生成按钮
        self.generate_button = ttk.Button(options_frame, text="生成拆分故事", 
                                        command=self.generate_split_stories)
        self.generate_button.pack(side=tk.LEFT)
        
        # 中部和下部 - 包含故事列表和故事详情
        bottom_frame = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左侧 - 故事列表
        list_frame = ttk.Frame(bottom_frame)
        bottom_frame.add(list_frame, weight=1)
        
        ttk.Label(list_frame, text="拆分的子故事:").pack(anchor=tk.W, pady=5)
        
        # 创建故事列表框和滚动条
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.story_listbox = tk.Listbox(list_frame, height=15, 
                                       yscrollcommand=list_scroll.set)
        self.story_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.story_listbox.yview)
        
        # 绑定列表选择事件
        self.story_listbox.bind('<<ListboxSelect>>', self.on_story_select)
        
        # 右侧 - 故事详情
        detail_frame = ttk.Frame(bottom_frame)
        bottom_frame.add(detail_frame, weight=2)
        
        ttk.Label(detail_frame, text="故事详情:").pack(anchor=tk.W, pady=5)
        
        # 创建故事详情文本框和滚动条
        detail_scroll = ttk.Scrollbar(detail_frame)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD,
                                 yscrollcommand=detail_scroll.set)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        detail_scroll.config(command=self.detail_text.yview)
        
        # 进度条
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.select_button = ttk.Button(button_frame, text="选择当前故事", 
                                      command=self.select_current_story,
                                      state='disabled')
        self.select_button.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="关闭", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_progress(self, show=True, message="正在拆分用户故事..."):
        """显示或隐藏进度条"""
        if show:
            self.progress_bar.pack(fill=tk.X, pady=5)
            self.progress_bar.start(10)
            self.progress_var.set(message)
            self.generate_button.configure(state='disabled')
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_var.set("")
            self.generate_button.configure(state='normal')
    
    def on_story_select(self, event):
        """当用户选择故事列表中的一项时触发"""
        selection = self.story_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.split_stories):
                # 在详情文本框中显示选中的故事
                self.detail_text.delete('1.0', tk.END)
                self.detail_text.insert('1.0', self.split_stories[index])
                # 启用选择按钮
                self.select_button.configure(state='normal')
    
    def generate_split_stories(self):
        """生成拆分故事的处理函数"""
        count = self.story_count.get()
        
        # 显示进度条
        self.show_progress(True)
        
        # 清空之前的结果
        self.story_listbox.delete(0, tk.END)
        self.detail_text.delete('1.0', tk.END)
        self.split_stories = []
        
        # 在新线程中执行拆分
        def split():
            try:
                # 导入拆分功能
                from parseuserstory import split_user_story, parse_user_story
                
                # 获取领域和角色信息（从主窗口获取）
                domain = ""
                role = ""
                
                # 安全地获取主窗口的输入值
                if hasattr(self.parent, 'domain_entry') and hasattr(self.parent, 'role_entry'):
                    domain = self.parent.domain_entry.get().strip()
                    role = self.parent.role_entry.get().strip()
                
                # 调用拆分函数
                stories = split_user_story(self.story, domain, role, count)
                
                if stories and len(stories) > 0:
                    self.split_stories = stories
                    
                    # 在主线程中更新UI
                    self.dialog.after(0, lambda: self.update_story_list(stories))
                else:
                    self.dialog.after(0, lambda: messagebox.showerror("错误", 
                                                               "无法拆分用户故事，请检查故事内容或重试"))
            except Exception as e:
                self.dialog.after(0, lambda: messagebox.showerror("错误", 
                                                           f"拆分用户故事时发生错误: {str(e)}"))
            finally:
                self.dialog.after(0, lambda: self.show_progress(False))
        
        threading.Thread(target=split, daemon=True).start()
    
    def update_story_list(self, stories):
        """更新故事列表"""
        for i, story in enumerate(stories):
            # 尝试解析故事获取目标
            try:
                from parseuserstory import parse_user_story
                parsed = parse_user_story(story)
                title = parsed.get('goal', f"用户故事 {i+1}")
            except:
                title = f"用户故事 {i+1}"
                
            # 添加到列表框
            self.story_listbox.insert(tk.END, title)
        
        # 自动选择第一个故事
        if len(stories) > 0:
            self.story_listbox.selection_set(0)
            self.story_listbox.event_generate('<<ListboxSelect>>')
    
    def select_current_story(self):
        """选择当前故事并返回结果"""
        selection = self.story_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.split_stories):
                self.result = {
                    'selected_story': self.split_stories[index]
                }
                self.dialog.destroy()
    
    def get_result(self):
        """等待对话框关闭并返回结果"""
        self.dialog.wait_window()
        return self.result