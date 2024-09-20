import requests
from bs4 import BeautifulSoup
import os
import json
import time
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

url = "https://odeme.atauni.edu.tr/yemekhane2.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/2 Firefox/123.0"
}

def makeText(text: list):
    bosListe = list()
    for i in text:
        i = i.text
        bosListe.append(i)
    return bosListe

def makeDic(text: list):
    dicList = dict()
    for i in range(0, len(text), 2):
        dicList[text[i]] = text[i + 1]
    return dicList

def path():
    try:
        appData_path = os.environ.get("APPDATA")
        dirName = "AtauniYemek"
        newDirPath = os.path.join(appData_path, dirName)
        os.makedirs(newDirPath, exist_ok=True)
    except FileExistsError:
        newDirPath = os.path.join(appData_path, dirName)
    except Exception:
        exit()
    return newDirPath

def useData():
    pathDir = path()
    formData = dict()
    filePath = os.path.join(pathDir, "data.txt")
    if os.path.exists(filePath):
        with open(filePath, 'r') as data:
            formData = json.loads(data.read())
        return formData
    else:
        tc = input("TC Kimlik Numaranız:")
        dogumTarihi = input("Doğum Tarihinizi Giriniz:")
        with open(filePath, "w") as data:
            formData["bakiye_tc"] = tc
            formData["dogum_tarihi"] = dogumTarihi
            data.write(json.dumps(formData))
        return formData

def get_default_browser():
    if sys.platform.startswith('win'):

        registry_keys = [
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice",
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice"
        ]
        for key in registry_keys:
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as reg_key:
                    value, _ = winreg.QueryValueEx(reg_key, 'ProgId')
                    return value.split('.')[0]
            except Exception as e:
                pass

    elif sys.platform == 'darwin':
        try:
            plist = subprocess.check_output(
                ['defaults', 'read', '-g', 'com.apple.LaunchServices/com.apple.launchservices.secure'],
                stderr=subprocess.DEVNULL
            )
            plist = plist.decode('utf-8').split('\n')
            for line in plist:
                if 'LSHandlerRoleAll' in line and 'http' in line:
                    return line.split('.')[-1]
        except Exception as e:
            pass

    elif sys.platform.startswith('linux'):
        try:
            subprocess.check_output(['xdg-settings', 'get', 'default-web-browser'])
        except Exception as e:
            pass

    return None

def yemekMenu():
    try:
        html = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html, "html.parser")
        liste = soup.find("div", {"id": "yemekListe"})
        listeH4 = liste.find_all("h4")
        tarih = [makeText(listeH4[0]), makeText(listeH4[2])]
        listeDiv = liste.find_all("div", {"class": "table-responsive"})
        yemek = [makeDic(makeText(listeDiv[0].find_all("td"))), makeDic(makeText(listeDiv[2].find_all("td")))]

        for i in range(len(tarih)):
            print(tarih[i][0])
            for key, value in yemek[i].items():
                print(f"{key}: {value}")
            print()
    except IndexError:
        try:
            html = requests.get(url, headers=headers).content
            soup = BeautifulSoup(html, "html.parser")
            liste = soup.find("div", {"id": "yemekListe"})
            listeH4 = liste.find_all("h4")
            tarih = makeText(listeH4[0])
            listeDiv = liste.find_all("div", {"class": "table-responsive"})
            yemek = makeDic(makeText(listeDiv[0].find_all("td")))
            for i in range(1):
                print(tarih[0])
                for key, value in yemek.items():
                    print(f"{key}: {value}")
                print()
        except IndexError:
            print("Yemek Bilgisi Girilmemiş!")
        except requests.exceptions.ConnectionError:
            print("Lütfen Bağlantınızı Kontrol Edin!")
            exit()
        except Exception:
            exit()

    except requests.exceptions.ConnectionError:
        print("Lütfen Bağlantınızı Kontrol Edin!")
        exit()
    except Exception:
        exit()

def bakiyeSorgula(tc: str, dogumTarihi: str):
    try:
        formData = dict()
        url = "https://odeme.atauni.edu.tr/OdemeIslem2.php"
        headers = {'fonksiyon': 'BakiyeSorgula'}
        formData["bakiye_tc"] = tc
        formData["dogum_tarihi"] = dogumTarihi
        response = requests.post(url, headers=headers, data=formData)
        response_json = response.json()
        bakiye = response_json.get("bakiye")
        print(f"Bakiyeniz {bakiye} TL")
    except requests.exceptions.ConnectionError:
        print("Lütfen Bağlantınızı Kontrol Edin!")
        exit()
    except  Exception:
        exit()

def bakiyeYukle(default_browser):
    if "chrome" in default_browser.lower():
        driver = webdriver.Chrome()
        driver.get(url)
        driver.find_element(By.CLASS_NAME, "btn-primary").click()
        time.sleep(3600)
    elif "firefox" in default_browser.lower():
        driver = webdriver.Firefox()
        driver.get(url)
        driver.find_element(By.CLASS_NAME, "btn-primary").click()
        time.sleep(3600)
    elif "edge" in default_browser.lower():
        driver = webdriver.Edge()
        driver.get(url)
        driver.find_element(By.CLASS_NAME, "btn-primary").click()
        time.sleep(3600)
    else:
        driver = webdriver.Edge()
        driver.get(url)
        driver.find_element(By.CLASS_NAME, "btn-primary").click()
        time.sleep(3600)

def main():
    useData()

    yemekMenu()

    formData = useData()
    tc = formData["bakiye_tc"]
    dogumTarihi = formData["dogum_tarihi"]
    bakiyeSorgula(tc, dogumTarihi)
    try:
        bakiyeFlag = input("Bakiye Yüklemek İster Misiniz?(E/H)")
        if bakiyeFlag.lower() == "e":
            try:
                default_browser = get_default_browser()
                bakiyeYukle(default_browser)
            except TypeError:
                print("Lütfen Bağlantınızı Kontrol Edin!")
                exit()
            except Exception:
                exit()
        elif bakiyeFlag.lower() == "h":
            print("Çıkış Yapılıyor...")
            exit()
        else:
            print("Hatalı Giriş! Çıkış Yapılıyor...")
            exit()
    except KeyboardInterrupt:
        exit()
    except  Exception:
        exit()

if __name__ == '__main__':
    main()
