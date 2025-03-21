
import pandas as pd
import time, lxml, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from IPython.display import display


import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



html = requests.get("https://auto.ru/moskovskaya_oblast/dilery/cars/bmw/new/?utm_referrer=https%3A%2F%2Fyandex.ru%2F").content.decode("utf-8")
soup = BeautifulSoup(html, "lxml")
dealer_articles = (soup.find_all("div", class_= "DealerList__snippets"))[0].find_all("div", class_="DealerListItem DealerList__item")

def get_data_from_articles(article, bulshit = 0):
  data = dict()
  data["Название"] = (article.find("a", class_="Link DealerListItem__name")).get_text(strip = True)
  data["Ссылка"] = (article.find("a", class_="Link DealerListItem__name")).find("href")
  data["Адрес"] = (article.find("div", class_="DealerListItem__address")).get_text(strip = True)
  try:
    data["Количество машин в продаже"] = ((article.find("a", class_="Link DealerListItem__search_results")
                                    ).get_text(strip = True))[:-15]
  except:
    data["Количество машин в продаже"] = 0
  return data


def get_coorditanes(adress):
  link = "https://yandex.ru/maps/?ll=37.761551%2C55.730599&z=9.62"
  driver = webdriver.Chrome()
  driver.get(link)
  #time.sleep(10)
  input_box = driver.find_element("class name", "input__control")
  input_box.send_keys(adress)
  input_box.send_keys(Keys.ENTER)
  time.sleep(3)
  htmll = driver.page_source
  soupp = BeautifulSoup(htmll, "lxml")
  driver.close()
  try: 
    coords = (soupp.find("div", class_="toponym-card-title-view__coords-badge")).get_text(strip = True)
    lat = coords.split(", ")[0]
    lon = coords.split(", ")[1]
    return (lat, lon)
  except:
    return None, None
  


df = pd.DataFrame()
for article in dealer_articles:
  new = pd.DataFrame([get_data_from_articles(article)])
  df = pd.concat([df, new], ignore_index=True)


df['Количество машин в продаже'] = df['Количество машин в продаже'].fillna(0)
df['Количество машин в продаже'] = df['Количество машин в продаже'].astype(float)
df[["lat", "lon"]] = df["Адрес"].apply(lambda x: pd.Series(get_coorditanes(x)))

fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    #size='Количество машин в продаже',
    text='Название',
    mapbox_style="carto-positron",
    zoom=9,
    center={"lat": 55.751244, "lon": 37.618423}
)


fig.show()