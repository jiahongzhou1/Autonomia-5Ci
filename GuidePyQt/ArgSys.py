import sys
from PyQt5.QtWidgets import QApplication, QLabel
import argparse

# Create the parser

parser = argparse.ArgumentParser(description="My PyQt5 App")

'''
Gli argomenti che mettiamo per QApplication sono flags in piu che possiamo usare quando facciamo partire il file per darli dei input da esterno
ad esempio passargli un testo con il flag --message python -u  "c:\Users\lol30\Documents\VSC\Autonomia-5Ci\PyQtGuide.py" --message "COCK"
'''

parser.add_argument('--message', type=str, help='Text to display')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')

# Parse args from sys.argv
args = parser.parse_args()

# Create app
app = QApplication(sys.argv)
label = QLabel(args.message or "Hello from PyQt5!")
label.show()

if args.debug:
    print("Debug mode is ON")

sys.exit(app.exec_())
