import os
import zipfile
import tqdm

# Makes the csv folder when it doesn't exist already. Folder is for the unpacked zips
if not os.path.isdir("data/csv"):
    os.mkdir("data/csv")

files = ["2024-02.zip",
         "2021-02.zip",
         "2018-02.zip",
         "2015-02.zip"]

# Check whether you have all the neccessary zip files containing the crime data.
files_os = os.listdir("data/zips")
# Filter only the .zip files
zip_files = {file for file in files_os if file.endswith('.zip')}
files_set = set(files)

if files_set != zip_files:
    print("You don't have all the required zip files. Run download_data.py first to download all the zips.")

for file_name in files:
    target_path = "data/csv"
    source = f"data/zips/{file_name}"
    print(f"Extracting {file_name} ...")
    with zipfile.ZipFile(source) as zf:
        for member in tqdm(zf.infolist(), desc='Extracting '):
            try:
                zf.extract(member, target_path)
            except zipfile.error as e:
                pass