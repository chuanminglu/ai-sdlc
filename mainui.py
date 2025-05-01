import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from parseuserstory import generate_user_story, parse_user_story, generate_and_save_api_spec, generate_multiple_user_stories
import re
import threading
import time
import queue
import warnings
import os
import logging
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from typing import Dict

def get_free_port():
    """获取一个空闲端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_doc_server(port=None):
    """启动文档服务器"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if port is None:
                port = get_free_port()
            server_address = ('', port)
            httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
            
            def run_server():
                httpd.serve_forever()
            
            # 在新线程中启动服务器
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            return httpd
        except OSError:
            if attempt < max_retries - 1:
                port = None  # Retry with a new port
            else:
                raise RuntimeError("无法启动文档服务器：所有尝试均失败")

# 禁用所有警告
warnings.filterwarnings('ignore')

# 配置日志记录器来捕获警告
logging.captureWarnings(True)
logging.getLogger().setLevel(logging.ERROR)

# 设置环境变量来禁用各种警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'
os.environ['PYTHONWARNINGS'] = 'ignore'

class VoiceRecorderDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("语音输入")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        
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
        
        self.setup_ui()
        self.is_recording = False
        self.result = None
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="准备录音...", font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # 录音时长
        self.time_label = ttk.Label(main_frame, text="00:00", font=('Arial', 14))
        self.time_label.pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # 开始/停止按钮
        self.record_button = ttk.Button(button_frame, text="开始录音", 
                                      command=self.toggle_recording)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        self.cancel_button = ttk.Button(button_frame, text="取消", 
                                      command=self.cancel_recording)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.configure(text="停止录音")
        self.status_label.configure(text="正在录音...")
        self.start_time = time.time()
        
        # 开始计时器
        self.update_timer()
        
        # 在新线程中开始录音
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.start()

    def _record_audio(self):
        self.recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.audio = self.recognizer.listen(source, timeout=30)
        except Exception as error:
            self.dialog.after(0, lambda error=error: self.status_label.configure(text=f"录音错误: {str(error)}"))

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.configure(text="处理中...")
            self.record_button.configure(state='disabled')
            self.status_label.configure(text="正在识别...")
            
            # 在新线程中处理语音识别
            threading.Thread(target=self._process_audio).start()

    def _process_audio(self):
        try:
            text = self.recognizer.recognize_google(self.audio, language='zh-CN')
            self.result = text
            self.dialog.quit()
        except sr.UnknownValueError:
            self.dialog.after(0, lambda: self.status_label.configure(text="无法识别语音"))
            self.dialog.after(0, lambda: self.record_button.configure(text="开始录音", state='normal'))
        except sr.RequestError as e:
            self.dialog.after(0, lambda: self.status_label.configure(text="语音识别服务错误"))
            self.dialog.after(0, lambda: self.record_button.configure(text="开始录音", state='normal'))
        except Exception as e:
            self.dialog.after(0, lambda: self.status_label.configure(text=f"错误: {str(e)}"))
            self.dialog.after(0, lambda: self.record_button.configure(text="开始录音", state='normal'))

    def update_timer(self):
        if self.is_recording:
            elapsed_time = int(time.time() - self.start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.dialog.after(1000, self.update_timer)

    def cancel_recording(self):
        self.is_recording = False
        self.result = None
        self.dialog.quit()

    def get_result(self):
        self.dialog.mainloop()
        self.dialog.destroy()
        return self.result

class RequirementInputUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("需求输入界面")
        self.root.geometry("1200x800")  # 扩大窗口以适应新的布局
        
        # 设置默认值
        self.default_domain = "新闻管理系统"
        self.default_role = "内容编辑"
        self.default_feature = "文章管理功能，包括创建、编辑、发布和归档文章，支持分类和标签管理"
        self.story_count = tk.StringVar(value="3")  # 默认生成3个用户故事
        
        # 存储生成的用户故事
        self.user_stories = []
        
        # 创建消息队列
        self.message_queue = queue.Queue()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主窗口的网格
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建左右分栏
        self.create_left_panel()
        self.create_right_panel()
        
        # 初始化其他组件
        self.doc_server = None
        self.server_port = None
        
        # 添加API文档存储目录
        self.api_docs_dir = os.path.join(os.path.dirname(__file__), 'api_docs')
        if not os.path.exists(self.api_docs_dir):
            os.makedirs(self.api_docs_dir)
        
        # 创建进度条
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(self.main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_bar = ttk.Progressbar(self.main_frame, mode='indeterminate')
        
        # 启动消息处理
        self.process_message_queue()

    def run(self):
        """启动主程序"""
        self.root.mainloop()

    def create_left_panel(self):
        """创建左侧面板：输入区域和控制按钮"""
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 输入区域
        ttk.Label(left_frame, text="业务领域:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.domain_entry = ttk.Entry(left_frame)
        self.domain_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.domain_entry.insert(0, self.default_domain)
        
        ttk.Label(left_frame, text="用户角色:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.role_entry = ttk.Entry(left_frame)
        self.role_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.role_entry.insert(0, self.default_role)
        
        ttk.Label(left_frame, text="功能特性:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.feature_text = tk.Text(left_frame, height=4)
        self.feature_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.feature_text.insert('1.0', self.default_feature)
        
        # 用户故事数量选择
        count_frame = ttk.Frame(left_frame)
        count_frame.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Label(count_frame, text="生成故事数量:").pack(side=tk.LEFT)
        story_count = ttk.Spinbox(count_frame, from_=1, to=5, width=5, 
                                 textvariable=self.story_count)
        story_count.pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="生成用户故事", 
                  command=self.generate_stories).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空输入", 
                  command=self.clear_inputs).pack(side=tk.LEFT, padx=5)
        
        # 迭代控制
        iteration_frame = ttk.Frame(left_frame)
        iteration_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Label(iteration_frame, text="是否继续迭代：").pack(side=tk.LEFT)
        ttk.Button(iteration_frame, text="继续", 
                  command=self.continue_iteration).pack(side=tk.LEFT, padx=5)
        ttk.Button(iteration_frame, text="完成", 
                  command=self.finish_iteration).pack(side=tk.LEFT, padx=5)

    def create_right_panel(self):
        """创建右侧面板：用户故事列表和详情"""
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 添加分隔器
        self.right_paned = ttk.PanedWindow(right_frame, orient=tk.VERTICAL)
        self.right_paned.pack(fill=tk.BOTH, expand=True)
        
        # 上半部分：用户故事列表和详情
        upper_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(upper_frame)
        
        # 创建用户故事列表框
        list_frame = ttk.Frame(upper_frame)
        list_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(list_frame, text="用户故事列表:").pack(side=tk.LEFT, pady=5)
        ttk.Button(list_frame, text="生成所有API文档", 
                  command=self.generate_all_api_docs).pack(side=tk.RIGHT, padx=5)
        
        self.story_listbox = tk.Listbox(upper_frame, height=5)
        self.story_listbox.pack(fill=tk.X, pady=5)
        self.story_listbox.bind('<<ListboxSelect>>', self.on_story_select)
        
        # 创建用户故事详情区域
        ttk.Label(upper_frame, text="用户故事详情:").pack(anchor=tk.W, pady=5)
        self.story_detail = tk.Text(upper_frame, height=10, wrap=tk.WORD)
        self.story_detail.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 下半部分：API文档验证结果
        lower_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(lower_frame)
        
        # 添加验证结果选项卡
        self.validation_notebook = ttk.Notebook(lower_frame)
        self.validation_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 解析结果选项卡
        parse_frame = ttk.Frame(self.validation_notebook)
        self.validation_notebook.add(parse_frame, text="解析结果")
        self.parse_result_text = tk.Text(parse_frame, height=6, wrap=tk.WORD)
        self.parse_result_text.pack(fill=tk.BOTH, expand=True)
        
        # 验收标准验证选项卡
        criteria_frame = ttk.Frame(self.validation_notebook)
        self.validation_notebook.add(criteria_frame, text="验收标准验证")
        self.criteria_text = tk.Text(criteria_frame, height=6, wrap=tk.WORD)
        self.criteria_text.pack(fill=tk.BOTH, expand=True)
        
        # 技术约束验证选项卡
        constraints_frame = ttk.Frame(self.validation_notebook)
        self.validation_notebook.add(constraints_frame, text="技术约束验证")
        self.constraints_text = tk.Text(constraints_frame, height=6, wrap=tk.WORD)
        self.constraints_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加操作按钮
        button_frame = ttk.Frame(lower_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="解析故事", 
                  command=self.parse_current_story).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Swagger UI", 
                  command=lambda: self.preview_api_doc('swagger')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ReDoc", 
                  command=lambda: self.preview_api_doc('redoc')).pack(side=tk.LEFT, padx=5)

    def update_validation_results(self, validation_results: Dict):
        """更新验证结果显示"""
        # 格式化错误信息
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        # 更新验收标准验证结果
        criteria_text = "验收标准验证结果:\n\n"
        if errors:
            criteria_text += "错误:\n"
            for error in errors:
                if "验收标准" in error:
                    criteria_text += f"- {error}\n"
        if warnings:
            criteria_text += "\n警告:\n"
            for warning in warnings:
                if "验收标准" in warning:
                    criteria_text += f"- {warning}\n"
        self.criteria_text.delete('1.0', tk.END)
        self.criteria_text.insert('1.0', criteria_text)
        
        # 更新技术约束验证结果
        constraints_text = "技术约束验证结果:\n\n"
        if errors:
            constraints_text += "错误:\n"
            for error in errors:
                if "验收标准" not in error:
                    constraints_text += f"- {error}\n"
        if warnings:
            constraints_text += "\n警告:\n"
            for warning in warnings:
                if "验收标准" not in warning:
                    constraints_text += f"- {warning}\n"
        self.constraints_text.delete('1.0', tk.END)
        self.constraints_text.insert('1.0', constraints_text)

    def on_story_select(self, event):
        """当用户选择一个用户故事时触发"""
        selection = self.story_listbox.curselection()
        if selection:
            index = selection[0]
            story = self.user_stories[index]
            self.story_detail.delete('1.0', tk.END)
            self.story_detail.insert('1.0', story['content'])

    def generate_stories(self):
        """生成多个用户故事"""
        domain = self.domain_entry.get().strip()
        role = self.role_entry.get().strip()
        feature = self.feature_text.get('1.0', tk.END).strip()
        count = int(self.story_count.get())
        
        if not all([domain, role, feature]):
            messagebox.showerror("错误", "请填写所有必填字段")
            return
        
        # 禁用生成按钮，显示进度条
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        self.show_progress(True)
        self.progress_var.set("正在生成用户故事...")
        
        # 在新线程中生成故事
        def generate():
            try:
                if not domain or not role or not feature:
                    self.message_queue.put({
                        'action': 'show_error',
                        'error': '业务领域、用户角色和功能特性不能为空'
                    })
                    return
                
                if count < 1 or count > 5:
                    self.message_queue.put({
                        'action': 'show_error',
                        'error': '生成故事数量必须在1到5之间'
                    })
                    return
                
                # Generate multiple user stories based on the provided domain, role, feature, and count.
                # Parameters:
                # - domain: The business domain for the user stories.
                # - role: The user role for which the stories are being generated.
                # - feature: The feature description to be included in the stories.
                # - count: The number of user stories to generate.
                generated_stories = generate_multiple_user_stories(domain, role, feature, count)
                # 将结果放入消息队列
                self.message_queue.put({
                    'action': 'update_stories',
                    'stories': generated_stories
                })
            except Exception as e:
                self.message_queue.put({
                    'action': 'show_error',
                    'error': str(e)
                })
            finally:
                self.message_queue.put({'action': 'finish_generation'})
        
        threading.Thread(target=generate, daemon=True).start()

    def parse_current_story(self):
        """解析当前选中的用户故事"""
        story = self.story_detail.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("错误", "请先选择一个用户故事")
            return
        
        # 禁用按钮，显示进度条
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        self.show_progress(True)
        self.progress_var.set("正在解析用户故事...")
        
        # 获取当前业务领域
        domain = self.domain_entry.get().strip()
        
        # 在新线程中解析故事
        def parse():
            try:
                # 传递业务领域信息
                parsed_data = parse_user_story(story, domain)
                # 生成API规范
                output_path = os.path.join(os.path.dirname(__file__), 'api_spec.json')
                generate_and_save_api_spec(parsed_data, output_path)
                
                # 将结果放入消息队列
                self.message_queue.put({
                    'action': 'update_parse_result',
                    'result': parsed_data
                })
                
                # 提示用户API文档已生成
                self.message_queue.put({
                    'action': 'show_api_doc_ready',
                    'message': 'API文档已生成，可以点击预览按钮查看'
                })
            except Exception as e:
                self.message_queue.put({
                    'action': 'show_error',
                    'error': str(e)
                })
            finally:
                self.message_queue.put({'action': 'finish_parsing'})
        
        threading.Thread(target=parse, daemon=True).start()

    def generate_all_api_docs(self):
        """为所有用户故事生成API文档"""
        if not self.user_stories:
            messagebox.showerror("错误", "请先生成用户故事")
            return
        
        # 获取当前业务领域
        domain = self.domain_entry.get().strip()
        # 禁用按钮，显示进度条
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        self.show_progress(True)
        self.progress_var.set("正在生成所有API文档...")
        
        # 在新线程中生成文档
        def generate():
            try:
                # 预编译正则表达式
                safe_title_pattern = re.compile(r'[^\w\s-]')
                    # Truncate the title to 20 characters to ensure the file name is concise and avoids overly long names
                safe_title = safe_title_pattern.sub('', story['title'])[:20]
                for i, story in enumerate(self.user_stories):
                    # 解析故事
                    parsed_data = parse_user_story(story['content'], domain)
                    
                    # 生成文件名（使用标题的前20个字符作为文件名的一部分）
                    safe_title = safe_title_pattern.sub('', story['title'])[:20]
                    file_name = f"api_spec_{i+1}_{safe_title}.json"
                    output_path = os.path.join(self.api_docs_dir, file_name)
                    
                    # 生成API规范
                    generate_and_save_api_spec(parsed_data, output_path)
                    
                    # 更新进度信息
                    self.message_queue.put({
                        'action': 'update_progress',
                        'message': f"已生成 {i+1}/{len(self.user_stories)} 个API文档"
                    })
                
                # 生成导航页面
                self._generate_navigation_page()
                
                # 提示完成
                self.message_queue.put({
                    'action': 'show_api_doc_ready',
                    'message': '所有API文档已生成，可以在浏览器中查看'
                })
                
            except Exception as e:
                self.message_queue.put({
                    'action': 'show_error',
                    'error': str(e)
                })
            finally:
                self.message_queue.put({'action': 'finish_generation'})
        
        threading.Thread(target=generate, daemon=True).start()

    def _generate_navigation_page(self):
        """生成API文档导航页面"""
        nav_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>用户故事API文档导航</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .story-card { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .story-title { font-size: 18px; margin-bottom: 10px; }
        .doc-links { margin-top: 10px; }
        .doc-link { display: inline-block; margin-right: 10px; padding: 5px 10px;
                   background: #f0f0f0; border-radius: 3px; text-decoration: none;
                   color: #333; }
        .doc-link:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <h1>用户故事API文档导航</h1>
"""
        
        # 添加每个故事的卡片
        for i, story in enumerate(self.user_stories):
            safe_title = re.sub(r'[^\w\s-]', '', story['title'])[:20]
            file_name = f"api_spec_{i+1}_{safe_title}.json"
            
            nav_html += f"""
    <div class="story-card">
        <div class="story-title">故事 {i+1}: {story['title']}</div>
        <div class="doc-links">
            <a href="../api_docs_swagger.html?spec=api_docs/{file_name}" class="doc-link" target="_blank">Swagger UI</a>
            <a href="../api_docs_redoc.html?spec=api_docs/{file_name}" class="doc-link" target="_blank">ReDoc</a>
        </div>
    </div>"""
        
        nav_html += """
</body>
</html>"""
        
        # 保存导航页面
        nav_path = os.path.join(self.api_docs_dir, 'index.html')
        with open(nav_path, 'w', encoding='utf-8') as f:
            f.write(nav_html)

    def process_message_queue(self):
        """处理消息队列中的UI更新请求"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                action = message.get('action')
                
                if action == 'update_stories':
                    generated_stories = message.get('stories')
                    if generated_stories:
                        # 更新故事列表
                        self.user_stories = generated_stories
                        self.story_listbox.delete(0, tk.END)
                        for story in generated_stories:
                            self.story_listbox.insert(tk.END, story['title'])
                        
                        # 选择第一个故事并显示详情
                        self.story_listbox.selection_set(0)
                        self.story_detail.delete('1.0', tk.END)
                        self.story_detail.insert('1.0', generated_stories[0]['content'])
                        
                        # 获取解析结果
                        result = message.get('result', {})
                        formatted_result = f"目标: {result.get('goal', '')}\n"
                        formatted_result += f"价值: {result.get('value', '')}\n\n"
                        formatted_result += "验收标准:\n"
                        
                        # 添加验收标准
                        for i, criterion in enumerate(result.get('criteria', []), 1):
                            formatted_result += f"{i}. {criterion}\n"
                        
                        # 更新解析结果显示
                        self.parse_result_text.delete('1.0', tk.END)
                        self.parse_result_text.insert('1.0', formatted_result)
                        
                        # 更新验证结果
                        validation_results = message.get('validation_results', {})
                        self.update_validation_results(validation_results)
                    else:
                        messagebox.showerror("错误", "解析用户故事失败")
                
                elif action == 'update_progress':
                    progress_message = message.get('message')
                    self.progress_var.set(progress_message)
                
                elif action == 'show_error':
                    error_message = message.get('error')
                    messagebox.showerror("错误", f"生成用户故事时发生错误: {error_message}")
                
                elif action == 'show_api_doc_ready':
                    messagebox.showinfo("成功", message.get('message'))
                
                elif action in ['finish_generation', 'finish_parsing']:
                    self.show_progress(False)
                    # 重新启用所有按钮
                    for widget in self.main_frame.winfo_children():
                        if isinstance(widget, ttk.Button):
                            widget.configure(state='normal')
                
        except queue.Empty:
            pass
        finally:
            # 每100ms检查一次消息队列
            self.root.after(100, self.process_message_queue)

    def show_progress(self, show=True):
        """显示或隐藏进度条"""
        if show:
            self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            self.progress_var.set("")

    def preview_api_doc(self, doc_type='swagger'):
        """预览API文档"""
        if not self.server_port:
            self.server_port = get_free_port()
            self.doc_server = start_doc_server(self.server_port)
        
        # 直接打开导航页面
        url = f"http://localhost:{self.server_port}/api_docs/index.html"
        webbrowser.open(url)

    def clear_inputs(self):
        """清空所有输入框并恢复默认值"""
        self.domain_entry.delete(0, tk.END)
        self.domain_entry.insert(0, self.default_domain)
        
        self.role_entry.delete(0, tk.END)
        self.role_entry.insert(0, self.default_role)
        
        self.feature_text.delete('1.0', tk.END)
        self.feature_text.insert('1.0', self.default_feature)
        
        self.story_listbox.delete(0, tk.END)
        self.story_detail.delete('1.0', tk.END)
        self.parse_result_text.delete('1.0', tk.END)
        
        self.story_count.set("3")  # 重置故事数量
        
        self.progress_var.set("")  # 重置进度变量
        
        self.user_stories = []  # 清空故事列表

    def continue_iteration(self):
        """继续新的迭代"""
        # 生成统计信息
        stats = self._generate_iteration_stats()
        
        # 显示统计对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("迭代完成")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # 添加统计信息
        stats_frame = ttk.Frame(dialog, padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(stats_frame, text="当前迭代统计", font=('Arial', 12, 'bold')).pack(pady=(0,10))
        
        for key, value in stats.items():
            ttk.Label(stats_frame, text=f"{key}: {value}").pack(pady=2)
        
        # 添加按钮框架
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def start_new_iteration():
            self.clear_inputs()
            dialog.destroy()
            messagebox.showinfo("新迭代", "请开始输入新的迭代需求")
            
        def end_all():
            dialog.destroy()
            self.finish_iteration()
        
        ttk.Button(button_frame, text="开始新迭代", command=start_new_iteration).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="结束所有迭代", command=end_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="返回继续当前迭代", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _generate_iteration_stats(self):
        """生成当前迭代的统计信息"""
        stats = {
            "用户故事总数": len(self.user_stories),
            "完成的API文档数": len([f for f in os.listdir(self.api_docs_dir) 
                               if f.startswith('api_spec_') and f.endswith('.json')]),
            "领域": self.domain_entry.get(),
            "主要角色": self.role_entry.get()
        }
        return stats

    def finish_iteration(self):
        """结束所有迭代并生成总结报告"""
        if not self.user_stories:
            messagebox.showinfo("提示", "没有可以总结的用户故事")
            return

        # 生成总结报告
        report = self._generate_summary_report()
        
        # 创建总结对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("项目总结报告")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # 创建报告显示区域
        report_frame = ttk.Frame(dialog, padding="20")
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加报告标题
        ttk.Label(report_frame, text="项目总结报告", 
                 font=('Arial', 14, 'bold')).pack(pady=(0,10))
        
        # 创建报告文本框
        report_text = tk.Text(report_frame, wrap=tk.WORD, height=15)
        report_text.pack(fill=tk.BOTH, expand=True)
        report_text.insert('1.0', report)
        report_text.configure(state='disabled')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, 
                                command=report_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        # 添加按钮
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def save_report():
            file_path = os.path.join(os.path.dirname(__file__), 'project_summary.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            messagebox.showinfo("成功", f"报告已保存至: {file_path}")
            
        def close_app():
            dialog.destroy()
            self.root.quit()
        
        ttk.Button(button_frame, text="保存报告", 
                  command=save_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭程序", 
                  command=close_app).pack(side=tk.LEFT, padx=5)

    def _generate_summary_report(self):
        """生成项目总结报告"""
        report = f"""项目概况
-----------------
业务领域：{self.domain_entry.get()}
主要用户角色：{self.role_entry.get()}
功能特性：{self.feature_text.get('1.0', tk.END).strip()}

用户故事统计
-----------------
总数：{len(self.user_stories)}
已生成API文档数：{len([f for f in os.listdir(self.api_docs_dir) 
                    if f.startswith('api_spec_') and f.endswith('.json')])}

用户故事列表
-----------------
"""
        for i, story in enumerate(self.user_stories, 1):
            report += f"\n{i}. {story['title']}\n"
            report += f"   内容：{story['content']}\n"
            
        report += "\n技术实现总结\n"
        report += "-----------------\n"
        report += "1. API端点设计完整性：包含了必要的CRUD操作\n"
        report += "2. 数据模型标准化：符合OpenAPI 3.0规范\n"
        report += "3. 安全性考虑：包含了基本的错误处理和参数验证\n"
        report += "4. 可扩展性：支持分页、排序和搜索功能\n"
        
        return report

if __name__ == "__main__":
    app = RequirementInputUI()
    app.run()