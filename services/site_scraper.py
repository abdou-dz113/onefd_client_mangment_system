import io
from PIL import Image
import requests
from bs4 import BeautifulSoup
import json

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
        

    def get_captcha(self,):
        r = self.request
        soup = BeautifulSoup(r.content, "html.parser")
        parent_div = soup.find("div", class_="image refresh")
        captcha_tag = parent_div.find("img")
        captcha_url = captcha_tag["src"]
        captcha_raw = requests.get(captcha_url, stream=True)
        return captcha_raw.content

    def get_info(self):
        r = self.session.get(url2, headers=custom_header)
        soup = BeautifulSoup(r.content,"html.parser")
        try:
            first_parent = soup.find("div",class_="row form-group")
            print(first_parent)
            try:
                last_name_tag = first_parent.find("input",id="nom")
                first_name_tag = first_parent.find("input",id="prenom")
                level_tag = first_parent.find("input",id="icode")
                print(last_name_tag)
                print(first_name_tag)
                print(level_tag)
            except Exception as e:
                print(e)

        except Exception as e:
            print(e)

def test1():
    login = WebLogin()
    login.request()
    image = Image.open(io.BytesIO(login.get_captcha()))
    image.show()
    username = input("username: ")
    password = input("password: ")
    captcha = input("captcha: ")
    r = login.login(username,password,captcha)
    if r.ok:
        print("--- logged in ---")
        r2 = login.session.get(url6,headers= custom_header)
        if r2.status_code == 200:
            data = r2.json()
            client_data_html = data.get("valid")
            soup = BeautifulSoup(client_data_html,"html.parser")
            inputs = {}
            for group in soup.select(".form-group"):
                label = group.find("label")
                inp = group.find("input")
                if label and inp:
                    print(
                        label.get_text(strip=True),
                        "\t:\t",
                        inp.get("value", "")
                    )
                with open("res.html","w",encoding="utf-8") as file:
                    file.write(soup.prettify())
def test2():
    with open("res.html","r",encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    
    
if __name__ == "__main__":
    test2()
