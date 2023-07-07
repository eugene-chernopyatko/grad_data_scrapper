import os
import requests
from bs4 import BeautifulSoup
import pandas
import gspread

MAIN_SITE_URL = 'https://gradgear.com.ua'
product_id_list = []
product_title_list = []
product_price_list = []
product_image_list = []

with open('urls.txt') as urls_file:
    urls = urls_file.readlines()

with open('Google_Sheet_Url.txt') as Url_file:
    GOOGLE_SHEET_URL = str(Url_file.readline())


def make_soup(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_product_urls_from_category(urls_list):
    products_url = []
    for url in urls_list:
        soup = make_soup(url)
        tag_product_url = soup.find_all('a', class_='item__title')
        for i in tag_product_url:
            products_url.append(f'{MAIN_SITE_URL}{i["href"]}')
    return products_url


product_url = get_product_urls_from_category(urls)
# print(product_url)

def get_product_data(urls_list):
    for url in urls_list:
        soup = make_soup(url)
        product_id = soup.find_all('div', class_='productKey')
        for i in product_id:
            product_id_list.append(i['data-productkey'])
        product_titles = soup.find_all('span', class_='item-pg__title-text')
        for i in product_titles:
            product_title_list.append(i.text)
        product_price = soup.find_all('span', class_='price-number s-product-price')
        for i in product_price:
            price = str(i['data-price'])
            if len(price) <= 3:
                product_price_list.append(f'{price},00')
            if len(price) > 3:
                product_price_list.append(f'{price[0]},{price[1:]}.00')
        image_links_tag = soup.find_all('li', class_='slideshow-owl-item-li')
        for i in image_links_tag:
            try:
                product_image_list.append(f'{MAIN_SITE_URL}{i.find("img")["src"]}')
            except TypeError:
                continue


get_product_data(product_url)

product_decript_list = ['Український виробник тактичного спорядження' for _ in range(len(product_id_list))]
product_availability_list = ['in stock' for _ in range(len(product_id_list))]
product_condition_list = ['new' for _ in range(len(product_id_list))]
product_brand_list = ['Grad Gead' for _ in range(len(product_id_list))]

pd = pandas.DataFrame()
pd['id'] = product_id_list
pd['title'] = product_title_list
pd['description'] = product_decript_list
pd['availability'] = product_availability_list
pd['condition'] = product_condition_list
pd['price'] = product_price_list
pd['link'] = product_url
pd['image_link'] = product_image_list
pd['brand'] = product_brand_list


def upload_data_to_sheet(pd):
    """Uploading data from pandas data frames to google sheet"""
    key_p = os.path.abspath('test-python-334320-9b1f7f660a78.json')
    gc = gspread.service_account(filename=key_p)
    sheet = gc.open_by_url(GOOGLE_SHEET_URL)
    worksheet = sheet.get_worksheet(0)
    # worksheet.resize(rows=len(self.ID))
    worksheet.update([pd.columns.values.tolist()] + pd.values.tolist())
    print('\nData Updated')


upload_data_to_sheet(pd)
