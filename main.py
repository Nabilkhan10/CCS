from turtle import title
import requests
from bs4 import BeautifulSoup
from colored import stylize, fg
from datetime import datetime as dt
import time
from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.action_chains import ActionChains
import warnings
class CCS:
    def __init__(self):
        warnings.filterwarnings('ignore')
        warnings.warn('DelftStack')
        warnings.warn('Do not show this message')
        self.username = 'CCS DATA TOOL'
        self.log("Enter Starting Date(MM/DD/YYYY)", color='yellow')
        self.startDate = input("")
        self.log("Enter End Date(MM/DD/YYYY)", color='yellow')
        self.endDate = input("")
        self.session = requests.Session()
    def log(self, *args, **kwargs):
        color = kwargs['color'] if 'color' in kwargs else None
        logs = [x + '\n' for x in args]
        for log in logs:
                print(
                    f"{dt.now().strftime('%H:%M:%S.%f')[:-3]} | " + stylize('\033[1m ' + 'Task[' + self.username + "]" + log + '\033[0m', fg(color)) if color else log, flush=True)
    def login(self):
        self.log("Logging In To Medlabs Online Portal", color='yellow')
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--profile-directory=Default')
            chrome_options.add_argument("--disable-plugins-discovery");
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
            driver.set_window_size(800,800)
            driver.set_window_position(0,0)
            driver.get("http://medlabonlineportal.com/")
            time.sleep(1)
            username = driver.find_element(by=By.XPATH, value='//*[@id="cphLogin_txtUserName"]')
            username.send_keys("fnz")
            password = driver.find_element(by=By.XPATH, value='//*[@id="cphLogin_txtPassword"]')
            password.send_keys("Bluediamond376")
            password.send_keys(Keys.RETURN)
            if 'Laboratory Requisition Home' in driver.page_source:
                self.log("Successfully Logged In", color='green')
                driver.get('http://medlabonlineportal.com/zCovidTestGrid.aspx')
                self.searchForDates(driver)
            else:
                self.log("Error Loggin In To Portal", color='yellow')
        except Exception as e:
            self.log("Error", color='red')
            print(e)
    def searchForDates(self, driver):
        self.log(f"Getting Covid Orders Data From {self.startDate} To {self.endDate}", color='yellow')
        fromDatePath = driver.find_element(by=By.XPATH, value='//*[@id="ContentPlaceHolder1_txtdatefrom"]')
        fromDatePath.clear()
        fromDatePath.send_keys(self.startDate)
        toDatePath = driver.find_element(by=By.XPATH, value='//*[@id="ContentPlaceHolder1_txtdateto"]')
        toDatePath.clear()
        toDatePath.send_keys(self.endDate)
        toDatePath.send_keys(Keys.RETURN)
        self.pageSource = driver.page_source
        self.getData(driver)
    def getData(self, driver):
        try:
            soup = BeautifulSoup(self.pageSource, 'html.parser')
            x = soup.find_all("a", {"style": "color:DarkOliveGreen;"})
            f = 0
            for x in x:
                f = f + 1
            self.log(f"{str(f)} Results Found", color='green')
            self.log("Gathering Patient Data", color='yellow')
            x = soup.find_all("a", {"style": "color:DarkOliveGreen;"})
            self.dataSheet = f"First Name, Last Name, Date Of Birth, Gender, Address, City, State, Zipcode, Date Of Service, Patient Phone Number, Patient Email(Optional), Insurance Name, Insurance ID, Insurance Group ID\n"
            doneNumber = 0
            for x in x:
                try:
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'max-age=0',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Cookie': 'ASP.NET_SessionId=xn4cjiib1bgbdto1oq4z4ztr',
                        'Origin': 'http://medlabonlineportal.com',
                        'Referer': 'http://medlabonlineportal.com/zCovidTestGrid.aspx',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                        }
                    response = requests.get(url=f"http://medlabonlineportal.com/zCovidTResult.aspx?CovidTestId={x['href'].replace('zCovidTResult.aspx?CovidTestId=','')}", headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    w = soup.find_all("span", {"class": "form-control-plaintext"})
                    doneNumber = doneNumber + 1
                    self.log(f"Successfully Loaded Data For Order#{x['href'].replace('zCovidTResult.aspx?CovidTestId=','')} - {str(doneNumber)}/{str(f)}", color='green')
                    self.dataSheet = self.dataSheet + f"{w[2].text.strip().strip()},{w[3].text.strip()},{w[5].text.strip()},{w[6].text.strip()},{w[9].text.strip()},{w[10].text.strip()},{w[11].text.strip()},{w[12].text.strip()},{w[23].text.strip()},{w[7].text.strip()},{w[8].text.strip()},{w[15].text.strip()},{w[16].text.strip()},{w[17].text.strip()}\n"
                except Exception as e:
                    self.log("Error", color='red')
            self.log(f"Successfully Listed Data For {f} Patients", color='green')
            self.log("Creating CSV File", color='yellow')
            nameOfFile = int(time.time())
            with open(f'{str(nameOfFile)}.csv', 'w') as f:
                f.write(self.dataSheet)
            self.log(f"Succesfully Created New CSV File - {str(nameOfFile)}.csv", color='green')
            driver.close()
        except Exception as e:
            self.log("Error", color='red')
CCS().login()         
