## necessary libraries needed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import requests
import cv2



## to make browser look like a real browser
options = Options()
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
dr = webdriver.Chrome(options=options)



## visiting the website and waiting for 10 seconds to load everything
link = 'https://www.citychain.com.hk/en/forhim'
dr.get(link)
sleep(10)




## extracting attributes of products
soup = BeautifulSoup(dr.page_source)

items = soup.findAll('div', {"class": "w_pro_pic22 pro_letter"})
titles = [x.text for x in soup.findAll('div', {'class': 'w_pro_text22'})]
prod_ids = [x.text for x in soup.findAll('div', {'class': 'w_pro_bh17'})]
original_prices = []
sale_prices = [] 
for x in soup.findAll('div', {'class': 'w_pro_price22'}):
    try:
        original_prices.append(x.find('del').text)
    except:
        try:
            original_prices.append(x.find('dd').text.strip())
        except:
            original_prices.append('N\A')
    try:
        sale_prices.append(x.find('dt').text)
    except:
        sale_prices.append('N\A')
prod_urls = ["https://www.citychain.com.hk" + x.find('a')['href'] for x in 
             soup.findAll('figure', {'class':"col-xs-6 w_pro_list22_box"})]


## creating a dataframe for csv file        
dff = pd.DataFrame({
    'ProductName': titles,
    'ProductID': prod_ids,
    'OriginalPrice': original_prices,
    'SalePrice': sale_prices,
    'ProductURL': prod_urls,
})




## saving the csv files for a particular category
categ_name = 'driver_watch.csv'
dff.to_csv(categ_name, index=False) 
