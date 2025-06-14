import os
import json
from datetime import datetime, timedelta

class PointSystem:
    def __init__(self):
        self.data_dir = "data"
        self.user_data_file = os.path.join(self.data_dir, "user_data.json")
        self.config_file = os.path.join(self.data_dir, "config.json")
        
        # Initialize point values
        self.points_config = {
            "productive_points_per_minute": 1,
            "entertainment_points_per_minute": 1
        }
        
        # Load user data and config
        self.load_data()
        self.load_config()
        
        # Initialize tracking
        self.current_points = 0
        self.current_streak = 0
        self.last_activity_time = None
        self.last_category = None

    def load_data(self):
        """Load user data from file."""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r') as f:
                    data = json.load(f)
                    self.current_points = data.get('points', 0)
                    self.current_streak = data.get('streak', 0)
            else:
                self.current_points = 0
                self.current_streak = 0
                self.save_data()
        except Exception as e:
            print(f"Error loading user data: {e}")
            self.current_points = 0
            self.current_streak = 0

    def load_config(self):
        """Load points configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.points_config.update(config.get('points', {}))
            else:
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_data(self):
        """Save user data to file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.user_data_file, 'w') as f:
                json.dump({
                    'points': self.current_points,
                    'streak': self.current_streak,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving user data: {e}")

    def save_config(self):
        """Save points configuration to file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({
                    'points': self.points_config
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_points(self, category: str, minutes: int):
        """Update points based on time spent in a category."""
        if category == "productive":
            points = minutes * self.points_config["productive_points_per_minute"]
            self.current_points += points
        elif category == "entertainment":
            points = minutes * self.points_config["entertainment_points_per_minute"]
            self.current_points -= points
        
        # Ensure points don't go below 0
        self.current_points = max(0, self.current_points)
        
        # Update streak
        if category == "productive":
            self.current_streak += minutes
        else:
            self.current_streak = 0
        
        self.save_data()

    def get_points(self) -> int:
        """Get current points."""
        return self.current_points

    def get_streak(self) -> int:
        """Get current streak in minutes."""
        return self.current_streak

    def update_config(self, productive_points: int, entertainment_points: int):
        """Update points configuration."""
        self.points_config["productive_points_per_minute"] = productive_points
        self.points_config["entertainment_points_per_minute"] = entertainment_points
        self.save_config()

    def get_config(self) -> dict:
        """Get current points configuration."""
        return self.points_config.copy() 