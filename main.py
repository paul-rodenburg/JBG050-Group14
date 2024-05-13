# Ask the user whether he/she wants to download or generate the database. Result will be the exact same database
# but by generating the database you will get the csv files also (generating will take more space and can take more time
# if your internet speed is high to download the database quickly)
def get_database():
    x = input("Do you want to download the database (1) or generate the database yourself (2). Type 1 or 2")
    if x == "1":
        print("Downloading the database...")
        # Importing lets the python scripts run
        from download_database import download_databases
    elif x == "2":
        print("Generating the database...")
        # Importing lets the python scripts run
        from generate_database import download_data, unpack_data, make_path_json, generate_database, PAS_to_sql
    else:
        print("Invalid input")
        get_database()


get_database()
