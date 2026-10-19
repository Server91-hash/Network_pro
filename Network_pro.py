"""
Network Tools Pro v1.0  -  native desktop app (Python + PySide6 / Qt)
Monitor . Diagnose . Troubleshoot

Install:   pip install PySide6 psutil
Run:       python network_tools_pro.py
(Run as Administrator / root to see process names for every port.)
"""
import csv
import datetime
import ipaddress
import platform
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QComboBox, QFileDialog, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
    QAbstractItemView, QCheckBox,
)

SYSTEM = platform.system()
IS_WIN = SYSTEM == "Windows"
NOWIN = subprocess.CREATE_NO_WINDOW if IS_WIN else 0

# ----------------------------------------------------------------------------
# Theme
# ----------------------------------------------------------------------------
QSS = """
* { font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif; font-size: 13px; color: #e6edff; }
QMainWindow, #root { background: #070d1c; }
#header { background: #08101f; border-bottom: 1px solid #14244a; }
#appTitle { font-size: 24px; font-weight: 600; color: #ffffff; }
#appSub { color: #9fb3dd; font-size: 13px; }
#version { color: #6b7fa8; font-size: 12px; }
#statusPill { background: #0b1530; border: 1px solid #1c2c55; border-radius: 8px; }
#sidebar { background: #08101f; border-right: 1px solid #14244a; }
QPushButton#nav { text-align: left; padding: 11px 16px; border: none; border-radius: 8px;
                  background: transparent; color: #c9d6f5; font-size: 14px; }
QPushButton#nav:hover { background: #101c3a; }
QPushButton#nav:checked { background: #14295a; color: #ffffff; }
#card { background: #0b1429; border: 1px solid #1b2c58; border-radius: 12px; }
#cardTitle { font-size: 16px; font-weight: 600; color: #ffffff; }
#key { color: #b8c6e6; }
#valBlue { color: #38bdf8; font-weight: 700; font-size: 16px; }
#valGreen { color: #4ade80; }
#valPurple { color: #a78bfa; font-weight: 700; }
#live { color: #4ade80; }
QPushButton#copy { background: transparent; border: none; color: #9fb3dd; font-size: 15px; }
QPushButton#copy:hover { color: #ffffff; }
QPushButton#qa { padding: 16px; border-radius: 8px; font-size: 14px; }
QPushButton#qaGreen  { background:#0b3b1f; border:1px solid #16a34a; color:#4ade80; }
QPushButton#qaRed    { background:#3b0b15; border:1px solid #ef4444; color:#ff6b7a; }
QPushButton#qaBlue   { background:#0b2a55; border:1px solid #2563eb; color:#7cc0ff; }
QPushButton#qaPurple { background:#2a0b55; border:1px solid #9333ea; color:#c9a0ff; }
QPushButton#qaGreen:hover  { background:#0f4f29; }
QPushButton#qaRed:hover    { background:#4f0f1c; }
QPushButton#qaBlue:hover   { background:#0f3a73; }
QPushButton#qaPurple:hover { background:#380f73; }
QLineEdit, QSpinBox, QComboBox { background: #0a1226; border: 1px solid #22345f; border-radius: 6px;
                                 padding: 6px 8px; font-size: 14px; selection-background-color: #1d4ed8; }
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid #3b82f6; }
QComboBox QAbstractItemView { background:#0a1226; border:1px solid #22345f; selection-background-color:#1d4ed8; }
QSpinBox::up-button, QSpinBox::down-button { width: 16px; background:#14244a; border:none; }
QPushButton#start { background: #1d5fd6; border: 1px solid #3b82f6; border-radius: 6px; padding: 11px; font-size: 15px; }
QPushButton#start:hover { background: #2a6fe8; }
QPushButton#small { background: #0a1226; border: 1px solid #22345f; border-radius: 6px; padding: 6px 18px; }
QPushButton#small:hover { border-color: #3b82f6; }
QPushButton#total { background:#0e5e8a; border:none; border-radius: 14px; padding: 6px 14px; color:#e8f7ff; }
QTableWidget { background: #0a1226; border: none; gridline-color: transparent; outline: 0;
               selection-background-color: #14295a; font-size: 13px; }
QTableWidget::item { padding: 4px 6px; border-bottom: 1px solid #101a34; }
QHeaderView::section { background: #0b1429; color: #dbe6ff; border: none; border-bottom: 1px solid #22345f;
                       padding: 8px 6px; font-weight: 600; }
QPlainTextEdit, QTextEdit { background: #070d1c; border: 1px solid #1b2c58; border-radius: 8px; padding: 6px;
                            font-family: Consolas, 'DejaVu Sans Mono', monospace; font-size: 12px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: transparent; padding: 9px 14px; color: #c9d6f5; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { background: #123a82; color: #ffffff; border: 1px solid #2563eb; border-radius: 6px; }
QTabBar::tab:hover:!selected { color: #ffffff; }
QPushButton#shortcut { text-align: left; padding: 8px 10px; background:#0a1226; border:1px solid #1b2c58;
                       border-radius: 8px; font-size: 12px; color:#9fb3dd; }
QPushButton#shortcut:hover { border-color:#3b82f6; background:#0e1a38; }
QCheckBox { spacing: 8px; color: #c9d6f5; }
QScrollBar:vertical { background: #0a1226; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #26407a; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
"""


