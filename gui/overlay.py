import tkinter as tk
from tkinter import ttk
import random
import time
from typing import List, Optional

class ShameOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
        self.haiku_entry = None
        self.timer_label = None
        self.timer_running = False
        self.timer_thread = None
        self.remaining_time = 30  # seconds
        self.shame_messages = [
            "Oh no! You tried to procrastinate!",
            "Back to work, you productivity thief!",
            "Your future self is disappointed!",
            "Is this really what you want to do?",
            "Your goals are crying in the corner!",
            "Your to-do list is getting longer!",
            "Your deadlines are laughing at you!",
            "Your productivity is taking a nap!",
            "Your motivation is on vacation!",
            "Your focus is playing hide and seek!"
        ]

    def show_haiku_challenge(self, app_name: str):
        """Show the haiku challenge overlay."""
        if self.overlay:
            self.overlay.destroy()

        # Create overlay window
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.title("Productivity Challenge")
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.9)
        self.overlay.attributes('-fullscreen', True)
        
        # Make it semi-transparent
        self.overlay.configure(bg='black')
        
        # Center the content
        content_frame = ttk.Frame(self.overlay)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Shame message
        shame_label = ttk.Label(
            content_frame,
            text=random.choice(self.shame_messages),
            font=("Arial", 24, "bold"),
            foreground="red"
        )
        shame_label.pack(pady=20)
        
        # App name
        app_label = ttk.Label(
            content_frame,
            text=f"Blocked App: {app_name}",
            font=("Arial", 18),
            foreground="white"
        )
        app_label.pack(pady=10)
        
        # Haiku instructions
        haiku_label = ttk.Label(
            content_frame,
            text="Write a haiku about productivity to continue:",
            font=("Arial", 16),
            foreground="white"
        )
        haiku_label.pack(pady=10)
        
        # Haiku entry
        self.haiku_entry = tk.Text(
            content_frame,
            height=3,
            width=40,
            font=("Arial", 14)
        )
        self.haiku_entry.pack(pady=10)
        
        # Submit button
        submit_button = ttk.Button(
            content_frame,
            text="Submit Haiku",
            command=self._check_haiku
        )
        submit_button.pack(pady=10)
        
        # Timer label
        self.timer_label = ttk.Label(
            content_frame,
            text=f"Time remaining: {self.remaining_time}s",
            font=("Arial", 14),
            foreground="white"
        )
        self.timer_label.pack(pady=10)
        
        # Start timer
        self.remaining_time = 30
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self._update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _check_haiku(self):
        """Check if the haiku is valid and grant access if it is."""
        haiku = self.haiku_entry.get("1.0", tk.END).strip()
        
        # Basic haiku validation (5-7-5 syllables)
        lines = haiku.split('\n')
        if len(lines) == 3:
            # For now, we'll just check if it's three lines
            # A more sophisticated syllable counter could be added later
            self._grant_access()
        else:
            # Show error message
            error_label = ttk.Label(
                self.overlay,
                text="Please write a proper haiku (3 lines)",
                font=("Arial", 12),
                foreground="red"
            )
            error_label.place(relx=0.5, rely=0.8, anchor='center')
            self.overlay.after(2000, error_label.destroy)

    def _grant_access(self):
        """Grant temporary access to the blocked app."""
        self.timer_running = False
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def _update_timer(self):
        """Update the timer display."""
        while self.timer_running and self.remaining_time > 0:
            self.remaining_time -= 1
            if self.timer_label:
                self.timer_label.config(text=f"Time remaining: {self.remaining_time}s")
            time.sleep(1)
        
        if self.timer_running:
            self._grant_access()

    def is_visible(self) -> bool:
        """Check if the overlay is currently visible."""
        return self.overlay is not None and self.overlay.winfo_exists() 