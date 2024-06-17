import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import warnings

external_stylesheets = ['style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# -------------------- SCRAPPED -------------------
warnings.warn('ANALYZING CLOSURE TIME IS NOT SOMETHING INCLUDED IN THE FINAL PRESENTATION BECAUSE '
              'CLOSURE TIME CAN ONLY BE COMPUTED IN MONTHS WHICH IS NOT SPECIFIC ENOUGH', category=DeprecationWarning)
# -------------------- SCRAPPED -------------------




q = """SELECT c.Crime_ID Crime_ID, closure_time_months, Longitude, Latitude
    FROM closure_time c, 'metropolitan-street' s
    WHERE c.Crime_ID == s.Crime_ID"""
conn = sqlite3.connect('data/crime_data.db')
df = pd.read_sql_query(q, conn)

fig_map = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', zoom=6, color="closure_time_months",
                            hover_data=["outcomes_month", "street_month", "closure_time_months"], hover_name="Crime_ID",
                            opacity=0.7, mapbox_style='open-street-map', )

app.layout = html.Div([dcc.Graph(figure=fig_map, id='map')])

app.title = "Crime Date | Group 14"
app.run_server(debug=True, dev_tools_ui=False)
