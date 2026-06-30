import sys
import io
from PIL import Image, ImageQt
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenu, QMessageBox, QLineEdit, QComboBox,QLabel,QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView,QDialog,QVBoxLayout,QGridLayout,QWidget,QAbstractItemView,QStyledItemDelegate,QStyle
)
from PyQt6.QtCore import Qt,QRect,QSize,QThread,pyqtSignal,QObject,QEvent,QRectF
from PyQt6.QtGui import QPen,QBrush, QColor, QPixmap, QIcon, QPainter
import resources_rc
import settings as s
from services import client_service as cs
from services.site_scraper import WebLogin


def debug_func(func,):
    def wrapper(*arg,**kwarg):
        print(f"running {func.__name__}")
        func(*arg)
        print(f"finshed running {func.__name__}")
    return wrapper

class Pill_Delegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(option.rect).adjusted(4,4,-4,-4)
        painter.save()
        text = index.data().strip()
        bg,fg = s.level_colors.get(text, s.color_fallback)
        pen = QPen(QColor(fg))
        brush = QBrush(QColor(bg))
        
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(rect,20,20)
        painter.drawText(
                        option.rect,
                        Qt.AlignmentFlag.AlignCenter,
                        str(index.data()),          
                )
        painter.restore()


class ExamDelegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(option.rect).adjusted(4,4,-4,-4)
        painter.save()
        try:
            text = int(index.data())
        except ValueError:
            print("value error")
        fg,bg = s.exams_ui_color.get(text, s.color_fallback)
        label = s.exams_progress_dict.get(text, "###")
        pen = QPen(QColor(fg))
        brush = QBrush(QColor(bg))
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(rect,20,20)
        painter.drawText(
            option.rect,
            Qt.AlignmentFlag.AlignCenter,
            str(label)
        )
        painter.restore()

#__________Action Delegates ______________

btnw = 50
btnh = 26
gap = 6

def _btn_rect(cell):
    total_w = btnw *2 +gap
    x = cell.x() + (cell.width() - total_w) //2
    y = cell.y() + (cell.height() - btnh) //2
    edit_rect = QRect(x,y,btnw,btnh)
    delete_rect = QRect(x+btnw+gap,y,btnw,btnh)
    return edit_rect,delete_rect



