import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel, QScrollArea, QFrame, QPushButton,QHBoxLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal # Import pyqtSignal

# Define the path to the 'Saves' directory
# This assumes the 'Saves' folder is in the same directory as the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_IR = os.path.join(SCRIPT_DIR, "Saves")

# New class for a clickable frame
class ClickableFrame(QFrame):
    """A QFrame that emits a clicked signal when pressed."""
    clicked = pyqtSignal() # Define a custom signal

    def __init__(self, filename, parent=None):
        super().__init__(parent)

        # Set frame properties to create the box appearance
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)

        # Create a layout for the content inside the box
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) # Add padding inside the box
        layout.setAlignment(Qt.AlignCenter) # Center the content vertically

        # Create a label for the filename (removing the last 4 characters for extension)
        # Ensure filename is long enough before slicing
        display_filename = filename[:-5] if len(filename) > 4 and filename.lower().endswith('.json') else filename # Only remove .json
        filename_label = QLabel(display_filename, self)
        filename_label.setAlignment(Qt.AlignCenter) # Center the text horizontally
        filename_label.setAttribute(Qt.WA_TransparentForMouseEvents) # Allow mouse events to pass through

        # Add the label to the frame's layout
        layout.addWidget(filename_label)

        self.setLayout(layout) # Set the layout for the frame

        # Store the original filename (including extension)
        self.original_filename = filename

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        # Check if the left mouse button was pressed
        if event.button() == Qt.LeftButton:
            # Emit the custom clicked signal
            self.clicked.emit()
        # Call the base class method to ensure normal event processing continues
        super().mousePressEvent(event)


