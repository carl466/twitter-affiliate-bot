
import os
import time
import random
import openai
import tweepy
import csv
from datetime import datetime, timedelta

# --- Configuration ---
PROMOTIONAL_LINK = "https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ"
PROMOTIONAL_RATIO = (0.1, 0.3)  # 10% to 30%
REPLY_DELAY = (90, 180)  # Delay between replies in seconds
LOG_FILE = "tweet_log.csv"
TRADE_KEYWORDS = [
    "electrician", "plumber", "roofer", "tiler", "gardener", "handyman",
    "painter", "decorator", "bricklayer", "joiner", "flooring", "loft",
    "cleaner", "builder", "fencing", "insulation", "flat roof", "removal",
    "window fitter", "tree surgeon", "ev charger", "bathroom", "kitchen"
]

# --- Authenticate Twitter ---
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"), os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# --- Load OpenAI ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Helper Functions ---

def log_tweet(tweet_id, username, reply, promo):
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), tweet_id, username, reply, promo])

def generate_reply(tweet_text, promo=False):
    personality = "You're a helpful UK homeowner called Jay who shares what’s worked on your DIY jobs. Keep the tone casual and authentic. Avoid sounding like a bot or salesperson."

    prompt = f"""
    {personality}

    Someone just posted: "{tweet_text}"

    Your reply should be short, natural and helpful.
    {"You want to casually recommend this site: " + PROMOTIONAL_LINK if promo else "Don't include any links, just offer useful advice or encouragement."}

    Write the reply:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

def search_and_reply():
    recent_tweets = client.search_recent_tweets(
        query=" OR ".join([f'"{kw}"' for kw in TRADE_KEYWORDS]) + " -is:retweet lang:en",
        max_results=10
    )

    if not recent_tweets.data:
        return

    for tweet in recent_tweets.data:
        if tweet.author_id == api.verify_credentials().id:
            continue

        promo_reply = random.random() < random.uniform(*PROMOTIONAL_RATIO)
        reply_text = generate_reply(tweet.text, promo=promo_reply)

        try:
            api.update_status(
                status=f"@{tweet.author_id} {reply_text}",
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True
            )
            log_tweet(tweet.id, tweet.author_id, reply_text, promo_reply)
            time.sleep(random.randint(*REPLY_DELAY))
        except Exception as e:
            print("Error replying:", e)

# --- Run Forever ---
while True:
    search_and_reply()
    time.sleep(300)  # Check every 5 minutes
