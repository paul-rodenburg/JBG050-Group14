import sqlite3
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from functions import make_table_SQL

analyzer = SentimentIntensityAnalyzer()


# Function to compute VADER sentiment scores
def get_vader_sentiment(text):
    sentiment = analyzer.polarity_scores(text)['compound']
    return sentiment


q = "SELECT * FROM bbc_articles"
conn = sqlite3.connect('../data/crime_data.db')
df = pd.read_sql_query(q, conn)
df['sentiment_text'] = df['text'].apply(get_vader_sentiment)
df['sentiment_headline'] = df['headline'].apply(get_vader_sentiment)

top5 = ['kingston upon thames', 'bexley', 'sutton', 'city of westminster', 'kensington and chelsea']
worst5 = ['hackney', 'lewisham', 'haringey', 'islington', 'lambeth']
boroughs_needed = top5.copy()
boroughs_needed.extend(worst5)
q_streets = f"""SELECT LOCAL_TYPE, DISTRICT_BOROUGH, NAME1
FROM street_names
WHERE LOWER(LOCAL_TYPE) == 'named road'
"""
df_streets = pd.read_sql_query(q_streets, conn)
df_streets['DISTRICT_BOROUGH'] = df_streets['DISTRICT_BOROUGH'].str.lower()
boroughs_needed = [i.lower() for i in boroughs_needed]
df_streets = df_streets[df_streets['DISTRICT_BOROUGH'].isin(boroughs_needed)]
print(df_streets)

count = 0
total = len(df)


def get_boroughs(text, headline):
    global df_streets
    global count

    count += 1
    if count % 10 == 0 or count == total:
        print(f"Scanning at {count / total * 100:.2f}% ({count}/{total})")
    boroughs = []
    for _, row in df_streets.iterrows():
        if row['NAME1'].lower() in text.lower() or row['DISTRICT_BOROUGH'].lower() in text.lower():
            boroughs.append(row['DISTRICT_BOROUGH'])
        if row['NAME1'].lower() in headline.lower() or row['DISTRICT_BOROUGH'].lower() in headline.lower():
            boroughs.append(row['DISTRICT_BOROUGH'])
    if len(boroughs) == 0:
        return None
    else:
        return str(list(set(boroughs)))  # Use set to avoid duplicate boroughs


df['boroughs'] = df.apply(lambda x: get_boroughs(x['text'], x['headline']), axis=1)
make_table_SQL(df, 'test_ana')
