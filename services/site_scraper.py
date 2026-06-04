import io
from PIL import Image
import requests
from bs4 import BeautifulSoup


url = "https://inscriptic.onefd.edu.dz/preinscription/auth/login"
url2 = "https://inscriptic.onefd.edu.dz/preinscription/Inscriptic"
url3 = "https://inscriptic.onefd.edu.dz/preinscription/Inscriptic/action"
url4 = "https://inscriptic.onefd.edu.dz/preinscription/download_pdf/imp_cert_inscription"
url5 = "https://inscriptic.onefd.edu.dz/preinscription/Auth/logout"
url6 = "https://inscriptic.onefd.edu.dz/preinscription/Confirmation_preinscriptic/wel"

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
# session = requests.Session()
# r1 = session.get(url, headers=custom_header)

# soup = BeautifulSoup(r1.content, "html.parser")

# parent_div = soup.find("div", class_="image refresh")
# captcha_tag = parent_div.find("img")
# captcha_url = captcha_tag["src"]
# captcha_raw = requests.get(captcha_url, stream=True)
# print(captcha_url)
# if captcha_raw.status_code == 200:
#     image = Image.open(io.BytesIO(captcha_raw.content))
#     image.show()

# # username = input("USERNAME: ")
# # password = input("PASSWORD: ")
# captcha  = input("CAPTCHA: ")

# payload= {
#         "identity" :  "user-03-40260",
#         "password" : "kc+56oLvR$N",
#         "captcha"  :  captcha}
    
# response = session.post(url,data=payload)
# if response.status_code == 200:
#     r2 = session.get(url2)
#     soup = BeautifulSoup(r2.content, "html.parser")
#     name= soup.find(id="prenomlat")["value"]
#     last_name= soup.find(id="nomlat")["value"]
#     print(f"{name} : {last_name}")


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
