# gui/video_window.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2

class guiwindow:
    def __init__(self, get_frame_callback, status_callback=None):
        self.root = tk.Tk()
        self.root.title("Face Recognition Security System")
        self.root.geometry("900x750")  # Increased height for status area
        self.root.resizable(False, False)  # lock resizing
        self.root.configure(bg='#2c2c2c')  # Dark background

        # Video frame
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
        self.update_frame()

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
