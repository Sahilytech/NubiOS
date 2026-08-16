from pathlib import Path
from nubios.config.settings import Settings
from nubios.core.intent_engine import IntentEngine
from nubios.core.permissions import PermissionManager
from nubios.memory.database import Database
from nubios.memory.service import MemoryService
from nubios.tasks.manager import TaskManager


def test_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("NUBIOS_DATA_DIR", str(tmp_path / "data"))
    s = Settings.from_env()
    assert s.data_dir == (tmp_path / "data").resolve()


def test_intents():
    e = IntentEngine()
    assert e.parse("open VS Code").name == "open_application"
    assert e.parse("find my AsistenteONG project").name == "find_file"
    assert e.parse("add task: finish README").value == "finish README"
    assert e.parse("remember that I am working on NubiOS").name == "remember"


def test_database_tasks_memory(tmp_path):
    db = Database(tmp_path / "test.sqlite3")
    tasks = TaskManager(db); memories = MemoryService(db)
    task_id = tasks.add("Build NubiOS")
    memories.remember("NubiOS is my desktop assistant")
    assert tasks.list()[0]["id"] == task_id
    assert memories.search("NubiOS")
    db.close()


def test_permissions():
    p = PermissionManager()
    assert p.check("filesystem.read")
    p.revoke("filesystem.read")
    assert not p.check("filesystem.read")
    p.grant("filesystem.read")
    assert p.check("filesystem.read")
