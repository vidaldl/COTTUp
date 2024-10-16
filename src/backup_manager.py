import os
import requests
import time
from src.token_manager import TokenManager
from src.file_manager import FileManager
from src.error_handler import ErrorHandler, APIError, FileError
from src.logger import Logger

class BackupManager:
    def __init__(self):
        self.api_base_url = "https://canvas.instructure.com/api/v1"
        self.token_manager = TokenManager()
        self.file_manager = FileManager()
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger()
        self.api_token = self.token_manager.get_token()
        self.courses = []

    def load_courses_from_csv(self, file_path):
        """Load and validate courses from a CSV file."""
        self.logger.info(f"Loading courses from CSV: {file_path}")
        try:
            courses = self.file_manager.validate_and_parse_csv(file_path)
            if not courses:
                raise FileError("No valid courses found in the CSV.")
            self.courses = courses
            self.logger.info(f"Successfully loaded {len(courses)} courses from CSV.")
        except Exception as e:
            self.error_handler.handle_file_error(e, "loading courses from CSV")

    def trigger_backup(self, course_name, course_id):
        """Mock method to simulate triggering a backup for a course."""
        self.logger.info(f"Triggering backup for course: {course_name} (ID: {course_id})")
        try:
            # Simulate an API call here (mocked for now)
            response_success = self.mock_api_call(course_id)
            if not response_success:
                raise APIError(f"Failed to initiate backup for course: {course_name}")
            self.logger.info(f"Backup successfully triggered for {course_name}")
            return True
        except APIError as e:
            self.error_handler.handle_api_error(e, f"triggering backup for {course_name}")
            return False
        
    def mock_api_call(self, course_id):
        """Mock API method for triggering backup, returns False to simulate an error."""
        return False

    def check_backup_status(self, course_id, backup_id):
        """Check the status of the backup for a given course ID."""
        endpoint = f"{self.api_base_url}/courses/{course_id}/backups/{backup_id}"
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            backup_status = response.json().get("status")
            print(f"Backup status for course {course_id}: {backup_status}")
            return backup_status
        except requests.exceptions.RequestException as e:
            self.error_handler.handle_api_error(e, f"checking backup status for course {course_id}")
            return None

    def download_backup(self, course_id, backup_id):
        """Download the completed backup for a given course."""
        endpoint = f"{self.api_base_url}/courses/{course_id}/backups/{backup_id}/download"
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        try:
            response = requests.get(endpoint, headers=headers, stream=True)
            response.raise_for_status()
            file_path = self.file_manager.save_backup(course_id, response)
            print(f"Backup downloaded for course {course_id} at {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading backup for course {course_id}: {e}")
            # Placeholder: Integrate with ErrorHandler to log and manage this error

    def start_backup_process(self, courses):
        """Start the backup process for a list of courses."""
        for course_name, course_id in courses:
            backup_id = self.trigger_backup(course_id)
            if backup_id:
                while True:
                    status = self.check_backup_status(course_id, backup_id)
                    if status == "completed":
                        self.download_backup(course_id, backup_id)
                        break
                    elif status == "failed":
                        print(f"Backup failed for course {course_id}")
                        # Placeholder: Integrate with ErrorHandler to log and manage this error
                        break
                    time.sleep(30)

if __name__ == "__main__":
    backup_manager = BackupManager()
    test_csv_path = os.path.join(os.path.dirname(__file__), "../tests/csv/testcsv.csv")
    backup_manager.load_courses_from_csv(test_csv_path)

    for course_name, course_id in backup_manager.courses:
        success = backup_manager.trigger_backup(course_name, course_id)
        if not success:
            print(f"Error triggering backup for {course_name}.")