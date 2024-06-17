import os
import zipfile
from tqdm import tqdm
from functions import make_table_SQL
from functions import download
import pandas as pd
import shutil
import warnings

# -------------------- SCRAPPED -------------------
warnings.warn('GETTING STREETNAMES WAS USED FOR ANALYZING BBC ARTICLES. '
              'SINCE THAT IS SCRAPPED THIS IS NOT USED FOR THE FINAL PRESENTATION', category=DeprecationWarning)
# -------------------- SCRAPPED -------------------





download_url = {"street_names.zip": "https://api.os.uk/downloads/v1/products/OpenNames/downloads?area=GB&format=CSV&redirect"}

if os.path.isdir('../data/street_names'):
    shutil.rmtree("../data/street_names")
os.makedirs('../data/street_names')

for filename in download_url.keys():
    download(download_url[filename], f'../data/street_names/{filename}')

for file_name in download_url.keys():
    target_path = "../data/street_names/"
    source = f"../data/street_names/{file_name}"
    print(f"Extracting {file_name} ...")
    with zipfile.ZipFile(source) as zf:
        for member in tqdm(zf.infolist(), desc='Extracting '):
            try:
                zf.extract(member, target_path)
            except zipfile.error as e:
                pass

# Define the path to the directory containing the CSV files
folder_path = '../data/street_names/Data'
header_path = '../data/street_names/Doc/OS_Open_Names_Header.csv'

# Read the header file to get the column names
header_df = pd.read_csv(header_path)

# Initialize an empty list to hold the dataframes
dataframes = []
count = 0
files_num = len(os.listdir(folder_path))
# Iterate over the files in the directory
for filename in os.listdir(folder_path):
    count += 1
    if count % 100 == 0 or count == files_num:
        print(f"Merged csv-s at {count/files_num*100:.2f}% ({count}/{files_num})")
    # Construct the full path to the file
    file_path = os.path.join(folder_path, filename)
    # Read the csv file without headers, suppressing DtypeWarning
    df = pd.read_csv(file_path, header=None, low_memory=False)
    # Append the dataframe to the list
    dataframes.append(df)

# Concatenate all the dataframes
merged_df = pd.concat(dataframes, ignore_index=True)

# Assign the header to the merged dataframe
merged_df.columns = header_df.columns

# Save the merged df to the SQL database
make_table_SQL(merged_df, "street_names")
