import requests
from bs4 import BeautifulSoup
url= "https://www.hepsiburada.com/magaza/first-sourcer?sayfa=1"
headers_param = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}

r = requests.get(url,headers=headers_param)
soup=BeautifulSoup(r.content,"lxml")


st3 = soup.find_all ("li",attrs={"data-index":"1"})
for detaylar in st3:
    link_basi = "https://www.hepsiburada.com"
    link_sonu = detaylar.a.get("href")
    link =  link_basi + link_sonu
    print(link)
    r1 = requests.get(link, headers=headers_param)
    soup1 = BeautifulSoup(r1.content,"lxml")
    #indirimli_ucret=soup1.find("span",{"class":"price product-price"})
    #print(indirimli_ucret)
    brandname = soup1.find("span",attrs={"class": "brand-name"}).getText('', True)
    print(brandname)
    name = soup1.find("h1",attrs={"itemprop":"name"}).getText('',True)
    print(name)
    print()

