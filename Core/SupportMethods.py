import requests
def ConvertToRubbles(currency):
    '''
    Just a method to convert money types
    '''
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    print (data['Valute'][currency]['Value'])