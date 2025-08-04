
import os
import tweepy
import time
import random
from openai import OpenAI

# Twitter API credentials from environment variables
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Authenticate with Twitter
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Target keywords
keywords = ["need a plumber", "recommend a roofer", "kitchen fitter quote", "electrician in my area"]

# Helper function to generate reply
def generate_reply(tweet_text, promo=False):
    system_prompt = (
        "You are a helpful UK homeowner named Jay who offers advice to people needing trades. "
        "Avoid promotional tone unless necessary. Never use em dashes — use natural punctuation."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": tweet_text}
    ]

    if promo:
        messages.append({"role": "system", "content": "Include this link naturally: https://www.myjobquote.co.uk/quote?click=UFUZATT7BXJ"})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    reply = response.choices[0].message.content.replace("—", "-")
    return reply

# Main loop
def search_and_reply():
    for keyword in keywords:
        tweets = api.search_tweets(q=keyword, lang="en", count=5, result_type="recent")
        for tweet in tweets:
            if tweet.user.screen_name != "JayMillerDIY":
                promo_reply = random.random() < 0.2  # 20% chance of promo
                reply_text = generate_reply(tweet.text, promo=promo_reply)
                try:
                    api.update_status(
                        status=f"@{tweet.user.screen_name} {reply_text}",
                        in_reply_to_status_id=tweet.id
                    )
                    print(f"Replied to @{tweet.user.screen_name}: {reply_text}")
                except Exception as e:
                    print(f"Failed to reply to @{tweet.user.screen_name}: {e}")
                time.sleep(10)

if __name__ == "__main__":
    while True:
        search_and_reply()
        time.sleep(3600)
