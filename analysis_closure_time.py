import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import os

REGENERATE_PARQUET = False

external_stylesheets = ['style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
if os.path.isfile("data/crimes_combined.parquet") and not REGENERATE_PARQUET:
    df = pd.read_parquet('data/crimes_combined.parquet')
else:
    q = """SELECT o.Crime_ID Crime_ID, o.Month outcomes_month, s.Month street_month, s.Longitude, s.Latitude
        FROM 'metropolitan-outcomes' o, 'metropolitan-street' s
        WHERE o.Crime_ID == s.Crime_ID
        LIMIT 10"""
    conn = sqlite3.connect('data/crime_data.db')
    df = pd.read_sql_query(q, conn)
    df.to_parquet('data/crimes_combined.parquet')

fig_map = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', zoom=6,
                                hover_data=["outcomes_month", "street_month"], hover_name="Crime_ID", opacity=0.7)

app.layout = html.Div([dcc.Graph(figure=fig_map, id='map')])

app.title = "Crime Date | Group 14"
app.run_server(debug=True, dev_tools_ui=False)
