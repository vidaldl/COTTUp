#src/persistence_manager.py
import json
from pathlib import Path
from src.logger import Logger
from src.error_handler import ErrorHandler

class PersistenceManager:
    def __init__(self):
        self.status_file_path = Path("data/backup_status.json")
        self.logger = Logger().get_logger()
        self.error_handler = ErrorHandler()
        self.status_data = {}
        self._load_status()

    def _load_status(self):
        """Load backup status data from the JSON file."""
        try:
            if self.status_file_path.exists():
                with open(self.status_file_path, "r") as file:
                    self.status_data = json.load(file)
                    self.logger.info("Backup status loaded successfully.")
            else:
                self.logger.info("No backup status file found; starting fresh.")
                self.status_data = {}
        except Exception as e:
            self.error_handler.handle_generic_error(e, "loading backup status")

    def save_status(self):
        """Save the current backup status to the JSON file."""
        try:
            self.status_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            with open(self.status_file_path, "w") as file:
                json.dump(self.status_data, file, indent=4)
                self.logger.info("Backup status saved successfully.")
        except Exception as e:
            self.error_handler.handle_generic_error(e, "saving backup status")

    def update_course_status(self, course_id, status, progress=0):
        """Update the status and progress of a specific course backup."""
        self.status_data[course_id] = {
            "status": status,
            "progress": progress
        }
        self.save_status()

    def get_course_status(self, course_id):
        """Retrieve the status and progress of a specific course backup."""
        return self.status_data.get(course_id, {"status": "Not Started", "progress": 0})

    def get_all_statuses(self):
        """Retrieve the statuses of all courses."""
        return self.status_data


if __name__ == "__main__":
    persistence_manager = PersistenceManager()
    
    # Simulate updating course status
    persistence_manager.update_course_status("12345", "In Progress", 50)
    persistence_manager.update_course_status("67890", "Completed", 100)

    # Retrieve and print all statuses
    all_statuses = persistence_manager.get_all_statuses()
    print("All Backup Statuses:")
    for course_id, status in all_statuses.items():
        print(f"Course ID: {course_id}, Status: {status['status']}, Progress: {status['progress']}")