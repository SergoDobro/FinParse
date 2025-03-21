import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import SupportMethods

print(SupportMethods.get_google_sheet('DubiCars'))


# Инициализация приложения Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Графики, взято из лекций
def generate_graphs():

    df = SupportMethods.get_google_sheet('DubiCars')
    fig_scatter = px.scatter(
        df, x=df[0], y=df[1],
        title='Матрица рассеяния: длина и ширина чашелистков'
    )
    fig_scatter.show()

    return fig_scatter, fig_scatter, fig_scatter


gfs, gfs2, gf3 = generate_graphs()


# Макет приложения
app.layout = dbc.Container([
    html.H1('Дашборд данных', className='text-center text-primary mb-4'),

    dbc.Row([
        dbc.Col(gfs, md=12),
        dbc.Col(gfs, md=12)
    ]),


], fluid=True)


# Запуск приложения
if __name__ == '__main__':
    SupportMethods.hash_currency("EUR")  # precalculate currency to make life faster without 10k requests
    app.run(debug=True)