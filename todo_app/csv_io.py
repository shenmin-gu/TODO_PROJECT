# todo_app/csv_io.py
"""CSV 导入导出模块 —— 为待办事项提供 CSV 格式的数据交换能力"""

import csv
import os
from typing import List, Optional

from .exceptions import FileReadError, FileWriteError, ValidationError
from .logger import logger
from .models import Task

# ============================================================
#  常量定义
# ============================================================
# CSV 文件的列名（也是 Task 模型的核心字段）
CSV_FIELDNAMES = ["id", "title", "completed"]


# ============================================================
#  导出功能：Task 列表 → CSV 文件
# ============================================================
def export_tasks_to_csv(tasks: List[Task], file_path: str) -> int:
    """
    将任务列表导出为 CSV 文件。
    参数:
        tasks: 要导出的 Task 对象列表
        file_path: 目标 CSV 文件路径（如 "tasks_export.csv"）
    返回:
        成功写入的行数（不含表头）
    异常:
        FileWriteError: 写入文件失败时抛出
    """
    logger.info("导出 %d 条任务到 %s", len(tasks), file_path)
    # 防御性检查：目录不存在则创建
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    try:
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            # 第1步：写表头
            writer.writeheader()
            # 第2步：逐条写入任务数据
            count = 0
            for task in tasks:
                writer.writerow(task.to_dict())
                count += 1
        logger.info("导出成功，写入 %d 行", count)
        return count
    except (IOError, OSError) as e:
        raise FileWriteError(f"导出 CSV 失败：{e}", file_path=file_path) from e


# ============================================================
#  导入功能：CSV 文件 → Task 列表
# ============================================================
def import_tasks_from_csv(file_path: str) -> List[Task]:
    """
    从 CSV 文件导入任务列表。
    预期的 CSV 格式（第一行为表头）：
        id,title,completed
        1,买菜,False
        2,写代码,True
    参数:
        file_path: 源 CSV 文件路径
    返回:
        Task 对象列表
    异常:
        FileReadError: 文件不存在或读取失败
        ValidationError: CSV 格式不正确（缺少必要列等）
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileReadError(f"文件不存在", file_path=file_path)
    tasks: List[Task] = []
    errors: List[str] = []  # 收集所有行的错误，最后一起报告
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # 验证表头是否包含必要列
            if reader.fieldnames is None:
                raise ValidationError("CSV 文件为空，没有表头行")
            missing_fields = set(CSV_FIELDNAMES) - set(reader.fieldnames)
            if missing_fields:
                raise ValidationError(
                    f"CSV 缺少必要列：{', '.join(missing_fields)}。"
                    f"需要的列：{', '.join(CSV_FIELDNAMES)}"
                )
            # 逐行解析
            for row_num, row in enumerate(
                reader, start=2
            ):  # 第1行是表头，数据从第2行开始
                try:
                    task = _parse_csv_row(row, row_num)
                    tasks.append(task)
                except (ValueError, KeyError) as e:
                    # 单行解析失败不中断，记录错误继续
                    errors.append(f"第 {row_num} 行：{e}")
    except (IOError, OSError) as e:
        raise FileReadError(f"读取 CSV 失败：{e}", file_path=file_path) from e
    # 如果有行解析失败，汇总报告
    if errors:
        error_detail = "\n  ".join(errors)
        raise ValidationError(
            f"CSV 导入完成，但以下行解析失败:\n {error_detail}\n"
            f"成功导入：{len(tasks)} 条"
        )
    return tasks


def _parse_csv_row(row: dict, row_num: int) -> Task:
    """
    将 CSV 的一行字典转换为 Task 对象。
    参数:
        row: DictReader 返回的一行数据，如 {"id": "1", "title": "买菜", "completed": "False"}
        row_num: 当前行号（用于错误提示）
    返回:
        Task 对象
    异常:
        ValueError: 数据格式不正确
    """
    # 去除首尾空白
    title = (row.get("title") or "").strip()
    if not title:
        raise ValueError(f"标题不能为空")
    # 解析 id
    raw_id = (row.get("id") or "").strip()
    if not raw_id:
        raise ValueError(f"缺少 id")
    try:
        task_id = int(raw_id)
    except ValueError:
        raise ValueError(f"id「{raw_id}」不是有效整数")
    raw_completed = (row.get("completed") or "False").strip().lower()
    completed = raw_completed in ("true", "1", "yes", "✅", "y")
    return Task(task_id=task_id, title=title, completed=completed)
