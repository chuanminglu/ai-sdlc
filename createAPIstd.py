"""
API 规范创建对话框模块

此模块提供了创建 API 规范的界面和功能，允许用户基于解析后的用户故事生成 API 规范。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import tempfile
import subprocess
import sys
from parseuserstory import generate_and_save_api_spec

class CreateAPIDialog:
    def __init__(self, parent, parsed_data):
        """
        初始化创建 API 规范对话框
        
        参数:
            parent: 父窗口对象
            parsed_data: 解析后的用户故事数据
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("创建 API 规范")
        self.dialog.geometry("900x700")
        self.dialog.resizable(True, True)
        
        # 保存解析数据
        self.parsed_data = parsed_data
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
        
        # API路径
        self.api_path = tk.StringVar()
        self.auto_generate_path()
        
        # API规范内容
        self.api_spec = None
        self.output_path = None
        
        # 创建界面
        self.setup_ui()
    
    def setup_ui(self):
        """创建对话框界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部部分 - 解析结果显示
        ttk.Label(main_frame, text="用户故事解析结果:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        parsed_frame = ttk.Frame(main_frame)
        parsed_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 创建滚动条
        parsed_scroll = ttk.Scrollbar(parsed_frame)
        parsed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 解析结果文本框
        self.parsed_text = tk.Text(parsed_frame, height=10, wrap=tk.WORD, 
                                  yscrollcommand=parsed_scroll.set)
        self.parsed_text.pack(fill=tk.X, expand=True)
        
        # 设置滚动条的命令
        parsed_scroll.config(command=self.parsed_text.yview)
        
        # 显示解析结果
        self.display_parsed_data()
        self.parsed_text.configure(state='disabled')
        
        # API 路径配置部分
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(10, 20))
        
        ttk.Label(path_frame, text="API 基础路径:").pack(side=tk.LEFT)
        
        # API 路径输入框
        path_entry = ttk.Entry(path_frame, textvariable=self.api_path, width=40)
        path_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # 重新生成按钮
        regenerate_button = ttk.Button(path_frame, text="重新生成路径", 
                                      command=self.auto_generate_path)
        regenerate_button.pack(side=tk.LEFT, padx=5)
        
        # 创建按钮
        self.generate_button = ttk.Button(main_frame, text="生成 API 规范", 
                                         command=self.generate_api_spec)
        self.generate_button.pack(pady=10)
        
        # API 规范显示区域
        ttk.Label(main_frame, text="生成的 API 规范:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(15, 5))
        
        spec_frame = ttk.Frame(main_frame)
        spec_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建滚动条
        spec_scroll = ttk.Scrollbar(spec_frame)
        spec_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # API规范文本框
        self.spec_text = tk.Text(spec_frame, wrap=tk.WORD,
                                yscrollcommand=spec_scroll.set)
        self.spec_text.pack(fill=tk.BOTH, expand=True)
        spec_scroll.config(command=self.spec_text.yview)
        
        # 进度条
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        
        # 底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 保存按钮
        self.save_button = ttk.Button(button_frame, text="保存到文件", 
                                    command=self.save_to_file,
                                    state='disabled')
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="关闭", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def display_parsed_data(self):
        """在文本框中显示解析数据"""
        if not self.parsed_data:
            self.parsed_text.insert('1.0', "没有有效的解析数据")
            return
        
        # 格式化解析结果
        formatted_result = (
            f"领域: {self.parsed_data.get('domain', '未指定')}\n"
            f"角色: {self.parsed_data.get('role', '')}\n"
            f"目标: {self.parsed_data.get('goal', '')}\n"
            f"价值: {self.parsed_data.get('value', '')}\n\n"
            f"验收标准:\n"
        )
        
        for i, criterion in enumerate(self.parsed_data.get('criteria', []), 1):
            formatted_result += f"{i}. {criterion}\n"
        
        # 如果有领域概念，也显示出来
        if self.parsed_data.get('domain_concepts'):
            formatted_result += f"\n领域概念: {', '.join(self.parsed_data.get('domain_concepts'))}\n"
        
        self.parsed_text.insert('1.0', formatted_result)
    
    def auto_generate_path(self):
        """自动生成 API 路径"""
        if not self.parsed_data:
            self.api_path.set("/api/v1/resource")
            return
        
        # 根据解析数据生成路径
        domain = self.parsed_data.get('domain', '').lower().replace(' ', '')
        goal = self.parsed_data.get('goal', '').lower()
        
        # 尝试从目标中提取核心名词作为资源名
        import re
        resource = ''
        
        # 常见资源词汇
        common_resources = ['product', 'user', 'order', 'comment', 'review', 'rating', 
                           'item', 'category', 'tag', 'article', 'post', 'message']
        
        # 中文资源词汇及其映射
        cn_resources = {
            '商品': 'products',
            '产品': 'products',
            '用户': 'users',
            '会员': 'members',
            '订单': 'orders',
            '评论': 'comments',
            '评价': 'reviews',
            '评分': 'ratings',
            '分类': 'categories',
            '标签': 'tags',
            '文章': 'articles',
            '帖子': 'posts',
            '消息': 'messages',
            '排序': 'sorting',
            '筛选': 'filter'
        }
        
        # 尝试从目标中匹配中文资源词
        for cn, en in cn_resources.items():
            if cn in goal:
                resource = en
                break
        
        # 如果没找到，尝试从英文匹配
        if not resource:
            for res in common_resources:
                if res in goal.lower():
                    resource = res + 's'  # 英文复数形式
                    break
        
        # 如果还是没找到，使用领域名作为前缀
        if not resource:
            if domain:
                resource = domain + 's'
            else:
                resource = 'resources'
        
        # 构建完整路径
        path = f"/api/v1/{resource}"
        
        # 特殊处理评论相关的API
        if any(word in goal for word in ['评论', '评价', 'comment', 'review']):
            if 'product' in goal or '商品' in goal or '产品' in goal:
                path = "/api/v1/products/comments"
        
        self.api_path.set(path)
    
    def show_progress(self, show=True, message="正在生成API规范..."):
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
    
    def generate_api_spec(self):
        """生成API规范"""
        api_path = self.api_path.get().strip()
        if not api_path:
            messagebox.showerror("错误", "请指定API路径")
            return
        
        # 添加API路径到解析数据
        self.parsed_data['api_path'] = api_path
        
        # 显示进度条
        self.show_progress(True)
        
        # 在新线程中生成规范
        def generate():
            try:
                # 创建临时文件路径
                import tempfile
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, "temp_api_spec.json")
                
                # 生成API规范
                api_spec = generate_and_save_api_spec(self.parsed_data, temp_file)
                
                # 读取生成的文件
                with open(temp_file, 'r', encoding='utf-8') as f:
                    spec_json = json.load(f)
                
                # 格式化JSON以便显示
                formatted_json = json.dumps(spec_json, indent=2, ensure_ascii=False)
                
                # 保存结果
                self.api_spec = spec_json
                self.output_path = temp_file
                
                # 在UI线程中更新文本框
                self.dialog.after(0, lambda: self.update_spec_text(formatted_json))
                
            except Exception as e:
                self.dialog.after(0, lambda: messagebox.showerror("错误", f"生成API规范时发生错误: {str(e)}"))
            finally:
                self.dialog.after(0, lambda: self.show_progress(False))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def update_spec_text(self, formatted_json):
        """更新规范文本框中的内容"""
        self.spec_text.delete('1.0', tk.END)
        self.spec_text.insert('1.0', formatted_json)
        # 启用保存按钮
        self.save_button.configure(state='normal')
    
    def save_to_file(self):
        """保存API规范到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存API规范")
        
        if file_path:
            try:
                # 获取当前文本框中的内容
                spec_json = self.spec_text.get("1.0", tk.END)
                
                # 保存到文件
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(spec_json)
                
                messagebox.showinfo("成功", f"API规范已保存到: {file_path}")
                
                # 更新类属性保存最新文件路径
                self.saved_file_path = file_path
                
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时发生错误: {str(e)}")
    
    def _open_file(self, file_path):
        """尝试用默认应用打开文件"""
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # linux variants
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            messagebox.showwarning("提示", f"无法自动打开文件: {str(e)}\n文件路径: {file_path}")
    
    def run(self):
        """运行对话框并返回结果"""
        self.dialog.wait_window()
        return self.output_path

if __name__ == "__main__":
    # 测试代码
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建测试数据
    test_data = {
        'domain': '电商平台',
        'role': '会员',
        'goal': '按照评分排序商品',
        'value': '更快找到高质量商品',
        'criteria': [
            '能够按照评分从高到低排序商品',
            '可以筛选近3个月的评论',
            '支持综合排序算法'
        ]
    }
    
    # 创建并显示对话框
    dialog = CreateAPIDialog(root, test_data)
    result = dialog.run()
    print("生成的API规范:", result)
    
    root.destroy()