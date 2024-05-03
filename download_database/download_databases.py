import hashlib
import os
import zipfile
import gdown
from tqdm import tqdm

# Dictionary with the database available to download, key is name, value is the Google Drive id (used to download)
databases = {"crime_data": "1pI6LmGOCYL589LRCPHhW73YgwqD6My7p"}
print("Checking your database version...")
hash_file_id = ""
url = f'https://drive.google.com/uc?id={hash_file_id}'
output = f'../data/hash_db.txt'
gdown.download(url, output, quiet=False)
f = open("../data/hash_db.txt", "r")
newest_hash = f.read()
f.close()
current_hash = hashlib.md5(open(f'../data/hash_db.txt', 'rb').read()).hexdigest()
if current_hash != newest_hash:
    print(f"There is a new version of the database found, newest version will be downloaded...\nYour hash: {current_hash}\n Newest hash: {newest_hash}")

# Download all database from Google Drive
for database in databases.keys():
    # Database file is already on disk, aks user to replace/update it
    if os.path.isfile(f'data/{database}.db'):
        replace = input(f"data/{database}.db already exists. Do you want to replace it? [y/n]")
        if replace.lower() == "y" or replace.lower() == "yes":
            os.remove(f'data/{database}.db')
        else:  # If user type something else than y or yes, it will continue to download the next database (if any).
            # This is in the else option because it's the safest option: user keeps the database file
            continue
    id = databases[database]
    url = f'https://drive.google.com/uc?id={id}'
    output = f'../data/{database}.zip'
    gdown.download(url, output, quiet=False)

# Unzip the downloaded zip file(s) (containing the database file)
target_path = "../data"
sources = ["data/crime_data.zip"]
for source in sources:
    print(f"Extracting {source} ...")
    with zipfile.ZipFile(source) as zf:
        for member in tqdm(zf.infolist(), desc='Extracting '):
            try:
                zf.extract(member, target_path)
            except zipfile.error as e:
                pass
