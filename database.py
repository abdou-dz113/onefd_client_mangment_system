import sqlite3



_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
            _db_instance = Database()
    return _db_instance


class Database():
    def __init__(self):
        self.connect = sqlite3.connect("app.db")
        self.cursor = self.connect.cursor()
        self.create_tables()
        self.table_select_text = """
        SELECT 
            t.id,
            t.lastname,
            t.firstname,
            l.level_text,
            t.username_01,
            t.password_01,
            t.username_02,
            t.password_02,
            t.phone_number,
            t.devoir_01,
            t.devoir_02,
            t.devoir_03,
            t.devoir_04,
            t.devoir_05
            FROM table_01 t 
            INNER JOIN level_lookup l ON t.level = l.level_index   
        """


    def table_select(self,level_names=True):
        if level_names:
            table_select =  self.table_select_text
            return table_select
        else:
           table_select =   self.table_select_text.replace("l.level_text,","t.level,")
           table_select =   table_select.replace("INNER JOIN level_lookup l ON t.level = l.level_index","")
           return table_select


    def create_tables(self):
        #username_01,password_01,firstname,lastname,level,phone_number,username_02,password_02
        #create the table that contain the client data
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_01(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username_01 TEXT UNIQUE,
        password_01 TEXT ,
        firstname TEXT,
        lastname TEXT,
        level INTEGER,
        phone_number TEXT,
        username_02 TEXT UNIQUE,
        password_02 TEXT,
        devoir_01 INTGER DEFAULT 0,
        devoir_02 INTGER DEFAULT 0,
        devoir_03 INTGER DEFAULT 0,
        devoir_04 INTGER DEFAULT 0,
        devoir_05 INTGER DEFAULT 0,
        form_number TEXT,
        ins_number TEXT                     
        )
        """)
        self.connect.commit()

        #create the level lookup table
        vals = [(0,"أولى متوسط"),(1,"ثانية متوسط"),(2,"ثالثة متوسط"),(3,"رابعة متوسط"),(4,"أولى ثانوي"),(5,"ثانية ثانوي"),(6,"ثالثة ثانوي"),]
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS level_lookup(
        level_index INTEGER UNIQUE ,
        level_text TEXT     
        )"""
        )
        insertlvl_sql = "INSERT OR IGNORE INTO level_lookup (level_index, level_text) VALUES (?,?)"
        self.cursor.executemany(insertlvl_sql,vals)
        self.connect.commit()


    
    def tablequery(self):
        query = self.cursor.execute(self.table_select_text)
        data = query.fetchall()
        return data

    def insert(self,input_dict):
        """insert data to sql table: table_01"""
        try:
            self.cursor.execute(
                """INSERT INTO table_01 (username_01,password_01,firstname,lastname,level,phone_number,username_02,password_02) VALUES (?,?,?,?,?,?,?,?)"""
                , (
                    input_dict["username_01"],
                    input_dict["password_01"],
                    input_dict["firstname"],
                    input_dict["lastname"],
                    input_dict["level"],
                    input_dict["phone_number"],
                    input_dict["username_02"],
                    input_dict["password_02"]
                    
                ))
            self.connect.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error code: {e}")
            return False




    def delete(self,client_id):
        sql = """DELETE FROM table_01 WHERE id = ? """
        try:
            self.cursor.execute(sql,(client_id))
            self.connect.commit()
            return True 
        except sqlite3.Error as error:
            print(error)
            return  
 
    def search(self,search_params,level_text=True):
        table_select = self.table_select(level_text)
        conditions = []
        values = []

        if type(search_params) == type(dict()):
            for widget, value in search_params.items():
                if widget == "level" or widget == "id":
                    con = f"t.{widget} = ?"
                    val = str(value)
                else:
                    con = f"t.{widget} LIKE ?"
                    val =f"%{value}%"
                
                conditions.append(con) 
                values.append(val)

            sql = table_select + "WHERE "+" AND ".join(conditions)
            self.cursor.execute(sql,values)
            results = self.cursor.fetchall()
            return results

    def search_by_id(self,client_id):
        sql = self.table_select_text + " WHERE  id = " + str(client_id)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result

    def update(self,client_id,new_info):
        table_select= """UPDATE table_01 SET """
        conditions = []
        for name, value in new_info.items():
           if name not in ('ins_number','form_number'):
                conditions.append(name +" = \'"+str(value)+"\' ")
       
        sql = table_select + ", ".join(conditions) + f" WHERE id = {client_id}"
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except sqlite3.Error as e:
            return print(e)


        
if __name__ == "__main__":
    db=Database()
    db.cursor.execute("""ALTER TABLE table_01 ADD COLUMN ins_number TEXT """)
    db.connect.commit()



