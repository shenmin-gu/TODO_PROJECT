# 从 cli 模块中导入 main 函数，这样外部可以这样做
# from todo_app.cli import main 或直接 todo_app.main()
from .cli import TodoAppCLI
print("待办事项包已加载")