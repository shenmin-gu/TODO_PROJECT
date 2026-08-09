"""自定义异常类"""


class TodoAppError(Exception):
    """应用根异常——所有自定义异常的基类"""

    pass


# ========== 存储层异常 ==========
class StorageError(TodoAppError):
    """数据存储相关异常"""

    def __init__(self, message: str, file_path: str | None = None) -> None:
        super().__init__(message)
        self.file_path: str | None = file_path

    def __str__(self) -> str:
        base = f"💾 存储错误"
        if self.file_path:
            base += f" [文件: {self.file_path}]"
        return f"{base}: {self.args[0]}"


class FileReadError(StorageError):
    """读取文件失败"""

    def __str__(self) -> str:
        base = f"📂 读取失败"
        if self.file_path:
            base += f" [文件: {self.file_path}]"
        return f"{base}: {self.args[0]}"


class FileWriteError(StorageError):
    """写入文件失败"""

    def __str__(self) -> str:
        base = f"💿 写入失败"
        if self.file_path:
            base += f" [文件：{self.file_path}]"
        return f"{base}: {self.args[0]}"


# ========== 业务层异常 ==========
class TaskError(TodoAppError):
    """任务业务异常基类"""

    pass


class TaskNotFoundError(TaskError):
    """任务不存在"""

    def __init__(self, task_id: int) -> None:
        self.task_id: int = task_id
        super().__init__(f"找不到 id 为 {task_id} 的任务")


class DuplicateTaskError(TaskError):
    """重复任务"""

    def __init__(self, title: str) -> None:
        self.title: str = title
        super().__init__(f"任务 {title} 已经存在")


# ========== 校验异常 ==========
class ValidationError(TodoAppError):
    """输入校验异常"""

    pass


class EmptyTitleError(ValidationError):
    """标题为空"""

    def __init__(self) -> None:
        super().__init__("任务内容不能为空")


class InvalidChoiceError(ValidationError):
    """无效菜单选择"""

    def __init__(self, choice: str) -> None:
        self.choice: str = choice
        super().__init__(f"无效选择 {choice}，请输入 0~4 之间的数字")
