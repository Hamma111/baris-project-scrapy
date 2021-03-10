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
import json
import shutil
from pathlib import Path


## setting global variables. These may be changed when needed manually when needed
USERNAME = 'First Sourcer'
PASSWORD = 'Os@12345'
DOWNLOAD_FOLDER_NAME = "Proformas"
PDF_DOWNLOAD_PATH = os.getcwd() + '\\' + DOWNLOAD_FOLDER_NAME + os.path.sep
SYSTEM_DOWNLOAD_FOLDER = str(Path.home() / "Downloads")
EXCEL_FILE_NAME = 'HepsiBurada Packed.xlsx'

# initating excel file
if not os.path.exists(EXCEL_FILE_NAME):
    df = pd.DataFrame(columns=['Customer Name Unpacked', 'Order No', 'Product Name', 'Product Price',
                               'Delivery Number', 'Customer Name Packed', 'Receiver Name', 'Telephone Number',
                               'TCKN', 'Detailed Address', 'City - Region', 'Invoice Saved'
                               ])
    df.to_excel(EXCEL_FILE_NAME, index=False)
else:
    df = pd.read_excel(EXCEL_FILE_NAME)


if not os.path.exists(PDF_DOWNLOAD_PATH):
    os.mkdir(PDF_DOWNLOAD_PATH)

## defining a function to load entire page i.e. go to the end of the page by scrolling systematically
def scrollToBottom():
    last_height = dr.execute_script('return document.body.scrollHeight')
    while True:
        dr.find_element_by_tag_name('body').send_keys(Keys.END)
        sleep(0.75)
        new_height = dr.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height
    sleep(2)
    last_height = dr.execute_script('return document.body.scrollHeight')
    while True:
        dr.find_element_by_tag_name('body').send_keys(Keys.END)
        sleep(0.75)
        new_height = dr.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height



## initiating an instance of Google Chrome
options = Options()
settings = {"recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
            "selectedDestinationId": "Save as PDF", "version": 2}
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),}
options.add_experimental_option('prefs', prefs)
options.add_argument('--kiosk-printing')
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
for x in USERNAME:
    dr.find_element_by_id('login-username').send_keys(x)
    sleep(random.uniform(0.01, 0.2))

for x in PASSWORD:
    dr.find_element_by_id('login-password').send_keys(x)
    sleep(random.uniform(0.01, 0.2))
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
sleep(2)
dr.switch_to.active_element.send_keys(Keys.ESCAPE)
sleep(1)
scrollToBottom()

## getting UNPACKED data
soup = BeautifulSoup(dr.page_source, 'lxml')

customer_name_array_unpack, order_no_array_unpack = [], []
prod_name_array_unpack, price_array_unpack = [], []

unpackeds = soup.findAll('div', {'class': 'order-row orders-page__item'})

for item in unpackeds:
    customer_name = item.find(text='Müşteri Bilgileri').next.text
    order_no = item.find(text='Sipariş No').next.text
    prod_name = item.find('span', {'class': 'product-card__name'}).getText('', True)
    price = item.find('span', {'class': 'summary-row__total-price__amount'}).getText('', True)

    customer_name_array_unpack.append(customer_name)
    order_no_array_unpack.append(order_no)
    prod_name_array_unpack.append(prod_name)
    price_array_unpack.append(price)

print('\n PLEASE PACK THE ITEMS\n')
_ = input('Press enter here when you are done')


## going to PACKED data and comparing UNPACKED and extracting relevant products' information
dr.get('https://merchant.hepsiburada.com/fulfilment/ready-to-ship')
scrollToBottom()
customer_name_array_pack, delivery_no_array_pack, index_array_pack = [], [], []
pdf_name_array = []
soup = BeautifulSoup(dr.page_source, 'lxml')
packeds = soup.findAll('div', {'class': 'order-row orders-page__item'})


