import time
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, cross_validate
import pandas as pd
import numpy as np
from generate_database.functions import get_trust
from generate_database.functions import download
import os

DOWNLOAD_HOUSE_PRICES = False  # Set to False ONLY when you already have downloaded the house price data

# prices download URL (period and region can be changed): https://landregistry.data.gov.uk/app/ukhpi/download/new.csv?from=2014-01-01&to=2023-12-31&location=http%3A%2F%2Flandregistry.data.gov.uk%2Fid%2Fregion%2Flondon

# Dictionary with name of borough as key and as value the mean trust of that borough of the years
# These are the 5 most and 5 least trusted boroughs (based on the mean trust value)
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

if not os.path.isdir('../data/economic/house_prices'):  # Make the house_prices folder inside data/economic
    # if it doesn't exist already
    os.mkdir('../data/economic/house_prices')


def get_link(borough):  # Return the link to the download for the house price csv
    borough = borough.replace(" ", "-")
    return f'https://landregistry.data.gov.uk/app/ukhpi/download/new.csv?from=2014-01-01&to=2023-12-31&location=http%3A%2F%2Flandregistry.data.gov.uk%2Fid%2Fregion%2F{borough}'


if DOWNLOAD_HOUSE_PRICES:
    print(f'Downloading house price data for {len(list(boroughs_trust.keys()))} boroughs')
    for borough in boroughs_trust.keys():  # Download all the house prices csv files for the 5 most
        # and 5 least trusted boroughs
        url = get_link(borough)
        save_path = f'../data/economic/house_prices/{borough}_house_prices.csv'
        download(url, save_path)
        time.sleep(1)  # Wait a bit for the download to be finished
        df = pd.read_csv(save_path)
        if len(df) < 5:
            print(f'Error with {save_path.split("/")[-1]}; only has {len(df)} rows, probably the borough '
                  f'name is not the same as in the house price database...')
print('Finished downloading the house price data! Now making the linear regression model...')


years = list(range(2016, 2023))  # Range of years to get data of; 2016 - 2023 is the years all the databases have

statistics = []
y = []

earnings = []
prices = []
unemployment = []
for BOROUGH in list(boroughs_trust.keys()):  # Get first all the data for each borough
    df_trust = get_trust(get_all=True)
    df_trust.columns = map(str.lower, df_trust.columns)
    df_trust = df_trust[df_trust.index.isin(years)]
    y = y + df_trust[BOROUGH.lower()].to_list()
    df_unemp = pd.read_csv('../data/economic/unemploymentRates.csv', delimiter=';')

    for column in df_unemp.columns[1:]:  # Make float values from the unemployment rate
        # Replace commas with dots and convert to floats
        df_unemp[column] = df_unemp[column].str.replace(',', '.').astype(float)


    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False


    BOROUGH = BOROUGH.replace('city of ', '')  # 'City of Westminster' is stored in the databases as
    # 'Westminster' so remove the 'City of ' part
    for i in range(len(years)):
        year_list = []
        # Unemployment values
        unemp_values = df_unemp[df_unemp['Area'].str.lower() == BOROUGH.lower()].values.tolist()
        try:
            unemp_values = unemp_values[0]
        except:
            print(f'Error!: {unemp_values}; for borough: {BOROUGH}')

        unemp_values = [i for i in unemp_values if is_float(i)]
        unemployment.append(unemp_values[i])

        # Earnings
        df_earning = pd.read_excel('../data/economic/earnings-residence-borough.xlsx', sheet_name='Total, Hourly')
        df_earning = df_earning[df_earning['Area'].str.lower() == BOROUGH.lower()]
        cols = ['Area'] + years
        df_earning = df_earning[cols]
        value_earning = df_earning.values.tolist()[0]
        value_earning = [i for i in value_earning if is_float(i)]
        value_earning = value_earning[i]
        earnings.append(value_earning)
        # House prices (ratio)
        # df_prices = pd.read_csv('../data/economic/ratio-house-price-earnings-residence-based.csv', delimiter=';')
        # df_prices = df_prices.dropna(axis='rows', how='all')
        # df_prices = df_prices[df_prices['Area'].str.lower() == BOROUGH.lower()]
        # price = df_prices[str(years[i])]
        # price = float(price.values[0].replace(',', '.'))
        # prices.append(price)

        # House prices (needs to be implemented)
        df_prices = pd.read_csv(f'../data/economic/house_prices/{BOROUGH.replace(" ", "-")}_house_prices.csv')
        df_prices = df_prices[df_prices['Name'].str.lower() == BOROUGH.lower()]
        df_prices['Year'] = df_prices['Period'].apply(lambda x: int(x.split('-')[0]))
        df_prices = df_prices[df_prices['Year'].isin(years)]

        # this snippet is because I keep getting files downloaded in welsh
        possible_price_cols = ['Average price All property types', 'Pris cyfartalog Pob math o eiddo']
        price_col = next((col for col in df_prices.columns if col in possible_price_cols), None)
        if not price_col:
            print(f"column not found")
            continue

        df_prices = df_prices.groupby(['Name', 'Year'])[price_col].mean().reset_index()
        df_prices = df_prices.pivot_table(index='Year', columns='Name', values=price_col)
        df_prices = df_prices.transpose()
        df_prices.reset_index(inplace=True)
        df_prices.rename(columns={'index': 'Name'}, inplace=True)
        value_prices = df_prices.values[0]
        value_prices = [i for i in value_prices if is_float(i)]
        value_prices = value_prices[i]
        prices.append(value_prices)
        print(prices)

# Make the model
x = []
for i in range(len(earnings)):
    x.append([unemployment[i], earnings[i], prices[i]])

x, y = np.array(x), np.array(y)  # Arrays needs to be a numpy array to work with the LinearRegression function
model = LinearRegression().fit(x, y)
r_sq = model.score(x, y)
coeffs = model.coef_

statistics.append({'Borough': 'ALL', 'R_sq': r_sq, 'Intercept': model.intercept_, 'Coefficient_unemp': coeffs[0],
                   'Coefficient_earnings': coeffs[1], 'Coefficient_housePrice': coeffs[2]})

scores = cross_val_score(model, x, y, cv=5)
df_statistics = pd.DataFrame(statistics)  # Make a dataframe from the model's statistics
df_statistics.to_excel('statistics.xlsx')  # Save the statistics dataframe as an excel file
print('Statistics of model saved to economic/statistics.xlsx')
