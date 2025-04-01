# bibliotēkas
import sys
import sqlite3
import bcrypt
import requests
import re
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QFileDialog, QMessageBox, QLabel, QLineEdit, QMessageBox, QDialog, QTableWidgetItem, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtGui import QPixmap, QImage, QStandardItemModel, QStandardItem, QPixmap, QImage
from PyQt5.QtCore import Qt
from datetime import datetime

# galvenais ekrāns, kurā lietotājs var izveidot jaunu kontu vai pieteikties
class WelcomeScreen(QMainWindow):
    def __init__(self, widget):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.gotologin)
        self.registerbutton.clicked.connect(self.gotocreate)

    # pāreja uz pieteikšanās ekrānu
    def gotologin(self):
        if not hasattr(self.widget, 'loginScreen'):
            self.widget.loginScreen = LoginScreen(self.widget)
            self.widget.addWidget(self.widget.loginScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.loginScreen))

    # pāreja uz reģistrācijas ekrānu
    def gotocreate(self):
        if not hasattr(self.widget, 'registerScreen'):
            self.widget.registerScreen = RegisterScreen(self.widget)
            self.widget.addWidget(self.widget.registerScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.registerScreen))

# pieteikšanās ekrāns ar paroles validāciju
class LoginScreen(QMainWindow):
    def __init__(self, widget):
        super(LoginScreen, self).__init__()
        loadUi("ui/login.ui", self)
        self.widget = widget
        self.loginbutton.clicked.connect(self.loginfunction)
        self.registerbutton_2.clicked.connect(self.gotoRegister)
        self.passwordfield.setEchoMode(QLineEdit.Password)

    # pārbauda ievadīto lietotājvārdu un paroli
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

        # pārbauda, vai lietotājs eksistē un parole ir pareiza
        if result:
            stored_password = result[0]
            if bcrypt.checkpw(password.encode(), stored_password.encode()):
                self.widget.currentUser = user
                print("✅ Veiksmīga pieslēgšanās!")

                if user == "administrators":
                    self.gotoAdmin()
                else:
                    self.gotoHome()
            else:
                self.error.setText("❌ Nepareiza parole vai lietotājvārds.")
        else:
            self.error.setText("❌ Lietotājvārds neeksistē.")

        conn.close()
        # notīra ievades laukus pēc pieslēgšanās mēģinājuma
        self.usernamefield.clear()
        self.passwordfield.clear()

    # novirza uz lietotāja sākumlapu
    def gotoHome(self):
        self.usernamefield.clear()
        self.passwordfield.clear()
        self.error.setText("")
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    # novirza uz administratora paneli
    def gotoAdmin(self):
        self.error.setText("")
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))

    # pāreja uz reģistrācijas ekrānu
    def gotoRegister(self):
        self.error.setText("")
        self.usernamefield.clear()
        self.passwordfield.clear()
        if not hasattr(self.widget, 'registerScreen'):
            self.widget.registerScreen = RegisterScreen(self.widget)
            self.widget.addWidget(self.widget.registerScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.registerScreen))

# reģistrācijas ekrāns ar lietotājvārda un paroles validāciju
class RegisterScreen(QMainWindow):
    def __init__(self, widget):
        super(RegisterScreen, self).__init__()
        loadUi("ui/register.ui", self)
        self.widget = widget
        self.registerbutton.clicked.connect(self.registerFunction)
        self.loginbutton_2.clicked.connect(self.gotoLogin)
        self.passwordfield.setEchoMode(QLineEdit.Password)
        self.passwordfield_2.setEchoMode(QLineEdit.Password)

    # reģistrē jaunu lietotāju
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

        self.error.setText("✅ Reģistrācija veiksmīga! <br>Lūdzu dodieties pieslēgšanos.")
        self.usernamefield.clear()
        self.passwordfield.clear()
        self.passwordfield_2.clear()

    # pāreja uz pieteikšanās ekrānu
    def gotoLogin(self):
        self.error.setText("")
        self.usernamefield.clear()
        self.passwordfield.clear()
        if not hasattr(self.widget, 'loginScreen'):
            self.widget.loginScreen = LoginScreen(self.widget)
            self.widget.addWidget(self.widget.loginScreen)
        self.widget.setCurrentIndex(self.widget.indexOf(self.widget.loginScreen))

