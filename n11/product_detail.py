from bs4 import BeautifulSoup

from utils import get_fail_safe_response

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.110 Safari/537.36 '
}


def parse_response_content(content):
    soup = BeautifulSoup(content, features="html.parser")

    title = soup.find("h1", {"class": "proName"}).get_text(strip=True)
    price = soup.find("div", {"class": "unf-p-summary-price"}).get_text(strip=True)

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

    primary_image_url = soup.find("div", {"class": "imgObj"}).img['data-src']
    all_image_urls = {
        x['data-original'].replace("60_86", "602_857")
        for x in soup.find_all("img", {"alt": title})
        if x.get("data-original")
    }

    return (
        title,
        price,
        details,
        ratings,
        num_reviews,
        num_favorites,
        primary_image_url,
        all_image_urls,
        features,
        features_html,
    )


def get_product_detail(product_url):
    response_content = get_fail_safe_response(product_url).content
    return parse_response_content(response_content)
