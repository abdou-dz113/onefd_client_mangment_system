import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import (QLineEdit,QComboBox,QHeaderView,QMenu,QApplication,QMessageBox,QMainWindow)
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
        self.table01.customContextMenuRequested.connect(self.show_context_menu)
        
    def initUI(self):
        self.reset_window()
        self.inputs_frame.setStyleSheet("""
            QLineEdit[hasError='true']{
                border: 2px solid #FF4D4D;
            
            }
            QLineEdit{
            
            }
            QComboBox[hasError='true']{
                border: 2px solid #FF4D4D;
            
            }
        """)
        self.table01.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def edit_client(self):
        self.client_edit_window= QMainWindow()
        uic.loadUi("edit_client.ui",self.client_edit_window)
        self.client_edit_window.show()

    def show_dialog(self,title,message):
        msg = QMessageBox()
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setWindowTitle(title)
        msg.setText(message)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Ok:
            return True
        elif result == QMessageBox.StandardButton.Cancel:
            return False



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
    

    def reset_window(self):
        self.loadtable()
        self.level.setCurrentIndex(-1)
        

    def show_context_menu(self,position):
        menu = QMenu()
        index = self.table01.indexAt(position)
        item = self.table01.item(0,1)

        if index.isValid():
 
            lname = self.table01.item(index.row(),0).text()
            frname = self.table01.item(index.row(),1).text()
            search = self.db.search({"firstname":frname,"lastname":lname})

            edit_action = menu.addAction(f"تعديل  [{lname} {frname}]")
            delete_action = menu.addAction(f"حذف {lname} {frname}")
            copy_login_username = menu.addAction(f"Copy Login Username ")
            copy_login_password = menu.addAction(f"Copy Login password ")
            copy_devoir_username = menu.addAction(f"Copy e-devoir username ")
            copy_devoir_password = menu.addAction(f"Copy e-devoir password ")
        else:
            return
        
        action = menu.exec(self.table01.viewport().mapToGlobal(position))
        item_names  =   ['lastname',
                        'firstname',
                        'level',
                        'username_01',
                        'password_01',
                        'username_02',
                        'password_02',
                        'phone_number']
        
        item_dict = dict(zip(item_names,search[0]))

        #print(item_dict)
        clipboard = QApplication.clipboard()
        if action == edit_action:
            self.edit_client()
        elif action == delete_action:
            self.delete_client(lname,frname)
        elif action == copy_login_username:
            clipboard.setText(item_dict.get("username_01"))
        elif action == copy_login_password:
            clipboard.setText(item_dict.get("password_01"))
        elif action == copy_devoir_username:
            clipboard.setText(item_dict.get("username_02"))
        elif action == copy_devoir_password:
            clipboard.setText(item_dict.get("password_02"))            
        
    def delete_client(self, last_name,first_name):
            window_title = "Delete client From database"
            message = f"Are you sure you want to delete: [{last_name} {first_name}]"
            if self.show_dialog(window_title,message):
                self.db.delete(last_name,first_name)
                self.reset_window()
                self.show_dialog("Message","Client has been deleted ")

  

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
        
        return widget_dict

     
    def is_valid(self,key,value):
        if key == "level":
            if value >=0:
                return True
        else:
            return bool(value)

    def validate_input(self,get_filled=False):
        """
        checks for empty input fields
        get_filled=True : return {field name: input} of any filled input
        get_filled=False : return inputs only if all filled
        """
        inputs = self.get_input()
        is_input_valid = True
        valid_inputs = {}
        
        for widget, value in inputs.items():
            if self.is_valid(widget, value):
                valid_inputs[widget] = value
            else:
                is_input_valid = False
        
        if valid_inputs.values:
            if is_input_valid:
                return valid_inputs
            elif get_filled:
                return valid_inputs
        
        



    def validate_ui(self,valid_inputs):
        """
        visualy show if input is not valid or emprty when you click insert
        """
        if not valid_inputs:
            for widget_name, widget_id in self.widget_map.items():
                widget_id.setProperty("hasError","true")
                self.redraw_widget(widget_id)
            return

        for widget_name, widget_id in self.widget_map.items():
            if not widget_name in valid_inputs.keys():
                widget_id.setProperty("hasError","true")
            else:
                widget_id.setProperty("hasError","false")
            self.redraw_widget(widget_id)


    def insert(self):
        valid = self.validate_input()
        self.validate_ui(self.validate_input(True))
        if valid:
            self.db.insert(valid)
            self.loadtable()
            self.clear()
        else:
            self.show_dialog("Error Message","Please fill all the red fields")
        



    def search(self):       
        inputs = self.validate_input(True)
        if not inputs:
            return
        search_table = self.db.search(inputs)
        self.update_table(search_table)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())