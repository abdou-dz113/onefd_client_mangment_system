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
    0:("غير منجز","#c0392b"),
    1:("منجز غير مدفوع","#e67e22"),
    2:("مدفوع غير منجز","#5b8fa8"),
    3:("منجز مدفوع","#27ae60"),
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
         }
         
         #QTableWidget::item {
            padding: 15px;
            border-bottom: 1px solid #f4f5f6;
            font-size: 12px;
            height: 20px;
            background-color: none;

         }

      """