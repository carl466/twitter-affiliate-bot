import os
import tweepy
import openai
import random
import time

# Authenticate with Twitter
auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# Authenticate with OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Expanded list of keywords
all_keywords = [
    "looking for a plumber", "need an electrician", "recommend a roofer",
    "builder for extension", "find gardener", "hire handyman", "any good tilers",
    "window cleaner in", "fence repair needed", "local tradesperson needed",
    "need a decorator", "recommend a tradesperson", "cheap handyman near me",
    "recommend a builder", "need garden help", "kitchen fitter recommendation",
    "bathroom installer", "urgent roofer needed", "local electrician wanted",
    "fence panel repair", "reliable joiner", "need someone to paint", "door won’t close",
    "recommend someone for tiling", "garage conversion help", "new driveway quote",
    "electrician for EV charger", "boiler service near me", "window repair person",
    "loft boarding service", "install laminate flooring", "shed base installer",
    "dripping tap repair", "mould on walls help", "decking installation help"
]

# Select a random subset to use this run
keywords_to_use = random.sample(all_keywords, 5)

# Promotional message to append to replies
promo_reply = "\n\nIf you're stuck, try this — it finds and compares local tradespeople quickly: https://www.localjobquotes.co.uk"

def generate_reply(tweet_text, promo):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and friendly assistant replying to someone looking for a tradesperson. Keep your tone casual, short, and don't use em dashes."},
                {"role": "user", "content": f"Reply to this tweet in a friendly, helpful tone:\n\n'{tweet_text}'"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        reply = response.choices[0].message.content.strip()
        return reply + " " + promo
    except Exception as e:
        print(f"Error generating reply: {e}")
        return None

def search_and_reply():
    for keyword in keywords_to_use:
        try:
            tweets = api.search_tweets(q=keyword, lang="en", count=5, result_type="recent")
            for tweet in tweets:
                if not tweet.user.following:
                    reply_text = generate_reply(tweet.text, promo=promo_reply)
                    if reply_text:
                        print(f"Replying to @{tweet.user.screen_name}: {reply_text}")
                        api.update_status(
                            status=f"@{tweet.user.screen_name} {reply_text}",
                            in_reply_to_status_id=tweet.id
                        )
                        time.sleep(5)
        except Exception as e:
            print(f"Error while processing keyword '{keyword}': {e}")
            continue

# Run bot
if __name__ == "__main__":
    search_and_reply()
