## libraries import
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
from multiprocessing.pool import ThreadPool

## to make our requesting agent look like a real agent
headers = {'User-Agent': 'My User Agent 1.0'}

## inializing empty arrays which will be populated when data will scraped
prod_urls, prod_ids, prod_skus, prod_in_stocks = [], [], [], []
new_prices, original_prices = [], []

## loop which will extract Products URLs and some more info from the 50 desired pages
for page_num in range(51)[:]:
    url = f'https://www.hepsiburada.com/magaza/first-sourcer?sayfa={page_num}'

    site = requests.get(url, headers=headers)
    soup = BeautifulSoup(site.content, 'lxml')

    print('extracting product URLs from page# ', page_num)
    for prod in soup.findAll('li', {'class': 'search-item col lg-1 md-1 sm-1 custom-hover not-fashion-flex'}):
        prod_url = "https://www.hepsiburada.com" + prod.find('a', {'href': True})['href']
        prod_id = prod.find('a')['data-productid']
        prod_sku = prod.find('a')['data-sku']
        prod_in_stock = prod.find('a')['data-isinstock']

        try:
            original_price = prod.find('del', {'class': 'price old product-old-price'}).getText('', True)
        except:
            original_price = 'N\A'

        try:
            new_price = prod.find('span', {'class': 'price product-price'}).getText('', True)
        except:
            new_price = prod.find('span', {'class': 'price old product-old-price'}).getText('', True)

        prod_urls.append(prod_url)
        prod_ids.append(prod_id)
        prod_skus.append(prod_sku)
        prod_in_stocks.append(prod_in_stock)
        new_prices.append(new_price)
        original_prices.append(original_price)


## creating dataframe of previously scraped data entries
df1 = pd.DataFrame({
    'ProductURL': prod_urls,
    'ProductID': prod_ids,
    'ProductSKU': prod_skus,
    'ProductAvailability': prod_in_stocks,
    'NewPrice': new_prices,
    'OriginalPrice': original_prices
})

## taking produtct URLs separately
prod_urls = list(set(df1.ProductURL))


print('\n\n\n', 'A total of ', len(prod_urls), ' product URLs were extracted.')
print('Now visiting each products webpage individually. This may take 5-10 minuts')
print('(It is possible that few products may give an error but that should be ignored)\n\n\nProcessing..')


## inializing empty arrays which will be populated when data will scraped
titles, brands = [], []
img_urls1, img_urls2, img_urls3, img_urls4, img_urls5 = [], [], [], [], []
description_htmls, urls_done = [], []

## function to extract data and add into above arrays
def scrapify(url):
    try:
        site = requests.get(url, headers=headers)
        soup = BeautifulSoup(site.content, 'lxml')

        # images URLs
        img_urls = ['N\A' for _ in range(5)]
        only_one_image = True
        for i, x in enumerate(soup.find('div', {'id': 'productThumbnailsCarousel'}).findAll('img')[:5]):
            only_one_image = False
            temp = x['src'].split('/')
            temp[-2] = '1000'
            img_urls[i] = '/'.join(temp)

        if only_one_image:
            img_urls[0] = soup.find('img', {'itemprop': 'image'})['src']

        ## other product info
        title = soup.find('h1', {'itemprop': 'name', 'id': 'product-name'}).getText('', True)
        brand = soup.find('span', {'class': 'brand-name'}).getText('', True)
        description_html = soup.find('div', {'id': 'tabProductDesc'})

        titles.append(title)
        brands.append(brand)
        description_htmls.append(description_html)
        img_urls1.append(img_urls[0])
        img_urls2.append(img_urls[1])
        img_urls3.append(img_urls[2])
        img_urls4.append(img_urls[3])
        img_urls5.append(img_urls[4])
        urls_done.append(url)
        print('.', end='')


    except Exception as ex:
        print(url, '==>>', ex)


## Using multi-threading(4 requests at a time) to speed up the scraping process
pool = ThreadPool(4)
results = pool.map(scrapify, prod_urls[:])

