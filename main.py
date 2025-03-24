import sys
import sqlite3
import bcrypt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QDialog

# Izveido lietotāju tabulu, ja tā neeksistē
conn = sqlite3.connect("lietotaji.db")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS lietotaji (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
conn.commit()
conn.close()

# Galvenais ekrāns (sākumlapa, kur izvēlēties pieteikšanos vai reģistrāciju)
class WelcomeScreen(QMainWindow):
    def __init__(self, widget):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.gotologin)
        self.registerbutton.clicked.connect(self.gotocreate)

    # Pāriet uz pieteikšanās ekrānu
    def gotologin(self):
        if not hasattr(self.widget, 'loginScreen'):
            self.widget.loginScreen = LoginScreen(self.widget)
            self.widget.addWidget(self.widget.loginScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.loginScreen))

    # Pāriet uz reģistrācijas ekrānu
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
        self.newbutton.clicked.connect(self.gotoRegister)

    # Funkcija, lai pārbaudītu lietotājvārdu un paroli
    def loginfunction(self):
        user = self.usernamefield.toPlainText().strip()
        password = self.passwordfield.toPlainText().strip()

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

    # Pāriet uz sākumlapu pēc veiksmīgas pieslēgšanās
    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))
    
    # Pāriet uz reģistrācijas lapu, ja nospiež pogu
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

    # Funkcija, lai reģistrētu jaunu lietotāju
    def registerFunction(self):
        user = self.usernamefield.toPlainText().strip()
        password = self.passwordfield.toPlainText().strip()
        confirmPassword = self.passwordfield_2.toPlainText().strip()

        if not user or not password or not confirmPassword:
            self.error.setText("❌ Visi lauki ir obligāti.")
            return

        if password != confirmPassword:
            self.error.setText("❌ Paroles nesakrīt.")
            return
        
        if len(user) > 16:
            self.error.setText("❌ Lietotājvārds nedrīkst pārsniegt 16 rakstzīmes.")
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

    # Pāriet uz pieteikšanās lapu, ja nospiež pogu
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

    # Atgriezties uz WelcomeScreen, ja nospiesta izrakstīšanās poga, currentusername tiek dzēsts
    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))


    # Pāriet uz AccountScreen, ja nospiesta konta poga
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

# Programmas sākšana
app = QApplication(sys.argv)
widget = QStackedWidget()

# Pievieno sākuma ekrānu un saglabā to kā atribūtu
widget.welcomeScreen = WelcomeScreen(widget)
widget.addWidget(widget.welcomeScreen)

widget.setFixedHeight(850)
widget.setFixedWidth(521)
widget.show()

# Palaist aplikāciju
try:
    sys.exit(app.exec_())
except Exception as e:
    print(f"Exiting: {e}")
