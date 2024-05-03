import pandas as pd
import sqlite3
import os
import gdown

files = {"PAS_Total.xlsx": "1gVG_-0WA-m7BL9z2tEIcrW8Z2G_j5yOq",
         "PAS_buroughs.xlsx": "156Ir1sosmv5LJmrFpH9Lvdg3Yrat35oH"}

# Make pas folder (if not already exists)
if not os.path.exists("../data/pas"):
    os.mkdir("../data/pas")

for file in files.keys():
    id = files[file]
    url = f'https://drive.google.com/uc?id={id}'
    output = f'../data/pas/{file}'
    gdown.download(url, output, quiet=False)

pas_dir = "../data/pas"
pas_csv_list = [file for file in os.listdir(pas_dir) if file.endswith(".xlsx")]

for file in pas_csv_list:
    df = pd.read_excel(f"../data/pas/{file}", index_col=0)
    sqlite_db_path = '../data/crime_data.db'

    # Define the SQLite table name
    table_name = file.split('/')[-1].replace(".xlsx", "")
    print(f"Beginning SQL conversion of {table_name} into {sqlite_db_path}")
    # Create a SQLite connection and cursor
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    # Create a table in the SQLite database with the same columns as the DataFrame
    df.to_sql(table_name, conn, index=False, if_exists='replace')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"CSV data successfully imported into SQLite database: {sqlite_db_path}, table: {table_name}")
    # Print summary statistics
    print(f"Table {table_name} successfully converted into the SQL database ({sqlite_db_path})")