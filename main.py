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

    def initUi(self):
        """
        -- intial window setup -- 
        """
        self.icons_and_text.setHidden(True)
        self.dashboard_1.setChecked(True)
        self.stackedWidget.setCurrentIndex(0)

        """
            --side bar menu button signals--
            first set small side bar buttons
            second set  big side bar buttons
        """
        self.dashboard_1.clicked.connect(self.open_dashboard)
        self.clients_1.clicked.connect(self.open_clients)
        self.new_client_1.clicked.connect(self.open_new_client)
        self.settings_1.clicked.connect(self.open_settings)

        self.dashboard_2.clicked.connect(self.open_dashboard)
        self.clients_2.clicked.connect(self.open_clients)
        self.new_client_2.clicked.connect(self.open_new_client)
        self.settings_2.clicked.connect(self.open_settings)
        self.drop_button.raise_()
        
        self.get_fields()
        self.load_table()

    def open_dashboard(self):
        self.stackedWidget.setCurrentIndex(0)
        self.get_fields()

   
    def open_clients(self):
        self.stackedWidget.setCurrentIndex(2)
        self.get_fields()

    
    def open_new_client(self):
        self.stackedWidget.setCurrentIndex(1)
        self.get_fields()        
   
    def open_settings(self):
        self.stackedWidget.setCurrentIndex(3)
        self.get_fields()
    
    @debug_func
    def get_fields(self):
        current_page = self.stackedWidget.currentWidget()
        if current_page:
            # self.current_table = current_page.findChild((QTableWidget))
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


class TabelWidget(QTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.init_table_settings()

    def init_table_settings(self):
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.setAlternatingRowColors(True)

        horizontal_header = self.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.hide_columns(hide=True)
        self.verticalHeader().setVisible(False)


    def hide_columns(self, hide=True):
        hiden_columns = (0,5,6,7,4)
        for column in hiden_columns:
            self.setColumnHidden(column,hide)

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
                table_item = QTableWidgetItem(str(col_data))
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_idx, col_idx, table_item)
        
        self.setSortingEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())