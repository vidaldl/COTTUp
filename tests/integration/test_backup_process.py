import os
import unittest
from unittest.mock import patch, MagicMock
from src.backup_manager import BackupManager
from src.scheduler import Scheduler
from src.file_manager import FileManager

class TestBackupProcess(unittest.TestCase):
    def setUp(self):
        """Set up the necessary objects before each test."""
        self.backup_manager = BackupManager()
        self.scheduler = Scheduler(self.backup_manager.trigger_backup)
        self.file_manager = FileManager()

        # Sample test data
        self.test_csv_path = os.path.join(os.path.dirname(__file__), "../csv/testcsv.csv")
        self.test_course_data = [("Test Course 1", "12345"), ("Test Course 2", "67890")]

    @patch("src.backup_manager.BackupManager.trigger_backup")
    def test_successful_backup(self, mock_trigger_backup):
        """Test a successful backup process."""
        mock_trigger_backup.return_value = True  # Mock a successful backup response

        self.backup_manager.load_courses_from_csv(self.test_csv_path)
        for course_name, course_id in self.backup_manager.courses:
            result = self.backup_manager.trigger_backup(course_name, course_id)
            self.assertTrue(result)
            print(f"Backup successful for {course_name}")

    @patch("src.backup_manager.BackupManager.trigger_backup")
    def test_backup_failure(self, mock_trigger_backup):
        """Test a backup process that encounters an API failure."""
        mock_trigger_backup.return_value = False  # Mock a failure response

        self.backup_manager.load_courses_from_csv(self.test_csv_path)
        for course_name, course_id in self.backup_manager.courses:
            result = self.backup_manager.trigger_backup(course_name, course_id)
            self.assertFalse(result)
            print(f"Backup failed for {course_name}")

    @patch("src.backup_manager.BackupManager.trigger_backup")
    def test_scheduler_integration(self, mock_trigger_backup):
        """Test scheduler integration with backup operations."""
        mock_trigger_backup.return_value = True  # Mock a successful backup

        self.backup_manager.load_courses_from_csv(self.test_csv_path)
        self.scheduler.schedule_backup("seconds", 1)  # Schedule backup every second for test

        # Run the scheduler briefly for testing purposes
        try:
            import time
            time.sleep(3)  # Let the scheduler run for a few seconds
        except KeyboardInterrupt:
            pass

        self.scheduler.stop_scheduler()
        print("Scheduler stopped after brief run.")

if __name__ == "__main__":
    unittest.main()
