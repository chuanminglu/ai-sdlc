import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from parseuserstory import generate_user_story, parse_user_story
from splituserstory import SplitStoryDialog  # 导入拆分用户故事对话框
from createconstraints import ConstraintsDialog  # 导入约束检查清单对话框
import re
import threading
import time
import queue
import warnings
import os
import logging

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
        self.audio = None
        
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
        try:
            self.is_recording = True
            self.record_button.configure(text="停止录音")
            self.status_label.configure(text="正在录音...")
            self.start_time = time.time()
            
            # 开始计时器
            self.update_timer()
            
            # 在新线程中开始录音
            self.record_thread = threading.Thread(target=self._record_audio)
            self.record_thread.start()
        except Exception as e:
            self.status_label.configure(text=f"录音启动错误: {str(e)}")
            self.is_recording = False
            self.record_button.configure(text="开始录音")

    def _record_audio(self):
        try:
            self.recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.audio = self.recognizer.listen(source, timeout=30)
        except Exception as e:
            self.dialog.after(0, lambda: self.status_label.configure(text=f"录音错误: {str(e)}"))

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
            # 检查是否有有效的音频数据
            if not hasattr(self, 'audio') or self.audio is None:
                self.dialog.after(0, lambda: self.status_label.configure(text="没有录制到音频"))
                self.dialog.after(0, lambda: self.record_button.configure(text="开始录音", state='normal'))
                return
                
            # 初始化识别器（如果还没有）
            if not hasattr(self, 'recognizer'):
                self.recognizer = sr.Recognizer()            # 使用 Google Web Speech API 进行语音识别
            try:
                # 使用 getattr 来动态获取方法，避免静态类型检查错误
                recognize_method = getattr(self.recognizer, 'recognize_google', None)
                if recognize_method:
                    text = recognize_method(self.audio, language='zh-CN')
                    self.result = text
                    self.dialog.quit()
                else:
                    raise AttributeError("语音识别方法不可用")
            except AttributeError:
                # 如果 recognize_google 方法不存在，尝试其他方法
                self.dialog.after(0, lambda: self.status_label.configure(text="语音识别功能不可用"))
                self.dialog.after(0, lambda: self.record_button.configure(text="开始录音", state='normal'))
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
        if self.is_recording and hasattr(self, 'start_time'):
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
    # 常量定义
    ERROR_NO_STORY = "请先生成或输入用户故事"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("需求输入界面")
        self.root.geometry("800x600")
        
        # 设置默认值
        self.default_domain = "电商平台"
        self.default_role = "会员"
        self.default_feature = "通过商品评论排序筛选商品，要求支持按照评分(1-5星)降序排列，允许选择近3个月的评论，默认显示综合排序(评分*70%+新近度*30%)"
        
        # 创建消息队列
        self.message_queue = queue.Queue()
          # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
          # 配置主窗口的网格
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建输入区域
        self.create_input_fields()
        
        # 创建按钮区域
        self.create_buttons()
        
        # 创建结果显示区域
        self.create_result_area()
        
        # 创建解析结果显示区域
        self.create_parse_result_area()
        
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
          # 创建进度条
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(self.main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=6, column=0, columnspan=3, sticky="ew", pady=5)
        
        self.progress_bar = ttk.Progressbar(self.main_frame, mode='indeterminate')
        
        # 启动消息处理
        self.process_message_queue()
        
    def create_input_fields(self):        # 业务领域输入
        ttk.Label(self.main_frame, text="业务领域:").grid(row=0, column=0, sticky="w", pady=5)
        self.domain_entry = ttk.Entry(self.main_frame)
        self.domain_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
        self.domain_entry.insert(0, self.default_domain)  # 插入默认值
        
        # 用户角色输入
        ttk.Label(self.main_frame, text="用户角色:").grid(row=1, column=0, sticky="w", pady=5)
        self.role_entry = ttk.Entry(self.main_frame)
        self.role_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
        self.role_entry.insert(0, self.default_role)  # 插入默认值
        
        # 功能特性输入
        ttk.Label(self.main_frame, text="功能特性:").grid(row=2, column=0, sticky="w", pady=5)
        self.feature_text = tk.Text(self.main_frame, height=4)
        self.feature_text.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
        self.feature_text.insert('1.0', self.default_feature)  # 插入默认值
    
    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 语音输入按钮
        self.voice_buttons = []
        voice_texts = ["语音输入领域", "语音输入角色", "语音输入功能"]
        for i, text in enumerate(voice_texts):
            btn = ttk.Button(button_frame, text=text, 
                           command=lambda x=i: self.start_voice_input(x))
            btn.grid(row=0, column=i, padx=5)
            self.voice_buttons.append(btn)
        
        # 生成用户故事按钮
        ttk.Button(button_frame, text="生成用户故事", 
                  command=self.generate_story).grid(row=0, column=3, padx=5)
        
        # 解析用户故事按钮
        ttk.Button(button_frame, text="解析用户故事", 
                  command=self.parse_story).grid(row=0, column=4, padx=5)
        
        # 清空输入按钮
        ttk.Button(button_frame, text="清空输入", 
                  command=self.clear_inputs).grid(row=0, column=5, padx=5)
    
    def create_result_area(self):        # 结果显示区域标题行
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        # 左侧标题
        ttk.Label(title_frame, text="生成的用户故事:").pack(side=tk.LEFT)
        
        # 右侧按钮
        button_container = ttk.Frame(title_frame)
        button_container.pack(side=tk.RIGHT)
        
        # API规范按钮
        self.api_button = ttk.Button(button_container, text="创建API规范", 
                                    command=self.create_api_spec)
        self.api_button.pack(side=tk.RIGHT, padx=5)
        
        # 拆分按钮
        self.split_button = ttk.Button(button_container, text="拆分用户故事", 
                                      command=self.split_story)
        self.split_button.pack(side=tk.RIGHT, padx=5)
        
        # 约束检查清单按钮
        self.constraints_button = ttk.Button(button_container, text="生成约束检查清单", 
                                           command=self.create_constraints)
        self.constraints_button.pack(side=tk.RIGHT, padx=5)
          # 创建一个Frame来容纳文本框和滚动条
        result_frame = ttk.Frame(self.main_frame)
        result_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 创建文本框并关联滚动条
        self.result_text = tk.Text(result_frame, height=15, wrap=tk.WORD,
                                 yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        
        # 设置滚动条的命令
        scrollbar.config(command=self.result_text.yview)
        
        # 配置文本框样式
        self.result_text.config(font=('Arial', 10))
    
    def create_parse_result_area(self):        # 解析结果显示区域
        ttk.Label(self.main_frame, text="解析结果:").grid(row=8, column=0, 
                                                    sticky="w", pady=5)
        
        # 创建一个Frame来容纳文本框和滚动条
        parse_frame = ttk.Frame(self.main_frame)
        parse_frame.grid(row=9, column=0, columnspan=3, sticky="nsew")
        parse_frame.columnconfigure(0, weight=1)
        parse_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(parse_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 创建文本框并关联滚动条
        self.parse_result_text = tk.Text(parse_frame, height=8, wrap=tk.WORD,
                                       yscrollcommand=scrollbar.set)
        self.parse_result_text.grid(row=0, column=0, sticky="nsew")
        
        # 设置滚动条的命令
        scrollbar.config(command=self.parse_result_text.yview)
        
        # 配置文本框样式
        self.parse_result_text.config(font=('Arial', 10))
    
    def clean_output_text(self, text):
        """清理输出文本，去除特殊符号"""
        # 去除星号
        text = re.sub(r'\*+', '', text)
        # 去除多余的空行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # 去除行首行尾的空白字符
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text
    
    def start_voice_input(self, field_index):
        """开始语音输入"""
        dialog = VoiceRecorderDialog(self.root)
        result = dialog.get_result()
        
        if result:
            # 根据field_index确定要更新哪个输入框
            if field_index == 0:
                self.domain_entry.delete(0, tk.END)
                self.domain_entry.insert(0, result)
            elif field_index == 1:
                self.role_entry.delete(0, tk.END)
                self.role_entry.insert(0, result)
            else:
                self.feature_text.delete('1.0', tk.END)
                self.feature_text.insert('1.0', result)
    
    def process_message_queue(self):
        """处理消息队列中的UI更新请求"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                action = message.get('action')
                
                if action == 'update_story':
                    story = message.get('story')
                    if story:
                        cleaned_story = self.clean_output_text(story)
                        self.result_text.delete('1.0', tk.END)
                        self.result_text.insert('1.0', cleaned_story)
                        self.result_text.see('1.0')
                    else:
                        messagebox.showerror("错误", "生成用户故事失败")
                
                elif action == 'update_parse_result':
                    result = message.get('result')
                    if result:
                        # 格式化解析结果，添加价值部分
                        formatted_result = (
                            f"角色: {result['role']}\n"
                            f"目标: {result['goal']}\n"
                            f"价值: {result.get('value', '')}\n"  # 添加价值显示，使用get方法防止键不存在
                            f"\n验收标准:\n"
                        )
                        for i, criterion in enumerate(result['criteria'], 1):
                            formatted_result += f"{i}. {criterion}\n"
                        
                        self.parse_result_text.delete('1.0', tk.END)
                        self.parse_result_text.insert('1.0', formatted_result)
                        self.parse_result_text.see('1.0')
                    else:
                        messagebox.showerror("错误", "解析用户故事失败")
                
                elif action == 'show_error':
                    error_message = message.get('error')
                    messagebox.showerror("错误", f"生成用户故事时发生错误: {error_message}")
                
                elif action == 'finish_generation':
                    self.show_progress(False)
                    # 重新启用所有按钮
                    for widget in self.main_frame.winfo_children():
                        if isinstance(widget, ttk.Button):
                            widget.configure(state='normal')
                
                elif action == 'finish_parsing':
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
            self.progress_bar.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5)
            self.progress_bar.start(10)
            self.progress_var.set("正在生成用户故事...")
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            self.progress_var.set("")
    
    def generate_story(self):
        """异步生成用户故事"""
        domain = self.domain_entry.get().strip()
        role = self.role_entry.get().strip()
        feature = self.feature_text.get('1.0', tk.END).strip()
        
        if not all([domain, role, feature]):
            messagebox.showerror("错误", "请填写所有必填字段")
            return
        
        # 禁用生成按钮，显示进度条
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        self.show_progress(True)
          # 在新线程中生成故事
        def generate():
            try:
                story = generate_user_story(domain, role, feature)
                # 将结果放入消息队列
                self.message_queue.put({'action': 'update_story', 'story': story})
            except Exception as e:
                # 将错误放入消息队列
                self.message_queue.put({'action': 'show_error', 'error': str(e)})
            finally:
                # 通知UI更新完成
                self.message_queue.put({'action': 'finish_generation'})
        
        threading.Thread(target=generate, daemon=True).start()
    
    def parse_story(self):
        """解析当前显示的用户故事"""
        story = self.result_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("错误", self.ERROR_NO_STORY)
            return
        
        # 禁用按钮，显示进度条
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        self.show_progress(True)
        self.progress_var.set("正在解析用户故事...")
        
        # 在新线程中解析故事
        def parse():
            try:
                parsed_data = parse_user_story(story)
                # 将结果放入消息队列
                self.message_queue.put({
                    'action': 'update_parse_result',
                    'result': parsed_data
                })
            except Exception as e:
                self.message_queue.put({
                    'action': 'show_error',
                    'error': str(e)
                })
            finally:
                self.message_queue.put({'action': 'finish_parsing'})
        
        threading.Thread(target=parse, daemon=True).start()
    
    def split_story(self):
        """拆分当前显示的用户故事"""
        story = self.result_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("错误", self.ERROR_NO_STORY)
            return
        
        # 获取当前领域和角色
        domain = self.domain_entry.get().strip()
        role = self.role_entry.get().strip()
        
        # 显示拆分对话框
        dialog = SplitStoryDialog(self.root, story)
        result = dialog.get_result()
        
        if not result:
            return  # 用户取消了操作
        
        # 禁用按钮，显示进度条
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        self.show_progress(True)
        self.progress_var.set("正在拆分用户故事...")
        
        # 在新线程中执行拆分
        def split():
            try:
                # 导入拆分功能
                from parseuserstory import split_user_story
                
                # 获取用户选择的拆分数量
                count = result['count']
                original_story = result['original_story']
                
                # 调用拆分函数
                stories = split_user_story(original_story, domain, role, count)
                
                if stories and len(stories) > 0:
                    # 创建拆分结果对话框
                    self.show_split_results(stories)
                else:
                    self.message_queue.put({
                        'action': 'show_error',
                        'error': "无法拆分用户故事，请检查故事内容或重试"
                    })
            except Exception as e:
                self.message_queue.put({
                    'action': 'show_error',
                    'error': str(e)
                })
            finally:
                self.message_queue.put({'action': 'finish_generation'})
        
        threading.Thread(target=split, daemon=True).start()
    
    def show_split_results(self, stories):
        """显示拆分后的用户故事"""
        # 创建新窗口
        result_window = tk.Toplevel(self.root)
        result_window.title("用户故事拆分结果")
        result_window.geometry("800x500")
        
        # 使窗口在主窗口之上
        result_window.transient(self.root)
        
        # 居中窗口
        result_window.update_idletasks()
        width = result_window.winfo_width()
        height = result_window.winfo_height()
        x = (result_window.winfo_screenwidth() // 2) - (width // 2)
        y = (result_window.winfo_screenheight() // 2) - (height // 2)
        result_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # 创建主框架
        main_frame = ttk.Frame(result_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="用户故事已拆分为以下子故事:", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建笔记本控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 为每个拆分的故事创建一个选项卡
        for i, story in enumerate(stories, 1):
            # 创建选项卡
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"故事 {i}")
            
            # 创建故事文本框
            story_text = tk.Text(tab, wrap=tk.WORD)
            story_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 添加故事内容
            story_text.insert('1.0', story)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=story_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            story_text.configure(yscrollcommand=scrollbar.set)
        
        # 底部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 用于选择当前选项卡中的故事
        def select_current_story():
            current_tab = notebook.index(notebook.select())
            if current_tab < len(stories):
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', stories[current_tab])
                # 自动解析新选择的故事
                self.parse_story()
                result_window.destroy()
        
        ttk.Button(button_frame, text="选择当前故事", 
                  command=select_current_story).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=result_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def clear_inputs(self):
        """清空所有输入框"""
        self.domain_entry.delete(0, tk.END)
        self.role_entry.delete(0, tk.END)
        self.feature_text.delete('1.0', tk.END)
        self.result_text.delete('1.0', tk.END)
        self.parse_result_text.delete('1.0', tk.END)
    
    def create_api_spec(self):
        """创建API规范"""
        # 首先确保有解析结果
        # 如果没有解析结果，先解析当前故事
        story = self.result_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("错误", self.ERROR_NO_STORY)
            return
        
        try:
            # 获取已解析的数据或进行解析
            parsed_data = None
            parsed_text = self.parse_result_text.get('1.0', tk.END).strip()
            
            # 检查是否已有解析结果
            if parsed_text:
                # 尝试从显示的解析文本中重建解析数据
                lines = parsed_text.split('\n')
                parsed_data = {}
                
                for line in lines:
                    if line.startswith("角色:"):
                        parsed_data['role'] = line.replace("角色:", "").strip()
                    elif line.startswith("目标:"):
                        parsed_data['goal'] = line.replace("目标:", "").strip()
                    elif line.startswith("价值:"):
                        parsed_data['value'] = line.replace("价值:", "").strip()
                
                # 提取验收标准
                criteria = []
                in_criteria_section = False
                for line in lines:
                    if "验收标准:" in line:
                        in_criteria_section = True
                        continue
                    if in_criteria_section and line.strip() and line[0].isdigit():
                        # 移除数字和点，获取标准内容
                        criterion = line.split(".", 1)[-1].strip() if "." in line else line.strip()
                        criteria.append(criterion)
                
                parsed_data['criteria'] = criteria
                
                # 添加领域信息
                parsed_data['domain'] = self.domain_entry.get().strip()
            else:
                # 如果没有解析结果，现在解析
                parsed_data = parse_user_story(story)
                
                # 添加领域信息
                parsed_data['domain'] = self.domain_entry.get().strip()
                
                # 显示解析结果
                self.message_queue.put({
                    'action': 'update_parse_result',
                    'result': parsed_data
                })
              # 导入并显示CreateAPIDialog
            from createAPIstd import CreateAPIDialog
            dialog = CreateAPIDialog(self.root, parsed_data)
            output_path = dialog.run()
            
            # 如果有输出路径，表示生成了规范
            if output_path:
                self.progress_var.set("API规范已生成")
                
        except Exception as e:
            messagebox.showerror("错误", f"创建API规范时发生错误: {str(e)}")
            self.progress_var.set("")
    
    def create_constraints(self):
        """生成约束检查清单"""
        # 首先确保有解析结果
        story = self.result_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("错误", self.ERROR_NO_STORY)
            return
        
        try:
            # 获取已解析的数据或进行解析
            parsed_data = None
            parsed_text = self.parse_result_text.get('1.0', tk.END).strip()
            
            # 检查是否已有解析结果
            if parsed_text:
                # 尝试从显示的解析文本中重建解析数据
                lines = parsed_text.split('\n')
                parsed_data = {}
                
                for line in lines:
                    if line.startswith("角色:"):
                        parsed_data['role'] = line.replace("角色:", "").strip()
                    elif line.startswith("目标:"):
                        parsed_data['goal'] = line.replace("目标:", "").strip()
                    elif line.startswith("价值:"):
                        parsed_data['value'] = line.replace("价值:", "").strip()
                
                # 提取验收标准
                criteria = []
                in_criteria_section = False
                for line in lines:
                    if "验收标准:" in line:
                        in_criteria_section = True
                        continue
                    if in_criteria_section and line.strip() and line[0].isdigit():
                        # 移除数字和点，获取标准内容
                        criterion = line.split(".", 1)[-1].strip() if "." in line else line.strip()
                        criteria.append(criterion)
                
                parsed_data['criteria'] = criteria
                
                # 添加领域信息
                parsed_data['domain'] = self.domain_entry.get().strip()
            else:
                # 如果没有解析结果，现在解析
                parsed_data = parse_user_story(story)
                
                # 添加领域信息
                parsed_data['domain'] = self.domain_entry.get().strip()
                
                # 显示解析结果
                self.message_queue.put({
                    'action': 'update_parse_result',
                    'result': parsed_data
                })
            
            # 显示约束检查清单对话框
            dialog = ConstraintsDialog(self.root, parsed_data)
            dialog.show()
                
        except Exception as e:
            messagebox.showerror("错误", f"创建约束检查清单时发生错误: {str(e)}")
            self.progress_var.set("")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RequirementInputUI()
    app.run()