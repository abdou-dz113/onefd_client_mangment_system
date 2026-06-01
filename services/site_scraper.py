import io
from PIL import Image
import requests
from bs4 import BeautifulSoup

url = "https://inscriptic.onefd.edu.dz/preinscription/auth/login"
url2 = "https://inscriptic.onefd.edu.dz/preinscription/Inscriptic"
url3 = "https://inscriptic.onefd.edu.dz/preinscription/Inscriptic/action"
url4 = "https://inscriptic.onefd.edu.dz/preinscription/download_pdf/imp_cert_inscription"

custom_header = {"user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.3"}

session = requests.Session()
r1 = session.get(url, headers=custom_header)

soup = BeautifulSoup(r1.content, "html.parser")

parent_div = soup.find("div", class_="image refresh")
captcha_tag = parent_div.find("img")
captcha_url = captcha_tag["src"]
captcha_raw = requests.get(captcha_url, stream=True)
print(captcha_url)
if captcha_raw.status_code == 200:
    image = Image.open(io.BytesIO(captcha_raw.content))
    image.show()

# username = input("USERNAME: ")
# password = input("PASSWORD: ")
captcha  = input("CAPTCHA: ")

payload= {
        "identity" :  "user-03-40260",
        "password" : "kc+56oLvR$N",
        "captcha"  :  captcha}
    
response = session.post(url,data=payload)
if response.status_code == 200:
    r2 = session.get(url2)
    soup = BeautifulSoup(r2.content, "html.parser")
    name= soup.find(id="prenomlat")["value"]
    last_name= soup.find(id="nomlat")["value"]
    print(f"{name} : {last_name}")


class WebLogin():
    def __init__(self):
        self.session = requests.session()
    
    def login_request(self,username,password,captcha):
        self.session.get(url, headers=custom_header)
        payload = {
            "identity" :  "user-03-40260",
            "password" : "kc+56oLvR$N",
            "captcha"  :  captcha}
        response = self.session.post(url,data=payload)
        

    def get_captcha(self):
        r = self.session.get(url, headers=custom_header)
        soup = BeautifulSoup(r.content, "html.parser")
        parent_div = soup.find("div", class_="image refresh")
        captcha_tag = parent_div.find("img")
        captcha_url = captcha_tag["src"]
        captcha_raw = requests.get(captcha_url, stream=True)
        return captcha_raw
    

