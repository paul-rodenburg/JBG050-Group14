import pandas as pd
import sqlite3
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from generate_database.functions import get_trust

BEST = True

df_unemp = pd.read_csv('../data/economic/unemploymentRates.csv', delimiter=';')
df_unemp.columns = ['Year'] + [col[-4:] for col in df_unemp.columns[1:]]
for column in df_unemp.columns[1:]:
    # Replace commas with dots and convert to floats
    df_unemp[column] = df_unemp[column].str.replace(',', '.').astype(float)


def min_max_scale(df):
    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()

    # Scale the values
    scaled_values = scaler.fit_transform(df)

    # Create a new DataFrame with the scaled values
    df_scaled = pd.DataFrame(scaled_values, index=df.index, columns=df.columns)
    return df_scaled


df_trust = get_trust(BEST, sqlite_path='../data/crime_data.db')
df_trust = df_trust.rename(columns={'City of Westminster': 'Westminster'})
df_unemp = df_unemp.set_index(df_unemp.columns[0]).transpose()
df_unemp = df_unemp[df_trust.columns]
min_value = df_unemp.values.min()
max_value = df_unemp.values.max()
print(f"Min unemp: {min_value}")
print(f"Max unemp: {max_value}")
# df_unemp = min_max_scale(df_unemp)
plot_unemp = sns.lineplot(df_unemp)
mapper = {True: "most", False: "least"}
plot_unemp.set_title(f"Unemployment rate [{min_value}, {max_value}] for the 5 {mapper[BEST]} trusted boroughs")
plt.savefig(f'figures/{mapper[BEST]}_unemployment_and_trust.png')
plt.show()
trust_plot = sns.lineplot(df_trust)
trust_plot.set_title(f"Trust for the 5 {mapper[BEST]} trusted boroughs")

plt.show()
