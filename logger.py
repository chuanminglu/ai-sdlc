"""
日志管理模块
提供统一的日志记录功能，支持：
1. 多级别日志
2. 文件滚动
3. 自定义格式化
4. 性能追踪
"""

import logging
import logging.handlers
import os
import time
from functools import wraps
from typing import Callable, Optional

class PerformanceLogger:
    def __init__(self, logger_instance):
        self.logger = logger_instance

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒
            self.logger.debug(
                f"函数 {func.__name__} 执行耗时: {execution_time:.2f}ms"
            )
            return result
        return wrapper

class CustomLogger:
    def __init__(self, name: str = "AI-SDLC", 
                 log_level: str = "INFO",
                 log_file: Optional[str] = "logs/app.log",
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件处理器
        if log_file:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.performance = PerformanceLogger(self.logger)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

# 创建全局日志实例
logger = CustomLogger()

# 性能装饰器示例使用:
# @logger.performance
# def some_function():
#     pass