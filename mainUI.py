import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import (QLineEdit,QComboBox,QHeaderView)
from database import Database


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.db = Database() 
        self.widgets = self.findChildren((QLineEdit, QComboBox))
        self.widget_map = {w.objectName():w for w in self.widgets}
        self.initUI()
        self.add_button.clicked.connect(self.insert)
        self.clear_button.clicked.connect(self.clear)
        self.search_button.clicked.connect(self.search)
    
    def initUI(self):
        self.reset_window()
        self.inputs_frame.setStyleSheet("""
            QLineEdit[hasError='true']{
                border: 2px solid #FF4D4D;
            
            }
            QLineEdit{
            
            }
            QLineComboBox[hasError='true']{
                border: 2px solid #FF4D4D;
            
            }
        """)
        self.table01.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def reset_window(self):
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
        
        inputs = self.get_input()
        empty_widgets = []
        is_input_valid = True

        for widget, value in inputs.items():
            if widget =='level':                
                if value < 0:
                    print(widget,"is empty")
                    is_input_valid = False
                    self.widget_map[widget].setProperty("hasError", "true")                                 
                else:
                    self.widget_map[widget].setProperty("hasError", "false")
           
            if not value and  not widget == 'level':
                #print(widget,"is empty")
                is_input_valid = False
                self.widget_map[widget].setProperty("hasError", "true")
            else:
                self.widget_map[widget].setProperty("hasError", "false")


            
            self.redraw_widget(self.widget_map[widget])

        if not is_input_valid:
            print("Please fill the empty field")
            return
        self.db.insert(inputs)
        self.reset_window()




    def redraw_widget(self,widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()



    def clear(self):    
        for widget in self.widgets:
            widget.setProperty("hasError","false")
            self.redraw_widget(widget)
            if not widget.objectName() == "level":
                widget.clear()
        return self.reset_window()
        

    
    def get_input(self):
        widget_dict = {}
        for widget in self.widgets:
            widget_id = widget.objectName()
            #Check for comboboxs
            if isinstance(widget, QtWidgets.QComboBox):
                widget_index = widget.currentIndex()
                widget_dict[widget_id] = widget_index

            #check for line text edits
            if isinstance(widget, QtWidgets.QLineEdit):
                widget_dict[widget_id] = widget.text()

        
        print(widget_dict)
        
        return widget_dict

    def search(self):
        inputs = self.get_input()
        search_table = self.db.search(inputs)
        self.update_table(search_table)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())