import logging
from tkinter import messagebox

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger("ErrorHandler")
        self.logger.setLevel(logging.ERROR)
        handler = logging.FileHandler("logs/error.log")
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle_api_error(self, error, action, retry_callback=None):
        """Handle API-related errors and show a pop-up in the GUI."""
        self.logger.error(f"API Error during {action}: {error}")
        messagebox.showerror("API Error", f"An error occurred while {action}.\nError: {error}")

        if retry_callback:
            retry = messagebox.askretrycancel("Retry?", "Would you like to retry the operation?")
            if retry:
                retry_callback()

    def handle_file_error(self, error, action):
        """Handle file-related errors and show a pop-up in the GUI."""
        self.logger.error(f"File Error during {action}: {error}")
        messagebox.showerror("File Error", f"An error occurred while {action}.\nError: {error}")

    def handle_generic_error(self, error, context):
        """Handle any other generic errors."""
        self.logger.error(f"Error in {context}: {error}")
        messagebox.showerror("Error", f"An unexpected error occurred in {context}.\nError: {error}")

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message):
        super().__init__(message)

class FileError(Exception):
    """Custom exception for file-related errors."""
    def __init__(self, message):
        super().__init__(message)

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    def __init__(self, message):
        super().__init__(message)
