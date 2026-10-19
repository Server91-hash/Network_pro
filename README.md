<div align="center">

# 🌐 Network Tools Pro

**Monitor • Diagnose • Troubleshoot**

A modern dark-themed desktop toolkit for network monitoring and diagnostics,
built with Python, PySide6 (Qt) and psutil.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)

<img width="1765" height="891" alt="Network Tools Pro Dashboard" src="https://github.com/user-attachments/assets/e38b14f7-39f7-4d7f-8672-abf3869998b9" />

</div>

---

## ✨ Features

### 📡 Monitoring
- 🖥️ **IP Information:** local IP, public IP, subnet mask, default gateway and MAC address
- 🔌 **Interface Status:** connection state, speed, bytes sent/received, IPv4 and IPv6
- 📋 **Live Ports Table:** listening TCP/UDP ports with process name and PID, plus search and filter
- 🔄 **Auto-refresh:** data updates every few seconds

### 🛠️ Built-in Tools
|        Tool       |          Description          |
|-------------------|-------------------------------|
| 📶 **Ping**       | Test connectivity and latency |
| 🔗 **Telnet**     | Check whether a port is open |
| 🔎 **DNS Lookup** | Forward and reverse DNS resolution |
| 🧭 **Traceroute** | Trace the network path to a host |
| 🎯 **Port Scan**  | Scan a range of ports on a host |
| 🌍 **HTTP Test**  | Check website status and response time |

---

## 📦 Build a Standalone EXE

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name NetworkToolsPro network_tools_pro.py
```

Your executable will be at `dist/NetworkToolsPro.exe`.

---

## ⚡ Auto-Start with Windows

1. Press `Win + R`, type `shell:startup` and press Enter.
2. Copy a **shortcut** of `NetworkToolsPro.exe` into that folder.
3. Restart your PC to test it.

---
