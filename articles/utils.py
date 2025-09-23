import tweepy
from django.conf import settings

def post_to_twitter(article):
    try:
        auth = tweepy.OAuth1UserHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_SECRET
        )
        api = tweepy.API(auth)

        tweet_text = f"📰 New article: {article.title} {article.get_absolute_url()}"
        api.update_status(status=tweet_text)
        print("Tweet posted successfully!")
    except Exception as e:
        print("Twitter post failed:", e)
