import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import plotly.express as px
from GetCarz.Core import support_methods

def has_bad_attrs(element):
  bad_ids = ['app-promotion', 'ad-intersect']
  for id in bad_ids:
    if ('id' in element.attrs and id in element['id']):
      return True

  bad_classes = ['serp-banner', 'serp-teads', 'advergic']
  for cl in bad_classes:
    if (cl in element['class']):
      return True
  return False


def get_dubicars_page(page):
  data = requests.get('https://www.dubicars.com/search?o=&did=&gen=&ul=RU&ma=13&mo=0&b=&set=bu&eo=export-only&stsd=&cr=USD&cy=&co=&s=&gi=&f=&g=&l=&st=&page='+str(page))
  soup = BeautifulSoup(data.content, 'html.parser')
  main_elements = soup.find_all("div", {"class" : "main"})
  cars = main_elements[0].find_all(recursive=False)[0].find_all(recursive=False)[0].find_all(recursive=False)



  cars = [car for car in cars if
        not has_bad_attrs(car)]



  cars_jsoned = [json.loads(car['data-ga4-detail']) for car in cars]

  data_frame_with_cars = pd.DataFrame(index=[car_param_name for car_param_name in cars_jsoned[0].keys()])
  for car in cars_jsoned:
    data_frame_with_cars[car['car_make'] + '_' + car['car_model'] + '_' + str(car['item_id'])] = [car_param for car_param in car.values()]

  print(f'[log]: processed page {page}')

  return data_frame_with_cars

def get_total_pages():
  data = requests.get('https://www.dubicars.com/search?o=&did=&gen=&ul=RU&ma=13&mo=0&b=&set=bu&eo=export-only&stsd=&cr=USD&cy=&co=&s=&gi=&f=&g=&l=&st=&page=1')
  soup = BeautifulSoup(data.content, 'html.parser')
  main_elements = soup.find_all("div", {"class" : "main"})
  return int(main_elements[1].find_all("li", {"class" : "base-btn"})[-1].find_all()[0].get_text())

def get_all_cars():
  total_pages = get_total_pages()
  print("[log]: total pages: "+str(total_pages))
  return pd.concat([get_dubicars_page(i) for i in range(total_pages)], axis = 1)



def refactor_data(cars_data):
  new_data = cars_data.copy()
  new_data.loc['price'].apply(int)
  new_data.loc['price'] = new_data.loc['price']*23.4 #converting to rubbles #TODO add converter
  mask = (new_data.loc['price'] > 0)
  #display(new_data.loc[:, mask])
  new_data = new_data.loc[:, mask]

  return new_data



def process_DubiCars():
  all_cars = get_all_cars()
  all_cars_dataset = refactor_data(all_cars)



  fig = px.bar(x=all_cars_dataset.columns, y=all_cars_dataset.loc['price'])
  fig.update_layout( xaxis={'categoryorder':'total ascending'})

  #fig.show()

  import numbers
  all_cars_dataset_2 = all_cars_dataset.copy()
  all_cars_dataset_2 = all_cars_dataset_2.transpose()
  grouped = all_cars_dataset_2.groupby("car_model")
  #display(grouped["price"].agg(["sum", "mean", "std"]))

  all_cars_dataset_2 = grouped.apply(lambda x: x).transpose()

  #display(all_cars_dataset_2)


  prices = grouped["price"].agg(["sum", "mean", "std"]);

  fig = px.bar(x=prices.index, y=prices['mean'])
  fig.update_layout( xaxis={'categoryorder':'total ascending'})

  #fig.show()
  support_methods.set_google_sheet(all_cars_dataset, 'DubiCars')


# Запуск парсинга
if __name__ == '__main__':
  process_DubiCars()