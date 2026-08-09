# todo_app/manager.py
from .exceptions import EmptyTitleError, TaskNotFoundError
from .models import Task
from .storage import TaskStorage


class TaskManager:
    def __init__(self, storage: TaskStorage):
        self.storage: TaskStorage = storage
        self.tasks: list[Task] = self.storage.load_all()

    def _get_next_id(self) -> int:
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def add_task(self, title: str) -> Task:
        """添加一个新任务，标题不能为空"""
        if not title or not title.strip():
            raise EmptyTitleError()
        new_task = Task(self._get_next_id(), title.strip())
        self.tasks.append(new_task)
        self.storage.save_all(self.tasks)  # 持久化
        return new_task

    def complete_task(self, task_id: int) -> Task:
        """根据 id 完成任务，找不到则抛异常"""
        task = self._find_task(task_id)
        task.mark_completed()
        self.storage.save_all(self.tasks)
        return task

    def delete_task(self, task_id: int) -> Task:
        """根据 id 删除任务，找不到则抛异常"""
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self.storage.save_all(self.tasks)
        return task

    def get_all_tasks(self) -> list[Task]:
        """返回所有任务（副本）"""
        return self.tasks.copy()

    def _find_task(self, task_id: int) -> Task:
        """内部查找任务，找不到抛出 TaskNotFoundError"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)
