from .models import Task
from .storage import TaskStorage
from .exceptions import TaskNotFoundError, EmptyTitleError
class TaskManager:
    def __init__(self, storage: TaskStorage):
        self.storage = storage
        self.tasks: list[Task] = self.storage.load_all()
    def _get_next_id(self) -> int:
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1
    def add_task(self, title: str) -> Task:
        if not title or not title.strip():
            raise EmptyTitleError()
        new_task = Task(self._get_next_id(), title.strip())
        self.tasks.append(new_task)
        self.storage.save_all(self.tasks)     # 持久化
        return new_task
    def complete_task(self, task_id: int) -> Task:
        task = self._find_task(task_id)
        task.mark_completed()
        self.storage.save_all(self.tasks)
        return task
    def delete_task(self, task_id: int) -> Task:
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self.storage.save_all(self.tasks)
        return task
    def get_all_tasks(self) -> list[Task]:
        return self.tasks.copy()     # 返回副本，防止外部意外修改
    def _find_task(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)