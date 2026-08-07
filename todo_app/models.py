# todo_app/models.py
from typing import Dict, Any, Union
class Task:
    """代表一个待办任务"""
    def __init__(self, task_id: int, title: str, completed: bool = False):
        self.id: int = task_id
        self.title: str = title
        self.completed: bool = completed
    def mark_completed(self) -> None:
        """标记为已完成，不返回任何值"""
        self.completed = True
    def to_dict(self) -> Dict[str, Union[int, str, bool]]:
        """转为字典，方便序列化""" 
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典还原成 Task 对象"""
        # 这里需要对字段作一点类型适配，假设 data 可能直接来自 json
        return cls(
            task_id=int(data["id"]), 
            title=str(data["title"]), 
            completed=bool(data.get("completed", False))
        )