class FileBrowserWindow(QMainWindow):
    """Main window for the file browser application."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Saves Folder Contents")
        self.setGeometry(100, 100, 400, 600) # Initial window size

        # Create the 'Saves' directory if it doesn't exist
        if not os.path.exists(SAVED_IR):
            try:
                os.makedirs(SAVED_IR)
                print(f"Created directory: {SAVED_IR}")
            except OSError as e:
                print(f"Error creating directory {SAVED_IR}: {e}")
                # Handle error, maybe show a message box and exit

        # Create a central widget and a layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Server Connection Box ---
        server_connect_frame = QFrame(self)
        server_connect_frame.setFrameShape(QFrame.StyledPanel)
        server_connect_layout = QHBoxLayout(server_connect_frame) #dice che tutti i componenti di server server_connect_frame finiranno detro server_connect_layout
        server_connect_layout.setContentsMargins(10, 10, 10, 10)
        server_connect_layout.setSpacing(10)

        self.ip_input = QLineEdit(self)
        # Removed: self.ip_input.setPlaceholderText("Server IP (e.g., 127.0.0.1)")
        self.ip_input.setText('127.0.0.1') # Default IP
        server_connect_layout.addWidget(QLabel("IP:", self))
        server_connect_layout.addWidget(self.ip_input)

        self.port_input = QLineEdit(self)
        # Removed: self.port_input.setPlaceholderText("Port (e.g., 5000)")
        self.port_input.setText('5000') # Default Port
        server_connect_layout.addWidget(QLabel("Port:", self))
        server_connect_layout.addWidget(self.port_input)

        self.connect_button = QPushButton("Connect to shared whiteboard", self)
        self.connect_button.clicked.connect(self.set_server_details)
        server_connect_layout.addWidget(self.connect_button)

        main_layout.addWidget(server_connect_frame)

        # --- Create New File Box ---
        create_file_frame = QFrame(self)
        create_file_frame.setFrameShape(QFrame.StyledPanel) # Use StyledPanel for a different look
        create_file_layout = QHBoxLayout(create_file_frame)
        create_file_layout.setContentsMargins(10, 10, 10, 10)
        create_file_layout.setSpacing(10)

        self.new_filename_input = QLineEdit(self)
        self.new_filename_input.setPlaceholderText("Enter new filename") # Removed .json from placeholder
        create_file_layout.addWidget(QLabel("New File:", self))
        create_file_layout.addWidget(self.new_filename_input)

        create_button = QPushButton("Create File", self)
        create_button.clicked.connect(self.create_new_file)
        create_file_layout.addWidget(create_button)

        main_layout.addWidget(create_file_frame)

        # --- Delete File Box ---
        delete_file_frame = QFrame(self)
        delete_file_frame.setFrameShape(QFrame.StyledPanel) # Use StyledPanel
        delete_file_layout = QHBoxLayout(delete_file_frame)
        delete_file_layout.setContentsMargins(10, 10, 10, 10)
        delete_file_layout.setSpacing(10)

        self.delete_filename_input = QLineEdit(self)
        self.delete_filename_input.setPlaceholderText("Enter filename to delete") # Removed .json from placeholder
        delete_file_layout.addWidget(QLabel("Delete File:", self))
        delete_file_layout.addWidget(self.delete_filename_input)

        delete_button = QPushButton("Delete File", self)
        delete_button.clicked.connect(self.delete_existing_file)
        delete_file_layout.addWidget(delete_button)

        main_layout.addWidget(delete_file_frame)


        # --- File List Display ---
        # Create a widget to hold the file boxes
        self.files_container_widget = QWidget(self)
        self.files_layout = QVBoxLayout(self.files_container_widget)
        self.files_layout.setAlignment(Qt.AlignTop) # Align items to the top

        # Create a scroll area and set the files container widget as its widget
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True) # Allow the widget inside to resize with the scroll area
        scroll_area.setWidget(self.files_container_widget)

        # Add the scroll area to the main window's layout
        main_layout.addWidget(scroll_area)

        # Set the main layout for the central widget
        central_widget.setLayout(main_layout)

        # Populate the initial file list
        self.refresh_file_list()

    def set_server_details(self, suppress_message=False):
        """
        Sets the server IP and Port from the input fields.
        Args:
            suppress_message (bool): If True, suppresses the QMessageBox.
        """
        ip = self.ip_input.text().strip()
        port_str = self.port_input.text().strip()

        if not ip:
            if not suppress_message:
                QMessageBox.warning(self, "Input Error", "Please enter a server IP address.")
            return False

        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError("Port must be between 1 and 65535.")
        except ValueError as e:
            if not suppress_message:
                QMessageBox.warning(self, "Input Error", f"Invalid port number: {e}")
            return False
        self.file_box_clicked(IP=ip,PORT=port)


    def refresh_file_list(self):
        """Clears the current file list display and repopulates it."""
        # Clear existing widgets from the layout
        while self.files_layout.count():
            child = self.files_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Check if the 'Saves' directory exists
        if os.path.exists(SAVED_IR) and os.path.isdir(SAVED_IR):
            print(f"Refreshing directory: {SAVED_IR}")
            # Get a list of files in the directory
            try:
                # Filter for actual files only
                files = [file for file in os.listdir(SAVED_IR) if os.path.isfile(os.path.join(SAVED_IR, file))]
                print(f"Found {len(files)} files.")

                if files:
                    # Create a ClickableFrame for each file and connect its clicked signal
                    for filename in files:
                        if(filename == "tmp.json"):
                            continue
                        # Create an instance of our new ClickableFrame class
                        file_box = ClickableFrame(filename, self)
                        # Connect the clicked signal to a handler method, passing the filename
                        file_box.clicked.connect(lambda checked=False, name=filename: self.file_box_clicked(filename=name ,filepath= os.path.join(SAVED_IR, name)))
                        # Add the clickable frame to the layout
                        self.files_layout.addWidget(file_box)
                else:
                    # Add a message if no files are found
                    no_files_label = QLabel("No files found in the 'Saves' folder.", self)
                    no_files_label.setAlignment(Qt.AlignCenter)
                    self.files_layout.addWidget(no_files_label)

            except Exception as e:
                error_label = QLabel(f"Error listing files: {e}", self)
                error_label.setAlignment(Qt.AlignCenter)
                self.files_layout.addWidget(error_label)

        else:
            # Add a message if the 'Saves' directory does not exist
            no_folder_label = QLabel(f"The 'Saves' folder was not found at:\n{SAVED_IR}", self)
            no_folder_label.setAlignment(Qt.AlignCenter)
            self.files_layout.addWidget(no_folder_label)

    def file_box_clicked(self, filename = "tmp.json" , filepath = "Saves/tmp.json" , IP = "127.0.0.1" , PORT = "5000"):
        env = os.environ.copy()
        env["QT_OPENGL"] = "software"
        """
        Handles the click event on a file box, launching the client script
        with the selected file and the configured server details.
        """
        try:
            # Pass IP and Port as additional command-line arguments to client.py
            # You will need to modify client.py to accept and use these arguments.
            print(f"AAAAAAA{IP}")
            subprocess.Popen([
                sys.executable,
                'client.py',
                f'{filename}',
                f'{filepath}',
                f'{IP}',
                f'{PORT}'
            ], cwd=SCRIPT_DIR , env=env) # Use check=True to raise CalledProcessError on non-zero exit codes
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Client Launch Error", f"Client script failed with error: {e}")
            print("Script failed:", e)
        except FileNotFoundError:
            QMessageBox.critical(self, "Client Launch Error", "Error: client.py not found. Make sure 'pythone/client.py' exists.")
            print("Error: client.py not found.")
        except Exception as e:
            QMessageBox.critical(self, "Client Launch Error", f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")


    def create_new_file(self):
        """Creates a new empty file in the Saves directory."""
        filename = self.new_filename_input.text().strip() # Get filename and remove whitespace

        if not filename:
            QMessageBox.warning(self, "Input Error", "Please enter a filename.")
            return

        # Ensure the filename ends with .json if not already
        if not filename.lower().endswith('.json'):
            filename += '.json'

        file_path = os.path.join(SAVED_IR, filename)

        if os.path.exists(file_path):
            QMessageBox.warning(self, "File Exists", f"File '{filename}' already exists.")
            return
        try:
            with open(file_path, 'w') as f:
                f.write("") # Create an empty file
            print(f"Created file: {file_path}")
            QMessageBox.information(self, "Success", f"File '{filename}' created successfully.")
            self.new_filename_input.clear() # Clear the input field
            self.refresh_file_list() # Refresh the list display
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating file '{filename}': {e}")

    def delete_existing_file(self):
        """Deletes an existing file from the Saves directory."""
        filename = self.delete_filename_input.text().strip() # Get filename and remove whitespace

        if not filename:
            QMessageBox.warning(self, "Input Error", "Please enter a filename to delete.")
            return

        # Ensure the filename ends with .json if not already, for consistency
        if not filename.lower().endswith('.json'):
            filename += '.json'

        file_path = os.path.join(SAVED_IR, filename)

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"File '{filename}' not found.")
            return

        # Optional: Add a confirmation dialog
        reply = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete '{filename}'?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
                QMessageBox.information(self, "Success", f"File '{filename}' deleted successfully.")
                self.delete_filename_input.clear() # Clear the input field
                self.refresh_file_list() # Refresh the list display
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting file '{filename}': {e}")
        else:
            print("Deletion cancelled.")


if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)

    # Create and show the main window
    window = FileBrowserWindow()
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())