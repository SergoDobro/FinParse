from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas

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
