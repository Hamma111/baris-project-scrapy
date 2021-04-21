#!/usr/bin/env python
# coding: utf-8

# In[25]:


URL = 'https://www.banggood.com/Wholesale-Cleaning-Appliances-ca-9002.html?brand=1845'


# In[24]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# path = r"chromedriver.exe"

options = Options()
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome( options=options)


# In[26]:


driver.switch_to.window(driver.window_handles[0])
links_list = []

driver.get(URL)
html = driver.execute_script("return document.documentElement.outerHTML")

from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

links = soup.find('ul', {'class': 'goodlist cf'}).find_all('li')
for url in links:
    url = url.find('a')['href']
    links_list.append(url)

page_list = []

num_of_pages = soup.find('div', {'class': 'total'}).text
num_of_pages = [int(s) for s in str.split(num_of_pages) if s.isdigit()][0]
print(num_of_pages)


base_url = URL.split('.html')[0][:-1]

print()
print()
print("************ STARTING ************")
print()
import time

for i in range(1,num_of_pages+1):
    page = base_url + str(i) + '.html';
    print(page)
    driver.get(page)
    time.sleep(3)
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find('ul', {'class': 'goodlist cf'}).find_all('li')
    for url in links:
        url = url.find('a')['href']
        links_list.append(url)

print()
print("Total Pages",num_of_pages)
print("Total items",len(links_list))
print()


# In[27]:



items = {}
loop_counter = 0


# In[6]:


def scrape():
    global url
    global items
    global loop_counter

    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')


    title = soup.find('span', {'class': 'product-title-text'}).text
    print('Title:',title)

    try:
        brand = soup.find('div', {'class': 'reviewer-brand'}).a.text
    except:
        brand = ''
    print("Brand:",brand)

    price = soup.find('span', {'class': 'main-price'}).text
    print('Price:',price)

    image_list = []
    print('Images:')
    images = soup.find('ul', {'class': 'list cf'}).find_all('li')
    for image in images:
        image = image.a.img['src'].replace('other_items','large')
        image_list.append(image)
        print(image)


    specs = ''
    trim_found = False
    try:
        specs_html = soup.find('div', {'class': 'tab-cnt'})
        specs = soup.find('div', {'class': 'tab-cnt'}).text.split('Trim\nEngine')[1].strip()
        trim_found = True
    except:
        specs_html = ''
        print('Trim not found')
    if trim_found:
        try:
            specs = soup.find('div', {'class': 'tab-cnt'}).find_all('div')
            print('Inside extract')
            for element in specs:
                if 'Trim' in element.text:
                    element.extract()
                    break


            specs = soup.find('div', {'class': 'tab-cnt'}).text.strip()
            print('main specs found')
        except:

            specs_rows = soup.find('tbody').find_all('tr')#, {'class': 'tab-cnt'}).text.split('Specifications:')[1].strip()
            for c in specs_rows:
                specs+=c.text + '  '

    img_s = []
    for i in range(10):
        img_s.append('')

    for i in range(10):
        try:
            img_s[i] = image_list[i]
        except:
            img_s[i] = ''


    items[loop_counter] = [ title,
                            price,
                            brand,
                            img_s[0],
                            img_s[1],
                            img_s[2],
                            img_s[3],
                            img_s[4],
                            img_s[5],
                            img_s[6],
                            img_s[7],
                            img_s[8],
                            img_s[9],
                            specs,
                            specs_html,
                            url
                         ]
    loop_counter+=1


# In[28]:


next_page = 0
for url in links_list[loop_counter:3]:
	print(loop_counter,url)
	driver.get(url)
	try:
	    scrape()
	except Exception as e:
		print(e)
		print('************')
	print('--------------------------------------------------------')

import pandas as pd
df_links = pd.DataFrame.from_dict(
    items, orient='index',
    columns=["Title","Price","Brand","specs", "specs(HTML)","Link",
	"image1","image2","image3","image4", "image5","image6","image7","image8","image9","image10"]
)
df_links.to_csv("bangood_col_by_col.csv",  index = False)
