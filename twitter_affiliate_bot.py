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

# Search terms
keywords = [
    "looking for a plumber", "need an electrician", "recommend a roofer",
    "builder for extension", "find gardener", "hire handyman", "any good tilers",
    "window cleaner in", "fence repair needed", "local tradesperson needed",
    "need a decorator", "install a bathroom", "kitchen fitter recommendations",
    "cheap driveway quotes", "trusted local builder", "EV charger install",
    "loft conversion quote", "find plasterer", "house clearance help",
    "reliable removal company", "flat roof repair", "man with a van needed",
    "recommend a joiner", "painter near me", "window replacement quote",
    "shed base installation", "soffit repair", "recommend gardener",
    "install laminate flooring", "home insulation installer"
]

# Rotating promo replies
promo_replies = [
    "\n\nStuck finding someone reliable? This compares local trades quickly: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nThis saved me some serious hassle. Compare local trades free: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nTry this tool it shows local tradespeople and compares prices: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nNot sure who to trust? This finds reviewed local pros fast: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x",
    "\n\nI always recommend this — it quickly shows top local trades: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ&clickref=x"
]

# Store replied tweet IDs
replied_ids = set()

# Generate a reply using OpenAI
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
        promo = random.choice(promo_replies)
        return reply + promo
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error generating reply: {e}")
        return None

# Search and reply function
def search_and_reply():
    for keyword in keywords:
        try:
            print(f"[{datetime.now().isoformat()}] 🔍 Searching for: {keyword}")
            search_results = client_v2.search_recent_tweets(query=keyword, max_results=10)
            if not search_results.data:
                continue
            for tweet in search_results.data:
                if tweet.id in replied_ids or tweet.author_id is None:
                    continue
                print(f"[{datetime.now().isoformat()}] 💬 Found tweet ID: {tweet.id}")
                reply_text = generate_reply(tweet.text)
                if reply_text:
                    try:
                        client_v2.create_tweet(
                            text=reply_text,
                            in_reply_to_tweet_id=tweet.id
                        )
                        print(f"[{datetime.now().isoformat()}] ✅ Replied to tweet {tweet.id}")
                        replied_ids.add(tweet.id)
                        time.sleep(10)  # pause between replies
                    except Exception as e:
                        print(f"[{datetime.now().isoformat()}] ❌ Error replying to tweet {tweet.id}: {e}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] ❌ Error while processing keyword '{keyword}': {e}")
        time.sleep(5)

# Main loop
if __name__ == "__main__":
    while True:
        print(f"\n[{datetime.now().isoformat()}] 🔁 Starting new search cycle...\n")
        search_and_reply()
        print(f"\n[{datetime.now().isoformat()}] ⏳ Sleeping for 5 minutes...\n")
        time.sleep(300)
