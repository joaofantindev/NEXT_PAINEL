import sys
import random
import datetime

from PySide6.QtCore import Qt, QTimer, QProcess
from PySide6.QtGui import QFont, QColor, QPalette, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QSizePolicy, QPlainTextEdit,
)

BG       = "#000000"
PANEL    = "#0a0000"
PANEL2   = "#120000"
RED      = "#ff0033"
RED_DIM  = "#8a0018"
RED_FAINT= "#3a000c"
TEXT     = "#ff4d4d"
TEXT_DIM = "#a11a2a"
GREEN    = "#00ff88"

MONO = "JetBrains Mono, DejaVu Sans Mono, Consolas, monospace"


def scanline_widget(parent=None):
    w = QWidget(parent)
    w.setAttribute(Qt.WA_StyledBackground, True)
    return w


class HackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("root@matrix:~#")
        self.resize(1100, 720)
        self.setStyleSheet(self._stylesheet())
        self._proc = None
        self._build_ui()
        self._boot_sequence()

    def _stylesheet(self):
        return f"""
        QMainWindow, QWidget {{
            background-color: {BG};
            color: {TEXT};
            font-family: {MONO};
            font-size: 13px;
        }}
        QLabel#brand {{
            color: {RED};
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 4px;
        }}
        QLabel#sub {{
            color: {TEXT_DIM};
            font-size: 11px;
            letter-spacing: 2px;
        }}
        QLabel#status {{
            color: {RED};
            font-size: 11px;
            letter-spacing: 1px;
        }}
        QLabel#stat-val {{
            color: {RED};
            font-size: 20px;
            font-weight: bold;
        }}
        QLabel#stat-lbl {{
            color: {TEXT_DIM};
            font-size: 10px;
            letter-spacing: 2px;
        }}
        QFrame#panel {{
            background-color: {PANEL};
            border: 1px solid {RED_FAINT};
        }}
        QFrame#header {{
            background-color: {PANEL};
            border-bottom: 2px solid {RED};
        }}
        QListWidget {{
            background-color: {PANEL};
            border: 1px solid {RED_FAINT};
            outline: none;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 8px 6px;
            border-left: 3px solid transparent;
        }}
        QListWidget::item:selected {{
            background-color: {RED_FAINT};
            color: {RED};
            border-left: 3px solid {RED};
        }}
        QListWidget::item:hover {{
            background-color: {PANEL2};
        }}
        QPlainTextEdit, QTextEdit {{
            background-color: {PANEL};
            border: 1px solid {RED_FAINT};
            color: {TEXT};
            selection-background-color: {RED};
            selection-color: #000000;
            padding: 6px;
        }}
        QLineEdit {{
            background-color: {PANEL2};
            border: 1px solid {RED_DIM};
            padding: 8px;
            color: {TEXT};
            selection-background-color: {RED};
            selection-color: #000000;
        }}
        QLineEdit:focus {{
            border: 1px solid {RED};
        }}
        QPushButton {{
            background-color: {PANEL2};
            border: 1px solid {RED};
            color: {RED};
            padding: 9px 16px;
            letter-spacing: 1px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {RED};
            color: #000000;
        }}
        QPushButton:pressed {{
            background-color: {RED_DIM};
            color: #000000;
        }}
        QScrollBar:vertical {{
            background: {BG};
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {RED_DIM};
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {RED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: {BG};
        }}
        QScrollBar:horizontal {{
            background: {BG};
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {RED_DIM};
            min-width: 20px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: {BG};
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
        body.addWidget(self._main(), 1)

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
        title.setStyleSheet(f"color:{RED}; letter-spacing:2px; font-weight:bold;")
        v.addWidget(title)

        self.modules = QListWidget()
        mods = [
            ("RECON", "network scanning"),
            ("CRYPTO", "encrypt / decrypt"),
            ("PAYLOAD", "generate binaries"),
            ("LOGS", "system logs"),
            ("PROCESSES", "running tasks"),
            ("EXPLOITS", "vulnerability db"),
        ]
        for name, desc in mods:
            it = QListWidgetItem(f"  {name}")
            it.setToolTip(desc)
            it.setData(Qt.UserRole, name)
            self.modules.addItem(it)
        self.modules.setCurrentRow(0)
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
        t.setStyleSheet(f"color:{RED}; letter-spacing:2px; font-weight:bold;")
        bar.addWidget(t)
        bar.addStretch()
        self.status = QLabel("● ONLINE")
        self.status.setObjectName("status")
        bar.addWidget(self.status)
        v.addLayout(bar)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("monospace", 11))
        v.addWidget(self.console, 1)

        return f

    def _command_panel(self):
        f = self._panel()
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        t = QLabel("> COMMAND INPUT")
        t.setStyleSheet(f"color:{RED}; letter-spacing:2px; font-weight:bold;")
        v.addWidget(t)

        row = QHBoxLayout()
        row.setSpacing(8)
        prompt = QLabel("root@matrix:~#")
        prompt.setStyleSheet(f"color:{RED}; font-weight:bold;")
        self.input = QLineEdit()
        self.input.setPlaceholderText("type a command and press ENTER   (help)")
        self.input.returnPressed.connect(self._run_command)
        row.addWidget(prompt)
        row.addWidget(self.input, 1)
        v.addLayout(row)

        return f

    def _statusbar(self):
        f = QFrame()
        f.setObjectName("panel")
        f.setFixedHeight(26)
        h = QHBoxLayout(f)
        h.setContentsMargins(14, 0, 14, 0)
        self.barbase = QLabel("SESSION: 0x%08X" % random.getrandbits(32))
        self.barright = QLabel("MEM 512MB   |   PID 1337   |   TLS 1.3")
        for l in (self.barbase, self.barright):
            l.setStyleSheet(f"color:{TEXT_DIM}; font-size:10px; letter-spacing:1px;")
        h.addWidget(self.barbase)
        h.addStretch()
        h.addWidget(self.barright)
        return f

    # ---------- behavior ----------

    def log(self, text, color=None):
        color = color or TEXT
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.appendHtml(
            f'<span style="color:{RED_DIM}">[{ts}]</span> '
            f'<span style="color:{color}">{text}</span>'
        )

    def _boot_sequence(self):
        lines = [
            ("initializing kernel modules...", TEXT),
            ("mounting encrypted volume /dev/nexus7...", TEXT),
            ("handshake with relay node 104.21.x.x ... OK", GREEN),
            ("tunneling traffic through 3 proxies...", TEXT),
            ("biometric auth accepted.", GREEN),
            ("SYSTEM READY. awaiting input.", RED),
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
        self.log("running full system diagnostic...", RED)
        for i in range(1, 5):
            QTimer.singleShot(i * 300, lambda i=i: self.log(f"  check {i}/4 ... OK", GREEN))

    def _run_command(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.input.clear()
        self.log(f"root@matrix:~# {cmd}", RED)
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
                "exit / quit       close the interface",
            ]:
                self.log("  " + line, TEXT)
        elif c == "clear":
            self.console.clear()
        elif c == "scan":
            self.log("scanning subnet 10.0.0.0/24 ...", RED)
            self._scan(0)
        elif c.startswith("crypto"):
            data = cmd[6:].strip() or "null"
            enc = "".join(random.choice("0123456789ABCDEF") for _ in range(len(data) * 2))
            self.log(f"plain  : {data}", TEXT)
            self.log(f"cipher : {enc}", GREEN)
        elif c == "sysinfo":
            self.log(f"hostname : NEXUS-7", TEXT)
            self.log(f"os       : HackerOS 7.7 (x86_64)", TEXT)
            self.log(f"uptime   : {random.randint(2, 400)}d {random.randint(0,23)}h", TEXT)
            self.log(f"arch     : 64-bit, quantum", TEXT)
        elif c in ("exit", "quit"):
            self.close()
        elif c.startswith("run "):
            self._spawn_shell(cmd[4:])
        else:
            self.log(f"command not found: {cmd}", RED_DIM)

    def _scan(self, host):
        if host > 5:
            self.log("scan complete. 6 hosts up.", GREEN)
            return
        ip = f"10.0.0.{host + 10}"
        mac = ":".join(f"{random.randint(0,255):02X}" for _ in range(6))
        self.log(f"  {ip:<15} UP   {mac}   {random.choice(['ssh','http','https','ftp','smb'])}", GREEN)
        QTimer.singleShot(180, lambda: self._scan(host + 1))

    def _spawn_shell(self, command):
        self.log(f"executing: {command}", RED)
        self._proc = QProcess(self)
        self._proc.setProcessChannelMode(QProcess.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._read_proc)
        self._proc.finished.connect(lambda *_: self.log("process finished.", GREEN))
        self._proc.start("bash", ["-c", command])

    def _read_proc(self):
        data = bytes(self._proc.readAllStandardOutput()).decode(errors="replace")
        for line in data.splitlines():
            self.log(line, TEXT)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NEXUS-7")
    f = HackerGUI()
    f.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
