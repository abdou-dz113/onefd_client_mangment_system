import sqlite3

class Database():
    def __init__(self):
        self.connect = sqlite3.connect("app.db")
        self.cursor = self.connect.cursor()
        self.ceate_tables()

    def ceate_tables(self):
        #username_01,password_01,firstname,lastname,level,phone_number,username_02,password_02
        vals = [(0,"أولى متوسط"),(1,"ثانية متوسط"),(2,"ثالثة متوسط"),(3,"رابعة متوسط"),(4,"أولى ثانوي"),(5,"ثانية ثانوي"),(6,"ثالثة ثانوي"),]
        #ceate the table that contain the client data
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_01(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username_01 TEXT UNIQUE,
        password_01 TEXT UNIQUE,
        firstname TEXT,
        lastname TEXT,
        level INTEGER,
        phone_number TEXT,
        username_02 TEXT UNIQUE,
        password_02 TEXT UNIQUE
        )
        """)
        self.connect.commit()


        #create the level lookup table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS level_lookup(
        level_index INTEGER UNIQUE NOT NULL,
        level_text TEXT     
        )"""
        )
        insertlvl_sql = "INSERT INTO level_lookup (level_index, level_text) VALUES (?,?)"


    
    def tablequery(self):
        query = self.cursor.execute("""
        SELECT table_01.lastname, table_01.firstname, level_lookup.level_text, table_01.username_01, table_01.password_01, table_01.username_02, table_01.password_02, table_01.phone_number
        FROM table_01
        JOIN level_lookup ON table_01.level = level_lookup.level_index
        """)
        data = query.fetchall()
        return data

    def insert(self,user1,pass1,lname,fname,lvl,pn,user2,pass2):
        try:
            self.cursor.execute(
                """INSERT INTO table_01 (username_01,password_01,firstname,lastname,level,phone_number,username_02,password_02) VALUES (?,?,?,?,?,?,?,?)"""
                , (user1,pass1,lname,fname,lvl,pn,user2,pass2))
            self.connect.commit()
        except sqlite3.Error as e:
            print(f"Database error code: {e}")

    def search(self,expestion):
        search_term = f"%{expestion}%"
        self.cursor.execute("SELECT * FROM table_01 WHERE lastname LIKE  ? ",(search_term,))
        result = self.cursor.fetchall()
        return result

if __name__ == "__main__":
    db=Database()

