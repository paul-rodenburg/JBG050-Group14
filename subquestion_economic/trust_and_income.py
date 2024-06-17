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

selected_boroughs = [i.replace('city of ', '') for i in selected_boroughs]  # Change 'City of Westminster' to 'Westminster'
df_income = df_income[df_income['Area'].str.lower().isin(selected_boroughs)]

df_income = df_income.set_index(df_income.columns[0]).transpose()

df_income = df_income.rename(columns={'Westminster': 'City of Westminster'})
df_income = df_income.rename(columns={'Area': 'Year'})
df_income.index.names = ['Year']
min_value = df_income.values.min()
max_value = df_income.values.max()
print(df_income)

def min_max_scale(df):
    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()

    # Scale the values
    scaled_values = scaler.fit_transform(df)

    # Create a new DataFrame with the scaled values
    df_scaled = pd.DataFrame(scaled_values, index=df.index, columns=df.columns)
    return df_scaled


df_income = min_max_scale(df_income)

fig, ax = plt.subplots(figsize=(15, 6))
sns.lineplot(data=df_income, dashes=False, ax=ax)

df_PAS = df_PAS.rename(columns={'year': 'Year'})
df_PAS.set_index('Year', inplace=True)
df_PAS.columns = [f'Trust {i}' for i in df_PAS.columns]
print(df_PAS)
sns.lineplot(data=df_PAS, ax=ax)

title_mapper = {True: 'most', False: 'least'}
ax.set_title(f'Hourly income for the {title_mapper[BEST]} 5 trusted boroughs', fontsize=24)
fig.patch.set_alpha(0.0)  # Set the plot background transparant
ax.set_xlim(2016, 2022)

fig.suptitle(f'Hourly income range: [£{min_value}, £{max_value}]')
# Move the legend to the right side of the plot
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='large')

plt.subplots_adjust(right=0.7)
plt.show()
fig.savefig(f'figures/{title_mapper[BEST]}_boroughs_trust_and_income.png')
