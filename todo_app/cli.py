# todo_app/cli.py
from .exceptions import EmptyTitleError, TaskNotFoundError, ValidationError
from .manager import TaskManager
from .storage import TaskStorage


class TodoAppCLI:
    def __init__(self) -> None:
        # 依赖注入：把具体存储对象传给管理器
        storage = TaskStorage("tasks.json")
        self.manager = TaskManager(storage)

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
            elif choice == "0":
                print("👋 再见！")
                break
            else:
                print(f"❌ 无效选择「{choice}」，请输入 0~4")

    def _show_menu(self) -> None:
        print("\n===== 待办事项应用 =====")
        print("1. 查看任务")
        print("2. 添加任务")
        print("3. 完成任务")
        print("4. 删除任务")
        print("0. 退出")

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
