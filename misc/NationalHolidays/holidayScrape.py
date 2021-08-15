import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
import json
from time import sleep
from tqdm.auto import tqdm

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.63',}
site = requests.get('https://www.timeanddate.com/holidays/?allcountries', headers=headers,)
soup = BeautifulSoup(site.content)

# urls of all the countries
countries_urls = ["https://www.timeanddate.com"+x.find('a')['href'] for x in soup.find("article", {'class':'category-list'}).findAll('li')]

# the years we want to extract. you can change this and use the years you want.
years = ["2018","2019", "2020", "2021", "2022"]

all_dfs = []
for country_url in tqdm(countries_urls): # country loop
    print(country_url, end=" => ") 
    for year in years: # year loop
        
        web_url = country_url + year
        try:
            df = pd.read_html(web_url)[0].dropna()
        except ValueError: # in case there is not tables in the website
            continue
        if len(df.columns) == 4:
            df['Details'] = ""
        df.columns = ["Date", "Day", "Name", "Type" , "Details"]
        df['Country'] = country_url.split("/")[-2].capitalize()
        df['Year'] = year
        all_dfs.append(df)
        
        print(df.shape[0], end=", ")
        del df 
    print()
        
#         break
#     break


df = pd.concat(all_dfs)
df.reset_index().drop(['index'], axis=1).to_excel('Holidays Data Total.xlsx', index=False)