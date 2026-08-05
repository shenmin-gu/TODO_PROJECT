from todo_app.cli import TodoAppCLI     # 等价于 from todo_app.cli import main
if __name__ == "__main__":
    app = TodoAppCLI()
    app.run()