import sys
import io
from PIL import Image, ImageQt
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import (QLineEdit,QComboBox,QHeaderView,QMenu,QApplication,QMessageBox,QMainWindow,)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush,QColor,QMovie,QPixmap
from services import client_service as cs
from services.site_scraper import WebLogin
import threading
from functools import wraps

headers_labels = ["id","lastname","firstname","level","username_01","password_01","username_02","password_02","phone_number","devoir_01","devoir_02","devoir_03","devoir_04","devoir_05",]
def make_threaded(func):
    """
    A decorator that automatically runs the decorated function 
    in a separate background thread.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Instantiate the thread with passed arguments
        new_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        # Start execution immediately
        new_thread.start()
        # Return the thread instance so the caller can join() it if needed
        return new_thread
    return wrapper
progress_dict= {
    0:("غير منجز","#c0392b"),
    1:("منجز غير مدفوع","#e67e22"),
    2:("مدفوع غير منجز","#5b8fa8"),
    3:("منجز مدفوع","#27ae60"),
}

def get_table_item(row_num,col_num,col_val):
    if col_num>8:
        item = QtWidgets.QTableWidgetItem(str(progress_dict.get(col_val)[0]))
        item.setBackground(QBrush(QColor(progress_dict.get(col_val)[1])))
        item.setForeground(QBrush(QColor("#f9f7f3")))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
    else:
        item = QtWidgets.QTableWidgetItem(str(col_val))
        return item


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.widgets = self.findChildren((QLineEdit, QComboBox))
        self.widget_map = {w.objectName():w for w in self.widgets}
        self.client_edit_window= QMainWindow()

        self.initUI()
        self.site_s = WebLogin()
        
        self.add_button.clicked.connect(self.insert)
        self.clear_button.clicked.connect(self.clear)
        self.search_button.clicked.connect(self.search)
        self.fill_from_site_button.clicked.connect(self.get_captcha)
        self.get_info_button.clicked.connect(self.fill_from_site)
        self.table01.customContextMenuRequested.connect(self.show_context_menu)
        self.refrech_captcha_button.clicked.connect(self.refrech_captcha)
    
    def loading_image(self):
        self.movie = QMovie("resources\loading.gif")
        self.captcha_image.setMovie(self.movie)
        self.movie.start()
        self.redraw_widget(self.captcha_image)

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
        self.table_header_labels = ["id","اللقب","الاسم","المستوى","اسم مستخدم الحساب","كلمة مرور الحساب","اسم مستخدم المعلام","كلمة مرور المعلام","رقم الهاتف","فرض 1","فرض 2","فرض 3","فرض 4","فرض 5",]
        self.table01.setHorizontalHeaderLabels(self.table_header_labels)
        self.table01.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        uic.loadUi("edit_client.ui",self.client_edit_window)
        self.client_edit_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.hide_columns(False)
        #self.captcha_frame.setHidden(True)

    def hide_columns(self,con):
        if con:
            column_to_hide = (0,4,5,6,7)
            for column in column_to_hide:
                self.table01.setColumnHidden(column,True)
            
    
    def loadtable(self):
        data = cs.table_query()
        self.update_table(data)

    def update_table(self,data):
        if not data:
            self.table01.setRowCount(0)
            return
        data_row_count = len(data)
        data_column_count = len(data[0])
        if data_row_count > 0 and data_column_count >0:
            self.table01.setRowCount(0)
            self.table01.setRowCount(data_row_count)
            self.table01.setColumnCount(data_column_count)
            for i, row in enumerate(data):
                for c, cell in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(cell))
                    self.table01.setItem(i,c,item)

    def update_row(self, row_num, new_data):
        for col_num, col_val in enumerate(new_data):
            item = get_table_item(row_num,col_num,col_val)
            self.table01.setItem(row_num,col_num,item)

    
    def edit_client(self,client_id):
         #Disable main window clicks↓↓↓
        info_dict = cs.get_from_id(client_id)
        self.client_edit_window.show()
        self.edit_forms = self.client_edit_window.findChildren((QLineEdit,QComboBox))
        self.edit_forms_map = {widget.objectName():widget for widget in self.edit_forms}
        #self.client_edit_window.id_label.setText(f"Client ID: {client_id}")
        self.fill_edit_client(info_dict)
        try:
            self.client_edit_window.save_button.clicked.disconnect()
        except:
            pass

        
        self.client_edit_window.save_button.clicked.connect(lambda:self.save_edit(info_dict))
        self.client_edit_window.cancel_button.clicked.connect(self.client_edit_window.close)


    
    def fill_edit_client(self,info_dict):
        if not info_dict:
            return
              
        for widget,value in info_dict.items():

            if isinstance(self.edit_forms_map[widget],QComboBox):
                self.edit_forms_map[widget].setCurrentIndex(int(value))
            elif isinstance(self.edit_forms_map[widget],QLineEdit):
                self.edit_forms_map[widget].setText(str(value))
   



    def save_edit(self,old_info):
        new_info = self.get_input(is_main_window=False)
        changed_info = cs.if_changed(old_info, new_info)
        save = cs.save_edit(changed_info)
        if save:
            print("Changes saved.")
            self.client_edit_window.close()
            row_info = cs.search_by_id(old_info.get("client_id"))
            self.current_row = self.table01.currentRow()
            self.update_row(self.current_row,row_info)
        else:
            print("no changes saved.")
 
    def row_changed(self,row_id):
        pass

    def show_dialog(self,title,message,cancel_button=True):
        msg = QMessageBox()
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel if cancel_button else QMessageBox.StandardButton.Ok)
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
        
    def on_row_double_click(self,row,column):
        pass

    def show_context_menu(self,position):
        menu = QMenu()
        index = self.table01.indexAt(position)
        item = self.table01.item(0,1)
        if index.isValid():
            client_id = self.table01.item(index.row(),0).text()
            lname = self.table01.item(index.row(),1).text()
            frname = self.table01.item(index.row(),2).text()
            search = cs.get_from_id(client_id)
            edit_action = menu.addAction(f"تعديل  [{lname} {frname}]")
            """delete """
            delete_action = menu.addAction(f"حذف {lname} {frname}")
            copy_login_username = menu.addAction(f"Copy Login Username ")
            copy_login_password = menu.addAction(f"Copy Login password ")
            copy_devoir_username = menu.addAction(f"Copy e-devoir username ")
            copy_devoir_password = menu.addAction(f"Copy e-devoir password ")
        else:
            return
        action = menu.exec(self.table01.viewport().mapToGlobal(position))

        #print(item_dict)
        clipboard = QApplication.clipboard()
        if action == edit_action:
            self.edit_client(client_id)

        elif action == delete_action:
            self.delete_client(client_id,lname,frname)
        elif action == copy_login_username:
            clipboard.setText(search.get("username_01"))
        elif action == copy_login_password:
            clipboard.setText(search.get("password_01"))
        elif action == copy_devoir_username:
            clipboard.setText(search.get("username_02"))
        elif action == copy_devoir_password:
            clipboard.setText(search.get("password_02"))            
        

    def get_input(self,is_main_window= True):
        if is_main_window:
            forms = self.widgets
        else:
            forms = self.edit_forms
        widget_dict = {}
        for widget in forms:
            widget_id = widget.objectName()
            #Check for comboboxs
            if isinstance(widget, QtWidgets.QComboBox):
                widget_index = widget.currentIndex()
                widget_dict[widget_id] = widget_index

            #check for line text edits
            if isinstance(widget, QtWidgets.QLineEdit):
                widget_dict[widget_id] = widget.text()
        
        return widget_dict 

     
    
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
        inputs = self.get_input()
        valid, filled_forms  = cs.validate_input(inputs)
        self.validate_ui(filled_forms)
        if valid:
            result = cs.insert(filled_forms)
            self.loadtable()
            self.clear()
        else:
            self.show_dialog("Error Message","Please fill all the input fields")
            
    def search(self):       
        inputs = self.get_input()
        search_table = cs.search(inputs)
        if search_table:
            self.update_table(search_table)

    def delete_client(self, client_id, last_name, first_name):
            window_title = "Delete client From database"
            message = f"Are you sure you want to delete: [{last_name} {first_name}]"
            if self.show_dialog(window_title,message):
                result = cs.delete(client_id)
                if result:
                    self.reset_window()
                    self.show_dialog("Message","Client has been deleted ",cancel_button=False)

    def fill_from_site(self):
        login_dict = self.get_input()
        username = login_dict.get("username_01")
        password = login_dict.get("password_01")
        captcha = login_dict.get("captcha_input")
        if all((username,password,captcha)):
            self.site_s.login(username,password,captcha)
            site_data = self.site_s.get_info()
            site_data = cs.clean_site_data(site_data)
        else:
            return

        if site_data:
            for widget_name, widget in self.widget_map.items():
                if widget_name in ("username_01","password_01"):
                    continue
                if isinstance(widget,QLineEdit):
                    widget.setText(str(site_data.get(widget_name)))
                elif isinstance(widget,QComboBox):
                    widget.setCurrentIndex(site_data.get("level"))
            

    def get_captcha(self,*args, **kwargs):
        self.loading_image()
        image_req = self.site_s.get_captcha()
        if image_req:
            image = Image.open(io.BytesIO(image_req))
            image_q = ImageQt.ImageQt(image)
            pixmap  =  QPixmap.fromImage(image_q)
            self.captcha_image.setPixmap(pixmap)
        

    def refrech_captcha(self,*args,**kwargs):
        self.loading_image()
        image_bytes = self.site_s.refresh_captcha()
        if image_bytes:
            image = Image.open(io.BytesIO(image_bytes))
            image_q = ImageQt.ImageQt(image)
            pixmap  =  QPixmap.fromImage(image_q)
            self.captcha_image.setPixmap(pixmap)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())