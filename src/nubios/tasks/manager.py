from __future__ import annotations

from .database import Database


class TaskManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, title: str) -> int:
        return int(self.db.execute("INSERT INTO tasks(title) VALUES (?)", (title,)).lastrowid)

    def list(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()]

    def complete(self, task_id: int) -> None:
        self.db.execute("UPDATE tasks SET status='completed', completed_at=CURRENT_TIMESTAMP WHERE id=?", (task_id,))
