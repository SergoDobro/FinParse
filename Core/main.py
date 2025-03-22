import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

import SupportMethods
import plotly.graph_objects as go
import car_import_price_calculator as import_calculator

SupportMethods.hash_currency("EUR")  # precalculate currency to make life faster without 10k requests
print(SupportMethods.get_hashed_currency("EUR"))

# Инициализация приложения Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def convert_autoscout_fuel_naming(name):
    """Helper method to fix formatting"""
    fuels = {"Дизель":'diesel', "Бензин":'gasoline', "e":'electro'
             , "Электро":'electro'
             , "Гибрид":'gasoline'}
    if name not in fuels.keys():
        print(name)
        return 'electro'
    return fuels[name]
def check_сonvert(element):
    """Helper method to fix formatting"""
    if type(element) is int or type(element) is float:
        return element
    if type(element) is str:
        return float(element.replace(',', '.'))
    if type(element.tolist()) is float:
        return element.tolist()
    return element.tolist()[0]



#preproooocessing
dubi_cars_dataset = SupportMethods.get_google_sheet('DubiCars', '!1:20')
autoscaut24_cars_dataset = SupportMethods.get_google_sheet('AutoScout24', '!A:J')
autoru_cars_dataset = SupportMethods.get_google_sheet('AutoRu', '!A:L')


#region Preprocessing

def preprocess_dubi_cars():
    dubi_cars_dataset.loc['price'] = dubi_cars_dataset.loc['price'].apply(float)
    imported = [import_calculator.count_import_price_estimation(
        check_сonvert(dubi_cars_dataset[dubi_cars_dataset.columns[i]].loc["price"]), 2200,
        2025 - int(check_сonvert(dubi_cars_dataset[dubi_cars_dataset.columns[i]].loc["car_year"])),
        350, 'electro')
        for i in range(len(dubi_cars_dataset.columns))]
    dubi_cars_dataset.loc['imported prices'] = imported
def preprocess_autoscout24_cars():
    global autoscaut24_cars_dataset
    autoscaut24_cars_dataset = autoscaut24_cars_dataset.reindex()
    autoscaut24_cars_dataset = autoscaut24_cars_dataset[autoscaut24_cars_dataset['мощность'] != '']
    autoscaut24_cars_dataset = autoscaut24_cars_dataset[autoscaut24_cars_dataset['вид топлива'] != '2']
    autoscaut24_cars_dataset = autoscaut24_cars_dataset[autoscaut24_cars_dataset['вид топлива'] != 'з']
    autoscaut24_cars_dataset = autoscaut24_cars_dataset[autoscaut24_cars_dataset['вид топлива'] != 'о']
    autoscaut24_cars_dataset[autoscaut24_cars_dataset['вид топлива'] == 'e'] = 'electro'
    autoscaut24_cars_dataset['цена'] = pd.to_numeric(
            autoscaut24_cars_dataset['цена'].str.replace('[^\d.]', '', regex=True), #gpt magic to convert prices correctly
            errors='coerce'
        ) * float(SupportMethods.get_hashed_currency("EUR"))
    autoscaut24_cars_dataset = autoscaut24_cars_dataset.loc[(autoscaut24_cars_dataset=='').any(axis=1)]

    #GPT (my cleaning failed here): Clean and convert numeric columns
    def process_int_power(rowint_power):
        if rowint_power == '':
            return 200
        return int(rowint_power)
    def process_int_year(rowint_power):
        if rowint_power == '':
            return 2025
        return int(rowint_power)

    autoscaut24_cars_dataset['imported prices'] = autoscaut24_cars_dataset.apply(lambda row:
            import_calculator.count_import_price_estimation(check_сonvert(row['цена']), 2000,  #volume is estimated cubic santimeters
                                                            2025 - process_int_year(row['год выпуска']),
                                                            process_int_power(row['мощность']),
                                                            convert_autoscout_fuel_naming(row['вид топлива']))
                                                                                 , axis=1)

    autoscaut24_cars_dataset['модель'] = autoscaut24_cars_dataset['модель'].str.upper().replace('_', ' ')
def preprocess_autoru():
    print(autoru_cars_dataset.columns)
    print(autoru_cars_dataset.index)
    print(autoru_cars_dataset)
    autoru_cars_dataset['Цена'] = autoru_cars_dataset['Цена'].apply(float)
    autoru_cars_dataset['Серия'] = autoru_cars_dataset['Серия'].str.upper().replace('_', ' ')


#endregion

preprocess_dubi_cars()
preprocess_autoscout24_cars()
preprocess_autoru()



#region Aggregation

