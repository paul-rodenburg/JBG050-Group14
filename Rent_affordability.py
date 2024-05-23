import pandas as pd
import matplotlib.pyplot as plt

df_unemp = pd.read_csv('data/unemploymentRates.csv', delimiter = ';')
df_unemp = df_unemp.set_index('Area')
df_unemp = df_unemp.map(lambda x: float(x.replace(',', '.')))
#plotting line charts
df_unemp.loc[["Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames"]].transpose().plot(kind='line', marker='o', figsize=(12, 8))
df_unemp.loc[["London"]].transpose().plot(kind='line', marker='o', linewidth=3, ax=plt.gca())

plt.title('Unemployment Rate per Most Trusting Boroughs')
plt.xlabel('Fiscal Year')
plt.ylabel('Unemployment Rate')
plt.grid(True)
plt.legend(title='Borough')
plt.show()
print(df_unemp)


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
