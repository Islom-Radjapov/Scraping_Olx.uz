from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import random
import sqlite3
import datetime
from list_useragent import UserAgent


# sets today's date. format(31/12/2022)
date = datetime.datetime.now()
today = f"_{date.day}_{date.month}_{date.year}_"

product_urls = []    # empty container to eat all urls


# function to get urls
def scraping_urls(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    cards = soup.find_all('div', class_='css-19ucd76')
    global num
    num = soup.find_all('a', class_='css-1mi714g')
    num = num[-1].text
    for card in cards:
        info_products = card.find_all('div', class_='css-9nzgu8')
        for info_product in info_products:
            prod_loc_time = info_product.find('p', class_='css-p6wsjo-Text eu5v0x0').text
            if 'Сегодня' in prod_loc_time and 'Ташкент' in prod_loc_time and 'Юнусабадский район' in prod_loc_time:
                try:
                    prod_url = "https://www.olx.uz" + card.a["href"]
                    product_urls.append(prod_url)
                    print(prod_url)
                except:
                        continue


def phone_get(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'user-agent={UserAgent()}')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url=url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1d90tha')))
        element = driver.find_element(By.CLASS_NAME, "css-1ferwkx")
        driver.execute_script("arguments[0].scrollIntoView();", element)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-cuxnr-BaseStyles')))
        sleep(7)
        try:
            phone_button = driver.find_element(By.CLASS_NAME, 'css-cuxnr-BaseStyles')
            phone_button.click()
            phone_button.click()
            sleep(7)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-v1ndtc')))
            phone = driver.find_element(By.CLASS_NAME, "css-v1ndtc").text
        except:
            pass
        driver.close()
        driver.quit()
    except:
        pass
    return phone



# function to get info
def scrap_info(urls):
    for url in urls:
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(range(100,500))}.0.0.0 Safari/537.36')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        try:
            driver.get(url=url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1d90tha')))
            element = driver.find_element(By.CLASS_NAME, "css-1ferwkx")
            driver.execute_script("arguments[0].scrollIntoView();", element)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-cuxnr-BaseStyles')))
            phone = None
            for _ in range(10):
                try:
                    sleep(7)
                    phone_button = driver.find_element(By.CLASS_NAME, 'css-cuxnr-BaseStyles')
                    phone_button.click()
                    sleep(7)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-v1ndtc')))
                    phone = driver.find_element(By.CLASS_NAME, "css-v1ndtc").text
                except Exception as error:
                    # print(error)
                    continue
                if phone:
                    break

            if not phone:
                sleep(7)
                phone = phone_get(url)
            if not phone:
                sleep(7)
                phone = phone_get(url)
            if not phone:
                sleep(7)
                phone = phone_get(url)


            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')
            try:
                name = soup.find('h4', class_= 'css-1rbjef7-Text eu5v0x0').text
            except:
                name = None
            try:
                product_name = soup.find('h1', class_="css-r9zjja-Text eu5v0x0").text
            except:
                product_name = None
            try:
                price = soup.find('h3', class_="css-okktvh-Text eu5v0x0").text
            except:
                price = None

            try:
                description = soup.find('div', class_="css-g5mtbi-Text").text
            except:
                description = None
            product_url = url

            print(f"""
name: {name.strip()},
product_name: {product_name.strip()},
price: {price},
phone: {phone},
description: {description.strip()}, 
product: {product_url}
""")
            # append data to the database
            data_sql(name.strip(), product_name.strip(), price, phone, description.strip(), product_url)

        except Exception as error:
            print(error)
        driver.close()
        driver.quit()


# function to append data to the database
def data_sql(name, product_name, price, phone, description, product_url):
        connect = sqlite3.connect(f"product_{len(product_urls)}.db")
        cursor = connect.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {today}(Name text, product_name text, price integer, phone text, description text, url text) ")
        cursor.execute(f"INSERT INTO {today} VALUES ('{name}', '{product_name}', '{price}', '{phone}', '{description}', '{product_url}')")
        connect.commit()
        connect.close()


# main function
if __name__ == "__main__":
    # first page gets urls
    url = 'https://www.olx.uz/d/nedvizhimost/kvartiry/'
    scraping_urls(url)
    # all page gets urls
    x = 2
    while x <= int(num):
        scraping_urls(f"{url}?page={x}")
        x += 1
    # all get info
    scrap_info(product_urls)

