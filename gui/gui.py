import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import cv2
import time
import os

LOG_DIR = "csv_logs"

# --- Simple Tooltip helper for ttk/tk widgets ---
class ToolTip:
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        widget.bind("<Enter>", self._enter)
        widget.bind("<Leave>", self._leave)
        widget.bind("<ButtonPress>", self._leave)

    def _enter(self, event=None):
        self._schedule()

    def _leave(self, event=None):
        self._unschedule()
        self._hidetip()

    def _schedule(self):
        self._unschedule()
        self.id = self.widget.after(self.delay, self._showtip)

    def _unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def _showtip(self, event=None):
        if self.tipwindow or not self.text:
            return
        # Some widgets (e.g., ttk.Button) don't support bbox("insert").
        if self.widget.winfo_ismapped():
            try:
                x, y, cx, cy = self.widget.bbox("insert")
            except Exception:
                x, y, cx, cy = (0, 0, 0, 0)
        else:
            x, y, cx, cy = (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 20
        y = y + self.widget.winfo_rooty() + 35
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#333333", foreground="white",
                         relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=4)

    def _hidetip(self):
        tw = self.tipwindow
        if tw:
            tw.destroy()
            self.tipwindow = None

class guiwindow:
    def __init__(self, get_frame_callback, status_callback=None, start_camera_callback=None):
        self.root = tk.Tk()
        self.root.title("Security Screening System")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        self.root.configure(bg='#1e1e1e')

        # --- Style ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background='#1e1e1e')
        self.style.configure("TLabel", background='#1e1e1e', foreground='white', font=("Segoe UI", 12))
        self.style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        self.style.configure("Status.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), foreground="white")
        self.style.map("TButton",
                       background=[('active', '#005f5f'), ('!disabled', '#008080')],
                       foreground=[('disabled', '#a9a9a9')])

        # --- Header ---
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(pady=20)
        self.header_label = ttk.Label(self.header_frame, text="Security Screening System", style="Title.TLabel")
        self.header_label.pack()

        # --- Video Feed ---
        self.video_frame = ttk.Frame(self.root, padding=6)
        self.video_frame.pack()
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()
        self.video_label.configure(background='black')


        # --- Status Panel ---
        self.status_panel = ttk.Frame(self.root, padding=10)
        self.status_panel.pack(pady=20)
        self.status_indicator = tk.Canvas(self.status_panel, width=20, height=20, bg='#1e1e1e', highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.status_label = ttk.Label(self.status_panel, text="Initializing system...", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        self.update_status_indicator('gray')


        # --- Control Panel ---
        self.control_panel = ttk.Frame(self.root, padding=10)
        self.control_panel.pack(pady=10)

        self.start_button = ttk.Button(self.control_panel, text="▶️ Start Camera", command=self.start_camera, width=20)
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ttk.Button(self.control_panel, text="⏸️ Pause", command=self.toggle_pause, width=20, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=10)

        self.export_log_button = ttk.Button(self.control_panel, text="📊 Export Log", command=self.export_log, width=20, state="disabled")
        self.export_log_button.grid(row=0, column=2, padx=10)

        # About button (non-intrusive)
        self.about_button = ttk.Button(self.control_panel, text="ℹ️ About", command=self.show_about, width=14)
        self.about_button.grid(row=0, column=3, padx=10)

        # Tooltips
        ToolTip(self.start_button, "Start camera (Ctrl+S). Initializes webcam and status announcements.")
        ToolTip(self.pause_button, "Pause/Resume detection (Space). Keeps the last frame visible.")
        ToolTip(self.export_log_button, "Export csv_logs/security_log.csv to a chosen location (Ctrl+E).")
        ToolTip(self.about_button, "About this application.")

        # Keyboard shortcuts
        self.root.bind("<Control-s>", lambda e: self.start_camera())
        self.root.bind_all("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Control-e>", lambda e: self.export_log())


        self.get_frame = get_frame_callback
        self.status_callback = status_callback
        self.start_camera_callback = start_camera_callback
        
        self._get_is_paused = None
        self._set_is_paused = None
        self._get_pause_start_time = None
        self._set_pause_start_time = None
        self._get_paused_names_time = None
        self._set_paused_names_time = None
        self._get_detection_time = None

        self.camera_started = False
        self.update_frame()

    def update_status_indicator(self, color):
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def export_log(self):
        log_file = os.path.join(LOG_DIR, "security_log.csv")
        if os.path.exists(log_file):
            export_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile="exported_log.csv",
                title="Choose Export Location"
            )
            if export_file:
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    with open(export_file, "w", encoding="utf-8") as ef:
                        ef.write(content)
                    self.update_status(f"Log exported successfully to {export_file}!", color='green')
                except Exception as e:
                    self.update_status(f"Export failed: {e}", color='red')
            else:
                self.update_status("Export cancelled by user.", color='orange')
        else:
            self.update_status("No log file found!", color='red')

    def set_pause_vars(
        self,
        get_is_paused, set_is_paused,
        get_pause_start_time, set_pause_start_time,
        get_paused_names_time, set_paused_names_time,
        get_detection_time
    ):
        self._get_is_paused = get_is_paused
        self._set_is_paused = set_is_paused
        self._get_pause_start_time = get_pause_start_time
        self._set_pause_start_time = set_pause_start_time
        self._get_paused_names_time = get_paused_names_time
        self._set_paused_names_time = set_paused_names_time
        self._get_detection_time = get_detection_time

    def toggle_pause(self):
        if not self.camera_started:
            self.update_status("Camera not started", "gray")
            return

        if not self._get_is_paused():
            self._set_is_paused(True)
            self._set_pause_start_time(time.time())
            detection_time = self._get_detection_time()
            paused_names_time = {name: time.time() - t for name, t in detection_time.items()}
            self._set_paused_names_time(paused_names_time)
            self.pause_button.config(text="▶️ Resume")
            self.style.map("TButton", background=[('active', '#005f5f'), ('!disabled', '#00af5f')])

        else:
            self._set_is_paused(False)
            pause_duration = time.time() - self._get_pause_start_time()
            detection_time = self._get_detection_time()
            paused_names_time = self._get_paused_names_time()
            for name in detection_time:
                detection_time[name] = time.time() - paused_names_time.get(name, 0)
            self._set_pause_start_time(None)
            self._set_paused_names_time({})
            self.pause_button.config(text="⏸️ Pause")
            self.style.map("TButton", background=[('active', '#005f5f'), ('!disabled', '#008080')])


    def start_camera(self):
        if not self.camera_started:
            if self.start_camera_callback:
                self.start_camera_callback()
            self.camera_started = True
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.export_log_button.config(state="normal")
            self.update_status("Camera starting...", color="green")
        else:
            self.update_status("Camera already started", color="green")

    def update_frame(self):
        frame = self.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

        if self.status_callback:
            status_text, status_color = self.status_callback()
            self.update_status(status_text, status_color)

        self.root.after(10, self.update_frame)

    def update_status(self, message, color='white'):
        self.status_label.config(text=message, foreground=color)
        self.update_status_indicator(color)

    def show_about(self):
        message = (
            "Security Screening System\n\n"
            "This GUI provides Start/Pause controls, status feedback, and log export.\n"
            "Shortcuts: Ctrl+S Start, Space Pause/Resume, Ctrl+E Export Log.\n"
            
        )
        messagebox.showinfo("About", message)

    def run(self):
        self.root.mainloop()