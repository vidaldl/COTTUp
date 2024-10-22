import unittest
import tempfile
import os
from src.file_manager import FileManager

class TestFileManager(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_manager = FileManager()

    def tearDown(self):
        """Cleanup the temporary directory after tests."""
        self.temp_dir.cleanup()

    def test_create_backup_folder(self):
        """Test creating a backup folder in the temporary directory."""
        course_name = "TestCourse"
        folder_path = self.file_manager.create_backup_folder(self.temp_dir.name, course_name)
        self.assertTrue(os.path.exists(folder_path))
        self.assertTrue(os.path.isdir(folder_path))
        print(f"Backup folder created at: {folder_path}")

if __name__ == "__main__":
    unittest.main()
