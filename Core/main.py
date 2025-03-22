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
app = dash.Dash(__name__, external_stylesheets=[
dbc.themes.DARKLY
])


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
drom_cars_dataset = SupportMethods.get_google_sheet('Drom', '!A:L')
avito_cars_dataset = SupportMethods.get_google_sheet('Avito', '!A:L')


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
    autoscaut24_cars_dataset = autoscaut24_cars_dataset[autoscaut24_cars_dataset['модель'] != 'unknown']
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
    autoru_cars_dataset['Цена'] = autoru_cars_dataset['Цена'].apply(float)
    autoru_cars_dataset['Серия'] = autoru_cars_dataset['Серия'].str.upper().replace('_', ' ')
def preprocess_drom():
    drom_cars_dataset['Цена'] = drom_cars_dataset['Цена'].apply(float)
    drom_cars_dataset['Серия'] = drom_cars_dataset['Серия'].str.upper().replace('_', ' ')
def preprocess_avito():
    avito_cars_dataset['Цена'] = avito_cars_dataset['Цена'].apply(float)
    avito_cars_dataset['Серия'] = avito_cars_dataset['Серия'].str.upper().replace('_', ' ')


#endregion

preprocess_dubi_cars()
preprocess_autoscout24_cars()
preprocess_autoru()
preprocess_drom()
preprocess_avito()



#region Aggregation

def setup_index_to_model(df):
    df.index.name = "Модель"
    df.index = df.index.str.upper()
    df.index = df.index.str.replace('_', ' ')

def aggregate_avito():
    aggregated_avito_cars = avito_cars_dataset.groupby("Серия").mean(numeric_only=True)
    setup_index_to_model(aggregated_avito_cars)
    aggregated_avito_cars.columns = ["Цена, avito"]
    print(aggregated_avito_cars.index)
    return aggregated_avito_cars

def aggregate_autoru():
    aggregated_autoru_cars = autoru_cars_dataset.groupby("Серия").mean(numeric_only=True)
    setup_index_to_model(aggregated_autoru_cars)
    aggregated_autoru_cars.columns = ["Цена, autoru"]
    print(aggregated_autoru_cars.index)
    return aggregated_autoru_cars

def aggregate_drom():
    aggregated_drom_cars = drom_cars_dataset.groupby("Серия").mean(numeric_only=True)
    setup_index_to_model(aggregated_drom_cars)
    aggregated_drom_cars.columns = ["Цена, drom"]
    print(aggregated_drom_cars.index)
    return aggregated_drom_cars

def aggregate_autoscout():
    print(autoscaut24_cars_dataset["модель"])
    aggregated_autoscout24_cars = autoscaut24_cars_dataset.groupby("модель").mean(numeric_only=True)
    setup_index_to_model(aggregated_autoscout24_cars)
    aggregated_autoscout24_cars.columns = ["Цена, autoscout", "Тарифы, autoscout"]
    print(aggregated_autoscout24_cars.index)
    return aggregated_autoscout24_cars



def aggregate_dubicars():
    dubi_cars_dataset_tr = dubi_cars_dataset.transpose()
    dubi_cars_dataset_tr['price'] = dubi_cars_dataset_tr['price'].apply(float)
    dubi_cars_dataset_tr['imported prices'] = dubi_cars_dataset_tr['imported prices'].apply(float) #fixing mistakes of the past..

    aggregated_dubicars_cars = dubi_cars_dataset_tr.groupby("car_model").mean(numeric_only=True)
    setup_index_to_model(aggregated_dubicars_cars)
    aggregated_dubicars_cars.columns = ["Цена, dubicars", "Тарифы, dubicars"]
    return aggregated_dubicars_cars

#endregion

aggregated_autoru_cars = aggregate_autoru()
aggregated_autoscout24_cars = aggregate_autoscout()
aggregated_dubicars_cars = aggregate_dubicars()
aggregated_drom_cars = aggregate_drom()
aggregated_avito_cars = aggregate_avito()

def make_graph_transparent(fig):
    fig.update_layout(
    paper_bgcolor = 'rgba(0,0,0,0)',
    plot_bgcolor = 'rgba(0,0,0,0)',
    font=dict(family="Old Standard TT",
                  size=24,
                  color="rgb(255, 255, 255)")
    )



def get_figure_aggregated_comparison():
    df = pd.concat([aggregated_autoru_cars, aggregated_autoscout24_cars, aggregated_dubicars_cars,
                    aggregated_drom_cars, aggregated_avito_cars], join='inner', axis=1)
    df = df.dropna()
    print(df)
    fig = go.Figure(data=[
        go.Bar(name='Цена, autoru',         x=df.index, y=df["Цена, autoru"]),
        go.Bar(name='Цена, drom',      x=df.index, y=df["Цена, drom"]),
        go.Bar(name='Цена, avito',      x=df.index, y=df["Цена, avito"]),
        go.Bar(name='Цена, autoscout',      x=df.index, y=df["Цена, autoscout"] + df["Тарифы, autoscout"]),
        go.Bar(name='Цена, autoscout без тарифов', x=df.index, y=df["Цена, autoscout"]),
        go.Bar(name='Цена, dubicars',      x=df.index, y=df["Цена, dubicars"] + df["Тарифы, dubicars"]),
        go.Bar(name='Цена, dubicars без тарифов', x=df.index, y=df["Цена, dubicars"])
    ])
    fig.update_layout(barmode='group')
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    make_graph_transparent(fig)
    fig_graph = dcc.Graph(figure=fig, style={'height': '70vh'})
    return fig_graph


