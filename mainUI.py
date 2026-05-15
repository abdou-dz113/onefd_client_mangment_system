import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import (QLineEdit,QComboBox)
from database import Database


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.db = Database() 
        self.widgets = self.findChildren((QLineEdit, QComboBox))
        self.initUI()
        self.add_button.clicked.connect(self.insert)
        self.clear_button.clicked.connect(self.clear)
        self.search_button.clicked.connect(self.search)
    
    def initUI(self):
        self.restwindow()

    def restwindow(self):
        self.loadtable()
        self.level.setCurrentIndex(-1)
        

    def loadtable(self):
        data = self.db.tablequery()
        self.update_table(data)

    def update_table(self,data):
        data_row_count = len(data)
        if not data:
            self.table01.setRowCount(0)
            return
        data_column_count = len(data[0])
        if data_row_count > 0 and data_column_count >0:
            self.table01.setRowCount(0)
            self.table01.setRowCount(data_row_count)
            self.table01.setColumnCount(data_column_count)
            for i, row in enumerate(data):
                for c, cell in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(cell))
                    self.table01.setItem(i,c,item)

    def insert(self):
        input = self.get_input()
        input_names = [i[0] for i in input]
        
        
        if not input:
            return
        else:
            for widget in self.widgets:
                if widget.objectName() not in input_names and not widget.objectName()=="QComboBox":
                    widget.setStyleSheet("background-color: #fa5a5f;")


            


    def insert2(self):
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
        for widget in self.widgets:
            widget.setStyleSheet("")
            if not widget.objectName() == "level":
                widget.clear()
        return self.restwindow()
        

    
    def get_input(self):
        active_widgets =[]
        widget_dict = {}
        for widget in self.widgets:
            widget_id = widget.objectName()
            widget.setStyleSheet("background-color: white;")
            #Check for comboboxs
            if isinstance(widget, QtWidgets.QComboBox):
                level_val = widget.currentIndex()
                widget_dict[widget_id] = level_val
                if level_val >=0:
                    active_widgets.append((widget_id, level_val))
            #check for line text edits
            if isinstance(widget, QtWidgets.QLineEdit):
                widget_dict[widget_id] = widget.text()
                text_val = widget.text().strip()
                if text_val:
                    active_widgets.append((widget_id,text_val))
        
        print(widget_dict)
        
        return active_widgets 

    def search(self):

        stext = self.username_01.text()
        expestion = self.lastname.text()
        search_table = self.db.search(stext)
        self.update_table(search_table)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())