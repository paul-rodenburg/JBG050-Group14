import pandas as pd
import sqlite3
import requests
from tqdm import tqdm


def make_table_SQL(df, table_name, sqlite_db_path="../data/crime_data.db"):
    print(f"Begin SQL Conversion of {table_name}")

    # Create a SQLite connection and cursor
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    # Define the SQLite table name
    table_name = table_name

    # Create a table in the SQLite database with the same columns as the DataFrame
    df.to_sql(table_name, conn, index=False, if_exists='replace')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Let the user know the csv data is converted into the SQL database successfully
    print(f"CSV data successfully imported into SQLite database: {sqlite_db_path}, table: {table_name}")


# Function to download files from an URL with a progress bar
def download(url: str, fname: str, chunk_size=1024):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            bar.update(size)


def get_trust(BEST=True, get_all=False, sqlite_path='../data/crime_data.db'):
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
    if get_all:
        selected_boroughs = list(boroughs_trust.keys())
    else:
        selected_boroughs = sorted(boroughs_trust, key=boroughs_trust.get, reverse=BEST)[:5]
    conn = sqlite3.connect(sqlite_path)
    q = 'SELECT * FROM Trust'
    df_PAS = pd.read_sql_query(q, conn)
    df_PAS['Date'] = pd.to_datetime(df_PAS['Date'])
    df_PAS = df_PAS[df_PAS['Borough'].str.lower().isin(selected_boroughs)]

    df_PAS['Year'] = df_PAS['Date'].dt.year
    columns_to_keep_pas = ['Year', 'Borough', 'Proportion']
    df_PAS = df_PAS[columns_to_keep_pas]
    df_PAS = df_PAS.rename(columns={'Proportion': 'Trust'})

    df_PAS = df_PAS.pivot_table(index='Year', columns='Borough', values='Trust', aggfunc='mean')

    # Reset index if needed
    df_PAS.reset_index(inplace=True)
    df_PAS = df_PAS.rename(columns={'year': 'Year'})
    df_PAS.set_index('Year', inplace=True)
    return df_PAS