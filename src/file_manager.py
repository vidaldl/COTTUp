#src/file_manager.py
import os
import csv
import time
import re
from pathlib import Path
from src.error_handler import ErrorHandler, FileError
from src.logger import Logger

class FileManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.backup_folder = None
        self.logger = Logger().get_logger()


    def sanitize_course_name(self, course_name):
        """Remove or replace invalid characters in course name."""
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', course_name)
        return sanitized_name
    

    def validate_and_parse_csv(self, file_path):
        """Validate and parse the CSV file containing course information."""
        courses = []
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 2:
                        course_name = row[0].strip()
                        course_id_raw = row[1].strip()
                        course_id = self.extract_course_id(course_id_raw)
                        if course_id:
                            courses.append((course_name, course_id))
                        else:
                            print(f"Invalid course ID in row: {row}")
                    else:
                        print(f"Skipping invalid row: {row}")
                return courses
        except Exception as e:
            self.error_handler.handle_file_error(e, "parsing CSV")
            return []

    def extract_course_id(self, course_id_raw):
        """Extract numeric course ID from the input, handling URLs and IDs."""
        # If the course_id_raw is a URL, extract the numeric ID
        if course_id_raw.startswith('http'):
            # Assuming the course URL ends with '/courses/{id}'
            try:
                parts = course_id_raw.rstrip('/').split('/')
                course_id = parts[-1]
                if course_id.isdigit():
                    return course_id
                else:
                    return None
            except Exception as e:
                print(f"Error extracting course ID from URL: {course_id_raw}")
                return None
        elif course_id_raw.isdigit():
            # If it's already a numeric ID
            return course_id_raw
        else:
            return None
    
    def create_backup_folder(self, base_folder, course_name):
        """Create a folder for the course backups based on the course name."""
        try:
            sanitized_course_name = self.sanitize_course_name(course_name)
            course_folder = Path(base_folder) / sanitized_course_name
            course_folder.mkdir(parents=True, exist_ok=True)
            return course_folder
        except Exception as e:
            self.error_handler.handle_file_error(e, f"creating backup folder for course {course_name}")
            return None

    def save_backup(self, course_name, response):
        """Save the backup file for a course in the specified folder."""
        try:
            if not self.backup_folder:
                raise FileError("Backup folder is not set.")

            course_folder = self.create_backup_folder(self.backup_folder, course_name)
            if not course_folder:
                raise FileError(f"Failed to create or access folder for course: {course_name}")

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            file_name = f"{course_name}_backup_{timestamp}.zip"
            file_path = course_folder / file_name

            self.logger.debug(f"Saving backup to {file_path}")

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            self.logger.info(f"Backup saved for course {course_name} at {file_path}")
            return file_path
        except Exception as e:
            self.logger.exception(f"Exception occurred while saving backup for course {course_name}")
            self.error_handler.handle_file_error(e, f"saving backup for course {course_name}")
            return None

if __name__ == "__main__":
    import os
    file_manager = FileManager()
    test_csv_path = os.path.join(os.path.dirname(__file__), "../tests/csv/testcsv.csv")
    test_base_folder = os.path.join(os.path.dirname(__file__), "../tests/backups")

    # Test CSV Parsing
    courses = file_manager.validate_and_parse_csv(test_csv_path)
    if courses:
        print("Courses loaded:", courses)

    # Test Backup Saving (dummy response for testing)
    from requests.models import Response

    class DummyResponse:
        def iter_content(self, chunk_size=8192):
            yield b"Dummy data"

    dummy_response = DummyResponse()
    file_manager.save_backup("Test Course", dummy_response, test_base_folder)