# sākumlapas ekrāna klase pēc pieslēgšanās
class HomeScreen(QMainWindow):
    # inicializē sākumlapas ekrānu un ielādē UI
    def __init__(self, widget, currentUser):
        super(HomeScreen, self).__init__()
        loadUi("ui/home.ui", self)
        self.widget = widget
        self.usernamelabel.setText(currentUser)
        self.laikapstakli.setText("Meklē laikapstākļus...")

        # pogu piesaiste dažādām funkcijām
        self.logoutbutton.clicked.connect(self.gotoWelcome)
        self.accountbutton.clicked.connect(self.gotoAccount)
        self.newbutton.clicked.connect(self.gotoNewUpload)
        self.collectionbutton.clicked.connect(self.gotoCollection)

        # ielādē laikapstākļus un jaunumus
        self.get_weather()
        self.load_home_news()

    # iegūst un attēlo pašreizējos laikapstākļus no API
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
            print(f"Laikapstākļu API kļūda: {e}")

    # ielādē un attēlo jaunumus no datubāzes
    def load_home_news(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT saturs, laiks FROM pazinojumi ORDER BY laiks DESC")
        news_entries = cur.fetchall()
        self.model = QStandardItemModel()
        self.news.setModel(self.model)
        conn.close()

        self.model.clear()
        for entry in news_entries:
            news_item = QStandardItem(f"{entry[1]}: {entry[0]}")
            self.model.appendRow(news_item)

    # pāriet uz sākumlapu (logout)
    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))

    # pāriet uz konta ekrānu
    def gotoAccount(self):
        account = AccountScreen(self.widget, self.usernamelabel.text())
        self.widget.addWidget(account)
        self.widget.setCurrentIndex(self.widget.indexOf(account))

    # pāriet uz jaunu augšupielādi
    def gotoNewUpload(self):
        newupload = NewUploadScreen(self.widget)
        self.widget.addWidget(newupload)
        self.widget.setCurrentIndex(self.widget.indexOf(newupload))

    # pāriet uz kolekcijas ekrānu
    def gotoCollection(self):
        collection = CollectionScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(collection)
        self.widget.setCurrentIndex(self.widget.indexOf(collection))


