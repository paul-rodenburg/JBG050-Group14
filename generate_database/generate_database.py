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
                df_temp = pd.read_csv(file)
                df_temp = df_temp.rename(columns={col: col.replace(' ', '_') for col in df_temp.columns})
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
    columns_deleted = "Columns whose values are *ONLY* NULLs are deleted since they are useless. This file contains some info about those removed columns"
    for parquet in parquets:
        try:
            # Read parquet file into DataFrame
            df = pd.read_parquet(f"../data/parquets/{parquet}")
            columns_before = df.columns
            df = df.dropna(axis="columns", how='all')  # Remove columns that ONLY have NULL values
            columns_after = df.columns
            print(f"{len(columns_before) - len(columns_after)} NULL columns deleted from {parquet.replace('.parquet', '')}")
            columns_removed = list(set(columns_before) - set(columns_after))
            text_columns_deleted = f"{len(columns_removed)} columns deleted ({len(columns_before)} -> {len(columns_after)}) in {parquet.replace('.parquet', '')}: [{', '.join(columns_removed)}]"

            # Set the columns deleted info text for the txt file
            columns_deleted = f"{columns_deleted}\n\n{text_columns_deleted}"
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

        # Make txt file containing the info about columns deleted
        with open("../data/CRIME_columns_deleted_info.txt", "w") as f:
            f.write(columns_deleted)

def ask_to_reset():
    x = input("Would you like to regenerate the SQL database (r) or update the database (u)? Type 'u' or 'r'")
    if x.lower() == "r":
        generate_database(["metropolitan"], replace_sql_database=True)
    elif x.lower() == "u":
        generate_database(["metropolitan"], replace_sql_database=False)
    elif x.lower() == "q" or x.lower() == 'quit' or x.lower() == 'exit':
        sys.exit(0)
    else:
        print("Invalid input, Try again (q for quit)")
        ask_to_reset()


ask_to_reset()
