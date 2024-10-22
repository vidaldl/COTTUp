#src/config_manager.py
import json
import os
from pathlib import Path
from src.error_handler import ErrorHandler, ConfigError

class ConfigManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.config_file_path = Path("config.json")
        self.default_config = {
            "backup_interval": {"type": "hours", "value": 24},
            "backup_folder": str(Path("data/backups")),
            "api_token": None
        }
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from the JSON file or create default config if not found."""
        try:
            if not self.config_file_path.exists():
                print("Configuration file not found. Creating a default configuration.")
                self.save_config(self.default_config)
                return self.default_config

            with open(self.config_file_path, "r") as file:
                config = json.load(file)
                return {**self.default_config, **config}  # Merge defaults with existing
        except Exception as e:
            self.error_handler.handle_generic_error(e, "loading configuration")
            return self.default_config

    def save_config(self, config):
        """Save the configuration to the JSON file."""
        try:
            with open(self.config_file_path, "w") as file:
                json.dump(config, file, indent=4)
                print("Configuration saved successfully.")
        except Exception as e:
            self.error_handler.handle_generic_error(e, "saving configuration")

    def get_config(self, key):
        """Get a configuration value by key."""
        return self.config.get(key)

    def update_config(self, key, value):
        """Update a configuration value and save it to the file."""
        try:
            self.config[key] = value
            self.save_config(self.config)
        except Exception as e:
            self.error_handler.handle_generic_error(e, f"updating configuration for {key}")


if __name__ == "__main__":
    config_manager = ConfigManager()
    
    # Test loading the config
    print("Loaded configuration:", config_manager.config)

    # Test updating a configuration setting
    config_manager.update_config("backup_interval", {"type": "minutes", "value": 60})
    print("Updated configuration:", config_manager.config)

    # Test retrieving a specific configuration value
    backup_interval = config_manager.get_config("backup_interval")
    print("Backup interval:", backup_interval)