def get_dubi_cars_aggregated_info(all_cars_dataset):
    all_cars_dataset_2 = all_cars_dataset.copy()
    all_cars_dataset_2 = all_cars_dataset_2.transpose()
    grouped = all_cars_dataset_2.groupby("car_model")
    prices = grouped["price"].agg(["sum", "mean", "std"])
    fig = px.bar(x=prices.index, y=prices['mean'], width=None)
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    make_graph_transparent(fig)
    fig.update_layout(
        title="Цены моделей DubiCars",
        xaxis_title="Наименование модели",
        yaxis_title="Цена"
    )
    fig_graph = dcc.Graph(figure=fig)

    return fig_graph

def get_dubicars_bar_graph_from_variable_by_car(df):
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

    fig_prices = px.bar(temp, x='car', y='price', color='price_type', width=None)
    fig_prices.update_layout(xaxis={'categoryorder': 'total ascending'})

    fig_prices.add_hline(y=np.mean(df.loc['price']), line_width=3, line_dash="dash", line_color="green", name='Средняя цена до тарифов')
    fig_prices.add_hline(y=np.mean(df.loc['price']+ df.loc['imported prices']), line_width=3, line_dash="dash", line_color="red", annotation_text='Средняя цена после тарифов')
    make_graph_transparent(fig_prices)
    fig_prices.update_layout(
        title="Цены DubiCars",
        xaxis_title="Наименование позиции",
        yaxis_title="Цена"
    )


    fig_graph = dcc.Graph(figure=fig_prices, style={'height': '70vh'} )

    return fig_graph


def get_all_dubi_cars_by_type():
    grouped = dubi_cars_dataset.copy().transpose().groupby("fuel_type")
    prices = grouped["price"].agg(["count"])

    fig = px.pie(names=prices.index, values=prices['count'], width=None)
    make_graph_transparent(fig)

    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig.update_layout(
        title="Типы машин на DubiCars",
        xaxis_title="Топливо",
        yaxis_title="Количество позиций"
    )
    fig_graph = dcc.Graph(
        figure=fig,
        style={'height': '110vh'},
    )

    return fig_graph

def get_autoscout_cars_by_type():
    grouped = autoscaut24_cars_dataset.copy().groupby("вид топлива")
    prices = grouped["цена"].agg(["count"])
    fig = px.pie(names=prices.index, values=prices['count'], width=None)
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_graph = dcc.Graph(
        figure=fig,
        style={'height': '70vh'},
    )

    make_graph_transparent(fig)
    return fig_graph

def get_all_autoscout_cars_by_model():
    # В этом методе куча страданий с тем, чтобы нормально аггрегировать инфу, больно. чутка гпт под середену кода, ведь мой код не работал (в аналогичном методе дибикарз работал в то же время)
     #Но обработка автоскаут датасета ушла в начало теперь


    fig = px.bar(
        aggregated_autoscout24_cars,
        x=aggregated_autoscout24_cars.index,
        y=aggregated_autoscout24_cars['Цена, autoscout'],
        labels={'average_price': 'Средняя цена за модель', 'Модель': 'Модель'},
        title='Анализ цен моделей', width=None
    )
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})

    make_graph_transparent(fig)
    return dcc.Graph(figure=fig)

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

    fig_prices = px.bar(temp, x='car', y='price', color='price_type', width=None, height=900)
    fig_prices.update_layout(xaxis={'categoryorder': 'total ascending'})
    fig_prices.update_layout(
        title="Предложения машин на AutoScout",
        xaxis_title="Наименоваании позиции",
        yaxis_title="Цена"
    )
    make_graph_transparent(fig_prices)
    return dcc.Graph(figure=fig_prices,
        style={'height': '120vh'})

def generate_graphs():
    return get_all_dubi_cars_by_type(), get_autoscout_cars_by_type()

dubi_cars_graph_by_id = get_dubicars_bar_graph_from_variable_by_car(dubi_cars_dataset)
dubi_cars_graph_by_model = get_dubi_cars_aggregated_info(dubi_cars_dataset)
comparison_graph = get_figure_aggregated_comparison()

scout_allcars_graph = get_all_autoscout_cars()
scout_models_graph = get_all_autoscout_cars_by_model()

dubi_cars_type, autoscout_cars_type = generate_graphs()


card_dubicars = dbc.Card([
    dbc.CardHeader('Данные с DubiCars'),
    dbc.CardBody([
        dbc.Row([
            dbc.Col(dubi_cars_graph_by_id),
        ]),
        dbc.Row([
            dbc.Col(dubi_cars_graph_by_model),
        ])
    ], style={'margin': '20px'}),
    dbc.CardFooter("DubiCars меет небольшое предложение авто, зато широкий спект моделей"),

])

card_autoscout = dbc.Card([
    dbc.CardHeader('Данные с AutoScout24'),
    dbc.CardBody([
    dbc.Row([
            dbc.Col(scout_allcars_graph),
        ]),
        dbc.Row([
            dbc.Col(scout_models_graph),
        ])
    ]),
    dbc.CardFooter("AutoScout дает широкий спектрр предложений, но в среднем цена бедт значительно повышаться после ввоза"),
], style={'margin': '20px'})

card_comparisons = dbc.Card([
    dbc.CardHeader('Сравнение средних ценовых показателей моделей'),
    dbc.CardBody([comparison_graph]),
    dbc.CardFooter("Импорт значительно снижает возможности заработка на ввозе автомобилей в Россию, но внутри страны, цены еще не подтянулсь к уровню других стран + импорт"),
], style={'margin': '20px'})


# Макет приложения
app.layout = dbc.Container([
    html.H1('GetCarz Dashboard', className='text-center text-primary mb-4'),
    dbc.Col([
card_dubicars, card_autoscout,

        dbc.Card([
            dbc.CardBody([
                dubi_cars_type,
                autoscout_cars_type
            ]),
        ], style={'margin': '15px'}),
        card_comparisons
    ])
])#,fluid=True


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)