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
                if user == "administrators" and password == "8aravika":
                    self.gotoAdmin()
                else:
                    self.widget.currentUser = user
                    print("✅ Veiksmīga pieslēgšanās!")
                    self.gotoHome()
            else:
                self.error.setText("❌ Nepareiza parole vai lietotājvārds.")
        else:
            self.error.setText("❌ Lietotājvārds neeksistē.")

        conn.close()

        self.usernamefield.clear()
        self.passwordfield.clear()

    def gotoHome(self):
        self.usernamefield.clear()
        self.passwordfield.clear()
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    def gotoAdmin(self):
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))

    def gotoRegister(self):
        self.usernamefield.clear()
        self.passwordfield.clear()
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

        if len(user) > 13:
            self.error.setText("❌ Lietotājvārds nedrīkst pārsniegt 13 rakstzīmes.")
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

        self.error.setText("✅ Reģistrācija veiksmīga! <br>Lūdzu dodieties uz lapu 'Pieteikties'.")
        self.usernamefield.clear()
        self.passwordfield.clear()
        self.passwordfield_2.clear()

    def gotoLogin(self):
        self.usernamefield.clear()
        self.passwordfield.clear()
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

    def gotoAccount(self):
        account = AccountScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(account)
        self.widget.setCurrentIndex(self.widget.indexOf(account))

# Admin ekrāns
class AdminScreen(QMainWindow):
    def __init__(self, widget):
        super(AdminScreen, self).__init__()
        loadUi("ui/admin.ui", self)
        self.widget = widget
        self.logoutbutton.clicked.connect(self.gotoWelcome)
        self.newsbutton.clicked.connect(self.gotoNews)
        self.usersbutton.clicked.connect(self.gotoUsers)

    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))

    def gotoNews(self):
        news = NewsScreen(self.widget)
        self.widget.addWidget(news)
        self.widget.setCurrentIndex(self.widget.indexOf(news))

    def gotoUsers(self):
        users = UsersScreen(self.widget)
        self.widget.addWidget(users)
        self.widget.setCurrentIndex(self.widget.indexOf(users))

# News ekrāns
class NewsScreen(QMainWindow):
    def __init__(self, widget):
        super(NewsScreen, self).__init__()
        loadUi("ui/news.ui", self)
        self.widget = widget
        self.backbutton.clicked.connect(self.gotoAdmin)

    def gotoAdmin(self):
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))

# Users ekrāns
class UsersScreen(QMainWindow):
    def __init__(self, widget):
        super(UsersScreen, self).__init__()
        loadUi("ui/users.ui", self)
        self.widget = widget
        self.backbutton.clicked.connect(self.gotoAdmin)

    def gotoAdmin(self):
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))

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
