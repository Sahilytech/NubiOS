from __future__ import annotations

from .database import Database


class MemoryService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def remember(self, content: str) -> int:
        return int(self.db.execute("INSERT INTO memories(content) VALUES (?)", (content,)).lastrowid)

    def search(self, query: str) -> list[str]:
        rows = self.db.execute("SELECT content FROM memories WHERE content LIKE ? ORDER BY id DESC", (f"%{query}%",)).fetchall()
        return [r["content"] for r in rows]

    def all(self) -> list[str]:
        return [r["content"] for r in self.db.execute("SELECT content FROM memories ORDER BY id DESC").fetchall()]
