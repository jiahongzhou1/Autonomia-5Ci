import sys
import socket
import threading
import json
import os
import math
import time
import errno
from LocalServer import WhiteboardServer

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSizePolicy, QVBoxLayout, QWidget, QScrollArea, QColorDialog, QPushButton , QMessageBox, QInputDialog# Import QScrollArea
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QMouseEvent, QCloseEvent
from PyQt5.QtCore import Qt, QPoint, QRect, QMetaObject


from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QColorDialog,
    QSlider, QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, Qt, QSize

# Define a fixed large size for the canvas
FIXED_CANVAS_WIDTH = 2000
FIXED_CANVAS_HEIGHT = 2000
# converts the values related to a line/object into a string
def encode_message(message_type, start_x, start_y, end_x, end_y, color, size):
    return f"{message_type},{start_x},{start_y},{end_x},{end_y},{color},{size};"
# retrieve from a string values of a line/object
def decode_message(data):
    # split the information based on ','
    parts = data.split(',')
    if len(parts) == 7:
        # deconstruction, assign parts[0] to message_type and so on
        message_type, start_x, start_y, end_x, end_y, color, size = parts
        # converts the strings into int
        try:
            start_x = int(start_x)
            start_y = int(start_y)
            end_x = int(end_x)
            end_y = int(end_y)
            size = int(size)
            # check that the coordinates are inside the canva height and width
            #?
            if not (0 <= start_x < FIXED_CANVAS_WIDTH and 0 <= start_y < FIXED_CANVAS_HEIGHT and
                    0 <= end_x < FIXED_CANVAS_WIDTH and 0 <= end_y < FIXED_CANVAS_HEIGHT):
                print(f"Warning: Received out-of-bounds coordinates: {data}")
                return None # ignores if coordinates are not valid

            return (message_type, start_x, start_y, end_x, end_y, color, size)
        except ValueError:
            print(f"Error converting drawing data to integers: {data}")
            return None
    else:
        return None # if the message doesn't come with 7 values, it means it is not the correct format

