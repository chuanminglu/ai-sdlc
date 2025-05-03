import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import datetime
import threading
import time
import os
import requests
from pathlib import Path
import configparser
import re

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
        
        # 加载配置文件
        self.config = self._load_config()
        
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
    
    def _load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        else:
            # 如果配置文件不存在，使用默认配置
            config['deepseek'] = {
                'api_key': '',
                'api_base': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat'
            }
            
        return config
    
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
        """生成约束清单的线程"""
        try:
            # 这里调用约束清单生成函数
            constraints = self._generate_constraints_data()
            self.constraints_list = constraints
            
            # 显示生成的约束清单
            markdown_content = self._format_constraints_markdown(constraints)
            
            # 在UI线程中更新文本框
            self.dialog.after(0, lambda: self._update_constraints_text(markdown_content))
            
        except Exception as e:
            # 在UI线程中显示错误
            self.dialog.after(0, lambda: messagebox.showerror("错误", f"生成约束清单时发生错误: {str(e)}"))
        finally:
            # 在UI线程中更新UI状态
            self.dialog.after(0, lambda: self._finish_generation())
    
    def _update_constraints_text(self, content):
        """更新约束清单文本框"""
        self.constraints_text.delete('1.0', tk.END)
        self.constraints_text.insert('1.0', content)
    
    def _finish_generation(self):
        """完成生成约束清单"""
        self.processing = False
        self.generate_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.NORMAL)
        self.show_progress(False, "约束清单生成完成")
    
    def _generate_constraints_data(self):
        """生成约束清单数据
        
        Returns:
            list: 约束清单数据列表
        """
        # 根据用户故事解析结果准备提示信息
        domain = self.parsed_data.get('domain', '')
        role = self.parsed_data.get('role', '')
        goal = self.parsed_data.get('goal', '')
        value = self.parsed_data.get('value', '')
        criteria = self.parsed_data.get('criteria', [])
        
        criteria_str = "\n".join([f"- {criterion}" for criterion in criteria])
        
        # 构建提示词
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
        
        try:
            # 调用DeepSeek API获取生成内容
            response = self._call_deepseek_api(prompt)
            
            # 提取JSON部分
            json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                constraints = json.loads(json_str)
            else:
                # 如果没有找到JSON格式，尝试解析整个响应
                constraints = json.loads(response)
                
            if not constraints:
                raise ValueError("生成的约束清单为空")
                
            return constraints
            
        except Exception as e:
            # 如果API调用失败或解析失败，使用默认约束清单
            print(f"警告: 调用大模型API失败，将使用默认约束清单: {str(e)}")
            return self._get_default_constraints(domain, role, goal)
    
    def _get_default_constraints(self, domain, role, goal):
        """获取默认约束清单（当API调用失败时使用）
        
        Args:
            domain: 用户故事领域
            role: 用户角色
            goal: 用户目标
            
        Returns:
            list: 默认约束清单
        """
        constraints = []
        
        # 性能约束
        constraints.append({
            'type': '性能',
            'metric': 'P99延迟',
            'value': '500毫秒',
            'description': '系统需要确保99%的请求响应时间不超过500毫秒'
        })
        
        constraints.append({
            'type': '性能',
            'metric': '系统吞吐量',
            'value': '1000 TPS',
            'description': f'系统需要支持每秒至少1000次的事务处理能力，以满足{role}的使用需求'
        })
        
        # 安全约束
        constraints.append({
            'type': '安全性',
            'metric': '身份认证',
            'value': 'OAuth 2.0',
            'description': f'应使用OAuth 2.0进行{role}身份验证，确保访问安全'
        })
        
        # 可靠性约束
        constraints.append({
            'type': '可靠性',
            'metric': '系统可用性',
            'value': '99.9%',
            'description': '系统年度可用性须达到99.9%（不超过8.76小时/年的停机时间）'
        })
        
        # 可扩展性约束
        constraints.append({
            'type': '可扩展性',
            'metric': '用户基数',
            'value': '支持100万用户',
            'description': f'系统架构需要支持最多100万{role}同时在线'
        })
        
        return constraints
    
    def _format_constraints_markdown(self, constraints):
        """格式化约束清单为Markdown格式
        
        Args:
            constraints: 约束清单数据
            
        Returns:
            str: Markdown格式的约束清单
        """
        domain = self.parsed_data.get('domain', '未指定领域')
        role = self.parsed_data.get('role', '未指定角色')
        goal = self.parsed_data.get('goal', '未指定目标')
        
        now = datetime.datetime.now().strftime("%Y年%m月%d日")
        
        markdown = f"# {domain} - 约束检查清单\n\n"
        markdown += f"**生成日期:** {now}\n\n"
        markdown += f"**用户角色:** {role}\n\n"
        markdown += f"**功能目标:** {goal}\n\n"
        markdown += "## 约束清单\n\n"
        
        # 按类型分组
        constraints_by_type = {}
        for constraint in constraints:
            constraint_type = constraint.get('type', '其他')
            if constraint_type not in constraints_by_type:
                constraints_by_type[constraint_type] = []
            constraints_by_type[constraint_type].append(constraint)
        
        # 按类型生成markdown表格
        for constraint_type, type_constraints in constraints_by_type.items():
            markdown += f"### {constraint_type}约束\n\n"
            markdown += "| 度量指标 | 要求值 | 描述 |\n"
            markdown += "|---------|--------|------|\n"
            
            for constraint in type_constraints:
                metric = constraint.get('metric', '')
                value = constraint.get('value', '')
                description = constraint.get('description', '')
                markdown += f"| {metric} | {value} | {description} |\n"
            
            markdown += "\n"
            
        return markdown
    
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
    
    def _call_deepseek_api(self, prompt):
        """调用DeepSeek API获取生成内容
        
        Args:
            prompt (str): 提示词
            
        Returns:
            str: 大模型返回的内容
        """
        try:
            # 获取API配置
            api_key = self.config.get('deepseek', 'api_key', fallback='')
            api_base = self.config.get('deepseek', 'api_base', fallback='https://api.deepseek.com/v1')
            model = self.config.get('deepseek', 'model', fallback='deepseek-chat')
            
            # 检查API密钥
            if not api_key:
                raise ValueError("DeepSeek API密钥未配置。请在config.ini文件中设置deepseek节下的api_key。")
            
            # 构建API请求
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': '你是一位软件工程质量专家，擅长分析用户故事并生成系统约束检查清单。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7
            }
            
            # 发送API请求
            url = f"{api_base}/chat/completions"
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            # 解析返回结果
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return content
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"解析API响应失败: {str(e)}")
        except Exception as e:
            raise Exception(f"调用DeepSeek API时发生错误: {str(e)}")
    
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