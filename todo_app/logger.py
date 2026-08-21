# todo_app/logger.py
"""统一日志配置"""

import logging
import os
import sys

from .config import settings


def setup_logger(
    name: str = "todo_app",
    log_file: str | None = None,
    level: int | None = None,
) -> logging.Logger:
    # 不传参数时，从配置中心取值
    log_file = log_file or settings.log_file
    level = level or settings.log_level
    logger = logging.getLogger(name)
    logger.setLevel(level)  # 总开关设为最低，由各 handler 控制
    # 避免重复添加 handler（热重载场景）
    if logger.handlers:
        return logger
    # ---- 格式 ----
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # ---- 控制台 handler（INFO 及以上） ----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # ---- 文件 handler（DEBUG 及以上） ----
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


# 默认实例，各处直接 import 使用
logger = setup_logger()
