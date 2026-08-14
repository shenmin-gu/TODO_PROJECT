# tests/test_csv_io.py
"""CSV 导入导出功能的单元测试"""

import os
import tempfile

import pytest

from todo_app.csv_io import export_tasks_to_csv, import_tasks_from_csv
from todo_app.exceptions import FileReadError, FileWriteError, ValidationError
from todo_app.models import Task


class TestExportTasksToCSV:
    """测试 CSV 导出"""

    def test_export_empty_list_creates_header_only(self):
        """导出空任务列表，文件只有表头"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            count = export_tasks_to_csv([], tmp_path)
            assert count == 0
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "id,title,completed" in content
        finally:
            os.unlink(tmp_path)

    def test_export_single_task(self):
        """导出一条任务"""
        tasks = [Task(task_id=1, title="测试任务", completed=False)]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            count = export_tasks_to_csv(tasks, tmp_path)
            assert count == 1
            with open(tmp_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            assert len(lines) == 2  # 表头 + 1 条数据
            assert "测试任务" in lines[1]
            assert "False" in lines[1]
        finally:
            os.unlink(tmp_path)

    def test_export_multiple_tasks(self):
        """导出多条任务，验证每行数据"""
        tasks = [
            Task(task_id=1, title="买菜", completed=False),
            Task(task_id=2, title="写代码", completed=True),
            Task(task_id=3, title="学Python", completed=False),
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            count = export_tasks_to_csv(tasks, tmp_path)
            assert count == 3
            with open(tmp_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            assert len(lines) == 4
            assert "买菜" in lines[1]
            assert "True" in lines[2]
        finally:
            os.unlink(tmp_path)

    def test_export_to_nonexistent_directory(self):
        """导出到不存在的目录，应自动创建"""
        import tempfile

        tmp_dir = tempfile.mkdtemp()
        nested_path = os.path.join(tmp_dir, "subdir", "tasks.csv")
        try:
            count = export_tasks_to_csv([Task(1, "测试", False)], nested_path)
            assert count == 1
            assert os.path.exists(nested_path)
        finally:
            import shutil

            shutil.rmtree(tmp_dir, ignore_errors=True)


class TestImportTasksFromCSV:
    """测试 CSV 导入"""

    def _create_csv(self, content: str) -> str:
        """辅助方法：创建临时 CSV 文件并返回路径"""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_import_basic(self):
        """基本导入：含表头和两条数据"""
        csv_content = "id,title,completed\n1,买菜,False\n2,写代码,True\n"
        path = self._create_csv(csv_content)
        try:
            tasks = import_tasks_from_csv(path)
            assert len(tasks) == 2
            assert tasks[0].title == "买菜"
            assert tasks[0].completed is False
            assert tasks[1].title == "写代码"
            assert tasks[1].completed is True
        finally:
            os.unlink(path)

    def test_import_empty_file(self):
        """导入只有表头的空文件"""
        csv_content = "id,title,completed\n"
        path = self._create_csv(csv_content)
        try:
            tasks = import_tasks_from_csv(path)
            assert len(tasks) == 0
        finally:
            os.unlink(path)

    def test_import_file_not_found(self):
        """导入不存在的文件应抛出 FileReadError"""
        with pytest.raises(FileReadError, match="文件不存在"):
            import_tasks_from_csv("/nonexistent/path/tasks.csv")

    def test_import_missing_column(self):
        """CSV 缺少必要列应抛出 ValidationError"""
        csv_content = "id,title\n1,买菜\n"  # 缺少 completed 列
        path = self._create_csv(csv_content)
        try:
            with pytest.raises(ValidationError, match="completed"):
                import_tasks_from_csv(path)
        finally:
            os.unlink(path)

    def test_import_with_spaces_in_title(self):
        """标题首尾空格应被去除"""
        csv_content = "id,title,completed\n1,  买菜  ,False\n"
        path = self._create_csv(csv_content)
        try:
            tasks = import_tasks_from_csv(path)
            assert tasks[0].title == "买菜"  # 去除了空格
        finally:
            os.unlink(path)

    def test_import_various_completed_formats(self):
        """completed 字段支持多种 true 值写法"""
        csv_content = (
            "id,title,completed\n"
            "1,任务A,true\n"
            "2,任务B,True\n"
            "3,任务C,1\n"
            "4,任务D,yes\n"
            "5,任务E,false\n"
            "6,任务F,0\n"
        )
        path = self._create_csv(csv_content)
        try:
            tasks = import_tasks_from_csv(path)
            assert tasks[0].completed is True  # true
            assert tasks[1].completed is True  # True
            assert tasks[2].completed is True  # 1
            assert tasks[3].completed is True  # yes
            assert tasks[4].completed is False  # false
            assert tasks[5].completed is False  # 0
        finally:
            os.unlink(path)

    def test_roundtrip_export_then_import(self):
        """往返测试：导出 → 导入，数据应一致"""
        original_tasks = [
            Task(task_id=1, title="买菜", completed=False),
            Task(task_id=2, title="写代码，写文档", completed=True),  # 含逗号的标题
        ]
        # 先导出
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            export_tasks_to_csv(original_tasks, tmp_path)
            # 再导入
            imported_tasks = import_tasks_from_csv(tmp_path)
            assert len(imported_tasks) == len(original_tasks)
            for orig, imp in zip(original_tasks, imported_tasks):
                assert imp.title == orig.title
                assert imp.completed == orig.completed
        finally:
            os.unlink(tmp_path)
