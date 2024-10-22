#src/token_manager.py
# src/token_manager.py

import keyring
from src.error_handler import ErrorHandler, ConfigError
from tkinter import simpledialog, Tk

class TokenManager:
    def __init__(self):
        self.service_name = "CanvasBackupManager"
        self.error_handler = ErrorHandler()
        self.api_token = None

    def get_token(self):
        """Retrieve the API token from the keyring."""
        try:
            if not self.api_token:
                self.api_token = keyring.get_password(self.service_name, "api_token")
            if not self.api_token:
                self.api_token = self.prompt_for_token()
            return self.api_token
        except Exception as e:
            self.error_handler.handle_generic_error(e, "retrieving API token")
            return None

    def prompt_for_token(self):
        """Prompt the user to enter an API token and store it securely."""
        try:
            root = Tk()
            root.withdraw()  # Hide the main window
            token = simpledialog.askstring("API Token", "Enter your Canvas API token:")
            root.destroy()

            if token:
                self.store_token(token)
                return token
            else:
                raise ConfigError("No API token was provided.")
        except Exception as e:
            self.error_handler.handle_generic_error(e, "prompting for API token")
            return None

    def store_token(self, token):
        """Store the API token securely using keyring."""
        try:
            keyring.set_password(self.service_name, "api_token", token)
        except Exception as e:
            self.error_handler.handle_generic_error(e, "storing API token")

    def delete_token(self):
        """Delete the stored API token."""
        try:
            keyring.delete_password(self.service_name, "api_token")
            self.api_token = None
            print("API token deleted successfully.")
        except Exception as e:
            self.error_handler.handle_generic_error(e, "deleting API token")

    def refresh_token(self):
        """Refresh or update the API token by prompting the user."""
        self.delete_token()
        return self.get_token()

if __name__ == "__main__":
    token_manager = TokenManager()
    token = token_manager.get_token()
    if token:
        print("API Token retrieved successfully.")
    else:
        print("Failed to retrieve API Token.")