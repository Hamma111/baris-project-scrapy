"""
Read Me!

This file contains the complete end to end code for extracting Hepsi Burada website in Turkish.
This code is faster and more reliable as compared to English extraction.

It's a better practice to run this code separately in 2 Steps:
Step 1: Extract all the links to the 'product_links.csv' file first by running 'link_extractor(url=url)' alone.
Step 2: Extract all the products from the 'product_links.csv' file into 'product_info.csv' and 'product_info.csv'
by running 'products_extractor()' alone.

Last tested : 21-12-2021

"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


path = '/Users/barissonmez/Desktop/Onesourcer/Python/chromedriver'

option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_argument("--lang=en")
option.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})

driver = webdriver.Chrome(executable_path=path, options=option)


def link_extractor(url):
    driver.get(url)
    print('Please wait while the page loads and extracts links...')
    time.sleep(4)
    print('It may take a while...')

    if len(driver.find_elements(By.ID, 'pagination')) > 0:
        paginator_path()
    else:
        scroll_path()


def scroll_path():
    for i in range(5000):
        element = driver.find_element(By.XPATH, "//*[contains(text(), 'Toplam')]")
        _ = element.location_once_scrolled_into_view
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.UP)
        time.sleep(4)

    count_pages = 5000
    try:
        while driver.find_element(By.XPATH, "//*[contains(text(), 'Daha fazla ürün göster')]"):
            driver.find_element(By.XPATH, "//*[contains(text(), 'Daha fazla ürün göster')]").click()
            time.sleep(4)
            count_pages = count_pages + 1
            print(f'Pages Loaded: {count_pages}')
    except:
        pass

    print(
        f'All Pages Loaded Successfully!\n Total Links To Be Expected: {count_pages * 24}\nEstimated Time: {count_pages * 0.14} minutes')

    products = driver.find_elements(By.CLASS_NAME, 'productListContent-item')
    print(f'Extracting {len(products)} product links...')
    product_list = []
    count_link = 0

    for product in products:
        link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
        title = product.find_element(By.TAG_NAME, 'a').get_attribute('title')
        product_list.append({
            'Title': title,
            'Link': link
        })
        count_link = count_link + 1
        print(f'Total Links Extracted: {count_link} ')

    print('Extraction of product links complete!')

    df = pd.DataFrame(product_list)
    print('Exporting product links to file...')
    df.to_csv('productlinks.csv', index=False)
    print('Saved file as productlinks.csv')

    return


def paginator_path():
    product_list = []
    count_pages = 1
    try:
        for i in range(2, 51):
            time.sleep(3)
            count_pages = count_pages + 1
            print(f'Total Pages Loaded: {count_pages}')
            product_batch = []
            products = driver.find_element(By.XPATH, '//ul[@class="product-list results-container do-flex  list"]') \
                .find_elements(By.TAG_NAME, 'li')

            for product in products:
                link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                title = product.find_element(By.TAG_NAME, 'h3').get_attribute('title')
                product_batch.append({
                    'Title': title,
                    'Link': link
                })

            product_list = product_list + product_batch
            driver.find_element(By.XPATH, '//*[@id="pagination"]'). \
                find_element(By.XPATH, f'//a[@class="page-{i} "]').click()
    except:
        pass
    print('Pages loaded successfully...\nExtraction of product links complete!')

    df = pd.DataFrame(product_list)
    print('Exporting product links to file...')
    df.to_csv('productlinks.csv', index=False)
    print('Saved file as productlinks.csv')

    return


def product_extractor(link):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    r = session.get(link, headers=headers)
    soup = BeautifulSoup(r.content)
    soup.prettify()

    name = soup.find('span', class_='product-name').text.strip()
    brand = soup.find('span', class_='brand-name').text.strip()
    info = soup.find('div', id="tabProductDesc")
    original_price = soup.find('del', id="originalPrice").text.strip()
    new_price = soup.find('span', attrs={"data-bind": "markupText:'currentPriceBeforePoint'"}).text.strip() \
                + ',' + soup.find('span',
                                  attrs={"data-bind": "markupText:'currentPriceAfterPoint'"}).text.strip() + 'TL'
    try:
        sku = soup.find('div', id="productTechSpecContainer").find('th', string="Stok Kodu").parent.find(
            'td').text.strip()
    except:
        sku = soup.find('div', id="productTechSpecContainer").find('th', string="Stock code").parent.find(
            'td').text.strip()
    images_html = soup.find('div', id="productDetailsCarousel").find_all('source', class_="product-image",
                                                                         type="image/jpeg")
    images = []

    for image_html in images_html:
        try:

            image_url1 = image_html['srcset'].replace('1x', '').replace('2x', '').strip()
            image_url = image_url1.split(' ,')[0]
            images.append(image_url)

        except:
            image_url = image_html['data-srcset'].replace('1x', '').replace('2x', '').strip()
            images.append(image_url)

    product = {
        'Title': name,
        'Brand': brand,
        'Description': info,
        'OriginalPrice': original_price,
        'NewPrice': new_price,
        'ProductSKU': sku,
        'ProductURL': link

    }

    if len(images) > 1:
        images_sec = ";".join(images[1:])
    else:
        images_sec = None
    product_sec = {
        'Title': name,
        'Brand': brand,
        'Description': info,
        'OriginalPrice': original_price,
        'NewPrice': new_price,
        'ProductSKU': sku,
        'ProductURL': link,
        'MainImage': images[0],
        'ExtraImages': images_sec

    }

    image_position = []
    pos = 0
    for image in images:
        pos = pos + 1
        image_position.append(pos)

    df1 = pd.DataFrame([product])
    df2 = pd.DataFrame({
        'ImageSrc': images,
        'ImagePosition': image_position
    })
    product = pd.concat([df1, df2], axis=1)
    # print(f'{name} successfully extracted...')
    product_sec = pd.DataFrame([product_sec])
    print(name)

    return product, product_sec


def products_extractor():
    df = pd.read_csv('productlinks.csv')
    links = df['Link'].tolist()[:5000]
    print(f'{len(links)} products found...\nExtracting Links...\nPlease Wait...')
    products = pd.DataFrame()
    products_sec = pd.DataFrame()
    count = 0
    for link in links:
        product, product_sec = product_extractor(link)
        products = pd.concat([products, product], axis=0)
        products_sec = pd.concat([products_sec, product_sec], axis=0)
        count = count + 1
        print(f'Extracted {count} out of {len(links)} products.. ')
    df = pd.DataFrame(products)
    df.to_csv('products_info.csv', index=False)
    print('Saved all the product information to file : products_info.csv')

    df_sec = pd.DataFrame(products_sec)
    df_sec.to_csv('products_info_normal_format.csv', index=False)
    print('Saved all the product information to file : products_info_simple_format.csv')

    return


url = 'https://www.hepsiburada.com/magaza/first-sourcer?markalar=firstsourcer&sayfa=2'

link_extractor(url=url)

products_extractor()
