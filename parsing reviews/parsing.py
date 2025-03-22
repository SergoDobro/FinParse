from yandex_reviews_parser.utils import YandexParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
ids = [1706136465, 61877138942, 1049259640, 30151116239, 49310954585, 
       1036653781, 1037910515, 1179175858, 
       1063235852, 1088261741, 216657971138, 
       111479261173, 1052789604]
id_ya =1706136465
total_data = [] 
for idb in ids:
    try:
      parser = YandexParser(idb)
      print("in progress")
      all_data = parser.parse() 
      total_data.append(all_data)
    except:
       pass
print("its over")

with open("total_data.json", "w", encoding="utf-8") as f:
    json.dump(total_data, f, ensure_ascii=False, indent=2)

print(" Данные сохранены")
print("businesses parsed:", len(total_data))