## creating another dataframe out of previously scraped data
df2 = pd.DataFrame({
    'Title': titles,
    'Brand': brands,
    'ProductURL': urls_done,
    'DescriptionHTML': description_htmls,
    'img_url1': img_urls1,
    'img_url2': img_urls2,
    'img_url3': img_urls3,
    'img_url4': img_urls4,
    'img_url5': img_urls5
})

## merging the two dataframe and creating a mutual complete dataframe
df = pd.merge(df1, df2, on="ProductURL")
df = df.drop_duplicates().reset_index().drop(columns=['index'], axis=1)


## there were some URLs with faulty HTML description. deleting those URLs
faulty_urls = ['https://www.hepsiburada.com/garmin-instinct-akilli-saat-ates-kirmizisi-p-HBV00000M9EFA?magaza=First%20Sourcer',
              'https://www.hepsiburada.com/garmin-instinct-akilli-saat-grafit-siyah-p-HBV00000M9EF9?magaza=First%20Sourcer',
              'https://www.hepsiburada.com/garmin-instinct-akilli-saat-tundra-beyazi-p-HBV00000M9EFE?magaza=First%20Sourcer',
              'https://www.hepsiburada.com/garmin-instinct-akilli-saat-deniz-kopugu-p-HBV00000M9EFB?magaza=First%20Sourcer',
              'https://www.hepsiburada.com/garmin-vivoactive-3-muzik-akilli-saat-p-HBV00000CJHAR?magaza=First%20Sourcer',
             ]
for i, x in enumerate(list(df.ProductURL)):
    if x in faulty_urls:
        df.drop([i], axis=0, inplace=True)



## CREATING THE CSV FILE ACCORDING TO THE SHOPIFY IMPORT TEMPLATE
def f(row):
    if row['img_url1'] != 'N\A':
        val1 = row['img_url1'] + ' '
    else:
        val1 = ''

    if row['img_url2'] != 'N\A':
        val2 = row['img_url2'] + ' '
    else:
        val2 = ''

    if row['img_url3'] != 'N\A':
        val3 = row['img_url3'] + ' '
    else:
        val3 = ''

    if row['img_url4'] != 'N\A':
        val4 = row['img_url4'] + ' '
    else:
        val4 = ''

    if row['img_url5'] != 'N\A':
        val5 = row['img_url5']
    else:
        val5 = ''

    return (val1 + val2 + val3 + val4 + val5).strip()


df['Images'] = ''
df['Images'] = df.apply(f, axis=1)

all_images_urls = []
for x in df['Images']:
    all_images_urls.append(x.split(' ') )

new_df = pd.DataFrame(columns=['Handle', 'Title', 'Brand', 'Description(HTML)', 'NewPrice',
                             'OriginalPrice', 'ProductAvailibility', 'ProductID', 'ProductSKU',
                             'ProductURL', 'Image Src', 'Image Position'
                            ])

for index, srcs in enumerate(all_images_urls):
    for i, x in enumerate(srcs):
        if i== 0:
            new_df = new_df.append({
                'Handle': df.loc[index, 'Title'],
                'Title':df.loc[index, 'Title'],
                'Brand': df.loc[index, 'Brand'],
                'Description(HTML)':df.loc[index, 'DescriptionHTML'],
                'NewPrice': df.loc[index, 'NewPrice'],
                'OriginalPrice': df.loc[index, 'OriginalPrice'],
                'ProductAvailibility': df.loc[index, 'ProductAvailability'],
                'ProductID':df.loc[index, 'ProductID'] ,
                'ProductSKU':df.loc[index, 'ProductSKU'] ,
                'ProductURL':df.loc[index, 'ProductURL'],
                'Image Src':x,
                'Image Position': i+1
            }, ignore_index = True)
        else:
            new_df = new_df.append({
                'Handle': df.loc[index, 'Title'],
                'Title':'',
                'Brand': '',
                'Description(HTML)':'',
                'NewPrice': '',
                'OriginalPrice': '',
                'ProductAvailibility': '',
                'ProductID':'' ,
                'ProductSKU':'' ,
                'ProductURL':'',
                'Image Src':x,
                'Image Position': i+1
            }, ignore_index = True)

new_df.to_csv('HepsiBurada_complete.csv', index=False)

print('\n\nExtraction completed successfully and results stored in HepsiBurada_complete.csv')
input()
input()