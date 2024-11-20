# src/backup_manager.py
import os
import requests
import time
from src.token_manager import TokenManager
from src.file_manager import FileManager
from src.error_handler import ErrorHandler, APIError, FileError
from src.logger import Logger

class BackupManager:
    def __init__(self, update_queue=None):
        self.api_base_url = "https://byui.instructure.com/api/v1"  # Update this URL
        self.token_manager = TokenManager()
        self.file_manager = FileManager()
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger()
        self.api_token = self.token_manager.get_token()
        self.courses = []
        self.update_queue = update_queue

    def load_courses_from_csv(self, file_path):
        """Load and validate courses from a CSV file."""
        self.logger.info(f"Loading courses from CSV: {file_path}")
        try:
            courses = self.file_manager.validate_and_parse_csv(file_path)
            if not courses:
                self.logger.error("No valid courses found in the CSV.")
            else:
                self.courses = courses
                self.logger.info(f"Successfully loaded {len(courses)} courses from CSV.")
                # Debug: Print courses to verify
                for course in self.courses:
                    print(f"Loaded course: {course[0]}, ID: {course[1]}")
        except Exception as e:
            self.error_handler.handle_file_error(e, "loading courses from CSV")


    def trigger_backup(self, course_name, course_id):
        """Initiate the backup process for a course."""
        if not self.file_manager.backup_folder:
            self.logger.error("Backup folder is not set. Please select a backup folder.")
            if self.update_queue:
                self.update_queue.put((course_name, "Failed", 0))
            return False
        self.logger.info(f"Triggering backup for course: {course_name} (ID: {course_id})")
        if self.update_queue:
            self.update_queue.put((course_name, "In Progress", 0))
        
        # Step 1: Initiate the export
        export_id = self.initiate_export(course_id)
        if not export_id:
            if self.update_queue:
                self.update_queue.put((course_name, "Failed", 0))
            return False
        
        # Step 2: Poll for export status
        export = self.poll_export_status(course_id, export_id, course_name)
        if not export:
            if self.update_queue:
                self.update_queue.put((course_name, "Failed", 0))
            return False
        
        # Step 3: Download the backup
        self.download_backup(course_name, export)
        return True
        

    def initiate_export(self, course_id):
        """Initiate a course export and return the export ID."""
        endpoint = f"{self.api_base_url}/courses/{course_id}/content_exports"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "export_type": "common_cartridge",
            "skip_notifications": True
        }
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            export = response.json()
            export_id = export['id']
            self.logger.info(f"Export initiated for course {course_id}, export ID: {export_id}")
            return export_id
        except requests.exceptions.RequestException as e:
            self.error_handler.handle_api_error(e, f"initiating backup for course {course_id}")
            return None
        
    def poll_export_status(self, course_id, export_id, course_name):
        """Poll the export status until it's completed or failed."""
        max_attempts = 2000
        delay = 5  # seconds
        attempts = 0

        while attempts < max_attempts:
            export = self.check_backup_status(course_id, export_id)
            if not export:
                attempts += 1
                time.sleep(delay)
                continue

            workflow_state = export['workflow_state']
            if self.update_queue:
                progress = min(90, int((attempts / max_attempts) * 90))
                self.update_queue.put((course_name, "In Progress", progress))
            
            if workflow_state == 'exported':
                self.logger.info(f"Export completed for course {course_id}")
                return export
            elif workflow_state in ['failed', 'cancelled']:
                self.logger.error(f"Export {workflow_state} for course {course_id}")
                return None
            else:
                self.logger.info(f"Export status for course {course_id}: {workflow_state}")
                attempts += 1
                time.sleep(delay)

        self.logger.error(f"Export did not complete in expected time for course {course_id}")
        return None

    def mock_api_call(self, course_id):
        """Mock API method for triggering backup, returns False to simulate an error."""
        return False

    def check_backup_status(self, course_id, export_id):
        """Check the status of the backup for a given course ID."""
        endpoint = f"{self.api_base_url}/courses/{course_id}/content_exports/{export_id}"
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            export = response.json()
            workflow_state = export['workflow_state']
            self.logger.info(f"Backup status for course {course_id}: {workflow_state}")
            return export
        except requests.exceptions.RequestException as e:
            self.error_handler.handle_api_error(e, f"checking backup status for course {course_id}")
            return None

    def download_backup(self, course_name, export):
        """Download the completed backup for a given course."""
        attachment = export.get('attachment')
        if not attachment:
            self.logger.error(f"No attachment found for export {export.get('id')}")
            return False

        download_url = attachment['url']
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        try:
            self.logger.debug(f"Downloading backup from {download_url}")
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()
            self.logger.debug(f"Received response with status code {response.status_code}")
            file_path = self.file_manager.save_backup(course_name, response)
            if not file_path:
                self.logger.error(f"Failed to save backup for course {course_name}")
                if self.update_queue:
                    self.update_queue.put((course_name, "Failed", 0))
                return False
            self.logger.info(f"Backup downloaded for course {course_name} at {file_path}")
            if self.update_queue:
                self.update_queue.put((course_name, "Completed", 100))
            return True
        except requests.exceptions.RequestException as e:
            self.error_handler.handle_api_error(e, f"downloading backup for course {course_name}")
            if self.update_queue:
                self.update_queue.put((course_name, "Failed", 0))
            return False

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