import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import queue
import json
import os
import sys
import webbrowser
import subprocess
import re
from datetime import datetime

# Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.tool_suite_initializer import ToolSuiteInitializer
from utils.utils import Utils, Shell_Colors
from kevin_friends.dora import Dora
from kevin_friends.frank import Frank
from kevin_friends.cesare import Cesare

class KevinGUI:
    def __init__(self, root, args=None):
        self.root = root
        self.root.title("KEVIN - Offensive Toolsuite")
        self.root.geometry("1100x850")
        self.root.minsize(900, 700)
        
        self.utils = Utils()
        self.colors = Shell_Colors()
        self.config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.assets', 'config.json'))
        self.load_config()
        
        self.theme = self.config.get('user_settings', {}).get('theme', 'dark')
        self.setup_styles()
        
        self.tool_suite = None
        self.active_jobs = {} 
        self.log_queue = queue.Queue()
        
        # Implement a real OS pipe for stdin to fix 'fileno' issue
        self.stdin_read_fd, self.stdin_write_fd = os.pipe()
        
        # Redirect stdout/stderr/stdin
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.original_stdin = sys.stdin
        sys.stdout = self
        sys.stderr = self
        sys.stdin = os.fdopen(self.stdin_read_fd, 'r')
        
        # Skip setup only if explicitly requested via CLI args (e.g. -gui flag)
        if args and hasattr(args, 'gui') and args.gui:
            self.create_main_window()
            self.init_from_args(args)
        else:
            self.create_setup_screen()
            
        self.root.after(100, self.process_log_queue)

    def init_from_args(self, args):
        try:
            self.args_nmap_requested = args.nmap
            self.tool_suite = ToolSuiteInitializer(
                DEBUG=args.d,
                CLEAN=args.clean_log,
                base_path=os.getcwd(),
                IP=args.ip,
                COMMON_NAME=args.common_name,
                HOST_NAME=args.host_name,
                UDP_SCAN=args.udp,
                WORKSPACE_PATH=args.workspace,
                VPN_PATH=args.vpn,
                ALIAS=args.alias
            )
            
            # Monkey patch log_actions
            original_log = self.tool_suite.log_actions
            def patched_log(message):
                original_log(message)
                self.log_queue.put(message)
            self.tool_suite.log_actions = patched_log
            
            self.add_job("INIT", "Workspace & Connection (CLI Args)")
            threading.Thread(target=self.init_task_thread, daemon=True).start()
            
        except Exception as e:
            self.show_error(f"Failed to initialize from CLI: {e}")
            self.create_setup_screen()

    def write(self, message):
        if message:
            self.log_queue.put(message)

    def flush(self):
        pass

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                raise FileNotFoundError
        except Exception:
            self.config = {
                "user_settings": {
                    "theme": "dark",
                    "seclist_path": "/usr/share/wordlists/seclists",
                    "dirbuster": "/usr/share/wordlists/dirbuster",
                    "dirb": "/usr/share/wordlists/dirb"
                },
                "functional_settings": {
                    "gobuster": {
                        "gobuster_thread": "40",
                        "dir_wordlist": "/usr/share/wordlists/dirb/common.txt",
                        "vhost_wordlist": "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt"
                    }
                }
            }

    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.show_error(f"Failed to save config: {e}")

    def setup_styles(self):
        self.style = ttk.Style()
        # Use 'clam' for better consistency on Linux
        try:
            self.style.theme_use('clam')
        except:
            pass

        if self.theme == 'dark':
            self.bg_color = "#1e1e1e"
            self.fg_color = "#d4d4d4"
            self.accent_color = "#e51400" # Kevin Red
            self.btn_color = "#333333"
            self.btn_active = "#454545"
            self.entry_bg = "#3c3c3c"
            self.tree_bg = "#252526"
        else:
            self.bg_color = "#f3f3f3"
            self.fg_color = "#000000"
            self.accent_color = "#007acc" # VS Blue
            self.btn_color = "#e1e1e1"
            self.btn_active = "#c5c5c5"
            self.entry_bg = "#ffffff"
            self.tree_bg = "#ffffff"

        self.root.configure(bg=self.bg_color)
        
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Segoe UI", 10))
        self.style.configure("TEntry", fieldbackground=self.entry_bg, foreground=self.fg_color, insertcolor=self.fg_color)
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.btn_color, foreground=self.fg_color, padding=[12, 4])
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_color)], foreground=[("selected", "white")])
        self.style.configure("Header.TLabel", font=("Segoe UI", 28, "bold"), foreground=self.accent_color)
        
        self.style.configure("Treeview", background=self.tree_bg, foreground=self.fg_color, fieldbackground=self.tree_bg, borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent_color)])
        self.style.configure("Treeview.Heading", background=self.btn_color, foreground=self.fg_color, font=("Segoe UI", 10, "bold"))

        # Use tk.Button for main actions to avoid theme glitches
        self.btn_style = {
            "bg": self.btn_color,
            "fg": self.fg_color,
            "activebackground": self.accent_color,
            "activeforeground": "white",
            "relief": tk.FLAT,
            "font": ("Segoe UI", 10)
        }

    def show_error(self, message):
        messagebox.showerror("KEVIN ERROR", message)

    def center_window(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def browse_path(self, var, mode='file'):
        if mode == 'file':
            path = filedialog.askopenfilename(initialdir=os.path.expanduser("~"))
        else:
            path = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if path:
            var.set(path)

    def create_setup_screen(self):
        self.setup_frame = ttk.Frame(self.root)
        self.setup_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        header = ttk.Label(self.setup_frame, text="KEVIN", style="Header.TLabel")
        header.pack(pady=(0, 30))
        
        form_frame = ttk.Frame(self.setup_frame)
        form_frame.pack(expand=True)
        
        fields = [
            ("IP Address:", "ip", "10.10.10.100", None),
            ("Common Name:", "common_name", "machine.htb", None),
            ("Host Name:", "host_name", "machine", None),
            ("Workspace Path:", "workspace", "~/EH_Workspaces/machine", "dir"),
            ("VPN Path:", "vpn", "~/lab.ovpn", "file"),
            ("Alias File:", "alias", "~/.bashrc", "file")
        ]
        
        self.setup_vars = {
            "ip": tk.StringVar(),
            "common_name": tk.StringVar(),
            "host_name": tk.StringVar(),
            "workspace": tk.StringVar(),
            "vpn": tk.StringVar(),
            "alias": tk.StringVar(),
            "debug": tk.BooleanVar(value=True),
            "clean_log": tk.BooleanVar(value=True)
        }
        
        for i, (label, key, default, browse_mode) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=8)
            entry = ttk.Entry(form_frame, textvariable=self.setup_vars[key], width=50)
            entry.grid(row=i, column=1, padx=10, pady=8)
            self.setup_vars[key].set(default)
            
            if browse_mode:
                btn_browse = tk.Button(form_frame, text="BROWSE", 
                                     command=lambda v=self.setup_vars[key], m=browse_mode: self.browse_path(v, m),
                                     **self.btn_style, width=10)
                btn_browse.grid(row=i, column=2, padx=5, pady=8)
            
        check_frame = tk.Frame(form_frame, bg=self.bg_color)
        check_frame.grid(row=len(fields), column=1, sticky="w", pady=10)
        tk.Checkbutton(check_frame, text="Debug Mode", variable=self.setup_vars["debug"], bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color, activeforeground=self.fg_color, selectcolor=self.btn_color).pack(side="left", padx=5)
        tk.Checkbutton(check_frame, text="Clean Log", variable=self.setup_vars["clean_log"], bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color, activeforeground=self.fg_color, selectcolor=self.btn_color).pack(side="left", padx=5)

        btn_confirm = tk.Button(self.setup_frame, text="CONFIRM SETTINGS", command=self.confirm_setup, **self.btn_style, width=20, height=2)
        btn_confirm.pack(side="bottom", anchor="se", pady=20)

    def confirm_setup(self):
        if not self.setup_vars["ip"].get() or not self.setup_vars["host_name"].get() or not self.setup_vars["workspace"].get():
            self.show_error("IP, Host Name and Workspace are mandatory!")
            return
            
        summary = "CONFIGURATION SUMMARY\n" + "="*30 + "\n\n"
        for key, var in self.setup_vars.items():
            if isinstance(var.get(), bool): continue
            summary += f"{key.replace('_', ' ').upper():<15}: {var.get()}\n"
            
        confirm_win = tk.Toplevel(self.root)
        confirm_win.title("Confirm Kevin Configuration")
        confirm_win.geometry("900x700")
        confirm_win.configure(bg=self.bg_color)
        self.center_window(confirm_win)
        
        tk.Label(confirm_win, text=summary, justify="left", bg=self.bg_color, fg=self.fg_color, font=("Consolas", 12), padx=40, pady=40).pack(expand=True, fill="both")
        
        btns = ttk.Frame(confirm_win)
        btns.pack(fill="x", pady=20, padx=40)
        
        tk.Button(btns, text="MODIFIY", command=confirm_win.destroy, **self.btn_style, width=15).pack(side="left")
        tk.Button(btns, text="START ENGINE", command=lambda: self.start_toolsuite(confirm_win), **self.btn_style, width=15).pack(side="right")

    def start_toolsuite(self, confirm_win):
        confirm_win.destroy()
        self.setup_frame.destroy()
        
        try:
            self.tool_suite = ToolSuiteInitializer(
                DEBUG=self.setup_vars["debug"].get(),
                CLEAN=self.setup_vars["clean_log"].get(),
                base_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                IP=self.setup_vars["ip"].get(),
                COMMON_NAME=self.setup_vars["common_name"].get(),
                HOST_NAME=self.setup_vars["host_name"].get(),
                UDP_SCAN=False, # Disabled by default as per request
                WORKSPACE_PATH=self.setup_vars["workspace"].get(),
                VPN_PATH=self.setup_vars["vpn"].get(),
                ALIAS=self.setup_vars["alias"].get()
            )
            
            # Monkey patch log_actions
            original_log = self.tool_suite.log_actions
            def patched_log(message):
                original_log(message)
                self.log_queue.put(message)
            self.tool_suite.log_actions = patched_log
            
            self.create_main_window()
            
            self.add_job("INIT", "Workspace & Connection")
            threading.Thread(target=self.init_task_thread, daemon=True).start()
            
        except Exception as e:
            self.show_error(f"Failed to initialize ToolSuite: {e}")
            self.create_setup_screen()

    def init_task_thread(self):
        try:
            success = self.tool_suite.setup()
            if success:
                self.update_job("INIT", "done")
                # Auto start nmap if it was checked in GUI or passed in CLI
                if hasattr(self, 'setup_vars'):
                    if self.setup_vars["nmap"].get():
                        self.start_nmap_task()
                elif hasattr(self, 'args_nmap_requested') and self.args_nmap_requested:
                    self.start_nmap_task()
            else:
                self.update_job("INIT", "error")
        except Exception as e:
            self.update_job("INIT", "error")
            self.log_queue.put(f"[ERROR] {e}")

    def start_nmap_task(self):
        self.add_job("NMAP", "Scanning Target")
        threading.Thread(target=self.nmap_task_thread, daemon=True).start()

    def nmap_task_thread(self):
        try:
            self.tool_suite.call_nmap()
            self.update_job("NMAP", "done")
            self.root.after(0, self.refresh_overview)
        except Exception as e:
            self.update_job("NMAP", "error")
            self.log_queue.put(f"[ERROR] Nmap failed: {e}")

    def create_main_window(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        
        self.tab_overview = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_dora = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_frank = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_creds = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_notes = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_settings = tk.Frame(self.notebook, bg=self.bg_color)
        
        self.notebook.add(self.tab_overview, text="OVERVIEW")
        self.notebook.add(self.tab_dora, text="DORA")
        self.notebook.add(self.tab_frank, text="FRANK")
        self.notebook.add(self.tab_creds, text="CREDENTIALS")
        self.notebook.add(self.tab_notes, text="TAKE A NOTE")
        self.notebook.add(self.tab_settings, text="SETTINGS")
        
        self.setup_overview_tab()
        self.setup_dora_tab()
        self.setup_frank_tab()
        self.setup_creds_tab()
        self.setup_notes_tab()
        self.setup_settings_tab()
        
        # Bottom Terminal/Log
        log_frame = ttk.LabelFrame(self.root, text="TERMINAL LOG")
        log_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, bg="#000000", fg="#ffffff", font=("Consolas", 10), padx=5, pady=5)
        self.log_text.pack(expand=True, fill="both")
        self.log_text.config(state="disabled")
        
        # Terminal Input for sudo etc.
        input_frame = ttk.Frame(log_frame)
        input_frame.pack(fill="x", pady=2)
        ttk.Label(input_frame, text="TERMINAL INPUT:").pack(side="left", padx=5)
        self.terminal_input = ttk.Entry(input_frame)
        self.terminal_input.pack(side="left", fill="x", expand=True, padx=5)
        self.terminal_input.bind("<Return>", self.send_to_terminal)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Kevin Engine Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=(5, 2))
        self.status_bar.pack(side="bottom", fill="x")

    def send_to_terminal(self, event=None):
        cmd = self.terminal_input.get()
        if cmd:
            self.log_queue.put(f"INPUT > {cmd}")
            os.write(self.stdin_write_fd, (cmd + "\n").encode())
            self.terminal_input.delete(0, tk.END)

    def setup_overview_tab(self):
        left_frame = ttk.Frame(self.tab_overview, width=250)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Label(left_frame, text="JOB POOL", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        self.jobs_canvas = tk.Canvas(left_frame, bg=self.bg_color, highlightthickness=0)
        self.jobs_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.jobs_canvas.yview)
        self.jobs_frame = ttk.Frame(self.jobs_canvas)
        
        self.jobs_frame.bind("<Configure>", lambda e: self.jobs_canvas.configure(scrollregion=self.jobs_canvas.bbox("all")))
        self.jobs_canvas.create_window((0, 0), window=self.jobs_frame, anchor="nw")
        self.jobs_canvas.configure(yscrollcommand=self.jobs_scroll.set)
        
        self.jobs_canvas.pack(side="left", fill="both", expand=True)
        self.jobs_scroll.pack(side="right", fill="y")
        
        center_frame = ttk.Frame(self.tab_overview)
        center_frame.pack(side="left", expand=True, fill="both", padx=20, pady=20)
        
        header = ttk.Label(center_frame, text="KEVIN ENGINE", style="Header.TLabel")
        header.pack(pady=20)
        
        self.info_box = tk.Text(center_frame, height=12, width=65, bg=self.entry_bg, fg=self.fg_color, font=("Consolas", 12), padx=15, pady=15, relief=tk.FLAT)
        self.info_box.pack(pady=10)
        self.info_box.config(state="disabled")
        
        btn_browser = tk.Button(center_frame, text="OPEN BROWSER", command=self.open_browser, **self.btn_style, width=20)
        btn_browser.pack(pady=10)
        self.add_tooltip(btn_browser, "Open http://target in your default browser")
        
        btn_pool = ttk.Frame(center_frame)
        btn_pool.pack(side="bottom", fill="x", pady=40)
        
        btn_dora = tk.Button(btn_pool, text="LAUNCH DORA", command=lambda: self.notebook.select(self.tab_dora), **self.btn_style, width=20)
        btn_dora.pack(side="left", padx=10, expand=True)
        self.add_tooltip(btn_dora, "Dora: VHost & Directory Enumeration Engine")
        
        btn_cred = tk.Button(btn_pool, text="NEW CREDENTIAL", command=self.show_add_cred_dialog, **self.btn_style, width=20)
        btn_cred.pack(side="left", padx=10, expand=True)
        self.add_tooltip(btn_cred, "Store a new discovered credential (username/password)")

    def add_tooltip(self, widget, text):
        widget.bind("<Enter>", lambda e: self.status_var.set(text))
        widget.bind("<Leave>", lambda e: self.status_var.set("Kevin Engine Ready"))

    def setup_dora_tab(self):
        config_frame = ttk.LabelFrame(self.tab_dora, text="DORA CONFIGURATION")
        config_frame.pack(fill="x", padx=20, pady=20)
        
        self.dora_vars = {
            "dir": tk.BooleanVar(value=True),
            "vhost": tk.BooleanVar(value=True),
            "fuzz": tk.BooleanVar(value=False)
        }
        
        tk.Checkbutton(config_frame, text="Directory Scan", variable=self.dora_vars["dir"], bg=self.bg_color, fg=self.fg_color, selectcolor=self.btn_color, activebackground=self.bg_color).pack(side="left", padx=15, pady=15)
        tk.Checkbutton(config_frame, text="VHost Scan", variable=self.dora_vars["vhost"], bg=self.bg_color, fg=self.fg_color, selectcolor=self.btn_color, activebackground=self.bg_color).pack(side="left", padx=15, pady=15)
        tk.Checkbutton(config_frame, text="Fuzzing", variable=self.dora_vars["fuzz"], bg=self.bg_color, fg=self.fg_color, selectcolor=self.btn_color, activebackground=self.bg_color).pack(side="left", padx=15, pady=15)
        
        tk.Button(config_frame, text="EXECUTE DORA", command=self.launch_dora, **self.btn_style, width=15).pack(side="right", padx=15)
        
        results_frame = ttk.Frame(self.tab_dora)
        results_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        search_frame = ttk.Frame(results_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(search_frame, text="FILTER:").pack(side="left", padx=5)
        self.dora_search_var = tk.StringVar()
        self.dora_search_var.trace_add("write", lambda *args: self.refresh_dora_results())
        ttk.Entry(search_frame, textvariable=self.dora_search_var).pack(side="left", fill="x", expand=True)
        
        self.dora_results_tree = ttk.Treeview(results_frame, columns=("Type", "URL"), show="headings")
        self.dora_results_tree.heading("Type", text="SCAN TYPE")
        self.dora_results_tree.heading("URL", text="FOUND TARGET")
        self.dora_results_tree.pack(expand=True, fill="both")
        self.dora_results_tree.bind("<Double-1>", self.on_dora_click)

    def setup_frank_tab(self):
        ttk.Label(self.tab_frank, text="FRANK'S INTELLIGENCE REPORT", font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        self.frank_text = scrolledtext.ScrolledText(self.tab_frank, bg=self.entry_bg, fg=self.fg_color, font=("Consolas", 11), padx=10, pady=10)
        self.frank_text.pack(expand=True, fill="both", padx=20, pady=10)
        
        export_frame = ttk.Frame(self.tab_frank)
        export_frame.pack(fill="x", padx=20, pady=20)
        ttk.Label(export_frame, text="CHEATSHEETS:").pack(side="left", padx=5)
        self.frank_cs_var = tk.StringVar()
        self.frank_cs_combo = ttk.Combobox(export_frame, textvariable=self.frank_cs_var, state="readonly", width=30)
        self.frank_cs_combo.pack(side="left", padx=10)
        
        tk.Button(export_frame, text="EXPORT TO WORKSPACE", command=self.export_frank_cs, **self.btn_style, width=20).pack(side="left", padx=10)
        tk.Button(export_frame, text="RE-RUN FRANK", command=self.refresh_frank, **self.btn_style, width=15).pack(side="right")

    def setup_creds_tab(self):
        top_frame = ttk.Frame(self.tab_creds)
        top_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(top_frame, text="SEARCH CREDENTIALS:").pack(side="left", padx=5)
        self.creds_search_var = tk.StringVar()
        self.creds_search_var.trace_add("write", lambda *args: self.refresh_creds_list())
        ttk.Entry(top_frame, textvariable=self.creds_search_var).pack(side="left", fill="x", expand=True, padx=10)
        
        self.creds_show_all = tk.BooleanVar(value=True)
        tk.Checkbutton(top_frame, text="Show All", variable=self.creds_show_all, command=self.refresh_creds_list, bg=self.bg_color, fg=self.fg_color, selectcolor=self.btn_color, activebackground=self.bg_color).pack(side="left")
        
        self.creds_list = ttk.Treeview(self.tab_creds, columns=("User", "Password", "URL"), show="headings")
        self.creds_list.heading("User", text="USERNAME")
        self.creds_list.heading("Password", text="PASSWORD")
        self.creds_list.heading("URL", text="REFERRED URL")
        self.creds_list.pack(expand=True, fill="both", padx=20, pady=10)
        self.creds_list.bind("<<TreeviewSelect>>", self.on_cred_select)
        
        actions_frame = ttk.LabelFrame(self.tab_creds, text="CREDENTIAL ACTIONS")
        actions_frame.pack(fill="x", padx=20, pady=20)
        
        self.selected_cred = None
        tk.Button(actions_frame, text="COPY URL", command=lambda: self.copy_to_clipboard("url"), **self.btn_style, width=15).grid(row=0, column=0, padx=20, pady=15)
        tk.Button(actions_frame, text="COPY USER", command=lambda: self.copy_to_clipboard("user"), **self.btn_style, width=15).grid(row=0, column=1, padx=20, pady=15)
        tk.Button(actions_frame, text="COPY PASS", command=lambda: self.copy_to_clipboard("pass"), **self.btn_style, width=15).grid(row=0, column=2, padx=20, pady=15)
        tk.Button(actions_frame, text="EDIT / UPDATE", command=self.edit_selected_cred, **self.btn_style, width=15).grid(row=0, column=3, padx=20, pady=15)

    def setup_notes_tab(self):
        header = ttk.Frame(self.tab_notes)
        header.pack(fill="x", padx=20, pady=10)
        ttk.Label(header, text="WORKSPACE NOTES", font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Button(header, text="SAVE NOTES", command=self.save_notes, **self.btn_style, width=15).pack(side="right")
        
        self.notes_text = scrolledtext.ScrolledText(self.tab_notes, bg=self.entry_bg, fg=self.fg_color, font=("Consolas", 11), undo=True, padx=10, pady=10)
        self.notes_text.pack(expand=True, fill="both", padx=20, pady=10)
        self.root.bind("<Control-s>", lambda e: self.save_notes())

    def setup_settings_tab(self):
        container = ttk.Frame(self.tab_settings)
        container.pack(expand=True, fill="both", padx=40, pady=40)
        
        ttk.Label(container, text="GLOBAL CONFIGURATION", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 25), sticky="w")
        
        self.setting_vars = {}
        row = 1
        
        # User settings
        ttk.Label(container, text="USER PREFERENCES", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, columnspan=2, pady=10, sticky="w")
        row += 1
        
        user_map = [
            ("Theme (dark/light)", "theme", None), 
            ("Seclists Path", "seclist_path", "dir"), 
            ("Dirbuster Path", "dirbuster", "dir"), 
            ("Dirb Path", "dirb", "dir")
        ]
        for label, key, browse_mode in user_map:
            ttk.Label(container, text=label+":").grid(row=row, column=0, sticky="e", padx=10, pady=5)
            var = tk.StringVar(value=str(self.config["user_settings"].get(key, "")))
            self.setting_vars[f"user_{key}"] = var
            ttk.Entry(container, textvariable=var, width=50).grid(row=row, column=1, padx=10, pady=5)
            if browse_mode:
                tk.Button(container, text="BROWSE", 
                          command=lambda v=var, m=browse_mode: self.browse_path(v, m),
                          **self.btn_style, width=10).grid(row=row, column=2, padx=5, pady=5)
            row += 1
            
        # Gobuster settings
        ttk.Label(container, text="GOBUSTER SETTINGS", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, columnspan=2, pady=20, sticky="w")
        row += 1
        
        gobuster_map = [
            ("Threads", "gobuster_thread", None), 
            ("Dir Wordlist", "dir_wordlist", "file"), 
            ("VHost Wordlist", "vhost_wordlist", "file")
        ]
        for label, key, browse_mode in gobuster_map:
            ttk.Label(container, text=label+":").grid(row=row, column=0, sticky="e", padx=10, pady=5)
            var = tk.StringVar(value=str(self.config["functional_settings"]["gobuster"].get(key, "")))
            self.setting_vars[f"gb_{key}"] = var
            ttk.Entry(container, textvariable=var, width=50).grid(row=row, column=1, padx=10, pady=5)
            if browse_mode:
                tk.Button(container, text="BROWSE", 
                          command=lambda v=var, m=browse_mode: self.browse_path(v, m),
                          **self.btn_style, width=10).grid(row=row, column=2, padx=5, pady=5)
            row += 1
            
        tk.Button(container, text="SAVE GLOBAL CONFIG", command=self.save_all_settings, **self.btn_style, width=25).grid(row=row, column=1, pady=30, sticky="e")

    def save_all_settings(self):
        for full_key, var in self.setting_vars.items():
            if full_key.startswith("user_"):
                self.config["user_settings"][full_key[5:]] = var.get()
            elif full_key.startswith("gb_"):
                self.config["functional_settings"]["gobuster"][full_key[3:]] = var.get()
        self.save_config()
        messagebox.showinfo("Settings", "Global configuration updated successfully!")

    def refresh_overview(self):
        if not self.tool_suite: return
        try:
            with open(self.tool_suite.INFO_FILE, 'r') as f:
                data = json.load(f)
            
            display_text = "TARGET INFORMATION\n" + "="*40 + "\n\n"
            keys = ["ip", "common_name", "host_name", "machine_OS"]
            for key in keys:
                val = data.get(key, "N/A")
                display_text += f"{key.replace('_', ' ').upper():<15}: {val}\n"
            
            self.info_box.config(state="normal")
            self.info_box.delete("1.0", tk.END)
            self.info_box.insert(tk.END, display_text)
            self.info_box.config(state="disabled")
            
            self.refresh_dora_results(data)
            self.load_notes()
            self.refresh_frank()
        except: pass

    def refresh_dora_results(self, data=None):
        if not self.tool_suite: return
        if not data:
            try:
                with open(self.tool_suite.INFO_FILE, 'r') as f:
                    data = json.load(f)
            except: return
            
        self.dora_results_tree.delete(*self.dora_results_tree.get_children())
        query = self.dora_search_var.get().lower()
        
        vhosts = data.get(self.utils.machine_vhosts(), [])
        for v in vhosts:
            url = f"http://{v}"
            if query in url.lower():
                self.dora_results_tree.insert("", "end", values=("VHost", url))

    def on_dora_click(self, event):
        item = self.dora_results_tree.selection()
        if item:
            url = self.dora_results_tree.item(item[0], "values")[1]
            webbrowser.open(url)

    def open_browser(self):
        host = self.setup_vars["host_name"].get()
        if host: webbrowser.open(f"http://{host}")

    def show_add_cred_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Credential")
        dialog.geometry("500x400")
        dialog.configure(bg=self.bg_color)
        self.center_window(dialog)
        
        vars = {"url": tk.StringVar(), "user": tk.StringVar(), "pass": tk.StringVar(), "note": tk.StringVar()}
        fields = [("URL:", "url"), ("USERNAME:", "user"), ("PASSWORD:", "pass"), ("NOTES:", "note")]
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=20, pady=15, sticky="e")
            ttk.Entry(dialog, textvariable=vars[key], width=35).grid(row=i, column=1, padx=20, pady=15)
            
        tk.Button(dialog, text="SAVE CREDENTIAL", command=lambda: self.save_new_cred(vars, dialog), **self.btn_style, width=20).grid(row=4, column=1, pady=30)

    def save_new_cred(self, vars, dialog):
        cesare = Cesare(self.tool_suite)
        cred = {"referred_url": vars["url"].get(), "username": vars["user"].get(), "password": vars["pass"].get(), "notes": vars["note"].get()}
        try:
            cesare.add_cred(cred)
            dialog.destroy()
            self.refresh_creds_list()
        except Exception as e:
            self.show_error(str(e))

    def refresh_creds_list(self):
        if not self.tool_suite: return
        self.creds_list.delete(*self.creds_list.get_children())
        cesare = Cesare(self.tool_suite)
        try:
            creds = cesare.find_cred("")
            if not creds: return
            query = self.creds_search_var.get().lower()
            for id, data in creds.items():
                u, p, r = data.get('username', ''), data.get('password', ''), data.get('referred_url', '')
                if query and not (query in u.lower() or query in p.lower() or query in r.lower()):
                    continue
                self.creds_list.insert("", "end", iid=id, values=(u, p, r))
        except: pass

    def on_cred_select(self, event):
        sel = self.creds_list.selection()
        if sel:
            self.selected_cred_id = sel[0]
            cesare = Cesare(self.tool_suite)
            creds = cesare.find_cred("")
            self.selected_cred = creds.get(self.selected_cred_id)

    def copy_to_clipboard(self, type):
        if not self.selected_cred: return
        val = self.selected_cred.get({'url':'referred_url', 'user':'username', 'pass':'password'}[type], '')
        self.root.clipboard_clear()
        self.root.clipboard_append(val)
        self.status_var.set(f"Copied {type} to clipboard")

    def edit_selected_cred(self):
        if not self.selected_cred: return
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Credential")
        dialog.geometry("500x400")
        dialog.configure(bg=self.bg_color)
        self.center_window(dialog)
        
        vars = {
            "url": tk.StringVar(value=self.selected_cred.get('referred_url', '')),
            "user": tk.StringVar(value=self.selected_cred.get('username', '')),
            "pass": tk.StringVar(value=self.selected_cred.get('password', '')),
            "note": tk.StringVar(value=self.selected_cred.get('notes', ''))
        }
        fields = [("URL:", "url"), ("USERNAME:", "user"), ("PASSWORD:", "pass"), ("NOTES:", "note")]
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=20, pady=15, sticky="e")
            ttk.Entry(dialog, textvariable=vars[key], width=35).grid(row=i, column=1, padx=20, pady=15)
            
        def update():
            cesare = Cesare(self.tool_suite)
            try:
                cesare.update_cred({self.selected_cred_id: {
                    "referred_url": vars["url"].get(), "username": vars["user"].get(),
                    "password": vars["pass"].get(), "notes": vars["note"].get()
                }})
                dialog.destroy()
                self.refresh_creds_list()
            except Exception as e: self.show_error(str(e))
        tk.Button(dialog, text="UPDATE CREDENTIAL", command=update, **self.btn_style, width=20).grid(row=4, column=1, pady=30)

    def launch_dora(self):
        opts = "".join([k[0] for k,v in self.dora_vars.items() if v.get()])
        if not opts: return self.show_error("Select at least one scan type!")
        self.add_job("DORA", f"Gobuster {opts.upper()}")
        threading.Thread(target=self.dora_task_thread, args=(opts,), daemon=True).start()

    def dora_task_thread(self, opts):
        try:
            Dora(self.tool_suite).go_bastard(opts)
            self.update_job("DORA", "done")
            self.root.after(0, self.refresh_overview)
        except Exception as e:
            self.update_job("DORA", "error")
            self.log_queue.put(f"[DORA ERROR] {e}")

    def refresh_frank(self):
        self.add_job("FRANK", "OSINT & Port Analysis")
        threading.Thread(target=self.frank_task_thread, daemon=True).start()

    def frank_task_thread(self):
        try:
            Frank(self.tool_suite).enlight_me()
            self.update_job("FRANK", "done")
            self.root.after(0, self.display_frank_report)
        except Exception as e:
            self.update_job("FRANK", "error")

    def display_frank_report(self):
        try:
            with open(self.tool_suite.FRANK_FILE, 'r') as f: content = f.read()
            self.frank_text.delete("1.0", tk.END)
            self.frank_text.insert(tk.END, content)
            frank = Frank(self.tool_suite)
            self.frank_cs_combo['values'] = list(frank.CHEATSHEETS.keys())
        except: pass

    def export_frank_cs(self):
        sel = self.frank_cs_var.get()
        if not sel: return
        try:
            Frank(self.tool_suite).export_file(sel)
            messagebox.showinfo("Export", f"Cheatsheet {sel} exported to workspace.")
        except Exception as e: self.show_error(str(e))

    def save_notes(self):
        if not self.tool_suite: return
        try:
            with open(os.path.join(self.tool_suite.MISC_PATH, 'notes.txt'), 'w') as f:
                f.write(self.notes_text.get("1.0", tk.END))
            self.status_var.set("Notes saved successfully")
        except: pass

    def load_notes(self):
        if not self.tool_suite: return
        path = os.path.join(self.tool_suite.MISC_PATH, 'notes.txt')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f: content = f.read()
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert(tk.END, content)
            except: pass

    def add_job(self, job_id, name):
        self.active_jobs[job_id] = {'name': name, 'status': 'running'}
        self.refresh_jobs_ui()

    def update_job(self, job_id, status):
        if job_id in self.active_jobs:
            self.active_jobs[job_id]['status'] = status
            self.refresh_jobs_ui()

    def refresh_jobs_ui(self):
        for w in self.jobs_frame.winfo_children(): w.destroy()
        for jid, info in self.active_jobs.items():
            f = ttk.Frame(self.jobs_frame)
            f.pack(fill="x", pady=5)
            c = tk.Canvas(f, width=15, height=15, bg=self.bg_color, highlightthickness=0)
            c.pack(side="left", padx=5)
            color = {"running":"yellow", "done":"#4caf50", "error":"#f44336"}.get(info['status'], "gray")
            c.create_oval(2, 2, 13, 13, fill=color, outline="")
            ttk.Label(f, text=f"{jid}: {info['status'].upper()}", font=("Segoe UI", 9, "bold")).pack(side="left")
            ttk.Label(self.jobs_frame, text=f"  {info['name']}", font=("Segoe UI", 8), foreground="gray").pack(fill="x")

    def process_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_text.config(state="normal")
            
            # ANSI Color Support
            ansi_colors = {
                '31': '#ff5252', '32': '#69f0ae', '33': '#ffd740', '34': '#40c4ff',
                '35': '#e040fb', '36': '#18ffff', '37': '#ffffff', '91': '#ff1744', 
                '92': '#00e676', '93': '#ffea00', '94': '#2979ff', '0': self.fg_color
            }
            
            # Simple regex to find ANSI codes
            parts = re.split(r'\x1b\[([0-9;]*)m', msg)
            current_fg = self.fg_color
            
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        tag_name = f"color_{current_fg.replace('#', '')}"
                        self.log_text.tag_config(tag_name, foreground=current_fg)
                        self.log_text.insert(tk.END, part, tag_name)
                else:
                    codes = part.split(';')
                    for code in codes:
                        if code == '0' or not code:
                            current_fg = self.fg_color
                        elif code in ansi_colors:
                            current_fg = ansi_colors[code]
            
            # Add newline if not present
            if not msg.endswith('\n'):
                self.log_text.insert(tk.END, "\n")
            
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
        self.root.after(100, self.process_log_queue)

def launch_gui(args=None):
    root = tk.Tk()
    app = KevinGUI(root, args)
    def on_closing():
        if app.tool_suite:
            if messagebox.askokcancel("QUIT KEVIN", "Do you want to shut down Kevin and clean up?"):
                app.tool_suite.turn_off_vpn()
                app.tool_suite.clean_hosts()
                root.destroy()
        else: root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
