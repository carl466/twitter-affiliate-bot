
import os
import tweepy
import openai
import random
import time

# Load environment variables
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Authenticate with Twitter v2
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

# Keywords to search for
keywords = [
    "looking for a plumber", "need an electrician", "recommend a roofer",
    "builder for extension", "find gardener", "hire handyman", "any good tilers",
    "window cleaner in", "fence repair needed", "local tradesperson needed"
]

# Promotional reply chance: 10–30%
PROMO_LINK = "https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ"

def generate_reply(tweet_text, promo=False):
    instruction = "Reply like a helpful UK homeowner giving friendly advice. Avoid sounding like a bot or ad. No em dashes."
    if promo:
        instruction += f" You can optionally recommend this site: {PROMO_LINK}."

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": tweet_text}
        ],
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

def search_and_reply():
    for keyword in keywords:
        try:
            results = client.search_recent_tweets(query=keyword, max_results=10)
            tweets = results.data if results.data else []

            for tweet in tweets:
                if tweet.text.startswith("RT") or tweet.author_id == client.get_me().data.id:
                    continue

                promo_reply = random.random() < random.uniform(0.1, 0.3)
                reply_text = generate_reply(tweet.text, promo=promo_reply)

                client.create_tweet(in_reply_to_tweet_id=tweet.id, text=reply_text)
                print(f"Replied to: {tweet.id} | Promo: {promo_reply}")

                time.sleep(random.randint(20, 60))  # Avoid spam rate limits

        except Exception as e:
            print(f"Error while processing keyword '{keyword}': {e}")
            continue

if __name__ == "__main__":
    while True:
        search_and_reply()
        time.sleep(1800)  # Run every 30 minutes
