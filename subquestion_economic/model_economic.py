import math

import statsmodels.api as sm
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split, cross_val_score
import pandas as pd
import numpy as np
from generate_database.functions import get_trust
from generate_database.functions import download
import os
import sqlite3
from sklearn.exceptions import UndefinedMetricWarning
import warnings


# Suppress the specific warning
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

DOWNLOAD_HOUSE_PRICES = False  # Set to False ONLY when you already have downloaded the house price data

# prices download URL (period and region can be changed): https://landregistry.data.gov.uk/app/ukhpi/download/new.csv?from=2014-01-01&to=2023-12-31&location=http%3A%2F%2Flandregistry.data.gov.uk%2Fid%2Fregion%2Flondon

if not os.path.isdir('../data/economic/house_prices'):  # Make the house_prices folder inside data/economic
    # if it doesn't exist already
    os.mkdir('../data/economic/house_prices')


def get_link(borough):  # Return the link to the download for the house price csv
    borough = borough.replace(" ", "-").lower()
    return f'https://landregistry.data.gov.uk/app/ukhpi/download/new.csv?from=2014-01-01&to=2023-12-31&location=http%3A%2F%2Flandregistry.data.gov.uk%2Fid%2Fregion%2F{borough}'


if DOWNLOAD_HOUSE_PRICES:
    print(f'Downloading house price data for {len(list(boroughs))} boroughs')
    for borough in boroughs:  # Download all the house prices csv files for the 5 most
        # and 5 least trusted boroughs
        url = get_link(borough)
        save_path = f'../data/economic/house_prices/{borough.lower()}_house_prices.csv'
        download(url, save_path)
        # time.sleep(1)  # Wait a bit for the download to be finished
        df = pd.read_csv(save_path)
        if len(df) < 5:
            print(f'Error with {save_path.split("/")[-1]}; only has {len(df)} rows, probably the borough '
                  f'name is not the same as in the house price database...')
print('Finished downloading the house price data! Now making the linear regression model...')


