import requests
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
import pandas as pd
import gspread_dataframe as gd
from os import listdir
from os.path import isfile, join

currencies = {}
def get_hashed_currency(currency):
    """Just a method to convert money types, but it """
    if currency not in currencies:
        hash_currency(currency)

    return  currencies[currency]

def hash_currency(currency):
    currencies[currency] = get_currency(currency)

def get_currency(currency):
    """
    Just a method to convert money types
    """
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    print (data['Valute'][currency]['Value'])

def set_google_sheet(df, sheet):
    CLIENT_SECRETS_FILE = '../DataParsers/credentials.json'
    SPREADSHEET_ID = '1UR_AI0_ZLKf_jYTVaCUbjadquveFLJlGjR-tUcELD0Y'

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    gc = gspread.authorize(creds)

    # Connecting with `gspread` here
    mySheet = gc.open_by_key(SPREADSHEET_ID)

    try:
        wks = mySheet.worksheet(sheet)
    except gspread.exceptions.WorksheetNotFound:
        wks = mySheet.add_worksheet(sheet, "999", "20")

    gd.set_with_dataframe(wks, df.reset_index())



def get_google_sheet(sheet):
    print(listdir('GetCarz/Core'))
    file = open("GetCarz/Core/google_sheets_api")
    API_KEY = file.read()
    file.close()

    SPREADSHEET_ID = '1UR_AI0_ZLKf_jYTVaCUbjadquveFLJlGjR-tUcELD0Y'

    RANGE_NAME = str(sheet)+'!1:20'

    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}?key={API_KEY}'

    # Выполняем GET-запрос
    response = requests.get(url)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        values = data.get('values', [])
        pdas = pd.DataFrame(columns=values[0], data=values[1:])
    else:
        print(f"Ошибка: {response.status_code}")

    #pdas.columns = pdas.iloc[0]
    pdas = pdas.set_index(pdas.columns[0])

    pdas.loc['price'] = pdas.loc['price'].apply(float)

    return pdas

# Запуск приложения
if __name__ == '__main__':
    get_google_sheet('DubiCars')

#Example: (Почему-то 2 авторизации)
#dict = {'name':["aparna", "pankaj", "sudhir", "Geeku"],
#        'degree': ["MBA", "BCA", "M.Tech", "MBA"],
#        'score':[90, 40, 80, 98]}

#df = pd.DataFrame(dict)
#SupportMethods.get_google_sheet(df, 'sheet1')