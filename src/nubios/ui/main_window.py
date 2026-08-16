from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QPushButton, QStackedWidget, QTextEdit, QVBoxLayout, QWidget

from ..core.assistant import Assistant


class MainWindow(QMainWindow):
    def __init__(self, assistant: Assistant) -> None:
        super().__init__()
        self.assistant = assistant
        self.setWindowTitle("NubiOS")
        self.resize(1100, 720)
        self.setStyleSheet("QMainWindow{background:#11131a;color:#f5f7fb} QLabel{color:#f5f7fb} QPushButton{padding:10px;border-radius:8px;background:#242938;color:white} QLineEdit,QTextEdit,QListWidget{background:#191c25;color:#f5f7fb;border:1px solid #303647;border-radius:8px;padding:8px}")
        root = QWidget(); layout = QHBoxLayout(root)
        sidebar = QVBoxLayout(); title = QLabel("NUBIOS"); title.setStyleSheet("font-size:24px;font-weight:700")
        sidebar.addWidget(title)
        self.nav = QListWidget(); self.nav.addItems(["Dashboard", "Chat", "Tasks", "Memory", "Settings"]); self.nav.setFixedWidth(180)
        sidebar.addWidget(self.nav); sidebar.addStretch(); sidebar.addWidget(QLabel("● LOCAL")); layout.addLayout(sidebar)
        self.stack = QStackedWidget(); layout.addWidget(self.stack, 1)
        self.stack.addWidget(self.dashboard()); self.stack.addWidget(self.chat()); self.stack.addWidget(self.tasks_view()); self.stack.addWidget(self.memory_view()); self.stack.addWidget(self.settings_view())
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex); self.nav.setCurrentRow(0)
        self.setCentralWidget(root)

    def dashboard(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel("Welcome to NubiOS")); l.addWidget(QLabel("Local-first desktop intelligence with controlled automation.")); l.addStretch(); return w

    def chat(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel("Nubi Chat")); self.output=QTextEdit(); self.output.setReadOnly(True); l.addWidget(self.output)
        row=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText("Ask Nubi something..."); send=QPushButton("Send"); send.clicked.connect(self.send); self.input.returnPressed.connect(self.send); row.addWidget(self.input); row.addWidget(send); l.addLayout(row); return w

    def send(self) -> None:
        text=self.input.text().strip()
        if not text:return
        self.output.append(f"You  ›  {text}"); response=self.assistant.handle(text); self.output.append(f"Nubi ›  {response}\n"); self.input.clear()

    def tasks_view(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel("Tasks")); self.task_list=QListWidget(); l.addWidget(self.task_list); refresh=QPushButton("Refresh"); refresh.clicked.connect(self.refresh_tasks); l.addWidget(refresh); return w

    def refresh_tasks(self) -> None:
        self.task_list.clear(); self.task_list.addItems([f"#{t['id']} [{t['status']}] {t['title']}" for t in self.assistant.tasks.list()])

    def memory_view(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel("Local Memory")); m=QListWidget(); m.addItems(self.assistant.memory.all()); l.addWidget(m); return w

    def settings_view(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel("Settings")); l.addWidget(QLabel("Configure NUBIOS_ALLOWED_DIRECTORIES in your environment or .env file.")); l.addStretch(); return w
