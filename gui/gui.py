# gui/video_window.py
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import time
import os
Log_DIR = "logs"
class guiwindow:
    def __init__(self, get_frame_callback, status_callback=None):
        self.root = tk.Tk()
        self.root.title("Face Recognition Security System")
        self.root.geometry("900x750")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c2c2c')

        self.label = tk.Label(self.root, bg='#2c2c2c')
        self.label.pack(pady=10)

        # Status message area
        self.status_frame = tk.Frame(self.root, bg='#2c2c2c')
        self.status_frame.pack(pady=10)

        # Status label with styling
        self.status_label = tk.Label(
            self.status_frame,
            text="Initializing system...",
            font=("Arial", 14, "bold"),
            fg='#ffffff',
            bg='#404040',
            padx=20,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        self.status_label.pack()

        self.get_frame = get_frame_callback
        self.status_callback = status_callback

        # Pause/Resume variables, set after initialization
        self._get_is_paused = None
        self._set_is_paused = None
        self._get_pause_start_time = None
        self._set_pause_start_time = None
        self._get_paused_names_time = None
        self._set_paused_names_time = None
        self._get_detection_time = None

        self.button_frame = tk.Frame(self.root, bg='#2c2c2c')
        self.button_frame.pack(pady=5)
        self.pause_button = tk.Button(
            self.button_frame, text="⏸️ Pause", font=("Arial", 12, "bold"), width=10,
            command=self.toggle_pause, bg="#ffaa00", fg="#222"
        )
        self.pause_button.grid(row=0, column=0, padx=5, pady=5)
        self.export_log_button = tk.Button(
            self.button_frame, text="📊 Export Log", font=("Arial", 12, "bold"), width=10,
            command=self.export_log, bg="#00aaff", fg="#222"
        )
        self.export_log_button.grid(row=0, column=1, padx=5, pady=5)
        self.update_frame()
    def export_log(self):
        log_file = os.path.join(Log_DIR, "security_log.csv")
        if os.path.exists(log_file):
            # Open a file dialog for the user to choose the export location
            root = tk.Tk()
            root.withdraw()  # Hide the main Tk window
            export_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile="exported_log.csv",
                title="Choose Export Location"
            )
            root.destroy()
            if export_file:  # If the user did not cancel
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    with open(export_file, "w", encoding="utf-8") as ef:
                        ef.write(content)
                    self.update_status(f"Log exported successfully to {export_file}!", color='#00ff00')
                except Exception as e:
                    self.update_status(f"Export failed: {e}", color='#ff0000')
            else:
                self.update_status("Export cancelled by user.", color='#ffaa00')
        else:
            self.update_status("No log file found!", color='#ff0000')
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
        # Use passed-in set/get functions to interact with main.py variables
        if not self._get_is_paused():
            self._set_is_paused(True)
            self._set_pause_start_time(time.time())
            detection_time = self._get_detection_time()
            paused_names_time = {name: time.time() - t for name, t in detection_time.items()}
            self._set_paused_names_time(paused_names_time)
            self.pause_button.config(text="▶️ Resume", bg="#00ff88")
        else:
            self._set_is_paused(False)
            pause_duration = time.time() - self._get_pause_start_time()
            detection_time = self._get_detection_time()
            paused_names_time = self._get_paused_names_time()
            for name in detection_time:
                detection_time[name] = time.time() - paused_names_time.get(name, 0)
            self._set_pause_start_time(None)
            self._set_paused_names_time({})
            self.pause_button.config(text="⏸️ Pause", bg="#ffaa00")

    def update_frame(self):
        frame = self.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.config(image=imgtk)

        # Update status message if callback is available
        if self.status_callback:
            status_text, status_color = self.status_callback()
            self.update_status(status_text, status_color)

        self.root.after(10, self.update_frame)

    def update_status(self, message, color='#ffffff'):
        """Update the status message with optional color"""
        self.status_label.config(text=message, fg=color)

    def run(self):
        self.root.mainloop()
