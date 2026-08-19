from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QPushButton,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget,
)

from ..ai.voice_controller import VoiceController
from ..core.assistant import Assistant


STYLE = """
QMainWindow { background: #fff7fb; color: #3b2635; }
QWidget { font-family: 'Segoe UI'; color: #3b2635; }
QLabel#brand { font-size: 27px; font-weight: 800; color: #d84f8f; padding: 8px 4px; }
QLabel#muted { color: #9b7b8d; }
QLabel#status { background: #ffe5f1; color: #c43d7d; border: 1px solid #f7bfd8; border-radius: 14px; padding: 7px 11px; font-weight: 700; }
QLabel#hero { background: #ffeaf4; border: 1px solid #f7c5dc; border-radius: 22px; padding: 18px; color: #8f3b68; }
QPushButton { background: #ffffff; border: 1px solid #f2c3d8; border-radius: 13px; padding: 10px 15px; font-weight: 650; color: #743b59; }
QPushButton:hover { background: #fff0f7; border-color: #e995ba; }
QPushButton#voice { background: #f28bb8; color: white; border: 1px solid #df6da2; border-radius: 15px; padding: 10px 18px; font-weight: 800; }
QPushButton#voice:hover { background: #e978aa; }
QPushButton#voice:disabled { background: #f3c4d8; color: #fff7fb; }
QLineEdit, QTextEdit, QListWidget { background: #ffffff; border: 1px solid #f0c8da; border-radius: 15px; padding: 11px; }
QTextEdit { selection-background-color: #f3a2c4; }
QListWidget::item { padding: 10px; border-radius: 10px; }
QListWidget::item:selected { background: #ffe5f1; color: #9b3f6d; }
"""


