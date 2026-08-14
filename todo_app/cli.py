# todo_app/cli.py（在原有基础上添加两个方法和两个菜单项）
# ===== 文件顶部添加导入 =====
from .csv_io import export_tasks_to_csv, import_tasks_from_csv
from .exceptions import (  # 🆕 新增
    EmptyTitleError,
    FileReadError,
    FileWriteError,
    TaskNotFoundError,
    ValidationError,
)
from .manager import TaskManager
from .storage import TaskStorage


class TodoAppCLI:
    def __init__(self) -> None:
        # 依赖注入：把具体存储对象传给管理器
        storage = TaskStorage("tasks.json")
        self.manager: TaskManager = TaskManager(storage)

    def run(self) -> None:
        print("待办事项应用 v2（OOP 版）")
        while True:
            self._show_menu()
            choice = input("请选择操作：").strip()
            if choice == "1":
                self._show_tasks()
            elif choice == "2":
                self._add_task()
            elif choice == "3":
                self._complete_task()
            elif choice == "4":
                self._delete_task()
            elif choice == "5":
                self._export_csv()
            elif choice == "6":
                self._import_csv()
            elif choice == "0":
                print("👋 再见！")
                break
            else:
                print(f"❌ 无效选择「{choice}」，请输入 0~6")

    def _show_menu(self) -> None:
        print("\n===== 待办事项应用 =====")
        print("1. 查看任务")
        print("2. 添加任务")
        print("3. 完成任务")
        print("4. 删除任务")
        print("5. 导出 CSV")
        print("6. 导入 CSV")
        print("0. 退出")

    def _export_csv(self) -> None:
        """将当前所有任务导出为 CSV 文件"""
        file_path = input("请输入导出文件路径（默认：tasks_export.csv)：").strip()
        if not file_path:
            file_path = "tasks_export.csv"
        # 自动加 .csv 后缀
        if not file_path.endswith(".csv"):
            file_path += ".csv"
        try:
            tasks = self.manager.get_all_tasks()
            count = export_tasks_to_csv(tasks, file_path)
            print(f"✅ 成功导出 {count} 条任务到「{file_path}」")
        except FileWriteError as e:
            print(f"❌ {e}")

    def _import_csv(self) -> None:
        """从 CSV 文件导入任务"""
        file_path = input("请输入要导入的 CSV 文件路径：").strip()
        if not file_path:
            print("❌ 文件路径不能为空")
            return
        try:
            imported_tasks = import_tasks_from_csv(file_path)
            if not imported_tasks:
                print("⚠️ CSV 文件中没有可导入的任务")
                return
            # 逐个添加到管理器（会自动处理 ID 和持久化）
            for task in imported_tasks:
                try:
                    self.manager.add_task(task.title)
                except EmptyTitleError:
                    print(f"⚠️ 跳过空标题任务")
            print(f"✅ 成功从 CSV 导入 {len(imported_tasks)} 条任务")
        except FileReadError as e:
            print(f"❌ {e}")
        except ValidationError as e:
            print(f"❌ {e}")

    def _show_tasks(self) -> None:
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("📭 当前没有任务")
            return
        print("\n📋 任务列表：")
        for task in tasks:
            status = "✅" if task.completed else "⬜"
            print(f"  {status} [{task.id}] {task.title}")
        print()

    def _add_task(self) -> None:
        title: str = input("请输入任务内容：").strip()
        try:
            task = self.manager.add_task(title)
            print(f"✅ 已添加任务：{task.title}")
        except EmptyTitleError as e:
            print(f"❌ {e}")

    def _complete_task(self) -> None:
        self._show_tasks()
        try:
            task_id: int = self._input_task_id("请输入要完成的任务 id: ")
            self.manager.complete_task(task_id)
            print(f"✅ 任务 [{task_id}] 已完成")
        except (TaskNotFoundError, ValidationError) as e:
            print(f"❌ {e}")

    def _delete_task(self) -> None:
        self._show_tasks()
        try:
            task_id: int = self._input_task_id("请输入要删除的任务 id: ")
            self.manager.delete_task(task_id)
            print(f"🗑️ 已删除任务 [{task_id}]")
        except (TaskNotFoundError, ValidationError) as e:
            print(f"❌ {e}")

    def _input_task_id(self, prompt: str) -> int:
        raw: str = input(prompt).strip()
        if not raw.isdigit():
            raise ValidationError(f"「{raw}」不是有效的数字")
        return int(raw)
