import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.63',
          }


print('Code is running. May take few minutes ...')


# fetcthing only all of the  products URLS
prod_urls = []
for page_num in range(1, 3):
    url = f'https://www.citiwide-online.com/categories/orient-classic-series?limit=72&page={page_num}'
    site = requests.get(url)
    soup = BeautifulSoup(site.content, 'lxml')
    prod_urls += ["https://www.citiwide-online.com"+x.find('a')['href'] for x in soup.findAll('product-item')]
    
    
name_array, original_price_array, discount_price_array = [], [], []
img_urls_array, description_html_array, description_text_array = [], [], []
prod_urls_array = []

# this function will scrap the products' pages and append information to above arrays
def scrapify(url):
    site = requests.get(url, headers=headers)
    soup = BeautifulSoup(site.content)
    title = soup.find('div', {'class':'title global-primary dark-primary'}).getText('', True)
    orignal_price = soup.find('div', {'class':'global-primary dark-primary price-regular price js-price price-crossed'}).getText('', True)
    discount_price = soup.find('div', {'class':'price-sale price js-price'}).getText('', True)
    description_text = soup.find('div', {'class':'global-secondary dark-secondary description-container'}).getText('', True)
    description_html = soup.find('div', {'class':'global-secondary dark-secondary description-container'})
    img_urls = []
    for temp in str(soup).split('detail_image_url')[1:]:
        img_urls.append(temp.split('?\\')[0][5:])
        
    
    name_array.append(title)
    original_price_array.append(orignal_price)
    discount_price_array.append(discount_price)
    description_text_array.append(description_text)
    description_html_array.append(description_html)
    img_urls_array.append(img_urls)
    prod_urls_array.append(url)
    
    

    
# for product_url in prod_urls[:5]:
#     scrapify(product_url, url)
    
# these 2 lines perform the above loop operation but does ~20 products in parallel simultaneously
pool = ThreadPool(20)
_ = pool.map(scrapify, prod_urls[:10])



#creating dataframe object
df = pd.DataFrame(columns=['Handle', 'Title', 'Description(HTML)', 'Description(text)','OriginalPrice',
                           'DiscountedPrice', 'ProductURL', 'Image Src', 'Image Position'
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
                'DiscountedPrice': discount_price_array[index],
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
                'OriginalPrice':  '',
                'DiscountedPrice': '',
                'ProductURL': '',
                'Image Src': src,
                'Image Position': i+1
            }, ignore_index = True)
            
            
df.to_csv('citywide - orient1.csv', index=False)

df.to_excel('citywide - orient1.xlsx', index=False)


print('\n\nResults saved in files. You may exit the code now')