class VoiceWorker(QThread):
    """Run microphone capture and Whisper inference away from the UI thread."""

    completed = Signal(str)
    failed = Signal(str)

    def __init__(self, voice: VoiceController) -> None:
        super().__init__()
        self.voice = voice

    def run(self) -> None:
        try:
            self.completed.emit(self.voice.listen_once())
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, assistant: Assistant, voice: VoiceController | None = None) -> None:
        super().__init__()
        self.assistant = assistant
        self.voice = voice
        self.voice_worker: VoiceWorker | None = None
        self.setWindowTitle("NubiOS — Nubi Assistant")
        self.resize(1180, 760)
        self.setStyleSheet(STYLE)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        sidebar = QVBoxLayout()
        brand = QLabel("☁ NUBI\n   OS")
        brand.setObjectName("brand")
        sidebar.addWidget(brand)
        subtitle = QLabel("PRIVATE • LOCAL-FIRST")
        subtitle.setObjectName("muted")
        sidebar.addWidget(subtitle)
        self.nav = QListWidget()
        self.nav.addItems(["Dashboard", "Chat", "Tasks", "Memory", "Automation", "Plugins", "Settings"])
        self.nav.setFixedWidth(200)
        sidebar.addWidget(self.nav, 1)
        status = QLabel("●  NUBI ONLINE")
        status.setObjectName("status")
        sidebar.addWidget(status)
        layout.addLayout(sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.stack.addWidget(self.dashboard())
        self.stack.addWidget(self.chat())
        self.stack.addWidget(self.tasks_view())
        self.stack.addWidget(self.memory_view())
        self.stack.addWidget(self.automation_view())
        self.stack.addWidget(self.plugins_view())
        self.stack.addWidget(self.settings_view())
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.input.setFocus)
        QShortcut(QKeySequence("Ctrl+K"), self, activated=lambda: self.nav.setCurrentRow(1))
        self.setCentralWidget(root)

    def heading(self, title: str, subtitle: str) -> QVBoxLayout:
        layout = QVBoxLayout()
        h = QLabel(title)
        h.setStyleSheet("font-size:28px;font-weight:750;color:#6f3654;")
        layout.addWidget(h)
        s = QLabel(subtitle)
        s.setObjectName("muted")
        layout.addWidget(s)
        return layout

    def dashboard(self) -> QWidget:
        w = QWidget()
        l = self.heading("NubiOS", "Your little cloud assistant for a serious desktop workflow.")
        hero = QLabel("☁  Nubi is ready\n\nChat, use voice, manage tasks and control only the parts of Windows you explicitly allow.")
        hero.setObjectName("hero")
        hero.setWordWrap(True)
        l.addWidget(hero)
        stats = QHBoxLayout()
        for title, value in (("STATUS", "ONLINE"), ("TASKS", str(len(self.assistant.tasks.list()))), ("MEMORY", str(len(self.assistant.memory.all()))), ("AI", self.assistant.ai.name.upper())):
            box = QLabel(f"{title}\n{value}")
            box.setStyleSheet("background:#ffffff;border:1px solid #f0c8da;border-radius:16px;padding:18px;font-size:15px;")
            stats.addWidget(box)
        l.addLayout(stats)
        l.addWidget(QLabel("Recent activity"))
        l.addWidget(QLabel("Your local activity appears here as NubiOS actions are executed."))
        l.addStretch()
        w.setLayout(l)
        return w

    def chat(self) -> QWidget:
        w = QWidget()
        l = self.heading("Chat with Nubi", "Type a command or tap the pink microphone.")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        l.addWidget(self.output, 1)
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Say: Open VS Code, show my tasks, find my project...")
        send = QPushButton("Send")
        send.clicked.connect(self.send)
        self.input.returnPressed.connect(self.send)
        row.addWidget(self.input, 1)
        row.addWidget(send)
        self.voice_button = QPushButton("♡  Hablar con Nubi")
        self.voice_button.setObjectName("voice")
        self.voice_button.setToolTip("Graba hasta 6 segundos y transcribe con Whisper")
        self.voice_button.setEnabled(self.voice is not None and self.voice.microphone_available())
        self.voice_button.clicked.connect(self.listen)
        row.addWidget(self.voice_button)
        l.addLayout(row)
        w.setLayout(l)
        return w

    def send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.output.append(f"<b style='color:#c43d7d'>You</b>  {text}")
        self.input.setEnabled(False)
        try:
            response = self.assistant.handle(text)
            self.output.append(f"<b style='color:#d84f8f'>Nubi</b>  {response}<br>")
        finally:
            self.input.clear()
            self.input.setEnabled(True)
            self.input.setFocus()

    def listen(self) -> None:
        if self.voice is None or (self.voice_worker is not None and self.voice_worker.isRunning()):
            return
        self.voice_button.setEnabled(False)
        self.voice_button.setText("●  Escuchando...")
        self.input.setEnabled(False)
        self.voice_worker = VoiceWorker(self.voice)
        self.voice_worker.completed.connect(self.voice_completed)
        self.voice_worker.failed.connect(self.voice_failed)
        self.voice_worker.finished.connect(self.voice_finished)
        self.voice_worker.start()

    def voice_completed(self, text: str) -> None:
        if not text:
            self.output.append("<b style='color:#d84f8f'>Nubi</b>  No detecté ninguna frase.<br>")
            return
        self.output.append(f"<b style='color:#c43d7d'>You</b>  {text}")
        try:
            response = self.assistant.handle(text)
            self.output.append(f"<b style='color:#d84f8f'>Nubi</b>  {response}<br>")
        except Exception as exc:
            self.voice_failed(str(exc))

    def voice_failed(self, message: str) -> None:
        self.output.append(f"<b style='color:#d84f8f'>Nubi</b>  No pude usar el micrófono: {message}<br>")

    def voice_finished(self) -> None:
        self.voice_button.setText("♡  Hablar con Nubi")
        self.voice_button.setEnabled(self.voice is not None and self.voice.microphone_available())
        self.input.setEnabled(True)
        self.input.setFocus()
        self.voice_worker = None

    def tasks_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Tasks", "Lightweight local task management."); self.task_list = QListWidget(); l.addWidget(self.task_list, 1); refresh = QPushButton("Refresh"); refresh.clicked.connect(self.refresh_tasks); l.addWidget(refresh); self.refresh_tasks(); w.setLayout(l); return w

    def refresh_tasks(self) -> None:
        self.task_list.clear(); self.task_list.addItems([f"#{t['id']}  [{t['status']}]  {t['title']}" for t in self.assistant.tasks.list()])

    def memory_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Memory", "Stored locally. Reviewable and deletable by you."); m = QListWidget(); m.addItems(self.assistant.memory.all()); l.addWidget(m, 1); w.setLayout(l); return w

    def automation_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Automation", "Controlled application launching and bounded filesystem access."); l.addWidget(QLabel(f"Allowed folders: {len(self.assistant.settings.allowed_directories)}")); l.addWidget(QLabel("No arbitrary shell execution is exposed to the assistant.")); l.addStretch(); w.setLayout(l); return w

    def plugins_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Plugins", "Permission-declared extensions."); l.addWidget(QLabel("Plugin execution is intentionally limited until a sandboxed runtime is available.")); l.addStretch(); w.setLayout(l); return w

    def settings_view(self) -> QWidget:
        w = QWidget(); l = self.heading("Settings", "Configuration is controlled through environment variables and local settings."); l.addWidget(QLabel("NUBIOS_ALLOWED_DIRECTORIES\nNUBIOS_AI_PROVIDER\nNUBIOS_AI_MODEL\nNUBIOS_MOCK_AI\nNUBIOS_THEME\nNUBIOS_TTS\nNUBIOS_TTS_PROVIDER")); l.addStretch(); w.setLayout(l); return w
