class Task:
    """代表一个待办任务"""
    def __init__(self, task_id: int, title: str, completed: bool = False):
        self.id = task_id
        self.title = title
        self.completed = completed
    def mark_completed(self):
        self.completed = True
    def to_dict(self):
        """转为字典，方便序列化""" 
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed
        }
    @classmethod
    def from_dict(cls, data: dict):
        """从字典还原成 Task 对象"""
        return cls(data["id"], data["title"], data.get("completed", False))