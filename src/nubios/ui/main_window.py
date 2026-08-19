from __future__ import annotations

from datetime import datetime
from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QStackedWidget, QTextEdit, QVBoxLayout, QWidget
)

from ..core.assistant import Assistant

PINK = "#ff4fa3"
CYAN = "#50eaff"
BG = "#05070d"
PANEL = "#0b101b"
PANEL_2 = "#101827"
TEXT = "#eaf7ff"
MUTED = "#71839a"


class HoloOrb(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(250, 250)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = self.rect().center()
        r = min(self.width(), self.height()) // 3
        for i in range(5):
            rr = r + i * 13
            pen = QPen(CYAN if i % 2 else PINK, 1)
            pen.setStyle(Qt.DashLine if i > 0 else Qt.SolidLine)
            p.setPen(pen)
            p.drawEllipse(c, rr, rr)
        p.setPen(QPen(CYAN, 2))
        p.drawEllipse(c, r // 2, r // 2)
        p.setPen(QPen(PINK, 1))
        p.drawLine(c.x() - r - 18, c.y(), c.x() + r + 18, c.y())
        p.drawLine(c.x(), c.y() - r - 18, c.x(), c.y() + r + 18)
        p.setPen(QPen(CYAN, 1))
        p.drawArc(c.x()-r-25, c.y()-r-25, 2*(r+25), 2*(r+25), 20*16, 115*16)
        p.drawArc(c.x()-r-35, c.y()-r-35, 2*(r+35), 2*(r+35), 205*16, 105*16)
        p.setPen(QPen(PINK, 2))
        p.drawPoint(c)


class MainWindow(QMainWindow):
    def __init__(self, assistant: Assistant) -> None:
        super().__init__()
        self.assistant = assistant
        self.last_response = ""
        self.setWindowTitle("NubiOS // Neural Desktop Interface")
        self.resize(1280, 820)
        self.setMinimumSize(980, 650)
        self.setStyleSheet(self.styles())
        root = QWidget(); layout = QHBoxLayout(root); layout.setContentsMargins(12,12,12,12); layout.setSpacing(12)
        layout.addWidget(self.sidebar()); self.stack = QStackedWidget(); layout.addWidget(self.stack, 1)
        self.stack.addWidget(self.dashboard()); self.stack.addWidget(self.chat()); self.stack.addWidget(self.tasks_view()); self.stack.addWidget(self.memory_view()); self.stack.addWidget(self.settings_view())
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex); self.nav.setCurrentRow(0); self.setCentralWidget(root)

    def styles(self):
        return f"""* {{ font-family:'Segoe UI'; color:{TEXT}; }} QMainWindow {{background:{BG};}} QFrame#sidebar,QFrame#card {{background:{PANEL};border:1px solid #17283a;border-radius:14px;}} QLabel#brand{{font-size:25px;font-weight:900;color:{CYAN};letter-spacing:2px;}} QLabel#cloud{{color:{PINK};font-size:11px;font-weight:800;letter-spacing:2px;}} QLabel#muted{{color:{MUTED};font-size:12px;}} QLabel#pageTitle{{font-size:29px;font-weight:900;color:{TEXT};letter-spacing:1px;}} QLabel#cardTitle{{font-size:12px;font-weight:800;color:{CYAN};letter-spacing:1px;}} QLabel#bigNumber{{color:{PINK};font-size:28px;font-weight:900;}} QListWidget{{background:transparent;border:none;outline:none;}} QListWidget::item{{padding:14px 12px;margin:3px 0;border-radius:8px;color:{MUTED};}} QListWidget::item:selected{{background:#101d2b;color:{CYAN};border:1px solid #21445a;}} QPushButton{{background:{PANEL_2};border:1px solid #1c3448;border-radius:8px;padding:10px 15px;font-weight:800;}} QPushButton:hover{{background:#142335;border-color:{CYAN};}} QPushButton#primary{{background:{PINK};color:#fff;border:1px solid {PINK};}} QLineEdit,QTextEdit{{background:#070b13;border:1px solid #1b3042;border-radius:10px;padding:12px;selection-background-color:{PINK};}} QLineEdit:focus,QTextEdit:focus{{border-color:{CYAN};}}"""

    def sidebar(self):
        frame=QFrame(); frame.setObjectName("sidebar"); frame.setFixedWidth(215); l=QVBoxLayout(frame); l.setContentsMargins(15,18,15,15); l.setSpacing(7)
        brand=QLabel("◈ NUBI"); brand.setObjectName("brand"); l.addWidget(brand); cloud=QLabel("N E U R A L   C O R E"); cloud.setObjectName("cloud"); l.addWidget(cloud); l.addSpacing(20)
        self.nav=QListWidget(); self.nav.addItems(["⌬   CORE","✦   CHAT","◫   TASKS","◌   MEMORY","⚙   CONFIG"]); l.addWidget(self.nav,1)
        status=QLabel("●  ONLINE // LOCAL CORE"); status.setStyleSheet(f"color:{CYAN};font-weight:800;padding:8px;font-size:10px;"); l.addWidget(status); footer=QLabel("NUBIWORKS\nNEURAL DESKTOP SYSTEM"); footer.setObjectName("muted"); l.addWidget(footer); return frame

    def header(self,title,subtitle):
        l=QVBoxLayout(); t=QLabel(title); t.setObjectName("pageTitle"); s=QLabel(subtitle); s.setObjectName("muted"); l.addWidget(t); l.addWidget(s); return l

    def card(self,title,value,subtitle):
        c=QFrame(); c.setObjectName("card"); l=QVBoxLayout(c); l.setContentsMargins(18,15,18,15); a=QLabel(title); a.setObjectName("cardTitle"); b=QLabel(value); b.setObjectName("bigNumber"); d=QLabel(subtitle); d.setObjectName("muted"); l.addWidget(a); l.addWidget(b); l.addWidget(d); return c

    def dashboard(self):
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(24,20,24,20); l.addLayout(self.header("NUBI // CORE","Neural desktop interface • systems nominal"));
        hero=QFrame(); hero.setObjectName("card"); hl=QHBoxLayout(hero); hl.setContentsMargins(25,20,25,20); left=QVBoxLayout(); title=QLabel("HOLOGRAPHIC ASSISTANT ONLINE"); title.setStyleSheet(f"font-size:22px;font-weight:900;color:{PINK};letter-spacing:1px;"); left.addWidget(title)
        text=QLabel("Voice, AI, files, tasks and memory connected through one cyberpunk control layer."); text.setObjectName("muted"); text.setWordWrap(True); left.addWidget(text); go=QPushButton("OPEN NEURAL CHAT  >>"); go.setObjectName("primary"); go.clicked.connect(lambda:self.nav.setCurrentRow(1)); left.addWidget(go); hl.addLayout(left,1); hl.addWidget(HoloOrb(),0); l.addWidget(hero,1); l.addSpacing(12)
        row=QHBoxLayout(); row.setSpacing(10); row.addWidget(self.card("TASKS",str(len(self.assistant.tasks.list())),"LOCAL DATABASE")); row.addWidget(self.card("MEMORY",str(len(self.assistant.memory.all())),"LOCAL MEMORY")); row.addWidget(self.card("AI CORE","LOCAL" if self.assistant.ai.__class__.__name__=="MockAIProvider" else "ONLINE","ACTIVE PROVIDER")); l.addLayout(row); return w

    def chat(self):
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(24,20,24,20); l.addLayout(self.header("NUBI // CHAT","Natural language command interface")); l.addSpacing(10)
        self.output=QTextEdit(); self.output.setReadOnly(True); self.output.setHtml(f"<p style='color:{MUTED}'>SYSTEM READY<br><span style='color:{CYAN}'>></span> Type a command or use the microphone to talk to Nubi.</p>"); l.addWidget(self.output,1)
        row=QHBoxLayout(); self.mic=QPushButton("◉  MICROPHONE"); self.mic.clicked.connect(self.listen); self.input=QLineEdit(); self.input.setPlaceholderText("> Enter command…"); send=QPushButton("EXECUTE  >>"); send.setObjectName("primary"); send.clicked.connect(self.send); self.input.returnPressed.connect(self.send); speak=QPushButton("VOICE OUT"); speak.clicked.connect(self.speak_last); row.addWidget(self.mic); row.addWidget(self.input,1); row.addWidget(speak); row.addWidget(send); l.addLayout(row); return w

    def listen(self):
        try:
            from ..voice.service import VoiceService
            voice = VoiceService(enabled=True, whisper_model=self.assistant.settings.whisper_model, tts_provider=self.assistant.settings.tts_provider, elevenlabs_api_key=self.assistant.settings.elevenlabs_api_key, elevenlabs_voice_id=self.assistant.settings.elevenlabs_voice_id)
            status = voice.status()
            if not status.available:
                self.output.append(f"<p style='color:{PINK}'>MIC ERROR // {escape(status.message)}</p>"); return
            self.mic.setText("◉  LISTENING…")
            self.output.append(f"<p style='color:{CYAN}'>MIC ACTIVE // processing audio…</p>")
            self.mic.setText("◉  MICROPHONE")
        except Exception as exc:
            self.mic.setText("◉  MICROPHONE")
            self.output.append(f"<p style='color:{PINK}'>MIC ERROR // {escape(str(exc))}</p>")

    def send(self):
        text=self.input.text().strip()
        if not text:return
        now=datetime.now().strftime("%H:%M"); self.output.append(f"<p><b style='color:{CYAN}'>YOU</b> <span style='color:{MUTED}'>{now}</span><br>{escape(text)}</p>"); self.last_response=self.assistant.handle(text); self.output.append(f"<p style='background:#0b1420;padding:10px;border-left:2px solid {PINK}'><b style='color:{PINK}'>NUBI</b><br>{escape(self.last_response).replace(chr(10),'<br>')}</p>"); self.input.clear(); self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def speak_last(self):
        if not self.last_response:return
        try:self.assistant.speak(self.last_response); self.output.append(f"<p style='color:{CYAN}'>VOICE OUT // TRANSMITTING…</p>")
        except Exception as exc:self.output.append(f"<p style='color:{PINK}'>VOICE ERROR // {escape(str(exc))}</p>")

    def tasks_view(self):
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(24,20,24,20); l.addLayout(self.header("NUBI // TASKS","Local execution queue")); self.task_list=QListWidget(); l.addWidget(self.task_list,1); b=QPushButton("REFRESH QUEUE"); b.clicked.connect(self.refresh_tasks); l.addWidget(b); self.refresh_tasks(); return w
    def refresh_tasks(self):
        self.task_list.clear(); [self.task_list.addItem(QListWidgetItem(f"  #{t['id']}   {t['title']}   •   {t['status']}")) for t in self.assistant.tasks.list()]
    def memory_view(self):
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(24,20,24,20); l.addLayout(self.header("NUBI // MEMORY","Encrypted-by-design local knowledge layer")); m=QListWidget(); m.addItems(self.assistant.memory.all() or ["NO MEMORY NODES YET"]); l.addWidget(m); return w
    def settings_view(self):
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(24,20,24,20); l.addLayout(self.header("NUBI // CONFIG","Core systems and peripherals")); c=QFrame(); c.setObjectName("card"); cl=QVBoxLayout(c); cl.setContentsMargins(22,22,22,22)
        for title,value in [("AI CORE",self.assistant.ai.__class__.__name__), ("DATA CORE",str(self.assistant.settings.data_dir)), ("VOICE INPUT","ENABLED" if self.assistant.settings.voice_enabled else "READY / ON DEMAND"), ("TTS CORE",self.assistant.settings.tts_provider.upper())]:
            row=QHBoxLayout(); a=QLabel(title); a.setObjectName("cardTitle"); b=QLabel(value); b.setObjectName("muted"); b.setAlignment(Qt.AlignRight); row.addWidget(a); row.addWidget(b,1); cl.addLayout(row)
        l.addWidget(c); l.addStretch(); return w
