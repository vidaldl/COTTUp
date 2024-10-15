import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Canvas LMS Backup Manager")
        self.root.geometry("800x600")
        self.setup_menu()
        self.setup_layout()

    def setup_menu(self):
        """Set up the menu bar for the application."""
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open CSV", command=self.open_csv_file)
        file_menu.add_command(label="Select Backup Folder", command=self.select_backup_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def setup_layout(self):
        """Set up the main layout of the application."""
        # Frame for File Selection
        self.file_frame = ttk.Frame(self.root, padding="10")
        self.file_frame.grid(row=0, column=0, sticky="ew")

        self.csv_label = ttk.Label(self.file_frame, text="CSV File: None Selected")
        self.csv_label.grid(row=0, column=0, sticky="w")

        self.folder_label = ttk.Label(self.file_frame, text="Backup Folder: None Selected")
        self.folder_label.grid(row=1, column=0, sticky="w")

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
            # Placeholder: Call method to process the CSV file (to be implemented)

    def select_backup_folder(self):
        """Open a folder dialog to select the backup directory."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_label.config(text=f"Backup Folder: {folder_path}")
            # Placeholder: Store folder path for backups (to be implemented)

    def exit_app(self):
        """Exit the application."""
        self.root.quit()

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = GUI()
    app.run()