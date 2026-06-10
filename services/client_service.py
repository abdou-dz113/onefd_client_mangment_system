from database import Database, get_db
import re


db = get_db()


def table_query():
    result = db.tablequery()
    if result:
        return result
    else:
        return None

def is_valid(key,value):
        if key == "level_input_1":
            if int(value) >=0:
                return True
        elif key == "phone_number_input":
                return True
        else:
            return bool(value)

def validate_input(inputs):
        """
        checks for empty input fields
        get_filled=True : return {field name: input} of any filled input
        get_filled=False : return inputs only if all filled
        """
        is_input_valid = True
        valid_inputs = {}
        if inputs:
            for widget, value in inputs.items():
                if is_valid(widget, value):
                    valid_inputs[widget] = value
                else:
                    is_input_valid = False
        
        if valid_inputs:
            return is_input_valid, valid_inputs
        else: 
            return None, None



def if_changed(old_info, new_info):
    changed_info = {k: v for k, v in new_info.items() if old_info.get(k) != v}
    changed_info.update({"client_id": old_info.get("client_id")})
    return changed_info

def save_edit(changed_info):
    if isinstance(changed_info,dict):
        client_id = changed_info.get("client_id")
        changed_info.pop("client_id")
        if changed_info:
            db.update(client_id, changed_info)
            return True
        else:
            return False

def get_from_id (client_id):
    client_info = db.search({"id":client_id},level_text=False)
    if not client_info:
        print("Client Not Found.")
        return
    client_info = client_info[0]
    info_dict = {
                    'client_id':client_info[0],
                    'lastname':client_info[1],
                    'firstname':client_info[2],
                    'level':client_info[3],
                    'username_01':client_info[4],
                    'password_01':client_info[5],
                    'form_number':client_info[4][8:],
                    'username_02':client_info[6],
                    'password_02':client_info[7],
                    'ins_number':client_info[6][:11],
                    'phone_number':client_info[8],
                    'devoir_01':client_info[9],
                    'devoir_02':client_info[10],
                    'devoir_03':client_info[11],
                    'devoir_04':client_info[12],
                    'devoir_05':client_info[13]
                    }
    return info_dict 

def search(inputs):
    is_valid,input_dict = validate_input(inputs)
    if is_valid:
        return # so the user dont query all the forms at ones
    if input_dict:
        search_table = db.search(input_dict)
        return search_table

def search_by_id(client_id):
    result = db.search_by_id(client_id)
    if result:
        return result

def delete(client_id):
    result = db.delete(client_id)
    return result

def maptodb(valid_inputs):
    db_dict = {}
    for key, value in valid_inputs.items():
        if key == "login_username_input_1":
            db_dict.update({"username_01":value})
        elif key == "login_password_input_1":
            db_dict.update({"password_01":value})
        elif key == "lastname_input_1":
            db_dict.update({"lastname":value})
        elif key == "firstname_input_1":
            db_dict.update({"firstname":value})
        elif key == "phone_number_input":
            db_dict.update({"phone_number":value})
        elif key == "exams_password_input_1":
            db_dict.update({"username_02":value})
        elif key == "exams_username_input_1":
            db_dict.update({"password_02":value})
        elif key == "level_input_1":
            db_dict.update({"level":value})
    if db_dict:
        return db_dict
    else:
        return valid_inputs


def insert(valid_inputs):
    if isinstance(valid_inputs, dict):
        inputs = maptodb(valid_inputs)
        result = db.insert(inputs)
        return result

def clean_site_data(input_dict):
    site_data_map = {
        "lastname":"last_name",
        "firstname":"first_name",
        "username_02":"exams_username",
        "password_02":"exams_password",
    }
    levels_map = {"104":0,
                  "204":1,
                  "304":2,
                  "404":3,
                  "111":4,
                  "112":4,
                  "122":4,
                  "124":4,
                  "211":5,
                  "212":5,
                  "213":5,
                  "214":5,
                  "215":5,
                  "311":6,
                  "312":6,
                  "314":6,
                  "315":6,
                  "316":6,}
    new_dict = {}
    if input_dict:
        for key, val in site_data_map.items():
            new_dict.update({key:input_dict.get(val)})
        #level_rf = "".join(c for c in input_dict.get("level") if c.isdigit())
        level_text = input_dict.get("level")
        match_obj = re.match(r"\d\d\d",level_text)
        level_rf = str(match_obj.group())
        print(level_rf)
        level = levels_map.get(level_rf)

        new_dict.update({"level":level})
        print(new_dict)
        return new_dict
        
def validate_login_inputs(inputs):
    username = inputs.get("login_username_input_1")
    password = inputs.get("login_password_input_1")
    username_pattern = r"user-\d{2}-\d{5}"
    valid = False
    if re.fullmatch(username_pattern, username) and password != "" :
        valid = True

    return valid