def make_economic_model(boroughs):
    years = list(range(2016, 2023))  # Range of years to get data of; 2016 - 2023 is the years all the databases have

    statistics = []
    y = []

    earnings = []
    prices = []
    sales_volumes = []
    prices_first_time_buyers = []
    unemployment = []
    for BOROUGH in boroughs:  # Get first all the data for each borough
        df_trust = get_trust(get_all=True)
        df_trust.columns = map(str.lower, df_trust.columns)
        df_trust = df_trust[df_trust.index.isin(years)]
        df_trust = df_trust.dropna(axis='columns',
                                   how='all')  # Sometimes there is a dataframe with a column with only NULL values: remove this column
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

        for i in range(len(years)):
            year_list = []
            # Unemployment values
            borough_unemp = BOROUGH.lower().replace('city of ', '')
            unemp_values = df_unemp[df_unemp['Area'].str.lower() == borough_unemp].values.tolist()
            try:
                unemp_values = unemp_values[0]
            except:
                print(f'Error!: {unemp_values}; for borough: {BOROUGH} ({borough_unemp})')
                print(df_unemp)

            unemp_values = [i for i in unemp_values if is_float(i)]
            unemployment.append(unemp_values[i])

            # Earnings
            df_earning = pd.read_excel('../data/economic/earnings-residence-borough.xlsx', sheet_name='Total, Hourly')
            df_earning = df_earning[df_earning['Area'].str.lower() == BOROUGH.lower().replace('city of ', '')]
            cols = ['Area'] + years
            df_earning = df_earning[cols]
            value_earning = df_earning.values.tolist()[0]
            value_earning = [i for i in value_earning if is_float(i)]
            value_earning = value_earning[i]
            earnings.append(value_earning)

            # House prices (mean price for all properties, sales volume, price for first time buyers)
            df_prices = pd.read_csv(f'../data/economic/house_prices/{BOROUGH.lower()}_house_prices.csv')
            df_prices['Period'] = pd.to_datetime(df_prices['Period'])
            df_prices['Year'] = df_prices['Period'].dt.year
            df_prices = df_prices[df_prices['Year'] == years[i]]
            sales_volume_col = list(df_prices.columns)[4]
            col = list(df_prices.columns)[
                6]  # Sometimes the column names have weird names so we just select the 7th one, which is always the price of all properties
            col_price_first_time_buyers = list(df_prices.columns)[27]
            try:
                price = math.log(df_prices[col].mean())
                sales_volume = df_prices[sales_volume_col].mean()
                price_first_time_buyers = df_prices[col_price_first_time_buyers].mean()
            except Exception as e:
                print(
                    f'Error!: ({e}): {df_prices} \nfor borough: {BOROUGH}; year: {years[i]}\ncolumns: {df_prices.columns}')
            prices.append(price)
            sales_volumes.append(sales_volume)
            prices_first_time_buyers.append(price_first_time_buyers)

    # Make the model
    x = []
    for i in range(len(earnings)):
        x.append([unemployment[i], earnings[i], prices[i], sales_volumes[i], prices_first_time_buyers[i]])

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Train the model
    model = LinearRegression().fit(x_train, y_train)

    # Make predictions
    y_pred = model.predict(x_test)

    # ----------- K FOLD ----------------

    # Train the model using k-fold cross-validation
    if len(boroughs) > 1:
        model_test = LinearRegression()
        scores = cross_val_score(model_test, x, y, cv=len(boroughs), scoring='r2')
        mean_r2 = np.mean(scores)
        mean_mse = -np.mean(scores)  # Mean of negative MSEs
        print(
            f'{len(boroughs)} boroughs - Cross K-fold cross validation:\nscores: {scores}\nmean_r2: {mean_r2}\nmean_mse: {mean_mse}\nTHIS IS NOT USED FOR THE SUMMARIES MODELS')
        print()
    # ---------- Create summary ----------

    # Train the model using statsmodels
    x_train_sm = sm.add_constant(x_train)  # Add a constant term for the intercept
    model_sm = sm.OLS(y_train, x_train_sm).fit()

    # Make predictions
    x_test_sm = sm.add_constant(x_test)  # Add a constant term for the intercept

    column_names = ['const', 'unemployment', 'earnings', 'prices', 'sales_volumes', 'prices_first_time_buyers']
    summary = model_sm.summary(xname=column_names)

    # Calculate R^2 and coefficients
    r_sq = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    coeffs = model.coef_
    if len(boroughs) == 1:
        text_borough = boroughs[0]
    else:
        text_borough = len(boroughs)
    statistics.append({'Boroughs': text_borough, 'R_sq': r_sq, 'MSE': mse, 'Intercept': model.intercept_,
                       'Coefficient_unemp': coeffs[0],
                       'Coefficient_earnings': coeffs[1], 'Coefficient_PropertyPriceAllTypes': coeffs[2],
                       'C_SalesVolume': coeffs[3],
                       'C_PriceFirst-TimeBuyers': coeffs[4]})

    # Make plot
    if len(boroughs) > 1:
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, edgecolor='k', alpha=0.7)
        plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'k--', lw=3)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title(f'Actual vs Predicted Trust in {len(boroughs)} Boroughs')
        plt.xlim((0.7, 0.95))
        plt.ylim((0.7, 0.95))
        if not os.path.isdir('figures'):
            os.mkdir('figures')
        plt.savefig(f'figures/{len(boroughs)} boroughs model.png')

    return summary


if not os.path.isdir('stats'):
    os.mkdir('stats')


def write_summary(summary, filename):
    with open('stats/AA_all_stats.txt', 'w') as f:
        f.write(str(summary_all))


# Make economic model with all the boroughs
q_boroughs = 'SELECT Borough FROM Trust'
conn = sqlite3.connect('../data/crime_data.db')
df_boroughs = pd.read_sql_query(q_boroughs, conn)
conn.close()
boroughs = list(set(df_boroughs['Borough'].values))
summary_all = make_economic_model(boroughs)
write_summary(summary_all, 'stats/AA_all_stats.txt')

# Make 1 economic model for each borough
df_stats = pd.DataFrame()
for borough in boroughs:
    summmary_borough = make_economic_model([borough])
    write_summary(summmary_borough, f'stats/{borough}_stats.txt')

# Make economic model with only the best and worst 5
boroughs = ["Kensington and Chelsea", "City of Westminster", "Sutton", "Bexley", "Kingston upon Thames",
            "Lambeth", "Islington", "Haringey", "Lewisham", "Hackney"]
summary_most_least = make_economic_model(boroughs)
write_summary(summary_most_least, 'stats/AA_most_least_stats.txt')

print('Summaries of the models saved in the econmic/stats folder!')
