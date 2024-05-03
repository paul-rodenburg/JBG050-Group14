def get_database():
    x = input("Do you want to download the database (1) or generate the database yourself (2). Type 1 or 2")
    if x == "1":
        print("Downloading the database...")
        from download_database import download_databases
    elif x == "2":
        print("Generating the database...")
        from generate_database import download_data, unpack_data, make_path_json, generate_database, PAS_to_sql
    else:
        print("Invalid input")
        get_database()


get_database()
