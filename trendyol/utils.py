from time import sleep

import requests
from requests.exceptions import ConnectionError

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}


def get_fail_safe_response(url):
    try:
        return requests.get(url, headers=headers)
    except ConnectionError:
        sleep(2)
        print("error!!! but sleeping for 2 seconds, url", url)
        return get_fail_safe_response(url)
