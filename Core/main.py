import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import SupportMethods

SupportMethods.hash_currency("EUR") #precalculate currency to make life faster without 10k requests

# Загрузка данных
df = px.data.iris()


# Инициализация приложения Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Основные статистики
def calculate_statistics(species_filter):
    filtered_df = df[df['species'] == species_filter] if species_filter else df
    stats = {
        'Количество измерений': len(filtered_df),
        'Средняя длина лепестков': round(filtered_df['petal_length'].mean(), 2),
        'Средняя ширина лепестков': round(filtered_df['petal_width'].mean(), 2)
    }
    return stats

# Графики, взято из лекций
def generate_graphs(species_filter):
    filtered_df = df[df['species'] == species_filter] if species_filter else df

    fig_scatter = px.scatter(
        filtered_df, x='sepal_length', y='sepal_width', color='species',
        title='Матрица рассеяния: длина и ширина чашелистков'
    )

    fig_hist_petal_length = px.histogram(
        filtered_df, x='petal_length', color='species',
        title='Распределение длины лепестков'
    )

    fig_hist_petal_width = px.histogram(
        filtered_df, x='petal_width', color='species',
        title='Распределение ширины лепестков'
    )

    return fig_scatter, fig_hist_petal_length, fig_hist_petal_width

# Макет приложения
app.layout = dbc.Container([
    html.H1('Дашборд данных', className='text-center text-primary mb-4'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Фильтр по видам'),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='species-dropdown',
                        options=[{'label': species, 'value': species} for species in df['species'].unique()] + [{'label': 'Все виды', 'value': ''}],
                        value='',
                        placeholder='Выберите вид ирисов'
                    )
                ])
            ])
        ], md=4),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Основные статистики'),
                dbc.CardBody([
                    html.P(id='measurement-count', className='card-text'),
                    html.P(id='avg-petal-length', className='card-text'),
                    html.P(id='avg-petal-width', className='card-text'),
                ])
            ])
        ], md=8)
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='car_model-prices-pre-tariff'), md=12),
        dbc.Col(dcc.Graph(id='car_model-prices-post-tariff'), md=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='hist-petal-length'), md=6),
        dbc.Col(dcc.Graph(id='hist-petal-width'), md=6),
    ]),

], fluid=True)

# Коллбэки для обновления статистики и графиков
@app.callback(
    [Output('measurement-count', 'children'),
     Output('avg-petal-length', 'children'),
     Output('avg-petal-width', 'children'),
     Output('scatter-graph', 'figure'),
     Output('hist-petal-length', 'figure'),
     Output('hist-petal-width', 'figure')],
    [Input('species-dropdown', 'value')]
)
def update_dashboard(species_filter):
    # Обновление статистик
    stats = calculate_statistics(species_filter)
    measurement_count = f"Количество измерений: {stats['Количество измерений']}"
    avg_petal_length = f"Средняя длина лепестков: {stats['Средняя длина лепестков']} см"
    avg_petal_width = f"Средняя ширина лепестков: {stats['Средняя ширина лепестков']} см"

    # Обновление графиков
    fig_scatter, fig_hist_petal_length, fig_hist_petal_width = generate_graphs(species_filter)

    return measurement_count, avg_petal_length, avg_petal_width, fig_scatter, fig_hist_petal_length, fig_hist_petal_width

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)