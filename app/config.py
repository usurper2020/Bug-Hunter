import json
import os

class ConfigManager:
    """Manages the configuration for the BugHunter application."""
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Loads the configuration from the specified JSON file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def get(self, key, default=None):
        """Gets a configuration value by key."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a configuration value by key."""
        self.config[key] = value
        self.save_config()

    def save_config(self):
        """Saves the current configuration to the JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
