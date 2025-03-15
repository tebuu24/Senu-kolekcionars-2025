import sys
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)

app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.show()
widget.setFixedHeight(800)
widget.setFixedWidth(1400)
try:
    sys.exit(app.exec())
except:
    print("exiting")
