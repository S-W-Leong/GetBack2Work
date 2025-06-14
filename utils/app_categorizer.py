import os
import json
from typing import Dict, List, Set, Tuple

class AppCategorizer:
    def __init__(self):
        self.data_dir = "data"
        self.categories_file = os.path.join(self.data_dir, "app_categories.json")
        self.productive_apps = set()
        self.entertainment_apps = set()
        self.load_categories()

    def load_categories(self):
        """Load app categories from file."""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r') as f:
                    data = json.load(f)
                    self.productive_apps = set(data.get('productive', []))
                    self.entertainment_apps = set(data.get('entertainment', []))
            else:
                # Default categories
                self.productive_apps = {
                    "code.exe", "vscode.exe", "notepad++.exe", "sublime_text.exe",
                    "chrome.exe", "firefox.exe", "msedge.exe",  # Browsers for work
                    "word.exe", "excel.exe", "powerpnt.exe", "outlook.exe",
                    "teams.exe", "slack.exe", "discord.exe",  # Communication for work
                    "git.exe", "github.exe", "gitkraken.exe",
                    "cmd.exe", "powershell.exe", "terminal.exe",
                    "python.exe", "java.exe", "node.exe"
                }
                self.entertainment_apps = {
                    "steam.exe", "epicgameslauncher.exe", "battle.net.exe",
                    "discord.exe", "teamspeak.exe", "skype.exe",  # Communication for fun
                    "spotify.exe", "vlc.exe", "itunes.exe",
                    "chrome.exe", "firefox.exe", "msedge.exe"  # Browsers for entertainment
                }
                self.save_categories()
        except Exception as e:
            print(f"Error loading categories: {e}")

    def save_categories(self):
        """Save app categories to file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.categories_file, 'w') as f:
                json.dump({
                    'productive': list(self.productive_apps),
                    'entertainment': list(self.entertainment_apps)
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving categories: {e}")

    def categorize_app(self, window_title: str, process_name: str) -> str:
        """Categorize an app as productive or entertainment."""
        process_name = process_name.lower()
        
        # Check if the process is in our known categories
        if process_name in self.productive_apps:
            return "productive"
        if process_name in self.entertainment_apps:
            return "entertainment"
        
        # Default categorization based on window title
        entertainment_keywords = {
            "game", "youtube", "netflix", "spotify", "music", "movie",
            "facebook", "instagram", "twitter", "tiktok", "reddit"
        }
        
        window_title = window_title.lower()
        if any(keyword in window_title for keyword in entertainment_keywords):
            return "entertainment"
        
        return "productive"

    def get_productive_apps(self) -> List[str]:
        """Get list of productive apps."""
        return sorted(list(self.productive_apps))

    def get_entertainment_apps(self) -> List[str]:
        """Get list of entertainment apps."""
        return sorted(list(self.entertainment_apps))

    def update_categories(self, productive_apps: List[str], entertainment_apps: List[str]):
        """Update the app categories."""
        # Convert to lowercase and remove duplicates
        productive_set = {app.lower() for app in productive_apps}
        entertainment_set = {app.lower() for app in entertainment_apps}
        
        # Remove any apps that exist in both categories
        common_apps = productive_set.intersection(entertainment_set)
        productive_set -= common_apps
        entertainment_set -= common_apps
        
        # Update the categories
        self.productive_apps = productive_set
        self.entertainment_apps = entertainment_set
        self.save_categories()

    def add_productive_app(self, app_name: str):
        """Add an app to the productive category."""
        self.productive_apps.add(app_name.lower())

    def remove_productive_app(self, app_name: str):
        """Remove an app from the productive category."""
        self.productive_apps.discard(app_name.lower())

    def add_entertainment_app(self, app_name: str):
        """Add an app to the entertainment category."""
        self.entertainment_apps.add(app_name.lower())

    def remove_entertainment_app(self, app_name: str):
        """Remove an app from the entertainment category."""
        self.entertainment_apps.discard(app_name.lower())

    def add_app(self, app_name: str, category: str, is_process: bool = True):
        """Add an app to a category."""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")

        key = "processes" if is_process else "keywords"
        if app_name not in self.categories[category][key]:
            self.categories[category][key].append(app_name)
            self.save_config()

    def remove_app(self, app_name: str, category: str, is_process: bool = True):
        """Remove an app from a category."""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")

        key = "processes" if is_process else "keywords"
        if app_name in self.categories[category][key]:
            self.categories[category][key].remove(app_name)
            self.save_config()

    def get_all_apps(self) -> Dict[str, Dict[str, List[str]]]:
        """Get all categorized apps."""
        return self.categories 