# ----------------------------------------------------------------------------
# Network helpers (all standard library + psutil)
# ----------------------------------------------------------------------------
def human_bytes(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # no packet is actually sent
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def default_gateway():
    try:
        if IS_WIN:
            out = subprocess.run(["route", "print", "0.0.0.0"], capture_output=True, text=True,
                                 creationflags=NOWIN, timeout=6).stdout
            m = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", out)
        elif SYSTEM == "Darwin":
            out = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True,
                                 timeout=6).stdout
            m = re.search(r"gateway:\s*(\S+)", out)
        else:
            out = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True,
                                 timeout=6).stdout
            m = re.search(r"default via (\S+)", out)
        return m.group(1) if m else "N/A"
    except Exception:
        return "N/A"


def gather_info():
    d = {"lan": local_ip(), "iface": "N/A", "mask": "N/A", "mac": "N/A", "ipv6": "N/A",
         "status": "Disconnected", "speed": "N/A", "sent": "N/A", "recv": "N/A",
         "gateway": default_gateway()}
    for name, addrs in psutil.net_if_addrs().items():
        if any(a.family == socket.AF_INET and a.address == d["lan"] for a in addrs):
            d["iface"] = name
            for a in addrs:
                if a.family == socket.AF_INET and a.address == d["lan"]:
                    d["mask"] = a.netmask or "N/A"
                elif a.family == psutil.AF_LINK:
                    d["mac"] = a.address.replace("-", ":").upper()
                elif a.family == socket.AF_INET6 and d["ipv6"] == "N/A":
                    d["ipv6"] = a.address.split("%")[0]
            st = psutil.net_if_stats().get(name)
            if st:
                d["status"] = "Connected" if st.isup else "Disconnected"
                d["speed"] = f"{st.speed} Mbps" if st.speed else "N/A"
            io = psutil.net_io_counters(pernic=True).get(name)
            if io:
                d["sent"], d["recv"] = human_bytes(io.bytes_sent), human_bytes(io.bytes_recv)
            break
    return d


def gather_ports():
    rows, seen, names = [], set(), {}
    try:
        conns = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        conns = []
    for c in conns:
        if not c.laddr:
            continue
        is_tcp = c.type == socket.SOCK_STREAM
        if is_tcp and c.status != psutil.CONN_LISTEN:
            continue
        proto = "TCP" if is_tcp else "UDP"
        key = (proto, c.laddr.ip, c.laddr.port, c.pid)
        if key in seen:
            continue
        seen.add(key)
        pid = c.pid or 0
        if pid not in names:
            try:
                names[pid] = psutil.Process(pid).name() if pid else "System"
            except Exception:
                names[pid] = "-"
        rows.append((proto, c.laddr.ip, c.laddr.port, "LISTENING", names[pid], pid))
    rows.sort(key=lambda r: (r[0], r[2]))
    return rows


