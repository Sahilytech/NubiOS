from __future__ import annotations

from datetime import datetime
from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.assistant import Assistant


PINK = "#ff6fae"
PINK_DARK = "#e94f91"
BG = "#0d0b12"
PANEL = "#17131d"
PANEL_2 = "#211a27"
TEXT = "#fff7fb"
MUTED = "#a99baa"


class MainWindow(QMainWindow):
    def __init__(self, assistant: Assistant) -> None:
        super().__init__()
        self.assistant = assistant
        self.setWindowTitle("NubiOS — Your desktop companion")
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)
        self.setStyleSheet(self.styles())

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        sidebar = self.sidebar()
        layout.addWidget(sidebar)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.stack.addWidget(self.dashboard())
        self.stack.addWidget(self.chat())
        self.stack.addWidget(self.tasks_view())
        self.stack.addWidget(self.memory_view())
        self.stack.addWidget(self.settings_view())
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self.setCentralWidget(root)

    def styles(self) -> str:
        return f"""
        * {{ font-family: 'Segoe UI'; color: {TEXT}; }}
        QMainWindow {{ background: {BG}; }}
        QFrame#sidebar, QFrame#card {{ background: {PANEL}; border: 1px solid #2c2331; border-radius: 20px; }}
        QLabel#brand {{ color: {TEXT}; font-size: 25px; font-weight: 800; }}
        QLabel#cloud {{ color: {PINK}; font-size: 14px; font-weight: 700; }}
        QLabel#muted {{ color: {MUTED}; font-size: 13px; }}
        QLabel#pageTitle {{ font-size: 30px; font-weight: 800; }}
        QLabel#cardTitle {{ font-size: 17px; font-weight: 700; }}
        QLabel#bigNumber {{ color: {PINK}; font-size: 30px; font-weight: 800; }}
        QListWidget {{ background: transparent; border: none; outline: none; }}
        QListWidget::item {{ padding: 13px 14px; margin: 3px 0; border-radius: 12px; color: {MUTED}; }}
        QListWidget::item:selected {{ background: #30202c; color: {TEXT}; border: 1px solid #4a3042; }}
        QPushButton {{ background: {PANEL_2}; border: 1px solid #3b2b3a; border-radius: 12px; padding: 11px 16px; font-weight: 700; }}
        QPushButton:hover {{ background: #302333; border-color: #654158; }}
        QPushButton#primary {{ background: {PINK}; color: white; border: none; }}
        QPushButton#primary:hover {{ background: {PINK_DARK}; }}
        QLineEdit, QTextEdit {{ background: #120f17; border: 1px solid #342735; border-radius: 14px; padding: 12px; selection-background-color: {PINK}; }}
        QLineEdit:focus, QTextEdit:focus {{ border-color: #b94d80; }}
        QScrollArea {{ border: none; background: transparent; }}
        """

    def sidebar(self) -> QFrame:
        frame = QFrame(); frame.setObjectName("sidebar"); frame.setFixedWidth(230)
        l = QVBoxLayout(frame); l.setContentsMargins(18, 20, 18, 18); l.setSpacing(8)
        brand = QLabel("☁ NUBI"); brand.setObjectName("brand"); l.addWidget(brand)
        cloud = QLabel("NubiOS • local-first assistant"); cloud.setObjectName("cloud"); l.addWidget(cloud)
        l.addSpacing(20)
        self.nav = QListWidget(); self.nav.addItems(["⌂   Dashboard", "✦   Chat with Nubi", "✓   Tasks", "◌   Memory", "⚙   Settings"])
        l.addWidget(self.nav, 1)
        status = QLabel("●  SYSTEM ONLINE"); status.setStyleSheet(f"color:{PINK}; font-weight:700; padding:8px;")
        l.addWidget(status)
        footer = QLabel("NubiWorks\nPersonal desktop intelligence"); footer.setObjectName("muted"); l.addWidget(footer)
        return frame

    def header(self, title: str, subtitle: str) -> QVBoxLayout:
        l = QVBoxLayout(); t = QLabel(title); t.setObjectName("pageTitle"); s = QLabel(subtitle); s.setObjectName("muted"); l.addWidget(t); l.addWidget(s); return l

    def card(self, title: str, value: str, subtitle: str) -> QFrame:
        c = QFrame(); c.setObjectName("card"); l = QVBoxLayout(c); l.setContentsMargins(20, 18, 20, 18)
        a = QLabel(title); a.setObjectName("cardTitle"); b = QLabel(value); b.setObjectName("bigNumber"); d = QLabel(subtitle); d.setObjectName("muted")
        l.addWidget(a); l.addWidget(b); l.addWidget(d); return c

    def dashboard(self) -> QWidget:
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(28, 24, 28, 24)
        l.addLayout(self.header("Good to see you.", "Nubi is ready to help with your desktop, projects and tasks.")); l.addSpacing(22)
        hero = QFrame(); hero.setObjectName("card"); hl = QHBoxLayout(hero); hl.setContentsMargins(24, 22, 24, 22)
        left = QVBoxLayout(); title = QLabel("☁  Hi, I'm Nubi"); title.setStyleSheet(f"font-size:25px;font-weight:800;color:{PINK};")
        left.addWidget(title); text = QLabel("Ask me to open apps, find files, manage tasks, remember things, or chat with your AI provider."); text.setObjectName("muted"); text.setWordWrap(True); left.addWidget(text)
        go = QPushButton("Start a conversation  →"); go.setObjectName("primary"); go.clicked.connect(lambda: self.nav.setCurrentRow(1)); left.addWidget(go); hl.addLayout(left, 1)
        orb = QLabel("☁"); orb.setAlignment(Qt.AlignCenter); orb.setStyleSheet(f"font-size:82px;color:{PINK};background:#291a26;border-radius:70px;min-width:140px;min-height:140px;"); hl.addWidget(orb)
        l.addWidget(hero); l.addSpacing(18)
        row = QHBoxLayout(); row.setSpacing(14)
        row.addWidget(self.card("TASKS", str(len(self.assistant.tasks.list())), "saved locally"))
        row.addWidget(self.card("MEMORY", str(len(self.assistant.memory.all())), "local memories"))
        row.addWidget(self.card("AI MODE", "LOCAL" if self.assistant.ai.__class__.__name__ == "MockAIProvider" else "ONLINE", "current provider"))
        l.addLayout(row); l.addStretch(); return w

    def chat(self) -> QWidget:
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(28, 24, 28, 24)
        l.addLayout(self.header("Chat with Nubi", "Your commands and conversations stay in NubiOS local history.")); l.addSpacing(12)
        self.output = QTextEdit(); self.output.setReadOnly(True); self.output.setPlaceholderText("Nubi will reply here…")
        self.output.setHtml(f"<p style='color:{MUTED}'>Start with <b style='color:{PINK}'>“open VS Code”</b>, <b style='color:{PINK}'>“show my tasks”</b>, or just say hi.</p>")
        l.addWidget(self.output, 1)
        row = QHBoxLayout(); self.input = QLineEdit(); self.input.setPlaceholderText("Talk to Nubi…"); send = QPushButton("Send  ↗"); send.setObjectName("primary"); send.clicked.connect(self.send); self.input.returnPressed.connect(self.send); row.addWidget(self.input, 1); row.addWidget(send); l.addLayout(row)
        return w

    def send(self) -> None:
        text = self.input.text().strip()
        if not text: return
        now = datetime.now().strftime("%H:%M")
        self.output.append(f"<p><b style='color:{PINK}'>You</b> <span style='color:{MUTED}'>{now}</span><br>{escape(text)}</p>")
        response = self.assistant.handle(text)
        self.output.append(f"<p style='background:#1b1520;padding:10px;border-radius:10px'><b style='color:{PINK}'>Nubi</b><br>{escape(response).replace(chr(10), '<br>')}</p>")
        self.input.clear()
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def tasks_view(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(28,24,28,24); l.addLayout(self.header("Tasks", "Keep your projects moving without leaving NubiOS.")); l.addSpacing(12)
        self.task_list=QListWidget(); l.addWidget(self.task_list,1); refresh=QPushButton("Refresh tasks"); refresh.clicked.connect(self.refresh_tasks); l.addWidget(refresh); self.refresh_tasks(); return w

    def refresh_tasks(self) -> None:
        self.task_list.clear();
        for t in self.assistant.tasks.list():
            item=QListWidgetItem(f"  #{t['id']}   {t['title']}   •   {t['status']}"); self.task_list.addItem(item)

    def memory_view(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(28,24,28,24); l.addLayout(self.header("Local Memory", "Things Nubi has been asked to remember.")); l.addSpacing(12)
        m=QListWidget(); m.addItems(self.assistant.memory.all() or ["No memories yet."]); l.addWidget(m); return w

    def settings_view(self) -> QWidget:
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(28,24,28,24); l.addLayout(self.header("Settings", "Configure NubiOS without changing the core app.")); l.addSpacing(12)
        c=QFrame(); c.setObjectName("card"); cl=QVBoxLayout(c); cl.setContentsMargins(22,22,22,22)
        for title, value in [("AI provider", self.assistant.ai.__class__.__name__), ("Data directory", str(self.assistant.settings.data_dir)), ("Allowed directories", str(len(self.assistant.settings.allowed_directories))), ("Voice", "Enabled" if self.assistant.settings.voice_enabled else "Disabled")]:
            row=QHBoxLayout(); a=QLabel(title); a.setObjectName("cardTitle"); b=QLabel(value); b.setObjectName("muted"); b.setAlignment(Qt.AlignRight); row.addWidget(a); row.addWidget(b,1); cl.addLayout(row)
        l.addWidget(c); l.addStretch(); return w
