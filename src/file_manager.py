import os
import csv
from pathlib import Path
from src.error_handler import ErrorHandler, FileError

class FileManager:
    def __init__(self):
        self.error_handler = ErrorHandler()

    def validate_and_parse_csv(self, file_path):
        """Validate and parse the CSV file to extract course information."""
        try:
            if not file_path.endswith('.csv'):
                raise FileError("The selected file is not a CSV file.")
            
            courses = []
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) < 2:
                        raise FileError("CSV file must have at least two columns: course name and course URL.")
                    courses.append((row[0], row[1]))
            return courses
        except Exception as e:
            self.error_handler.handle_file_error(e, "parsing the CSV file")
            return []

    def create_backup_folder(self, base_folder, course_name):
        """Create a folder for the course backups based on the course name."""
        try:
            course_folder = Path(base_folder) / course_name
            course_folder.mkdir(parents=True, exist_ok=True)
            return course_folder
        except Exception as e:
            self.error_handler.handle_file_error(e, f"creating backup folder for course {course_name}")
            return None

    def save_backup(self, course_name, response, base_folder):
        """Save the backup file for a course in the specified folder."""
        try:
            course_folder = self.create_backup_folder(base_folder, course_name)
            if not course_folder:
                raise FileError(f"Failed to create or access folder for course: {course_name}")

            file_name = f"{course_name}_backup.zip"  # Assuming the backup is a zip file
            file_path = course_folder / file_name

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Backup saved for course {course_name} at {file_path}")
            return file_path
        except Exception as e:
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
