import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import json

external_stylesheets = ['style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

q = """SELECT sentiment_text, sentiment_headline, boroughs
    FROM BBC_articles
    WHERE boroughs IS NOT NULL"""
conn = sqlite3.connect('data/crime_data.db')
df = pd.read_sql_query(q, conn)
# Convert the string representation of lists to actual lists
df["boroughs"] = df["boroughs"].apply(lambda x: eval(x))

boroughs_sentiment = {"best5":
                          {"kingston upon thames": 0.848750,
                           "bexley": 0.850313,
                           "sutton": 0.851562,
                           "city of westminster": 0.858750,
                           "kensington and chelsea": 0.860000
                           },
                      "worst5":
                          {"hackney": 0.737812,
                           "lewisham": 0.745000,
                           "haringey": 0.748437,
                           "islington": 0.756250,
                           "lambeth": 0.759375
                           }
                      }
boroughs = list(boroughs_sentiment["best5"].keys()) + list(boroughs_sentiment["worst5"].keys())


def generate_histo(attribute, borough, bins):
    df_histo = df.copy()
    df_histo = df_histo[df_histo['boroughs'].apply(lambda x: borough in x)]
    len_bbc_articles = len(df_histo)
    mean_sentiment = df_histo[attribute].mean()
    fig_map = px.histogram(df_histo, x=attribute, nbins=bins)
    return fig_map, len_bbc_articles, mean_sentiment


def get_mean_text(borough):
    df_histo = df.copy()
    df_histo = df_histo[df_histo['boroughs'].apply(lambda x: borough in x)]
    mean_sentiment = df_histo['sentiment_text'].mean()
    return round(mean_sentiment, 4)


def get_mean_headline(borough):
    df_histo = df.copy()
    df_histo = df_histo[df_histo['boroughs'].apply(lambda x: borough in x)]
    mean_sentiment = df_histo['sentiment_headline'].mean()
    return round(mean_sentiment, 4)


# Convert the dictionary to DataFrames
best5_df = pd.DataFrame(list(boroughs_sentiment['best5'].items()), columns=['Borough', 'Trust']).sort_values(
    by='Trust', ascending=False)
best5_df['sentiment_text_mean'] = best5_df['Borough'].apply(get_mean_text)
best5_df['sentiment_headline_mean'] = best5_df['Borough'].apply(get_mean_headline)

worst5_df = pd.DataFrame(list(boroughs_sentiment['worst5'].items()), columns=['Borough', 'Trust']).sort_values(
    by='Trust')
worst5_df['sentiment_text_mean'] = best5_df['Borough'].apply(get_mean_text)
worst5_df['sentiment_headline_mean'] = best5_df['Borough'].apply(get_mean_headline)

# Create map

# Load GeoJSON data
with open('london_boroughs.geojson') as f:
    geojson_data = json.load(f)
# df_map = pd.DataFrame({
#     "Borough": boroughs,
#     "Value": [1] * len(boroughs)  # You can use any value here; it's for coloring purposes
# })

df_map = pd.concat([best5_df, worst5_df], ignore_index=True)
# Lowercase the "name" property of each feature
for feature in geojson_data['features']:
    feature['properties']['name'] = feature['properties']['name'].lower()

color_options = [i for i in best5_df.columns if i != "Borough"]


def make_map(color):
    map_boroughs = px.choropleth_mapbox(df_map, geojson=geojson_data, locations='Borough', featureidkey="properties.name",
                                        color=color, color_continuous_scale="Viridis",
                                        mapbox_style="carto-positron",
                                        hover_data=color_options,
                                        zoom=9, center={"lat": 51.5074, "lon": -0.1278},
                                        opacity=0.5)
    return map_boroughs

histo, len_bbc_articles, _ = generate_histo("sentiment_text", boroughs[0], 45)

app.layout = html.Div(
    [html.Span(id="leaderboard-title", children='Borough Sentiment Leaderboard'),

     html.Span(className="top-title", children='Best 5 Boroughs', style={'color': 'green'}),
     dash_table.DataTable(
         id='best5-table',
         columns=[{"name": i, "id": i} for i in best5_df.columns],
         data=best5_df.to_dict('records'),
         style_table={'width': '50%', 'margin': 'auto'},
         style_header={
             'backgroundColor': 'rgb(230, 230, 230)',
             'fontWeight': 'bold'
         },
         style_cell={
             'textAlign': 'left',
             'minWidth': '150px', 'maxWidth': '150px', 'width': '150px'
         }
     ),

     html.Span(className="top-title", children='Worst 5 Boroughs', style={'color': 'red'}),
     dash_table.DataTable(
         id='worst5-table',
         columns=[{"name": i, "id": i} for i in worst5_df.columns],
         data=worst5_df.to_dict('records'),
         style_table={'width': '50%', 'margin': 'auto'},
         style_header={
             'backgroundColor': 'rgb(230, 230, 230)',
             'fontWeight': 'bold'
         },
         style_cell={
             'textAlign': 'left',
             'minWidth': '150px', 'maxWidth': '150px', 'width': '150px'
         }
     ),
     html.Br(),
     html.Br(),
     dcc.Dropdown(className='dropdown', id="borough-dropdown", value=boroughs[0], options=boroughs, clearable=False),
     dcc.Dropdown(className='dropdown', id="sentiment-dropdown", value="sentiment_text",
                  options=["sentiment_text", "sentiment_headline"], clearable=False),
     dcc.Dropdown(className='dropdown', id="bins-dropdown", value=15, options=[i for i in range(1, 51)],
                  clearable=False),
     html.Span(id="title-histo",
               children=f"Histogram about 'sentiment_text' of the BBC articles ({len_bbc_articles}) for borough '{boroughs[0]}' (15 bins)"),
     dcc.Graph(figure=histo, id='histo'),
     html.Span(children="Attribute to base color on:", style={'display': 'block', 'width': '100%', 'text-align': 'center'}),
     dcc.Dropdown(className='dropdown', id='color-dropdown', options=color_options, clearable=False, value=color_options[0]),
     html.Div(id='map-container', children=[
         dcc.Graph(figure=make_map(color_options[0]), id='map-boroughs')
     ]),
     ])


@app.callback([Output('histo', 'figure'),
               Output('title-histo', 'children')],
              [Input('borough-dropdown', 'value'),
               Input('sentiment-dropdown', 'value'),
               Input('bins-dropdown', 'value')])
def update_histo(borough, sentiment, bins):
    histo_return, len_bbc_articles_return, mean_sentiment = generate_histo(sentiment, borough, bins)
    title_histo = f"Histogram about '{sentiment}' of the BBC articles ({len_bbc_articles_return}) for borough '{borough}' ({bins} bins) | Mean of {sentiment}: {mean_sentiment:.4f}"
    return histo_return, title_histo


@app.callback([Output('map-boroughs', 'figure')],
              [Input('color-dropdown', 'value')])
def update_map(color_attribute):
    map_boroughs_return = make_map(color_attribute)
    print(f"Updated map with {color_attribute}")
    return map_boroughs_return


app.title = "BBC articles | Group 14"
app.run_server(debug=True, dev_tools_ui=False)
