import sys
import sqlite3
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QDialog

#sākums/welcome screen
class WelcomeScreen(QMainWindow):
    def __init__(self, widget):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.gotologin)
        self.registerbutton.clicked.connect(self.gotocreate)

    def gotologin(self):
        login = LoginScreen(self.widget)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
    def gotocreate(self):
        createAccount = RegisterScreen(self.widget)
        self.widget.addWidget(createAccount)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

#Login screen
class LoginScreen(QMainWindow):
    
    def __init__(self, widget):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.loginfunction)


    def loginfunction(self):
        user = self.usernamefield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Nedrīkst būt tukši lauki.")
        else:
            conn = sqlite3.connect("lietotaji.db")
            cur = conn.cursor()
            query = "SELECT password FROM lietotaji WHERE username = ?"
            cur.execute(query, (user,))
            result_pass = cur.fetchone()[0]
            if result_pass == password:
                print("veiksmīga pieslēgšanās")
            else:
                self.error.setText("Nav pareiza parole vai lietotājvārds")
                
class RegisterScreen(QMainWindow):
    def __init__(self, widget):
        super(RegisterScreen, self).__init__()
        loadUi("register.ui", self)
        self.widget = widget

    def registerFunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmPassword = self.confirmpasswordfield.text()

        if len(user) == 0 or len(password) == 0 or len(confirmPassword) == 0:
            self.error.setText("Nedrīkst būt tukši lauki.")
            return

        if password != confirmPassword:
            self.error.setText("Paroles nesakrīt.")
            return

        conn = sqlite3.connect("lietotaji.db")
        cur = conn.cursor()
        cur.execute("SELECT username FROM login_info WHERE username = ?", (user,))
        if cur.fetchone():
            self.error.setText("Lietotājvārds jau eksistē.")
            conn.close()
            return

        cur.execute("INSERT INTO lietotaji (username, password) VALUES (?, ?)", (user, password))
        conn.commit()
        conn.close()
        self.error.setText("Reģistrācija veiksmīga!")

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