from datetime import date

import pandas as pd
from tqdm import tqdm

from product_detail import get_product_detail
from product_listing import get_product_urls_for_category

category_url = "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu?m=Samsung"

product_urls = get_product_urls_for_category(category_url)

products_data = []
for product_url in tqdm(product_urls[:]):
    product_data = get_product_detail(product_url)
    products_data.append(product_data)

df = pd.DataFrame(
    products_data,
    columns=[
        "Title", "Price", "Details", "Ratings", "Reviews Count", "Favorites Count",
        "Primary Image URL", "All Image URLs", "Features", "Features HTML"
    ],
)

df.to_csv(f"N11 - {date.today()}.csv", index=False)
