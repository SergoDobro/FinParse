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


# Инициализация приложения Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def checkConvert(element):
    if type(element) is int or type(element) is float:
        return element
    if type(element.tolist()) is float:
        return element.tolist()
    print(type(element.tolist()))
    print(element.tolist()[0])
    return element.tolist()[0]

def get_dubi_cars_aggregated_info(all_cars_dataset):
    all_cars_dataset_2 = all_cars_dataset.copy()
    all_cars_dataset_2 = all_cars_dataset_2.transpose()
    grouped = all_cars_dataset_2.groupby("car_model")

    all_cars_dataset_2 = grouped.apply(lambda x: x).transpose()


    prices = grouped["price"].agg(["sum", "mean", "std"]);

    fig = px.bar(x=prices.index, y=prices['mean'])
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})

    fig_graph = dcc.Graph(
                          figure=fig,
                          style={'height': '70vh'},  # Установка высоты графика
                          )


    return fig_graph

def get_bar_graph_from_variable_by_car(df):
    df = df.loc[:, ~df.columns.duplicated()]

    temp = pd.DataFrame(columns=['car','price_type', 'price', 'import price'])
    temp['car'] = df.columns
    for i in range(len(df.columns)):
        temp.loc[2*i, "car"] = df.columns[i]
        temp.loc[2*i, "price_type"] = 'base'
        temp.loc[2*i, "price"] = float(checkConvert(df[df.columns[i]]['price']))
        #temp.loc[i, "tariff"] = float(checkConvert(df[df.columns[i]]['imported prices']))

        temp.loc[2*i+1, "car"] = df.columns[i]
        temp.loc[2*i+1, "price_type"]= 'tariffs'
        temp.loc[2*i+1, "price"] = float(checkConvert(df[df.columns[i]]['imported prices']))
        #temp.loc[i + 1, "tariff"] = float(checkConvert(df[df.columns[i]]['imported prices']))
    fig_prices = px.bar(temp, x='car', y='price', color='price_type')
    fig_prices.update_layout(xaxis={'categoryorder': 'total ascending'})


    fig_prices.add_hline(y=np.median(df.loc['price']), line_width=3, line_dash="dash", line_color="green")
    fig_prices.add_hline(y=np.median(df.loc['price']+ df.loc['imported prices']), line_width=3, line_dash="dash", line_color="red")
    # Update layout
    fig_prices.update_layout(
        title="DubiCars cars!",
        xaxis_title="Car id",
        yaxis_title="price"
    )


    fig_graph = dcc.Graph(id='scatter-graph',
                          figure=fig_prices,
                          style={'height': '70vh'},  # Установка высоты графика
                          )



    return fig_graph

def get_all_dubi_cars():
    dubi_cards_dataset = SupportMethods.get_google_sheet('DubiCars')
    imported = [import_calculator.count_import_price_estimation(
        checkConvert(dubi_cards_dataset[dubi_cards_dataset.columns[i]].loc["price"]), 2000, 3, 150, 'electro')
        for i in range(len(dubi_cards_dataset.columns))]

    dubi_cards_dataset.loc['imported prices'] = imported

    dubi_all_prices = get_bar_graph_from_variable_by_car(dubi_cards_dataset)
    dubi_agregated_prices = get_dubi_cars_aggregated_info(dubi_cards_dataset)
    #fig_graph_importing_prices = get_bar_graph_from_variable_by_car(dubi_cards_dataset, 'imported prices', ['red'])

    return dubi_all_prices, dubi_agregated_prices


def generate_graphs():
    dubi_all_prices, dubi_agregated_prices = get_all_dubi_cars()
    return dubi_all_prices, dubi_agregated_prices

gfs, gfs2 = generate_graphs()


# Макет приложения
app.layout = dbc.Container([
    html.H1('Дашборд данных', className='text-center text-primary mb-4'),

    dbc.Row([
        dbc.Col(gfs),
        dbc.Col(gfs2)
    ]),


])


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)