# konta ekrāna klase
class AccountScreen(QMainWindow):
    # inicializē konta ekrānu un ielādē UI
    def __init__(self, widget, currentUser):
        super(AccountScreen, self).__init__()
        loadUi("ui/account.ui", self)
        self.widget = widget
        self.currentUser = currentUser

        # pogu piesaiste dažādām funkcijām
        self.changedatabutton.clicked.connect(self.gotoData)
        self.usernamelabel.setText(currentUser)
        self.homebutton.clicked.connect(self.gotoHome)
        self.deleteaccbutton.clicked.connect(self.showDeleteConfirmation)

        # ielādē lietotāja kolekcijas datu summu
        self.loadSumData()

    # pāriet uz datu pārvaldības ekrānu
    def gotoData(self):
        data = DataScreen(self.widget)
        self.widget.addWidget(data)
        self.widget.setCurrentIndex(self.widget.indexOf(data))

    # pāriet uz sākumlapu
    def gotoHome(self):
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    # ielādē un attēlo lietotāja kolekcijas kopējo summu
    def loadSumData(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT SUM(skaits) FROM kolekcijas WHERE lietotajs_id = ?", (self.currentUser,))
        total_count = cur.fetchone()[0]

        conn.close()

        if total_count is None:
            total_count = 0

        self.datasum.setText(str(total_count))

    # parāda apstiprinājuma logu pirms konta dzēšanas
    def showDeleteConfirmation(self):
        self.dialog = QDialog(self)
        loadUi('ui/confirm.ui', self.dialog)

        self.dialog.yesbutton.clicked.connect(self.deleteAccount)
        self.dialog.nobutton.clicked.connect(self.dialog.reject)

        self.dialog.exec_()

    # dzēš lietotāja kontu no datubāzes
    def deleteAccount(self):
        try:
            connection = sqlite3.connect("senu_kolekcionars.db")
            cursor = connection.cursor()

            cursor.execute("DELETE FROM lietotaji WHERE lietotajvards=?", (self.currentUser,))
            connection.commit()

            msg = QMessageBox(self)
            msg.setWindowTitle("Konts ir dzēsts")
            msg.setText("✅ Konts tika veiksmīgi dzēsts.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    background-color: white;
                    color: black;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid gray;
                     padding: 5px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            msg.exec_()

            self.gotoWelcome()
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Kļūda")
            msg.setText(f"❌ Kļūda dzēšot kontu: {e}")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    background-color: white;
                    color: black;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid gray;
                     padding: 5px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            msg.exec_()
        finally:
            connection.close()
            self.dialog.accept()

    # pāriet uz sākumlapu pēc konta dzēšanas
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

    # dodas uz sākumlapu pēc izmaiņām vai atcelšanas
    def gotoHome(self):
        self.error.setText("")
        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    # dodas atpakaļ uz konta ekrānu
    def gotoAccount(self):
        self.error.setText("")
        account = AccountScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(account)
        self.widget.setCurrentIndex(self.widget.indexOf(account))

    # maina lietotājvārdu un/vai paroli, ja ievades dati ir korekti
    def changeData(self):
        new_username = self.usernamefield.text().strip()
        current_password = self.currentpasswordfield.text().strip()
        new_password = self.newpasswordfield.text().strip()
        confirm_password = self.newpasswordfield_2.text().strip()

        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT parole FROM lietotaji WHERE lietotajvards = ?", (self.current_username,))
        result = cur.fetchone()

        # pārbauda, vai ievadītā parole sakrīt ar esošo paroli
        if not result:
            self.error.setText("❌ Lietotājs netika atrasts.")
            conn.close()
            return

        # pārbauda, vai jaunais lietotājvārds atbilst prasībām un nav jau izmantots
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

        # pārbauda, vai jaunā parole ir korekta un atšķiras no iepriekšējās
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
            self.error.setText("")
            hashed_new_password = stored_password

        # saglabā izmaiņas datubāzē un atjaunina lietotāja informāciju
        cur.execute("UPDATE lietotaji SET lietotajvards = ?, parole = ? WHERE lietotajvards = ?",
                    (new_username, hashed_new_password, self.current_username))
        conn.commit()
        conn.close()

        self.widget.currentUser = new_username
        self.error.setText("✅ Dati veiksmīgi atjaunināti!")
        self.currentpasswordfield.clear()
        self.newpasswordfield.clear()
        self.newpasswordfield_2.clear()


# ekrāns administratoram
class AdminScreen(QMainWindow):
    def __init__(self, widget):
        super(AdminScreen, self).__init__()
        loadUi("ui/admin.ui", self)
        self.widget = widget
        self.logoutbutton.clicked.connect(self.gotoWelcome)
        self.newsbutton.clicked.connect(self.gotoNews)
        self.usersbutton.clicked.connect(self.gotoUsers)

        self.model = QStandardItemModel()
        self.news.setModel(self.model)

        self.load_admin_news()

    # dodas uz sākuma ekrānu, izrakstoties no sistēmas
    def gotoWelcome(self):
        self.widget.currentUser = None
        welcome = WelcomeScreen(self.widget)
        self.widget.addWidget(welcome)
        self.widget.setCurrentIndex(self.widget.indexOf(welcome))

    # pāriet uz ziņu pārvaldības ekrānu
    def gotoNews(self):
        news = NewsScreen(self.widget)
        self.widget.addWidget(news)
        self.widget.setCurrentIndex(self.widget.indexOf(news))

    # pāriet uz lietotāju pārvaldības ekrānu
    def gotoUsers(self):
        users = UsersScreen(self.widget)
        self.widget.addWidget(users)
        self.widget.setCurrentIndex(self.widget.indexOf(users))

    # ielādē jaunākās ziņas no datubāzes
    def load_admin_news(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()


        cur.execute("SELECT saturs, laiks FROM pazinojumi ORDER BY laiks DESC")
        news_entries = cur.fetchall()

        conn.close()
        self.model.clear()

        for entry in news_entries:
            news_item = QStandardItem(f"{entry[1]}: {entry[0]}")
            self.model.appendRow(news_item)


# ekrāns ziņu pārvaldībai
class NewsScreen(QMainWindow):
    def __init__(self, widget):
        super(NewsScreen, self).__init__()
        loadUi("ui/news.ui", self)
        self.widget = widget

        self.model = QStandardItemModel()
        self.news.setModel(self.model)

        self.publishbutton.clicked.connect(self.publish_news)
        self.backbutton.clicked.connect(self.gotoAdmin)
        self.deletebutton.clicked.connect(self.delete_last_news)

        self.load_news()

    # dodas atpakaļ uz administratora ekrānu
    def gotoAdmin(self):
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))

    # publicē jaunu ziņu, ja teksts nav tukšs
    def publish_news(self):
        news_text = self.newsfield.toPlainText().strip()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if news_text:
            conn = sqlite3.connect("senu_kolekcionars.db")
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pazinojumi (saturs, laiks)
                VALUES (?, ?)
            """, (news_text, current_time))

            conn.commit()
            conn.close()

            self.newsfield.clear()

            msg = QMessageBox(self)
            msg.setWindowTitle("Ziņa publicēta")
            msg.setText("Ziņa veiksmīgi publicēta!")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    background-color: white;
                    color: black;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid gray;
                     padding: 5px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            msg.exec_()


            self.load_news()

    # ielādē visas ziņas un attēlo tās sarakstā
    def load_news(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT saturs, laiks FROM pazinojumi ORDER BY laiks DESC")
        news_entries = cur.fetchall()

        conn.close()
        self.model.clear()

        for entry in news_entries:
            news_item = QStandardItem(f"{entry[1]}: {entry[0]}")
            self.model.appendRow(news_item)
    
    # izdzēš pēdējo publicēto ziņu no datubāzes
    def delete_last_news(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT id FROM pazinojumi ORDER BY laiks DESC LIMIT 1")
        last_news = cur.fetchone()

        if last_news:
            last_news_id = last_news[0]

            cur.execute("DELETE FROM pazinojumi WHERE id = ?", (last_news_id,))
            conn.commit()
            conn.close()

            msg = QMessageBox(self)
            msg.setWindowTitle("Ziņa dzēsta")
            msg.setText("Pēdējā ziņa veiksmīgi dzēsta!")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    background-color: white;
                    color: black;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid gray;
                     padding: 5px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            msg.exec_()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Nav ziņu")
            msg.setText("Nav nevienas ziņas, ko dzēst!")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    background-color: white;
                    color: black;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid gray;
                     padding: 5px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            msg.exec_()
            
            conn.close()

        self.load_news()


# Lietotāju pārvaldības ekrāns
class UsersScreen(QMainWindow):
    def __init__(self, widget):
        super(UsersScreen, self).__init__()
        loadUi("ui/users.ui", self)
        self.widget = widget
        self.backbutton.clicked.connect(self.gotoAdmin)
        self.loadUsers()
        self.filter.currentIndexChanged.connect(self.sortUsers)

        self.deletebutton.clicked.connect(self.deleteUser)
        self.newsbutton.clicked.connect(self.send_news)

    # dodas atpakaļ uz administratora ekrānu
    def gotoAdmin(self):
        admin = AdminScreen(self.widget)
        self.widget.addWidget(admin)
        self.widget.setCurrentIndex(self.widget.indexOf(admin))
    
    # ielādē un sakārto lietotāju sarakstu pēc izvēlētā kritērija
    def loadUsers(self, order_by="kolekcijas.skaits DESC"):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        query = f"""
            SELECT lietotaji.id, lietotaji.lietotajvards, 
                COALESCE(SUM(kolekcijas.skaits), 0) AS skaits
            FROM lietotaji
            LEFT JOIN kolekcijas ON lietotaji.lietotajvards = kolekcijas.lietotajs_id
            GROUP BY lietotaji.lietotajvards
            ORDER BY {order_by}
        """

        try:
            cur.execute(query)
            records = cur.fetchall()

            conn.close()

            if records:
                self.userstable.setRowCount(len(records))
                self.userstable.setColumnCount(3)
                self.userstable.setHorizontalHeaderLabels(["ID", "Lietotājvārds", "Skaits"])

                for row_index, user in enumerate(records):
                    print(f"Lietotāja dati: {user}")
                    self.userstable.setItem(row_index, 0, QTableWidgetItem(str(user[0])))
                    self.userstable.setItem(row_index, 1, QTableWidgetItem(user[1]))
                    self.userstable.setItem(row_index, 2, QTableWidgetItem(str(user[2])))
            else:
                self.userstable.setRowCount(1)
                self.userstable.setColumnCount(1)
                self.userstable.setHorizontalHeaderLabels(["Nav lietotāju"])
                self.userstable.setItem(0, 0, QTableWidgetItem("Nav lietotāju datu."))

        except Exception as e:
            print(f"SQL kļūda: {e}")
            conn.close()

    # maina lietotāju šķirošanas secību pēc izvēlnes izvēles
    def sortUsers(self):
        selected_option = self.filter.currentText()
        
        if selected_option == "ID (↓)":
            self.loadUsers("lietotaji.id ASC")  
        elif selected_option == "ID (↑)":
            self.loadUsers("lietotaji.id DESC")  
        elif selected_option == "Nosaukuma (↓)":
            self.loadUsers("lietotaji.lietotajvards ASC")  
        elif selected_option == "Nosaukuma (↑)":
            self.loadUsers("lietotaji.lietotajvards DESC")  
        elif selected_option == "Skaita (↓)":
            self.loadUsers("skaits DESC")
        elif selected_option == "Skaita (↑)":
            self.loadUsers("skaits ASC")
        else:
            print("Nezināma šķirošanas opcija!")
        
    # izdzēš izvēlēto lietotāju no datubāzes
    def deleteUser(self):
        selected_row = self.userstable.currentRow()
        if selected_row != -1: 
            user_id = self.userstable.item(selected_row, 0).text()
            conn = sqlite3.connect("senu_kolekcionars.db")
            cur = conn.cursor()

            # Dzēš lietotāju no datubāzes
            cur.execute("DELETE FROM lietotaji WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()

            self.loadUsers()

    # nosūta personalizētu paziņojumu par aktīvāko lietotāju
    def send_news(self):
        selected_row = self.userstable.currentRow()
        if selected_row != -1:
            user_name = self.userstable.item(selected_row, 1).text()

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            kolekcijas_id = None

            message = f"Visaktīvākais sēņotājs ir {user_name}"

            conn = sqlite3.connect("senu_kolekcionars.db")
            cur = conn.cursor()

            cur.execute("INSERT INTO pazinojumi (saturs, kolekcijas_id, laiks) VALUES (?, ?, ?)", 
                        (f"Visaktīvākais sēņotājs ir {user_name}", kolekcijas_id, current_time))
            conn.commit()
            conn.close()

            msg = QMessageBox(self)
            msg.setWindowTitle("Ziņa")
            msg.setText(message)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    background-color: white;
                    color: black;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid gray;
                     padding: 5px;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
            """)
            msg.exec_()


