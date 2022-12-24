from bs4 import BeautifulSoup

from trendyol.utils import get_fail_safe_response


def get_product_urls_by_category(url):
    url = url.split("?")[0]

    page_number = 0
    product_urls = []

    while True:
        page_number += 1
        response = get_fail_safe_response(url + f"?pi={page_number}")

        if response.url == url or not response.ok:
            break

        soup = BeautifulSoup(response.content, features="html.parser")

        product_urls += [
            "https://www.trendyol.com" + e.find("a", {"href": True})['href']
            for e in
            soup.find_all("div", {"class": "p-card-chldrn-cntnr card-border"})
        ]

        if product_urls is None:
            break

        # if page_number == 5:
        #     break

        print(page_number, end=", ")

    return product_urls
