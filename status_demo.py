#!/usr/bin/env python3
"""
Demo script to showcase the new status message functionality
This script demonstrates the different status messages that can appear
"""

import time
import tkinter as tk
from gui.gui import guiwindow

class StatusDemo:
    def __init__(self):
        self.demo_states = [
            ("System ready - Please position yourself in front of the camera", '#00ff00'),
            ("👁️ Scanning for faces... Please position yourself in front of the camera", '#ffff00'),
            ("⚠️ Multiple faces detected - Please ensure only one person is in frame", '#ff8800'),
            ("✅ Match found: John Doe (Confidence: 95.2%)", '#00ff00'),
            ("⏱️ Please stand still for 5 seconds - Processing...", '#ffaa00'),
            ("⏱️ Please stand still for 3 seconds - Processing...", '#ffaa00'),
            ("⏱️ Please stand still for 1 seconds - Processing...", '#ffaa00'),
            ("🚨 THREAT DETECTED: John Doe - Security alert triggered!", '#ff0000'),
            ("❌ No match detected. You are safe to go.", '#ff0000'),
            ("✅ SCAN COMPLETE: No match detected - You are safe to proceed", '#00ff00'),
        ]
        self.current_state = 0
        self.last_change = time.time()

    def get_frame(self):
        # Return a dummy frame (None for demo)
        return None

    def get_status(self):
        # Change status every 2 seconds for demo
        if time.time() - self.last_change > 2:
            self.current_state = (self.current_state + 1) % len(self.demo_states)
            self.last_change = time.time()

        return self.demo_states[self.current_state]

if __name__ == "__main__":
    print("🎬 Starting Status Message Demo...")
    print("This demo will cycle through different status messages every 2 seconds")
    print("Close the window to exit the demo")

    demo = StatusDemo()
    app = guiwindow(get_frame_callback=demo.get_frame, status_callback=demo.get_status)
    app.run()
