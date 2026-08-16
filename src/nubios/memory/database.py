from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class Database:
    """Small SQLite gateway. All application persistence goes through this boundary."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.initialize()

    def initialize(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'pending', priority TEXT NOT NULL DEFAULT 'normal', due_date TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, completed_at TEXT);
        CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, content TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'fact', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, event TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        """)
        self._ensure_column("tasks", "description", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("tasks", "priority", "TEXT NOT NULL DEFAULT 'normal'")
        self._ensure_column("tasks", "due_date", "TEXT")
        self._ensure_column("memories", "kind", "TEXT NOT NULL DEFAULT 'fact'")
        self.conn.commit()

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        columns = {row[1] for row in self.conn.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def close(self) -> None:
        self.conn.close()
