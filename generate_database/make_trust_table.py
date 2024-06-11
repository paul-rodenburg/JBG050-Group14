from functions import make_table_SQL, download
import pandas as pd
import os

download_url = "https://data.london.gov.uk/download/mopac-surveys/c3db2a0c-70f5-4b73-916b-2b0fcd9decc0/PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx"

if not os.path.isfile('../data/trust.xlsx'):  # Only download when the file is not already downloaded
    download(download_url, '../data/trust.xlsx')

df = pd.read_excel('../data/trust.xlsx', sheet_name='Borough')
print(df)
df = df[df['Measure'] == 'Trust MPS']
df['Date'] = pd.to_datetime(df['Date'])

# Remove columns with "Unnamed" in the column name
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

make_table_SQL(df, 'Trust', sqlite_db_path='../data/crime_data.db')
