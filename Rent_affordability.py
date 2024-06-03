import pandas as pd
import matplotlib.pyplot as plt
borough_order = ["Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames", "London"]
borough_order1 = ["Lambeth", "Islington", "Haringey", "Lewisham", "Hackney", "London"]
df_unemp = pd.read_csv('data/unemploymentRates.csv', delimiter = ';')
df_unemp = df_unemp.set_index('Area')
df_unemp = df_unemp.map(lambda x: float(x.replace(',', '.')))

def get_df_income(file_path):
    df = pd.read_excel(file_path, sheet_name="Total, Hourly", usecols= "A,P:V")
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df
df_income = get_df_income('data/earnings-residence-borough.xlsx')
df_income_best = df_income.loc[df_income["Area"].isin(borough_order1)] #edit the borough order for most/least trusting boroughs
df_income_best = df_income_best.set_index(df_income.columns[0]).transpose()

print(df_income_best)
#plot
df_income_best.plot(kind = "line", marker='o', linewidth=3, ax=plt.gca())
plt.title('Hourly Income by Borough')
plt.xlabel('Year')
plt.ylabel('Income (Hourly)')
plt.grid(True)
plt.legend(title='Borough')
plt.show()
def get_df_crime(file_path):
    df_crime = pd.read_csv(file_path, delimiter = ',')
    df_crime = df_crime[['Crime ID', 'Month', 'borough']]

    df_crime['Month'] = pd.to_datetime(df_crime['Month'])

    # Filter out dates before 2016 and after 2023
    df_crime = df_crime[df_crime['Month'].dt.year >= 2016]
    df_crime = df_crime[df_crime['Month'].dt.year <= 2023]

    df_crime['Month'] = pd.to_datetime(df_crime['Month'], format='%Y-%m')
    grouped_crime = df_crime.groupby(
        [df_crime['Month'].dt.year.rename('Year'), 'borough']).size().reset_index(name='Count')

    pivot_df_crime = grouped_crime.pivot(index='Year', columns='borough', values='Count')
    return pivot_df_crime
def unemp_crime_best(df_crime_best):
    df_crime_best = get_df_crime('data/metropolitan_normal_with_best_boroughs.csv')
    del df_crime_best['Westminster']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    #unemployment plot 1
    df_unemp.loc[["Kensington and Chelsea", "Sutton", "Bexley", "Kingston upon Thames"]].transpose().plot(kind='line', marker='o', ax=ax1)
    ax1.set_title('Unemployment Rate per Most Trusting Boroughs')
    ax1.set_xlabel('Fiscal Year')
    ax1.set_ylabel('Unemployment Rate')
    ax1.grid(True)
    ax1.legend(title='Borough')
    ax1.tick_params(axis='x', labelrotation=45)

    #crime plot 1
    df_crime_best = df_crime_best[borough_order]
    df_crime_best.plot(kind='line', marker='o', ax=ax2)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Crime Count')
    ax2.set_title('Total Crimes per Most Trusting Boroughs')
    ax2.legend(title='Borough')
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
def four_plots(df_crime_best, df_crime_worst):
    df_crime_best = get_df_crime('data/metropolitan_normal_with_best_boroughs.csv')
    df_crime_worst = get_df_crime('data/metropolitan_normal_with_worst_boroughs.csv')
    #plotting line charts
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 14))
    #unemployment plot 1
    df_unemp.loc[["Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames"]].transpose().plot(kind='line', marker='o', ax=ax1)
    ax1.set_title('Unemployment Rate per Most Trusting Boroughs')
    ax1.set_xlabel('Fiscal Year')
    ax1.set_ylabel('Unemployment Rate')
    ax1.grid(True)
    ax1.legend(title='Borough')
    ax1.tick_params(axis='x', labelrotation=45)

    #crime plot 1
    df_crime_best = df_crime_best[borough_order]
    df_crime_best.plot(kind='line', marker='o', ax=ax2)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Crime Count')
    ax2.set_title('Total Crimes per Most Trusting Boroughs')
    ax2.legend(title='Borough')
    ax2.grid(True)

    #unemployment plot 2
    df_unemp.loc[["Lambeth", "Islington", "Haringey", "Lewisham", "Hackney"]].transpose().plot(kind='line', marker='o', ax=ax3)
    ax3.set_title('Unemployment Rate per Least Trusting Boroughs')
    ax3.set_xlabel('Fiscal Year')
    ax3.set_ylabel('Unemployment Rate')
    ax3.grid(True)
    ax3.legend(title='Borough')
    ax3.tick_params(axis='x', labelrotation=45)

    #crime plot 2
    df_crime_worst = df_crime_worst[borough_order1]
    df_crime_worst.plot(kind='line', marker='o', ax=ax4)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Crime Count')
    ax4.set_title('Total Crimes per Least Trusting Boroughs')
    ax4.legend(title='Borough')
    ax4.grid(True)

    plt.tight_layout()
    plt.show()

'''
#plotting line charts
df_unemp.loc[["Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames"]].transpose().plot(kind='line', marker='o', figsize=(12, 8))
df_unemp.loc[["London"]].transpose().plot(kind='line', marker='o', linewidth=3, ax=plt.gca())
plt.title('Unemployment Rate per Most Trusting Boroughs')
plt.xlabel('Fiscal Year')
plt.ylabel('Unemployment Rate')
plt.grid(True)
plt.legend(title='Borough')
plt.show()

'''

'''

Analysis of Unemployment Rates:
The plots show that all boroughs experienced a dip in 
unemployment rates in the fiscal year of 2022, except for Hackney, the lowest ranking
borough on the trust scale. As expected, all boroughs experienced a rise in unemployment rates
in 2020 (due to lay offs during the pandemic). The most trusting boroughs look to have a lower
rate than London overall, showing that these top 5 boroughs are especially well-off.

Overall, the most trusting boroughs have their unemployement rate 
ranging from ~2.3 to ~6.1. (3.8)

The least trusting boroughs range from ~3.5 to ~7.2. (3.7) This group has a higher unemployment
rates which point to 
'''
'''

df = pd.read_csv('data/ratio-house-price-earnings-residence-based.csv', delimiter = ';')
df_indexed = df.set_index('Area')
del df_indexed['2002']
df_best_worst = df_indexed.loc[["Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames",
                                "Lambeth", "Islington", "Haringey", "Lewisham", "Hackney"]]

#turning the ratios from object to float
df_best_worst = df_best_worst.map(lambda x: float(x.replace(',', '.')))

df_best = df_best_worst.loc[["Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames"]]
df_worst = df_best_worst.loc[["Lambeth", "Islington", "Haringey", "Lewisham", "Hackney"]]


#plotting line charts
df_best.transpose().plot(kind='line', marker='o', figsize=(12, 8))
plt.title('Property Affordability for Most Trusting Boroughs (2016-2022)')
plt.xlabel('Year')
plt.ylabel('Income to Rent Ratio')
plt.grid(True)
plt.legend(title='Borough')
plt.show()
df_worst.transpose().plot(kind='line', marker='o', figsize=(12, 8))
plt.title('Property Affordability for Least Trusting Boroughs (2016-2022)')
plt.xlabel('Year')
plt.ylabel('Income to Rent Ratio')
plt.grid(True)
plt.legend(title='Borough')
plt.show()
'''
'''
Analysis: 
The line plot shows that the two boroughs that have the most trust and confidence
in the police (Kensington and Chelsea, city of Westminster) 
also have less affordable housing (or highest rent prices)

Although the lower rated boroughs (Sutton and Bexley) have the most affordable housing
out of the 10 boroughs. 
'''
