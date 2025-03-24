import sys
import sqlite3
import bcrypt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
import datubaze  # Import the new database file

# Galvenais ekrāns (sākumlapa, kur izvēlēties pieteikšanos vai reģistrāciju)
class WelcomeScreen(QMainWindow):
    def __init__(self, widget):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.gotologin)
        self.registerbutton.clicked.connect(self.gotocreate)

    def gotologin(self):
        if not hasattr(self.widget, 'loginScreen'):
            self.widget.loginScreen = LoginScreen(self.widget)
            self.widget.addWidget(self.widget.loginScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.loginScreen))

    def gotocreate(self):
        if not hasattr(self.widget, 'registerScreen'):
            self.widget.registerScreen = RegisterScreen(self.widget)
            self.widget.addWidget(self.widget.registerScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.registerScreen))

# Pieteikšanās ekrāns
class LoginScreen(QMainWindow):
    def __init__(self, widget):
        super(LoginScreen, self).__init__()
        loadUi("ui/login.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.loginfunction)
        self.registerbutton_2.clicked.connect(self.gotoRegister)

    def loginfunction(self):
        user = self.usernamefield.text().strip()
        password = self.passwordfield.text().strip()

        if not user or not password:
            self.error.setText("❌ Lietotājvārds un parole nedrīkst būt tukši.")
            return

        conn = sqlite3.connect("lietotaji.db")
        cur = conn.cursor()
        cur.execute("SELECT password FROM lietotaji WHERE username = ?", (user,))
        result = cur.fetchone()

        if result:
            stored_password = result[0]
            if bcrypt.checkpw(password.encode(), stored_password.encode()):
                self.widget.currentUser = user
                print("✅ Veiksmīga pieslēgšanās!")
                self.gotoHome()
            else:
                self.error.setText("❌ Nepareiza parole vai lietotājvārds.")
        else:
            self.error.setText("❌ Lietotājvārds neeksistē.")

        conn.close()

    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    def gotoRegister(self):
        if not hasattr(self.widget, 'registerScreen'):
            self.widget.registerScreen = RegisterScreen(self.widget)
            self.widget.addWidget(self.widget.registerScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.registerScreen))

# Reģistrācijas ekrāns
class RegisterScreen(QMainWindow):
    def __init__(self, widget):
        super(RegisterScreen, self).__init__()
        loadUi("ui/register.ui", self)
        self.widget = widget
        self.registerbutton.clicked.connect(self.registerFunction)
        self.loginbutton_2.clicked.connect(self.gotoLogin)

    def registerFunction(self):
        user = self.usernamefield.text().strip()
        password = self.passwordfield.text().strip()
        confirmPassword = self.passwordfield_2.text().strip()

        if not user or not password or not confirmPassword:
            self.error.setText("❌ Visi lauki ir obligāti.")
            return

        if len(user) > 16:
            self.error.setText("❌ Lietotājvārds nedrīkst pārsniegt 16 rakstzīmes.")
            return

        if password != confirmPassword:
            self.error.setText("❌ Paroles nesakrīt.")
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        conn = sqlite3.connect("lietotaji.db")
        cur = conn.cursor()
        cur.execute("SELECT username FROM lietotaji WHERE username = ?", (user,))
        if cur.fetchone():
            self.error.setText("❌ Lietotājvārds jau eksistē.")
            conn.close()
            return

        cur.execute("INSERT INTO lietotaji (username, password) VALUES (?, ?)", (user, hashed_password))
        conn.commit()
        conn.close()

        self.error.setText("✅ Reģistrācija veiksmīga!")

    def gotoLogin(self):
        if not hasattr(self.widget, 'loginScreen'):
            self.widget.loginScreen = LoginScreen(self.widget)
            self.widget.addWidget(self.widget.loginScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.loginScreen))

# Sākumlapa pēc pieslēgšanās
class HomeScreen(QMainWindow):
    def __init__(self, widget, currentUser):
        super(HomeScreen, self).__init__()
        loadUi("ui/home.ui", self)
        self.widget = widget
        self.logoutbutton.clicked.connect(self.gotoWelcome)
        self.accountbutton.clicked.connect(self.gotoAccount)
        self.usernamelabel.setText(currentUser)

    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))

    def gotoAccount(self):
        account = AccountScreen(self.widget, self.usernamelabel.text())
        self.widget.addWidget(account)
        self.widget.setCurrentIndex(self.widget.indexOf(account))

# Konta ekrāns
class AccountScreen(QMainWindow):
    def __init__(self, widget, currentUser):
        super(AccountScreen, self).__init__()
        loadUi("ui/account.ui", self)
        self.widget = widget
        self.changedatabutton.clicked.connect(self.gotoData)
        self.usernamelabel.setText(currentUser)

    def gotoData(self):
        data = DataScreen(self.widget)
        self.widget.addWidget(data)
        self.widget.setCurrentIndex(self.widget.indexOf(data))

# Labot konta datus
class DataScreen(QMainWindow):
    def __init__(self, widget):
        super(DataScreen, self).__init__()
        loadUi("ui/accountchangedata.ui", self)
        self.widget = widget

# Programmas sākšana
app = QApplication(sys.argv)
widget = QStackedWidget()

widget.currentUser = None

widget.welcomeScreen = WelcomeScreen(widget)
widget.addWidget(widget.welcomeScreen)

widget.setFixedHeight(850)
widget.setFixedWidth(521)
widget.show()

try:
    sys.exit(app.exec_())
except Exception as e:
    print(f"Exiting: {e}")
