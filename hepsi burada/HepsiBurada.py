## libraries import
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
from multiprocessing.pool import ThreadPool


## headers to make requests look legitimate
headers = {'User-Agent': 'My User Agent 1.0'}


prod_urls, prod_ids, prod_skus, prod_in_stocks = [], [], [], []


for page_num in range(51)[:2]:
    url = f'https://www.hepsiburada.com/magaza/first-sourcer?sayfa={page_num}'    
    site = requests.get(url, headers=headers)
    soup = BeautifulSoup(site.content, 'lxml')
    print('extracting product URLs from page# ', page_num)
    for prod in soup.findAll('li', {'class':'search-item col lg-1 md-1 sm-1 custom-hover not-fashion-flex'}):
        prod_url = "https://www.hepsiburada.com"+prod.find('a', {'href':True})['href']
        prod_id = prod.find('a')['data-productid']
        prod_sku = prod.find('a')['data-sku']
        prod_in_stock = prod.find('a')['data-isinstock']

        prod_urls.append(prod_url); prod_ids.append(prod_id)
        prod_skus.append(prod_sku); prod_in_stocks.append(prod_in_stock)    
		
		
		
		
df1 = pd.DataFrame({
    'ProductURL': prod_urls,
    'ProductID': prod_ids,
    'ProductSKU': prod_skus,
    'ProductAvailability': prod_in_stocks
})

prod_urls = list(set(df1.ProductURL))


print('\n\n\n', 'A total of ', len(prod_urls), ' product URLs were extracted.')
print('Now visiting each products webpage individually. This may take 5-10 minuts')
print('(It is possible that few products may give an error but that should be ignored)\n')



titles, brands, prices, original_prices = [], [], [], []
img_urls1, img_urls2, img_urls3, img_urls4, img_urls5 = [], [], [], [], []
description_htmls, urls_done = [], []

def scrapify(url):
    try:
        site = requests.get(url, headers=headers)
        soup = BeautifulSoup(site.content)

        ## images URLs
        img_urls = ['N\A' for _ in range(5)]
        only_one_image = True
        for i, x in enumerate(soup.find('div', {'id':'productThumbnailsCarousel'}).findAll('img')[:5]):
            only_one_image = False
            temp = x['src'].split('/')
            temp[-2] = '1000'
            img_urls[i] = '/'.join(temp)
    #         print(img_urls[i])
        if only_one_image:
            img_urls[0] = soup.find('img', {'itemprop':'image'})['src']

        ## other product info 
        title = soup.find('h1', {'itemprop':'name', 'id':'product-name'}).getText('', True)
        print('1')
        brand = soup.find('span', {'class':'brand-name'}).getText('', True)
        print('2')
        price = soup.find('', {'itemprop':'price'}).getText('', True)
        print('3')
        original_price = soup.find('del', {'id':'originalPrice'}).getText('', True)
        print('4s')
        description_html = soup.find('div', {'id':'tabProductDesc'}) 

        titles.append(title); brands.append(brand); prices.append(price); original_prices.append(original_price)
        description_htmls.append(description_html)
        img_urls1.append(img_urls[0]); img_urls2.append(img_urls[1]); img_urls3.append(img_urls[2]);
        img_urls4.append(img_urls[3]); img_urls5.append(img_urls[4]);
        urls_done.append(url)
        print('.', end='')
        
        
    except Exception as ex:
        print(url, '==>>', ex)

pool = ThreadPool(4)
results = pool.map(scrapify, prod_urls[:3])

df2 = pd.DataFrame({
    'Title': titles,
    'Brand': brands,
    'Price': prices,
    'ProductURL': urls_done,
    'OriginalPrice': original_prices,
    'DescriptionHTML': description_htmls,
    'img_url1': img_urls1,
    'img_url2': img_urls2,
    'img_url3': img_urls3,
    'img_url4': img_urls4,
    'img_url5': img_urls5
}) 

df = pd.merge(df1, df2, on="ProductURL")
df = df.drop_duplicates().reset_index().drop(columns=['index'], axis=1)
df.to_csv('sample_hepsiburada.csv', index=False)

print('extraction completed successfully and stored results in sample_hepsiburada.csv')
input()
input()