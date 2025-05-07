import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
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
        # 创建左右分栏
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=7)
        self.main_frame.rowconfigure(0, weight=1)
        
        # 左侧评审标准列表
        self._create_standards_list(left_frame)
        
        # 右侧PRD编辑和评审结果
        self._create_prd_editor(right_frame)
    
    def _create_standards_list(self, parent):
        """创建评审标准列表"""
        # 标题
        ttk.Label(parent, text="评审标准", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        # 创建带滚动条的框架
        standards_frame = ttk.Frame(parent)
        standards_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview控件
        columns = ('id', 'title')
        self.standards_tree = ttk.Treeview(standards_frame, columns=columns, show='headings', height=25)
        self.standards_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 设置列标题
        self.standards_tree.heading('id', text='ID')
        self.standards_tree.heading('title', text='标准名称')
        
        # 配置列宽
        self.standards_tree.column('id', width=40, anchor='center')
        self.standards_tree.column('title', width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(standards_frame, orient=tk.VERTICAL, command=self.standards_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.standards_tree.configure(yscrollcommand=scrollbar.set)
        
        # 添加评审标准到列表
        for std in self.checker.standards:
            self.standards_tree.insert('', tk.END, values=(std['id'], std['title']))
        
        # 标准详情框
        ttk.Label(parent, text="标准详情:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.standard_detail = tk.Text(parent, height=10, wrap=tk.WORD)
        self.standard_detail.pack(fill=tk.X, expand=False)
        
        # 绑定选择事件
        self.standards_tree.bind('<<TreeviewSelect>>', self._on_standard_selected)
    
    def _create_prd_editor(self, parent):
        """创建PRD编辑区域和评审结果显示"""
        # 创建笔记本控件
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # PRD编辑页
        prd_frame = ttk.Frame(notebook)
        notebook.add(prd_frame, text="PRD内容")
        
        # 评审结果页
        result_frame = ttk.Frame(notebook)
        notebook.add(result_frame, text="评审结果")
        
        # PRD模板选择区域
        template_frame = ttk.Frame(prd_frame)
        template_frame.pack(fill=tk.X, pady=5)
        
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
            *list(templates.keys()),
            command=self.load_template
        )
        template_menu.pack(side=tk.LEFT, padx=5)
        
        # PRD内容编辑区
        prd_content_frame = ttk.Frame(prd_frame)
        prd_content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建文本框和滚动条
        self.prd_text = tk.Text(prd_content_frame, wrap=tk.WORD)
        self.prd_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        prd_scrollbar = ttk.Scrollbar(prd_content_frame, command=self.prd_text.yview)
        prd_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prd_text.configure(yscrollcommand=prd_scrollbar.set)
        
        # 按钮区域
        button_frame = ttk.Frame(prd_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.check_button = ttk.Button(button_frame, text="评审文档", command=self.check_prd)
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        # 评审结果区域
        result_notebook = ttk.Notebook(result_frame)
        result_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建格式化结果标签页
        formatted_frame = ttk.Frame(result_notebook)
        result_notebook.add(formatted_frame, text="格式化结果")
        
        # 添加格式化结果文本框
        self.result_text = tk.Text(formatted_frame, wrap=tk.WORD)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        result_scrollbar = ttk.Scrollbar(formatted_frame, command=self.result_text.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        # 创建JSON格式标签页
        json_frame = ttk.Frame(result_notebook)
        result_notebook.add(json_frame, text="JSON数据")
        
        # 添加JSON文本框
        self.json_text = tk.Text(json_frame, wrap=tk.WORD)
        self.json_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        json_scrollbar = ttk.Scrollbar(json_frame, command=self.json_text.yview)
        json_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_text.configure(yscrollcommand=json_scrollbar.set)
        
        # 初始化加载示例PRD
        self.load_template()
    
    def _on_standard_selected(self, event):
        """处理评审标准选择事件"""
        selected_items = self.standards_tree.selection()
        if selected_items:
            item = selected_items[0]
            item_id = self.standards_tree.item(item, 'values')[0]
            
            # 根据ID查找标准详情
            for std in self.checker.standards:
                if str(std['id']) == str(item_id):
                    self.standard_detail.delete('1.0', tk.END)
                    detail_text = f"标准名称: {std['title']}\n\n描述: {std['description']}"
                    self.standard_detail.insert('1.0', detail_text)
                    break
    
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
        # 更新格式化结果显示
        self.result_text.delete('1.0', tk.END)
        
        # 配置文本标签样式
        self.result_text.tag_configure("title", font=("Arial", 12, "bold"))
        self.result_text.tag_configure("subtitle", font=("Arial", 10, "bold"))
        self.result_text.tag_configure("item", font=("Arial", 10))
        self.result_text.tag_configure("score_high", foreground="green")
        self.result_text.tag_configure("score_medium", foreground="orange")
        self.result_text.tag_configure("score_low", foreground="red")
        
        # 显示总分
        self.result_text.insert(tk.END, "总体评分：", "title")
        score = result.get('score', 0)
        score_tag = "score_high" if score >= 80 else "score_medium" if score >= 60 else "score_low"
        self.result_text.insert(tk.END, f"{score}/100\n\n", score_tag)
        
        # 显示缺失项
        missing_items = result.get('missing_items', [])
        if missing_items:
            self.result_text.insert(tk.END, "缺失项：\n", "subtitle")
            for item in missing_items:
                self.result_text.insert(tk.END, f"• {item}\n", "item")
            self.result_text.insert(tk.END, "\n")
        
        # 显示改进建议
        improvement_suggestions = result.get('improvement_suggestions', [])
        if improvement_suggestions:
            self.result_text.insert(tk.END, "改进建议：\n", "subtitle")
            for suggestion in improvement_suggestions:
                self.result_text.insert(tk.END, f"• {suggestion}\n", "item")
            self.result_text.insert(tk.END, "\n")
        
        # 显示详细评分
        self.result_text.insert(tk.END, "详细评分：\n", "subtitle")
        details = result.get('details', {})
        for std_id, detail in sorted(details.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
            score = detail.get('score', 0)
            score_tag = "score_high" if score >= 80 else "score_medium" if score >= 60 else "score_low"
            
            self.result_text.insert(tk.END, f"{detail.get('title', f'标准{std_id}')}：", "subtitle")
            self.result_text.insert(tk.END, f"{score}分\n", score_tag)
            self.result_text.insert(tk.END, f"  {detail.get('reason', '无说明')}\n\n", "item")
        
        # 显示原始JSON数据，格式化显示
        self.json_text.delete('1.0', tk.END)
        formatted_json = json.dumps(result, indent=4, ensure_ascii=False)
        self.json_text.insert('1.0', formatted_json)
        
        # 高亮评审标准树中的问题项
        self._highlight_problem_standards(details)
    
    def _highlight_problem_standards(self, details):
        """高亮评审标准树中的问题项"""
        # 先重置所有项目的标签
        for item in self.standards_tree.get_children():
            self.standards_tree.item(item, tags=())
        
        # 配置标签样式
        self.standards_tree.tag_configure('low_score', background='#ffcccc')
        self.standards_tree.tag_configure('medium_score', background='#ffffcc')
        self.standards_tree.tag_configure('high_score', background='#ccffcc')
        
        # 根据评分结果设置标签
        for item in self.standards_tree.get_children():
            item_id = self.standards_tree.item(item, 'values')[0]
            if str(item_id) in details:
                score = details[str(item_id)].get('score', 0)
                if score < 60:
                    self.standards_tree.item(item, tags=('low_score',))
                elif score < 80:
                    self.standards_tree.item(item, tags=('medium_score',))
                else:
                    self.standards_tree.item(item, tags=('high_score',))
    
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