from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import threading
from src.gui import GUI
from src.logger import Logger

class TrayApp:
    def __init__(self):
        self.icon = None
        self.thread = None
        self.gui = GUI()
        self.logger = Logger().get_logger()

    def _create_image(self, width, height, color1, color2):
        """Helper method to create a simple icon for the tray."""
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill=color2
        )
        return image

    def setup_tray(self):
        """Set up the tray icon and menu."""
        # Create the tray menu
        menu = Menu(
            MenuItem('Open GUI', self.open_gui),
            MenuItem('Exit', self.exit_app)
        )
        # Create the icon image
        image = self._create_image(64, 64, 'black', 'white')
        # Initialize the icon
        self.icon = Icon("CanvasBackupManager", image, "Canvas Backup Manager", menu)

    def open_gui(self, icon, item):
        self.logger.info("Opening the GUI window from tray icon.")
        self.gui.run()  

    def exit_app(self, icon, item):
        """Exit the application."""
        self.icon.stop()

    def run(self):
        """Run the tray icon in a separate thread."""
        self.setup_tray()
        self.thread = threading.Thread(target=self.icon.run, daemon=True)
        self.thread.start()

    def start_backup(self, icon, item):
        """Placeholder method to start backup operations."""
        print("Backup operations started!")  # This will be connected later

    def setup_tray(self):
        """Set up the tray icon and menu."""
        menu = Menu(
            MenuItem('Open GUI', self.open_gui),
            MenuItem('Start Backup', self.start_backup),
            MenuItem('Exit', self.exit_app)
        )
        image = self._create_image(64, 64, 'black', 'white')
        self.icon = Icon("CanvasBackupManager", image, "Canvas Backup Manager", menu)

if __name__ == "__main__":
    tray_app = TrayApp()
    tray_app.run()
    input("Tray application running... Press Enter to exit.\n")
