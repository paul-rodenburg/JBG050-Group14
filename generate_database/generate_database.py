import json
import sqlite3
import sys
import pandas as pd
import os
import shutil


def generate_database(areas: [str], replace_sql_database, generate_parquets=True):
    if generate_parquets:
        print("Emptying parquets folder...")
        # Empty parquets folder
        shutil.rmtree("../data/parquets")
        os.mkdir("../data/parquets")
        print(f"Generating parquets for area(s): {', '.join(areas)}")
        f = open("../data/paths.json", "r")
        paths = json.load(f)
        f.close()
        keys_all = paths.keys()
        columns = []
        for area in areas:
            columns_to_add = [attribute for attribute in keys_all if area in attribute]
            columns.extend(columns_to_add)
        count = 0
        for column in columns:
            count += 1
            files = paths[column]
            df = pd.DataFrame()
            print(f"Creating parquet for {column} ({count}/{len(columns)})")
            for file in files:
                df_temp = pd.read_csv(file).astype(str)
                df_temp = df_temp.rename(columns={col: col.replace(' ', '_') for col in df.columns})
                if "stop" in column:
                    print(df_temp.columns)
                    print(df_temp["Outcome_linked_to_object_of_search"].head())
                df = pd.concat([df, df_temp])
            df.to_parquet(f"../data/parquets/{column}.parquet")

    print("Parquet created! Now creating the SQL database...")
    if replace_sql_database:  # Remove the database so entirely new database will be made
        os.remove("../data/crime_data.db")
    parquet_dir = "../data/parquets"
    # Filter only parquet files
    parquets = [file for file in os.listdir(parquet_dir) if file.endswith(".parquet")]
    count = 1
    count_rows = 0
    # Make for each parquet (police force) a table in the SQL database
    for parquet in parquets:
        try:
            # Read parquet file into DataFrame
            df = pd.read_parquet(f"../data/parquets/{parquet}")
            if df.empty:
                raise ValueError("Empty dataframe")
        except Exception as e:
            print(f"There was an error with {parquet}: {e}")
            continue

        count_rows += len(df)
        sqlite_db_path = '../data/crime_data.db'

        # Define the SQLite table name
        table_name = parquet.replace(".parquet", "")

        print(f"Begin SQL Conversion of {parquet} ({table_name}) ({count}/{len(parquets)})")
        # Create a SQLite connection and cursor
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()

        # Create a table in the SQLite database with the same columns as the DataFrame
        df.to_sql(table_name, conn, index=False, if_exists='replace')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        print(f"CSV data successfully imported into SQLite database: {sqlite_db_path}, table: {table_name}")
        count += 1
        # Print summary statistics
        print(f"Table {table_name} has in total {count_rows:,} rows.")


def ask_to_reset():
    x = input("Would you like to regenerate the SQL database (r) or update the database (u)? Type 'u' or 'r'")
    if x == "r":
        generate_database(["metropolitan"], replace_sql_database=True)
    elif x == "u":
        generate_database(["metropolitan"], replace_sql_database=False)
    elif x == "q":
        sys.exit(0)
    else:
        print("Invalid input, Try again (q for quit)")
        ask_to_reset()


ask_to_reset()
