# gui/video_window.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import shutil
import os
class guiwindow:
    def __init__(self, get_frame_callback):
        self.root = tk.Tk()
        self.root.title("Face Recognition Security System")
        self.root.geometry("900x700")
        self.root.resizable(False, False)  # lock resizing

        self.label = tk.Label(self.root)
        self.label.pack()
        self.get_frame = get_frame_callback
        self.paused = False
        self.paused_button = tk.Button(self.root, text="Pause", command=self.toggle_pause)
        self.paused_button.pack(pady=9)
        self.export= tk.Button(self.root, text="Export logs", command=self.export_logs)
        self.export.pack(pady=9)
        self.update_frame()

    def export_logs(self):
        log_path ="logs/detection_alerts.csv"
        if not os.path.exists(log_path):
            tk.messagebox.showerror("Error", "No logs found to export.")
            return
        export_path =tk.filedialog.asksaveasfilename(defaultextention=".csv", title="save logs", filetypes=[("CSV files", "*.csv")])
        if export_path:
            try:
                shutil.copy(log_path, export_path)
                tk.messagebox.showinfo("Success", "Logs exported successfully.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to export logs: {e}")
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.paused_button.config(text="Resume")
        else:
            self.paused_button.config(text="Pause")
        self.update_frame()
    def update_frame(self):
        frame = self.get_frame(self.paused)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.config(image=imgtk)
        self.root.after(10, self.update_frame)

    def run(self):
        self.root.mainloop()
