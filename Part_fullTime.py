import pandas as pd     andas

xls = pd.ExcelFile('data/employment-status-by-genderxls.xlsx')
df1 = pd.read_excel(xls, '2016')
df2 = pd.read_excel(xls, '2017')
df3 = pd.read_excel(xls, '2018')
df4 = pd.read_excel(xls, '2019')
df5 = pd.read_excel(xls, '2020')
df6 = pd.read_excel(xls, '2021')
df7 = pd.read_excel(xls, '2022')
df8 = pd.read_excel(xls, '2023')