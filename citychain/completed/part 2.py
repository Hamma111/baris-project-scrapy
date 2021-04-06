## Libraries imports
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import urllib.request
from multiprocessing.dummy import Pool as ThreadPool




## initializing empty arrays which will be populated by values later on
cases, straps, dials, movements, water_resists = [], [], [], [], []
product_urls_done = [] 
img_urls_1, img_urls_2, img_urls_3, img_urls_4, img_urls_5 = [], [], [], [], []




## This function scraps the data from indvidual product website
## This function will populate above arrays
def scrapFunc(url):
    try:
        site = requests.get(url)
        soup = BeautifulSoup(site.content)

        all_images_tags = soup.find('ul', {'id':"ulImgList"}).findAll('li')
        img_url_1 = all_images_tags[0].find('img')['src'].replace('48x57', '700x650')
        try:
            img_url_2 = all_images_tags[1].find('img')['src'].replace('48x57', '700x650')
        except:
            img_url_2 = 'N\A'
        try:
            img_url_3 = all_images_tags[2].find('img')['src'].replace('48x57', '700x650')
        except:
            img_url_3 = 'N\A'
        try:
            img_url_4 = all_images_tags[3].find('img')['src'].replace('48x57', '700x650')
        except:
            img_url_4 = 'N\A'
        try:
            img_url_5 = all_images_tags[4].find('img')['src'].replace('48x57', '700x650')
        except:
            img_url_5 = 'N\A'
    
        table1 = soup.findAll('table', {"class": "product-details-table"})[1]
        table1_text = table1.getText(separator=" ")

        ind1 = table1_text.find('CASE') + 5
        ind2 = table1_text.find('DIAL')
        case = table1_text[ind1:ind2].replace('\t', '').strip()

        ind1 = table1_text.find('DIAL') + 4
        ind2 = table1_text.find('STRAP')
        dial = table1_text[ind1:ind2].replace('\t', '').strip()

        ind1 = table1_text.find('STRAP') + 5
        strap = table1_text[ind1:].replace('\t', '').strip()

        try:
            table2 = soup.findAll('table', {"class": "product-details-table"})[2]
            table2_text = table2.getText(separator=" ")
            try:
                ind1 = table2_text.find('MOVEMENT')+8
                ind2 = table2_text.find('WATER RESISTANT')
                movement = table2_text[ind1:ind2].replace('\t', '').strip()
            except:
                movement = 'N\A'
                
            try:
                ind1 = table2_text.find('WATER RESISTANT')+18
                ind2 = table2_text.find('ESTIMATED')
                water_resist = table2_text[ind1:ind2].replace('\t', '').strip()
                if ind2 == -1:
                    water_resist = table2_text[ind1:].replace('\t', '').strip()
            except:
                water_resist = 'N\A'
        except:
            movement = 'N\A'
            water_resist = 'N\A'
    
        cases.append(case); dials.append(dial) ; straps.append(strap)
        movements.append(movement); water_resists.append(water_resist)
        product_urls_done.append(url)
        img_urls_1.append(img_url_1); img_urls_2.append(img_url_2); img_urls_3.append(img_url_3);
        img_urls_4.append(img_url_4); img_urls_5.append(img_url_5);

    except Exception as ex:
        print(url, '==>>', ex)






##path to where previous csv files of product categories are located.
base_path = ''



## main loop which will iterate through all the csv files
## This loop will also be creating the final csv files for each product category
for file in os.listdir(base_path)[:]:
    try:
        df1 = pd.read_csv(base_path + file)

        product_urls = list(df1['ProductURL'])

        cases, straps, dials, movements, water_resists = [], [], [], [], []
        product_urls_done = [] 
        img_urls_1, img_urls_2, img_urls_3, img_urls_4, img_urls_5 = [], [], [], [], []

        pool = ThreadPool(20)
        _ = pool.map(scrapFunc, product_urls)

        df2 = pd.DataFrame({
            'ProductURL': product_urls_done,
            'Case': cases,
            'Dial': dials,
            'Strap': straps,
            'Movement': movements,
            'WaterResistant': water_resists,
            'img_url_1': img_urls_1,
            'img_url_2': img_urls_2,
            'img_url_3': img_urls_3,
            'img_url_4': img_urls_4,
            'img_url_5': img_urls_5,
        })

        df = pd.merge(df1, df2, on="ProductURL")
        df.to_csv(file , index=False)
        
        del df1, df2, df
        
        print(file, " successfully scraped")
    
    except Exception as ex:
        print('!!!error occured!!! ', file, ex)
