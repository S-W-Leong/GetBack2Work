import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import json
import random

from window_monitor import WindowMonitor
from point_system import PointSystem
from utils.app_categorizer import AppCategorizer
from app_controller import AppController

class GetBack2Work:
    def __init__(self):
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Initialize components
        self.point_system = PointSystem()
        self.app_categorizer = AppCategorizer()
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("GetB@ck2Work!")
        self.root.geometry("480x600")
        
        # Initialize app controller after GUI
        self.app_controller = AppController(self.point_system, self.root)
        
        # Initialize window monitor
        self.window_monitor = WindowMonitor(self.on_window_change)
        
        # Initialize activity tracking
        self.current_activity = {
            "name": "No activity",
            "start_time": None,
            "points_earned": 0
        }
        
        self.setup_gui()
        
        # Start monitoring
        self.window_monitor.start_monitoring()
        self.app_controller.start_monitoring()

        # Set up periodic updates
        self.root.after(100, self.process_window_queue)
        self.root.after(1000, self.update_stats)

    def setup_gui(self):
        """Set up the main GUI interface."""
        # Configure root window
        self.root.grid_rowconfigure(3, weight=1)  # Make the activity section expandable
        self.root.grid_columnconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # TOP ROW - Points and Streak
        # Points Card
        points_frame = ttk.LabelFrame(main_frame, text="💎 POINTS", padding="5")
        points_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.points_label = ttk.Label(
            points_frame,
            text=f"{self.point_system.current_points}",
            font=("Arial", 36, "bold")
        )
        self.points_label.pack(pady=10)

        # Streak Card
        streak_frame = ttk.LabelFrame(main_frame, text="🎯 TODAY'S STREAK", padding="5")
        streak_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.streak_label = ttk.Label(
            streak_frame,
            text=f"{self.point_system.current_streak} minutes",
            font=("Arial", 24)
        )
        self.streak_label.pack(pady=5)

        self.streak_progress = ttk.Progressbar(
            streak_frame,
            length=200,
            mode='determinate'
        )
        self.streak_progress.pack(pady=5)

        # MIDDLE SECTION - Entertainment Time Bank
        time_bank_frame = ttk.LabelFrame(main_frame, text="🎮 ENTERTAINMENT TIME BANK", padding="5")
        time_bank_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.time_bank_progress = ttk.Progressbar(
            time_bank_frame,
            length=460,
            mode='determinate'
        )
        self.time_bank_progress.pack(pady=10)

        # CURRENT ACTIVITY SECTION
        activity_frame = ttk.LabelFrame(main_frame, text="📊 CURRENT ACTIVITY", padding="5")
        activity_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a canvas with scrollbar for the apps list
        canvas = tk.Canvas(activity_frame)
        scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=canvas.yview)
        self.apps_frame = ttk.Frame(canvas)

        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=self.apps_frame, anchor="nw")
        
        # Bind events for scrolling
        self.apps_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))

        # Dictionary to store app labels
        self.app_labels = {}

        # BOTTOM BUTTONS
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        buy_time_btn = ttk.Button(
            buttons_frame,
            text="🎮 Buy Time",
            command=self.show_buy_time
        )
        buy_time_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))

        settings_btn = ttk.Button(
            buttons_frame,
            text="⚙️ Settings",
            command=self.show_settings
        )
        settings_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

        stats_btn = ttk.Button(
            buttons_frame,
            text="📊 Stats",
            command=self.show_stats
        )
        stats_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))

        # Make buttons equal width
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)

    def show_buy_time(self):
        """Show the buy time dialog."""
        # TODO: Implement buy time dialog
        pass

    def show_settings(self):
        """Show the settings dialog."""
        # TODO: Implement settings dialog
        pass

    def show_stats(self):
        """Show the stats dialog."""
        # TODO: Implement stats dialog
        pass

    def update_activity_display(self):
        """Update the current activity display."""
        # This method is no longer needed as we're showing all apps
        pass

    def process_window_queue(self):
        """Process window updates from the queue."""
        try:
            # Get all current windows
            windows_info = self.window_monitor.get_all_windows_info()
            if windows_info:
                # Clear old labels
                for label in self.app_labels.values():
                    label.destroy()
                self.app_labels.clear()

                # Create new labels for each window
                for i, (process_name, (window_title, _, _)) in enumerate(windows_info.items()):
                    if window_title:  # Only show windows with titles
                        # Create a frame for each app
                        app_frame = ttk.Frame(self.apps_frame)
                        app_frame.pack(fill="x", padx=5, pady=2)

                        # App name and title
                        app_label = ttk.Label(
                            app_frame,
                            text=f"{process_name} - {window_title}",
                            font=("Arial", 10)
                        )
                        app_label.pack(side="left", fill="x", expand=True)
                        self.app_labels[process_name] = app_label

                        # Add block button
                        block_btn = ttk.Button(
                            app_frame,
                            text="🚫",
                            width=3,
                            command=lambda p=process_name: self.block_app(p)
                        )
                        block_btn.pack(side="right", padx=5)

        except Exception as e:
            print(f"Error processing window queue: {e}")

        # Schedule next check
        self.root.after(100, self.process_window_queue)

    def block_app(self, process_name):
        """Block the selected app."""
        try:
            self.app_controller.block_app(process_name, 30)  # Block for 30 minutes
        except Exception as e:
            print(f"Error blocking app: {e}")

    def update_stats(self):
        """Update statistics display."""
        try:
            # Update points
            self.points_label.config(
                text=f"{self.point_system.current_points}"
            )

            # Update streak
            self.streak_label.config(
                text=f"{self.point_system.current_streak} minutes"
            )
            self.streak_progress["value"] = min(self.point_system.current_streak, 100)

            # Update time bank
            # TODO: Implement time bank progress
            self.time_bank_progress["value"] = 50  # Placeholder

        except Exception as e:
            print(f"Error updating stats: {e}")

        # Schedule next update
        self.root.after(1000, self.update_stats)

    def on_window_change(self, window_title: str, process_name: str, executable_path: str):
        """Handle window change events."""
        try:
            category = self.app_categorizer.categorize_app(window_title, process_name)
            
            if category == "productive":
                self.point_system.add_points(1, "productivity")
                self.current_activity["points_earned"] += 1
            elif category == "entertainment":
                if not self.app_controller.check_app_permission(process_name, 1):
                    self.app_controller.block_app(process_name, int(self.block_duration.get()))
        except Exception as e:
            print(f"Error handling window change: {e}")

    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = GetBack2Work()
    app.run() 