import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import Flask
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pandas.io.json import json_normalize 
import json
from urllib.request import urlopen
import datetime

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, external_stylesheets=[dbc.themes.BOOTSTRAP],  server = server)
# app.config.supress_callback_exceptions = True

#Custome Header
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Covid-19 Dashboard</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

d = pd.read_json("https://pomber.github.io/covid19/timeseries.json")
iso_alpha_df = pd.read_csv("datasets/iso_alpha.csv")
with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
    countries = json.load(response)


df = pd.DataFrame()

for i in d.columns:
    dff = d[i]
    normalized_dff = json_normalize(dff)
    normalized_dff["country"] = i
    if df.empty:
        df = normalized_dff
    else:
        df = df.append(normalized_dff, ignore_index=True)

iso_alpha_df.rename(columns={"alpha-3": "alpha_code"}, inplace=True)
last_day = df["date"].unique().tolist()[-1]



#create a dictionary of dataframe
iso_alpha_dict = dict(zip(iso_alpha_df.name, iso_alpha_df.alpha_code))


colorscale_confirmed = ["#4292c6", "#ffe6e6"]

colorscale_deaths = ["#ff1414", "#4292c6", ]

colorscale_recovered = ["#2ed14f", "#ffe6e6"]

dff = df[df["date"]==last_day].sum()

body = html.Div([
        dcc.Loading(children=[
            dbc.Row([
                dbc.Col(
                    html.Div(
                        html.H1("Covid-19 Worldwide", className="display-4")
                    ), lg=4, md=12, sm=12,  xs=12, className="site-header")
            ],
            justify="center"), 
            dbc.Row([
                dbc.Col(
                    html.Div(
                        html.H4("Last updated: %s" % datetime.datetime.strptime(last_day, '%Y-%m-%d').date())
                    ), lg=4, md=12, sm=12,  xs=12, className="last_update")
            ],
            justify="center"),
            dbc.Row([
                dbc.Col(
                    html.Div(
                        dbc.Alert(
                            html.H1(children="Total Confirmed: %s" % format(dff.loc["confirmed"], ",")
                        ), color="primary")
                    ), lg=4, md=4, sm=12,  xs=12, className="summed-figs"), 
                dbc.Col(
                    html.Div(
                        dbc.Alert(
                            html.H1(children="Total Deaths: %s" % format(dff.loc["deaths"], ",")
                        ), color="primary")
                    ), lg=4, md=4, sm=12, xs=12, className="summed-figs"),
                dbc.Col(
                    html.Div(
                        dbc.Alert(
                            html.H1(children="Total Recovered: %s" % format(dff.loc["recovered"], ",")
                        ), color="primary")
                    ), lg=4, md=4, sm=12, xs=12, className="summed-figs")
            ],
            justify="center"),
    
            dbc.Row([
                dbc.Col(
                    html.Div(
                        className="country_stat_wrapper",
                        children=[
                            dbc.Row([
                                dbc.Col(
                                    html.Div(
                                        className="custom-radio, radio-group",
                                        children=[
                                            dbc.FormGroup([
                                                dbc.RadioItems(
                                                    options=[
                                                        {'label': 'Confirmed Cases', 'value': 'confirmed'},
                                                        {'label': 'Deaths', 'value': 'deaths'},
                                                        {'label': 'Recovered', 'value': 'recovered'}
                                                    ],
                                                    value="confirmed",
                                                    id="input_case",
                                                    inline=True
                                                )
                                            ])
                                        ]
                                    ), lg=4, md=4, sm=12,  xs=12, width=3, className="inputs"), 
                                dbc.Col(
                                    html.Div(
                                        className="custom-dropdown",
                                        children=[
                                            dcc.Dropdown(
                                                id="input_countries",
                                                options=[{'label': i.title(), 'value': i} for i in df["country"].unique()],
                                                multi=True,
                                                value=["US", "China", "United Kingdom"]
                                            )
                                        ]
                                    ), lg=4, md=4, sm=12, xs=12, className="inputs"),
                            ],
                            justify="center"
                            ),
                            dbc.Row([
                                dbc.Col(
                                    html.Div(
                                        className="graph-wrapper", 
                                        children=[
                                            dbc.Col(
                                            html.Div(
                                                dbc.Alert(
                                                    html.H3(children="Covid-19 Around the World"), color="light")
                                            ), lg=6, md=6, sm=12, xs=12, className="graph-title"),
                                            dcc.Graph(
                                                id='display_selected_values',
                                            )
                                        ]
                                    ), lg=6, md=12, sm=12,  xs=12, className="summed-figs"), 
                                dbc.Col(
                                    html.Div(
                                        className="graph-wrapper", 
                                        children=[
                                            dbc.Col(
                                                html.Div(
                                                    dbc.Alert(
                                                        html.H3(children="Compared Daily Growth"), color="light")
                                                ), lg=6, md=6, sm=12, xs=12, className="graph-title"),
                                                dcc.Graph(
                                                    id='display_selected_values_2',
                                                )
                                        ]
                                    ), lg=6, md=12, sm=12, xs=12, className="summed-figs"),
                            ],
                            justify="center")
                        ]
                    )
                )
            ])
        ])])

    


