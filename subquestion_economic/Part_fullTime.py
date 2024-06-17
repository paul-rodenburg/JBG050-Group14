import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

xls = pd.ExcelFile('../data/employment-status-by-genderxls.xlsx')
ordered_boroughs = [
    "Kensington and Chelsea", "Westminster", "Sutton", "Bexley", "Kingston upon Thames",
    "Lambeth", "Islington", "Haringey", "Lewisham", "Hackney"
]
years = list(range(2016, 2024))
dfs = []
for year in years:
    df = pd.read_excel(xls, str(year))
    df['Year'] = year
    df['Proportion_full_to_part_time'] = np.where(df['% in employment working part-time - working age'] != 0, df['% in employment working full-time - working age']/df['% in employment working part-time - working age'], np.nan)
    dfs.append(df)


combined_df = pd.concat(dfs, ignore_index=True)
del combined_df['Unnamed: 2']

print(combined_df)
filtered_df = combined_df[combined_df['Area'].isin(ordered_boroughs)]
filtered_df['Area'] = pd.Categorical(filtered_df['Area'], categories=ordered_boroughs, ordered=True)
filtered_df = filtered_df.sort_values('Area')
pivot_table = filtered_df.pivot_table(index='Area', columns='Year', values='Proportion_full_to_part_time')

# plotting heatmap
plt.figure(figsize=(14, 8))
sns.heatmap(pivot_table, annot=True, cmap='coolwarm', cbar_kws={'label': 'Ratio (Full-time to Part-time)'})
boroughs = pivot_table.index.tolist()
line_position = boroughs.index("Lambeth")
plt.axhline(y=line_position, color='black', linewidth=2)
plt.title('Heatmap of Ratios (Full-time to Part-time Employees) per Borough')
plt.ylabel('Boroughs')
plt.xlabel('Year')
plt.show()