def fetch_public_ip():
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                ip = r.read().decode().strip()
                ipaddress.ip_address(ip)
                return ip
        except Exception:
            continue
    return "Unavailable"


# ----------------------------------------------------------------------------
# Tool implementations (run in worker threads)
# ----------------------------------------------------------------------------
class Ctx:
    def __init__(self, panel):
        self.panel, self.stop, self.proc = panel, threading.Event(), None

    def emit(self, text):
        self.panel.line.emit(text)


def run_cmd(cmd, ctx):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         errors="replace", creationflags=NOWIN)
    ctx.proc = p
    for line in p.stdout:
        if ctx.stop.is_set():
            break
        ctx.emit(line.rstrip())
    if ctx.stop.is_set():
        try:
            p.terminate()
        except Exception:
            pass
        ctx.emit("\n[stopped]")
    p.wait()


def do_ping(p, ctx):
    host, count, to = p["host"].strip(), p["count"], p["timeout"]
    if IS_WIN:
        cmd = ["ping", "-n", str(count), "-w", str(to), host]
    elif SYSTEM == "Darwin":
        cmd = ["ping", "-c", str(count), "-W", str(to), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(max(1, to // 1000)), host]
    run_cmd(cmd, ctx)


def do_telnet(p, ctx):
    host, port, to = p["host"].strip(), p["port"], p["timeout"]
    ctx.emit(f"Connecting to {host}:{port} ...")
    t0 = time.time()
    try:
        with socket.create_connection((host, port), timeout=to / 1000) as s:
            ms = int((time.time() - t0) * 1000)
            ctx.emit(f"SUCCESS: connected in {ms} ms  ->  port {port} is OPEN")
            s.settimeout(1.5)
            try:
                data = s.recv(1024)
                if data:
                    ctx.emit("Banner: " + data.decode(errors="replace").strip())
            except socket.timeout:
                ctx.emit("(no banner received)")
    except ConnectionRefusedError:
        ctx.emit(f"FAILED: connection refused  ->  port {port} is CLOSED")
    except socket.timeout:
        ctx.emit("FAILED: timed out  ->  port is filtered or host is down")
    except socket.gaierror:
        ctx.emit("FAILED: host name could not be resolved")
    except OSError as e:
        ctx.emit(f"FAILED: {e}")


def do_dns(p, ctx):
    q = p["host"].strip()
    try:
        ipaddress.ip_address(q)
        is_ip = True
    except ValueError:
        is_ip = False
    if is_ip:
        ctx.emit(f"Reverse lookup for {q}")
        try:
            name, aliases, _ = socket.gethostbyaddr(q)
            ctx.emit(f"  Hostname : {name}")
            for a in aliases:
                ctx.emit(f"  Alias    : {a}")
        except OSError as e:
            ctx.emit(f"  No PTR record found ({e})")
        return
    ctx.emit(f"Forward lookup for {q}")
    t0 = time.time()
    try:
        infos = socket.getaddrinfo(q, None)
    except socket.gaierror as e:
        ctx.emit(f"  Could not resolve: {e}")
        return
    seen = set()
    for fam, _, _, canon, sa in infos:
        ip = sa[0]
        if ip in seen:
            continue
        seen.add(ip)
        ctx.emit(f"  {'A   ' if fam == socket.AF_INET else 'AAAA'}  {ip}")
    ctx.emit(f"\nResolved in {int((time.time() - t0) * 1000)} ms")
    for ip in list(seen)[:3]:
        try:
            ctx.emit(f"  Reverse {ip} -> {socket.gethostbyaddr(ip)[0]}")
        except OSError:
            pass


def do_trace(p, ctx):
    host, hops = p["host"].strip(), p["hops"]
    if IS_WIN:
        cmd = ["tracert", "-d", "-h", str(hops), host]
    else:
        cmd = ["traceroute", "-n", "-m", str(hops), host]
    run_cmd(cmd, ctx)


def do_portscan(p, ctx):
    host, a, b, to = p["host"].strip(), p["start"], p["end"], p["timeout"] / 1000
    if b < a:
        a, b = b, a
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        ctx.emit("Could not resolve host.")
        return
    ctx.emit(f"Scanning {host} ({ip}) ports {a}-{b} ...")
    found = []

    def probe(port):
        s = socket.socket()
        s.settimeout(to)
        try:
            return port if s.connect_ex((ip, port)) == 0 else None
        finally:
            s.close()

    with ThreadPoolExecutor(max_workers=200) as ex:
        futs = [ex.submit(probe, port) for port in range(a, b + 1)]
        for f in as_completed(futs):
            if ctx.stop.is_set():
                ex.shutdown(wait=False, cancel_futures=True)
                ctx.emit("[stopped]")
                break
            r = f.result()
            if r:
                found.append(r)
                try:
                    svc = socket.getservbyport(r)
                except OSError:
                    svc = "unknown"
                ctx.emit(f"  OPEN  {r:<6} {svc}")
    ctx.emit(f"\nScan finished: {len(found)} open port(s) found.")


def do_http(p, ctx):
    url, to = p["host"].strip(), p["timeout"] / 1000
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    ctx.emit(f"GET {url}")
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "NetworkToolsPro/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=to)
    except urllib.error.HTTPError as e:
        r = e
    except Exception as e:
        ctx.emit(f"FAILED: {e}")
        return
    ms = int((time.time() - t0) * 1000)
    ctx.emit(f"  Status       : {r.status if hasattr(r, 'status') else r.code} {r.reason}")
    ctx.emit(f"  Response time: {ms} ms")
    ctx.emit(f"  Final URL    : {r.geturl()}")
    for h in ("Server", "Content-Type", "Content-Length"):
        if r.headers.get(h):
            ctx.emit(f"  {h:<13}: {r.headers.get(h)}")


# ----------------------------------------------------------------------------
# UI building blocks
# ----------------------------------------------------------------------------
def make_card(icon, title):
    f = QFrame()
    f.setObjectName("card")
    v = QVBoxLayout(f)
    v.setContentsMargins(16, 12, 16, 12)
    v.setSpacing(8)
    h = QLabel(f"{icon}   {title}")
    h.setObjectName("cardTitle")
    v.addWidget(h)
    return f, v


def kv_grid(rows):
    """rows: list of (label, key, objectName or None). Returns (layout, {key: QLabel})."""
    g = QGridLayout()
    g.setHorizontalSpacing(18)
    g.setVerticalSpacing(7)
    vals = {}
    for i, (label, key, obj) in enumerate(rows):
        k = QLabel(label)
        k.setObjectName("key")
        v = QLabel("...")
        v.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if obj:
            v.setObjectName(obj)
        g.addWidget(k, i, 0)
        g.addWidget(v, i, 1)
        vals[key] = v
    g.setColumnStretch(1, 1)
    return g, vals


class ToolPanel(QWidget):
    line = Signal(str)
    done = Signal()

    def __init__(self, icon, title, fields, func, logger):
        super().__init__()
        self.title, self.func, self.logger = title, func, logger
        self.ctx, self.running, self.label = None, False, ""
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 10, 0, 0)
        v.setSpacing(8)

        top = QHBoxLayout()
        t = QLabel(f"{icon}  {title} Tool")
        t.setObjectName("cardTitle")
        clear = QPushButton("Clear")
        clear.setObjectName("small")
        top.addWidget(t)
        top.addStretch()
        top.addWidget(clear)
        v.addLayout(top)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.w = {}
        for label, key, kind, default, lo, hi in fields:
            col = QVBoxLayout()
            col.setSpacing(2)
            lab = QLabel(label)
            lab.setObjectName("key")
            col.addWidget(lab)
            if kind == "text":
                w = QLineEdit(default)
                row.addLayout(col, 1)
            else:
                w = QSpinBox()
                w.setRange(lo, hi)
                w.setValue(default)
                w.setFixedWidth(110)
                row.addLayout(col)
            w.returnPressed.connect(self.toggle) if kind == "text" else None
            col.addWidget(w)
            self.w[key] = w
        v.addLayout(row)

        self.btn = QPushButton(f"▶  Start {title}")
        self.btn.setObjectName("start")
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self.toggle)
        v.addWidget(self.btn)

        self.out = QPlainTextEdit()
        self.out.setReadOnly(True)
        v.addWidget(self.out, 1)

        clear.clicked.connect(self.out.clear)
        self.line.connect(self.out.appendPlainText)
        self.done.connect(self.on_done)

    def toggle(self):
        if self.running:
            self.ctx.stop.set()
            try:
                if self.ctx.proc:
                    self.ctx.proc.terminate()
            except Exception:
                pass
            return
        params = {k: (w.text() if isinstance(w, QLineEdit) else w.value()) for k, w in self.w.items()}
        if "host" in params and not params["host"].strip():
            self.out.setPlainText("Please enter a host / IP address.")
            return
        self.out.clear()
        self.running = True
        self.btn.setText("■  Stop")
        self.label = params.get("host", "")
        ctx = self.ctx = Ctx(self)

        def work():
            try:
                self.func(params, ctx)
            except FileNotFoundError as e:
                ctx.emit(f"Required system command not found: {e.filename}")
            except Exception as e:
                ctx.emit(f"Error: {e}")
            finally:
                self.done.emit()

        threading.Thread(target=work, daemon=True).start()

    def on_done(self):
        self.running = False
        self.btn.setText(f"▶  Start {self.title}")
        self.logger(f"{self.title} completed for {self.label}")


# ----------------------------------------------------------------------------
# Main window
# ----------------------------------------------------------------------------
class MainWindow(QMainWindow):
    info_ready = Signal(dict)
    ports_ready = Signal(list)
    public_ready = Signal(str)

    TAB_INDEX = {"Ping": 0, "Telnet": 1, "DNS Lookup": 2, "Traceroute": 3, "Port Scan": 4, "HTTP Test": 5, "Tools": 5}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Tools Pro")
        self.resize(1440, 900)
        self.setMinimumSize(1180, 780)
        self.all_ports, self.visible_ports, self.info = [], [], {}
        self.monitoring = True

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self.build_header())

        body = QHBoxLayout()
        body.setSpacing(0)
        content = QWidget()
        self.grid = QGridLayout(content)
        self.grid.setContentsMargins(14, 12, 14, 12)
        self.grid.setSpacing(12)
        body.addWidget(content, 1)
        outer.addLayout(body, 1)

        self.grid.addWidget(self.build_ip_card(), 0, 0)
        self.grid.addWidget(self.build_iface_card(), 0, 1)
        self.grid.addWidget(self.build_ports_card(), 1, 0, 1, 2)
        self.grid.addWidget(self.build_tools_card(), 0, 2, 2, 1)
        for c in (0, 1, 2):
            self.grid.setColumnStretch(c, 1)
        self.grid.setRowStretch(0, 0)
        self.grid.setRowStretch(1, 5)

        self.info_ready.connect(self.apply_info)
        self.ports_ready.connect(self.apply_ports)
        self.public_ready.connect(lambda ip: self.v["public"].setText(ip))

        self.clock = QTimer(self)
        self.clock.timeout.connect(self.tick)
        self.clock.start(1000)
        self.tick()

        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(lambda: self.refresh_all(public=False))
        self.timer.start()

        self.refresh_all(public=True)

    # ---- header / sidebar --------------------------------------------------
    def build_header(self):
        h = QFrame()
        h.setObjectName("header")
        h.setFixedHeight(80)
        lay = QHBoxLayout(h)
        lay.setContentsMargins(22, 8, 22, 8)
        logo = QLabel("📶")
        logo.setStyleSheet("font-size: 40px;")
        lay.addWidget(logo)
        col = QVBoxLayout()
        col.setSpacing(0)
        row = QHBoxLayout()
        t = QLabel("Network Tools Pro")
        t.setObjectName("appTitle")
        ver = QLabel("v1.0")
        ver.setObjectName("version")
        row.addWidget(t)
        row.addWidget(ver, 0, Qt.AlignBottom)
        row.addStretch()
        col.addLayout(row)
        sub = QLabel("Monitor   •   Diagnose   •   Troubleshoot")
        sub.setObjectName("appSub")
        col.addWidget(sub)
        lay.addLayout(col)
        lay.addStretch()

        pill = QFrame()
        pill.setObjectName("statusPill")
        pl = QHBoxLayout(pill)
        pl.setContentsMargins(14, 8, 14, 8)
        pl.setSpacing(14)
        self.dot = QLabel("●")
        self.status_lbl = QLabel("Running...")
        self.date_lbl, self.time_lbl = QLabel(), QLabel()
        for w in (self.dot, self.status_lbl, QLabel("📅"), self.date_lbl, QLabel("|"), self.time_lbl):
            pl.addWidget(w)
        self.set_status(True)
        lay.addWidget(pill)
        return h

    # ---- cards -------------------------------------------------------------
    def build_ip_card(self):
        f, v = make_card("🌐", "IP Address Information")
        g, vals = kv_grid([("Local IP (LAN)", "lan", "valBlue"), ("Public IP (Internet)", "public", "valGreen"),
                           ("Interface", "iface", "valPurple"), ("Subnet Mask", "mask", None),
                           ("Default Gateway", "gateway", None), ("MAC Address", "mac", None)])
        self.v = vals
        vals["public"].setObjectName("valBlue")
        vals["public"].setStyleSheet("color:#4ade80; font-weight:700; font-size:16px;")
        for key, row in (("lan", 0), ("public", 1)):
            b = QPushButton("⧉")
            b.setObjectName("copy")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=key: QApplication.clipboard().setText(self.v[k].text()))
            g.addWidget(b, row, 2)
        b = QPushButton("⧉")
        b.setObjectName("copy")
        b.clicked.connect(lambda: QApplication.clipboard().setText(self.v["mac"].text()))
        g.addWidget(b, 5, 2)
        v.addLayout(g)
        v.addStretch()
        return f

    def build_iface_card(self):
        f, v = make_card("🖧", "Network Interface Status")
        g, vals = kv_grid([("Interface Name", "i_name", "valPurple"), ("Status", "i_status", "valGreen"),
                           ("Speed", "i_speed", None), ("Bytes Sent", "i_sent", None),
                           ("Bytes Received", "i_recv", None), ("IPv4", "i_v4", None), ("IPv6", "i_v6", None)])
        self.v.update(vals)
        v.addLayout(g)
        v.addStretch()
        return f

    def build_ports_card(self):
        f, v = make_card("🗄", "Currently Running Ports")
        # replace title row by title + live + search + filter + total
        title = v.itemAt(0).widget()
        title.setText("🗄   Currently Running Ports")
        row = QHBoxLayout()
        row.setSpacing(10)
        live = QLabel("(Live)")
        live.setObjectName("live")
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search port, process or address...")
        self.search.setMinimumWidth(260)
        self.filter = QComboBox()
        self.filter.addItems(["All Ports", "TCP", "UDP"])
        self.total = QPushButton("Total: 0")
        self.total.setObjectName("total")
        row.addWidget(title)
        row.addWidget(live)
        row.addStretch()
        row.addWidget(self.search)
        row.addWidget(self.filter)
        row.addWidget(self.total)
        v.insertLayout(0, row)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["#", "Protocol", "Local Address", "Port", "State", "Process Name", "PID"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Interactive)
        hh.setSectionResizeMode(5, QHeaderView.Stretch)
        for i, w in enumerate((45, 90, 150, 80, 120, 200, 80)):
            self.table.setColumnWidth(i, w)
        v.addWidget(self.table, 1)
        self.search.textChanged.connect(self.render_ports)
        self.filter.currentTextChanged.connect(self.render_ports)
        return f

    def build_tools_card(self):
        f = QFrame()
        f.setObjectName("card")
        v = QVBoxLayout(f)
        v.setContentsMargins(12, 8, 12, 12)
        self.tabs = QTabWidget()
        specs = [
            ("📈", "Ping", [("Host / IP Address", "host", "text", " ", 0, 0),
                            ("Count", "count", "int", 4, 1, 100), ("Timeout (ms)", "timeout", "int", 1000, 100, 30000)], do_ping),
            ("🖥", "Telnet", [("Host / IP Address", "host", "text", " ", 0, 0),
                              ("Port", "port", "int", 80, 1, 65535), ("Timeout (ms)", "timeout", "int", 3000, 100, 30000)], do_telnet),
            ("🔎", "DNS Lookup", [("Domain or IP Address", "host", "text", " ", 0, 0)], do_dns),
            ("🧭", "Traceroute", [("Host / IP Address", "host", "text", " ", 0, 0),
                                  ("Max Hops", "hops", "int", 30, 1, 64)], do_trace),
            ("🎯", "Port Scan", [("Host / IP Address", "host", "text", " ", 0, 0),
                                 ("Start", "start", "int", 1, 1, 65535), ("End", "end", "int", 1024, 1, 65535),
                                 ("Timeout (ms)", "timeout", "int", 300, 50, 10000)], do_portscan),
            ("🌐", "HTTP Test", [("URL", "host", "text", " ", 0, 0),
                                 ("Timeout (ms)", "timeout", "int", 5000, 500, 60000)], do_http),
        ]
        for icon, name, fields, func in specs:
            self.tabs.addTab(ToolPanel(icon, name, fields, func, lambda m: None), name)
        v.addWidget(self.tabs)
        return f

    # ---- behaviour ---------------------------------------------------------
    def set_status(self, running):
        color = "#22c55e" if running else "#ef4444"
        self.dot.setStyleSheet(f"color:{color}; font-size:16px;")
        self.status_lbl.setText("Running..." if running else "Stopped")

    def tick(self):
        now = datetime.datetime.now()
        self.date_lbl.setText(now.strftime("%d %b %Y"))
        self.time_lbl.setText(now.strftime("%I:%M:%S %p"))

    def refresh_all(self, public=True):
        def work():
            try:
                self.info_ready.emit(gather_info())
                self.ports_ready.emit(gather_ports())
            except Exception:
                pass

        threading.Thread(target=work, daemon=True).start()
        if public:
            threading.Thread(target=lambda: self.public_ready.emit(fetch_public_ip()), daemon=True).start()

    def apply_info(self, d):
        self.info = d
        v = self.v
        v["lan"].setText(d["lan"])
        v["iface"].setText(d["iface"])
        v["mask"].setText(d["mask"])
        v["gateway"].setText(d["gateway"])
        v["mac"].setText(d["mac"])
        v["i_name"].setText(d["iface"])
        up = d["status"] == "Connected"
        v["i_status"].setText(("📶 " if up else "✖ ") + d["status"])
        v["i_status"].setStyleSheet("color:%s;" % ("#4ade80" if up else "#f87171"))
        v["i_speed"].setText(d["speed"])
        v["i_sent"].setText(d["sent"])
        v["i_recv"].setText(d["recv"])
        v["i_v4"].setText(d["lan"])
        v["i_v6"].setText(d["ipv6"])

    def apply_ports(self, rows):
        self.all_ports = rows
        self.render_ports()

    def render_ports(self):
        q, f = self.search.text().lower().strip(), self.filter.currentText()
        rows = [r for r in self.all_ports
                if (f == "All Ports" or r[0] == f) and (not q or q in " ".join(map(str, r)).lower())]
        self.visible_ports = rows
        vbar = self.table.verticalScrollBar().value()
        self.table.setRowCount(len(rows))
        for i, (proto, addr, port, state, name, pid) in enumerate(rows):
            vals = [i + 1, proto, addr, port, state, name, pid]
            for j, val in enumerate(vals):
                it = QTableWidgetItem(str(val))
                it.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if j == 1:
                    it.setBackground(QColor("#1e40af" if proto == "TCP" else "#6d28d9"))
                elif j == 3:
                    it.setForeground(QColor("#fbbf24"))
                elif j == 4:
                    it.setForeground(QColor("#4ade80"))
                    it.setBackground(QColor("#0f3d22"))
                self.table.setItem(i, j, it)
        self.table.verticalScrollBar().setValue(vbar)
        self.total.setText(f"Total: {len(rows)}")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()