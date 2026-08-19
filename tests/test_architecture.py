from pathlib import Path

from nubios.core.actions import Action, ActionExecutor, ActionResult
from nubios.core.event_bus import EventBus
from nubios.core.permissions import PermissionManager
from nubios.automation.files import SafeFileSystem
from nubios.plugins.manager import PluginManager


class DemoAction(Action):
    name = "demo"
    description = "demo action"
    required_permission = "tasks.write"

    def execute(self) -> ActionResult:
        return ActionResult(True, "ok")


def test_action_permission_gate():
    permissions = PermissionManager(); permissions.revoke("tasks.write")
    result = ActionExecutor(permissions).run(DemoAction())
    assert not result.success


def test_event_bus():
    bus = EventBus(); seen = []
    bus.subscribe("x", lambda payload: seen.append(payload["value"]))
    bus.publish("x", value=42)
    assert seen == [42]


def test_filesystem_boundary(tmp_path):
    allowed = tmp_path / "allowed"; allowed.mkdir(); (allowed / "project.txt").write_text("x")
    fs = SafeFileSystem((allowed,))
    assert fs.search("project") == [allowed / "project.txt"]
    try:
        fs.open_file(tmp_path / "outside.txt")
    except PermissionError:
        pass
    else:
        raise AssertionError("outside path must be rejected")


def test_plugin_manifest_discovery(tmp_path):
    plugin = tmp_path / "example"; plugin.mkdir()
    (plugin / "plugin.json").write_text('{"name":"example","version":"1.0.0","description":"x","author":"test","permissions":["tasks.read"]}')
    manager = PluginManager(tmp_path, PermissionManager())
    manifests = manager.discover()
    assert manifests[0].name == "example"
    assert manager.can_load("example")
