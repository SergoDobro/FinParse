from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import re
import requests
import GetCarz.Core.support_methods

class Auto:
    def __init__(self, model: str = "", gen: str = "", year: int = 0, engine_volume: float = 0.0, fuel_type: str = "",
                 drive: str = "", power_hp: int = 0, mileage: int = 0, transmission: str = "", price: int = 0, url: str = ""):
        self.model = model                      # модель
        self.gen = gen                          # серия
        self.year = year                        # год выпуска
        self.engine_volume = engine_volume      # объем двигателя
        self.fuel_type = fuel_type              # бензин/дизель
        self.drive = drive                      # привод
        self.power_hp = power_hp                # мощность в л.с.
        self.mileage = mileage                  # пробег (==0, если новая)
        self.transmission = transmission        # КПП
        self.price = price                      # цена
        self.url = url

    def __str__(self):
        return (f"{self.model} | {self.gen} | {self.year} | {self.mileage} |{self.engine_volume}L | {self.power_hp} HP | {self.fuel_type} | "
                f"{self.transmission} | {self.drive} | {self.price} ₽ | {self.url}")


def parse_html(num_pages, start_page=1):
    """
    num_pages - количество страниц для парсинга

    non_dymanic - если True, то браузер не открывается явно
    """

    htmls = []                                                                                      # сюда положим все HTML-коды, чтобы парсить после выкачки данных

    for page in range(start_page, num_pages + 1):
        print(f"processed pages: {page}/{num_pages}")
        url = f"https://www.avito.ru/all/avtomobili/bmw-ASgBAgICAUTgtg3klyg?cd=1&f=ASgBAgECAUTgtg3klygBRfqMFBd7ImZyb20iOjIwMTAsInRvIjpudWxsfQ&p={page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers).text

        htmls.append(response)                                                            # Сохраняем HTML-код страницы

        #time.sleep(1)

    
    return htmls


def collect_data(responses):
    cars = []

    for response in responses:
        soup = BeautifulSoup(response, "html.parser")
        offers = soup.find_all(class_="iva-item-content-OWwoq")

        for item in offers:
            model_name = item.find('h3', "styles-module-root-s3nJ7 styles-module-root-s4tZ2 styles-module-size_l-j3Csw styles-module-size_l_compensated-trWgn styles-module-size_l-ai2ZG styles-module-ellipsis-A5gkK styles-module-weight_bold-Bh2pN stylesMarningNormal-module-root-_xKyG stylesMarningNormal-module-header-l-GrtnL")

            if model_name == None:
                continue

            model_name = model_name.get_text().strip()
            price = item.find('strong', "styles-module-root-LEIrw").get_text().strip()[:-2].replace('\xa0', '')
            link = 'https://www.avito.ru' + item.find('a', "styles-module-root-m3BML styles-module-root_noVisited-HHF0s").get('href')
            description = item.find('p', "styles-module-root-s4tZ2 styles-module-size_s-nEvE8 styles-module-size_s-PDQal stylesMarningNormal-module-root-_xKyG stylesMarningNormal-module-paragraph-s-HX94M").get_text().split(', ')
            description = [item.replace('\xa0', '') for item in description]

            parts = model_name.split(", ")

            year = parts[1]
            generation = parts[0].split()[1]


            if 'км' not in description[0] and 'AT' not in description[1] and 'л.с.' not in description[1]:
                continue

            usage = description[0][:-2]
            liters = description[1][:3]
            power = re.search(r"\((\d+)", description[1]).group(1)

            drive_type = description[-2]
            fuel = description[-1]

            new_car = Auto(
                model = model_name,
                gen = generation,
                year = int(year),
                price = int(price),
                url = link,
                mileage = usage,
                engine_volume = liters,
                power_hp = int(power),
                drive = drive_type,
                fuel_type = fuel
            )

            cars.append(new_car)

    return cars

def modify_gen(car):
    if car.gen.isdigit():
        car.gen += '-Series'


def cars_list_to_dataframe(cars):
    df = pd.DataFrame([{
        "Модель": car.model,
        "Серия": car.gen,
        "Год": car.year,
        "Объем двигателя": car.engine_volume,
        "Топливо": car.fuel_type,
        "Привод": car.drive,
        "Мощность": car.power_hp,
        "Пробег": car.mileage,
        "КПП": car.transmission,
        "Цена": car.price,
        "Ссылка": car.url
    } for car in cars])

    return df

# Запуск парсинга
if __name__ == '__main__':
    htmls = parse_html(10, 1)
    cars = collect_data(htmls)

    GetCarz.Core.support_methods.set_google_sheet(cars_list_to_dataframe(cars), 'Avito')