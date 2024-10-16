import logging
import logging.handlers
from pathlib import Path

class Logger:
    def __init__(self, log_file_path="logs/app.log"):
        self.log_file_path = Path(log_file_path)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the logs directory exists

        self.logger = logging.getLogger("CanvasBackupManager")
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler for logging
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler for logging to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Set the logging format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """Return the logger instance."""
        return self.logger

if __name__ == "__main__":
    logger_manager = Logger()
    logger = logger_manager.get_logger()

    # Test logging at different levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")