for index_unpack, customer_name_unpack in enumerate(customer_name_array_unpack):
    for index_pack, item in enumerate(packeds):
        customer_name_pack = item.find(text='Müşteri Bilgileri').next.text
        delivery_no = item.find(text='Teslimat No').next.text
        prod_name_pack = item.find('span', {'class': 'product-card__name'}).getText('', True)
        price_pack = item.find('span', {'class': 'summary-row__total-price__amount'}).getText('', True)

        # making certain search criteria so our unpacked products matches correctly with the packed ones
        if customer_name_pack == customer_name_unpack:
            if price_pack == price_array_unpack[index_unpack]:
                if prod_name_pack == prod_name_array_unpack[index_unpack]:
                    print('extracting ', customer_name_pack, '.. ', end='')

                    # clicking
                    dr.find_elements_by_class_name('summary-row__order-info')[index_pack].click()
                    WebDriverWait(dr, 15).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "order-detail__info-and-action"))
                    )
                    sleep(3)


                    # comparing order numbers to be 100% sure than packed and unpacked order matches
                    soup_ = BeautifulSoup(dr.page_source, 'lxml')
                    soup_.find(text='Sipariş Numarası')
                    order_no_pack = soup_.findAll(text='Sipariş Numarası')[-1].next.find('span').text
                    if order_no_pack != order_no_array_unpack[index_unpack]:
                        continue

                    # click on "Proforma Görüntüle/Yazdır" => to save performa
                    dr.find_element_by_xpath("//button[@class='solo-button solo-button--small solo-button--style-ghost']").click()
                    sleep(3)
                    #wait for print to load
                    WebDriverWait(dr, 15).until(
                        EC.visibility_of_element_located(
                            (By.XPATH,
                             "//button[@class='solo-button print-proforma-label__actions__button solo-button--style-primary']"))
                    )
                    sleep(2)

                    # saving source html which will be scraped for individual values at the end of loop
                    soup = BeautifulSoup(dr.page_source, 'lxml')

                    #clikc on Yazdir button => print
                    dr.find_element_by_xpath("//button[@class='solo-button print-proforma-label__actions__button solo-button--style-primary']").click()
                    sleep(4)
                    # wait for print to finish downloading
                    cancel_button = WebDriverWait(dr, 15).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//button[@class='solo-modal__header__close-button']"))
                    )
                    sleep(4)
                    cancel_button.click()
                    sleep(4)
                    dr.find_elements_by_class_name('summary-row__order-info')[index_pack].click()
                    sleep(4)

                    pdf_name = f'{customer_name_pack} - {order_no_pack}.pdf'
                    pdf_name_array.append(pdf_name)

                    receiver_name = soup.find(text='Recipient').next.getText('', True)
                    telephone_number = soup.find(text='Phone Number').next.getText('', True)
                    tckn = soup.find(text='Identity number').next.getText('', True)
                    detailed_address = soup.find(text='Delivery Adress').next.getText(', ', True)
                    city_region = soup.find(text='District & Province').next.getText(', ', True)

                    df = df.append({
                        # unpacked
                        'Customer Name Unpacked': customer_name_unpack,
                        'Order No': order_no_array_unpack[index_unpack],
                        'Product Name': prod_name_array_unpack[index_unpack],
                        'Product Price': price_array_unpack[index_unpack],

                        # packed
                        'Delivery Number': delivery_no,
                        'Customer Name Packed': customer_name_pack,
                        'Receiver Name': receiver_name,
                        'Telephone Number': telephone_number,
                        'TCKN': tckn,
                        'Detailed Address': detailed_address,
                        'City - Region': city_region,
                        'Invoice Saved': pdf_name
                    }, ignore_index=True)

                    print('complete')


df.to_excel(EXCEL_FILE_NAME, index=False)


## To move downloaded files from downloads to our pdf folder
pdf_in_dwnlds = [x for x in os.listdir(SYSTEM_DOWNLOAD_FOLDER) if "Kargoya Teslim Edilecek Siparişler - Hepsiburada" in x]
temps = sorted(pdf_in_dwnlds)
pdf_in_dwnlds = []
pdf_in_dwnlds.append(temps[-1])
pdf_in_dwnlds += temps[:-1]

for i, x in enumerate(pdf_in_dwnlds):
    source = SYSTEM_DOWNLOAD_FOLDER + '\\' + x
    destination = PDF_DOWNLOAD_PATH + pdf_name_array[i]
    shutil.move(source, destination)

print('\nData extracted and downloaded the pdf file successfully.')

