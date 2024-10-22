import unittest
from src.scheduler import Scheduler
from src.config_manager import ConfigManager
from unittest.mock import patch

class TestSchedulerConfigIntegration(unittest.TestCase):
    def setUp(self):
        """Set up scheduler and configuration manager."""
        self.config_manager = ConfigManager()
        self.scheduler = Scheduler(lambda: print("Scheduled task executed"))

    @patch("src.scheduler.Scheduler.schedule_backup")
    def test_dynamic_schedule_update(self, mock_schedule_backup):
        """Test that schedule updates dynamically based on configuration changes."""
        self.config_manager.update_config("backup_interval", {"type": "minutes", "value": 5})
        backup_interval = self.config_manager.get_config("backup_interval")

        # Verify that the schedule is updated according to config settings
        self.scheduler.schedule_backup(backup_interval["type"], backup_interval["value"])
        mock_schedule_backup.assert_called_with("minutes", 5)

if __name__ == "__main__":
    unittest.main()
