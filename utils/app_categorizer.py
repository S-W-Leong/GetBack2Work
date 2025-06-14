import os
import json
from typing import Dict, List, Set

class AppCategorizer:
    def __init__(self):
        self.productive_apps: Set[str] = set()
        self.entertainment_apps: Set[str] = set()
        self.load_categories()

    def load_categories(self):
        """Load app categories from JSON files."""
        try:
            # Load productive apps
            if os.path.exists("data/productive_apps.json"):
                with open("data/productive_apps.json", 'r') as f:
                    self.productive_apps = set(json.load(f))

            # Load entertainment apps
            if os.path.exists("data/entertainment_apps.json"):
                with open("data/entertainment_apps.json", 'r') as f:
                    self.entertainment_apps = set(json.load(f))
        except Exception as e:
            print(f"Error loading app categories: {e}")

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

    def categorize_app(self, window_title: str, process_name: str) -> str:
        """
        Categorize an application as productive or entertainment.
        Returns 'productive', 'entertainment', or 'neutral'.
        """
        process_name = process_name.lower()
        window_title = window_title.lower()

        # Check custom lists first
        if process_name in self.productive_apps:
            return "productive"
        if process_name in self.entertainment_apps:
            return "entertainment"

        # Default categorization rules
        productive_keywords = {
            "code", "visual studio", "pycharm", "eclipse", "intellij",
            "terminal", "cmd", "powershell", "git", "github", "bitbucket",
            "excel", "word", "powerpoint", "outlook", "onenote",
            "notepad", "notepad++", "sublime", "atom", "vscode",
            "browser", "chrome", "firefox", "edge", "safari",
            "slack", "teams", "zoom", "meet", "webex",
            "jira", "trello", "asana", "confluence",
            "pdf", "adobe reader", "acrobat",
            "calculator", "calendar", "mail", "notes",
            "task", "todo", "project", "planning",
            "document", "spreadsheet", "presentation",
            "research", "study", "learn", "course",
            "work", "job", "career", "professional",
            "development", "programming", "coding",
            "design", "art", "creative", "drawing",
            "writing", "editor", "text", "document",
            "database", "sql", "query", "data",
            "analysis", "analytics", "statistics",
            "meeting", "conference", "call",
            "email", "communication", "chat",
            "file", "folder", "directory",
            "system", "settings", "configuration",
            "backup", "sync", "cloud", "storage",
            "security", "antivirus", "firewall",
            "update", "install", "setup",
            "monitor", "performance", "resource",
            "network", "internet", "web",
            "server", "client", "host",
            "api", "interface", "gui",
            "test", "debug", "error",
            "log", "report", "status",
            "help", "support", "guide",
            "manual", "tutorial", "documentation"
        }

        entertainment_keywords = {
            "game", "steam", "epic", "origin", "battle.net",
            "minecraft", "roblox", "fortnite", "league of legends",
            "youtube", "netflix", "disney+", "hulu", "prime video",
            "spotify", "music", "player", "media",
            "social", "facebook", "twitter", "instagram",
            "tiktok", "snapchat", "reddit", "discord",
            "twitch", "stream", "broadcast",
            "movie", "film", "video", "tv",
            "anime", "manga", "comic",
            "gaming", "play", "fun",
            "entertainment", "leisure",
            "chat", "message", "social",
            "photo", "picture", "image",
            "video", "movie", "film",
            "music", "song", "audio",
            "game", "play", "fun",
            "stream", "watch", "view",
            "social", "friend", "chat",
            "entertainment", "leisure",
            "hobby", "interest", "fun"
        }

        # Check window title and process name against keywords
        for keyword in productive_keywords:
            if keyword in window_title or keyword in process_name:
                return "productive"

        for keyword in entertainment_keywords:
            if keyword in window_title or keyword in process_name:
                return "entertainment"

        return "neutral"

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