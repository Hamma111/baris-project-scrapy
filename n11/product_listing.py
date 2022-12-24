from bs4 import BeautifulSoup

from n11.utils import get_fail_safe_response

PAGINATION_URL = "https://www.n11.com/searchCategoryForPagination/{category_id}?pg={page_number}"


def get_category_id_for_category_url(url):
    response = get_fail_safe_response(url)
    soup = BeautifulSoup(response.content, features="html.parser")

    category_id = soup.find("input", {"class": "categoryId"}).attrs['value']

    return category_id


def _get_product_urls_for_category(category_id):
    product_urls = []
    i = 0
    while True:
        i += 1
        url = PAGINATION_URL.format(category_id=category_id, page_number=str(i))
        response = get_fail_safe_response(url)
        soup = BeautifulSoup(response.content, features="html.parser")

        _product_urls = [x.attrs.get("href") for x in soup.find_all("a", {"class": "plink"})]

        if not _product_urls:
            break

        product_urls += _product_urls

        print(i, end=", ")

    return product_urls


def get_product_urls_for_category(category_url):
    category_id = get_category_id_for_category_url(category_url)
    return _get_product_urls_for_category(category_id)