# Lietotāja kolekcijas ekrāns
class CollectionScreen(QMainWindow):
    def __init__(self, widget, currentUser):
        super(CollectionScreen, self).__init__(widget)
        loadUi("ui/collection.ui", self)

        # UI loga ģeometrijas labojums
        self.setFixedSize(521, 850)
        self.setGeometry(0, 0, 521, 850)
        self.setParent(widget)
        self.setWindowFlags(Qt.Widget)
        self.hide()
        self.showNormal()

        self.widget = widget
        self.currentUser = currentUser
        self.loadCollectionData()

        self.homebutton.clicked.connect(self.gotoHome)
        self.filter.currentIndexChanged.connect(self.sortCollection)
        self.deletebutton.clicked.connect(self.deleteSelectedRow)

    # ielādē kolekcijas datus no datubāzes
    def loadCollectionData(self, order_by="k.datums DESC"):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        query = f"""
        SELECT k.id, s.nosaukums, l.nosaukums, k.skaits, k.datums, k.attels
        FROM kolekcijas k
        JOIN senes s ON k.senes_id = s.id
        JOIN lokacija l ON k.lokacija_id = l.id
        WHERE k.lietotajs_id = ?
        ORDER BY {order_by}
        """

        cur.execute(query, (self.currentUser,))
        records = cur.fetchall()
        conn.close()

        # iestatām tabulas rindu un kolonnu skaitu
        self.collectiontable.setRowCount(len(records))
        self.collectiontable.setColumnCount(5)
        self.collectiontable.setHorizontalHeaderLabels(["Sēne", "Lokācija", "Skaits", "Datums", "Attēls"])

        for row_index, row_data in enumerate(records):
            id_, nosaukums, location, skaits, datums, image_blob = row_data

            self.collectiontable.setItem(row_index, 0, QTableWidgetItem(nosaukums))
            self.collectiontable.setItem(row_index, 1, QTableWidgetItem(location))
            self.collectiontable.setItem(row_index, 2, QTableWidgetItem(str(skaits)))
            self.collectiontable.setItem(row_index, 3, QTableWidgetItem(datums))

            # blob -> bilde
            if image_blob:
                pixmap = QPixmap()
                pixmap.loadFromData(image_blob)
                scaled_pixmap = pixmap.scaled(100, 100)

                # Izveidojam QLabel, lai attēlotu attēlu
                label = QLabel()
                label.setPixmap(scaled_pixmap)
                label.setAlignment(Qt.AlignCenter)

                # Izveidojam widget, kurā ievietojam QLabel
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.addWidget(label)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)

                # Iestatām widget kā tabulas šūnas saturu
                self.collectiontable.setCellWidget(row_index, 4, widget)
            self.collectiontable.setColumnWidth(4, 100)
            self.collectiontable.verticalHeader().setDefaultSectionSize(100)

    # kārto kolekciju pēc izvēlētā kritērija
    def sortCollection(self):

        selected_option = self.filter.currentText()

        if selected_option == "Nosaukuma (↓)":
            order_by = "s.nosaukums ASC"
        elif selected_option == "Nosaukuma (↑)":
            order_by = "s.nosaukums DESC"
        elif selected_option == "Datuma (↓)":
            order_by = "k.datums ASC"
        elif selected_option == "Datuma (↑)":
            order_by = "k.datums DESC"
        elif selected_option == "Skaita (↓)":
            order_by = "k.skaits ASC"
        elif selected_option == "Skaita (↑)":
            order_by = "k.skaits DESC"

        self.loadCollectionData(order_by)

    # dzēš izvēlēto ierakstu no kolekcijas
    def deleteSelectedRow(self):
        selected_row = self.collectiontable.currentRow()
        if selected_row == -1:
            return

        mushroom_name = self.collectiontable.item(selected_row, 0).text()
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT k.id, k.skaits FROM kolekcijas k JOIN senes s ON k.senes_id = s.id WHERE s.nosaukums = ? AND k.lietotajs_id = ?", 
                    (mushroom_name, self.currentUser))
        row_data = cur.fetchone()
        conn.close()

        if not row_data:
            return

        item_id, skaits = row_data

        # ja ir vairāk par vienu eksemplāru, rādām brīdinājumu
        if skaits > 1:
            self.showWarningDialog(item_id, skaits)
        else:
            self.confirmDelete(item_id)

    # rāda brīdinājumu, ja kolekcijā ir vairāk par vienu ierakstu
    def showWarningDialog(self, item_id, skaits): 
        warning_dialog = QDialog(self)
        loadUi('ui/warning.ui', warning_dialog)

        all_button = warning_dialog.findChild(QPushButton, 'allbutton')
        last_button = warning_dialog.findChild(QPushButton, 'lastbutton')

        all_button.clicked.connect(lambda: self.handleDelete(warning_dialog, item_id, skaits, True))
        last_button.clicked.connect(lambda: self.handleDelete(warning_dialog, item_id, skaits, False))

        warning_dialog.exec_()

    # dati tiek dzēsti un logs aizvērts
    def handleDelete(self, dialog, item_id, skaits, delete_all):
        if delete_all:
            self.confirmDelete(item_id)
        else:
            self.reduceCount(item_id, skaits)

        dialog.accept()



    # apstiprina un dzēš ierakstu no datubāzes
    def confirmDelete(self, item_id):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM kolekcijas WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        self.loadCollectionData()

    # samazina ieraksta daudzumu, ja ir vairāk par vienu
    def reduceCount(self, item_id, skaits):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()
        new_skaits = skaits - 1
        cur.execute("UPDATE kolekcijas SET skaits = ? WHERE id = ?", (new_skaits, item_id))
        conn.commit()
        conn.close()
        self.loadCollectionData()

    # atgriežas uz sākuma ekrānu
    def gotoHome(self):
        home = HomeScreen(self.widget, self.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))


