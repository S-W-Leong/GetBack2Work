import json
import time
from datetime import datetime
from typing import Dict, Any

class PointSystem:
    def __init__(self, config_path: str = "data/config.json"):
        self.current_points = 0
        self.daily_stats = {}
        self.config_path = config_path
        self.load_config()
        self.load_data()
        self.current_streak = 0
        self.last_productive_time = time.time()

    def load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                "point_interval_seconds": 60,
                "entertainment_cost_per_minute": 2,
                "productivity_points_per_interval": 1,
                "streak_bonus_multiplier": 1.5,
                "max_streak_bonus": 3.0
            }
            self.save_config()

    def save_config(self):
        """Save configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def load_data(self):
        """Load user data from JSON file."""
        try:
            with open("data/user_data.json", 'r') as f:
                data = json.load(f)
                self.current_points = data.get("current_points", 0)
                self.daily_stats = data.get("daily_stats", {})
        except FileNotFoundError:
            self.save_data()

    def save_data(self):
        """Save user data to JSON file."""
        data = {
            "current_points": self.current_points,
            "daily_stats": self.daily_stats
        }
        with open("data/user_data.json", 'w') as f:
            json.dump(data, f, indent=2)

    def add_points(self, amount: int, reason: str = "productivity") -> None:
        """Add points and update statistics."""
        current_time = time.time()
        today = datetime.now().strftime("%Y-%m-%d")

        # Update streak if productive
        if reason == "productivity":
            time_diff = current_time - self.last_productive_time
            if time_diff <= self.config["point_interval_seconds"] * 2:
                self.current_streak += 1
            else:
                self.current_streak = 1
            self.last_productive_time = current_time

            # Apply streak bonus
            streak_multiplier = min(
                1 + (self.current_streak * self.config["streak_bonus_multiplier"]),
                self.config["max_streak_bonus"]
            )
            amount = int(amount * streak_multiplier)

        # Update points and stats
        self.current_points += amount
        
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                "productive_minutes": 0,
                "entertainment_minutes": 0,
                "points_earned": 0,
                "points_spent": 0
            }

        if reason == "productivity":
            self.daily_stats[today]["points_earned"] += amount
            self.daily_stats[today]["productive_minutes"] += amount
        else:
            self.daily_stats[today]["points_spent"] += amount
            self.daily_stats[today]["entertainment_minutes"] += amount

        self.save_data()

    def spend_points(self, amount: int, app_name: str) -> bool:
        """Deduct points for entertainment usage."""
        if self.current_points >= amount:
            self.current_points -= amount
            self.add_points(-amount, reason="entertainment")
            return True
        return False

    def can_afford(self, app_name: str, duration_minutes: int) -> bool:
        """Check if user has enough points for entertainment time."""
        cost = duration_minutes * self.config["entertainment_cost_per_minute"]
        return self.current_points >= cost

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return {
            "current_points": self.current_points,
            "current_streak": self.current_streak,
            "streak_multiplier": min(
                1 + (self.current_streak * self.config["streak_bonus_multiplier"]),
                self.config["max_streak_bonus"]
            )
        } 