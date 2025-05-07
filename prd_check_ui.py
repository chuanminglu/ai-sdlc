import tkinter as tk
from tkinter import ttk, messagebox
import threading
from sample_prd import generate_sample_prd
from prd_checker import PRDChecker

class PRDCheckUI:
    """PRD文档检查器界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PRD文档检查器")
        self.root.geometry("1200x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置grid权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # 初始化检查器
        self.checker = PRDChecker()
        
        # 创建界面组件
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        # 模板选择区域
        template_frame = ttk.Frame(self.main_frame)
        template_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(template_frame, text="选择示例PRD模板：").pack(side=tk.LEFT)
        self.template_var = tk.StringVar(value="missing_background")
        templates = {
            'missing_background': '缺少业务背景的PRD',
            'missing_value': '缺少价值描述的PRD',
            'missing_goal': '缺少明确目标的PRD',
            'missing_flow': '缺少业务流程的PRD',
            'missing_criteria': '缺少验收标准的PRD',
            'incomplete': '多项缺失的PRD'
        }
        template_menu = ttk.OptionMenu(
            template_frame, 
            self.template_var,
            self.template_var.get(),
            *templates.keys(),
            command=self.load_template
        )
        template_menu.pack(side=tk.LEFT, padx=5)
        
        # PRD内容编辑区
        ttk.Label(self.main_frame, text="PRD内容:").grid(row=1, column=0, sticky=tk.W)
        
        prd_frame = ttk.Frame(self.main_frame)
        prd_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        prd_frame.columnconfigure(0, weight=1)
        prd_frame.rowconfigure(0, weight=1)
        
        # 创建文本框和滚动条
        self.prd_text = tk.Text(prd_frame, wrap=tk.WORD, width=80, height=20)
        self.prd_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        prd_scrollbar = ttk.Scrollbar(prd_frame, command=self.prd_text.yview)
        prd_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.prd_text.configure(yscrollcommand=prd_scrollbar.set)
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.check_button = ttk.Button(button_frame, text="评审文档", command=self.check_prd)
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        # 评审结果区域
        ttk.Label(self.main_frame, text="评审结果:").grid(row=3, column=0, sticky=tk.W)
        
        result_frame = ttk.Frame(self.main_frame)
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建结果文本框和滚动条
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, width=80, height=20)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        result_scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        # 初始化加载示例PRD
        self.load_template()
        
    def load_template(self, *args):
        """加载PRD模板"""
        template_type = self.template_var.get()
        prd_content = generate_sample_prd(template_type)
        self.prd_text.delete('1.0', tk.END)
        self.prd_text.insert('1.0', prd_content)
        
    def check_prd(self):
        """检查PRD文档"""
        # 禁用检查按钮
        self.check_button.configure(state=tk.DISABLED)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', '正在评审文档，请稍候...\n')
        
        # 在新线程中运行检查
        threading.Thread(target=self._check_prd_thread, daemon=True).start()
        
    def _check_prd_thread(self):
        """在新线程中运行PRD检查"""
        try:
            prd_content = self.prd_text.get('1.0', tk.END)
            result = self.checker.check_prd(prd_content)
            
            # 在主线程中更新UI
            self.root.after(0, self._update_result, result)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, lambda: self.check_button.configure(state=tk.NORMAL))
            
    def _update_result(self, result):
        """更新评审结果显示"""
        self.result_text.delete('1.0', tk.END)
        
        # 显示总分
        self.result_text.insert(tk.END, f"总体评分：{result['score']}/100\n\n")
        
        # 显示缺失项
        self.result_text.insert(tk.END, "缺失项：\n")
        for item in result['missing_items']:
            self.result_text.insert(tk.END, f"- {item}\n")
        self.result_text.insert(tk.END, "\n")
        
        # 显示改进建议
        self.result_text.insert(tk.END, "改进建议：\n")
        for suggestion in result['improvement_suggestions']:
            self.result_text.insert(tk.END, f"- {suggestion}\n")
        self.result_text.insert(tk.END, "\n")
        
        # 显示详细评分
        self.result_text.insert(tk.END, "详细评分：\n")
        for std_id, detail in result['details'].items():
            self.result_text.insert(tk.END, 
                f"[{detail['score']}分] {detail.get('title', f'标准{std_id}')}：\n"
                f"  {detail.get('reason', '无说明')}\n")
        
    def _show_error(self, error_msg):
        """显示错误消息"""
        messagebox.showerror("错误", f"评审过程中发生错误：{error_msg}")
        self.result_text.delete('1.0', tk.END)
        
def main():
    root = tk.Tk()
    app = PRDCheckUI(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()