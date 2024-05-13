import hashlib
import os
import sys
import zipfile
import gdown
from tqdm import tqdm

# Dictionary with the database available to download, key is name, value is the Google Drive id (used to download)
databases = {"crime_data": "1i0OVndCQ8739vCXTrbJG_Gd1zJupVmk4"}

# Check if user has newest version of database (using hashing), if not download the latest database from Google Drive.
print("Checking your database version...")
hash_file_id = "1p1-qeApY27-FpY50u9V-r4au3whIt2G3"
url = f'https://drive.google.com/uc?id={hash_file_id}'
output = f'../data/hash_db.txt'
gdown.download(url, output, quiet=False)
f = open("../data/hash_db.txt", "r")
newest_hash = f.read()
f.close()
print("Now hashing your database (in order to get the version), this can take a while ... It will probably take not more than 60 seconds")
current_hash = hashlib.md5(open(f'../data/crime_data.db', 'rb').read()).hexdigest()
# Remove hash_db.txt (text file containing the hash value of the latest database file) because not needed to keep
os.remove('../data/hash_db.txt')
if current_hash != newest_hash:
    print(f"There is a new version of the database found, newest version will be downloaded...\nYour hash: {current_hash}\nNewest hash: {newest_hash}")
else:
    print("You already have the latest database!")
    sys.exit(0)


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
# Remove database zip file to save space
os.remove("../data/crime_data.zip")
