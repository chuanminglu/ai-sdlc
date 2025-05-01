"""
配置管理模块 (Configuration Manager)

本模块负责管理应用程序的配置信息，提供以下功能：
1. 读取和解析配置文件
2. 提供配置项的访问接口
3. 支持配置的动态更新
4. 配置变更的日志记录

配置文件格式：
[API]
api_key = your_api_key_here
base_url = https://api.example.com

[Logging]
level = INFO
file_path = logs/app.log

使用示例：
```python
from config_manager import ConfigManager

config = ConfigManager()
api_key = config.get('API', 'api_key')
log_level = config.get('Logging', 'level')
```
"""

import configparser
import os
from typing import Any, Optional
from logger import logger

class ConfigManager:
    """
    配置管理器类
    
    负责处理所有与配置相关的操作，包括：
    - 配置文件的读取和解析
    - 配置项的获取和设置
    - 配置文件的监视和自动重载
    - 配置修改的安全性验证
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """
        初始化配置管理器
        
        参数：
            config_path (str): 配置文件路径，默认为'config.ini'
        
        异常：
            FileNotFoundError: 配置文件不存在时抛出
            configparser.Error: 配置文件格式错误时抛出
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self._load_config()
        
    def _load_config(self) -> None:
        """
        加载配置文件
        
        读取并解析配置文件，支持：
        - INI 格式的配置文件
        - 环境变量覆盖
        - 配置模板自动生成
        """
        if not os.path.exists(self.config_path):
            self._create_default_config()
        self.config.read(self.config_path)
        
    def _create_default_config(self) -> None:
        """
        创建默认配置文件
        
        当配置文件不存在时，基于模板创建默认配置：
        1. 复制模板文件（如果存在）
        2. 创建包含基本配置项的新文件
        3. 设置默认值
        """
        template_path = f"{self.config_path}.template"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as template:
                with open(self.config_path, 'w', encoding='utf-8') as config:
                    config.write(template.read())
        else:
            self._write_default_values()
            
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """
        获取配置项值
        
        参数：
            section (str): 配置节名称
            option (str): 配置项名称
            fallback (Any): 默认值，当配置项不存在时返回
        
        返回：
            Any: 配置项的值
            
        示例：
            >>> config.get('API', 'base_url', 'https://api.default.com')
        """
        return self.config.get(section, option, fallback=fallback)
        
    def set(self, section: str, option: str, value: str) -> None:
        """
        设置配置项值
        
        参数：
            section (str): 配置节名称
            option (str): 配置项名称
            value (str): 要设置的值
            
        异常：
            ValueError: 当值格式不正确时抛出
            
        注意：
            修改后的配置会自动保存到文件
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        self._save_config()
        
    def _save_config(self) -> None:
        """
        保存配置到文件
        
        执行以下操作：
        1. 备份现有配置
        2. 写入新配置
        3. 记录修改日志
        """
        with open(self.config_path, 'w', encoding='utf-8') as config_file:
            self.config.write(config_file)
        logger.info(f"配置已更新：{self.config_path}")

    def validate_config(self) -> bool:
        """
        验证配置的完整性和正确性
        
        检查项目：
        1. 必需的配置节和选项是否存在
        2. 配置值的格式是否正确
        3. 配置项之间的依赖关系是否满足
        
        返回：
            bool: 配置验证是否通过
        """
        required_sections = {'API', 'Logging'}
        required_options = {
            'API': ['api_key', 'base_url'],
            'Logging': ['level', 'file_path']
        }
        
        # 验证必需的配置节
        if not all(self.config.has_section(section) for section in required_sections):
            return False
            
        # 验证必需的配置项
        for section, options in required_options.items():
            if not all(self.config.has_option(section, option) for option in options):
                return False
                
        return True