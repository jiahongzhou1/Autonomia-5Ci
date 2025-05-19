import sys
import socket
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint

# Client Configuration
CLIENT_HOST = '100.104.236.29'
CLIENT_PORT = 5000

def encode_message(message_type, start_x, start_y, end_x, end_y, color, size):
    """Encodes drawing data into a string format."""
    return f"{message_type},{start_x},{start_y},{end_x},{end_y},{color},{size};"

def decode_message(data):
    """Decodes a string into drawing data."""
    parts = data.split(',')
    if len(parts) == 7:
        message_type, start_x, start_y, end_x, end_y, color, size = parts
        return (message_type, int(start_x), int(start_y), int(end_x), int(end_y), color, int(size))
    else:
        return None  # Handle invalid format/


# Client Code
class PaintClient(QMainWindow):
    """Main window for the paint client application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Collaborative Paint")
        self.setGeometry(100, 100, 800, 600)
        self.canvas = QLabel(self)
        self.canvas.setPixmap(QPixmap(800, 600))
        self.canvas.pixmap().fill(Qt.white)
        self.setCentralWidget(self.canvas)

        self.brush_color = QColor(Qt.black)
        self.brush_size = 3
        self.last_point = None
        self.drawing = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((CLIENT_HOST, CLIENT_PORT))
        except Exception as e:
            print(f"Error connecting to server at {CLIENT_HOST}:{CLIENT_PORT}: {e}")
            print("Please make sure the server is running and the host/port are correct.")
            sys.exit(1)

        self.listen_thread = threading.Thread(target=self.listen_server, daemon=True)
        self.listen_thread.start()

    def listen_server(self):
        """Listens for data from the server in a separate thread."""
        while True:
            try:
                data = self.socket.recv(4096).decode('utf-8') # Receive as string
                if not data:
                    print("Server disconnected.")
                    break
                print(f"DATA RAW {data}")
                messages = data.split(';') #split the messages
                for message in messages:
                    if message:
                        decoded_message = decode_message(message.strip())
                        if decoded_message:
                            self.draw_remote(*decoded_message)
                            
                        else:
                            print(f"Error decoding message: {message}")

            except Exception as e:
                print(f"Error receiving data from server: {e}")
                break

    def draw_remote(self, message_type, start_x, start_y, end_x, end_y, color, size):
        """Draws on the canvas based on data received from the server."""
        if message_type == "draw":
            painter = QPainter(self.canvas.pixmap())
            pen = QPen(QColor(color), size, Qt.SolidLine)
            painter.setPen(pen)
            start = QPoint(start_x, start_y)
            end = QPoint(end_x, end_y)
            painter.drawLine(start, end)
            painter.end()
            self.canvas.update()

    def mousePressEvent(self, event):
        """Handles mouse press events for drawing."""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        """Handles mouse move events for drawing."""
        if self.drawing and self.last_point:
            painter = QPainter(self.canvas.pixmap())
            pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()
            self.canvas.update()

            message = encode_message(
                "draw",
                self.last_point.x(),
                self.last_point.y(),
                event.pos().x(),
                event.pos().y(),
                # .name() Ritorna il colore in formato esadecimale esempio #AAAAAA
                self.brush_color.name(),
                self.brush_size
            )
            try:
                self.socket.sendall((message).encode('utf-8'))
            except Exception as e:
                print(f"Error sending data to server: {e}")

            self.last_point = event.pos()

    def mouseReleaseEvent(self, event):
        """Handles mouse release events for drawing."""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.last_point = None

if __name__ == "__main__":
    # Start the client on the main thread
    app = QApplication(sys.argv)
    window = PaintClient()
    window.show()
    sys.exit(app.exec_())