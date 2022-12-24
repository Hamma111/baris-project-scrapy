from time import sleep

from trendyol.store_data import store_data
from trendyol.product_detail import get_product_data
from trendyol.product_listing import get_product_urls_by_category
from datetime import datetime
from tqdm import tqdm


# category_url = input("Enter category URL: ")
category_url = "https://www.trendyol.com/oyuncak-x-c90?pi=1"
scrape_variants = True

print("\nExtracting Product URLs from the listing page #: ")
product_urls = get_product_urls_by_category(category_url)

print("\n\nNow extracting the Products details.")

products_data = []
for url in tqdm(product_urls[:]):
    try:
        products_data += get_product_data(url, scrape_variants)
    except:
        print("!!!Skipping failed URL:", url)
        sleep(3)

file_name = f'trendyol-{datetime.now().strftime("%y-%m-%d-%H-%M")}.csv'
if scrape_variants:
    file_name = file_name.replace("trendyol", "trendyol-with-variants-")

store_data(products_data, file_name)
