import os
import zipfile
from tqdm import tqdm
import shutil

files = ["2024-02.zip",
         "2021-02.zip",
         "2018-02.zip",
         "2015-02.zip"]

# Check whether you have all the neccessary zip files containing the crime data.
files_os = os.listdir("../data/zips")
# Filter only the .zip files
zip_files = {file for file in files_os if file.endswith('.zip')}
files_set = set(files)

if files_set != zip_files:
    raise ValueError(
        f"You don't have all the required zip files. Run download_data.py first to download all the zips.\n You have: {zip_files} \n You need {files_set}")

# Make sure data folder is empty
if os.path.isdir("../data/csv"):
    shutil.rmtree("../data/csv")
os.mkdir("../data/csv")

for file_name in files:
    target_path = "../data/csv"
    source = f"../data/zips/{file_name}"
    print(f"Extracting {file_name} ...")
    with zipfile.ZipFile(source) as zf:
        for member in tqdm(zf.infolist(), desc='Extracting '):
            try:
                zf.extract(member, target_path)
            except zipfile.error as e:
                pass
