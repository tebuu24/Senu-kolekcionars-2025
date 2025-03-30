import sys
import sqlite3
import bcrypt
import time
import requests
import re
import os
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QFileDialog, QMessageBox, QProgressBar, QLabel, QLineEdit, QMessageBox, QDialog, QCompleter
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


# Galvenais ekrāns
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
        self.passwordfield.setEchoMode(QLineEdit.Password)


    def loginfunction(self):
        user = self.usernamefield.text().strip()
        password = self.passwordfield.text().strip()

        if not user or not password:
            self.error.setText("❌ Lietotājvārds un parole nedrīkst būt tukši.")
            return

        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()
        cur.execute("SELECT parole FROM lietotaji WHERE lietotajvards = ?", (user,))
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
        self.passwordfield.setEchoMode(QLineEdit.Password)
        self.passwordfield_2.setEchoMode(QLineEdit.Password)

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

        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()
        cur.execute("SELECT lietotajvards FROM lietotaji WHERE lietotajvards = ?", (user,))
        if cur.fetchone():
            self.error.setText("❌ Lietotājvārds jau eksistē.")
            conn.close()
            return

        cur.execute("INSERT INTO lietotaji (lietotajvards, parole) VALUES (?, ?)", (user, hashed_password))
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
        self.usernamelabel.setText(currentUser)
        self.laikapstakli.setText("Meklē laikapstākļus...")
        
        self.logoutbutton.clicked.connect(self.gotoWelcome)
        self.accountbutton.clicked.connect(self.gotoAccount)
        self.newbutton.clicked.connect(self.gotoNewUpload)
        self.collectionbutton.clicked.connect(self.gotoCollection)

        self.get_weather()

    def get_weather(self):
        try:
            api_key = "d912d90fac064f76bfb140614253003"
            city = "Riga"
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"

            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                current_weather = data['current']
                temperature = current_weather['temp_c']
                humidity = current_weather['humidity']
                icon_url = "http:" + current_weather['condition']['icon']
                
                self.laikapstakli.setText(f"{temperature}°C, mitrums: {humidity}%")
                image = QImage()
                image.loadFromData(requests.get(icon_url).content)
                self.weathericon.setPixmap(QPixmap(image))
            else:
                self.laikapstakli.setText("❌ Nav laikapstākļu datu.")
        except Exception as e:
            self.laikapstakli.setText("❌ Kļūda meklējot laikapstākļu datus.")
            print(f"Laikapstākļu api kļūda: {e}")


    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))

    def gotoAccount(self):
        account = AccountScreen(self.widget, self.usernamelabel.text())
        self.widget.addWidget(account)
        self.widget.setCurrentIndex(self.widget.indexOf(account))

    def gotoNewUpload(self):
        newupload = NewUploadScreen(self.widget)
        self.widget.addWidget(newupload)
        self.widget.setCurrentIndex(self.widget.indexOf(newupload))

    def gotoCollection(self):
        collection = CollectionScreen(self.widget)
        self.widget.addWidget(collection)
        self.widget.setCurrentIndex(self.widget.indexOf(collection))


# Konta ekrāns
class AccountScreen(QMainWindow):
    def __init__(self, widget, currentUser):
        super(AccountScreen, self).__init__()
        loadUi("ui/account.ui", self)
        self.widget = widget
        self.currentUser = currentUser
        self.changedatabutton.clicked.connect(self.gotoData)
        self.usernamelabel.setText(currentUser)
        self.homebutton.clicked.connect(self.gotoHome)
        self.deleteaccbutton.clicked.connect(self.showDeleteConfirmation)

    def gotoData(self):
        data = DataScreen(self.widget)
        self.widget.addWidget(data)
        self.widget.setCurrentIndex(self.widget.indexOf(data))
    
    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

        
    # Konta dzēšanai ir apstiprinājums
    def showDeleteConfirmation(self):
        self.dialog = QDialog(self)
        loadUi('ui/confirm.ui', self.dialog)
        
        self.dialog.yesbutton.clicked.connect(self.deleteAccount)
        self.dialog.nobutton.clicked.connect(self.dialog.reject)
        
        self.dialog.exec_()

    def deleteAccount(self):
        try:
            connection = sqlite3.connect("senu_kolekcionars.db")
            cursor = connection.cursor()

            cursor.execute("DELETE FROM lietotaji WHERE lietotajvards=?", (self.currentUser,))
            connection.commit()

            QMessageBox.information(self, '✅', 'Konts tika veiksmīgi dzēsts.')

            self.gotoWelcome()

        except Exception as e:
            QMessageBox.critical(self, '❌', f"Kļūda dzēšot kontu: {e}")

        finally:
            connection.close()
            self.dialog.accept()

    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))



