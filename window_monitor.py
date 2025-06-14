import time
import threading
import psutil
import pygetwindow as gw
from typing import Tuple, Callable, List, Dict, Optional
import os
from queue import Queue
import win32gui
import win32process
import sys

class WindowMonitor:
    def __init__(self, callback: Callable[[str, str, str], None]):
        self.callback = callback
        self.running = False
        self.monitor_thread = None
        self.check_interval = 2  # seconds
        self.window_queue = Queue()
        self.process_cache = {}
        self.cache_timeout = 5  # seconds
        self.our_process_name = None
        self.last_windows = set()
        self._lock = threading.Lock()

    def start_monitoring(self):
        """Start the window monitoring thread."""
        if not self.running:
            self.running = True
            # Get our process name
            try:
                self.our_process_name = os.path.basename(sys.executable).lower()
                print(f"Starting window monitor. Our process: {self.our_process_name}")
            except Exception as e:
                print(f"Error getting our process name: {e}")
                self.our_process_name = "python.exe"
            
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
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
                # Update process cache periodically
                current_time = time.time()
                self.process_cache = {
                    pid: (info, timestamp)
                    for pid, (info, timestamp) in self.process_cache.items()
                    if current_time - timestamp < self.cache_timeout
                }

                # Get all visible windows
                current_windows = set()
                def enum_windows_callback(hwnd, _):
                    if win32gui.IsWindowVisible(hwnd):
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            if pid:
                                current_windows.add((hwnd, pid))
                        except Exception as e:
                            print(f"Error getting window info: {e}")
                    return True

                win32gui.EnumWindows(enum_windows_callback, None)

                # Check for new or changed windows
                for hwnd, pid in current_windows:
                    try:
                        window_title = win32gui.GetWindowText(hwnd)
                        if not window_title:  # Skip windows with no title
                            continue

                        # Get process info
                        process_info = self._get_process_info(pid)
                        if not process_info:
                            continue

                        process_name, executable_path = process_info
                        
                        # Skip our own process
                        if process_name.lower() == self.our_process_name:
                            continue

                        # Add to queue for processing
                        self.window_queue.put((window_title, process_name, executable_path))
                        
                        # Call callback for new windows
                        if (hwnd, pid) not in self.last_windows:
                            self.callback(window_title, process_name, executable_path)
                            
                    except Exception as e:
                        print(f"Error processing window {hwnd}: {e}")

                # Update last known windows
                self.last_windows = current_windows

            except Exception as e:
                print(f"Error in monitor loop: {e}")

            time.sleep(self.check_interval)

    def _get_process_info(self, pid: int) -> Optional[Tuple[str, str]]:
        """Get process information with caching."""
        try:
            # Check cache first
            if pid in self.process_cache:
                info, _ = self.process_cache[pid]
                return info

            # Get process info
            process = psutil.Process(pid)
            process_name = process.name()
            try:
                executable_path = process.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                executable_path = ""

            # Cache the result
            self.process_cache[pid] = ((process_name, executable_path), time.time())
            return process_name, executable_path

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
        except Exception as e:
            print(f"Error getting process info for PID {pid}: {e}")
            return None

    def get_all_windows_info(self) -> Dict[str, Tuple[str, str, str]]:
        """Get information about all visible windows."""
        windows_info = {}
        try:
            def enum_windows_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    try:
                        window_title = win32gui.GetWindowText(hwnd)
                        if not window_title:  # Skip windows with no title
                            return True

                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        if not pid:
                            return True

                        process_info = self._get_process_info(pid)
                        if not process_info:
                            return True

                        process_name, executable_path = process_info
                        
                        # Skip our own process
                        if process_name.lower() == self.our_process_name:
                            return True

                        windows_info[process_name] = (window_title, process_name, executable_path)
                    except Exception as e:
                        print(f"Error processing window {hwnd}: {e}")
                return True

            win32gui.EnumWindows(enum_windows_callback, None)
        except Exception as e:
            print(f"Error getting all windows info: {e}")
        
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