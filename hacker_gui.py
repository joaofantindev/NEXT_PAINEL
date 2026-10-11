import sys
import random
import datetime

from PySide6.QtCore import Qt, QTimer, QProcess
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QStackedWidget, QPlainTextEdit,
)

THEMES = {
    "RED // Clássico": {
        "bg": "#000000", "panel": "#0a0000", "panel2": "#120000",
        "main": "#ff0033", "dim": "#8a0018", "faint": "#3a000c",
        "text": "#ff4d4d", "text_dim": "#a11a2a", "good": "#00ff88",
    },
    "GREEN // Fósforo": {
        "bg": "#000000", "panel": "#00120a", "panel2": "#001a10",
        "main": "#00ff88", "dim": "#00a356", "faint": "#003322",
        "text": "#33ffaa", "text_dim": "#0f8f5f", "good": "#a8ff3c",
    },
    "AMBER // Âmbar": {
        "bg": "#000000", "panel": "#120d00", "panel2": "#1a1500",
        "main": "#ffb000", "dim": "#b07a00", "faint": "#3a2a00",
        "text": "#ffc94d", "text_dim": "#a87f1a", "good": "#8cff66",
    },
    "CYAN // Gelo": {
        "bg": "#000000", "panel": "#000a12", "panel2": "#00121a",
        "main": "#00e5ff", "dim": "#009bb3", "faint": "#002b3a",
        "text": "#66f0ff", "text_dim": "#0f8ea3", "good": "#7dff9b",
    },
    "VIOLET // Estelar": {
        "bg": "#000000", "panel": "#0d0012", "panel2": "#15001a",
        "main": "#b026ff", "dim": "#7a12b0", "faint": "#2b0a3a",
        "text": "#d07cff", "text_dim": "#8b3db8", "good": "#66ffd9",
    },
}

FONT_CANDIDATES = [
    "JetBrains Mono", "Ubuntu Mono", "Source Code Pro", "Fira Code",
    "DejaVu Sans Mono", "Menlo", "Consolas", "Monospace", "Monofur",
    "Cascadia Mono", "Hack", "Courier New",
]


def available_mono_fonts():
    installed = set(QFontDatabase.families())
    ordered = [f for f in FONT_CANDIDATES if f in installed]
    ordered += [f for f in FONT_CANDIDATES if f not in installed]
    return ordered


class HackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("root@matrix:~#")
        self.resize(1120, 740)
        self.theme = dict(THEMES[list(THEMES)[0]])
        self.font_name = "DejaVu Sans Mono"
        self._proc = None
        self._build_ui()
        self._apply_theme()
        self._boot_sequence()

    # ---------- theming ----------

    def _apply_theme(self):
        self.setStyleSheet(self._stylesheet())
        self.console.setFont(QFont(self.font_name, 11))
        self.preview.setFont(QFont(self.font_name, 16))
        self.preview.setStyleSheet(
            f"background-color: {self.theme['panel']}; color: {self.theme['main']};"
            f"border: 1px solid {self.theme['dim']}; padding: 14px;"
        )
        self.preview_mini.setText(f"current: {self.font_name}")

    def _stylesheet(self):
        T = self.theme
        F = self.font_name
        return f"""
        QMainWindow, QWidget {{
            background-color: {T['bg']};
            color: {T['text']};
            font-family: "{F}";
            font-size: 13px;
        }}
        QLabel#brand {{
            color: {T['main']};
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 4px;
        }}
        QLabel#sub {{
            color: {T['text_dim']};
            font-size: 11px;
            letter-spacing: 2px;
        }}
        QLabel#status {{
            color: {T['main']};
            font-size: 11px;
            letter-spacing: 1px;
        }}
        QLabel#stat-val {{
            color: {T['main']};
            font-size: 20px;
            font-weight: bold;
        }}
        QLabel#stat-lbl {{
            color: {T['text_dim']};
            font-size: 10px;
            letter-spacing: 2px;
        }}
        QLabel#panel-title, QLabel#mod-title {{
            color: {T['main']};
            letter-spacing: 2px;
            font-weight: bold;
        }}
        QLabel#prompt {{
            color: {T['main']};
            font-weight: bold;
        }}
        QLabel#barbase, QLabel#barright {{
            color: {T['text_dim']};
            font-size: 10px;
            letter-spacing: 1px;
        }}
        QFrame#panel {{
            background-color: {T['panel']};
            border: 1px solid {T['faint']};
        }}
        QFrame#header {{
            background-color: {T['panel']};
            border-bottom: 2px solid {T['main']};
        }}
        QListWidget {{
            background-color: {T['panel']};
            border: 1px solid {T['faint']};
            outline: none;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 8px 6px;
            border-left: 3px solid transparent;
        }}
        QListWidget::item:selected {{
            background-color: {T['faint']};
            color: {T['main']};
            border-left: 3px solid {T['main']};
        }}
        QListWidget::item:hover {{
            background-color: {T['panel2']};
        }}
        QPlainTextEdit, QTextEdit {{
            background-color: {T['panel']};
            border: 1px solid {T['faint']};
            color: {T['text']};
            selection-background-color: {T['main']};
            selection-color: #000000;
            padding: 6px;
        }}
        QLineEdit {{
            background-color: {T['panel2']};
            border: 1px solid {T['dim']};
            padding: 8px;
            color: {T['text']};
            selection-background-color: {T['main']};
            selection-color: #000000;
        }}
        QLineEdit:focus {{
            border: 1px solid {T['main']};
        }}
        QPushButton {{
            background-color: {T['panel2']};
            border: 1px solid {T['main']};
            color: {T['main']};
            padding: 9px 16px;
            letter-spacing: 1px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {T['main']};
            color: #000000;
        }}
        QPushButton:pressed {{
            background-color: {T['dim']};
            color: #000000;
        }}
        QScrollBar:vertical {{
            background: {T['bg']};
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {T['dim']};
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {T['main']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: {T['bg']};
        }}
        QScrollBar:horizontal {{
            background: {T['bg']};
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {T['dim']};
            min-width: 20px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: {T['bg']};
        }}
        """

    def _panel(self):
        f = QFrame()
        f.setObjectName("panel")
        return f

    def _stat(self, parent_layout, label):
        box = QWidget()
        v = QVBoxLayout(box)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        val = QLabel("0")
        val.setObjectName("stat-val")
        lbl = QLabel(label)
        lbl.setObjectName("stat-lbl")
        v.addWidget(val)
        v.addWidget(lbl)
        parent_layout.addWidget(box)
        return val

    # ---------- layout ----------

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._header())

        body = QHBoxLayout()
        body.setContentsMargins(12, 12, 12, 8)
        body.setSpacing(12)
        outer.addLayout(body, 1)

        body.addWidget(self._sidebar(), 0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._main())
        self.stack.addWidget(self._custom_page())
        body.addWidget(self.stack, 1)

        outer.addWidget(self._statusbar())

    def _header(self):
        f = QFrame()
        f.setObjectName("header")
        f.setFixedHeight(70)
        h = QHBoxLayout(f)
        h.setContentsMargins(20, 8, 20, 8)

        left = QVBoxLayout()
        left.setSpacing(0)
        brand = QLabel("// NEXUS-7")
        brand.setObjectName("brand")
        sub = QLabel("SECURE TERMINAL INTERFACE v2.6")
        sub.setObjectName("sub")
        left.addWidget(brand)
        left.addWidget(sub)
        h.addLayout(left)
        h.addStretch()

        stats = QHBoxLayout()
        stats.setSpacing(34)
        self.stat_cpu = self._stat(stats, "CPU LOAD")
        self.stat_net = self._stat(stats, "PACKETS")
        self.stat_enc = self._stat(stats, "ENCRYPTED")
        h.addLayout(stats)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(0)
        self.clock = QLabel("00:00:00")
        self.clock.setObjectName("stat-val")
        self.clock.setAlignment(Qt.AlignRight)
        cl = QLabel("SYSTEM TIME")
        cl.setObjectName("stat-lbl")
        cl.setAlignment(Qt.AlignRight)
        clock_box.addWidget(self.clock)
        clock_box.addWidget(cl)
        h.addLayout(clock_box)

        return f

    def _sidebar(self):
        f = self._panel()
        f.setFixedWidth(230)
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 12, 10, 12)
        v.setSpacing(10)

        title = QLabel("> MODULES")
        title.setObjectName("mod-title")
        v.addWidget(title)

        self.modules = QListWidget()
        mods = [
            ("RECON", "network scanning"),
            ("CRYPTO", "encrypt / decrypt"),
            ("PAYLOAD", "generate binaries"),
            ("LOGS", "system logs"),
            ("PROCESSES", "running tasks"),
            ("EXPLOITS", "vulnerability db"),
            ("PERSONALIZAR", "themes and fonts"),
        ]
        for name, desc in mods:
            it = QListWidgetItem(f"  {name}")
            it.setToolTip(desc)
            it.setData(Qt.UserRole, name)
            self.modules.addItem(it)
        self.modules.currentRowChanged.connect(self._on_module)
        self.modules.setCurrentRow(0)
        self._active_module = "RECON"
        v.addWidget(self.modules, 1)

        btn = QPushButton("RUN DIAGNOSTIC")
        btn.clicked.connect(self._run_diagnostic)
        v.addWidget(btn)

        return f

    def _main(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(12)

        v.addWidget(self._console_panel(), 3)
        v.addWidget(self._command_panel(), 0)
        return w

    def _console_panel(self):
        f = self._panel()
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        bar = QHBoxLayout()
        t = QLabel("> OUTPUT STREAM")
        t.setObjectName("panel-title")
        bar.addWidget(t)
        bar.addStretch()
        self.status = QLabel("● ONLINE")
        self.status.setObjectName("status")
        bar.addWidget(self.status)
        v.addLayout(bar)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont(self.font_name, 11))
        v.addWidget(self.console, 1)

        return f

    def _command_panel(self):
        f = self._panel()
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        t = QLabel("> COMMAND INPUT")
        t.setObjectName("panel-title")
        v.addWidget(t)

        row = QHBoxLayout()
        row.setSpacing(8)
        prompt = QLabel("root@matrix:~#")
        prompt.setObjectName("prompt")
        self.input = QLineEdit()
        self.input.setPlaceholderText("type a command and press ENTER   (help)")
        self.input.returnPressed.connect(self._run_command)
        row.addWidget(prompt)
        row.addWidget(self.input, 1)
        v.addLayout(row)

        return f

    def _custom_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)

        outer.addWidget(self._custom_preview(), 0)
        outer.addWidget(self._custom_lists(), 1)
        outer.addWidget(self._custom_footer(), 0)
        return page

    def _custom_preview(self):
        f = self._panel()
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        t = QLabel("> PREVIEW")
        t.setObjectName("panel-title")
        v.addWidget(t)

        self.preview = QLabel("AaGgHh 0123 // NEXUS-7 → root@matrix:~#")
        self.preview.setFont(QFont(self.font_name, 16))
        self.preview_mini = QLabel(f"current: {self.font_name}")
        self.preview_mini.setStyleSheet("color:#666;" if False else "color:#888; font-size:10px;")
        v.addWidget(self.preview)
        v.addWidget(self.preview_mini)
        return f

    def _custom_lists(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        f1 = self._panel()
        v1 = QVBoxLayout(f1)
        v1.setContentsMargins(10, 10, 10, 10)
        v1.setSpacing(8)
        l1 = QLabel("> THEMES")
        l1.setObjectName("panel-title")
        v1.addWidget(l1)
        self.theme_list = QListWidget()
        for name in THEMES:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self.theme_list.addItem(item)
        self.theme_list.currentItemChanged.connect(self._on_theme)
        v1.addWidget(self.theme_list, 1)
        row.addWidget(f1, 1)

        f2 = self._panel()
        v2 = QVBoxLayout(f2)
        v2.setContentsMargins(10, 10, 10, 10)
        v2.setSpacing(8)
        l2 = QLabel("> FONTS")
        l2.setObjectName("panel-title")
        v2.addWidget(l2)
        self.font_list = QListWidget()
        for name in available_mono_fonts():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            item.setFont(QFont(name, 12))
            self.font_list.addItem(item)
        self.font_list.currentItemChanged.connect(self._on_font)
        v2.addWidget(self.font_list, 1)
        row.addWidget(f2, 1)

        holder = QWidget()
        holder.setLayout(row)
        return holder

    def _custom_footer(self):
        f = self._panel()
        h = QHBoxLayout(f)
        h.setContentsMargins(10, 8, 10, 8)

        hint = QLabel("seleção é aplicada na hora")
        hint.setObjectName("barbase")
        h.addWidget(hint)
        h.addStretch()

        restore = QPushButton("RESTAURAR PADRÃO")
        restore.clicked.connect(self._restore_defaults)
        h.addWidget(restore)
        return f

    def _statusbar(self):
        f = QFrame()
        f.setObjectName("panel")
        f.setFixedHeight(26)
        h = QHBoxLayout(f)
        h.setContentsMargins(14, 0, 14, 0)
        self.barbase = QLabel("SESSION: 0x%08X" % random.getrandbits(32))
        self.barbase.setObjectName("barbase")
        self.barright = QLabel("MEM 512MB   |   PID 1337   |   TLS 1.3")
        self.barright.setObjectName("barright")
        h.addWidget(self.barbase)
        h.addStretch()
        h.addWidget(self.barright)
        return f

    # ---------- customization ----------

    def _on_theme(self, current, previous):
        if current is None:
            return
        self.theme = dict(THEMES[current.data(Qt.UserRole)])
        self._apply_theme()

    def _on_font(self, current, previous):
        if current is None:
            return
        self.font_name = current.data(Qt.UserRole)
        self._apply_theme()

    def _restore_defaults(self):
        self.theme = dict(THEMES["RED // Clássico"])
        self.font_name = "DejaVu Sans Mono"
        for i in range(self.theme_list.count()):
            if self.theme_list.item(i).data(Qt.UserRole) == "RED // Clássico":
                self.theme_list.setCurrentRow(i)
        for i in range(self.font_list.count()):
            if self.font_list.item(i).data(Qt.UserRole) == "DejaVu Sans Mono":
                self.font_list.setCurrentRow(i)
        self._apply_theme()
        self.log("tema e fonte restaurados aos padrões.", self.theme["good"])

    # ---------- module navigation ----------

    def _on_module(self, row):
        item = self.modules.item(row)
        if item is None or not getattr(self, "stack", None):
            return
        name = item.data(Qt.UserRole)
        if name == "PERSONALIZAR":
            self.stack.setCurrentIndex(1)
            return
        self.stack.setCurrentIndex(0)
        if name != self._active_module:
            self._active_module = name
            self.log(f"módulo {name} carregado.", self.theme["good"])

    # ---------- behavior ----------

    def log(self, text, color=None):
        color = color or self.theme["text"]
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.appendHtml(
            f'<span style="color:{self.theme["dim"]}">[{ts}]</span> '
            f'<span style="color:{color}">{text}</span>'
        )

    def _boot_sequence(self):
        lines = [
            ("initializing kernel modules...", self.theme["text"]),
            ("mounting encrypted volume /dev/nexus7...", self.theme["text"]),
            ("handshake with relay node 104.21.x.x ... OK", self.theme["good"]),
            ("tunneling traffic through 3 proxies...", self.theme["text"]),
            ("biometric auth accepted.", self.theme["good"]),
            ("SYSTEM READY. awaiting input.", self.theme["main"]),
        ]
        self._pending = list(lines)
        self._push_boot()
        self._tick()

    def _push_boot(self):
        if self._pending:
            text, color = self._pending.pop(0)
            self.log(text, color)
            QTimer.singleShot(260, self._push_boot)

    def _tick(self):
        self._packets = getattr(self, "_packets", 12903)
        self._packets += random.randint(5, 240)
        self.stat_cpu.setText(f"{random.randint(8, 97)}%")
        self.stat_net.setText(f"{self._packets:,}")
        self.stat_enc.setText(f"{random.randint(2, 9)}.{random.randint(0,9)}GB")
        self.clock.setText(datetime.datetime.now().strftime("%H:%M:%S"))
        self.barright.setText(
            f"MEM {random.randint(320,780)}MB   |   PID {random.randint(1000,9999)}   |   TLS 1.3"
        )
        QTimer.singleShot(1000, self._tick)

    def _run_diagnostic(self):
        self.log("running full system diagnostic...", self.theme["main"])
        for i in range(1, 5):
            QTimer.singleShot(i * 300, lambda i=i: self.log(f"  check {i}/4 ... OK", self.theme["good"]))

    def _run_command(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.input.clear()
        self.log(f"root@matrix:~# {cmd}", self.theme["main"])
        self._execute(cmd)

    def _execute(self, cmd):
        c = cmd.lower()
        if c in ("help", "?"):
            for line in [
                "help              show this help",
                "clear             clear the console",
                "scan              simulate a network scan",
                "crypto <text>     mock encryption of text",
                "sysinfo           show fake system info",
                "custom            open the customization page",
                "exit / quit       close the interface",
            ]:
                self.log("  " + line, self.theme["text"])
        elif c == "clear":
            self.console.clear()
        elif c == "custom":
            self.stack.setCurrentIndex(1)
            self.modules.setCurrentRow(self.modules.count() - 1)
        elif c == "scan":
            self.log("scanning subnet 10.0.0.0/24 ...", self.theme["main"])
            self._scan(0)
        elif c.startswith("crypto"):
            data = cmd[6:].strip() or "null"
            enc = "".join(random.choice("0123456789ABCDEF") for _ in range(len(data) * 2))
            self.log(f"plain  : {data}", self.theme["text"])
            self.log(f"cipher : {enc}", self.theme["good"])
        elif c == "sysinfo":
            self.log(f"hostname : NEXUS-7", self.theme["text"])
            self.log(f"os       : HackerOS 7.7 (x86_64)", self.theme["text"])
            self.log(f"uptime   : {random.randint(2, 400)}d {random.randint(0,23)}h", self.theme["text"])
            self.log(f"arch     : 64-bit, quantum", self.theme["text"])
        elif c in ("exit", "quit"):
            self.close()
        elif c.startswith("run "):
            self._spawn_shell(cmd[4:])
        else:
            self.log(f"command not found: {cmd}", self.theme["dim"])

    def _scan(self, host):
        if host > 5:
            self.log("scan complete. 6 hosts up.", self.theme["good"])
            return
        ip = f"10.0.0.{host + 10}"
        mac = ":".join(f"{random.randint(0,255):02X}" for _ in range(6))
        self.log(f"  {ip:<15} UP   {mac}   {random.choice(['ssh','http','https','ftp','smb'])}", self.theme["good"])
        QTimer.singleShot(180, lambda: self._scan(host + 1))

    def _spawn_shell(self, command):
        self.log(f"executing: {command}", self.theme["main"])
        self._proc = QProcess(self)
        self._proc.setProcessChannelMode(QProcess.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._read_proc)
        self._proc.finished.connect(lambda *_: self.log("process finished.", self.theme["good"]))
        self._proc.start("bash", ["-c", command])

    def _read_proc(self):
        data = bytes(self._proc.readAllStandardOutput()).decode(errors="replace")
        for line in data.splitlines():
            self.log(line, self.theme["text"])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NEXUS-7")
    f = HackerGUI()
    f.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()