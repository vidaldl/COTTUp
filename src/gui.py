#src/gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.scheduler import Scheduler
from src.backup_manager import BackupManager
from src.persistence_manager import PersistenceManager
import threading
import queue
#
class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("COTT - Up")
        self.root.geometry("800x600")
        self.setup_menu()
        self.setup_layout()
        self.selected_csv_path = None 
        self.persistence_manager = PersistenceManager()
        self.scheduler = Scheduler(self.run_scheduled_backup)
        self.setup_schedule_options()
        self.update_queue = queue.Queue()
        self.process_queue()
        self.backup_manager = BackupManager(update_queue=self.update_queue)
        self.error_handler = self.backup_manager.error_handler



    def process_queue(self):
        try:
            while True:
                # Try to get a message from the queue without blocking
                item = self.update_queue.get_nowait()
                course_name, status, progress = item
                self.update_gui_with_status(course_name, status, progress)
        except queue.Empty:
            pass
        # Schedule the next queue check
        self.root.after(100, self.process_queue)
    def run_backup_now(self):
        """Run backups immediately for all loaded courses."""
        if not self.backup_manager.courses:
            messagebox.showwarning("No Courses", "No courses loaded to backup.")
            return

        for course_name, course_id in self.backup_manager.courses:
            thread = threading.Thread(
                target=self.backup_manager.trigger_backup, 
                args=(course_name, course_id)
            )
            thread.start()


    def load_saved_statuses(self):
        """Load and display the saved statuses in the GUI."""
        print("Loading saved statuses into the GUI.")
        saved_statuses = self.persistence_manager.get_all_statuses()
        for course_name, course_id in self.backup_manager.courses:
            print(f"Adding course to GUI: {course_name}, ID: {course_id}")
            status_info = saved_statuses.get(course_id, {"status": "Not Started", "progress": 0})
            self.update_gui_with_status(course_name, status_info["status"], status_info["progress"])

    def setup_course_list(self):
        """Set up the list to display courses and their status."""
        self.course_list = ttk.Treeview(
            self.root, 
            columns=("Course Name", "Status", "Progress"), 
            show="headings", 
            height=10
        )
        self.course_list.heading("Course Name", text="Course Name")
        self.course_list.heading("Status", text="Status")
        self.course_list.heading("Progress", text="Progress")

        # Set column widths
        self.course_list.column("Course Name", width=200)
        self.course_list.column("Status", width=100)
        self.course_list.column("Progress", width=100)

        # Place the Treeview in the grid
        self.course_list.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def update_gui_with_status(self, course_name, status, progress):
        """Update the GUI with the course status and progress."""
        print(f"Updating GUI: Course: {course_name}, Status: {status}, Progress: {progress}%")
        # Check if the item already exists and update it
        for item in self.status_table.get_children():
            values = self.status_table.item(item, 'values')
            if values[0] == course_name:
                self.status_table.item(item, values=(course_name, status, f"{progress}%"))
                return
        # Insert new item if not found
        self.status_table.insert("", "end", values=(course_name, status, f"{progress}%"))
        
    def setup_schedule_options(self):
        """Set up scheduling options in the GUI."""
        schedule_frame = ttk.LabelFrame(self.root, text="Schedule Backups")
        schedule_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.interval_var = ttk.Combobox(schedule_frame, values=["Test - 5 Seconds", "30 minutes", "1 hour", "Daily"])
        self.interval_var.set("Select Interval")
        self.interval_var.grid(row=0, column=0, padx=5, pady=5)

        set_schedule_button = ttk.Button(schedule_frame, text="Set Schedule", command=self.set_schedule)
        set_schedule_button.grid(row=0, column=1, padx=5, pady=5)
        

    def set_schedule(self):
        """Set the schedule based on user selection."""
        interval = self.interval_var.get()
        if interval == "30 minutes":
            self.scheduler.schedule_backup("minutes", 30)
        elif interval == "1 hour":
            self.scheduler.schedule_backup("hours", 1)
        elif interval == "Daily":
            self.scheduler.schedule_backup("days", 1)
        elif interval == "Test - 5 Seconds":
            self.scheduler.schedule_backup("seconds", 1)
        else:
            print(f"Unknown interval: {interval}")


        print(f"Backup scheduled: {interval}")

    def run_scheduled_backup(self):
        """Callback for running scheduled backups."""
        for course_name, course_id in self.backup_manager.courses:
            thread = threading.Thread(target=self.backup_manager.trigger_backup, args=(course_name, course_id))
            thread.start()

    def setup_menu(self):
        """Set up the menu bar for the application."""
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open CSV", command=self.open_csv_file)
        file_menu.add_command(label="Select Backup Folder", command=self.select_backup_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Refresh API Token", command=self.refresh_api_token)  # New menu item
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def refresh_api_token(self):
        """Refresh the API token by prompting the user to enter a new one."""
        try:
            # Delete the existing token
            self.backup_manager.token_manager.delete_token()
            # Prompt for a new token
            new_token = self.backup_manager.token_manager.get_token()
            if new_token:
                messagebox.showinfo("API Token Updated", "API token refreshed successfully.")
                self.backup_manager.api_token = new_token  # Update the token in BackupManager
            else:
                messagebox.showwarning("API Token Not Updated", "API token was not updated.")
        except Exception as e:
            self.error_handler.handle_generic_error(e, "refreshing API token")

    def setup_layout(self):
        """Set up the main layout of the application."""
        # Frame for File Selection
        self.file_frame = ttk.Frame(self.root, padding="10")
        self.file_frame.grid(row=0, column=0, sticky="ew")

        self.csv_label = ttk.Label(self.file_frame, text="CSV File: None Selected")
        self.csv_label.grid(row=0, column=0, sticky="w")

        self.folder_label = ttk.Label(self.file_frame, text="Backup Folder: None Selected")
        self.folder_label.grid(row=1, column=0, sticky="w")

        # Add "Run Backup Now" button
        run_backup_button = ttk.Button(self.root, text="Run Backup Now", command=self.run_backup_now)
        run_backup_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Frame for Backup Status Table
        self.table_frame = ttk.Frame(self.root, padding="10")
        self.table_frame.grid(row=1, column=0, sticky="nsew")
        self.setup_status_table()

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_status_table(self):
        """Set up the table to display backup status."""
        columns = ("course_name", "status", "progress")
        self.status_table = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        self.status_table.heading("course_name", text="Course Name")
        self.status_table.heading("status", text="Status")
        self.status_table.heading("progress", text="Progress")

        # Add scrollbar for the table
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.status_table.yview)
        self.status_table.configure(yscroll=scrollbar.set)
        self.status_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Set grid weights to allow the table to resize
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def open_csv_file(self):
        """Open a file dialog to select the CSV file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_label.config(text=f"CSV File: {file_path}")
            self.selected_csv_path = file_path
            self.process_csv()

    def process_csv(self):
        """Pass the selected CSV to the BackupManager for processing."""
        self.backup_manager.load_courses_from_csv(self.selected_csv_path)
        self.load_saved_statuses()  # Update GUI after loading courses

    def select_backup_folder(self):
        """Open a folder dialog to select the backup directory."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_label.config(text=f"Backup Folder: {folder_path}")
            # Store the backup folder path
            self.backup_manager.file_manager.backup_folder = folder_path

    def exit_app(self):
        """Exit the application."""
        self.root.quit()

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = GUI()
    app.run()