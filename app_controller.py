import psutil
import subprocess
import time
import threading
from typing import Dict, Optional
from gui.overlay import ShameOverlay

class AppController:
    def __init__(self, point_system, root_window):
        self.point_system = point_system
        self.root_window = root_window
        self.blocked_apps: Dict[str, float] = {}  # app_name -> block_until_timestamp
        self.shame_overlay: Optional[ShameOverlay] = None
        self.monitoring_thread = None
        self.running = False

    def start_monitoring(self):
        """Start monitoring for blocked apps."""
        if self.running:
            return

        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_blocked_apps)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring for blocked apps."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def _monitor_blocked_apps(self):
        """Monitor and block unauthorized apps."""
        while self.running:
            try:
                current_time = time.time()
                
                # Check all running processes
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        process_name = proc.info['name'].lower()
                        
                        # Check if this is a blocked app
                        if process_name in self.blocked_apps:
                            block_until = self.blocked_apps[process_name]
                            
                            if current_time < block_until:
                                # App is still blocked, terminate it
                                self._terminate_process(proc)
                            else:
                                # Block period is over
                                del self.blocked_apps[process_name]
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Error in app monitoring: {e}")
                time.sleep(1)

    def _terminate_process(self, process):
        """Terminate a process and show shame overlay."""
        try:
            process.terminate()
            if not self.shame_overlay or not self.shame_overlay.is_visible():
                self.show_shame_overlay(process.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def block_app(self, app_name: str, duration_minutes: int = 5):
        """Block an app for a specified duration."""
        self.blocked_apps[app_name.lower()] = time.time() + (duration_minutes * 60)

    def show_shame_overlay(self, app_name: str):
        """Show the shame overlay for a blocked app."""
        if not self.shame_overlay:
            self.shame_overlay = ShameOverlay(self.root_window)
        self.shame_overlay.show_haiku_challenge(app_name)

    def check_app_permission(self, app_name: str, duration_minutes: int = 1) -> bool:
        """Check if an app can be run based on point balance."""
        cost = duration_minutes * self.point_system.config["entertainment_cost_per_minute"]
        if self.point_system.can_afford(app_name, duration_minutes):
            self.point_system.spend_points(cost, app_name)
            return True
        return False

    def get_blocked_apps(self) -> Dict[str, float]:
        """Get currently blocked apps and their block end times."""
        current_time = time.time()
        return {
            app: end_time - current_time
            for app, end_time in self.blocked_apps.items()
            if end_time > current_time
        } 