def aggregate_autoru():
    aggregated_autoru_cars = autoru_cars_dataset.groupby("Серия").mean(numeric_only=True)
    aggregated_autoru_cars.index.name = "Модель"
    aggregated_autoru_cars.index = aggregated_autoru_cars.index.str.upper()
    aggregated_autoru_cars.index = aggregated_autoru_cars.index.str.replace('_', ' ')
    aggregated_autoru_cars.columns = ["Цена, autoru"]
    print(aggregated_autoru_cars.index)
    return aggregated_autoru_cars

def aggregate_autoscout():
    print(autoscaut24_cars_dataset["модель"])
    aggregated_autoscout24_cars = autoscaut24_cars_dataset.groupby("модель").mean(numeric_only=True)
    aggregated_autoscout24_cars.index.name = "Модель"
    aggregated_autoscout24_cars.index = aggregated_autoscout24_cars.index.str.upper()
    aggregated_autoscout24_cars.index = aggregated_autoscout24_cars.index.str.replace('_', ' ')
    aggregated_autoscout24_cars.columns = ["Цена, autoscout", "Тарифы, autoscout"]
    print(aggregated_autoscout24_cars.index)
    return aggregated_autoscout24_cars



def aggregate_dubicars():
    dubi_cars_dataset_tr = dubi_cars_dataset.transpose()
    dubi_cars_dataset_tr['price'] = dubi_cars_dataset_tr['price'].apply(float)
    dubi_cars_dataset_tr['imported prices'] = dubi_cars_dataset_tr['imported prices'].apply(float)

    print(dubi_cars_dataset_tr["car_model"])
    aggregated_dubicars_cars = dubi_cars_dataset_tr.groupby("car_model").mean(numeric_only=True)
    aggregated_dubicars_cars.index.name = "Модель"
    aggregated_dubicars_cars.index = aggregated_dubicars_cars.index.str.upper()
    aggregated_dubicars_cars.index = aggregated_dubicars_cars.index.str.replace('_', ' ')
    aggregated_dubicars_cars.columns = ["Цена, dubicars", "Тарифы, dubicars"]
    print(aggregated_dubicars_cars.index)
    return aggregated_dubicars_cars

#endregion

aggregated_autoru_cars = aggregate_autoru()
aggregated_autoscout24_cars = aggregate_autoscout()
aggregated_dubicars_cars = aggregate_dubicars()

def get_figure_aggregated_comparison():
    df = pd.concat([aggregated_autoru_cars, aggregated_autoscout24_cars, aggregated_dubicars_cars], join='inner', axis=1)
    df = df.dropna()
    print(df)
    fig = go.Figure(data=[
        go.Bar(name='Цена, autoru',         x=df.index, y=df["Цена, autoru"]),
        go.Bar(name='Цена, autoscout',      x=df.index, y=df["Цена, autoscout"] + df["Тарифы, autoscout"]),
        go.Bar(name='Цена, autoscout без тарифов', x=df.index, y=df["Цена, autoscout"]),
        go.Bar(name='Цена, dubicars',      x=df.index, y=df["Цена, dubicars"] + df["Тарифы, dubicars"]),
        go.Bar(name='Цена, dubicars без тарифов', x=df.index, y=df["Цена, dubicars"])
    ])
    fig.update_layout(barmode='group')

    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_graph = dcc.Graph(figure=fig, style={'height': '70vh'})
    return fig_graph

get_figure_aggregated_comparison()

def get_dubi_cars_aggregated_info(all_cars_dataset):
    all_cars_dataset_2 = all_cars_dataset.copy()
    all_cars_dataset_2 = all_cars_dataset_2.transpose()
    grouped = all_cars_dataset_2.groupby("car_model")
    prices = grouped["price"].agg(["sum", "mean", "std"])
    fig = px.bar(x=prices.index, y=prices['mean'])
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_graph = dcc.Graph(figure=fig, style={'height': '70vh'})
    return fig_graph

def get_bar_graph_from_variable_by_car(df):
    df = df.loc[:, ~df.columns.duplicated()]

    temp = pd.DataFrame(columns=['car','price_type', 'price', 'import price'])
    temp['car'] = df.columns
    for i in range(len(df.columns)): #double bar chart
        temp.loc[2*i, "car"] = df.columns[i]
        temp.loc[2*i, "price_type"] = 'base'
        temp.loc[2*i, "price"] = float(check_сonvert(df[df.columns[i]]['price']))

        temp.loc[2*i+1, "car"] = df.columns[i]
        temp.loc[2*i+1, "price_type"]= 'tariffs'
        temp.loc[2*i+1, "price"] = float(check_сonvert(df[df.columns[i]]['imported prices']))

    fig_prices = px.bar(temp, x='car', y='price', color='price_type')
    fig_prices.update_layout(xaxis={'categoryorder': 'total ascending'})

    fig_prices.add_hline(y=np.median(df.loc['price']), line_width=3, line_dash="dash", line_color="green")
    fig_prices.add_hline(y=np.median(df.loc['price']+ df.loc['imported prices']), line_width=3, line_dash="dash", line_color="red")
    fig_prices.update_layout(
        title="DubiCars cars prices",
        xaxis_title="Car id",
        yaxis_title="price"
    )


    fig_graph = dcc.Graph(figure=fig_prices, style={'height': '70vh'} )

    return fig_graph

