import pandas as pd
import matplotlib.pyplot as plt



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
Analysis: 
The line plot shows that the two boroughs that have the most trust and confidence
in the police (Kensington and Chelsea, city of Westminster) 
also have less affordable housing (or highest rent prices)

Although the lower rated boroughs (Sutton and Bexley) have the most affordable housing
out of the 10 boroughs. 
'''