# Jaunas sēnes ekrāns
class NewUploadScreen(QMainWindow):
    def __init__(self, widget):
        super(NewUploadScreen, self).__init__(widget)
        loadUi("ui/newupload.ui", self)
        self.widget = widget

        # UI loga ģeometrijas piespiedu labojums
        self.setFixedSize(521, 850)
        self.setGeometry(0, 0, 521, 850)
        self.setParent(widget)
        self.setWindowFlags(Qt.Widget)
        self.hide()
        self.showNormal()

        self.homebutton.clicked.connect(self.gotoHome)
        self.uploadbutton.clicked.connect(self.upload)
        self.error.setText("")
        
    # jaunas sēnes attēla augšupielāde un pāreja uz nākamo soli
    def upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Izvēlies attēlu", "", "Images (*.png *.jpg *.jpeg)")

        if not file_path:
            self.error.setText("❌ Lūdzu izvēlieties failu.")
            return

        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.error.setText("❌ Failam jābūt .jpg, .jpeg vai .png formātā.")
            return
        
        # pārbauda vai logs jau neeksistē, lai nedubultotos
        for i in range(self.widget.count()):
            if isinstance(self.widget.widget(i), AddScreen):
                self.widget.setCurrentIndex(i)
                return

        add_screen = AddScreen(self.widget, file_path)
        self.widget.addWidget(add_screen)
        self.widget.setCurrentIndex(self.widget.indexOf(add_screen))

    # pārslēdz uz sākuma ekrānu, pārbaudot, ka logs nedubultojas
    def gotoHome(self):
        for i in range(self.widget.count()):
            if isinstance(self.widget.widget(i), HomeScreen):
                self.widget.setCurrentIndex(i)
                return

        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))


