# gui/video_window.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2

class guiwindow:
    def __init__(self, get_frame_callback):
        self.root = tk.Tk()
        self.root.title("Face Recognition Security System")
        self.root.geometry("900x700")
        self.root.resizable(False, False)  # lock resizing

        self.label = tk.Label(self.root)
        self.label.pack()
        self.get_frame = get_frame_callback
        self.update_frame()

    def update_frame(self):
        frame = self.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.config(image=imgtk)
        self.root.after(10, self.update_frame)

    def run(self):
        self.root.mainloop()
