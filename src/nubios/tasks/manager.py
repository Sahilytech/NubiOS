from __future__ import annotations

from datetime import date
from typing import Any

from ..memory.database import Database


class TaskManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, title: str, description: str = "", priority: str = "normal", due_date: str | None = None) -> int:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        cur = self.db.execute(
            "INSERT INTO tasks(title, description, priority, due_date) VALUES (?, ?, ?, ?)",
            (title.strip(), description.strip(), priority, due_date),
        )
        return int(cur.lastrowid)

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        if status:
            rows = self.db.execute("SELECT * FROM tasks WHERE status=? ORDER BY id DESC", (status,)).fetchall()
        else:
            rows = self.db.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def complete(self, task_id: int) -> None:
        self.db.execute("UPDATE tasks SET status='completed', completed_at=CURRENT_TIMESTAMP WHERE id=?", (task_id,))

    def overdue(self) -> list[dict[str, Any]]:
        today = date.today().isoformat()
        rows = self.db.execute("SELECT * FROM tasks WHERE status != 'completed' AND due_date IS NOT NULL AND due_date < ? ORDER BY due_date", (today,)).fetchall()
        return [dict(r) for r in rows]
