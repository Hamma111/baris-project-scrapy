from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import openpyxl


options = Options()
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

dr = webdriver.Chrome(options=options)

dr.get('https://merchant.hepsiburada.com/v2/dashboard')
print('Attempting to log in')

sleep(0.8)
dr.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
sleep(0.4)
for x in 'First Sourcer':
    dr.find_element_by_id('login-username').send_keys(x)
    sleep(random.uniform(0.01, 0.4))

for x in 'Os@12345':
    dr.find_element_by_id('login-password').send_keys(x)
    sleep(random.uniform(0.01, 0.4))
sleep(0.5)
dr.find_element_by_id('submit-login').click()
sleep(1)

try:
    WebDriverWait(dr, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "dashboardContainer"))
    )
    print('Logged in successfully.')
except:
    print('Automated Login failed. Please try to log in manually')
    input('\n\nPress enter here when you have logged in')

try:
    WebDriverWait(dr, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "dashboardContainer"))
    )

except:
    input('The program couldnt detect that you have logged.\nPlease log in again and press enter here')

dr.get('https://merchant.hepsiburada.com/fulfilment/to-be-packed')