# tests/test_storage.py
import json
from unittest.mock import MagicMock, mock_open, patch

import pytest

from todo_app.exceptions import FileReadError, FileWriteError
from todo_app.models import Task
from todo_app.storage import TaskStorage


# ============================================================
# Fixture：提供一个 TaskStorage 实例（但还没 mock open）
# ============================================================
@pytest.fixture
def storage():
    """返回一个指向假路径的 TaskStorage"""
    return TaskStorage(file_path="/fake/path/tasks.json")


# ============================================================
# 测试用例 1：文件不存在 → 返回空列表
# ============================================================
@patch("todo_app.storage.os.path.exists")
def test_load_all_file_not_exists(mock_exists, storage):
    """当文件不存在时，load_all 应返回 []"""
    mock_exists.return_value = False  # 模拟 os.path.exists 返回 False
    result = storage.load_all()
    assert result == []
    # 注意：因为文件不存在，open() 根本不会被调用


# ============================================================
# 测试用例 2：文件存在且有合法 JSON → 返回 Task 列表
# ============================================================
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=json.dumps([{"id": 1, "title": "测试任务", "completed": False}]),
)
@patch("todo_app.storage.os.path.exists")
def test_load_all_success(mock_exists, mock_file, storage):
    """正常情况：文件存在、JSON 合法 → 返回正确的 Task 列表"""
    mock_exists.return_value = True
    result = storage.load_all()
    assert len(result) == 1
    assert isinstance(result[0], Task)
    assert result[0].id == 1
    assert result[0].title == "测试任务"
    assert result[0].completed is False


# ============================================================
# 测试用例 3：文件存在但为空 → 返回空列表
# ============================================================
@patch("builtins.open", new_callable=mock_open, read_data="")
@patch("todo_app.storage.os.path.exists")
def test_load_all_empty_file(mock_exists, mock_file, storage):
    """文件存在但内容为空 → 返回 []"""
    mock_exists.return_value = True
    result = storage.load_all()
    assert result == []


# ============================================================
# 测试用例 4：文件包含无效 JSON → 返回空列表（你的代码目前这样处理）
# ============================================================
@patch("builtins.open", new_callable=mock_open, read_data="这不是合法 JSON {{{")
@patch("todo_app.storage.os.path.exists")
def test_load_all_invalid_json(mock_exists, mock_file, storage):
    """JSON 格式损坏 → 应优雅处理，返回 []"""
    mock_exists.return_value = True
    result = storage.load_all()
    assert result == []  # 你代码中 json.JSONDecodeError 被捕获并返回 []


# ============================================================
# 测试用例 5：正常保存
# ============================================================
@patch("builtins.open", new_callable=mock_open)
def test_save_all_success(mock_file, storage):
    """正常保存任务列表 → open 被调用，写入正确的 JSON"""
    tasks = [
        Task(task_id=1, title="任务A", completed=False),
        Task(task_id=2, title="任务B", completed=True),
    ]
    # save_all 不返回值（返回 None），所以只需验证无异常
    storage.save_all(tasks)
    # === 关键：验证 open 以正确的方式被调用 ===
    mock_file.assert_called_once_with("/fake/path/tasks.json", "w", encoding="utf-8")
    # 更进一步：验证写入了正确的 JSON 内容
    # mock_file 是 open 返回的文件句柄，它的 .write() 被 json.dump 调用
    # 我们可以获取所有 write 调用的参数
    handle = mock_file()
    # json.dump 可能会分多次 write，拼接起来
    written_data = "".join(call.args[0] for call in handle.write.call_args_list)
    assert "任务A" in written_data
    assert "任务B" in written_data


# ============================================================
# 测试用例 6：写入失败 → 抛出 FileWriteError
# ============================================================
@patch("builtins.open")
def test_save_all_write_error(mock_open_func, storage):
    """模拟磁盘满或权限不足 → 应抛出 FileWriteError"""
    # 让 open 成功（返回 mock 文件句柄），但文件句柄的写入抛异常
    mock_handle = MagicMock()
    mock_handle.__enter__.return_value = mock_handle
    # json.dump 会调用 write，我们让它抛 OSError
    mock_handle.write.side_effect = OSError("磁盘已满")
    mock_open_func.return_value = OSError("磁盘已满")
    tasks = [Task(task_id=1, title="测试", completed=False)]
    with pytest.raises(FileWriteError):
        storage.save_all(tasks)
