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

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, app_categorizer, point_system, app_controller):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Store references
        self.app_categorizer = app_categorizer
        self.point_system = point_system
        self.app_controller = app_controller
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_app_categories_tab()
        self.create_points_tab()
        
        # Add save button at bottom
        self.save_button = ttk.Button(self, text="Save", command=self.save_settings)
        self.save_button.pack(pady=10)

    def create_app_categories_tab(self):
        """Create the app categories tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="App Categories")
        
        # Create frames for productive and entertainment apps
        lists_frame = ttk.Frame(tab)
        lists_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        productive_frame = ttk.LabelFrame(lists_frame, text="Productive Apps", padding="5")
        productive_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        entertainment_frame = ttk.LabelFrame(lists_frame, text="Entertainment Apps", padding="5")
        entertainment_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # Create listboxes with scrollbars
        # Productive apps
        productive_scroll = ttk.Scrollbar(productive_frame)
        productive_scroll.pack(side="right", fill="y")
        
        self.productive_list = tk.Listbox(productive_frame, yscrollcommand=productive_scroll.set)
        self.productive_list.pack(side="left", fill="both", expand=True)
        productive_scroll.config(command=self.productive_list.yview)
        
        # Add remove button for productive apps
        ttk.Button(
            productive_frame,
            text="Remove Selected",
            command=lambda: self.remove_app(self.productive_list, self.productive_list.curselection()[0] if self.productive_list.curselection() else -1)
        ).pack(side="bottom", fill="x", pady=5)
        
        # Entertainment apps
        entertainment_scroll = ttk.Scrollbar(entertainment_frame)
        entertainment_scroll.pack(side="right", fill="y")
        
        self.entertainment_list = tk.Listbox(entertainment_frame, yscrollcommand=entertainment_scroll.set)
        self.entertainment_list.pack(side="left", fill="both", expand=True)
        entertainment_scroll.config(command=self.entertainment_list.yview)
        
        # Add remove button for entertainment apps
        ttk.Button(
            entertainment_frame,
            text="Remove Selected",
            command=lambda: self.remove_app(self.entertainment_list, self.entertainment_list.curselection()[0] if self.entertainment_list.curselection() else -1)
        ).pack(side="bottom", fill="x", pady=5)
        
        # Add input frame at the bottom
        input_frame = ttk.LabelFrame(tab, text="Add New App", padding="5")
        input_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # App selection dropdown
        ttk.Label(input_frame, text="Select App:").pack(side="left", padx=(0, 5))
        self.app_var = tk.StringVar()
        self.app_dropdown = ttk.Combobox(
            input_frame,
            textvariable=self.app_var,
            state="readonly",
            width=30
        )
        self.app_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Category dropdown
        ttk.Label(input_frame, text="Category:").pack(side="left", padx=(0, 5))
        self.category_var = tk.StringVar(value="productive")
        category_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.category_var,
            values=["productive", "entertainment"],
            state="readonly",
            width=15
        )
        category_dropdown.pack(side="left", padx=(0, 5))
        
        # Add button
        ttk.Button(
            input_frame,
            text="Add",
            command=self.add_new_app
        ).pack(side="left")
        
        # Load current categories and installed apps
        self.load_categories()
        self.load_installed_apps()

    def load_installed_apps(self):
        """Load installed apps into the dropdown."""
        installed_apps = self.app_controller.get_installed_apps()
        self.app_dropdown['values'] = installed_apps
        if installed_apps:
            self.app_dropdown.set(installed_apps[0])

    def load_categories(self):
        """Load current app categories into the listboxes."""
        # Clear existing items
        self.productive_list.delete(0, tk.END)
        self.entertainment_list.delete(0, tk.END)
        
        # Load productive apps
        for app in self.app_categorizer.get_productive_apps():
            self.productive_list.insert(tk.END, app)
        
        # Load entertainment apps
        for app in self.app_categorizer.get_entertainment_apps():
            self.entertainment_list.insert(tk.END, app)

    def add_new_app(self):
        """Add a new app to the selected category."""
        app = self.app_var.get().strip()
        if app:
            category = self.category_var.get()
            if category == "productive":
                # Check if app is already in entertainment list
                if app in self.entertainment_list.get(0, tk.END):
                    messagebox.showwarning(
                        "Warning",
                        f"{app} is already in the Entertainment list. Please remove it first."
                    )
                    return
                self.productive_list.insert(tk.END, app)
            else:
                # Check if app is already in productive list
                if app in self.productive_list.get(0, tk.END):
                    messagebox.showwarning(
                        "Warning",
                        f"{app} is already in the Productive list. Please remove it first."
                    )
                    return
                self.entertainment_list.insert(tk.END, app)
            
            # Remove the app from the dropdown to prevent duplicates
            current_values = list(self.app_dropdown['values'])
            if app in current_values:
                current_values.remove(app)
                self.app_dropdown['values'] = current_values
                if current_values:
                    self.app_dropdown.set(current_values[0])

    def remove_app(self, listbox, index):
        """Remove an app from the specified listbox."""
        if index >= 0:
            listbox.delete(index)

    def create_points_tab(self):
        """Create tab for configuring point values."""
        points_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(points_frame, text="Points")
        
        # Create main content frame
        content_frame = ttk.Frame(points_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Get current config
        config = self.point_system.get_config()
        
        # Productive points
        ttk.Label(content_frame, text="Points per minute for productive apps:").pack(anchor='w', pady=(0, 5))
        self.productive_points = ttk.Spinbox(
            content_frame,
            from_=1,
            to=100,
            width=10,
            validate='key',
            validatecommand=(self.register(self.validate_number), '%P')
        )
        self.productive_points.set(config["productive_points_per_minute"])
        self.productive_points.pack(anchor='w', pady=(0, 20))
        
        # Entertainment points
        ttk.Label(content_frame, text="Points deducted per minute for entertainment apps:").pack(anchor='w', pady=(0, 5))
        self.entertainment_points = ttk.Spinbox(
            content_frame,
            from_=1,
            to=100,
            width=10,
            validate='key',
            validatecommand=(self.register(self.validate_number), '%P')
        )
        self.entertainment_points.set(config["entertainment_points_per_minute"])
        self.entertainment_points.pack(anchor='w')
        
        # Add explanation text
        explanation = (
            "Points are awarded or deducted based on time spent in each category.\n"
            "For example, if you set 2 points per minute for productive apps,\n"
            "you'll earn 2 points for each minute spent on productive apps.\n"
            "Similarly, if you set 1 point per minute for entertainment apps,\n"
            "you'll lose 1 point for each minute spent on entertainment apps."
        )
        ttk.Label(
            content_frame,
            text=explanation,
            wraplength=500,
            justify='left'
        ).pack(anchor='w', pady=(20, 0))

    def validate_number(self, value):
        """Validate that input is a positive number."""
        if value == "":
            return True
        try:
            num = int(value)
            return num > 0
        except ValueError:
            return False

    def save_settings(self):
        """Save all settings."""
        # Get all apps from both lists
        productive_apps = list(self.productive_list.get(0, tk.END))
        entertainment_apps = list(self.entertainment_list.get(0, tk.END))
        
        # Update the categorizer with new lists
        self.app_categorizer.update_categories(productive_apps, entertainment_apps)
        
        # Save point values
        try:
            productive_points = int(self.productive_points.get())
            entertainment_points = int(self.entertainment_points.get())
            self.point_system.update_config(productive_points, entertainment_points)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for point values")
            return
        
        self.destroy()

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
        
        # Add protocol handler for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize app controller after GUI
        self.app_controller = AppController(self.point_system, self.root)
        
        # Initialize window monitor
        self.window_monitor = WindowMonitor(self.on_window_change)
        
        # Initialize activity tracking
        self.current_activity = {
            'name': None,
            'category': None,
            'start_time': None,
            'points_earned': 0
        }
        
        # Initialize window tracking
        self.last_window = None
        self.last_window_time = None
        
        # List of protected system apps that should never be blocked
        self.protected_apps = {
            'taskmgr.exe',  # Task Manager
            'explorer.exe',  # Windows Explorer
            'python.exe',    # Python interpreter
            'pythonw.exe',   # Python windowless
            'cmd.exe',       # Command Prompt
            'powershell.exe', # PowerShell
            'systemsettings.exe', # Windows Settings
            'ms-settings:',  # Windows Settings
            'control.exe',   # Control Panel
        }
        
        # Setup GUI
        self.setup_gui()
        
        # Start processing window changes
        self.process_window_queue()

    def on_closing(self):
        """Handle window closing."""
        try:
            # Stop all monitoring
            self.window_monitor.stop_monitoring()
            self.app_controller.stop_monitoring()
            
            # Unblock all apps
            self.app_controller.unblock_all_apps()
            
            # Destroy the window
            self.root.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            # Force quit if normal shutdown fails
            self.root.quit()

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
        activity_frame.grid_rowconfigure(0, weight=1)
        activity_frame.grid_columnconfigure(0, weight=1)

        # Create a canvas with scrollbar for the apps list
        self.canvas = tk.Canvas(activity_frame)
        self.scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.canvas.yview)
        self.apps_frame = ttk.Frame(self.canvas)

        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Create window in canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.apps_frame, anchor="nw")

        # Bind events for scrolling
        self.apps_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

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

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Reset the width of the inner frame to match the canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def show_buy_time(self):
        """Show the buy time dialog."""
        # TODO: Implement buy time dialog
        pass

    def show_settings(self):
        """Show the settings dialog."""
        SettingsDialog(self.root, self.app_categorizer, self.point_system, self.app_controller)

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
                for widget in self.apps_frame.winfo_children():
                    widget.destroy()
                self.app_labels.clear()

                # Create new labels for each window
                for process_name, (window_title, hwnd, process_id) in windows_info.items():
                    # Create a frame for each app
                    app_frame = ttk.Frame(self.apps_frame)
                    app_frame.pack(fill="x", padx=5, pady=2)

                    # App name and title
                    app_label = ttk.Label(
                        app_frame,
                        text=f"{os.path.basename(process_name)} - {window_title}",
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

                # Update scroll region
                self._on_frame_configure()

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
            points = self.point_system.get_points()
            self.points_label.config(text=f"{points:,}")

            # Update streak
            streak = self.point_system.get_streak()
            hours = streak // 60
            minutes = streak % 60
            self.streak_label.config(text=f"{hours:02d}:{minutes:02d}")
            self.streak_progress["value"] = minutes

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
            # Create window info dictionary
            window_info = {
                'process_name': process_name,
                'window_title': window_title,
                'executable_path': executable_path
            }
            
            # Process the window change
            self.process_window_change(window_info)
            
        except Exception as e:
            print(f"Error handling window change: {e}")

    def process_window_change(self, window_info):
        """Process window change and update points."""
        if not window_info:
            return
            
        process_name = window_info.get('process_name', '').lower()
        window_title = window_info.get('window_title', '')
        
        # Skip if it's our own window
        if process_name == "python" and "GetB@ck2Work" in window_title:
            return
            
        # Skip if it's a protected system app
        if process_name in self.protected_apps:
            return
            
        # Get current time
        current_time = datetime.now()
        
        # If we have a previous window, calculate time spent
        if self.last_window and self.last_window_time:
            time_spent = (current_time - self.last_window_time).total_seconds() / 60  # Convert to minutes
            if time_spent >= 1:  # Only update if at least 1 minute has passed
                # Get category of the last window
                category = self.app_categorizer.get_category(self.last_window['process_name'])
                if category:
                    # Update points based on time spent
                    self.point_system.update_points(category, int(time_spent))
                    # Update display
                    self.update_display()
        
        # Check if the new window is an entertainment app
        category = self.app_categorizer.get_category(process_name)
        if category == "entertainment":
            # Calculate cost for 1 minute of entertainment
            cost = self.point_system.points_config["entertainment_points_per_minute"]
            current_points = self.point_system.get_points()
            
            if current_points < cost:
                # Not enough points, block the app
                self.app_controller.block_app(process_name)
                messagebox.showwarning(
                    "Insufficient Points",
                    f"You need {cost} points to use {process_name}.\n"
                    f"Current points: {current_points}\n"
                    "Earn more points by using productive apps!"
                )
                return
        
        # Update last window info
        self.last_window = window_info
        self.last_window_time = current_time
        
        # Update current activity display
        if process_name:
            if category:
                self.current_activity_label.config(
                    text=f"Current Activity: {process_name} ({category})"
                )
            else:
                self.current_activity_label.config(
                    text=f"Current Activity: {process_name} (uncategorized)"
                )
        else:
            self.current_activity_label.config(text="Current Activity: None")

    def check_points_for_entertainment(self):
        """Check if user has enough points for entertainment apps."""
        current_points = self.point_system.get_points()
        cost_per_minute = self.point_system.points_config["entertainment_points_per_minute"]
        
        # Get all running entertainment apps
        running_apps = self.app_controller.get_running_apps()
        for app_name, app_info in running_apps.items():
            category = self.app_categorizer.get_category(app_name)
            if category == "entertainment" and app_info['is_blocked'] == False:
                if current_points < cost_per_minute:
                    # Not enough points, block the app
                    self.app_controller.block_app(app_name)
                    messagebox.showwarning(
                        "Insufficient Points",
                        f"You need {cost_per_minute} points to use {app_name}.\n"
                        f"Current points: {current_points}\n"
                        "Earn more points by using productive apps!"
                    )

    def update_display(self):
        """Update the display with current points and streak."""
        # Update points display
        points = self.point_system.get_points()
        self.points_label.config(text=f"{points:,}")
        
        # Update streak display
        streak = self.point_system.get_streak()
        hours = streak // 60
        minutes = streak % 60
        self.streak_label.config(text=f"{hours:02d}:{minutes:02d}")
        
        # Update streak progress bar
        self.streak_progress['value'] = minutes

    def run(self):
        """Start the application."""
        # Start window monitoring
        self.window_monitor.start_monitoring()
        
        # Start app controller
        self.app_controller.start_monitoring()
        
        # Start points checking
        def check_points():
            self.check_points_for_entertainment()
            self.root.after(1000, check_points)  # Check every second
        
        self.root.after(1000, check_points)
        
        # Start stats updates
        self.root.after(1000, self.update_stats)
        
        # Start the main loop
        self.root.mainloop()

if __name__ == "__main__":
    app = GetBack2Work()
    app.run() 