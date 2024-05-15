import json
import requests
from bs4 import BeautifulSoup

url = 'https://www.bbc.com/news/uk-england-london-53198702'

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

# Extracting publishing date (doesnt work)
publishing_time_tag = soup.select_one("time")
if publishing_time_tag:
    publishing_date = publishing_time_tag.get("datetime")
    print("Publishing Date:", publishing_date)
else:
    print("Publishing date not found.")
