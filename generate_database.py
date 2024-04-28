import math
import os
import sqlite3
import pandas as pd
import glob
from datetime import datetime

# Get current time for performance measurement
a = datetime.now()

# Makes the parquet folder when it doesn't exist already.
if not os.path.isdir("data/parquets"):
    os.mkdir("data/parquets")


def generate_database_tables(type_data: str, generate_parquets=True):
    types = ["outcome", "stop-and-search", "normal"]
    if type_data not in types:
        raise ValueError("Type must be one of: " + ", ".join(types))
    if generate_parquets:
        # Traverse through all directories and subdirectories to find CSV files
        directory = 'data/csv/'
        names = []
        for root, dirs, files in os.walk(directory):
            current_file = glob.glob(os.path.join(root, '*.csv'))
            for file in current_file:
                # Extracting names from file paths
                name = file.split("/")[-1][8:].replace(".csv", "").replace("-outcomes", "").replace("-stop-and-search", "")
                names.append(name)

        # Deduplicate the list of names
        names = list(set(names))
        names = [name for name in names if "metropolitan" in name]
        len_names = len(names)
        count = 0
        times = []
        for name in names:
            a1 = datetime.now()
            df = pd.DataFrame()
            for root, dirs, files in os.walk(directory):
                current_file = glob.glob(os.path.join(root, '*.csv'))
                for file in current_file:
                    if type_data == 'normal':
                        if "outcomes" not in file and "stop-and-search" not in file and name in file:
                            df_temp = pd.read_csv(file)
                            df = pd.concat([df, df_temp], ignore_index=True)
                    else:
                        if type_data in file and name in file:
                            df_temp = pd.read_csv(file)
                            df = pd.concat([df, df_temp], ignore_index=True)
            if len(df) == 0 or df.empty:
                continue
            df.to_parquet(f"data/parquets/{name}-{type_data}.parquet")
            count += 1
            a2 = datetime.now()
            d1 = a2 - a1
            times.append(d1.seconds)
            # Print progress and estimated time to complete
            print(f"Making parquets at {(count / len_names * 100):.2f}%. Will take {math.ceil((sum(times) / len(times)) * (len_names - count))} seconds to complete. Last parquet took {d1.seconds} seconds")

    parquet_dir = "data/parquets"
    # Filter only parquet files
    parquets = [file for file in os.listdir(parquet_dir) if file.endswith(".parquet")]
    count = 1
    count_rows = 0
    # Make for each parquet (police force) a table in the SQL database
    for parquet in parquets:
        try:
            # Read parquet file into DataFrame
            df = pd.read_parquet(f"data/parquets/{parquet}")
            if df.empty or len(df) == 0:
                raise ValueError("Empty dataframe")
        except Exception as e:
            print(f"There was an error with {parquet}: {e}")
            continue
        count_rows += len(df)
        sqlite_db_path = 'data/crime_data.db'

        print(f"Begin SQL Conversion of {parquet} ({type_data}) ({count}/{len(parquets)})")
        # Create a SQLite connection and cursor
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()

        # Define the SQLite table name
        table_name = parquet.replace(".parquet", "")

        # Create a table in the SQLite database with the same columns as the DataFrame
        df.to_sql(table_name, conn, index=False, if_exists='replace')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        print(f"CSV data successfully imported into SQLite database: {sqlite_db_path}, table: {table_name}")
        count += 1
    # Print summary statistics
    print(f"Table {type_data} has in total {count_rows:,} rows. {math.ceil(count_rows / len(parquets)):,} rows on average per table ({len(parquets)} tables)")


# Generate database tables for different types of data
types = ["outcome", "stop-and-search", "normal"]
# Generate database tables for other types
print("Generating database, this can take up to 10-20 minutes... and will take 10 GB of space!")
for type_data in types:
    generate_database_tables(type_data)

# Get end time for performance measurement
b = datetime.now()
d = b - a
print(f"Generating database [{', '.join(types)}] took {d.seconds} seconds ({math.ceil(d.seconds/60)} minutes) total")  # Print total execution time
