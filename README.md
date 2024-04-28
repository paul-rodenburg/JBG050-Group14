## How to run the code

Follow these steps in order to generate the SQL database containing all the crime data from 2010-12 to 2024-02:

1. Run `download_data.py`. This can take a while because it needs to download **6.4 GB**. Zips will be downloaded to data/zips.
2. Run `unpack_data.py`. This will unzip all the zip files to the data/csv folder.
3. Run `generate_database.py`. This will generate the SQL database, this can take a while (and will take a couple of GB's of RAM) because there is so much data. SQL database will be saved to data/crime_data.db.

## Download database

Alternatively you can download the database directly from Google Drive to avoid the running time of downloading the data and generating the database. Follow these steps to download the database:

1. Run `download_database.py`, this file will download a zip containing the database, this python file will also automatically extract the zip for you. Database will be saved in the data folder. Zip file will be **2.11 GB** and the database itself will be **9,.12 GB**.

Tip: you can use this tool to inspect the SQL database: [Download sqlitebrowser](https://sqlitebrowser.org/dl/)
