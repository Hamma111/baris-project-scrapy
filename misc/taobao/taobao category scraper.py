import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
#from mtranslate import translate
#import http.cookies
#import re
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
#from fake_useragent import UserAgent
from time import sleep

cookies = pd.read_json('cookies.json')

def scrapify(site, url, vend_num):
    soup1 = BeautifulSoup(site, 'lxml')
    if 'detail.tmall.com' in url:
        name = soup1.find('div', {'class':'tb-detail-hd'}).getText('\n', True)
        original_price = soup1.find('span', {'class':'tm-price'}).getText('', True)
        try:
            discount_price = soup1.findAll('span', {'class':'tm-price'})[1].getText('', True)
        except:
            discount_price = ''
        img_urls = [x['src'].replace('400x400', '800x800').replace('jpg_50x50', 'jpg_800x800')
                    for x in soup1.find('ul', {'id': 'J_UlThumb'}).findAll('img', {'src': True})]
        description_html = soup1.find('div', {'id': 'attributes'})
        description_text = soup1.find('div', {'id': 'attributes'}).getText('\n', True)
        vendor = vendors_array[vend_num]
    
    
    elif 'item.taobao.com' in url:
        name = soup1.find('h3', {'class': 'tb-main-title'}).getText('', True)
        try:
            discount_price = soup1.find('em', {'class': "tb-rmb-num", 'id':True}).getText('', True)
        except:
            discount_price = ''
        original_price = soup1.find('em', {'class': "tb-rmb-num", 'id':False}).getText('', True)
            
        img_urls = [x['src'].replace('400x400', '800x800').replace('50x50', '800x800').replace('60x60', '800x800')
                    for x in soup1.find('ul', {'id': 'J_UlThumb'}).findAll('img', {'src': True})]
        description_html = soup1.find('div', {'id': 'attributes'})
        description_text = soup1.find('div', {'id': 'attributes'}).getText('\n', True)
        vendor = vendors_array[vend_num]
        
    else:
        print('weird url => ', url)
        return
    
    name_array.append(name)
    vendors_final_array.append(vendor)
    original_price_array.append(original_price)
    discount_price_array.append(discount_price) 
    img_urls_array.append(img_urls)
    description_html_array.append(description_html)
    description_text_array.append(description_text)


options = Options()
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
dr = webdriver.Chrome(options=options)

dr.set_page_load_timeout(6)	

try:
    dr.get('https://s.taobao.com/search?spm=a21wu.241046-global.6977698868.164.4103b6cbbgbVCY&q=%E9%A5%B0%E5%93%81DIY&acm=lb-zebra-241046-2075394.1003.4.1812236&scm=1003.4.lb-zebra-241046-2075394.OTHER_15206383875223_1812236&bcoffset=6&ntoffset=6&p4ppushleft=1%2C48&s=0')
except TimeoutException:
    pass
	
for index, cookie in cookies.drop(['httpOnly', 'sameSite', 'session', 'storeId', 'id', 'hostOnly', 'expirationDate'], axis=1).iterrows():
    dr.add_cookie(dict(cookie))
	
url = 'https://s.taobao.com/search?q=camping+tents&type=p&tmhkh5=&spm=a21wu.241046-global.a2227oh.d100&from=sea_1_searchbutton&catId=100'
try:
    dr.get(url)
except TimeoutException:
    pass
	
	
_ = os.system('cls')
_ = os.system('cls')


NUM_PAGES = int(input('Please navigate to the desired category.\n\nPlease enter the number of pages you would like scraped: '))

prod_urls_array = []
vendors_array = []
name_array, original_price_array, discount_price_array = [], [], []
img_urls_array, description_html_array, description_text_array = [], [], []
vendors_final_array, prod_urls_final_array = [], []

for i in range(NUM_PAGES):
    for _ in range(7):
        dr.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        sleep(0.5)
    sleep(1)
    
    soup = BeautifulSoup(dr.page_source, 'lxml')
    prods = soup.find('div', {'id':'mainsrp-itemlist'}).findAll('div', {"data-category": "auctions"})
    prod_urls = [x.find('a')['href'] for x in prods]
    vendors = [x.getText('', True) for x in soup.findAll('div', {'class': 'shop'})]
    prod_urls_array += prod_urls
    vendors_array += vendors
    
    dr.find_element_by_xpath('//li[@class="item next"]').click() 
    WebDriverWait(dr, 10).until(
            EC.visibility_of_element_located((By.XPATH, f'//span[@class="num" and contains(text(),{i+2})]'))
        )		
		


for vend_num, url in enumerate(prod_urls_array[:]):
    if "https" not in url:
        url = "https:" + url
    try:
        dr.get(url)
#         sleep(5)
        
#         try:
#             popup_dialogue = WebDriverWait(dr, 5).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "baxia-dialog-close"))
#             )
#             popup_dialogue.click()
#             popup_dialogue = WebDriverWait(dr, 5).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "baxia-dialog-close"))
#             )
#             popup_dialogue.click()
#             print('reached1')
#         except:
#             print('s')
    except TimeoutException:
        sleep(5)
    try:
      #  print('reached2')
        WebDriverWait(dr, 15).until(
            EC.presence_of_element_located((By.ID, "J_UlThumb"))
        )
        WebDriverWait(dr, 15).until(
            EC.presence_of_element_located((By.ID, "attributes"))
        )
      #  print('reached3')
        WebDriverWait(dr, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tb-detail-hd"))
        )
        WebDriverWait(dr, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tm-price"))
        )
       # print('reache4')
    except:
        sleep(2)
        try:
            WebDriverWait(dr, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tb-main-title"))
            )
            WebDriverWait(dr, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tb-rmb-num"))
            )
        except Exception as ex:
            print('skipped because taobao did its thing\n')
            #print(ex)
            continue
           
    scrapify(dr.page_source, dr.current_url, vend_num)
    print('scraped\n')
#     break




df = pd.DataFrame(columns=['Handle', 'Title', 'Description(HTML)', 'Description(text)','OriginalPrice',
                           'DiscountPrice', 'ProductURL', 'Image Src', 'Image Position'
                            ])
#preparing according to shopify import template
for index, imgs in enumerate(img_urls_array):
    for i, src in enumerate(imgs):
        if i== 0:
            df = df.append({
                'Handle': name_array[index],
                'Title': name_array[index],
                'Description(HTML)': description_html_array[index],
                'Description(text)': description_text_array[index],
                'OriginalPrice': original_price_array[index],
                'DiscountPrice': discount_price_array[index],
                'ProductURL': prod_urls_array[index],
                'Image Src': src,
                'Image Position': i+1
            }, ignore_index = True)
        else:
            df = df.append({
                'Handle': name_array[index],
                'Title': '',
                'Description(HTML)': '',
                'Description(text)': '',
                'OriginalPrice': '',
                'DiscountPrice': '',
                'ProductURL': '',
                'Image Src': src,
                'Image Position': i+1
            }, ignore_index = True)
            
			
df['Image Src'] = df['Image Src'].apply(lambda x: x.replace('60x60', '800x800').replace('400x400', '800x800').replace('50x50', '800x800'))
writer = pd.ExcelWriter(r'file.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})
df.to_excel(writer, index=False)
writer.close()