from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QPushButton,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget,
)

from ..core.assistant import Assistant


STYLE = """
QMainWindow { background: #0b0e14; color: #edf2f7; }
QWidget { font-family: 'Segoe UI'; color: #edf2f7; }
QLabel#brand { font-size: 25px; font-weight: 700; padding: 8px 4px; }
QLabel#muted { color: #8e99aa; }
QPushButton { background: #171c27; border: 1px solid #283143; border-radius: 10px; padding: 10px 14px; }
QPushButton:hover { background: #202737; }
QLineEdit, QTextEdit, QListWidget { background: #111620; border: 1px solid #283143; border-radius: 12px; padding: 10px; }
QListWidget::item { padding: 9px; border-radius: 8px; }
QListWidget::item:selected { background: #252d3d; }
"""


class MainWindow(QMainWindow):
    def __init__(self, assistant: Assistant) -> None:
        super().__init__()
        self.assistant = assistant
        self.setWindowTitle("NubiOS")
        self.resize(1180, 760)
        self.setStyleSheet(STYLE)
        root = QWidget(); layout = QHBoxLayout(root); layout.setContentsMargins(18, 18, 18, 18)

        sidebar = QVBoxLayout(); brand = QLabel("NUBI\nOS"); brand.setObjectName("brand"); sidebar.addWidget(brand)
        subtitle = QLabel("LOCAL-FIRST ASSISTANT"); subtitle.setObjectName("muted"); sidebar.addWidget(subtitle)
        self.nav = QListWidget(); self.nav.addItems(["Dashboard", "Chat", "Tasks", "Memory", "Automation", "Plugins", "Settings"]); self.nav.setFixedWidth(190); sidebar.addWidget(self.nav, 1)
        status = QLabel("●  ONLINE"); status.setObjectName("muted"); sidebar.addWidget(status)
        layout.addLayout(sidebar)

        self.stack = QStackedWidget(); layout.addWidget(self.stack, 1)
        self.stack.addWidget(self.dashboard()); self.stack.addWidget(self.chat()); self.stack.addWidget(self.tasks_view()); self.stack.addWidget(self.memory_view()); self.stack.addWidget(self.automation_view()); self.stack.addWidget(self.plugins_view()); self.stack.addWidget(self.settings_view())
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex); self.nav.setCurrentRow(0)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.input.setFocus)
        QShortcut(QKeySequence("Ctrl+K"), self, activated=lambda: self.nav.setCurrentRow(1))
        self.setCentralWidget(root)

    def heading(self, title: str, subtitle: str) -> QVBoxLayout:
        layout = QVBoxLayout(); h = QLabel(title); h.setStyleSheet("font-size:28px;font-weight:650;"); layout.addWidget(h); s = QLabel(subtitle); s.setObjectName("muted"); layout.addWidget(s); return layout

    def dashboard(self) -> QWidget:
        w = QWidget(); l = self.heading("NubiOS", "Private desktop intelligence with controlled automation.");
        stats = QHBoxLayout()
        for title, value in (("STATUS", "ONLINE"), ("TASKS", str(len(self.assistant.tasks.list()))), ("MEMORY", str(len(self.assistant.memory.all()))), ("AI", self.assistant.ai.name.upper())):
            box = QLabel(f"{title}\n{value}"); box.setStyleSheet("background:#111620;border:1px solid #283143;border-radius:14px;padding:18px;font-size:15px;"); stats.addWidget(box)
        l.addLayout(stats); l.addWidget(QLabel("Recent activity")); l.addWidget(QLabel("Your local activity appears here as NubiOS actions are executed.")); l.addStretch();
        w.setLayout(l); return w

    def chat(self) -> QWidget:
        w = QWidget(); l = self.heading("Chat", "Talk to Nubi or use deterministic desktop commands."); self.output = QTextEdit(); self.output.setReadOnly(True); l.addWidget(self.output, 1)
        row = QHBoxLayout(); self.input = QLineEdit(); self.input.setPlaceholderText("Try: Open VS Code, show my tasks, find my project..."); send = QPushButton("Send"); send.clicked.connect(self.send); self.input.returnPressed.connect(self.send); row.addWidget(self.input, 1); row.addWidget(send); l.addLayout(row); w.setLayout(l); return w

    def send(self) -> None:
        text = self.input.text().strip()
        if not text: return
        self.output.append(f"<b>You</b>  {text}"); self.input.setEnabled(False)
        try: response = self.assistant.handle(text); self.output.append(f"<b>Nubi</b>  {response}<br>")
        finally: self.input.clear(); self.input.setEnabled(True); self.input.setFocus()

    def tasks_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Tasks", "Lightweight local task management."); self.task_list = QListWidget(); l.addWidget(self.task_list, 1); refresh = QPushButton("Refresh"); refresh.clicked.connect(self.refresh_tasks); l.addWidget(refresh); self.refresh_tasks(); w.setLayout(l); return w

    def refresh_tasks(self) -> None:
        self.task_list.clear(); self.task_list.addItems([f"#{t['id']}  [{t['status']}]  {t['title']}" for t in self.assistant.tasks.list()])

    def memory_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Memory", "Stored locally. Reviewable and deletable by the user."); m = QListWidget(); m.addItems(self.assistant.memory.all()); l.addWidget(m, 1); w.setLayout(l); return w

    def automation_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Automation", "Controlled application launching and bounded filesystem access."); l.addWidget(QLabel(f"Allowed folders: {len(self.assistant.settings.allowed_directories)}")); l.addWidget(QLabel("No arbitrary shell execution is exposed to the assistant.")); l.addStretch(); w.setLayout(l); return w

    def plugins_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Plugins", "Permission-declared extensions."); l.addWidget(QLabel("Plugin execution is intentionally limited until a sandboxed runtime is available.")); l.addStretch(); w.setLayout(l); return w

    def settings_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Settings", "Configuration is controlled through environment variables and local settings."); l.addWidget(QLabel("NUBIOS_ALLOWED_DIRECTORIES\nNUBIOS_AI_PROVIDER\nNUBIOS_AI_MODEL\nNUBIOS_MOCK_AI\nNUBIOS_THEME")); l.addStretch(); w.setLayout(l); return w
