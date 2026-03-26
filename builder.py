"""
Remote Admin Tool - Builder
Premium Tkinter UI with setup guide, builder, and donate section.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
import shutil
import threading


def get_base_dir():
    """Get the directory where the builder exe/script lives."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_bundled_dir():
    """Get the directory for bundled data files (PyInstaller _MEIPASS)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def find_python():
    """Find the system Python executable."""
    if not getattr(sys, 'frozen', False):
        return sys.executable
    # When frozen, sys.executable is the builder .exe — find real Python
    import shutil as _sh
    py = _sh.which('python') or _sh.which('python3')
    if py:
        return py
    # Common install locations
    for path in [
        os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python*\python.exe'),
        os.path.expandvars(r'%PROGRAMFILES%\Python*\python.exe'),
        r'C:\Python*\python.exe',
    ]:
        import glob
        matches = glob.glob(path)
        if matches:
            return matches[-1]  # newest version
    return 'python'  # fallback, hope it's on PATH
import webbrowser


# ============================================================
# THEME COLORS
# ============================================================
COLORS = {
    'bg_dark':     '#0a0a14',
    'bg_card':     '#12121f',
    'bg_input':    '#1a1a2e',
    'bg_hover':    '#1e1e35',
    'accent':      '#e94560',
    'accent_hover':'#ff5a7a',
    'accent_glow': '#e9456033',
    'success':     '#4ade80',
    'info':        '#60a5fa',
    'warning':     '#fbbf24',
    'text':        '#ffffff',
    'text_dim':    '#8888aa',
    'text_muted':  '#555570',
    'border':      '#2a2a40',
    'tab_active':  '#e94560',
    'tab_inactive':'#2a2a40',
}


class BuilderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vortex RAT — Builder")
        self.root.geometry("620x780")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 310
        y = (self.root.winfo_screenheight() // 2) - 390
        self.root.geometry(f"620x780+{x}+{y}")

        # Try to set icon
        try:
            self.root.iconbitmap(default='')
        except:
            pass

        # ── Header ──
        self._build_header()

        # ── Tab Bar ──
        self.current_tab = tk.StringVar(value="setup")
        self._build_tab_bar()

        # ── Content Area ──
        self.content_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        self.content_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        # ── Pages ──
        self.pages = {}
        self._build_setup_page()
        self._build_builder_page()
        self._build_donate_page()

        # Show initial page
        self._show_page("setup")

    # ============================================================
    # HEADER
    # ============================================================
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=COLORS['bg_dark'])
        hdr.pack(fill="x", padx=25, pady=(20, 0))

        # Title row
        title_frame = tk.Frame(hdr, bg=COLORS['bg_dark'])
        title_frame.pack(fill="x")

        tk.Label(title_frame, text="⚡", font=("Segoe UI", 24),
                 bg=COLORS['bg_dark'], fg=COLORS['accent']).pack(side="left")
        title_text = tk.Frame(title_frame, bg=COLORS['bg_dark'])
        title_text.pack(side="left", padx=(8, 0))
        tk.Label(title_text, text="Vortex RAT",
                 font=("Segoe UI", 18, "bold"),
                 bg=COLORS['bg_dark'], fg=COLORS['text']).pack(anchor="w")
        tk.Label(title_text, text="Configure • Build • Deploy",
                 font=("Segoe UI", 9),
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted']).pack(anchor="w")

        # Version badge
        ver = tk.Label(title_frame, text=" v2.0 ",
                       font=("Segoe UI", 8, "bold"),
                       bg=COLORS['accent'], fg=COLORS['text'])
        ver.pack(side="right", pady=(5, 0))

        # Separator line
        sep = tk.Frame(hdr, bg=COLORS['border'], height=1)
        sep.pack(fill="x", pady=(12, 0))

    # ============================================================
    # TAB BAR
    # ============================================================
    def _build_tab_bar(self):
        tab_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        tab_frame.pack(fill="x", padx=25, pady=(12, 8))

        tabs = [
            ("📋  Setup Guide", "setup"),
            ("🔨  Builder", "builder"),
            ("💖  Donate", "donate"),
        ]

        self.tab_buttons = {}
        for text, name in tabs:
            btn = tk.Label(
                tab_frame, text=text,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS['bg_dark'],
                fg=COLORS['text_dim'],
                padx=16, pady=6,
                cursor="hand2"
            )
            btn.pack(side="left", padx=(0, 4))
            btn.bind("<Button-1>", lambda e, n=name: self._switch_tab(n))
            btn.bind("<Enter>", lambda e, b=btn, n=name:
                     b.config(fg=COLORS['text']) if self.current_tab.get() != n else None)
            btn.bind("<Leave>", lambda e, b=btn, n=name:
                     b.config(fg=COLORS['text_dim']) if self.current_tab.get() != n else None)
            self.tab_buttons[name] = btn

    def _switch_tab(self, name):
        self.current_tab.set(name)
        self._show_page(name)
        # Update tab styles
        for tab_name, btn in self.tab_buttons.items():
            if tab_name == name:
                btn.config(fg=COLORS['accent'], bg=COLORS['bg_card'])
            else:
                btn.config(fg=COLORS['text_dim'], bg=COLORS['bg_dark'])

    def _show_page(self, name):
        for page_name, page in self.pages.items():
            page.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        # Trigger tab style
        for tab_name, btn in self.tab_buttons.items():
            if tab_name == name:
                btn.config(fg=COLORS['accent'], bg=COLORS['bg_card'])
            else:
                btn.config(fg=COLORS['text_dim'], bg=COLORS['bg_dark'])

    # ============================================================
    # SETUP GUIDE PAGE
    # ============================================================
    def _build_setup_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS['bg_dark'])
        self.pages["setup"] = page

        # Scrollable canvas
        canvas = tk.Canvas(page, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS['bg_dark'])

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=555)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Title
        tk.Label(scroll_frame, text="Setup Guide",
                 font=("Segoe UI", 16, "bold"),
                 bg=COLORS['bg_dark'], fg=COLORS['text']).pack(anchor="w", pady=(5, 2))
        tk.Label(scroll_frame, text="Follow these steps to set up your Remote Admin Tool",
                 font=("Segoe UI", 9),
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted']).pack(anchor="w", pady=(0, 15))

        # Steps
        steps = [
            {
                "num": "1",
                "title": "Create a Telegram Bot",
                "desc": "Open Telegram and search for @BotFather. Send /newbot and follow the prompts. Give your bot a name and username.",
                "tip": "💡 Save the Bot Token — you'll need it in the Builder tab.",
                "color": COLORS['info']
            },
            {
                "num": "2",
                "title": "Get Your Bot Token",
                "desc": "After creating the bot, @BotFather will send you a token like:\n8551779985:AAFxIsKFSSviwldBGhk-oeqRlYSrmIV-xxx\n\nCopy this entire token.",
                "tip": "⚠️ Keep this token secret! Anyone with it can control your bot.",
                "color": COLORS['warning']
            },
            {
                "num": "3",
                "title": "Get Your User ID",
                "desc": "Search for @userinfobot on Telegram and start it.\nIt will instantly reply with your numeric User ID.\n\nAlternatively, use @rawdatabot or @getmyid_bot.",
                "tip": "💡 Your User ID is a number like 8310686102",
                "color": COLORS['info']
            },
            {
                "num": "4",
                "title": "Install Prerequisites",
                "desc": "Make sure you have Python 3.8+ and PyInstaller installed on this PC.\nOpen a terminal and run:\npip install pyinstaller\n\nThis is needed to compile the client .exe.",
                "tip": "💡 Python + PyInstaller are required on the build machine only.",
                "color": COLORS['info']
            },
            {
                "num": "5",
                "title": "Build the Client Executable",
                "desc": "Go to the Builder tab, paste your Bot Token and User ID, customize the name/icon, then click BUILD.\n\nThe client .exe will be saved in the /output folder next to this builder.",
                "tip": "⏱️ Building takes 1-2 minutes. Be patient!",
                "color": COLORS['success']
            },
            {
                "num": "6",
                "title": "Deploy & Connect",
                "desc": "Run the built .exe on the target machine. It will appear in the system tray and auto-notify you on Telegram.\n\nSend /help to see all 55+ commands!\nSend /devices to see all connected machines.",
                "tip": "🔒 Only your User ID can send commands to the bot.",
                "color": COLORS['success']
            },
        ]

        for step in steps:
            self._create_step_card(scroll_frame, step)

        # Spacer
        tk.Frame(scroll_frame, bg=COLORS['bg_dark'], height=20).pack()

    def _create_step_card(self, parent, step):
        # Card container
        card = tk.Frame(parent, bg=COLORS['bg_card'], highlightthickness=1,
                        highlightbackground=COLORS['border'])
        card.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(card, bg=COLORS['bg_card'])
        inner.pack(fill="x", padx=15, pady=12)

        # Top row: number badge + title
        top = tk.Frame(inner, bg=COLORS['bg_card'])
        top.pack(fill="x")

        badge = tk.Label(top, text=f" {step['num']} ",
                         font=("Segoe UI", 10, "bold"),
                         bg=step['color'], fg=COLORS['text'])
        badge.pack(side="left")

        tk.Label(top, text=f"  {step['title']}",
                 font=("Segoe UI", 11, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text']).pack(side="left")

        # Description
        tk.Label(inner, text=step['desc'],
                 font=("Segoe UI", 9),
                 bg=COLORS['bg_card'], fg=COLORS['text_dim'],
                 wraplength=500, justify="left", anchor="w").pack(fill="x", pady=(8, 0))

        # Tip
        if step.get('tip'):
            tip_frame = tk.Frame(inner, bg=COLORS['bg_input'])
            tip_frame.pack(fill="x", pady=(8, 0))
            tk.Label(tip_frame, text=step['tip'],
                     font=("Segoe UI", 8),
                     bg=COLORS['bg_input'], fg=step['color'],
                     padx=8, pady=4, anchor="w").pack(fill="x")

    # ============================================================
    # BUILDER PAGE
    # ============================================================
    def _build_builder_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS['bg_dark'])
        self.pages["builder"] = page

        # Scrollable content
        canvas = tk.Canvas(page, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_inner = tk.Frame(canvas, bg=COLORS['bg_dark'])
        scroll_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_inner, anchor="nw", width=555)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel_builder(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel_builder))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Title
        tk.Label(scroll_inner, text="Build Executable",
                 font=("Segoe UI", 16, "bold"),
                 bg=COLORS['bg_dark'], fg=COLORS['text']).pack(anchor="w", pady=(5, 2))
        tk.Label(scroll_inner, text="Enter your credentials, customize, and build",
                 font=("Segoe UI", 9),
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted']).pack(anchor="w", pady=(0, 15))

        # Use scroll_inner instead of page for all children
        form_parent = scroll_inner

        # Form Card
        form_card = tk.Frame(form_parent, bg=COLORS['bg_card'], highlightthickness=1,
                             highlightbackground=COLORS['border'])
        form_card.pack(fill="x")
        form = tk.Frame(form_card, bg=COLORS['bg_card'])
        form.pack(fill="x", padx=20, pady=18)

        # Bot Token
        token_lbl_frame = tk.Frame(form, bg=COLORS['bg_card'])
        token_lbl_frame.pack(fill="x")
        tk.Label(token_lbl_frame, text="🤖  Telegram Bot Token",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text_dim']).pack(side="left")
        tk.Label(token_lbl_frame, text="from @BotFather",
                 font=("Segoe UI", 8),
                 bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(side="right")

        self.token_entry = tk.Entry(
            form, font=("Consolas", 11),
            bg=COLORS['bg_input'], fg=COLORS['text'],
            insertbackground=COLORS['text'],
            relief="flat", bd=10, selectbackground=COLORS['accent'])
        self.token_entry.pack(fill="x", pady=(4, 16))
        self.token_entry.insert(0, "")
        self._add_placeholder(self.token_entry, "Paste your bot token here...")

        # Admin User ID
        uid_lbl_frame = tk.Frame(form, bg=COLORS['bg_card'])
        uid_lbl_frame.pack(fill="x")
        tk.Label(uid_lbl_frame, text="👤  Admin Telegram User ID",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text_dim']).pack(side="left")
        tk.Label(uid_lbl_frame, text="from @userinfobot",
                 font=("Segoe UI", 8),
                 bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(side="right")

        self.userid_entry = tk.Entry(
            form, font=("Consolas", 11),
            bg=COLORS['bg_input'], fg=COLORS['text'],
            insertbackground=COLORS['text'],
            relief="flat", bd=10, selectbackground=COLORS['accent'])
        self.userid_entry.pack(fill="x", pady=(4, 12))
        self._add_placeholder(self.userid_entry, "Enter your numeric user ID...")

        # ── Customization Section ──
        custom_sep = tk.Frame(form, bg=COLORS['border'], height=1)
        custom_sep.pack(fill="x", pady=(5, 12))

        tk.Label(form, text="🎨  Customization",
                 font=("Segoe UI", 11, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text']).pack(anchor="w", pady=(0, 10))

        # EXE Name
        name_lbl_frame = tk.Frame(form, bg=COLORS['bg_card'])
        name_lbl_frame.pack(fill="x")
        tk.Label(name_lbl_frame, text="📛  Executable Name",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text_dim']).pack(side="left")
        tk.Label(name_lbl_frame, text=".exe added automatically",
                 font=("Segoe UI", 8),
                 bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(side="right")

        self.exename_entry = tk.Entry(
            form, font=("Consolas", 11),
            bg=COLORS['bg_input'], fg=COLORS['text'],
            insertbackground=COLORS['text'],
            relief="flat", bd=10, selectbackground=COLORS['accent'])
        self.exename_entry.pack(fill="x", pady=(4, 12))
        self._add_placeholder(self.exename_entry, "RemoteAdmin")

        # Icon File
        icon_lbl_frame = tk.Frame(form, bg=COLORS['bg_card'])
        icon_lbl_frame.pack(fill="x")
        tk.Label(icon_lbl_frame, text="🖼️  Custom Icon",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text_dim']).pack(side="left")
        tk.Label(icon_lbl_frame, text=".ico files only",
                 font=("Segoe UI", 8),
                 bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(side="right")

        icon_row = tk.Frame(form, bg=COLORS['bg_card'])
        icon_row.pack(fill="x", pady=(4, 12))

        self.icon_path_var = tk.StringVar(value="")
        self.icon_entry = tk.Entry(
            icon_row, font=("Consolas", 10),
            bg=COLORS['bg_input'], fg=COLORS['text'],
            insertbackground=COLORS['text'],
            relief="flat", bd=8, selectbackground=COLORS['accent'],
            textvariable=self.icon_path_var, state="readonly")
        self.icon_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._add_placeholder(self.icon_entry, "No icon selected (default)")

        browse_btn = tk.Button(
            icon_row, text="📂 Browse",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['bg_input'], fg=COLORS['text_dim'],
            activebackground=COLORS['bg_hover'],
            activeforeground=COLORS['text'],
            relief="flat", bd=0, cursor="hand2",
            command=self._browse_icon, padx=12, pady=6)
        browse_btn.pack(side="right")
        browse_btn.bind("<Enter>",
            lambda e: browse_btn.config(bg=COLORS['bg_hover'], fg=COLORS['text']))
        browse_btn.bind("<Leave>",
            lambda e: browse_btn.config(bg=COLORS['bg_input'], fg=COLORS['text_dim']))

        clear_icon_btn = tk.Button(
            icon_row, text="✕",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['bg_input'], fg=COLORS['accent'],
            activebackground=COLORS['bg_hover'],
            relief="flat", bd=0, cursor="hand2",
            command=self._clear_icon, padx=6, pady=6)
        clear_icon_btn.pack(side="right", padx=(0, 4))

        # Run as Administrator checkbox
        self.admin_var = tk.BooleanVar(value=True)
        admin_frame = tk.Frame(form, bg=COLORS['bg_card'])
        admin_frame.pack(fill="x", pady=(0, 15))

        admin_cb = tk.Checkbutton(
            admin_frame, text="  🛡️  Run as Administrator (auto UAC prompt)",
            variable=self.admin_var,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['bg_card'], fg=COLORS['text_dim'],
            activebackground=COLORS['bg_card'],
            activeforeground=COLORS['text'],
            selectcolor=COLORS['bg_input'],
            cursor="hand2")
        admin_cb.pack(anchor="w")

        tk.Label(admin_frame,
                 text="        When enabled, Windows will always show a UAC elevation prompt",
                 font=("Segoe UI", 8),
                 bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(anchor="w")

        # Separator
        build_sep = tk.Frame(form, bg=COLORS['border'], height=1)
        build_sep.pack(fill="x", pady=(0, 15))

        # Build Button
        self.build_btn = tk.Button(
            form, text="⚡  BUILD EXECUTABLE",
            font=("Segoe UI", 13, "bold"),
            bg=COLORS['accent'], fg=COLORS['text'],
            activebackground=COLORS['accent_hover'],
            activeforeground=COLORS['text'],
            relief="flat", bd=0, command=self.start_build,
            cursor="hand2", height=2)
        self.build_btn.pack(fill="x")

        # Hover effects
        self.build_btn.bind("<Enter>",
            lambda e: self.build_btn.config(bg=COLORS['accent_hover']))
        self.build_btn.bind("<Leave>",
            lambda e: self.build_btn.config(bg=COLORS['accent']))

        # Status Area
        self.status_frame = tk.Frame(form_parent, bg=COLORS['bg_dark'])
        self.status_frame.pack(fill="x", pady=(15, 0))

        self.status_var = tk.StringVar(value="Ready — Enter your details above")
        self.status_label = tk.Label(
            self.status_frame, textvariable=self.status_var,
            font=("Segoe UI", 9), bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
            wraplength=540, justify="center")
        self.status_label.pack()

        # Progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("red.Horizontal.TProgressbar",
                        troughcolor=COLORS['bg_input'],
                        background=COLORS['accent'],
                        darkcolor=COLORS['accent'],
                        lightcolor=COLORS['accent_hover'])
        self.progress = ttk.Progressbar(
            self.status_frame, mode='indeterminate', length=540,
            style="red.Horizontal.TProgressbar")

        # Info card below
        info_card = tk.Frame(form_parent, bg=COLORS['bg_input'])
        info_card.pack(fill="x", pady=(15, 0))
        info_inner = tk.Frame(info_card, bg=COLORS['bg_input'])
        info_inner.pack(fill="x", padx=12, pady=8)

        tk.Label(info_inner,
                 text="📌 The built .exe will be saved in the /output folder\n"
                      "📌 Python 3.8+ and PyInstaller must be installed on this PC\n"
                      "📌 .ico icon must be a valid Windows icon file\n"
                      "📌 Each device auto-notifies you when it comes online",
                 font=("Segoe UI", 8), bg=COLORS['bg_input'],
                 fg=COLORS['text_muted'], justify="left", anchor="w").pack(anchor="w")

        # Spacer
        tk.Frame(form_parent, bg=COLORS['bg_dark'], height=15).pack()

    def _add_placeholder(self, entry, placeholder):
        """Add placeholder text to an entry widget."""
        entry.placeholder = placeholder
        entry.has_placeholder = True
        entry.insert(0, placeholder)
        entry.config(fg=COLORS['text_muted'])

        def on_focus_in(e):
            if entry.has_placeholder:
                entry.delete(0, "end")
                entry.config(fg=COLORS['text'])
                entry.has_placeholder = False

        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS['text_muted'])
                entry.has_placeholder = True

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _browse_icon(self):
        """Open file dialog to select an .ico file."""
        filepath = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")],
            initialdir=get_base_dir()
        )
        if filepath:
            self.icon_entry.config(state="normal")
            self.icon_entry.delete(0, "end")
            self.icon_entry.insert(0, filepath)
            self.icon_entry.config(fg=COLORS['text'])
            self.icon_entry.has_placeholder = False
            self.icon_entry.config(state="readonly")
            self.icon_path_var.set(filepath)

    def _clear_icon(self):
        """Clear the selected icon."""
        self.icon_entry.config(state="normal")
        self.icon_entry.delete(0, "end")
        self.icon_entry.insert(0, "No icon selected (default)")
        self.icon_entry.config(fg=COLORS['text_muted'])
        self.icon_entry.has_placeholder = True
        self.icon_entry.config(state="readonly")
        self.icon_path_var.set("")

    # ============================================================
    # DONATE PAGE
    # ============================================================
    def _build_donate_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS['bg_dark'])
        self.pages["donate"] = page

        # Title
        tk.Label(page, text="Support the Developer",
                 font=("Segoe UI", 16, "bold"),
                 bg=COLORS['bg_dark'], fg=COLORS['text']).pack(anchor="w", pady=(5, 2))
        tk.Label(page, text="If you like this tool, consider buying me a coffee ☕",
                 font=("Segoe UI", 9),
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted']).pack(anchor="w", pady=(0, 20))

        # Donate card
        donate_card = tk.Frame(page, bg=COLORS['bg_card'], highlightthickness=1,
                               highlightbackground=COLORS['border'])
        donate_card.pack(fill="x")
        donate_inner = tk.Frame(donate_card, bg=COLORS['bg_card'])
        donate_inner.pack(padx=20, pady=20)

        # Heart emoji
        tk.Label(donate_inner, text="💖",
                 font=("Segoe UI", 36),
                 bg=COLORS['bg_card'], fg=COLORS['accent']).pack(pady=(0, 5))

        tk.Label(donate_inner, text="Donate via UPI",
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS['bg_card'], fg=COLORS['text']).pack()
        tk.Label(donate_inner,
                 text="Scan the QR code below with any UPI app\n(GPay, PhonePe, Paytm, etc.)",
                 font=("Segoe UI", 9),
                 bg=COLORS['bg_card'], fg=COLORS['text_dim'],
                 justify="center").pack(pady=(4, 15))

        # QR Code Image
        try:
            from PIL import Image, ImageTk
            base_dir = get_base_dir()
            bundled_dir = get_bundled_dir()
            # Try bundled first (frozen), then base dir (dev)
            qr_path = os.path.join(bundled_dir, "image.png")
            if not os.path.exists(qr_path):
                qr_path = os.path.join(base_dir, "image.png")
            if os.path.exists(qr_path):
                img = Image.open(qr_path)
                img = img.resize((200, 200), Image.LANCZOS)
                self.qr_photo = ImageTk.PhotoImage(img)

                # QR frame with border
                qr_frame = tk.Frame(donate_inner, bg=COLORS['text'],
                                    padx=3, pady=3)
                qr_frame.pack(pady=(0, 15))
                qr_label = tk.Label(qr_frame, image=self.qr_photo,
                                    bg=COLORS['text'])
                qr_label.pack()
            else:
                tk.Label(donate_inner, text="[QR Code: image.png not found]",
                         font=("Segoe UI", 10),
                         bg=COLORS['bg_card'], fg=COLORS['accent']).pack(pady=15)
        except ImportError:
            tk.Label(donate_inner, text="[Install Pillow to show QR code]",
                     font=("Segoe UI", 10),
                     bg=COLORS['bg_card'], fg=COLORS['accent']).pack(pady=15)

        # Thank you message
        thanks = tk.Frame(page, bg=COLORS['bg_input'])
        thanks.pack(fill="x", pady=(15, 0))
        tk.Label(thanks,
                 text="🙏 Every donation helps keep this project alive and motivates\n"
                      "development of new features. Thank you for your support!",
                 font=("Segoe UI", 9), bg=COLORS['bg_input'],
                 fg=COLORS['text_dim'], justify="center", pady=10).pack()

    # ============================================================
    # BUILD LOGIC
    # ============================================================
    def set_status(self, text, color=None):
        if color is None:
            color = COLORS['text_muted']
        self.status_var.set(text)
        self.status_label.configure(fg=color)
        self.root.update_idletasks()

    def _get_entry_value(self, entry):
        """Get entry value, ignoring placeholder."""
        val = entry.get().strip()
        if hasattr(entry, 'has_placeholder') and entry.has_placeholder:
            return ""
        return val

    def start_build(self):
        token = self._get_entry_value(self.token_entry)
        userid = self._get_entry_value(self.userid_entry)
        exe_name = self._get_entry_value(self.exename_entry) or "RemoteAdmin"
        icon_path = self.icon_path_var.get().strip()
        run_as_admin = self.admin_var.get()

        if not token:
            messagebox.showwarning("Missing",
                "Please enter a Bot Token.\n\n"
                "Get one from @BotFather on Telegram.")
            return
        if not userid:
            messagebox.showwarning("Missing",
                "Please enter your Admin User ID.\n\n"
                "Get it from @userinfobot on Telegram.")
            return
        if not userid.isdigit():
            messagebox.showwarning("Invalid",
                "User ID must be a number.\n\n"
                "Get your numeric ID from @userinfobot on Telegram.")
            return

        # Sanitize exe name
        exe_name = exe_name.replace('.exe', '').strip()
        exe_name = "".join(c for c in exe_name if c.isalnum() or c in '-_ ')
        if not exe_name:
            exe_name = "RemoteAdmin"

        # Validate icon
        if icon_path and not os.path.exists(icon_path):
            messagebox.showwarning("Invalid",
                f"Icon file not found:\n{icon_path}")
            return
        if icon_path and not icon_path.lower().endswith('.ico'):
            messagebox.showwarning("Invalid",
                "Icon file must be a .ico file.\n\n"
                "Convert your image to .ico format first.")
            return

        self.build_btn.config(state="disabled", text="⏳  BUILDING...",
                              bg=COLORS['text_muted'])
        self.progress.pack(pady=(10, 0))
        self.progress.start(10)

        threading.Thread(
            target=lambda: self.build(token, userid, exe_name, icon_path, run_as_admin),
            daemon=True).start()

    def build(self, token, userid, exe_name="RemoteAdmin", icon_path="", run_as_admin=True):
        try:
            self.set_status("📝 Configuring client...", COLORS['info'])

            base_dir = get_base_dir()
            bundled_dir = get_bundled_dir()

            # Look for client.py: bundled (frozen) first, then base dir (dev)
            template_path = os.path.join(bundled_dir, "client.py")
            if not os.path.exists(template_path):
                template_path = os.path.join(base_dir, "client.py")
            if not os.path.exists(template_path):
                raise FileNotFoundError(
                    "client.py not found! Place it next to the builder.")

            with open(template_path, "r", encoding="utf-8") as f:
                client_code = f.read()

            # Embed configuration
            client_code = client_code.replace(
                'BOT_TOKEN = "PLACEHOLDER_TOKEN"',
                f'BOT_TOKEN = "{token}"')
            client_code = client_code.replace(
                'ADMIN_ID = "PLACEHOLDER_ID"',
                f'ADMIN_ID = "{userid}"')

            # Temp build directory
            build_dir = os.path.join(base_dir, "_build_temp")
            os.makedirs(build_dir, exist_ok=True)
            configured = os.path.join(build_dir, "remote_admin.py")
            with open(configured, "w", encoding="utf-8") as f:
                f.write(client_code)

            # Build with PyInstaller
            build_info = f"🔨 Building '{exe_name}.exe'"
            if icon_path:
                build_info += f" with custom icon"
            if run_as_admin:
                build_info += " (admin mode)"
            build_info += "... This may take 1-2 minutes."
            self.set_status(build_info, COLORS['info'])

            output_dir = os.path.join(base_dir, "output")
            os.makedirs(output_dir, exist_ok=True)

            # Find the real Python (not ourselves if we're frozen)
            python_exe = find_python()

            cmd = [
                python_exe, "-m", "PyInstaller",
                "--onefile",
                "--noconsole",
                "--name", exe_name,
                "--distpath", output_dir,
                "--workpath", os.path.join(build_dir, "work"),
                "--specpath", build_dir,
                "--clean",
                "--hidden-import", "telebot",
                "--collect-all", "pyTelegramBotAPI",
                "--copy-metadata", "pyTelegramBotAPI",
                "--hidden-import", "pystray",
                "--collect-all", "pystray",
                "--hidden-import", "pyttsx3",
                "--hidden-import", "pyttsx3.drivers",
                "--hidden-import", "pyttsx3.drivers.sapi5",
                "--collect-all", "pyttsx3",
                "--hidden-import", "cv2",
                "--collect-all", "cv2",
                "--hidden-import", "PIL",
                "--hidden-import", "psutil",
                "--hidden-import", "requests",
                "--hidden-import", "pyperclip"
            ]

            # Custom icon
            if icon_path and os.path.exists(icon_path):
                cmd.extend(["--icon", icon_path])

            # Run as Administrator (embed UAC manifest)
            if run_as_admin:
                cmd.append("--uac-admin")

            # Add the script as last argument
            cmd.append(configured)

            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=300)

            # Cleanup temp
            shutil.rmtree(build_dir, ignore_errors=True)

            if result.returncode == 0:
                exe_path = os.path.join(output_dir, f"{exe_name}.exe")
                self.progress.stop()
                self.progress.pack_forget()

                admin_note = "\n🛡️ Will auto-request admin privileges" if run_as_admin else ""
                icon_note = "\n🖼️ Custom icon applied" if icon_path else ""

                self.set_status(f"✅ Build successful!\n{exe_path}", COLORS['success'])
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"✅ Build complete!\n\n"
                    f"Executable:\n{exe_path}\n"
                    f"{admin_note}{icon_note}\n\n"
                    f"Send /start in your Telegram bot to connect."))
            else:
                self.progress.stop()
                self.progress.pack_forget()
                err = result.stderr[-500:] if result.stderr else "Unknown error"
                self.set_status("❌ Build failed", COLORS['accent'])
                self.root.after(0, lambda: messagebox.showerror(
                    "Build Failed", err))

        except FileNotFoundError as e:
            self.progress.stop()
            self.progress.pack_forget()
            self.set_status(f"❌ {e}", COLORS['accent'])
        except subprocess.TimeoutExpired:
            self.progress.stop()
            self.progress.pack_forget()
            self.set_status("❌ Build timed out (>5 min)", COLORS['accent'])
        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            self.set_status(f"❌ Error: {e}", COLORS['accent'])
        finally:
            self.root.after(0, lambda: self.build_btn.config(
                state="normal", text="⚡  BUILD EXECUTABLE",
                bg=COLORS['accent']))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BuilderApp()
    app.run()
