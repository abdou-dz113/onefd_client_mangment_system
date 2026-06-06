import io
from PIL import Image
import requests
from bs4 import BeautifulSoup
import time
from functools import wraps


url = "https://inscriptic.onefd.edu.dz/preinscription/auth/login"
url2 = "https://inscriptic.onefd.edu.dz/preinscription/Inscriptic"
url3 = "https://inscriptic.onefd.edu.dz/preinscription/Inscriptic/action"
url4 = "https://inscriptic.onefd.edu.dz/preinscription/download_pdf/imp_cert_inscription"
url5 = "https://inscriptic.onefd.edu.dz/preinscription/Auth/logout"
url6 = "https://inscriptic.onefd.edu.dz/preinscription/Confirmation_preinscriptic/wel"
refrech_captcha_url = "https://inscriptic.onefd.edu.dz/preinscription/aja_function/refresh_captcha"

custom_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }


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

def expect_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"function exited with the error: {e}")
            return None
    return wrapper

        


class WebLogin():
    def __init__(self):
        self.session = requests.session()
    
    def request(self):
        self.request = self.session.get(url, headers=custom_header)
        return self.request

    def login(self,username,password,captcha):
        payload = {
            "identity" :  username,
            "password" :  password,
            "captcha"  :  captcha}
        response = self.session.post(url,data=payload)
        return response
        

    def get_captcha(self):
        try:
            self.request()
            r = self.request
            soup = BeautifulSoup(r.content, "html.parser")
            parent_div = soup.find("div", class_="image refresh")
            captcha_tag = parent_div.find("img")
            captcha_url = captcha_tag["src"]
            captcha_raw = requests.get(captcha_url, stream=True)
            return captcha_raw.content
        except Exception as e:
            print(e)
    
    def refresh_captcha(self):

        r = self.session.post(refrech_captcha_url, headers=custom_header)
        if r.ok:
            soup = BeautifulSoup(r.content,"html.parser")
            img_url = soup.find("img")["src"]
            image_raw = requests.get(img_url, stream=False)
            return image_raw.content

    def get_info(self):
        form_map = site_form_map
        site_vals = {}
        try:
            request = self.session.get(url6, headers=custom_header)
            if request.ok:
                html = request.json()["valid"]
                soup = BeautifulSoup(html,"html.parser")
                for group in soup.select(".form-group"):
                    label = group.find("label")
                    inp   = group.find("input")
                    if label and inp:
                        field_name = label.get_text(strip=True)
                        field_value= inp.get("value")
                        site_vals.update({form_map.get(field_name):field_value})
                return site_vals
        except Exception as e:
            print(e)

    
if __name__ == "__main__":
    login = WebLogin()
    image_raw = login.get_captcha()
    img = Image.open(io.BytesIO(image_raw))
    img.show()
    username = "user-03-00024"
    password = "_mw0J*@x7Bq"
    captcha  = input("enter the captcha: ")
    logged_in = login.login(username,password,captcha)
    if logged_in:
        data = login.get_info()
        print(data)
