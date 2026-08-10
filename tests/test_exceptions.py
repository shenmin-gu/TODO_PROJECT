# tests/test_exceptions.py
"""自定义异常类的单元测试"""

import pytest

from todo_app.exceptions import (
    DuplicateTaskError,
    EmptyTitleError,
    FileReadError,
    FileWriteError,
    InvalidChoiceError,
    StorageError,
    TaskError,
    TaskNotFoundError,
    TodoAppError,
    ValidationError,
)


class TestExceptionHierarchy:
    """验证异常继承体系"""

    def test_storage_error_is_todo_app_error(self):
        assert issubclass(StorageError, TodoAppError)

    def test_file_read_error_is_storage_error(self):
        assert issubclass(FileReadError, StorageError)

    def test_task_not_found_error_is_task_error(self):
        assert issubclass(TaskNotFoundError, TaskError)

    def test_empty_title_error_is_validation_error(self):
        assert issubclass(EmptyTitleError, ValidationError)

    def test_can_catch_by_base_class(self):
        """所有异常都能被 TodoAppError 捕获"""
        try:
            raise TaskNotFoundError(42)
        except TodoAppError:
            pass  # ✅ 应该捕获到
        else:
            pytest.fail("TaskNotFoundError 应该能被 TodoAppError 捕获")


class TestStorageError:
    def test_without_file_path(self):
        err = StorageError("存储失败")
        assert "存储失败" in str(err)
        assert err.file_path is None

    def test_with_file_path(self):
        err = StorageError("存储失败", file_path="/tmp/test.json")
        assert "/tmp/test.json" in str(err)
        assert err.file_path == "/tmp/test.json"


class TestFileReadError:
    def test_message_format(self):
        err = FileReadError("权限不足", file_path="/data/tasks.json")
        msg = str(err)
        assert "读取失败" in msg
        assert "/data/tasks.json" in msg
        assert "权限不足" in msg


class TestFileWriteError:
    def test_message_format(self):
        err = FileWriteError("磁盘已满", file_path="/data/tasks.json")
        msg = str(err)
        assert "写入失败" in msg
        assert "磁盘已满" in msg


class TestTaskNotFoundError:
    def test_storage_task_id(self):
        err = TaskNotFoundError(42)
        assert err.task_id == 42
        assert "42" in str(err)

    def test_can_be_caught_as_task_error(self):
        try:
            raise TaskNotFoundError(1)
        except TaskError:
            pass


class TestDuplicateTaskError:
    def test_stores_title(self):
        err = DuplicateTaskError("买菜")
        assert err.title == "买菜"
        assert "买菜" in str(err)


class TestEmptyTitleError:
    def test_default_message(self):
        err = EmptyTitleError()
        assert "不能为空" in str(err)


class TestInvalidChoiceError:
    def test_stores_choice(self):
        err = InvalidChoiceError("X")
        assert err.choice == "X"
        assert "X" in str(err)
