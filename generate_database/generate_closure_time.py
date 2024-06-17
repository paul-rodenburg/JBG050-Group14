import pandas as pd
import sqlite3
import warnings

# -------------------- SCRAPPED -------------------
warnings.warn('ANALYZING CLOSURE TIME IS NOT SOMETHING INCLUDED IN THE FINAL PRESENTATION BECAUSE '
              'CLOSURE TIME CAN ONLY BE COMPUTED IN MONTHS WHICH IS NOT SPECIFIC ENOUGH', category=DeprecationWarning)
# -------------------- SCRAPPED -------------------




q = """SELECT o.Crime_ID Crime_ID, o.Month outcomes_month, s.Month street_month
FROM 'metropolitan-outcomes' o, 'metropolitan-street' s
WHERE o.Crime_ID == s.Crime_ID"""
conn = sqlite3.connect('../data/crime_data.db')
df = pd.read_sql_query(q, conn)
df['outcomes_month'] = pd.to_datetime(df['outcomes_month'])
df['street_month'] = pd.to_datetime(df['street_month'])
df['closure_time_months'] = (df['outcomes_month'] - df['street_month']) // pd.Timedelta('30 days')
df[['Crime_ID', 'closure_time_months']].to_parquet('../data/crimes_combined.parquet')

sqlite_db_path = '../data/crime_data.db'

# Define the SQLite table name
table_name = "closure_time"
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