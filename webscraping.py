import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os


def extract_links_from_html(file_path):
    # Read HTML content from file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_string = file.read()

    # Regular expression pattern to match links
    soup = BeautifulSoup(html_string, 'html.parser')

    # Find the div with data-testid="liverpool-card"
    links = soup.find_all('div', {'data-testid': 'liverpool-card'})
    links_return = []
    for link in links:
        a_tag = link.find('a', {'data-testid': 'internal-link'})
        if a_tag:
            # print(a_tag['href'])  # This will print the href attribute of the <a> tag
            links_return.append(a_tag['href'])

    return links_return

files_os = os.listdir("data\zips\\bbc")
# Filter only the .zip files
html_files = [file for file in files_os if file.endswith('.html')]
links = []
for file in html_files:
    path = f'data\zips\\bbc{file}'
    links.extend(extract_links_from_html(path))

errors = 0
# Make sure we have unique links
links = list(set(links))

articles = []
count = 0
print(f"Found {len(links)} links/articles!")
for url in links:
    try:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        data = json.loads(soup.select_one("#__NEXT_DATA__").text)
        #data1 = json.loads(soup.select_one("__next").text)

        # Extracting headline and text content
        page = next(
            v for k, v in data["props"]["pageProps"]["page"].items() if k.startswith("@")
        )
        text = ""
        headline = ""
        for c in page["contents"]:
            if c["type"] == "headline":
                headline_to_add = c["model"]["blocks"][0]["model"]["text"]
                headline = f"{headline}\n{headline_to_add}"
            elif c["type"] == "text":
                text_to_add = c["model"]["blocks"][0]["model"]["text"]
                text = f"{text}\n{text_to_add}"

        # Extracting publishing date (Using RE, regular expression, this is a hacky way but it works and it will always work
        # I think)
        pattern = r'"publicationDate":"(\d+)"'
        html_content = str(soup)
        # Use re.search to find the pattern in the text
        match = re.search(pattern, html_content)

        if match:  # There is a regex match
            publication_date = match.group(1)

            # Time is given into seconds (epoch format) so we convert it to a readable format
            timestamp_seconds = int(publication_date) / 1000
            publication_date = datetime.fromtimestamp(timestamp_seconds)
        else:  # Publication date is not found using regex!
            errors += 1
            publication_date = None

        article = {"publication_date": publication_date, "url": url, "text": text, "headline": headline}
        articles.append(article)
    except Exception as e:
        errors += 1
        print(f'Error (#{errors}): {e}')
    count += 1
    if count % 20 == 0:
        print(f'At {count/len(links)*100:.2f}% ({count}/{len(links)})')
df = pd.DataFrame(articles)
df['text'] = df['text'].str.strip()
df['headline'] = df['headline'].str.strip()
df.to_parquet('data/bbc.parquet')

sqlite_db_path = 'data/crime_data.db'
# Define the SQLite table name
table_name = "BBC_articles"
print(f"Beginning SQL conversion of {table_name} into {sqlite_db_path}")
# Create a SQLite connection and cursor
conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

# Create a table in the SQLite database with the same columns as the DataFrame
df.to_sql(table_name, conn, index=False, if_exists='replace')

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"CSV data successfully imported into SQLite database: {sqlite_db_path}, table: {table_name}")
# Print summary statistics
print(f"Table {table_name} successfully converted into the SQL database ({sqlite_db_path})")

