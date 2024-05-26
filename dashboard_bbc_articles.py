import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import json

# Disable pandas warning
pd.options.mode.chained_assignment = None

external_stylesheets = ['style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
NAME = "BBC articles visualized"
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

boroughs_trust = {
    "kingston upon thames": 0.848750,
    "bexley": 0.850313,
    "sutton": 0.851562,
    "city of westminster": 0.858750,
    "kensington and chelsea": 0.860000,
    "hackney": 0.737812,
    "lewisham": 0.745000,
    "haringey": 0.748437,
    "islington": 0.756250,
    "lambeth": 0.759375
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


def get_number_of_articles(borough):
    df_histo = df.copy()
    df_histo = df_histo[df_histo['boroughs'].apply(lambda x: borough in x)]
    number_of_articles = len(df_histo)
    df_histo = None
    return f'{number_of_articles} ({number_of_articles / len(df) * 100:.2f}%)'


def get_positive_articles(borough):
    df_histo = df.copy()
    df_histo = df_histo[df_histo['boroughs'].apply(lambda x: borough in x)]
    number_of_positive_articles = len(df_histo[df_histo['sentiment_text'] > 0])
    return number_of_positive_articles


def get_negative_articles(borough):
    df_histo = df.copy()
    df_histo = df_histo[df_histo['boroughs'].apply(lambda x: borough in x)]
    number_of_negative_articles = len(df_histo[df_histo['sentiment_text'] < 0])
    return number_of_negative_articles


# Convert the dictionary to DataFrames
best5_df = pd.DataFrame(list(boroughs_sentiment['best5'].items()), columns=['Borough', 'Trust']).sort_values(
    by='Trust', ascending=False)
best5_df['sentiment_text'] = best5_df['Borough'].apply(get_mean_text)
best5_df['sentiment_headline'] = best5_df['Borough'].apply(get_mean_headline)
best5_df['number_of_articles'] = best5_df['Borough'].apply(get_number_of_articles)
best5_df['positive_articles'] = best5_df['Borough'].apply(get_positive_articles)
best5_df['negative_articles'] = best5_df['Borough'].apply(get_negative_articles)
best5_df['ratio_pos_neg'] = round(best5_df['positive_articles'] / best5_df['negative_articles'], 4)

worst5_df = pd.DataFrame(list(boroughs_sentiment['worst5'].items()), columns=['Borough', 'Trust']).sort_values(
    by='Trust')
worst5_df['sentiment_text'] = worst5_df['Borough'].apply(get_mean_text)
worst5_df['sentiment_headline_'] = worst5_df['Borough'].apply(get_mean_headline)
worst5_df['number_of_articles'] = worst5_df['Borough'].apply(get_number_of_articles)
worst5_df['positive_articles'] = worst5_df['Borough'].apply(get_positive_articles)
worst5_df['negative_articles'] = worst5_df['Borough'].apply(get_negative_articles)
worst5_df['ratio_pos_neg'] = round(worst5_df['positive_articles'] / worst5_df['negative_articles'], 4)

# Create map

# Load GeoJSON data
with open('london_boroughs.geojson') as f:
    geojson_data = json.load(f)

df_map = pd.concat([best5_df, worst5_df], ignore_index=True)
# Lowercase the "name" property of each feature
for feature in geojson_data['features']:
    feature['properties']['name'] = feature['properties']['name'].lower()

color_options = [i for i in best5_df.columns if i != "Borough"]


def make_map(color):
    df_map['Borough'] = df_map['Borough'].replace('city of westminster', 'westminster')
    map_boroughs = px.choropleth_mapbox(df_map, geojson=geojson_data, locations='Borough',
                                        featureidkey="properties.name",
                                        color=color, color_continuous_scale="Viridis",
                                        mapbox_style="carto-positron",
                                        hover_data=color_options,
                                        zoom=9, center={"lat": 51.5074, "lon": -0.1278},
                                        opacity=0.5)
    return map_boroughs


histo, len_bbc_articles, _ = generate_histo("sentiment_text", boroughs[0], 45)

ranking = {'kensington and chelsea': 1,
           'city of westminster': 2,
           'sutton': 3,
           'bexley': 4,
           'kingston upon thames': 5,
           'hackney': 6,
           'lewisham': 7,
           'haringey': 8,
           'islington': 9,
           'lambeth': 10
           }


def generate_heatmap(z: str):
    global best5_df, worst5_df
    global ranking

    best = best5_df['Borough'].values
    worst = worst5_df['Borough'].values

    df_heatmap_best = df[df['boroughs'].apply(lambda x: any(item in best for item in x))]
    df_heatmap_worst = df[df['boroughs'].apply(lambda x: any(item in worst for item in x))]

    def get_borough(borough_list):
        global ranking

        for b in borough_list:
            if b in best:
                return f'{b} ({ranking[b]})'
            if b in worst:
                return f'{b} ({ranking[b]})'
        return None

    def get_is_positive(sentiment_text):
        if sentiment_text > 0:
            return 1
        else:
            return 0

    def get_trust(borough):
        global boroughs_trust
        borough = borough.split('(')[0]
        borough = borough.rstrip()
        return boroughs_trust[borough]

    df_heatmap_best['borough'] = df_heatmap_best['boroughs'].apply(get_borough)
    df_heatmap_worst['borough'] = df_heatmap_worst['boroughs'].apply(get_borough)

    df_heatmap_best['is_positive'] = df_heatmap_best['sentiment_text'].apply(get_is_positive)
    df_heatmap_worst['is_positive'] = df_heatmap_worst['sentiment_text'].apply(get_is_positive)

    df_heatmap_best['trust'] = df_heatmap_best['borough'].apply(get_trust)
    df_heatmap_worst['trust'] = df_heatmap_worst['borough'].apply(get_trust)

    df_heatmap = pd.concat([df_heatmap_best, df_heatmap_worst])

    # Create subplots
    heatmap = px.density_heatmap(
        df_heatmap,
        x='trust',
        y='borough',
        z='is_positive',
        color_continuous_scale='brwnyl',
        nbinsx=20,
        category_orders={'borough': ranking}
    )
    heatmap.update_xaxes(categoryorder="category ascending")
    return heatmap


def generate_scatter(x: str):
    global best5_df, worst5_df
    global ranking

    best = best5_df['Borough'].values
    worst = worst5_df['Borough'].values

    df_scatter_best = df[df['boroughs'].apply(lambda x: any(item in best for item in x))]
    df_scatter_worst = df[df['boroughs'].apply(lambda x: any(item in worst for item in x))]

    def get_borough(borough_list):
        global ranking

        for b in borough_list:
            if b in best:
                return f'{b} ({ranking[b]})'
            if b in worst:
                return f'{b} ({ranking[b]})'
        return None

    def get_is_positive(sentiment_text):
        if sentiment_text > 0:
            return 1
        else:
            return 0

    def get_trust(borough):
        global boroughs_trust
        borough = borough.split('(')[0]
        borough = borough.rstrip()
        return boroughs_trust[borough]

    df_scatter_best['borough'] = df_scatter_best['boroughs'].apply(get_borough)
    df_scatter_worst['borough'] = df_scatter_worst['boroughs'].apply(get_borough)

    df_scatter_best['is_positive'] = df_scatter_best['sentiment_text'].apply(get_is_positive)
    df_scatter_worst['is_positive'] = df_scatter_worst['sentiment_text'].apply(get_is_positive)

    df_scatter_best['trust'] = df_scatter_best['borough'].apply(get_trust)
    df_scatter_worst['trust'] = df_scatter_worst['borough'].apply(get_trust)

    df_scatter = pd.concat([df_scatter_best, df_scatter_worst])

    # Create subplots
    scatter = px.scatter(
        df_scatter,
        x=x,
        y='sentiment_text'
    )
    scatter.update_xaxes(categoryorder="category ascending")
    if x != 'borough':
        correlation = round(df_scatter[x].corr(df_scatter['sentiment_text']), 4)
    else:
        second_last_chars = df_scatter[x].str[-2]  # Extract second last character from each string in df_scatter[x]
        correlation = round(second_last_chars.astype(float).corr(df_scatter['sentiment_text']),
                            4)  # Compute correlation
    return scatter, correlation


scatter, correlation = generate_scatter('borough')
TOTAL = 1133

app.layout = html.Div(
    [html.Span(id='title', children=NAME),
     html.Div(id='left-column', children=[
         html.Span(id="leaderboard-title", children='Borough Sentiment Leaderboard'),
         html.Br(),
         html.Br(),
         html.Br(),
         html.Span(className="top-title", children='Most Trusted 5 Boroughs', style={'color': 'green'}),
         html.Br(),
         html.Br(),
         html.Br(),
         dash_table.DataTable(
             id='best5-table',
             columns=[{"name": i, "id": i} for i in best5_df.columns],
             data=best5_df.to_dict('records'),
             style_table={'width': '90%', 'margin': 'auto', 'max-width': '90%'},
             style_header={
                 'backgroundColor': 'rgb(230, 230, 230)',
                 'fontWeight': 'bold'
             },
             fixed_columns={'headers': True, 'data': 1},
             style_cell={
                 'textAlign': 'left',
                 'minWidth': '50px', 'max-width': '350px'
             }
         ),
         html.Br(),
         html.Span(className="top-title", children='Least Trusted 5 Boroughs', style={'color': 'red'}),
         html.Br(),
         html.Br(),
         html.Br(),
         dash_table.DataTable(
             id='worst5-table',
             columns=[{"name": i, "id": i} for i in worst5_df.columns],
             data=worst5_df.to_dict('records'),
             style_table={'width': '90%', 'margin': 'auto', 'max-width': '90%'},
             style_header={
                 'backgroundColor': 'rgb(230, 230, 230)',
                 'fontWeight': 'bold'
             },
             fixed_columns={'headers': True, 'data': 1},
             style_cell={
                 'textAlign': 'left',
                 'minWidth': '50px', 'max-width': '350px'
             }
         ),
         html.Div(id='info-div', children=[html.Span(
             className='info-table',
             children=[
                 'Sentiment (computed with',
                 html.A('VADER', href='https://github.com/cjhutto/vaderSentiment', target='_blank',
                        style={'padding-left': '3px'}),
                 ') is the mean over all the articles of that specific borough'
             ]
         ),
             html.Span(className='info-table',
                       children="Percentage in the 'number_of_articles' column is the percentage "
                                'of the number of articles that that borough has compared to the '
                                f'total number of articles ({len(df)})')])

     ]
              ),
     html.Div(id='right-column', children=[
         html.Span(className='title-plot',
                   children="Heatmap of boroughs"),
         dcc.Graph(id='heatmap', figure=generate_heatmap('negative_articles')),
         dcc.Dropdown(className='dropdown', id='scatter-dropdown', clearable=False, value='borough',
                      options=['borough', 'trust', 'sentiment_headline']),
         html.Span(id='correlation-scatter', children=f"Correlation of -1 is {correlation}", className='title-plot'),
         dcc.Graph(id='scatter', figure=scatter),
         html.Span(id='total-input-title', children='Values to calculate percentage of:',
                   style={'width': '100%', 'text-align': 'center', 'display': 'block'}),
         dcc.Input(id='input-total', value=TOTAL, placeholder='Total of all: 1133', type='number'),
         html.Button(id='set-current-total', children='Set current selected values as total'),
         html.Span(id='selected-text-scatter', children='Selected 0 values',
                   style={'width': '100%', 'text-align': 'center', 'font-style': 'italic', 'display': 'block'}),
         html.Br(),
         html.Span(className='title-plot', id="title-histo",
                   children=f"Histogram about 'sentiment_text' of the BBC articles ({len_bbc_articles}) for borough '{boroughs[0]}' (15 bins)"),
         html.Br(),
         dcc.Dropdown(className='dropdown', id="borough-dropdown", value=boroughs[0],
                      options=[{'label': b, 'value': b} for b in boroughs], clearable=False),
         dcc.Dropdown(className='dropdown', id="sentiment-dropdown", value="sentiment_text",
                      options=[{'label': i, 'value': i} for i in ["sentiment_text", "sentiment_headline"]],
                      clearable=False),
         dcc.Dropdown(className='dropdown', id="bins-dropdown", value=15,
                      options=[{'label': i, 'value': i} for i in range(1, 51)], clearable=False),
         dcc.Graph(figure=histo, id='histo'),
         html.Span(children="Attribute to base color on:",
                   style={'display': 'block', 'width': '100%', 'text-align': 'center'}),
         dcc.Dropdown(className='dropdown', id='color-dropdown',
                      options=[{'label': i, 'value': i} for i in color_options], clearable=False,
                      value=color_options[0]),
         dcc.Graph(figure=make_map(color_options[0]), id='map-boroughs')
     ]
              )
     ]
)


@app.callback([Output('histo', 'figure'),
               Output('title-histo', 'children')],
              [Input('borough-dropdown', 'value'),
               Input('sentiment-dropdown', 'value'),
               Input('bins-dropdown', 'value')])
def update_histo(borough, sentiment, bins):
    histo_return, len_bbc_articles_return, mean_sentiment = generate_histo(sentiment, borough, bins)
    title_histo = f"Histogram about '{sentiment}' of the BBC articles ({len_bbc_articles_return}) for borough '{borough}' ({bins} bins) | Mean of {sentiment}: {mean_sentiment:.4f}"
    return histo_return, title_histo


number_selected_points = TOTAL


@app.callback(Output('input-total', 'value'),
              Input('set-current-total', 'n_clicks'))
def update_total(n_clicks):
    if n_clicks:
        return number_selected_points
    else:
        return dash.no_update

@app.callback(Output('selected-text-scatter', 'children'),
              [Input('scatter', 'selectedData'),
               Input('input-total', 'value')])
def update_scatter_data(selectedData, total):
    global number_selected_points
    if total is None:
        total = TOTAL
    number_selected_points = len(selectedData['points'])
    if selectedData:
        return f"Selected {number_selected_points} values ({number_selected_points / total * 100:.2f}% of total ({total}))"
    else:
        return f"Selected 0 values (0% of total ({total}))"


@app.callback([Output('scatter', 'figure'),
               Output('correlation-scatter', 'children')],
              [Input('scatter-dropdown', 'value')])
def update_scatter(x):
    scatter, correlation = generate_scatter(x)
    if x == 'borough':
        x = f'{x} (ranking)'
    correlation_text = f"Correlation between {x} and sentiment_text is {correlation}"
    return scatter, correlation_text


@app.callback(Output('map-boroughs', 'figure'),
              [Input('color-dropdown', 'value')])
def update_map(color_attribute):
    map_boroughs_return = make_map(color_attribute)
    return map_boroughs_return


app.title = f"{NAME} | Group 14"
app.run_server(debug=True, dev_tools_ui=False)