# Sēnes datu ievades logs
class AddScreen(QMainWindow):
    def __init__(self, widget, file_path):
        super(AddScreen, self).__init__(widget)
        loadUi("ui/newadd.ui", self)
        self.widget = widget

        # UI loga ģeometrijas piespiedu labojums
        self.setFixedSize(521, 850)
        self.setGeometry(0, 0, 521, 850)
        self.setParent(widget)
        self.setWindowFlags(Qt.Widget)
        self.hide()
        self.showNormal()
        self.error.setText("")

        #šodienas datums automātiski tiek piedāvāts
        today_date = datetime.today().strftime("%d.%m.%Y")
        self.datefield.setText(today_date)

        self.file_path = file_path
        # parāda un pārbauda attēlu
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.error.setText("❌ Nevarēja ielādēt attēlu.")
        else:
            self.imagelabel.setPixmap(pixmap.scaled(self.imagelabel.size(), Qt.KeepAspectRatio))

        self.loadComboBoxes()
        self.homebutton.clicked.connect(self.gotoHome)
        self.addbutton.clicked.connect(self.addToDatabase)
        self.deletebutton.clicked.connect(self.gotoNewUpload)

    # pārslēdz uz sākuma ekrānu, pārbaudot, ka logs nedubultojas
    def gotoHome(self):
        for i in range(self.widget.count()):
            if isinstance(self.widget.widget(i), HomeScreen):
                self.widget.setCurrentIndex(i)
                return

        home = HomeScreen(self.widget, self.widget.currentUser)
        self.widget.addWidget(home)
        self.widget.setCurrentIndex(self.widget.indexOf(home))

    # pārslēdz uz augšupielādes ekrānu, pārbaudot, ka logs nedubultojas
    def gotoNewUpload(self):
        for i in range(self.widget.count()):
            if isinstance(self.widget.widget(i), NewUploadScreen):
                self.widget.setCurrentIndex(i)
                return

        newupload = NewUploadScreen(self.widget)
        self.widget.addWidget(newupload)
        self.widget.setCurrentIndex(self.widget.indexOf(newupload))

    # ielādē iespējamos nosaukumus un lokācijas no datubāzes
    def loadComboBoxes(self):
        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT nosaukums FROM senes")
        self.namecombo.addItems([row[0] for row in cur.fetchall()])

        cur.execute("SELECT nosaukums FROM lokacija")
        self.locationcombo.addItems([row[0] for row in cur.fetchall()])

        conn.close()
    
    # saglabā jauno sēni datubāzē, pārbaudot ievadītos datus
    def addToDatabase(self):
        selected_name = self.namecombo.currentText()
        selected_location = self.locationcombo.currentText()
        entered_date = self.datefield.text().strip()

        # Convert dd.mm.yyyy -> yyyy-mm-dd
        import datetime
        try:
            date_obj = datetime.datetime.strptime(entered_date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            self.error.setText("❌ Nepareizs datuma formāts. Izmantojiet: dd.mm.gggg")
            self.datefield.setText("dd.mm.gggg")
            return

        # bilde -> blob
        with open(self.file_path, 'rb') as file:
            image_blob = file.read()

        conn = sqlite3.connect("senu_kolekcionars.db")
        cur = conn.cursor()

        cur.execute("SELECT id FROM lokacija WHERE nosaukums = ?", (selected_location,))
        location_id = cur.fetchone()
        if not location_id:
            self.error.setText("❌ Kļūda: Nepareiza lokācija.")
            return
        location_id = location_id[0]

        cur.execute("SELECT id FROM senes WHERE nosaukums = ?", (selected_name,))
        mushroom_id = cur.fetchone()
        if not mushroom_id:
            self.error.setText("❌ Kļūda: Nepareizs nosaukums.")
            return
        mushroom_id = mushroom_id[0]

        cur.execute("SELECT skaits FROM kolekcijas WHERE lietotajs_id = ? AND senes_id = ?", 
                    (self.widget.currentUser, mushroom_id))
        existing_record = cur.fetchone()

        # pārbaude, vai lietotājs ir jau iepriekš pievienojis šo sēni
        if existing_record:
            new_count = existing_record[0] + 1
            cur.execute("UPDATE kolekcijas SET skaits = ?, lokacija_id = ?, datums = ? WHERE lietotajs_id = ? AND senes_id = ?",
                        (new_count, location_id, formatted_date, self.widget.currentUser, mushroom_id))
        else:
            cur.execute("INSERT INTO kolekcijas (lietotajs_id, senes_id, lokacija_id, attels, skaits, datums) VALUES (?, ?, ?, ?, ?, ?)",
                        (self.widget.currentUser, mushroom_id, location_id, image_blob, 1, formatted_date))

        conn.commit()
        conn.close()

        self.error.setText("✅ Pievienots kolekcijai!")






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