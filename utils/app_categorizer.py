import os
import json
from typing import Dict, List, Set, Tuple, Optional

class AppCategorizer:
    def __init__(self):
        self.data_dir = "data"
        self.categories_file = os.path.join(self.data_dir, "app_categories.json")
        
        # Initialize categories
        self.productive_apps = set()
        self.entertainment_apps = set()
        
        # Load existing categories
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
                # Create default categories if file doesn't exist
                self.productive_apps = {
                    'code', 'word', 'excel', 'powerpoint', 'outlook',
                    'notepad', 'visual studio', 'pycharm', 'vscode'
                }
                self.entertainment_apps = {
                    'chrome', 'firefox', 'edge', 'spotify', 'discord',
                    'steam', 'epic games', 'minecraft'
                }
                self.save_categories()
        except Exception as e:
            print(f"Error loading categories: {e}")
            # Initialize with empty sets if loading fails
            self.productive_apps = set()
            self.entertainment_apps = set()

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

    def update_categories(self, productive_apps: List[str], entertainment_apps: List[str]):
        """Update the category lists and save to file."""
        # Convert to lowercase for case-insensitive comparison
        self.productive_apps = {app.lower() for app in productive_apps}
        self.entertainment_apps = {app.lower() for app in entertainment_apps}
        
        # Save the updated categories
        self.save_categories()

    def get_category(self, app_name: str) -> Optional[str]:
        """Get the category of an app."""
        app_name = app_name.lower()
        if app_name in self.productive_apps:
            return "productive"
        elif app_name in self.entertainment_apps:
            return "entertainment"
        return None

    def get_productive_apps(self) -> List[str]:
        """Get list of productive apps."""
        return sorted(list(self.productive_apps))

    def get_entertainment_apps(self) -> List[str]:
        """Get list of entertainment apps."""
        return sorted(list(self.entertainment_apps))

    def is_productive(self, app_name: str) -> bool:
        """Check if an app is productive."""
        return app_name.lower() in self.productive_apps

    def is_entertainment(self, app_name: str) -> bool:
        """Check if an app is entertainment."""
        return app_name.lower() in self.entertainment_apps

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