app.layout = html.Div([body])


@app.callback(
    [Output(component_id='display_selected_values', component_property='figure'),
     Output(component_id='display_selected_values_2', component_property='figure')],
    [Input(component_id='input_case', component_property='value'),
     Input(component_id='input_countries', component_property='value')
    ])


def create_datasets(input_case, input_countries):
    if input_case == "confirmed":
        colorscale = colorscale_confirmed
    elif input_case == "deaths":
        colorscale = colorscale_deaths
    elif input_case == "recovered":
        colorscale = colorscale_recovered

    datasets = pd.DataFrame()
    
    for country in input_countries:
        country_df = df.copy()[df['country'] == country]
        country_df['alpha_code'] = country_df["country"].map(iso_alpha_dict)
        last_d_filtered_df = country_df[country_df["date"] == last_day]
        if datasets.empty:
            datasets = last_d_filtered_df  
        else:
            datasets = datasets.append(last_d_filtered_df, ignore_index=True)
        
    
    trace = []
        
    for i in datasets["country"].unique():
        region_df = datasets[datasets["country"]==i]
        trace.append(go.Choroplethmapbox( 
        locations= region_df["alpha_code"],
        z= region_df[input_case],
        colorscale=colorscale,
        name=i,
        geojson=countries,
        marker_opacity=0.5,
        showscale=False
        ))
    
        trace[0]['visible'] = True    
    
    layout = go.Layout(
        margin=dict(
        l=0,
        r=0,
        b=0,
        t=10,
        pad=4
    ),
        
        geo = go.layout.Geo(
        projection_type = 'natural earth'
    )
        )
    
    fig=go.Figure(data=trace, layout=layout)
    fig.update_layout(mapbox_style="carto-positron", hovermode=False)

    second_datasets = pd.DataFrame()

    for country in input_countries:
        second_country_df = df[df["country"]==country]
        second_country_df = second_country_df[["country", input_case]]
        second_country_df = second_country_df.loc[second_country_df[input_case] > 0]
        second_country_df.reset_index(inplace=True)
        second_country_df.drop(columns={"index"}, inplace=True)
        second_country_df.reset_index(inplace=True)
        if second_datasets.empty:
            second_datasets = second_country_df  # note the double square brackets!
        else:
            second_datasets = second_datasets.append(second_country_df)
#         print(datasets)     
        
        
    second_trace = []    

    for i in second_datasets["country"].unique():
        region_df = second_datasets[second_datasets["country"]==i]
        second_trace.append(
            go.Scatter( 
                x=region_df["index"],
                y=region_df[input_case],
                name = i + " " + format(region_df[input_case].max(),",") + " " + input_case +  " cases documented." ,
                mode="markers+lines",
                showlegend=True,
                line=dict(width=1)
                ))
    
        second_trace[0]['visible'] = True 
    
   

    second_layout = go.Layout( 
        plot_bgcolor='#fffdfc',
        xaxis = dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
        ),
        ),
        xaxis_title="Days since first documented case",
        yaxis=dict(
            showgrid=False,
        ),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=10,
            pad=4
        ),
        legend=dict(
        x=0,
        y=1,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="#7a7978"
        ),
        bgcolor="#fffdfc",
    )

        
    )
    
    
    second_fig=go.Figure(data=second_trace, layout=second_layout)
            
    return fig, second_fig

if __name__ == '__main__':
    app.run_server(debug=True)
