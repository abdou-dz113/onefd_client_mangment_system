import sys
from PyQt6 import QtWidgets, uic
from database import Database


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.db = Database() 

        self.initUI()
        self.add_button.clicked.connect(self.insert)
        self.clear_button.clicked.connect(self.clear)
        self.search_button.clicked.connect(self.search)
    
    def initUI(self):
        self.level.setCurrentIndex(-1)
        self.loadtable()

    def loadtable(self):
        data = self.db.tablequery()
        self.update_table(data)

    def update_table(self,data):
        self.table01.setRowCount(0)
        self.table01.setRowCount(len(data))
        self.table01.setColumnCount(len(data[0]))
        for i, row in enumerate(data):
            for c, cell in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(cell))
                self.table01.setItem(i,c,item)


    def insert(self):
        username_01=self.username_01.text()
        password_01=self.password_01.text()
        firstname=self.firstname.text()
        lastname=self.lastname.text()
        level=self.level.currentIndex()
        phone_number=self.phone_number.text()
        username_02=self.username_02.text()
        password_02=self.password_02.text()

        self.db.insert(username_01,password_01,firstname,lastname,level,phone_number,username_02,password_02)
        self.loadtable()

    def clear(self):    
        for widget in self.findChildren((QtWidgets.QLineEdit,)):
            widget.clear()
        self.level.setCurrentIndex(-1)
    
    def search(self,expestion):
        expestion = self.lastname.text()
        search_table = self.db.search(expestion)
        self.update_table(search_table)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())