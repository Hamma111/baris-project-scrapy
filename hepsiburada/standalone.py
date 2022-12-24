from datetime import datetime
import json
import re
from time import sleep

import requests
from requests.exceptions import ConnectionError

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

site = requests.get("", headers=headers)

soup = BeautifulSoup(site.content)

title = soup.find("header", {"class": "title-wrapper"}).get_text(strip=True)
