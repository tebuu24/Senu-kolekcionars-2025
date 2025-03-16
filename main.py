import sys
import sqlite3
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton
from PyQt5.QtWidgets import QDialog

#sākums/welcome screen
class WelcomeScreen(QMainWindow):
    def __init__(self, widget):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.widget = widget
        self.login.clicked.connect(self.gotologin)

    def gotologin(self):
        login = LoginScreen(self.widget)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

#Login screen
class LoginScreen(QDialog):
    def __init__(self, widget):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)
        self.widget = widget

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Nedrīkst būt tukši lauki.")
        else:
            conn = sqlite3.connect("lietotaji.db")
            cur = conn.cursor()
            query = "SELECT password FROM login_info WHERE username = ?"
            cur.execute(query, (user,))
            result_pass = cur.fetchone()[0]
            if result_pass == password:
                print("veiksmīga pieslēgšanās")
            else:
                self.error.setText("Nav pareiza parole vai lietotājvārds")

# konfigurācija/kas ir kas
app = QApplication(sys.argv)
widget = QStackedWidget()
welcome = WelcomeScreen(widget)
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1400)
widget.show()

# atver aplikāciju
try:
    sys.exit(app.exec_())  # Use exec_() for PyQt5
except Exception as e:
    print(f"exiting: {e}")
