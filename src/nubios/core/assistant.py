from __future__ import annotations

import logging

from ..ai.provider import AIProvider
from ..automation.system import ApplicationRegistry, FileSearcher
from ..config.settings import Settings
from .intent_engine import IntentEngine
from .permissions import PermissionManager, Permission
from ..memory.database import Database
from ..memory.service import MemoryService
from ..tasks.manager import TaskManager


class Assistant:
    def __init__(self, settings: Settings, ai: AIProvider) -> None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings = settings
        self.db = Database(settings.data_dir / "nubios.sqlite3")
        self.intent = IntentEngine()
        self.permissions = PermissionManager()
        self.apps = ApplicationRegistry()
        self.files = FileSearcher(settings.allowed_directories)
        self.tasks = TaskManager(self.db)
        self.memory = MemoryService(self.db)
        self.ai = ai
        self.log = logging.getLogger("nubios.assistant")

    def handle(self, text: str) -> str:
        self.db.execute("INSERT INTO conversations(role, content) VALUES (?, ?)", ("user", text))
        intent = self.intent.parse(text)
        try:
            if intent.name == "open_application":
                if not self.permissions.check(Permission.APPLICATIONS_LAUNCH):
                    return "Permission denied: applications.launch"
                response = self.apps.launch(intent.value)
            elif intent.name == "find_file":
                if not self.permissions.check(Permission.FILESYSTEM_READ):
                    return "Permission denied: filesystem.read"
                if not self.settings.allowed_directories:
                    response = "No allowed directories are configured. Set NUBIOS_ALLOWED_DIRECTORIES first."
                else:
                    matches = self.files.search(intent.value)
                    response = "\n".join(str(p) for p in matches) if matches else "No matching files found."
            elif intent.name == "show_tasks":
                tasks = self.tasks.list()
                response = "\n".join(f"#{t['id']} [{t['status']}] {t['title']}" for t in tasks) or "No tasks yet."
            elif intent.name == "add_task":
                if not self.permissions.check(Permission.TASKS_WRITE):
                    return "Permission denied: tasks.write"
                task_id = self.tasks.add(intent.value)
                response = f"Task #{task_id} created: {intent.value}"
            elif intent.name == "remember":
                if not self.permissions.check(Permission.MEMORY_WRITE):
                    return "Permission denied: memory.write"
                self.memory.remember(intent.value)
                response = "I'll remember that locally."
            elif intent.name == "recall":
                if not self.permissions.check(Permission.MEMORY_READ):
                    return "Permission denied: memory.read"
                matches = self.memory.search(intent.value)
                response = "\n".join(matches) if matches else "I don't have a matching memory."
            else:
                response = self.ai.chat(text)
        except Exception:
            self.log.exception("assistant_action_failed")
            response = "I couldn't complete that action. Check the local logs for details."
        self.db.execute("INSERT INTO conversations(role, content) VALUES (?, ?)", ("assistant", response))
        self.db.execute("INSERT INTO audit_log(event, details) VALUES (?, ?)", (intent.name, response[:500]))
        return response