# Client Code
# Inherit from QmainWindow
class PaintClient(QMainWindow):
    """Main window for the paint client application."""
    socketLost = pyqtSignal(bool)
    def __init__(self):
        # call the parent constructor
        super().__init__()
        # set the window title to Collaborative paint, this function is defined in QWidget which is parent class of QMainWindow
        self.setWindowTitle("Collaborative Paint")
        # Set the initial window size, also comes from QWidget    
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and a layout
        central_widget = QWidget(self) # assign this widget(PaintClient) to a variable called central_widget
        self.setCentralWidget(central_widget)  # make the central_widget become the centralWidget, this function comes from QMainWindow
        layout = QVBoxLayout(central_widget) # create a vertical layout and associate it with central_widget, so the child of central_widget will be vertically organized
        
        # Create the canvas label, Qlabel is a class that allows to display image or text, in our case it will be image
        self.canvas = QLabel(self)
        # Create a pixmap with the size that we want
        self.canvas_pixmap = QPixmap(FIXED_CANVAS_WIDTH, FIXED_CANVAS_HEIGHT)
        # fill the pixmap with white color
        self.canvas_pixmap.fill(Qt.white)
        # make the pixmap as the content of the canva Qlabel
        self.canvas.setPixmap(self.canvas_pixmap)

        self.canvas.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred) # the Qlabel widget can resize if the main window resizes.
        self.canvas.adjustSize()   # tell the canva to resize to map the pixmap size
        
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # retrieve from command line arguments and assign to variables.
        print(f'AA:{sys.argv}')
        if len(sys.argv) > 1:
            self.fileName = sys.argv[1]
        if len(sys.argv) > 2:
            self.pathName = sys.argv[2]
        if len(sys.argv) > 3:
            self.ipAddress = sys.argv[3]
        if len(sys.argv) > 4:
            self.remotePort = sys.argv[4]


        self.drawing_history = [] # an array of object that contains draw data

        print(len(sys.argv))
        # retrieve from command line arguments server ip and server port.

        try:
            # check if the file exists and that it isn't empty
            if os.path.exists(self.pathName) and os.path.getsize(self.pathName) > 0:
                # Use 'with open(...) as f:' to ensure the file is automatically closed
                # 'r' mode is for reading (default)
                with open(self.pathName, 'r', encoding='utf-8') as f:
                    # json.load() reads the JSON data from the file object (f)
                    # and parses it into a Python object (which should be a list here)
                    data_list = json.load(f)
                    if(data_list):
                        self.drawing_history = data_list
                print(f"Successfully read data from '{self.pathName}'")                
            elif not os.path.exists(self.pathName):
                print(f"Error: The file '{self.pathName}' was not found.")
            else: # File exists but is empty
                print(f"Warning: The file '{self.pathName}' is empty. Returning empty list.")            

        except json.JSONDecodeError:
            # This exception is raised if the file contains invalid JSON
            print(f"Error: Could not decode JSON from '{self.pathName}'. The file may be corrupted or not valid JSON.")
        except Exception as e:
            # Catch any other potential errors during file reading
            print(f"An error occurred while reading the file '{self.pathName}': {e}")
        
        self.update_canvas()  # calls the update_canvas function to convert drawing_history into actual draw
        
        

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # once we start the server the instance will be saved here
        #?
        self.server = None
        self.serverThread = None
        
        # Initialize ToolStatusPanel first as it handles tool selections
        # toolstatuspanel is a child of paintclass
        self.status_panel = ToolStatusPanel(parent_instance = self)
        layout.addWidget(self.status_panel)

        # Connect signals from ToolStatusPanel to PaintClient's handlers
        # self.status_panel.color_changed is a pyqtSignal and when we receive signals self.on_color_changed will be called
        self.status_panel.color_changed.connect(self.on_color_changed)
        self.status_panel.brush_size_changed.connect(self.on_brush_size_changed)
        self.status_panel.shape_changed.connect(self.on_shape_changed)       
        

        self.scroll_area = QScrollArea(self) # allows scrolling
        self.scroll_area.setWidgetResizable(False)  # so the canva will not resize as we scroll
        self.scroll_area.setWidget(self.canvas)   # tells that the canva should be scrolled

        layout.addWidget(self.scroll_area)
        central_widget.setLayout(layout)

        # Brush settings are now primarily managed through ToolStatusPanel's signals
        # Initialize default brush color and size here, which can be updated by ToolStatusPanel
        self.brush_color = self.status_panel.get_color() # Get initial color from panel
        #? self.brush_size = 3 # Default, will be updated by panel
        self.brush_size = self.status_panel.get_brush_size() # Get initial brush size
        self.current_shape = self.status_panel.get_shape() # Get initial shape
        self.drawing_shape = False # tells if we are trying to draw a shape or not 
        self.shape_start_point = None # start point of a shape 
        self.shape_temp_end_point = None # temp end point because we want to preview 

        # Remove or comment out the redundant color button from PaintClient
        # self.color_button = QPushButton("Choose Color", self)
        # self.color_button.clicked.connect(self.setColor) # This was the problematic line
        # layout.addWidget(self.color_button) 

        self.last_point = None # last point of line/object
        self.drawing = False # tells if we are drawing
        # self.addText = False # Assuming these are for future features
        # self.addGeometry = False
        
        self.socketLost.connect(self.onDisconnect)

        self.dragging = False # tells if we are dragging
        self.drag_start_pos = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

        print(self.ipAddress)
        if(self.ipAddress != "127.0.0.1"):
            print("Bomboclat")
            try:
                self.socket.connect((self.ipAddress, int(self.remotePort)))
                self.listen_thread = threading.Thread(target=self.listen_server, daemon=True)
                self.listen_thread.start()
            except Exception as e:
                print(f"Error connecting to server at {self.ipAddress}:{self.remotePort}: {e}")
                print("Please make sure the server is running and the host/port are correct.")
                print("PORCO DIO")
                sys.exit(1)

        self.listen_thread = None

    def resizeEvent(self, event):
        """Handles window resize events."""
        # The QScrollArea handles displaying the fixed-size canvas within the resized window.
        # No need to redraw the pixmap here.
        super().resizeEvent(event) # Call the base class implementation

    def update_canvas(self, preview=False):
        temp_pixmap = QPixmap(self.canvas_pixmap.size())
        temp_pixmap.fill(Qt.white)

        painter = QPainter(temp_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        for item in self.drawing_history:
            pen = QPen(QColor(item['color']), item['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            start = QPoint(item['start_x'], item['start_y'])
            end = QPoint(item['end_x'], item['end_y'])

            if item['type'] == 'draw':
                painter.drawLine(start, end)
            elif item['type'] == 'rectangle':
                painter.drawRect(QRect(start, end))
            elif item['type'] == 'square':
                dx = item['end_x'] - item['start_x']
                dy = item['end_y'] - item['start_y']
                side = min(abs(dx), abs(dy))

                if dx >= 0 and dy >= 0:
                    top_left = QPoint(item['start_x'], item['start_y'])
                elif dx < 0 and dy >= 0:
                    top_left = QPoint(item['start_x'] - side, item['start_y'])
                elif dx >= 0 and dy < 0:
                    top_left = QPoint(item['start_x'], item['start_y'] - side)
                else:  # dx < 0 and dy < 0
                    top_left = QPoint(item['start_x'] - side, item['start_y'] - side)

                rect = QRect(top_left, QSize(side, side))
                painter.drawRect(rect)
            elif item['type'] == 'circle':
                center = QPoint(start.x(),start.y())
                radius = int(math.sqrt(pow(start.x()-end.x(),2)+(pow(start.y()-end.y(),2))))
                painter.drawEllipse(center, radius, radius)

        # Live preview of shape
        if preview and getattr(self, "drawing_shape", False) and hasattr(self, "temp_end_point"):
            pen = QPen(self.brush_color, self.brush_size, Qt.DashLine)
            painter.setPen(pen)
            rect = QRect(self.shape_start_point, self.temp_end_point)

            if self.current_shape == "Rectangle":
                painter.drawRect(rect) # this function auto converts 
            elif self.current_shape == "Square":
                dx = self.temp_end_point.x() - self.shape_start_point.x()
                dy = self.temp_end_point.y() - self.shape_start_point.y()
                side = min(abs(dx), abs(dy))

                if dx >= 0 and dy >= 0:
                    top_left = QPoint(self.shape_start_point.x(), self.shape_start_point.y())
                elif dx < 0 and dy >= 0:
                    top_left = QPoint(self.shape_start_point.x() - side, self.shape_start_point.y())
                elif dx >= 0 and dy < 0:
                    top_left = QPoint(self.shape_start_point.x(), self.shape_start_point.y() - side)
                else:  # dx < 0 and dy < 0
                    top_left = QPoint(self.shape_start_point.x() - side, self.shape_start_point.y() - side)

                rect = QRect(top_left, QSize(side, side))
                painter.drawRect(rect)
            elif self.current_shape == "Circle":
                # find the radius with pitagoras theorem 
                dx = self.temp_end_point.x() - self.shape_start_point.x()
                dy = self.temp_end_point.y() - self.shape_start_point.y()
                radius = int(math.sqrt((dx*dx)+(dy*dy)))
                center = self.shape_start_point
                painter.drawEllipse(center, radius, radius)

        painter.end()
        self.canvas.setPixmap(temp_pixmap)
        self.canvas.update()

    def onDisconnect(self):
        if(self.ipAddress == "127.0.0.1"):
            return
        QMessageBox.warning(self,"Chiusura Applicazione","Connesione con l'host perso")
        time.sleep(1)
        QApplication.quit()

    def listen_server(self):
        while True:
            if not self.is_socket_alive():
                self.socketLost.emit(True)
            try:
                data = ""
                try:
                    data = self.socket.recv(4096).decode('utf-8')
                except Exception as e:
                    pass
                if not data:
                    print("Server disconnected.")
                    break
                messages = data.split(';')
                for message in messages:
                    if message:
                        decoded_message = decode_message(message.strip())
                        if decoded_message:
                            # Append remote drawing to history and update canvas
                            self.drawing_history.append({
                                'type': decoded_message[0],
                                'start_x': decoded_message[1],
                                'start_y': decoded_message[2],
                                'end_x': decoded_message[3],
                                'end_y': decoded_message[4],
                                'color': decoded_message[5],
                                'size': decoded_message[6]
                            }) 
                            if(not self.drawing):
                                self.update_canvas()
                        else:
                            print(f"Error decoding message: {message}")

            except Exception as e:
                print(f"Error receiving data from server: {e}")
                break

    def is_socket_alive(self):
        """Checks if the TCP socket is still alive (portable)."""
        if self.socket is None:
            return False
        try:
            # Try sending a 0-byte message
            self.socket.send(b'')
            return True
        except socket.error as e:
            # Common errors indicating disconnection
            if e.errno in (errno.ECONNRESET, errno.ENOTCONN, errno.EPIPE, errno.EBADF): # EBADF for bad file descriptor
                return False
            # For non-blocking sockets, a "would block" error isn't a disconnection
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK or e.errno == 10035: # Windows WSAEWOULDBLOCK
                return True
            print(f"Socket check failed with unexpected error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during socket liveness check: {e}")
            return False

    def mousePressEvent(self, event: QMouseEvent):
        # canvas_pos = self.canvas.mapFromParent(event.pos()) # this gives relative position and its related to parent
        canvas_pos = self.canvas.mapFromGlobal(event.globalPos()) # this one gives absolute position on the screen

        print("A") 
        # check if the pressed area is inside the canva
        if event.button() == Qt.LeftButton and self.canvas.geometry().contains(event.pos()):
            if self.current_shape == "Freehand":
                self.drawing = True
                self.last_point = canvas_pos
            else:
                self.shape_start_point = canvas_pos
                self.drawing_shape = True

        elif event.button() == Qt.RightButton:
            self.dragging = True
            self.drag_start_pos = event.pos()
            # change the cursor so the user knows that he is dragging and not drawing
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)

        super().mousePressEvent(event)


    def mouseMoveEvent(self, event: QMouseEvent):
        """Handles mouse move events for drawing and dragging."""
        # Get the position relative to the canvas widget
        canvas_pos = self.canvas.mapFromGlobal(event.globalPos())
        if not self.is_socket_alive():
            self.socketLost.emit(True)
        print("B")
        if self.drawing and self.last_point is not None and self.current_shape == "Freehand":
            # Check if the move is within the canvas bounds
            if self.canvas.geometry().contains(event.pos()):
                current_point = canvas_pos # Point relative to canvas absolute coords

                # Add the current line segment to the drawing history
                self.drawing_history.append({
                    'type': 'draw',
                    'start_x': self.last_point.x(),
                    'start_y': self.last_point.y(),
                    'end_x': current_point.x(),
                    'end_y': current_point.y(),
                    'color': self.brush_color.name(), # Store color as hex string
                    'size': self.brush_size
                })


                # Update the canvas to show the newly added line
                self.update_canvas()

                # Encode and send the drawing data to the server (using absolute canvas coordinates)
                message = encode_message(
                    "draw",
                    self.last_point.x(),
                    self.last_point.y(),
                    current_point.x(),
                    current_point.y(),
                    self.brush_color.name(), # Send color as hex string
                    self.brush_size
                )
                try:
                    self.socket.sendall((message).encode('utf-8'))

                except Exception as e:
                    print(f"Error sending data to server: {e}")

                self.last_point = current_point # Update last_point with the current absolute canvas coordinate

        elif getattr(self, "drawing_shape", False):
            self.temp_end_point = canvas_pos
            self.update_canvas(preview=True)  # Pass flag to show preview

        elif self.dragging and self.drag_start_pos is not None:
            # Calculate the movement delta
            delta = event.pos() - self.drag_start_pos

            # Scroll the scroll area based on the drag delta
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_area.horizontalScrollBar().value() - delta.x())
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value() - delta.y())

            # Update the drag start position for the next move event
            self.drag_start_pos = event.pos()

        super().mouseMoveEvent(event) # Call the base class implementation


    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.is_socket_alive():
            self.socketLost.emit(True)
        if event.button() == Qt.LeftButton:
            # se stiamo disegnando un shape e ho lasciato il tasto sinistro -> conferma e mando a tutti
            if self.current_shape != "Freehand" and getattr(self, "drawing_shape", False):
                end_point = self.canvas.mapFromGlobal(event.globalPos())
                self.drawing_shape = False

                start_x, start_y = self.shape_start_point.x(), self.shape_start_point.y()
                end_x, end_y = end_point.x(), end_point.y()

                self.drawing_history.append({
                    'type': self.current_shape.lower(),
                    'start_x': start_x,
                    'start_y': start_y,
                    'end_x': end_x,
                    'end_y': end_y,
                    'color': self.brush_color.name(),
                    'size': self.brush_size
                })


                message = encode_message(
                    self.current_shape.lower(),
                    start_x, start_y, end_x, end_y,
                    self.brush_color.name(), self.brush_size
                )
                try:
                    self.socket.sendall(message.encode('utf-8'))

                except Exception as e:
                    print(f"Error sending shape data: {e}")

                self.update_canvas()

            else:
                self.drawing = False
                self.last_point = None

        elif event.button() == Qt.RightButton:
            self.dragging = False
            self.drag_start_pos = None
            QApplication.restoreOverrideCursor()

        super().mouseReleaseEvent(event) # faccio sapere la classe padre che ho lasciato il tasto sinistro
    
    # definire le funzioni che gestiscono le risposte da tool bar
    def on_color_changed(self, color: QColor):
        self.brush_color = color

    def on_brush_size_changed(self, size: int):
        self.brush_size = size

    def on_shape_changed(self, shape: str):
        self.current_shape = shape
    # viene chiamato quando cerchiamo di chiudere la finestra
    def closeEvent(self, event: QCloseEvent):
            """
            This method is called when the window is about to be closed.
            """
            # Your code to run when the window is closing goes here
            print("Close event received.")

            # You must either accept or ignore the event
            # event.accept() # Allows the window to close
            # event.ignore() # Prevents the window from closing

            if(self.ipAddress == "127.0.0.1"):
            # Example with confirmation:
                # offers different options
                reply = QMessageBox.question(self, 'Save Unsaved File', "Do you want to save before Quitting?",QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,QMessageBox.Cancel)
                # se vuole salvare.
                if reply == QMessageBox.Yes:
                    self.clear_file(self.pathName)
                    stringa_json = json.dumps(self.drawing_history, indent=4, ensure_ascii=False)
                    try:
                        # Apri il file in modalitÃ  scrittura ('w').
                        # Se il file esiste, il suo contenuto viene cancellato prima di scrivere.
                        # Se il file non esiste, viene creato.
                        # Usiamo encoding='utf-8' per gestire correttamente vari caratteri.
                        with open(self.pathName, 'w', encoding='utf-8') as file_oggetto:
                            # Scrivi la stringa JSON nel file
                            file_oggetto.write(stringa_json)

                        print(f"\nStringa JSON salvata con successo in '{self.pathName}'")

                    except Exception as e:
                        print(f"\nErrore durante il salvataggio della stringa JSON nel file: {e}")
                    event.accept() # User confirmed, allow close

                elif reply == QMessageBox.No:
                    event.accept()
                else:
                    event.ignore() # User cancelled, prevent close
            else:
                reply = QMessageBox.question(self,"Exit share mode", 'Do you really want to exit share mode?',QMessageBox.Yes | QMessageBox.Cancel,QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    event.accept() # User confirmed, allow close
                elif reply == QMessageBox.Cancel:
                    event.ignore()
    # delete contents within the file
    def clear_file(self,filepath):
        try:
            # Open the file in write mode ('w').
            # This truncates the file if it exists or creates it if it doesn't.
            # Using 'with' ensures the file is closed automatically.
            with open(filepath, 'w', encoding='utf-8') as f:
                pass # We don't need to write anything, just opening in 'w' clears it

            print(f"File '{filepath}' has been cleared.")
        except Exception as e:
            print(f"Error clearing file '{filepath}': {e}")



class ToolStatusPanel(QWidget):
    # signal che avverte alla classe parente quando qualcosa cambia
    color_changed = pyqtSignal(QColor)
    brush_size_changed = pyqtSignal(int)
    shape_changed = pyqtSignal(str)

    

    def __init__(self,parent_instance, parent=None ):
        super().__init__(parent)
        self.parent_instance = parent_instance
        self.pathName = parent_instance.pathName
        self.fileName = parent_instance.fileName

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout) # Set the main layout for the QWidget
        self.button1 = QPushButton("Salva File", self)
        self.button2 = QPushButton("Stream File", self)
        self.button1.clicked.connect(self.on_button1_clicked)
        # questi 2 bottoni vengono attivati solo se io sono il server.
        if(self.parent_instance.ipAddress != "127.0.0.1"):
            self.button1.setEnabled(False)
            self.button1.setText("Salva File (non disponibile su file di altri)")
            
            self.button2.setEnabled(False)
            self.button2.setText("Stream File (non disponibile su file di altri)")
        self.button2.clicked.connect(self.on_button2_clicked)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)

        # --- Color ---
        color_section_layout = QHBoxLayout() # Use a more descriptive name
        self.color_label = QLabel("Color:")
        # default con colori vicino ai neri idk pk non funzia nel scegliere
        self.current_color = QColor("#0000ff")

        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet(
            f"background-color: {self.current_color.name()}; border: 1px solid black;"
        )
                                        
        self.color_button = QPushButton("Change Color")
        self.color_button.clicked.connect(self.choose_color)

        color_section_layout.addWidget(self.color_label)
        color_section_layout.addWidget(self.color_preview)
        color_section_layout.addWidget(self.color_button)
        self.layout.addLayout(color_section_layout) # Add color section to main layout

        # --- Brush Size ---
        brush_section_layout = QHBoxLayout() # Horizontal layout for brush controls
        self.size_label = QLabel()  # Text will be set by change_brush_size
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.valueChanged.connect(self.change_brush_size)
        
        brush_section_layout.addWidget(self.size_label)
        brush_section_layout.addWidget(self.size_slider)
        self.layout.addLayout(brush_section_layout) # Add brush section to main layout

        # Initialize brush size (this will also set the label text and slider position)
        self.change_brush_size(3) 

        # --- Shape Selection ---
        shape_section_layout = QHBoxLayout() # Horizontal layout for shape controls
        self.shape_label = QLabel("Shape:")
        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["Freehand", "Square", "Rectangle", "Circle"])
        self.shape_selector.currentTextChanged.connect(self.shape_changed.emit)

        shape_section_layout.addWidget(self.shape_label)
        shape_section_layout.addWidget(self.shape_selector)
        self.layout.addLayout(shape_section_layout) # Add shape section to main layout

        # Add a spacer at the bottom to push everything up if more vertical space is available
        # self.layout.addStretch(1) # Optional: uncomment if you want controls to group at the top

    # open a dialog that allows me to change color
    def choose_color(self):
        # Restored initial and parent arguments for better UX
        color = QColorDialog.getColor(initial=self.current_color, parent=self)
        if color.isValid():
            # print("aaa") # Debug print, can be removed
            self.update_color(color)

    def update_color(self, color: QColor):
        self.current_color = color
        self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
        self.color_changed.emit(color)

    def change_brush_size(self, value: int):
        if self.size_slider.value() != value: # Sync slider if value comes from elsewhere
            self.size_slider.setValue(value)
        self.size_label.setText(f"Brush Size: {value}")
        self.brush_size_changed.emit(value)


    # getter per colori, brush e shape che sono usati dal paintclient alla sua inizializzazione.
    def get_color(self):
        return self.current_color

    def get_brush_size(self):
        return self.size_slider.value()

    def get_shape(self):
        return self.shape_selector.currentText()
    

    def on_button1_clicked(self):
        #save button
        self.parent_instance.clear_file(self.pathName)
        stringa_json = json.dumps(self.parent_instance.drawing_history, indent=4, ensure_ascii=False)
        try:
                # Apri il file in modalitÃ  scrittura ('w').
                # Se il file esiste, il suo contenuto viene cancellato prima di scrivere.
                # Se il file non esiste, viene creato.
                # Usiamo encoding='utf-8' per gestire correttamente vari caratteri.
                with open(self.pathName, 'w', encoding='utf-8') as file_oggetto:
                    # Scrivi la stringa JSON nel file
                    file_oggetto.write(stringa_json)

                print(f"\nStringa JSON salvata con successo in '{self.pathName}'")

        except Exception as e:
                    print(f"\nErrore durante il salvataggio della stringa JSON nel file: {e}")
        pass

    # divento il server e apro un thread che runna il server.
    def on_button2_clicked(self):
        if (self.parent_instance.server == None):
            print("Attivato Server")
            self.parent_instance.server = WhiteboardServer(self.parent_instance.drawing_history)
            self.parent_instance.serverThread = threading.Thread(target=self.parent_instance.server.start_server, daemon=True)
            self.parent_instance.serverThread.start()
            time.sleep(1)
            #?
            try:
                print(self.parent_instance.socket)
                self.parent_instance.socket.connect((self.parent_instance.ipAddress, int(self.parent_instance.remotePort)))
            except Exception as e:
                print(f"Error connecting to server at {self.parent_instance.ipAddress}:{self.parent_instance.remotePort}: {e}")
                print("Please make sure the server is running and the host/port are correct.")
                sys.exit(1)

            self.parent_instance.listen_thread = threading.Thread(target=self.parent_instance.listen_server, daemon=True)
            self.parent_instance.listen_thread.start()

    
if __name__ == "__main__":
    # Start the client on the main thread
    app = QApplication(sys.argv)
    window = PaintClient()
    window.show()
    sys.exit(app.exec_())