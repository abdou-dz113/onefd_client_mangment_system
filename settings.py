mainwinui = "modern_ui.ui"
table_headers = ["id",
               "Last Name",
               "First Name",
               "Level",
               "Login Username",
               "Login Password",
               "Exams Username",
               "Exams Password",
               "Phone Number",
               "Exame 01",
               "Exame 02",
               "Exame 03",
               "Exame 04",
               "Exame 05"]

level_map ={
    0:"أولى متوسط",
    1:"ثانية متوسط",
    2:"ثالثة متوسط",
    3:"رابعة متوسط",
    4:"أولى ثانوي",
    5:"ثانية ثانوي",
    6:"ثالثة ثانوي",
    }

level_colors ={
   "أولى متوسط":("#eef2ff","#5839d8"),
   "ثانية متوسط":("#f0f9ff","#026aa9"),
   "ثالثة متوسط":("#f0f9ff","#026aa8"),
   "رابعة متوسط":("#f5f3ff","#7008e7"),
   "أولى ثانوي":("#ecfdf5","#007a55"),
   "ثالثة ثانوي":("#fff1f2","#c70036"),
   "ثانية ثانوي":("#fffbeb","#d87c16")
}

color_fallback = ("#f0f0f0","#6c6f72")


site_form_map ={
   "اللقب": "last_name",
   "الإسم" : "first_name",
   "العنوان": "addr",
   "القسم": "level",
   "رقم الإستمارة": "form_number",
   "رقم التسجيل": "insc_number",
   "رقم الترتيب": "num",
   "نوع الدروس" : "lesson_type",
   "اسم المستخدم :": "exams_username",
   "كلمة المرور :":"exams_password",
}

exams_progress_dict= {
   0:("غير منجز"),
   1:("منجز غير مدفوع"),
   2:("مدفوع غير منجز"),
   3:("منجز مدفوع"),
}
exams_ui_color = {
   0:("#c0392b","#ffe5e3"),
   1:("#e67e22","#ffeede"),
   2:("#5b8fa8","#ecf9ff"),
   3:("#27ae60","#ecfff4"),
}


tabel_css = """
         QTabelWidget{

         }
         QHeaderView::section:horizontal{
            background-color: #f7f9fb;
            color: #64748b;
            border: none;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: bold;
            border-bottom: 1px solid #e3e6e9;
            border-top: 1px solid #e3e6e9;
         }
         
         #QTableWidget::item {
            padding: 15px;
            border-bottom: 1px solid #f4f5f6;
            font-size: 12px;
            height: 20px;
            background-color: none;

            }
         QScrollBar:vertical {
         background-color: #F5F5F5;
         width: 14px;
         margin: 16px 0 16px 0;
         border: 1px solid #DCDCDC;
      }

         /* The scroll thumb/handle */
         QScrollBar::handle:vertical {
            background-color: #C0C0C0;
            min-height: 20px;
            border-radius: 4px;
         }

         /* Thumb hover state */
         QScrollBar::handle:vertical:hover {
            background-color: #A8A8A8;
         }

         /* Thumb pressed state */
         QScrollBar::handle:vertical:pressed {
            background-color: #787878;
         }

         /* The top arrow button */
         QScrollBar::sub-line:vertical {
            border: 1px solid #DCDCDC;
            background-color: #F5F5F5;
            height: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
         }

         /* The bottom arrow button */
         QScrollBar::add-line:vertical {
            border: 1px solid #DCDCDC;
            background-color: #F5F5F5;
            height: 16px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
         }

         /* Style the arrows inside the buttons (Optional) */
         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            width: 6px;
            height: 6px;
            background-color: #666666;
         }

         /* Hide the track background above and below the thumb */
         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
         }

         """