class Actions_Delegates(QStyledItemDelegate):
    edit = pyqtSignal(int)
    delete = pyqtSignal(int)


    def paint(self, painter, option, index):
        painter.save()
        row = index.row()
        edit_rect, delete_rect = _btn_rect(option.rect)

        self._draw_btn(painter,edit_rect,"EDIT","blue",row)
        self._draw_btn(painter,delete_rect,"DELETE","red",row)
        painter.restore()
        
    def _draw_btn(self,painter,rect,text,color,row):
        bg = QColor(color)
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawRoundedRect(rect, 4, 4)
 
        # Label
        painter.setPen(QColor("white"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonRelease:
            edit_rect, delete_rect = _btn_rect(option.rect)
            pos = event.pos()
            if edit_rect.contains(pos):
                self.edit.emit(index.row())
                return True
            if delete_rect.contains(pos):
                self.delete.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(s.mainwinui,self)
        self.session = WebLogin()
        self.table_1 = TabelWidget(s.table_headers, parent=self)
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
        self.get_from_site_button.clicked.connect(self.open_dialog)



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
  
    

    def get_fields(self):
        current_page = self.stackedWidget.currentWidget()
        if current_page:
            self.widgets = current_page.findChildren((QLineEdit, QComboBox))
            self.widgets_map = {w.objectName():w for w in self.widgets}
       


    def load_table(self):
        data = cs.table_query()
        self.table_1.fill_table(data)



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
            if widget_name not in filled_froms.keys():
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
                else:
                    continue
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
    
    def open_dialog(self):
        valid = cs.validate_login_inputs(self.get_input())
        if valid:
            dialog = CustomDialog(parent=self)
            dialog.exec()
        else:
            print("input not valid")

    def open_edit_client(self, client_id):
        self.stackedWidget.setCurrentIndex(1)
        self.new_client_2.setChecked(True)
        self.get_fields()
        client_info = cs.get_from_id(client_id)
        if not client_info:
            return
        self._editing_client_id = client_id
        field_map = {
        "lastname_input_2":         client_info.get("lastname"),
        "firstname_input_2":        client_info.get("firstname"),
        "level_input_2":            client_info.get("level",-1),
        "login_username_input_2":   client_info.get("username_01"),
        "login_password_input_2":   client_info.get("password_01"),
        "exams_username_input_2":   client_info.get("username_02"),
        "exams_password_input_2":   client_info.get("password_02"),
        "phone_number_input_2":     client_info.get("phone_number","not found"),
        "form_number_label_2":      client_info.get("form_number","not found"),
        "inscription_number_input": client_info.get("ins_number", "not found")

        }
        for widget_name, value in field_map.items():
            widget = self.widgets_map.get(widget_name)
            if isinstance(widget, QLineEdit) and value is not None:
                widget.setText(str(value))
            if isinstance(widget,QComboBox):
                if widget_name == "level_input_2":
                    widget.setCurrentIndex(value)

        #____ exams status ____________________________
        exams_fields_map = {
            "paid_full_checkbox" :client_info.get("paid_in_full",0),
            "exam_1"             :client_info.get("exam_1"),
            "exam_2"             :client_info.get("exam_2"),
            "exam_3"             :client_info.get("exam_3"),
            "exam_4"             :client_info.get("exam_4"),
            "exam_5"             :client_info.get("exam_5"),
        }
        
        exams_ui_frame = self.findChild(QWidget,"exams_status_frame")
        if exams_ui_frame:
            exams_comboxes =exams_ui_frame.findChildren(QComboBox)
            if exams_comboxes:
                for cbox in exams_comboxes:
                    name = cbox.objectName()
                    index = client_info.get(name,-1)
                    cbox.setCurrentIndex(index)
        
        paid_in_full = self.findChild(QCheckBox,"paid_full_checkbox")
        if paid_in_full:
            paid_in_full_status = exams_fields_map.get("paid_full_checkbox")

        if paid_in_full_status:
            paid_in_full.setChecked(True)




class CaptchaWorker(QThread):
    captcha_ready = pyqtSignal(object)  # emits raw bytes or None

    def __init__(self, session):
        super().__init__()
        self.session = session

    def run(self):
        captcha_raw = self.session.refresh_captcha()
        self.captcha_ready.emit(captcha_raw)


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("web login")
        uic.loadUi("captcha_dialogbox_ui.ui", self)
        self.loadinfo()
        self.loadcaptcha()

    def loadinfo(self):
        parent = self.parent()
        info = parent.get_input()
        self.username.setText(info.get("login_username_input_1"))
        self.password.setText(info.get("login_password_input_1"))

    def loadcaptcha(self):
        # Show a placeholder while loading
        self.captcha_label.setText("Loading captcha...")

        self._worker = CaptchaWorker(self.parent().session)
        self._worker.captcha_ready.connect(self._on_captcha_ready)
        self._worker.start()

    def _on_captcha_ready(self, captcha_raw):
        if captcha_raw:
            image = Image.open(io.BytesIO(captcha_raw))
            imageqt = ImageQt.ImageQt(image)
            pixmap = QPixmap.fromImage(imageqt)
            self.captcha_label.setPixmap(pixmap)
        else:
            self.captcha_label.setText("Failed to load captcha.") 
    def login(self):
        username = self.username.text()
        password = self.password.text()
        captcha = self.captcha.text()
        if all((username,password,captcha)):
            response = self.parent().session.login(username,password,captcha)
            if response:
                self.frame.setHidden()
            



class TabelWidget(QTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.init_table_settings()
        
        self.setStyleSheet(s.tabel_css)

    def init_table_settings(self):
        self.main_window = self._get_main_window()
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.setAlternatingRowColors(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        horizontal_header = self.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.hide_columns(hide=True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.verticalHeader().setDefaultSectionSize(40)

        self.set_clients_number()
        

        self.set_cols_delegate()

        self.setSortingEnabled(True)

    def set_cols_delegate(self):
        exams_cols = (9,10,11,12,13)
        self.exam_delgate = ExamDelegate()
        self.pill_delegate = Pill_Delegate()
        self.action_delegate = Actions_Delegates()
        self.setItemDelegateForColumn(3,self.pill_delegate)
        for i in exams_cols:
            self.setItemDelegateForColumn(i,self.exam_delgate)
        self.setItemDelegateForColumn(14,self.action_delegate)

        #______ connect delgate signals to handlers
        self.action_delegate.edit.connect(self._on_edit_row)
        self.action_delegate.delete.connect(self._on_delete_row)

    def _get_main_window(self) -> QMainWindow:
        widget = self.parent()
        while widget is not None:
            if isinstance(widget,QMainWindow):
                return widget
            widget = widget.parent()
        return None

    def set_clients_number(self):
        if self.main_window:
            label = self.main_window.findChild(QLabel,"client_num_label_1")
            if label:
                label.setText(f"Clients: {self.rowCount()}")

    def _on_edit_row(self,row):
        client_id = int(self.item(row,0).text())
        if self.main_window:
            self.main_window.open_edit_client(client_id)

    def _on_delete_row(self,row):
        client_id = int(self.item(row,0).text())
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete Client ID: {client_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if cs.delete(client_id):
                self.removeRow(row)
                self.set_clients_number()



    def hide_columns(self, hide=True):
        hiden_columns = (0,5,6,7,4)
        for column in hiden_columns:
            self.setColumnHidden(column,hide)

    def item_gen(self,col_idx,col_val):
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
        clients_number = len(data_matrix)

        self.setRowCount(clients_number)

        self.horizontalHeader().setVisible(True)
        self.setSortingEnabled(False)
        for row_idx, row_data in enumerate(data_matrix):
            for col_idx, col_data in enumerate(row_data):
                table_item = self.item_gen(col_idx,col_data)
                self.setItem(row_idx, col_idx, table_item)


    
        self.set_clients_number()
    


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())