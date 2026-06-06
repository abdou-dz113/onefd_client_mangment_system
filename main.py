import sys
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenu, QMessageBox, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
import resources_rc
import settings as s
from services import client_service as cs


def debug_func(func,):
    def wrapper(*arg,**kwarg):
        print(f"running {func.__name__}")
        func(*arg)
        print(f"finshed running {func.__name__}")
    return wrapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(s.mainwinui,self)
        self.table_1 = TabelWidget(s.table_headers)
        self.dashboard_tabel_layout.addWidget(self.table_1)
        self.initUi()
        
        #___ side bar menu buttons signal __________________
        self.dashboard_1.clicked.connect(self.open_dashboard)
        self.clients_1.clicked.connect(self.open_clients)
        self.new_client_1.clicked.connect(self.open_new_client)
        self.settings_1.clicked.connect(self.open_settings)

        self.dashboard_2.clicked.connect(self.open_dashboard)
        self.clients_2.clicked.connect(self.open_clients)
        self.new_client_2.clicked.connect(self.open_new_client)
        self.settings_2.clicked.connect(self.open_settings)
        
        #___ Dashboard buttons signal ______________________
        self.add_button.clicked.connect(self.insert)
        self.refresh_button.clicked.connect(self.reset_inputs)

    def initUi(self):
        #___ input vadlidation stylesheet _________________
        self.inputs_frame.setStyleSheet("""
                QLineEdit[hasError='true']{
                border: 2px solid #FF4D4D;
            }
            QComboBox[hasError='true']{
                border: 2px solid #FF4D4D;           
            }
                                        """)
        #___ initial window setup __________________________
        self.icons_and_text.setHidden(True)
        self.dashboard_1.setChecked(True)
        self.stackedWidget.setCurrentIndex(0)
        #___ Dashboard level combobox setup ________________
        self.level_input_1.clear()
        self.level_input_1.addItems(s.level_map.values())
        self.level_input_1.setCurrentIndex(-1)
        
        #___ client edit level combobox setup ______________
        self.level_input_2.clear()
        self.level_input_2.addItems(s.level_map.values())
        self.level_input_2.setCurrentIndex(-1)

        self.get_fields()
        self.load_table()

    #___ side bar menu buttons functions __________________
    def open_dashboard(self):
        self.stackedWidget.setCurrentIndex(0)
  
    def open_clients(self):
        self.stackedWidget.setCurrentIndex(2)
    
    def open_new_client(self):
        self.stackedWidget.setCurrentIndex(1)
          
    def open_settings(self):
        self.stackedWidget.setCurrentIndex(3)
  
    
    @debug_func
    def get_fields(self):
        current_page = self.stackedWidget.currentWidget()
        if current_page:
            self.widgets = current_page.findChildren((QLineEdit, QComboBox))
            self.widgets_map = {w.objectName():w for w in self.widgets}
       
    @debug_func
    def table_setup(self):
        self.clients_tabel_1.setHorizontalHeaderLabels(s.table_headers)
        self.clients_tabel_1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.clients_tabel_2.setHorizontalHeaderLabels(s.table_headers)
        self.clients_tabel_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    @debug_func
    def load_table(self):
        data = cs.table_query()
        self.table_1.fill_table(data)

    @debug_func
    def update_table(self, data, table):
       
        current_table = table
        
        if not current_table:
            print("There is no tabel in this page.")
            return 
        
        if not data:
            current_table.setRowCount(1)
            item = QTableWidgetItem("There is nothing to Show")
            current_table.setItem(0,0,item)
            print ("There is Nothing to show")
            return 
        else:
            row_count = len(data)
            column_count = len(data[0])
            if row_count == 0 or column_count == 0:
                return
            current_table.setRowCount(0)
            current_table.setRowCount(row_count)
            current_table.setColumnCount(column_count)
            for row_id, data_row in enumerate(data):
                for column_id, column in enumerate(data_row):
                    item = QTableWidgetItem(str(column))
                    current_table.setItem(row_id,column_id,item)

    def redraw_widget(self,widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def reset_inputs(self):
        if self.widgets_map:
            for widget_name, widget_obj in self.widgets_map.items():
                if isinstance(widget_obj, QComboBox):
                    widget_obj.setCurrentIndex(-1)
                elif isinstance(widget_obj, QLineEdit):
                    widget_obj.setText("")
                widget_obj.setProperty("hasError","false")
                self.redraw_widget(widget_obj)

    def validate_ui(self,filled_froms):
        if not filled_froms:
            return
        for widget_name, widget_obj in self.widgets_map.items():
            if not widget_name in filled_froms.keys():
                widget_obj.setProperty("hasError", "true")
            else:
                widget_obj.setProperty("hasError", "false")
            self.redraw_widget(widget_obj)

    def get_input(self):
        widgets_map = self.widgets_map
        widget_values = {}
        if widgets_map:
            for widget_name, widget in widgets_map.items():
                if isinstance(widget,QComboBox):
                        value = widget.currentIndex()
                elif isinstance(widget, QLineEdit):
                        value = widget.text()
                widget_values.update({widget_name:value})
        return widget_values
    
    def insert(self):
        inputs = self.get_input()
        valid, valid_inputs = cs.validate_input(inputs)
        self.validate_ui(valid_inputs)
        if valid:
            resp = cs.insert(valid_inputs)
            if resp:
                print("data added")
                self.reset_inputs()
                self.load_table()
            else:
                print("error")




class TabelWidget(QTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.init_table_settings()
        
        self.setStyleSheet(s.tabel_css)

    def init_table_settings(self):
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.setAlternatingRowColors(False)

        horizontal_header = self.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.hide_columns(hide=True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.verticalHeader().setDefaultSectionSize(40)


    def hide_columns(self, hide=True):
        hiden_columns = (0,5,6,7,4)
        for column in hiden_columns:
            self.setColumnHidden(column,hide)

    def item_gen(self,col_idx,col_val):
        exam_indexs = (9,10,11,12,13)
        if col_idx in exam_indexs:
            item = QTableWidgetItem(str(s.exams_progress_dict.get(col_val)[0]))
            item.setBackground(QBrush(QColor(s.exams_progress_dict.get(col_val)[1])))
            item.setForeground(QBrush(QColor("#f9f7f3")))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return item
        else:
            item = QTableWidgetItem(str(col_val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return item
        

    def fill_table(self, data_matrix):
        if not data_matrix:
            text = "There is nothing to show."
            print(text)
            self.setRowCount(1)
            self.setColumnCount(2)
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.setItem(0,1,item)
            self.horizontalHeader().setVisible(False)
            return

        self.setRowCount(len(data_matrix))
        self.horizontalHeader().setVisible(True)
        self.setSortingEnabled(False)
        for row_idx, row_data in enumerate(data_matrix):
            for col_idx, col_data in enumerate(row_data):
                table_item = self.item_gen(col_idx,col_data)
                self.setItem(row_idx, col_idx, table_item)
        self.setSortingEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())