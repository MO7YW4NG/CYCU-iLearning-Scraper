import os
import aiohttp
import getpass
import json
import hashlib
from Crypto.Cipher import DES
import base64
from bs4 import BeautifulSoup
import urllib
import time
import asyncio

url = "https://i-learning.cycu.edu.tw/"

# MD5 Encrypt
def md5_encode(input_string) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()

# DES Encrypt ECB NoPadding
def des_encode(key:str, data) -> str:
    cipher = DES.new(key.encode('utf-8'), DES.MODE_ECB)
    encrypted_data = cipher.encrypt(data.encode('utf-8'))
    return str(base64.encodebytes(encrypted_data),encoding='utf-8').replace("\n","")

async def fetch_login_key(session):
    while True:
        async with session.get(url + "sys/door/re_gen_loginkey.php?xajax=reGenLoginKey", headers=headers) as response:
            res = await response.text()
            if "loginForm.login_key.value = \"" in res:
                return res.split("loginForm.login_key.value = \"")[1].split("\"")[0]

async def login(session, id, pwd, loginKey):
    async with session.post(url + "login.php", headers=headers, data={
        "username": id,
        "pwd": pwd,
        "password": "*" * len(pwd),
        "login_key": loginKey,
        "encrypt_pwd": des_encode(md5_encode(pwd)[:4] + loginKey[:4], pwd + " " * 6),
    }) as response:
        res = await response.text()
        if "lang=\"big5" in res:
            print("登入失敗，請重新再試!")
            return False
    return True

async def fetch_courses(session):
    async with session.get(url + "learn/mooc_sysbar.php", headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        courses = {
            option["value"]: option.text
            for child in soup.select("optgroup[label=\"正式生、旁聽生\"]")
            for option in child.find_all("option")
        }
        return courses

async def fetch_hrefs(session, course_id):
    async with session.get(url + f"xmlapi/index.php?action=my-course-path-info&cid={course_id}", headers=headers) as response:
        items = json.loads(await response.text())
        hrefs = []
        if items['code'] == 0:
            def search_hrefs(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == 'href' and (value.endswith('.pdf') or value.endswith('.pptx')):
                            hrefs.append(value)
                        elif isinstance(value, (dict, list)):
                            search_hrefs(value)
                elif isinstance(data, list):
                    for item in data:
                        search_hrefs(item)
            search_hrefs(items['data']['path']['item'])
        return hrefs

async def download_pdf(session, href, course_name):
    async with session.get(href, headers=headers) as response:
        if response.status != 200: 
            return
        # Retrieve file name
        content_disposition = response.headers.get('Content-Disposition')
        filename = content_disposition.split('filename=')[-1].strip('"') if content_disposition else os.path.basename(str(response.url))
        filename = urllib.parse.unquote(filename)
        save_path = f"pdf/{course_name}/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, filename)
        if os.path.exists(file_path):
            return
        # Write PDF with chunks
        with open(file_path, 'wb') as file:
            async for chunk in response.content.iter_chunked(8192):
                if chunk:
                    file.write(chunk)
                    
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"}

async def main():
    os.system("title CYCU-iLearning-Scraper")
    print("<!!! 尊重版權/著作權 尊重版權/著作權 尊重版權/著作權 !!!>")
    
    id = input("輸入您的學號：")
    pwd = getpass.getpass("輸入您的itouch密碼：")
    
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        login_key = await fetch_login_key(session)
        if not await login(session, id, pwd, login_key):
            return
        
        courses = await fetch_courses(session)
            
        print("下載中... ")
        start = time.time()
        
        for course_id, course_name in courses.items():
            hrefs = await fetch_hrefs(session, course_id)
            tasks = [ download_pdf(session, href, course_name) for href in hrefs ]
            await asyncio.gather(*tasks)
        
        print(f"下載完成! 耗時: {time.time() - start}s")
        os.system("pause")

if __name__ == "__main__":
    asyncio.run(main())