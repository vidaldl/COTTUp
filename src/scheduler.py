import schedule
import time
import threading
from src.error_handler import ErrorHandler

class Scheduler:
    def __init__(self, backup_callback):
        self.error_handler = ErrorHandler()
        self.backup_callback = backup_callback
        self.scheduler_thread = None

    def schedule_backup(self, interval_type, interval_value):
        """Schedule the backup task based on the interval type and value."""
        try:
            if interval_type == "seconds":
                schedule.every(interval_value).seconds.do(self.backup_callback)
            elif interval_type == "minutes":
                schedule.every(interval_value).minutes.do(self.backup_callback)
            elif interval_type == "hours":
                schedule.every(interval_value).hours.do(self.backup_callback)
            elif interval_type == "days":
                schedule.every(interval_value).days.do(self.backup_callback)
            else:
                raise ValueError("Invalid interval type provided.")
            
            print(f"Scheduled backup every {interval_value} {interval_type}.")
            self.start_scheduler()
        except Exception as e:
            self.error_handler.handle_generic_error(e, "scheduling backups")

    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            print("Scheduler is already running.")
            return

        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def run_scheduler(self):
        """Run the scheduler loop to check and execute tasks."""
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            self.error_handler.handle_generic_error(e, "running the scheduler")

    def stop_scheduler(self):
        """Stop the scheduler."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=1)
            print("Scheduler stopped.")

    def clear_schedule(self):
        """Clear all scheduled tasks."""
        schedule.clear()
        print("All scheduled tasks cleared.")

if __name__ == "__main__":
    import datetime

    def dummy_backup():
        print(f"Backup started at {datetime.datetime.now()}")

    scheduler = Scheduler(backup_callback=dummy_backup)
    scheduler.schedule_backup("seconds", 5)  # Schedule backup every 5 seconds

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped manually.")
        scheduler.stop_scheduler()
