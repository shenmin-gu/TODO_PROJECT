# todo_app/config.py
"""集中式配置中心：所有配置从这里读取，其他模块禁止散落硬编码。"""

import logging
import os

from dotenv import load_dotenv

# 模块一被导入就执行：把 .env 注入 os.environ（只注入一次，重复调用无害）
load_dotenv()


class Settings:
    """项目配置。读取优先级：真实环境变量 > .env 文件 > 这里的默认值"""

    def __init__(self) -> None:
        self.data_file: str = os.environ.get("TODO_DATA_FILE", "tasks.json")
        self.log_file: str = os.environ.get("TODO_LOG_FILE", "todo_app.log")
        self.log_level: int = self._parse_log_level(
            os.environ.get("TODO_LOG_LEVEL", "INFO")
        )

    @staticmethod
    def _parse_log_level(raw: str) -> int:
        """把字符串级别转成 logging 常量；写错了就宽容回退到 INFO。"""
        level = getattr(logging, raw.strip().upper(), None)
        return level if isinstance(level, int) else logging.INFO


settings = Settings()
