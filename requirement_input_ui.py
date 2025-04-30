import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from parseuserstory import generate_user_story, parse_user_story
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
        with sr.Microphone() as source:
            try:
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
        self.root.geometry("800x600")
        
        # 创建消息队列
        self.message_queue = queue.Queue()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        self.progress_label.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_bar = ttk.Progressbar(self.main_frame, mode='indeterminate')
        
        # 启动消息处理
        self.process_message_queue()
        
    def create_input_fields(self):
        # 业务领域输入
        ttk.Label(self.main_frame, text="业务领域:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.domain_entry = ttk.Entry(self.main_frame)
        self.domain_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # 用户角色输入
        ttk.Label(self.main_frame, text="用户角色:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.role_entry = ttk.Entry(self.main_frame)
        self.role_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # 功能特性输入
        ttk.Label(self.main_frame, text="功能特性:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.feature_text = tk.Text(self.main_frame, height=4)
        self.feature_text.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
    
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
    
    def create_result_area(self):
        # 结果显示区域
        ttk.Label(self.main_frame, text="生成的用户故事:").grid(row=4, column=0, 
                                                          sticky=tk.W, pady=5)
        # 创建一个Frame来容纳文本框和滚动条
        result_frame = ttk.Frame(self.main_frame)
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 创建文本框并关联滚动条
        self.result_text = tk.Text(result_frame, height=15, wrap=tk.WORD,
                                 yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置滚动条的命令
        scrollbar.config(command=self.result_text.yview)
        
        # 配置文本框样式
        self.result_text.config(font=('Arial', 10))
    
    def create_parse_result_area(self):
        # 解析结果显示区域
        ttk.Label(self.main_frame, text="解析结果:").grid(row=8, column=0, 
                                                    sticky=tk.W, pady=5)
        
        # 创建一个Frame来容纳文本框和滚动条
        parse_frame = ttk.Frame(self.main_frame)
        parse_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        parse_frame.columnconfigure(0, weight=1)
        parse_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(parse_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 创建文本框并关联滚动条
        self.parse_result_text = tk.Text(parse_frame, height=8, wrap=tk.WORD,
                                       yscrollcommand=scrollbar.set)
        self.parse_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
                        # 格式化解析结果
                        formatted_result = (
                            f"角色: {result['role']}\n"
                            f"目标: {result['goal']}\n"
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
            self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
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
            messagebox.showerror("错误", "请先生成或输入用户故事")
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
    
    def clear_inputs(self):
        """清空所有输入框"""
        self.domain_entry.delete(0, tk.END)
        self.role_entry.delete(0, tk.END)
        self.feature_text.delete('1.0', tk.END)
        self.result_text.delete('1.0', tk.END)
        self.parse_result_text.delete('1.0', tk.END)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RequirementInputUI()
    app.run()