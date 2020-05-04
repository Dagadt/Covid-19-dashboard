import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_csv("C:\\Dagadt\\scripts\\dash-apps\\covid-19\\datasets\\covid-19-final_2020-04-19.csv")
dff = df[df["ObservationDate"]=="04/19/2020"].sum()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


body = html.Div([
    dbc.Row([
        dbc.Col(html.Div(html.H1("Covid-19 Worldwide", className="display-3")), lg=4, md=12, sm=12,  xs=12, className="site-header")
        ],
        justify="center"), 
    dbc.Row([
        dbc.Col(html.Div(dbc.Alert(html.H1(children="Confirmed: %s" % dff.loc["Confirmed"]), color="primary")), lg=4, md=4, sm=12,  xs=12, className="summed-figs"), 
        dbc.Col(html.Div(dbc.Alert(html.H1(children="Deaths: %s" % dff.loc["Deaths"]), color="primary")), lg=4, md=4, sm=12, xs=12, className="summed-figs"),
        dbc.Col(html.Div(dbc.Alert(html.H1(children="Recovered: %s" % dff.loc["Recovered"]), color="primary")), lg=4, md=4, sm=12, xs=12, className="summed-figs")
        ],
        justify="center"),
    dbc.Row([
        dbc.Col(html.Div(
        className="radio-group",
        children=[
        dcc.RadioItems(
            id="input_case",
            options=[
                {'label': 'Confirmed Cases', 'value': 'Confirmed'},
                {'label': 'Deaths', 'value': 'Deaths'}     
            ],
            value='Deaths',
            )
        ]), lg=4, md=4, sm=12,  xs=12, className="summed-figs"), 
        dbc.Col(html.Div(children=[
        dcc.Dropdown(
            id="input_countries",
            options=[{'label': i.title(), 'value': i} for i in df["Country/Region"].unique()],
            multi=True,
            value=['US', "United Kingdom"]
            ),
        ]), lg=4, md=4, sm=12, xs=12, className="summed-figs"),
        ],
        justify="center"),
        dbc.Row([dbc.Col(html.Div(children=[
        dcc.Graph(
            id='display_selected_values',
        )]), lg=4, md=4, sm=12,  xs=12, className="summed-figs"), 
        dbc.Col(html.Div(children=[
        dcc.Graph(
            id='display_selected_values_2',
        )]), lg=4, md=4, sm=12, xs=12, className="summed-figs"),
        ],
        justify="center")
    
    ])



app.layout = html.Div([body])

if __name__ == "__main__":
    app.run_server(debug = True)









