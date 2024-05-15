import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

API_KEY = '87007567182b41abbec5e78702dea483'

# All the URL of news articles.
urls = ['https://www.bbc.com/news/uk-england-london-53198702']


for url in urls:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    data = json.loads(soup.select_one("#__NEXT_DATA__").text)
    #data1 = json.loads(soup.select_one("__next").text)

    # Extracting headline and text content
    page = next(
        v for k, v in data["props"]["pageProps"]["page"].items() if k.startswith("@")
    )
    for c in page["contents"]:
        if c["type"] == "headline":
            print("Headline:", c["model"]["blocks"][0]["model"]["text"])
        elif c["type"] == "text":
            print("Text:", c["model"]["blocks"][0]["model"]["text"])

    # Extracting publishing date (Using RE, regular expression, this is a hacky way but it works and it will always work
    # I think)
    pattern = r'"publicationDate":"(\d+)"'
    html_content = str(soup)
    # Use re.search to find the pattern in the text
    match = re.search(pattern, html_content)

    if match:  # There is a regex match
        publication_date = match.group(1)
        print("Pubdate using RE!")

        # Time is given into seconds (epoch format) so we convert it to a readable format
        timestamp_seconds = int(publication_date) / 1000
        publication_date = datetime.fromtimestamp(timestamp_seconds)
        print(publication_date)
    else:  # Publication date is not found using regex!
        print("Publication date not found.")
