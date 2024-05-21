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
