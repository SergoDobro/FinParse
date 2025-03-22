from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

import GetCarz.Core.SupportMethods


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



def parse_html(year, num_pages, non_dymanic, start_page=1):
    """
    year - минимальный год выпуска

    num_pages - количество страниц для парсинга

    non_dymanic - если True, то браузер не открывается явно
    """
    options = webdriver.ChromeOptions()
    if non_dymanic:
        options.add_argument("--headless")

    htmls = []                                                                                      # сюда положим все HTML-коды, чтобы парсить после выкачки данных

    driver = webdriver.Edge(options=options)
    for page in range(start_page, num_pages + 1):
        driver.get(f"https://auto.ru/rossiya/cars/bmw/all/?year_from={year}&page={page}")           # открываем браузер

        htmls.append(driver.page_source)                                                            # Сохраняем HTML-код страницы

        #time.sleep(1)

    driver.quit()                                                                                   # закрываем браузер
    
    return htmls


def collect_data(htmls):
    cars = []
    
    for html in htmls:
        soup = BeautifulSoup(html, "html.parser")
        offers = soup.find_all(class_="ListingItem__description")
        for item in offers:
            model_name = item.find('a', 'Link ListingItemTitle__link').get_text().strip()

            tech_summary = item.find('div', class_='ListingItemTechSummaryDesktop')
            columns = tech_summary.find_all('div', class_='ListingItemTechSummaryDesktop__column')

            engine_data = columns[0].find_all('div', class_='ListingItemTechSummaryDesktop__cell')[0].get_text()
            engine_data = engine_data.split('\u2009')
            engine_data = [part.replace('\xa0', ' ') for part in engine_data if part != '/']
            if engine_data[2] != 'Электро':
                liters, hp, fuel = engine_data[0][:len(engine_data[0])-2], engine_data[1][:len(engine_data[1])-5], engine_data[2]
                transmission_type = columns[0].find_all('div', class_='ListingItemTechSummaryDesktop__cell')[1].get_text()
            else:
                liters, hp, fuel = 0, engine_data[0][:len(engine_data[0])-5], engine_data[2]
                transmission_type = "автомат"

            
            drive_type = columns[1].find_all('div', class_='ListingItemTechSummaryDesktop__cell')[0].get_text()


            price = item.find('div', 'ListingItemPrice__content').get_text() if item.find('div', 'ListingItemPrice__content') else "Not found"
            price = price.lstrip('от ').replace('\xa0', '').rstrip('₽')
            if price == "Not found":
                continue

            usage = item.find('div', "ListingItem__kmAge").get_text()
            usage = usage[:len(usage)-3].replace('\xa0', '')
            if usage == 'Но':
                continue
            
            link = item.find('a', 'Link ListingItemTitle__link').get('href')
            parts = urlparse(link).path.split('/')

            # if "bmw" in parts:
            generation_index = parts.index("bmw") + 1
            generation = parts[generation_index] if generation_index < len(parts) else None

            # print("Model:", generation)  # 5er
            

            # print(engine_data)
            new_car = Auto(
                model = model_name,
                gen = generation,
                engine_volume = float(liters),
                power_hp = int(hp),
                fuel_type = fuel,
                transmission = transmission_type,
                drive = drive_type,
                url = link,
                price = int(price) if price != "Not found" else "Not found",
                year = item.find('div', 'ListingItem__year').get_text(),
                mileage = int(usage)
            )
            cars.append(new_car)
            
            # print(model_name) 
    return cars

def modify_gen(car):
    car.gen = car.gen.upper()
    if car.gen[-2:] in ('ER', '_M') and not car.gen[0].isdigit():
        car.gen = car.gen[:-2]
        
    elif car.gen[0].isdigit() and len(car.gen) >= 3:
        car.gen = car.gen[0]+"-Series"

    elif car.gen[0].isdigit():
        car.gen = car.gen[0]+"-Series"   

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
    year = 2010  # самый ранний год выпуска машины
    htmls = parse_html(year, 100, False, 1)
    cars = collect_data(htmls)

    GetCarz.Core.SupportMethods.set_google_sheet(cars_list_to_dataframe(cars), 'AutoRu')