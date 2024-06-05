import pandas as pd
import sqlite3
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from generate_database.functions import make_table_SQL

BEST = True

conn = sqlite3.connect("../data/crime_data.db")
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

# df_PAS = pd.read_excel("data/PAS_T&Cdashboard_to Q3 23-24.xlsx", sheet_name='Borough', engine='openpyxl')
# df_PAS = df_PAS[df_PAS['Measure'] == 'Trust MPS']
# df_PAS = df_PAS[df_PAS['Borough'].str.lower().isin(list(boroughs_trust.keys()))]
# df_PAS = df_PAS.loc[:, ~df_PAS.columns.str.contains('^Unnamed')]
# make_table_SQL(df_PAS, 'Trust', sqlite_db_path='data/crime_data.db')
selected_boroughs = sorted(boroughs_trust, key=boroughs_trust.get, reverse=BEST)[:5]

q = 'SELECT * FROM Trust'
df_PAS = pd.read_sql_query(q, conn)
df_PAS['Date'] = pd.to_datetime(df_PAS['Date'])
df_PAS = df_PAS[df_PAS['Borough'].str.lower().isin(selected_boroughs)]

def get_year_pas(date):
    return date[-4:]


df_PAS['Year'] = df_PAS['Date'].dt.year
columns_to_keep_pas = ['Year', 'Borough', 'Proportion']
df_PAS = df_PAS[columns_to_keep_pas]
df_PAS = df_PAS.rename(columns={'Proportion': 'Trust'})

df_PAS = df_PAS.pivot_table(index='Year', columns='Borough', values='Trust', aggfunc='mean')

# Reset index if needed
df_PAS.reset_index(inplace=True)


# Rename the columns to lowercase and replace spaces with underscores


def get_df_income(file_path):
    df_income = pd.read_excel(file_path, sheet_name="Total, Hourly", usecols="A,P:V")
    for col in df_income.columns[1:]:
        df_income[col] = df_income[col].astype(str).str.replace(',', '.')
        df_income[col] = pd.to_numeric(df_income[col], errors='coerce')
    return df_income


df_income = get_df_income('../data/economic/earnings-residence-borough.xlsx')

df_income = df_income[df_income['Area'].str.lower().isin(selected_boroughs)]

df_income = df_income.set_index(df_income.columns[0]).transpose()

df_income = df_income.rename(columns={'Area': 'Year'})

df_income.index.names = ['Year']


def min_max_scale(df):
    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()

    # Scale the values
    scaled_values = scaler.fit_transform(df)

    # Create a new DataFrame with the scaled values
    df_scaled = pd.DataFrame(scaled_values, index=df.index, columns=df.columns)
    return df_scaled


df_income = min_max_scale(df_income)


fig_best = sns.lineplot(df_income, dashes=False)
# years = [2016, 2017, 2018, 2019, 2020, 2021, 2022]

# # Create a DataFrame with these years as the index
# df_trust = pd.DataFrame(index=years)
#
# # Assign the trust values to each year
# for area, trust in boroughs_trust.items():
#     df_trust[area] = trust
#
# df_trust.index.names = ['Year']
# print(df_trust)

df_PAS = df_PAS.rename(columns={'year': 'Year'})
df_PAS.set_index('Year', inplace=True)
pas_plot = sns.lineplot(df_PAS, ax=fig_best)


title_mapper = {True: 'most', False: 'least'}
fig_best.set_title(f'House prices for the {title_mapper[BEST]} 5 trusted boroughs')
# fig_best.get_legend().remove()
plt.show()
