## How to run the code
Follow these steps in order to generate the SQL database containing all the crime data from 2010-12 to 2024-02:
1. Run download_data.py. This can take a while because it needs to download **6.4 GB**. Zips will be downloaded to data/zips.
2. Run unpack_data.py. This will unzip all the zip files to the data/csv folder.
3. generate_database.py. This will generate the SQL database, this can take a while (and will take a couple of GB's of RAM) because there is so much data. SQL database will be saved to data/crime_data.db.

Tip: you can use this tool to inspect the SQL database: [Download sqlitebrowser](https://sqlitebrowser.org/dl/)
