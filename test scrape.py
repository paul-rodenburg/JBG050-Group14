from ntscraper import Nitter
import json
# No instance specified, using random instance https://nitter.privacydev.net
scraper = Nitter(log_level=1, skip_instance_check=False)
tweets = scraper.get_tweets("london", mode="hashtag", number=10)
with open('data/tweets.json', 'w') as f:
    json.dump(tweets, f)
