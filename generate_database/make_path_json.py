import json
import os
import glob

directory = "../data/csv"
paths = {}
count = 0
for root, dirs, files in os.walk(directory):
    current_file = glob.glob(os.path.join(root, '*.csv'))
    for file in current_file:
        if ".csv" in file:  # We only want csv file no hidden system files or other files
            name = "-".join(file.split("-")[3:]).replace(".csv", "")
            count += 1
            try:
                paths[name].append(file)
            except:
                paths[name] = [file]

print(f"{count} files to json")
with open('../data/paths.json', 'w') as f:
    json.dump(paths, f, indent=2)
