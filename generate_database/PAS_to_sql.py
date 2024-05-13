import pandas as pd
import sqlite3
import os
import gdown
import zipfile
from tqdm import tqdm
import shutil

# Dictionary containing the file name of the PAS zip and its Google Drive ID (used to download it)
files = {"PAS.zip": "1K-_DRciZvkYMDp0EGV5WBX_CVNrHp9_H"}

# Empty pas if it already exists (so the newest version available is always added and older versions are not used) and otherwise make the folder
if os.path.exists("../data/pas"):
    shutil.rmtree("../data/pas")
os.mkdir("../data/pas")

# Download the PAS zip file from Google Drive
for file in files.keys():
    id = files[file]
    url = f'https://drive.google.com/uc?id={id}'
    output = f'../data/pas/{file}'
    gdown.download(url, output, quiet=False)

pas_dir = "../data/pas"

# Unzip/extract the downloaded PAS zip file containing the PAS csv files
for file_name in files.keys():
    source = f"../data/pas/{file_name}"
    print(f"Extracting {file_name} ...")
    with zipfile.ZipFile(source) as zf:
        for member in tqdm(zf.infolist(), desc='Extracting '):
            try:
                zf.extract(member, pas_dir)
            except zipfile.error as e:
                pass

# Get a list of the PAS csv files
pas_csv_list = [file for file in os.listdir(pas_dir) if file.endswith(".csv")]

# Convert all PAS csv files to the SQL database
columns_deleted = "Columns whose values are *ONLY* NULLs are deleted since they are useless. This file contains some info about those removed columns"
count = 0
for file in pas_csv_list:
    count += 1
    print(f"Combining PAS file {file} ({count}/{len(pas_csv_list)}) ...)")
    df = pd.read_csv(f"../data/pas/{file}")
    print(f"{len(df.columns)} columns in PAS file {file}")

    # The first column (called 'Unnamed: 0') of the PAS csv's is empty, with as value the index, it is useless so we remove that column
    df = df.drop(columns="Unnamed: 0")

    # Remove columns which only contains NULL values
    columns_before = df.columns
    df = df.dropna(axis="columns", how='all')
    columns_after = df.columns
    columns_removed = list(set(columns_before) - set(columns_after))
    print(f"{len(columns_removed)} NULL columns deleted\nBefore: {len(columns_before)} columns\nAfter: {len(columns_after)} columns")
    text_columns_deleted = f"{len(columns_removed)} columns deleted ({len(columns_before)} -> {len(columns_after)}) in {file}: [{', '.join(columns_removed)}]"

    # Set the columns deleted info text for the txt file
    columns_deleted = f"{columns_deleted}\n\n{text_columns_deleted}"
    # Convert the PAS DataFrame into the SQL database
    sqlite_db_path = '../data/crime_data.db'

    # Define the SQLite table name
    table_name = file.replace(".csv", "")
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

# Make txt file containing the info about columns deleted
with open("../data/PAS_columns_deleted_info.txt", "w") as f:
    f.write(columns_deleted)

# Remove the (empty) __MACOSX folder that is extracted from the PAS zip file
if os.path.isdir("../data/pas/__MACOSX"):
    shutil.rmtree("../data/pas/__MACOSX")
