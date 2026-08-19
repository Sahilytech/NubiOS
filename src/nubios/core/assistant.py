from __future__ import annotations

import threading

from ..ai.provider import AIProvider
from ..ai.tts import NoOpTTS, TTSProvider
from ..automation.system import ApplicationRegistry, FileSearcher
from ..config.settings import Settings
from ..memory.database import Database
from ..memory.service import MemoryService
from ..tasks.manager import TaskManager
from .event_bus import EventBus
from .intent_engine import IntentEngine
from .logger import audit
from .permissions import Permission, PermissionManager


class Assistant:
    def __init__(
        self,
        settings: Settings,
        ai: AIProvider,
        event_bus: EventBus | None = None,
        tts: TTSProvider | None = None,
    ) -> None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings = settings
        self.db = Database(settings.data_dir / "nubios.sqlite3")
        self.intent = IntentEngine()
        self.permissions = PermissionManager()
        self.events = event_bus or EventBus()
        self.apps = ApplicationRegistry()
        self.files = FileSearcher(settings.allowed_directories)
        self.tasks = TaskManager(self.db)
        self.memory = MemoryService(self.db)
        self.ai = ai
        self.tts = tts or NoOpTTS()

    def handle(self, text: str) -> str:
        self.db.execute("INSERT INTO conversations(role, content) VALUES (?, ?)", ("user", text))
        intent = self.intent.parse(text)
        self.events.publish("assistant.command_received", intent=intent.name, confidence=intent.confidence)
        try:
            if intent.name == "open_application":
                response = self._launch(intent.value)
            elif intent.name == "find_file":
                response = self._find(intent.value)
            elif intent.name == "show_tasks":
                tasks = self.tasks.list()
                response = "\n".join(f"#{t['id']} [{t['status']}] {t['title']}" for t in tasks) or "No tasks yet."
            elif intent.name == "add_task":
                self._require(Permission.TASKS_WRITE)
                task_id = self.tasks.add(intent.value)
                self.events.publish("task.created", task_id=task_id)
                response = f"Task #{task_id} created: {intent.value}"
            elif intent.name == "complete_task":
                self._require(Permission.TASKS_WRITE)
                task_id = self._task_id(intent.value)
                self.tasks.complete(task_id)
                self.events.publish("task.completed", task_id=task_id)
                response = f"Task #{task_id} completed."
            elif intent.name == "remember":
                self._require(Permission.MEMORY_WRITE)
                memory_id = self.memory.remember(intent.value)
                self.events.publish("memory.created", memory_id=memory_id)
                response = "Saved locally."
            elif intent.name == "recall":
                self._require(Permission.MEMORY_READ)
                matches = self.memory.search(intent.value)
                response = "\n".join(matches) if matches else "I don't have a matching memory."
            else:
                response = self.ai.chat(text).text
        except PermissionError as exc:
            response = str(exc)
            self.events.publish("assistant.action_failed", reason=response)
        except Exception:
            response = "I couldn't complete that action. Check the local logs for details."
            self.events.publish("assistant.action_failed", reason="internal_error")
        self.db.execute("INSERT INTO conversations(role, content) VALUES (?, ?)", ("assistant", response))
        self._speak_async(response)
        audit(__import__("logging").getLogger("nubios"), "assistant.request", intent=intent.name, status="ok")
        self.events.publish("assistant.action_completed", intent=intent.name)
        return response

    def _speak_async(self, text: str) -> None:
        """Generate speech off the UI thread so cloud TTS never freezes NubiOS."""
        worker = threading.Thread(target=self._speak_safe, args=(text,), daemon=True, name="nubios-tts")
        worker.start()

    def _speak_safe(self, text: str) -> None:
        try:
            self.tts.speak(text)
            self.events.publish("assistant.tts_completed")
        except Exception as exc:
            audit(__import__("logging").getLogger("nubios"), "assistant.tts_failed", error=str(exc))
            self.events.publish("assistant.tts_failed", reason="tts_error")

    def _require(self, permission: Permission) -> None:
        if not self.permissions.check(permission):
            raise PermissionError(f"Permission denied: {permission}")

    def _launch(self, application: str) -> str:
        self._require(Permission.APPLICATIONS_LAUNCH)
        return self.apps.launch(application)

    def _find(self, query: str) -> str:
        self._require(Permission.FILESYSTEM_READ)
        if not self.settings.allowed_directories:
            return "No allowed directories are configured. Set NUBIOS_ALLOWED_DIRECTORIES first."
        matches = self.files.search(query)
        return "\n".join(str(p) for p in matches) if matches else "No matching files found."

    def _task_id(self, value: str) -> int:
        try:
            return int(value.lstrip("#").strip())
        except ValueError:
            for task in self.tasks.list():
                if task["title"].casefold() == value.casefold():
                    return int(task["id"])
        raise ValueError(f"Task not found: {value}")