def get_all_dubi_cars():
    dubi_all_prices = get_bar_graph_from_variable_by_car(dubi_cars_dataset)
    dubi_agregated_prices = get_dubi_cars_aggregated_info(dubi_cars_dataset)
    return dubi_all_prices, dubi_agregated_prices

def get_all_dubi_cars_by_type():
    grouped = dubi_cars_dataset.copy().transpose().groupby("fuel_type")
    prices = grouped["price"].agg(["count"])

    fig = px.pie(names=prices.index, values=prices['count'])
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_graph = dcc.Graph(
        figure=fig,
        style={'height': '70vh'},
    )

    return fig_graph

def get_all_autoscout_cars_by_type():
    grouped = autoscaut24_cars_dataset.copy().groupby("вид топлива")
    prices = grouped["цена"].agg(["count"])
    fig = px.pie(names=prices.index, values=prices['count'])
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_graph = dcc.Graph(
        figure=fig,
        style={'height': '70vh'},
    )

    return fig_graph

def get_all_autoscout_cars():
    # В этом методе куча страданий с тем, чтобы нормально аггрегировать инфу, больно. чутка гпт под середену кода, ведь мой код не работал (в аналогичном методе дибикарз работал в то же время)
     #Но обработка автоскаут датасета ушла в начало теперь
    grouped = autoscaut24_cars_dataset.groupby('модель', as_index=False).agg(
        average_price=('цена', 'mean'),
        total_imports=('imported prices', 'sum'),
        price_deviation=('цена', 'std')
    )

    fig = px.bar(
        grouped,
        x='Модель',
        y='Средняя цена за модель',
        labels={'average_price': 'Средняя цена за модель', 'модель': 'Модель'},
        title='Анализ цен моделей'
    )
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    return dcc.Graph(id='price-analysis', figure=fig, style={'height': '70vh'})

def get_all_autoscout_cars():
    _temp = autoscaut24_cars_dataset.transpose()
    _temp.columns = _temp.loc['Полное название модели']
    df = _temp.loc[:, ~_temp.columns.duplicated()]
    temp = pd.DataFrame(columns=['car', 'price_type', 'price', 'import price'])
    temp['car'] = df.columns
    for i in range(len(df.columns)):  # double bar chart Полное название модели
        temp.loc[2 * i, "car"] = df.columns[i]
        temp.loc[2 * i, "price_type"] = 'base'
        temp.loc[2 * i, "price"] = float(check_сonvert(df[df.columns[i]]['цена']))

        temp.loc[2 * i + 1, "car"] = df.columns[i]
        temp.loc[2 * i + 1, "price_type"] = 'tariffs'
        temp.loc[2 * i + 1, "price"] = float(check_сonvert(df[df.columns[i]]['imported prices']))

    fig_prices = px.bar(temp, x='car', y='price', color='price_type')
    fig_prices.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_graph = dcc.Graph(
        figure=fig_prices,
        style={'height': '70vh'},
    )

    return fig_graph

def generate_graphs():
    autoscout_all_prices = get_all_autoscout_cars()
    dubi_all_prices, dubi_agregated_prices = get_all_dubi_cars()
    return dubi_all_prices, dubi_agregated_prices, autoscout_all_prices, get_all_dubi_cars_by_type(), get_all_autoscout_cars_by_type()

gfs, gfs2, scout, dubi_cars_type, autoscout_cars_type = generate_graphs()

# Макет приложения
app.layout = dbc.Container([
    html.H1('Дашборд данных', className='text-center text-primary mb-4'),

    dbc.Row([
        dbc.Col(gfs),
    ]),
    dbc.Row([
        dbc.Col(gfs2),
        dbc.Col(scout)
    ]),
    dbc.Row([
        dbc.Col(dubi_cars_type, md=12),
        dbc.Col(autoscout_cars_type, md=12)
    ]),
    dbc.Row(
        [get_figure_aggregated_comparison()]
    )


])


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)