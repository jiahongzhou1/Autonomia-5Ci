from PyQt5.QtWidgets import QApplication, QWidget , QPushButton

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window. 
# (like a blank screen, we can have more by instantiating more Q components 
# [we can also use QpushButton to give us a windows with only a button] , QWidgets have no parents Componets and so they Are hidden by default)
window = QPushButton("Im a fucking button") #This may be cool but not very usefull (some components are not designed to contain other components so its pretty ussleess this)
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

window2 = QWidget()
window2.show() 

# Start the event loop.
app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.

