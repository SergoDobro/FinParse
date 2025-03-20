from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re

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



def parse_html(year, num_pages, non_dymanic):
    """
    year - минимальный год выпуска

    num_pages - количество страниц для парсинга

    non_dymanic - если True, то браузер не открывается явно
    """
    options = webdriver.ChromeOptions()
    if non_dymanic:
        options.add_argument("--headless")

    htmls = []                                                                                      # сюда положим все HTML-коды, чтобы парсить после выкачки данных

    driver = webdriver.Chrome(options=options)
    for page in range(1, num_pages + 1):
        driver.get(f"https://auto.drom.ru/bmw/all/page{page}/?minyear={year}")                      # открываем браузер

        htmls.append(driver.page_source)                                                            # Сохраняем HTML-код страницы

        #time.sleep(1)

    driver.quit()                                                                                   # закрываем браузер
    
    return htmls



def collect_data(htmls):
    cars = []

    for html in htmls:
        soup = BeautifulSoup(html, "html.parser")
        offers = soup.find_all(class_="css-1f68fiz ea1vuk60")
        for offer in offers:
            
            try:
                model_name = offer.find('h3', 'css-16kqa8y efwtv890').get_text()[4:].split(", ")
            except:
                continue
            descr = offer.find('div', 'css-1fe6w6s e162wx9x0').get_text()
            url = offer.find('a', 'g6gv8w4 g6gv8w8 _1ioeqy90').get('href')
            price = offer.find('span', 'css-46itwz e162wx9x0').get_text()[:-2].replace("\xa0", "")

            parts = descr.split(", ")
            if not ("л" in parts[0] and "л.с.)" in parts[0]):
                continue
            if parts[1].lower() not in ('бензин', 'дизель', 'гибрид'):
                continue

            #print(parts)

            liters = parts[0][:3]
            power = re.search(r'(\d+)\s*л\.с\.', parts[0]).group(1)
            fuel = parts[1]
            drive_type = parts[2]
            transmission_type = parts[3]
            usage = parts[4][:len(parts[4])-3] if len(parts) >= 5 else 0
        

            #print(model_name[0], parts, liters, power, fuel, drive_type, transmission_type, usage, year, price)

            
            new_car = Auto(
                model = offer.find('h3', 'css-16kqa8y efwtv890').get_text(),
                gen = model_name[0],
                year = model_name[1],
                engine_volume = liters,
                fuel_type = fuel,
                drive = drive_type,
                power_hp = power,
                mileage = usage,
                transmission = transmission_type,
                price = int(price),
                url = url
            )

            cars.append(new_car)


    return cars
