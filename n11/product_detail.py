import json
import re

from bs4 import BeautifulSoup

from n11.utils import get_fail_safe_response


def parse_response_content(content, scrape_variant):
    soup = BeautifulSoup(content, features="html.parser")

    product_script_text = (
        soup
        .find(text=re.compile('{"pBrand"'))
        .strip()
        .replace("\n", '')
    )
    product_script_text = product_script_text[product_script_text.find('{"pBrand"'):product_script_text.find("};")]
    product_script_dict = json.loads(product_script_text)

    var_script_text = (
        soup
        .find(text=re.compile("var skuList"))
        .replace("\n", ""))

    var_script_text = var_script_text[var_script_text.find('{"skuList"'):var_script_text.find('"};') + 2]
    script_variants_dict = json.loads(var_script_text)

    sku_id = soup.find("input", {"name": "skuId"})['value']
    pims_id = soup.find("input", {"id": "unificationDetailPims"})['value']
    product_id = soup.find("input", {"id": "prodId"})['value']
    category_id = soup.find("input", {"id": "catId"})['value']

    category = product_script_dict['pCatMain']
    brand = product_script_dict['pBrand']

    seller_id = soup.find("input", {"id": "sellerId"})['value']
    seller_name = soup.find("a", {"class": "unf-p-seller-name"})['title']
    seller_url = soup.find("a", {"class": "unf-p-seller-name"})['href']

    title = soup.find("h1", {"class": "proName"}).get_text(strip=True)
    discount_price = product_script_dict['pOriginalPrice']
    original_price = product_script_dict['pDiscountedPrice']

    hierarchy = soup.find("div", {"id": "breadCrumb"}).get_text(separator=" > ", strip=True)

    details_element = soup.find("div", {"id": "unf-info"})
    details = details_element.get_text(strip=True) if details_element else ""

    ratings_element = soup.find("strong", {"class": "ratingScore"})
    ratings = ratings_element.text if ratings_element else ""

    num_reviews_element = soup.find("span", {"class": "reviewNum"})
    num_reviews = num_reviews_element.text if num_reviews_element else ""

    num_favorites_element = soup.find("span", {"class": "wishListCount"})
    num_favorites = num_favorites_element.text.replace("favori", "").strip() if num_favorites_element else ""

    features_list = [
        x.get_text(separator=" - ", strip=True)
        for x in soup.find_all("li", {"class": "unf-prop-list-item"})
    ]
    features = "\n".join(features_list)
    features_html = soup.find("div", {"class": "unf-prop-context"})

    default_product_dict = {
        "sku_id": sku_id,
        "pims_id": pims_id,
        "product_id": product_id,
        "category_id": category_id,
        "category": category,
        "brand": brand,

        "seller_id": seller_id,
        "seller_name": seller_name,
        "seller_url": seller_url,

        "title": title,
        "original_price": original_price,
        "discount_price": discount_price,

        "hierarchy": hierarchy,

        "details": details,

        "ratings": ratings,
        "num_reviews": num_reviews,
        "num_favorites": num_favorites,

        "features": features,
        "features_html": features_html,
    }

    if scrape_variant:
        data = []
        for variant in script_variants_dict['skuList']:
            _data = default_product_dict.copy()
            _data['variant'] = variant['hash']
            _data['pims_id'] = variant['pimsId']
            _data['primary_image_url'] = variant['images'][0]
            _data['all_image_urls'] = ", ".join([
                "https://n11scdn.akamaized.net/a1/602_857/" + img
                for img in variant['images'][1:]
            ])

            data.append(_data)

    else:
        default_product_dict['variant'] = script_variants_dict['skuList'][0]['hash']
        default_product_dict['pims_id'] = script_variants_dict['skuList'][0]['pimsId']
        default_product_dict['primary_image_url'] = script_variants_dict['skuList'][0]['images'][0]
        default_product_dict['all_image_urls'] = ", ".join([
            "https://n11scdn.akamaized.net/a1/602_857/" + img
            for img in script_variants_dict['skuList'][0]['images'][1:]
        ])
        data = [default_product_dict]

    return data


def get_product_detail(product_url, scrape_variant: bool):
    response_content = get_fail_safe_response(product_url).content
    return parse_response_content(response_content, scrape_variant)

product_url = "https://www.n11.com/urun/xiaomi-redmi-note-11-pro-8-gb-128-gb-xiaomi-turkiye-garantili-3042752?magaza=xiaomiturkiye"