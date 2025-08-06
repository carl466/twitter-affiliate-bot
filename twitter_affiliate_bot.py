import os
import tweepy
import random
import time
from datetime import datetime
from openai import OpenAI

# Load environment variables
TWITTER_BEARER_TOKEN = os.getenv("BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("API_KEY")
TWITTER_API_SECRET = os.getenv("API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Authenticate with Twitter API v2
client_v2 = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

# Authenticate with OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Full list of grouped trade-related keyword queries
keywords = [
    # Handyman
    '"recommend a handyman" OR "recommend handymen" OR "need a handyman" OR "looking for a handyman" OR "any good handymen" OR "find a handyman"',

    # Removal
    '"recommend a removal company" OR "recommend removal companies" OR "need a removal company" OR "looking for a removal company" OR "removal firm near me" OR "moving house help"',

    # Roofer
    '"recommend a roofer" OR "recommend roofers" OR "need a roofer" OR "looking for roofer" OR "fix my roof" OR "roof repair"',

    # Builder
    '"recommend a builder" OR "recommend builders" OR "need a builder" OR "looking for builder" OR "builder for extension" OR "trusted builder"',

    # Plumber
    '"recommend a plumber" OR "recommend plumbers" OR "need a plumber" OR "looking for a plumber" OR "any good plumbers" OR "plumber near me"',

    # Decorator
    '"recommend a decorator" OR "recommend decorators" OR "need a decorator" OR "looking for decorator" OR "painter and decorator" OR "decorator near me"'
]

# Promo replies to rotate
promo_replies = [
    "\n\nStuck finding someone reliable? This compares local trades quickly: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nThis saved me some serious hassle. Compare local trades free: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nTry this tool it shows local tradespeople and compares prices: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nNot sure who to trust? This finds reviewed local pros fast: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nI always recommend this — it quickly shows top local trades: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x"
]

# Track replied tweet IDs
replied_ids = set()

# Create a natural response + optional promo
def generate_reply(tweet_text):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're replying to someone who just asked for help with a tradesperson. "
                        "Keep it friendly and helpful. Suggest checking out a site that compares local tradespeople. "
                        "Don't use hashtags, emojis, or em dashes. Don't sound like an ad. Keep the tone natural."
                    )
                },
                {"role": "user", "content": tweet_text}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()

        # Add promo 60% of the time
        if random.random() < 0.6:
            reply += random.choice(promo_replies)

        return reply
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error generating reply: {e}")
        return None

# Search and reply function using random 4-keyword sample
def search_and_reply():
    total_matches = 0
    total_replies = 0

    search_set = random.sample(keywords, 4)

    for keyword in search_set:
        try:
            print(f"[{datetime.now().isoformat()}] 🔍 Searching for: {keyword}")
            search_results = client_v2.search_recent_tweets(query=keyword, max_results=10)
            if not search_results.data:
                continue
            for tweet in search_results.data:
                if tweet.id in replied_ids or tweet.author_id is None:
                    continue
                total_matches += 1

                print(f"\n[{datetime.now().isoformat()}] 🧠 Match Found:")
                print(f"  Text: {tweet.text}")
                print(f"  Link: https://twitter.com/i/web/status/{tweet.id}")

                reply_text = generate_reply(tweet.text)
                if reply_text:
                    try:
                        client_v2.create_tweet(
                            text=reply_text,
                            in_reply_to_tweet_id=tweet.id
                        )
                        print(f"[{datetime.now().isoformat()}] ✅ Replied to tweet {tweet.id}\n")
                        replied_ids.add(tweet.id)
                        total_replies += 1
                        time.sleep(10)
                    except Exception as e:
                        print(f"[{datetime.now().isoformat()}] ❌ Error replying to tweet {tweet.id}: {e}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] ❌ Error while processing keyword '{keyword}': {e}")
        time.sleep(5)

    print(f"\n[{datetime.now().isoformat()}] 📊 Search Cycle Summary:")
    print(f"  Total matches found: {total_matches}")
    print(f"  Total replies sent:  {total_replies}\n")

# Run every 60 minutes
if __name__ == "__main__":
    while True:
        print(f"\n[{datetime.now().isoformat()}] 🔁 Starting new search cycle...\n")
        search_and_reply()
        print(f"\n[{datetime.now().isoformat()}] ⏳ Sleeping for 60 minutes...\n")
        time.sleep(3600)
