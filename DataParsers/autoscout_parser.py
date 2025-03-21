import urllib, requests, socket, re, lxml, io, bs4, sqlite3, sqlalchemy
from bs4 import BeautifulSoup
import pandas as pd

import time
from GetCarz.Core import SupportMethods


def get_page(page_number, model):
  #html = requests.get(f"https://www.autoscout24.ru/lst/bmw?atype=C&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=0&fregfrom=2010&page={page_number}&powertype=kw&search_id=1r8svk9jevn&sort=standard&source=listpage_pagination&ustate=N%2CU").content.decode('UTF-8')
  the_link = f"https://www.autoscout24.ru/lst/bmw/{model}?_gl=1%2A17rtokj%2A_up%2AMQ..%2A_ga%2ANTE2NDQ1MjQxLjE3NDIyMzI1MTA.%2A_ga_BGSHTTTQ7W%2AMTc0MjIzMjUwOS4xLjAuMTc0MjIzMjUwOS4wLjAuMA..&atype=C&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=0&fregfrom=2010&page={page_number}"
  html = requests.get(the_link).content.decode('UTF-8')
  soup = BeautifulSoup(html, "lxml")
  return html

def fixing_get_page(page_number, model):
  #html = requests.get(f"https://www.autoscout24.ru/lst/bmw?atype=C&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=0&fregfrom=2010&page={page_number}&powertype=kw&search_id=1r8svk9jevn&sort=standard&source=listpage_pagination&ustate=N%2CU").content.decode('UTF-8')
  the_link = f"https://www.autoscout24.ru/lst/bmw/{model}?_gl=1%2A17rtokj%2A_up%2AMQ..%2A_ga%2ANTE2NDQ1MjQxLjE3NDIyMzI1MTA.%2A_ga_BGSHTTTQ7W%2AMTc0MjIzMjUwOS4xLjAuMTc0MjIzMjUwOS4wLjAuMA..&atype=C&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=0&fregfrom=2010&page={page_number}"
  html = requests.get(the_link).content.decode('UTF-8')
  soup = BeautifulSoup(html, "lxml")
  return the_link

def get_articles(html):
  pattern = r'<main[^>]*class=["\'].*?ListPage_main___0g2X.*?["\'][^>]*>(.*?)</main>'
  match = re.search(pattern, html, re.DOTALL)
  main_content = match.group(0)
  soup = BeautifulSoup(main_content, "lxml")
  articles = soup.find_all("article")
  return articles

def get_car_data_autoscout(article):
  data = dict()
  data["марка"] = article.get("data-make")
  data["цена"] = article.get("data-price")
  try:
    data["пробег"] = int(article.get("data-mileage"))
  except:
    data["пробег"] = article.get("data-mileage")
  data["вид топлива"] = article.get("data-fuel-type")
  if article.get("data-fuel-type") == "d":
     data["вид топлива"] = "Дизель"
  if article.get("data-fuel-type") == "b":
     data["вид топлива"] = "Бензин"
  data["модель"] = article.get("data-model")
  try:
    data["год выпуска"] = int(article.get("data-first-registration")[3:])
  except:
    data["год выпуска"] = article.get("data-first-registration")[3:]
  car_title_tag = article.find("a", class_="ListItem_title__ndA4s")
  if car_title_tag and "aria-label" in car_title_tag.attrs:
    data['Полное название модели'] = car_title_tag["aria-label"]
  details = article.find_all("span", class_="VehicleDetailTable_item__4n35N")
  for detail in details:
        label = detail.get("aria-label")
        value = detail.text.strip()
        if "Коробка передач" in label:
            data["трансмиссия"] = value
        elif "Мощность" in label:
            match = re.search(r'(\d+)\s*л\.с\.', value)         #ре запрос написал гпт
            if match:
               data["мощность"] = int(match.group(1))
  return data

def get_model_table(model):
  i = 0
  model_table = pd.DataFrame(columns=["марка", "модель", "год выпуска", "трансмиссия", "мощность", "вид топлива", "цена", "пробег", "Полное название модели"])
  while True:
    try:
      page_articles = get_articles(get_page(i+1, model))
      for j in range(len(page_articles)):
        model_table = pd.concat([model_table, pd.DataFrame(data = [get_car_data_autoscout(page_articles[j])])], ignore_index=True)
      #print(fixing_get_page(i+1, models[0]))
      i = i+1
    #print(pd.DataFrame(data = [get_car_data_autoscout(page_articles[j])]))
    except Exception as e:
      print(model, i+1, bool(page_articles), e)
      #print(fixing_get_page(i+1, models[0]))
      break
    if i == 20: #        check that it's 20                             check that it's 20                                  check that it's 20
      break
  return model_table




models = [
    "114", "116", "118", "120", "123", "125", "128", "130", "135", "140",
    "214", "216", "218", "220", "223", "225", "228", "230", "235", "240", "2002",
    "315", "316", "318", "320", "323", "324", "325", "328", "330", "335", "340", "active-hybrid-3",
    "418", "420", "425", "428", "430", "435", "440",
    "518", "520", "523", "524", "525", "528", "530", "535", "540", "545", "550", "active-hybrid-5",
    "620", "628", "630", "633", "635", "640", "645", "650",
    "725", "728", "730", "732", "735", "740", "745", "750", "760", "active-hybrid-7",
    "830", "840", "850", "1er-m-coupé", "M1", "M2", "M3", "M4", "M5", "M550", "M6", "M8", "M850",
    "active-hybrid-X6", "X1", "X2", "X2-M", "X3", "X3-M", "X4", "X4-M", "X5", "X5-M", "X6", "X6-M", "X7", "X7-M", "XM",
    "Z1", "Z3", "Z3-M", "Z4", "Z4-M", "Z8",
    "i3", "i4", "i5", "i7", "i8", "iX", "iX1", "iX2", "iX3", "Others"
]




#код таймера написал гпт
start_time = time.time()
model_tables = dict()
for model in models:
  model_tables[model] = get_model_table(model)
  elapsed_time = time.time() - start_time
  minutes = int(elapsed_time // 60)
  seconds = int(elapsed_time % 60)
  if  minutes>0:
      break
  print(f"\rCurrent model: {model}. Прогресс: {100*(1+models.index(model))//len(models)}% . Текущее время выполнения: {minutes} мин {seconds} сек", end="", flush=True)
time.sleep(2)
end_time = time.time()
print()
print(f"Время выполнения: {end_time - start_time:.4f} секунд")

tables_for_models = model_tables




merged_table = pd.DataFrame()
for tablee in tables_for_models.values():
  merged_table = pd.concat([merged_table, tablee])




for column in merged_table.columns:
  print(column, ": ", len(merged_table[column].unique())) #merged_table.loc[merged_table['вид топлива'] == "unknown"]
print("total amount: ", len(merged_table))


SupportMethods.set_google_sheet(merged_table, 'AutoScout24')