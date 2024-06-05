from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from generate_database.functions import get_trust


# prices download URL (period can be changed): https://landregistry.data.gov.uk/app/ukhpi/download/new.csv?from=2014-01-01&to=2023-12-31&location=http%3A%2F%2Flandregistry.data.gov.uk%2Fid%2Fregion%2Flondon

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

codes_borough = {

}
years = list(range(2016, 2023))

statistics = []
y = []


earnings = []
prices = []
unemployment = []
for BOROUGH in list(boroughs_trust.keys()):
    df_trust = get_trust(get_all=True)
    df_trust.columns = map(str.lower, df_trust.columns)
    df_trust = df_trust[df_trust.index.isin(years)]
    y = y + df_trust[BOROUGH.lower()].to_list()
    df_unemp = pd.read_csv('../data/economic/unemploymentRates.csv', delimiter=';')

    for column in df_unemp.columns[1:]:
        # Replace commas with dots and convert to floats
        df_unemp[column] = df_unemp[column].str.replace(',', '.').astype(float)


    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False



    BOROUGH = BOROUGH.replace('city of ', '')
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

        # House prices
        df_prices = pd.read_csv('../data/economic/Average-prices-2024-03.csv')


# Make the model

x = []
for i in range(len(earnings)):
    x.append([unemployment[i], earnings[i], prices[i]])


x, y = np.array(x), np.array(y)
model = LinearRegression().fit(x, y)
r_sq = model.score(x, y)
coeffs = model.coef_

statistics.append({'Borough': 'ALL', 'R_sq': r_sq, 'Intercept': model.intercept_, 'Coefficient_unemp': coeffs[0],
                   'Coefficient_earnings': coeffs[1], 'Coefficient_housePrice': coeffs[2]})
# print(f"coefficient of determination: {r_sq}")
#
# print(f"intercept: {model.intercept_}")
#
# print(f"coefficients: {model.coef_}")

df_statistics = pd.DataFrame(statistics)
df_statistics.to_excel('statistics.xlsx')
print('Statistics of model saved to economic/statistics.xlsx')
