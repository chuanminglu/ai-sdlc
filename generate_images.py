from PIL import Image, ImageDraw, ImageFont
import os
import pyautogui
from datetime import datetime
import time

class ImageGenerator:
    def __init__(self):
        self.output_dir = "docs/images"
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        # 设置截图等待时间
        self.wait_time = 15

    def generate_logo(self):
        """生成AI-SDLC Logo"""
        # 创建一个新的图片，使用RGBA模式支持透明背景
        img = Image.new('RGBA', (400, 400), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            # 尝试加载字体，如果失败则使用默认字体
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

        # 绘制文字
        draw.text((100, 150), "AI-SDLC", fill=(98, 0, 238), font=font)
        draw.text((100, 220), "智能需求管理", fill=(0, 0, 0), font=font)
        
        # 保存logo
        logo_path = os.path.join(self.output_dir, "ai-sdlc-logo.png")
        img.save(logo_path)
        return logo_path

    def capture_main_ui(self):
        """捕获主界面截图"""
        print(f"\n=== 主界面截图 ===")
        print("1. 请切换到AI-SDLC主界面")
        print("2. 确保界面显示完整")
        print(f"3. 将在{self.wait_time}秒后自动截图...")
        
        self._countdown()
        
        # 捕获屏幕截图
        screenshot = pyautogui.screenshot()
        ui_path = os.path.join(self.output_dir, "main-ui.png")
        screenshot.save(ui_path)
        return ui_path

    def capture_story_parsing(self):
        """捕获用户故事解析示例截图"""
        print(f"\n=== 用户故事解析界面截图 ===")
        print("1. 请生成并解析一个用户故事")
        print("2. 确保解析结果显示完整")
        print(f"3. 将在{self.wait_time}秒后自动截图...")
        
        self._countdown()
        
        screenshot = pyautogui.screenshot()
        parsing_path = os.path.join(self.output_dir, "story-parsing.png")
        screenshot.save(parsing_path)
        return parsing_path

    def capture_api_spec(self):
        """捕获API规范生成界面截图"""
        print(f"\n=== API规范生成界面截图 ===")
        print("1. 请点击'创建API规范'按钮")
        print("2. 等待API规范生成完成")
        print(f"3. 将在{self.wait_time}秒后自动截图...")
        
        self._countdown()
        
        screenshot = pyautogui.screenshot()
        api_path = os.path.join(self.output_dir, "api-spec.png")
        screenshot.save(api_path)
        return api_path

    def capture_constraints(self):
        """捕获约束条件示例截图"""
        print(f"\n=== 约束条件界面截图 ===")
        print("1. 请点击'生成约束检查清单'按钮")
        print("2. 等待约束条件生成完成")
        print(f"3. 将在{self.wait_time}秒后自动截图...")
        
        self._countdown()
        
        screenshot = pyautogui.screenshot()
        constraints_path = os.path.join(self.output_dir, "constraints.png")
        screenshot.save(constraints_path)
        return constraints_path

    def _countdown(self):
        """倒计时显示"""
        for i in range(self.wait_time, 0, -1):
            print(f"倒计时: {i}秒...", end='\r')
            time.sleep(1)
        print("\n准备截图...")

    def generate_all(self):
        """生成所有需要的图片"""
        print("开始生成图片...\n")
        
        # 生成Logo
        logo_path = self.generate_logo()
        print(f"Logo已生成：{logo_path}")
        
        # 捕获主界面
        ui_path = self.capture_main_ui()
        print(f"主界面截图已保存：{ui_path}")
        
        # 捕获用户故事解析示例
        parsing_path = self.capture_story_parsing()
        print(f"解析示例截图已保存：{parsing_path}")
        
        # 捕获API规范生成界面
        api_path = self.capture_api_spec()
        print(f"API规范截图已保存：{api_path}")
        
        # 捕获约束条件示例
        constraints_path = self.capture_constraints()
        print(f"约束条件截图已保存：{constraints_path}")
        
        print("\n所有图片生成完成！")
        return {
            'logo': logo_path,
            'ui': ui_path,
            'parsing': parsing_path,
            'api': api_path,
            'constraints': constraints_path
        }

if __name__ == "__main__":
    generator = ImageGenerator()
    generator.generate_all()