import json
import re

from bs4 import BeautifulSoup

from trendyol.utils import get_fail_safe_response


def get_product_script_dict(product_url):
    response = get_fail_safe_response(product_url)
    soup = BeautifulSoup(response.content, features="html.parser")

    script_text = (
        soup
        .find(text=re.compile(r"window.__PRODUCT_DETAIL_APP_INITIAL_STATE__"))
        .strip()
        .replace("window.__PRODUCT_DETAIL_APP_INITIAL_STATE__", "")
        .replace("=", "")
        .replace("\n        ", "")
        .strip()
    )
    script_text = script_text[:script_text.find(';window.TYPageName')]

    return json.loads(script_text)


def get_product_parsed_data(product_script_dict, scrape_variants):
    product_key_dict = product_script_dict['product']

    id = product_key_dict['id']
    product_code = product_key_dict['productCode']
    item_number = product_key_dict['variants'][0]['itemNumber']
    name = product_key_dict['name']
    name_with_code = product_key_dict['nameWithProductCode']
    url = "https://www.trendyol.com/" + product_key_dict['url']
    barcode = product_key_dict['variants'][0]['barcode']
    in_stock = product_key_dict['hasStock']

    merchant = product_key_dict['merchant']['name']
    merchant_official_name = product_key_dict['merchant']['officialName']
    merchant_tax_number = product_key_dict['merchant'].get('taxNumber')
    merchant_score = product_key_dict['merchant'].get('sellerScore')
    merchant_url = "https://www.trendyol.com/" + product_key_dict['merchant']["sellerLink"]

    brand = product_key_dict['brand']['name']
    category = product_key_dict['category']['name']
    category_hierarchy = product_key_dict['category']['hierarchy']

    gender = product_key_dict['gender'].get('name', "")
    color = product_key_dict['color']

    attribute_type = product_key_dict['variants'][0]['attributeType']
    attribute_value = product_key_dict['variants'][0]['attributeValue']

    original_price = product_key_dict['variants'][0]['price']['discountedPrice']['text']
    discounted_price = product_key_dict['variants'][0]['price']['originalPrice']['text']
    currency = product_key_dict['variants'][0]['price']['currency']

    average_rating = product_key_dict['ratingScore']['averageRating']
    ratings_count = product_key_dict['ratingScore']['totalRatingCount']
    favorite_count = product_key_dict['favoriteCount']

    description = "\n".join([x['description'] for x in product_key_dict['contentDescriptions']])
    # color_attr = next(
    #     (attr for attr in product_key_dict['attributes'] if attr['key']['name'] == 'Renk'), None
    # )
    # color = color_attr['value']['name'] if color_attr else ""

    image_urls_list = ["https://cdn.dsmcdn.com" + img for img in product_key_dict['images']]
    primary_image_url = image_urls_list[0]
    image_urls = ", ".join(image_urls_list[1:])

    default_product_dict = {
        "id": id,
        "product_code": product_code,
        "item_number": item_number,
        "name": name,
        "name_with_code": name_with_code,
        "url": url,
        "barcode": barcode,
        "in_stock": in_stock,

        "merchant": merchant,
        "merchant_official_name": merchant_official_name,
        "merchant_tax_number": merchant_tax_number,
        "merchant_score": merchant_score,
        "merchant_url": merchant_url,

        "brand": brand,
        "category": category,
        "category_hierarchy": category_hierarchy,

        "gender": gender,
        "color": color,

        "attribute_type": attribute_type,
        "attribute_value": attribute_value,

        "original_price": original_price,
        "discounted_price": discounted_price,
        "currency": currency,

        "average_rating": average_rating,
        "ratings_count": ratings_count,
        "favorite_count": favorite_count,

        "description": description,
        "primary_image_url": primary_image_url,
        "image_urls": image_urls,
    }

    if scrape_variants:
        data = get_variants(product_key_dict, default_product_dict)
    else:
        data = default_product_dict

    return data


def get_variants(product_key_dict, default_product_dict):
    variants = []

    for variant_dict in product_key_dict['allVariants']:
        variant_data = default_product_dict.copy()
        variant_data['item_number'] = variant_dict['itemNumber']
        variant_data['attribute_value'] = variant_dict['value']
        variant_data['in_stock'] = variant_dict['inStock']
        variant_data['barcode'] = variant_dict['barcode']
        variant_data['discounted_price'] = variant_dict['price']

        variants.append(variant_data)

    return variants


def get_product_data(product_url, scrape_variants: bool):
    product_script_dict = get_product_script_dict(product_url)
    try:
        data = get_product_parsed_data(product_script_dict, scrape_variants)
    except:
        print(product_script_dict)
        raise Exception()

    return data


