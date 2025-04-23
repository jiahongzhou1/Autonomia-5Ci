import sys
import subprocess
import os
import signal
from selenium import webdriver
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtGui import QIcon


class ServerControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.process = None
        self.drive = None

    def init_ui(self):
        self.setWindowTitle("LAN Server Controller")
        self.setGeometry(100, 100, 300, 150)

        self.status_label = QLabel("Status: Stopped", self)

        self.start_button = QPushButton("Start Server", self)
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton("Stop Server", self)
        self.stop_button.clicked.connect(self.stop_server)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def start_server(self):
        if self.process is None:
            self.drive = webdriver.Chrome()
            self.drive.get("http://localhost:5000")
            self.process = subprocess.Popen(["python", "CreatePartyRoom.py"])
            self.status_label.setText("Status: Running")

    def stop_server(self):
        if self.process:
            try:
                os.kill(self.process.pid, signal.SIGTERM)
                self.drive.quit()
            except Exception as e:
                print(f"Error stopping server: {e}")
            self.process = None
            self.drive = None
            self.status_label.setText("Status: Stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerControlApp()
    window.show()
    sys.exit(app.exec_())
