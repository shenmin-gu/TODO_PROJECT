# todo_app/storage.py
import json
import os
from typing import Any

from .exceptions import FileReadError, FileWriteError
from .logger import logger
from .models import Task


class TaskStorage:
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path: str = file_path

    def load_all(self) -> list[Task]:
        """从文件加载所有任务对象"""
        logger.info("正在从 %s 加载任务...", self.file_path)
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # 文件为空
                    return []
                raw: Any = json.loads(content)
                if not isinstance(raw, list):
                    return []
                data: list[dict[str, Any]] = raw  # 使用 loads，或继续用 load
                tasks = [Task.from_dict(item) for item in data]
                logger.debug("加载完成，共 %d 条任务", len(tasks))
                return tasks
        except json.JSONDecodeError as e:
            # 若文件内容无效，可返回空列表或抛出更明确的异常
            # 这里建议返回空列表，以便应用能启动
            logger.warning(
                "数据文件 %s 内容损坏，无法解析，已按空列表处理", self.file_path
            )
            return []
        except OSError as e:
            logger.exception("加载文件 %s 失败", self.file_path)
            raise FileReadError(str(e), file_path=self.file_path) from e

    def save_all(self, tasks: list[Task]) -> None:
        """将所有任务对象保存到文件"""
        try:
            data: list[dict[str, Any]] = [task.to_dict() for task in tasks]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("已保存 %d 条任务到 %s", len(tasks), self.file_path)
        except (IOError, TypeError) as e:
            logger.exception("保存任务到 %s 失败", self.file_path)  # 红灯 + 完整堆栈
            raise FileWriteError(str(e), file_path=self.file_path) from e
