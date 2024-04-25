import requests
from tqdm import tqdm
import os
import hashlib

# Makes the data folder when it doesn't exist already. Folder is for the downloaded zips, csv's, and SQL database
if not os.path.isdir("data"):
    os.mkdir("data")
# Makes the zips folder (in the data folder) when it doesn't exist already. Folder is for the downloaded zips
if not os.path.isdir("data/zips"):
    os.mkdir("data/zips")

# Function to download files from an URL with a progress bar
def download(url: str, fname: str, chunk_size=1024):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            bar.update(size)

# Dictionary of needed file names with the hash/checksum as value so it can be checked if you have the right file.
files = {"2024-02.zip": "46057dde71e363cc0bf564030a932f83",
         "2021-02.zip": "c98026342d18c16ebd8725e3192b4625",
         "2018-02.zip": "7e09e8efe92285ea0cf061469ab6be37",
         "2015-02.zip": "d7de411e0900c2f75bbb2cabbefa6388"}

# Download all neccessary zips containing the data from https://data.police.uk/data/archive/
for file_name in files.keys():
    if os.path.isfile(f"data/zips/{file_name}"):
        hash = hashlib.md5(open(f'data/zips/{file_name}','rb').read()).hexdigest()
        print(f"Hash of {file_name}: {hash}")
        if hash == files[file_name]:
            print(f"{file_name} was already downloaded correctly!")
            continue
        os.remove(f"data/zips/{file_name}")
        print(f"Redownloading {file_name} ...")
    download(f"https://data.police.uk/data/archive/{file_name}", f"data/zips/{file_name}")
    hash_finished = hashlib.md5(open(f'data/zips/{file_name}', 'rb').read()).hexdigest()
    if hash == files[file_name]:
        print(f"File {file_name} is succesfully downloaded!")
    else:
        print(f"File {file_name} is not downloaded correctly. Run this python file again to redownload the file")

