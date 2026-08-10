# todo_app/storage.py
import json
import os
from typing import Any

from .exceptions import FileReadError, FileWriteError
from .models import Task


class TaskStorage:
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path: str = file_path

    def load_all(self) -> list[Task]:
        """从文件加载所有任务对象"""
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
                return [Task.from_dict(item) for item in data]
        except json.JSONDecodeError as e:
            # 若文件内容无效，可返回空列表或抛出更明确的异常
            # 这里建议返回空列表，以便应用能启动
            return []
        except OSError as e:
            raise FileReadError(str(e), file_path=self.file_path) from e

    def save_all(self, tasks: list[Task]) -> None:
        """将所有任务对象保存到文件"""
        try:
            data: list[dict[str, Any]] = [task.to_dict() for task in tasks]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (IOError, TypeError) as e:
            raise FileWriteError(str(e), file_path=self.file_path) from e