# Labot konta datus, jauns lietotājvārds vai parole (vai abi) 
class DataScreen(QMainWindow):
    def __init__(self, widget):
        super(DataScreen, self).__init__()
        loadUi("ui/accountchangedata.ui", self)
        self.widget = widget
        self.current_username = self.widget.currentUser
        self.currentpasswordfield.setEchoMode(QLineEdit.Password)
        self.newpasswordfield.setEchoMode(QLineEdit.Password)
        self.newpasswordfield_2.setEchoMode(QLineEdit.Password)

        self.homebutton.clicked.connect(self.gotoHome)
        self.cancelbutton.clicked.connect(self.gotoAccount)
        self.changedatabutton.clicked.connect(self.changeData)

        self.usernamefield.setText(self.current_username)

    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    def gotoAccount(self):
        account = AccountScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(account)
        self.widget.setCurrentIndex(self.widget.indexOf(account))

    def changeData(self):
        new_username = self.usernamefield.text().strip()
        current_password = self.currentpasswordfield.text().strip()
        new_password = self.newpasswordfield.text().strip()
        confirm_password = self.newpasswordfield_2.text().strip()

        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT parole FROM lietotaji WHERE lietotajvards = ?", (self.current_username,))
        result = cur.fetchone()

        if not result:
            self.error.setText("❌ Lietotājs netika atrasts.")
            conn.close()
            return

        stored_password = result[0]
        if not bcrypt.checkpw(current_password.encode(), stored_password.encode()):
            self.error.setText("❌ Nepareiza pašreizējā parole.")
            conn.close()
            return

        # Ja ir jauns lietotājvards
        if new_username != self.current_username:
            if not re.match("^[a-zA-Z0-9_]+$", new_username):
                self.error.setText("❌ Lietotājvārds var saturēt tikai burtus, ciparus un '_'.")
                conn.close()
                return
            if len(new_username) > 13:
                self.error.setText("❌ Lietotājvārds nedrīkst pārsniegt 13 rakstzīmes.")
                conn.close()
                return
            cur.execute("SELECT lietotajvards FROM lietotaji WHERE lietotajvards = ?", (new_username,))
            if cur.fetchone():
                self.error.setText("❌ Lietotājvārds jau eksistē.")
                conn.close()
                return

        # Ja ir jauna parole
        if new_password or confirm_password:
            if new_password != confirm_password:
                self.error.setText("❌ Jaunās paroles nesakrīt.")
                conn.close()
                return
            if new_password == current_password:
                self.error.setText("❌ Jaunā parole nevar būt tāda pati kā vecā parole.")
                conn.close()
                return
            hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        else:
            hashed_new_password = stored_password

        # Dati uz datubāzi
        cur.execute("UPDATE lietotaji SET lietotajvards = ?, parole = ? WHERE lietotajvards = ?",
                    (new_username, hashed_new_password, self.current_username))
        conn.commit()
        conn.close()

        self.widget.currentUser = new_username
        self.error.setText("✅ Dati veiksmīgi atjaunināti!")
        self.currentpasswordfield.clear()
        self.newpasswordfield.clear()
        self.newpasswordfield_2.clear()


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

# Lietotāju pāŗvaldības ekrāns
class UsersScreen(QMainWindow):
    def __init__(self, widget):
        super(UsersScreen, self).__init__()
        loadUi("ui/users.ui", self)
        self.widget = widget
        self.backbutton.clicked.connect(self.gotoAdmin)
        self.loadUsers()

    def gotoAdmin(self):
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))

    def loadUsers(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()
        cur.execute("SELECT id, lietotajvards FROM lietotaji")
        users = cur.fetchall()
        conn.close()

        self.userstable.setRowCount(len(users))
        self.userstable.setColumnCount(2)
        self.userstable.setHorizontalHeaderLabels(["ID", "Lietotājvārds"])

# Lietotāja kolekcijas ekrāns
class CollectionScreen(QMainWindow):
    def __init__(self, widget):
        super(CollectionScreen, self).__init__()
        loadUi("ui/collection.ui", self)
        self.widget = widget
        self.homebutton.clicked.connect(self.gotoHome)

    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))


# Jaunas sēnes ekrāns
class NewUploadScreen(QMainWindow):
    def __init__(self, widget):
        super(NewUploadScreen, self).__init__(widget)
        loadUi("ui/newupload.ui", self)
        self.widget = widget
        self.homebutton.clicked.connect(self.gotoHome)
        self.uploadbutton.clicked.connect(self.upload) 
        self.showNormal()
        print(f"Window geometry: {self.geometry()}")


    def upload(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Izvēlies attēlu", "", "Images (*.png *.jpg *.jpeg)")
            
            if not file_path:
                self.error.setText("❌ Lūdzu izvēlieties failu.")
                return
            
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.error.setText("❌ Failam jābūt .jpg, .jpeg vai .png formātā.")
                return
            self.gotoAdd

        except Exception as e:
            self.error.setText(f"❌ Kļūda faila apstrādē: {str(e)}")
            print(f"Error during file upload: {e}")


    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    def gotoAdd(self):
        add = AddScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(add)
        self.widget.setCurrentIndex(self.widget.indexOf(add))



class AddScreen(QMainWindow):
    def __init__(self, widget, file_path):
        super(AddScreen, self).__init__(widget)
        loadUi("ui/newwait.ui", self)

        self.file_path = file_path
        self.homebutton.clicked.connect(self.gotoHome)
        self.cancelbutton.clicked.connect(self.gotoNewUpload)
    

    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))
    def gotoNewUpload(self):
        newupload = NewUploadScreen(self.widget)
        self.widget.addWidget(newupload)
        self.widget.setCurrentIndex(self.widget.indexOf(newupload))



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