import psutil
import win32gui
import win32process
import win32con
import time
import threading
import os
from typing import Optional, Dict, Any, List
from gui.overlay import ShameOverlay

class AppController:
    def __init__(self, point_system, root_window):
        self.point_system = point_system
        self.root_window = root_window
        self.blocked_apps = set()
        self.app_processes = {}  # Store process IDs for quick lookup
        self.last_check_time = time.time()
        self.check_interval = 1  # Check every second
        self.shame_overlay = None
        self.running = False
        self.monitoring_thread = None
        self._installed_apps_cache = None
        self._last_cache_update = 0
        self._cache_duration = 300  # Cache for 5 minutes

    def start_monitoring(self):
        """Start monitoring for blocked apps."""
        if self.running:
            return
            
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True  # Thread will exit when main program exits
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring for blocked apps."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)

    def unblock_all_apps(self):
        """Unblock all currently blocked apps."""
        for app_name in list(self.blocked_apps):
            self.unblock_app(app_name)

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self.check_and_terminate_blocked_apps()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)  # Prevent tight loop on error

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
                            self._terminate_process(proc)
                        else:
                            # Check if this is a running app
                            if self.is_app_running(process_name):
                                self.block_app(process_name)

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                time.sleep(self.check_interval)
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

    def is_app_running(self, app_name: str) -> bool:
        """Check if an app is currently running."""
        app_name = app_name.lower()
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == app_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_app_pid(self, app_name: str) -> Optional[int]:
        """Get the process ID of a running app."""
        app_name = app_name.lower()
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == app_name:
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def block_app(self, app_name: str) -> bool:
        """Block an app from running."""
        app_name = app_name.lower()
        if app_name in self.blocked_apps:
            return False

        # Get the process ID if the app is running
        pid = self.get_app_pid(app_name)
        if pid:
            try:
                # Terminate the process
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=3)  # Wait for process to terminate
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass

        self.blocked_apps.add(app_name)
        return True

    def unblock_app(self, app_name: str) -> bool:
        """Unblock an app."""
        app_name = app_name.lower()
        if app_name in self.blocked_apps:
            self.blocked_apps.remove(app_name)
            return True
        return False

    def is_app_blocked(self, app_name: str) -> bool:
        """Check if an app is blocked."""
        return app_name.lower() in self.blocked_apps

    def terminate_app(self, app_name: str) -> bool:
        """Terminate a running app."""
        pid = self.get_app_pid(app_name)
        if pid:
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=3)  # Wait for process to terminate
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                return False
        return False

    def check_and_terminate_blocked_apps(self) -> None:
        """Check for and terminate any blocked apps that are running."""
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return

        self.last_check_time = current_time
        for app_name in self.blocked_apps:
            if self.is_app_running(app_name):
                self.terminate_app(app_name)

    def get_running_apps(self) -> Dict[str, Any]:
        """Get information about currently running apps."""
        running_apps = {}
        for proc in psutil.process_iter(['name', 'pid', 'create_time']):
            try:
                app_name = proc.info['name'].lower()
                if app_name not in running_apps:
                    running_apps[app_name] = {
                        'pid': proc.info['pid'],
                        'create_time': proc.info['create_time'],
                        'is_blocked': app_name in self.blocked_apps
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return running_apps

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

    def get_installed_apps(self) -> List[str]:
        """Get a list of installed applications."""
        current_time = time.time()
        
        # Return cached list if it's still valid
        if (self._installed_apps_cache is not None and 
            current_time - self._last_cache_update < self._cache_duration):
            return self._installed_apps_cache
        
        installed_apps = set()
        
        # Get apps from Program Files
        program_files_paths = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        ]
        
        for program_files in program_files_paths:
            if os.path.exists(program_files):
                for root, dirs, files in os.walk(program_files):
                    for file in files:
                        if file.endswith('.exe'):
                            app_name = os.path.splitext(file)[0].lower()
                            installed_apps.add(app_name)
        
        # Get apps from Windows Start Menu
        start_menu_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ.get('ProgramData', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]
        
        for start_menu in start_menu_paths:
            if os.path.exists(start_menu):
                for root, dirs, files in os.walk(start_menu):
                    for file in files:
                        if file.endswith('.lnk'):
                            app_name = os.path.splitext(file)[0].lower()
                            installed_apps.add(app_name)
        
        # Get currently running apps
        for proc in psutil.process_iter(['name']):
            try:
                app_name = os.path.splitext(proc.info['name'])[0].lower()
                installed_apps.add(app_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Convert to sorted list
        self._installed_apps_cache = sorted(list(installed_apps))
        self._last_cache_update = current_time
        
        return self._installed_apps_cache 