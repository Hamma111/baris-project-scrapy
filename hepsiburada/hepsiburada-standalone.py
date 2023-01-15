import re

import requests

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

# We update this URL
category_url = "https://www.hepsiburada.com/yazicilar-c-3013118"
# category_url = "https://www.hepsiburada.com/magaza/first-sourcer?markalar=Garanti%E2%82%AC20Mall"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.110 Safari/537.36'
}

print("Extracting the products urls from listing page # : ")

product_urls = set()

page_no = 1
while True:
    if "?" not in category_url:
        url = f"{category_url}?sayfa={page_no}"
    else:
        url = f"{category_url}&sayfa={page_no}"

    print(url)

    site = requests.get(url, headers=headers)
    if site.url != url and "sayfa=1" not in url:
        break

    soup = BeautifulSoup(site.content, "html.parser")
    if soup.find("div", {"id": re.compile("ProductList")}):
        products_elements = (
            soup
            .find("div", {"id": re.compile("ProductList")})
            .find("ul", {"class": re.compile("productListContent")})
            .find_all("li", {"class": re.compile("productListContent")})
        )
    elif soup.find("ul", {"class": "product-list"}):
        products_elements = (
            soup
            .find("ul", {"class": "product-list"})
            .find_all("li", {"class": "search-item"})
        )
    else:
        raise Exception("Invalid listing page received. Code has not been written to handle such listing page.")

    product_urls |= {f"https://www.hepsiburada.com{p.a.attrs['href']}" for p in products_elements if p.a}
    print(page_no, end=", ")
    page_no += 1


def extract_product_details(product_url):
    site = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(site.content, "html.parser")

    name = soup.find("h1", {"id": "product-name"}).get_text(strip=True)
    brand = soup.find("span", {"class", "brand-name"}).get_text(strip=True)
    brand_url = f'https://www.hepsiburada.com{soup.find("span", {"class", "brand-name"}).a.attrs["href"]}'

    sku = soup.find("meta", {"itemprop": "sku"}).attrs.get('content', "")
    gtin = soup.find("meta", {"itemprop": "gtin"}).attrs.get('content', "")

    price = soup.find('span', {'itemprop': 'price'}).attrs.get('content', "")

    average_rating_el = soup.find("span", {"class": "rating-star"})
    average_rating = average_rating_el.get_text(strip=True) if average_rating_el else ""
    num_of_comments_el = soup.find("div", {"id": "comments-container"})
    num_of_comments = num_of_comments_el.get_text(strip=True).replace("Değerlendirme",
                                                                      "").strip() if num_of_comments_el else ""

    breadcrumbs = [b.get_text(strip=True) for b in soup.find("ul", {"class": "breadcrumbs"}).find_all("li")]
    breadcrumbs_urls = [b.a.attrs['href'] for b in soup.find("ul", {"class": "breadcrumbs"}).find_all("li")]

    primary_image_url = soup.find("div", {"id": "productDetailsCarousel"}).img['src']
    image_urls = [
        img.attrs['src'].replace("/80/", "/500/")
        for img in
        soup.find("div", {"id": "productThumbnailsCarousel"}).find_all("img")[1:]
    ]

    description_text = soup.find("div", {"id": "tabProductDesc"}).get_text("\n", True)
    description_text_html = soup.find("div", {"id": "tabProductDesc"})

    data = {
        "name": name,
        "brand": brand,
        "brand_url": brand_url,
        "sku": sku,
        "gtin": gtin,
        "price": price,
        "url": product_url,
        "average_rating": average_rating,
        "num_of_comments": num_of_comments,
        "breadcrumbs": breadcrumbs,
        "breadcrumbs_urls": breadcrumbs_urls,
        "primary_image_url": primary_image_url,
        "image_urls": image_urls,
        "description_text": description_text,
        "description_text_html": description_text_html,
        "variant_attribute_value": ""
    }

    variants_el = soup.find("div", {"class": "product-variants-content"})
    variants_data = []
    if variants_el and len(variants_el.find_all("div", {"class": "variants-content"})) > 1:
        for variant_el in variants_el.find_all("div", {"class": "variants-content"}):
            _data = data.copy()
            _data['variant_attribute_value'] = variant_el.find("span", {"class": "variant-name"}).get_text(strip=True)
            _data['price'] = variant_el.find("span", {"class": "variant-property-price"}).get_text(strip=True)
            variants_data.append(_data)
        data = variants_data
    else:
        data = [data]

    return data


print("Now extracting product details..")

products_data = []
for product_url in tqdm(list(product_urls)):
    products_data += extract_product_details(product_url)

df = pd.DataFrame(products_data)
df.to_csv("output.csv", index=False)
