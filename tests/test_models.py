# tests/test_models.py
"""Task 数据类的单元测试"""

import pytest

from todo_app.models import Task


class TestTaskCreation:
    """测试 Task 对象的创建"""

    def test_create_task_with_defaults(self):
        """用最少参数创建任务，completed 默认为 False"""
        task = Task(task_id=1, title="学习")
        assert task.id == 1
        assert task.title == "学习"
        assert task.completed is False

    def test_create_completed_task(self):
        """创建时指定 completed=True"""
        task = Task(task_id=2, title="已完成", completed=True)
        assert task.completed is True

    def test_task_id_can_be_large(self):
        """边界：大 ID 值"""
        task = Task(task_id=99999, title="大 ID")
        assert task.id == 99999

    def test_task_title_can_be_long(self):
        """边界：长标题"""
        long_title = "学" * 1000
        task = Task(task_id=1, title=long_title)
        assert len(task.title) == 1000


class TestMarkCompleted:
    """测试 mark_completed 方法"""

    def test_mark_completed_changes_status(self):
        task = Task(task_id=1, title="测试")
        assert task.completed is False
        task.mark_completed()
        assert task.completed is True

    def test_mark_completed_is_idempotent(self):
        """幂等性：多次调用结果不变"""
        task = Task(task_id=1, title="测试")
        task.mark_completed()
        task.mark_completed()
        task.mark_completed()
        assert task.completed is True


class TestToDict:
    """测试 to_dict 序列化"""

    def test_to_dict_returns_correct_keys(self):
        task = Task(task_id=1, title="买菜", completed=False)
        result = task.to_dict()
        assert set(result.keys()) == {"id", "title", "completed"}

    def test_to_dict_values_match(self):
        task = Task(task_id=42, title="写代码", completed=True)
        result = task.to_dict()
        assert result["id"] == 42
        assert result["title"] == "写代码"
        assert result["completed"] is True

    def test_to_dict_roundtrip_with_from_dict(self):
        """往返测试：Task → dict → Task，数据应一致"""
        original = Task(task_id=7, title="往返测试", completed=True)
        as_dict = original.to_dict()
        restored = Task.from_dict(as_dict)
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.completed == original.completed


class TestFromDict:
    """测试 from_dict 反序列化"""

    def test_from_dict_basic(self):
        data = {"id": 3, "title": "测试任务", "completed": True}
        task = Task.from_dict(data)
        assert task.id == 3
        assert task.title == "测试任务"
        assert task.completed is True

    def test_from_dict_missing_completed_defaults_to_false(self):
        """缺少 completed 字段时默认为 False"""
        data = {"id": 1, "title": "无 completed 字段"}
        task = Task.from_dict(data)
        assert task.completed is False

    def test_from_dict_with_string_id(self):
        """id 是字符串也能转换（模拟 JSON 反序列化场景）"""
        data = {"id": "5", "title": "字符串 ID", "completed": False}
        task = Task.from_dict(data)
        assert task.id == 5  # int() 转换成功
        assert isinstance(task.id, int)

    def test_from_dict_with_string_completed(self):
        """completed 是字符串也能转换"""
        data = {"id": 1, "title": "测试", "completed": "True"}
        task = Task.from_dict(data)
        # bool("True") → True（非空字符串都是 True）
        assert task.completed is True
