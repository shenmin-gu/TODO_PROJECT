# tests/test_manager.py
from unittest.mock import MagicMock

import pytest

from todo_app.exceptions import EmptyTitleError, TaskNotFoundError
from todo_app.manager import TaskManager
from todo_app.models import Task


# ============================================================
# Fixture：创建一个"干净的" TaskManager，不碰真实文件
# ============================================================
@pytest.fixture
def manager():
    """
    pytest fixture 的作用：
    每个测试函数调用 manager 时，都会获得一个全新的、空白的 TaskManager 实例。
    我们用 MagicMock 替代真实的 TaskStorage：
    - storage.load_all() 返回空列表（模拟没有历史数据）
    - storage.save_all() 什么也不做（不写文件）
    """
    mock_storage = MagicMock()
    mock_storage.load_all.return_value = []  # 初始化为空
    mock_storage.save_all.return_value = [None]  # 保存时不做任何事
    return TaskManager(storage=mock_storage)


# ============================================================
# 测试用例 1：添加一个有效任务（正常路径）
# ============================================================
def test_add_task_success(manager):
    """添加一个正常标题的任务，应该返回 Task 对象且属性正确"""
    task = manager.add_task("学习 pytest")
    # 断言返回类型
    assert isinstance(task, Task)
    # 断言标题
    assert task.title == "学习 pytest"
    # 断言 id（第一个任务 id 应为 1）
    assert task.id == 1
    # 断言新任务默认未完成
    assert task.completed is False
    # 断言任务已加入列表
    assert len(manager.get_all_tasks()) == 1


# ============================================================
# 测试用例 2：用空标题添加任务（异常路径）
# ============================================================
def test_add_task_with_empty_title(manager):
    """添加空标题应该抛出 EmptyTitleError"""
    with pytest.raises(EmptyTitleError):
        manager.add_task("")
    with pytest.raises(EmptyTitleError):
        manager.add_task("   ")  # 只有空格也不行
    # 确认任务列表没有变化
    assert len(manager.get_all_tasks()) == 0


# ============================================================
# 测试用例 3：完成一个存在的任务（正常路径）
# ============================================================
def test_complete_task_success(manager):
    """标记一个存在的任务为已完成"""
    # 先添加一个任务
    task = manager.add_task("买菜")
    assert task.completed is False  # 初始未完成
    # 完成任务
    completed_task = manager.complete_task(task.id)
    assert completed_task.completed is True
    # 从列表中也确认
    tasks = manager.get_all_tasks()
    assert tasks[0].completed is True


# ============================================================
# 测试用例 4：删除一个存在的任务（正常路径）
# ============================================================
def test_delete_task_success(manager):
    """删除一个存在的任务，列表应该变短"""
    # 添加两个任务
    task1 = manager.add_task("任务A")
    task2 = manager.add_task("任务B")
    assert len(manager.get_all_tasks()) == 2
    # 删除第一个任务
    deleted = manager.delete_task(task1.id)
    assert deleted.id == task1.id
    # 现在只剩一个任务
    tasks = manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == task2.id  # 剩下的是任务B


# ============================================================
# 测试用例 5：查找不存在的任务（异常路径）
# ============================================================
def test_find_nonexistent_task(manager):
    """对不存在的任务 ID 进行操作应该抛出 TaskNotFoundError"""
    # 完成一个不存在的任务
    with pytest.raises(TaskNotFoundError):
        manager.complete_task(999)
    # 删除一个不存在的任务
    with pytest.raises(TaskNotFoundError):
        manager.delete_task(999)


# ============================================================
# 测试用例 6（附加题）：_get_next_id 的逻辑
# ============================================================
def test_get_next_id(manager):
    """验证 ID 分配逻辑：自动递增，且不会重复"""
    task1 = manager.add_task("第一个")
    task2 = manager.add_task("第二个")
    assert task1.id == 1
    assert task2.id == 2
    # 删除第一个，再添加一个新任务，id 应为 3（而非 1）
    manager.delete_task(task1.id)
    task3 = manager.add_task("第三个")
    assert task3.id == 3
