import requests
import time
from src.token_manager import TokenManager
from src.file_manager import FileManager

class BackupManager:
    def __init__(self):
        self.api_base_url = "https://canvas.instructure.com/api/v1"
        self.token_manager = TokenManager()
        self.file_manager = FileManager()
        self.api_token = self.token_manager.get_token()

    def trigger_backup(self, course_id):
        """Trigger a backup for a given course ID."""
        endpoint = f"{self.api_base_url}/courses/{course_id}/backups"
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        try:
            response = requests.post(endpoint, headers=headers)
            response.raise_for_status()
            backup_id = response.json().get("id")
            print(f"Backup triggered for course {course_id}. Backup ID: {backup_id}")
            return backup_id
        except requests.exceptions.RequestException as e:
            print(f"Error triggering backup for course {course_id}: {e}")
            # Placeholder: Integrate with ErrorHandler to log and manage this error
            return None

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
            print(f"Error checking backup status for course {course_id}: {e}")
            # Placeholder: Integrate with ErrorHandler to log and manage this error
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
    manager = BackupManager()
    # Example courses list (course name, course ID)
    courses = [("Test Course", "12345")]
    manager.start_backup_process(courses)