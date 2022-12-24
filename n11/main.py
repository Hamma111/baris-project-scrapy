from datetime import datetime

import pandas as pd
from tqdm import tqdm

from n11.product_detail import get_product_detail
from n11.product_listing import get_product_urls_for_category

# category_url = "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu?m=Samsung"
category_url = input("Enter the category URL: ")
scrape_variants = True

print("\nExtracting Product URLs from the listing page #: ")
product_urls = get_product_urls_for_category(category_url)

print("\n\nNow extracting the Products details.")

products_data = []
for product_url in tqdm(product_urls[:]):
    product_data = get_product_detail(product_url, scrape_variants)
    products_data += product_data

file_name = f'n11-{datetime.now().strftime("%y-%m-%d-%H-%M")}.csv'
if scrape_variants:
    file_name = file_name.replace("n11", "n11-with-variants-")

df = pd.DataFrame(products_data)
df.to_csv(file_name, index=False)

