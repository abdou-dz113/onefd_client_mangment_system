from database import Database, get_db


db = get_db()


def table_query():
    result = db.tablequery()
    if result:
        return result

def is_valid(key,value):
        if key == "level":
            if value >=0:
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

def insert(valid_inputs):
    if isinstance(valid_inputs, dict):
        form_number = valid_inputs.get("username_01")[8:]
        ins_number  = valid_inputs.get("username_01")[:11]
        valid_inputs.update({"form_number":form_number})
        valid_inputs.update({"ins_number":ins_number})

        result = db.insert(valid_inputs)
        return result


        