import time
import threading
import psutil
import pygetwindow as gw
from typing import Tuple, Callable, List, Dict, Optional
import os
from queue import Queue
import win32gui
import win32process
import win32api
import win32con
import sys
from datetime import datetime, timedelta

class WindowMonitor:
    def __init__(self, callback: Callable[[str, str, str], None]):
        self.callback = callback
        self.running = False
        self.monitor_thread = None
        self.check_interval = 2  # seconds
        self.window_queue = Queue()
        self.process_cache = {}
        self.cache_timeout = timedelta(seconds=30)
        self.our_process_name = os.path.basename(sys.executable)
        self.last_windows = {}
        self._lock = threading.Lock()

    def start_monitoring(self):
        """Start the window monitoring thread."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("Window monitoring started")

    def stop_monitoring(self):
        """Stop the window monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            print("Window monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Get current windows
                current_windows = self.get_all_windows_info()
                
                # Check for changes
                for process_name, (window_title, hwnd, process_id) in current_windows.items():
                    if process_name not in self.last_windows or self.last_windows[process_name][0] != window_title:
                        # Window changed or new window
                        self.window_queue.put((window_title, process_name, hwnd))
                        if self.callback:
                            self.callback(window_title, process_name, hwnd)
                
                # Update last known windows
                self.last_windows = current_windows
                
                # Sleep for the check interval
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(self.check_interval)

    def get_all_windows_info(self):
        """Get information about all visible windows that appear in the taskbar."""
        windows_info = {}
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                # Check if window has a taskbar button
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if not (style & win32con.WS_EX_TOOLWINDOW):  # Exclude tool windows
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:  # Only include windows with titles
                        try:
                            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                            process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process_id)
                            process_name = win32process.GetModuleFileNameEx(process_handle, 0)
                            
                            # Skip our own process
                            if os.path.basename(process_name).lower() != self.our_process_name.lower():
                                windows_info[process_name] = (window_title, hwnd, process_id)
                        except Exception as e:
                            print(f"Error getting process info: {e}")
        win32gui.EnumWindows(callback, None)
        return windows_info

    def get_active_window_info(self) -> Tuple[str, str, str]:
        """Get information about the currently active window."""
        try:
            active_window = gw.getActiveWindow()
            if not active_window or not active_window.title:
                return ("", "", "")

            window_title = active_window.title
            process_name = ""
            executable_path = ""

            # Try to get process info from cache
            try:
                if active_window._hWnd in self.process_cache:
                    proc_info = self.process_cache[active_window._hWnd]
                    process_name = proc_info['name'].lower()
                    executable_path = proc_info['exe']
            except Exception:
                pass

            # Skip our own process
            if process_name == self.our_process_name:
                return ("", "", "")

            return (window_title, process_name, executable_path)

        except Exception as e:
            print(f"Error getting window info: {e}")
            return ("", "", "") 