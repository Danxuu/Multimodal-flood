import tweepy
import pandas as pd
import simplejson
import time
import datetime

# This file obtains text, date and language for tweets in the labelled data
# and place the hydrated data in data/labeled_data_hydrated.csv.
#

# Twitter configuration
from config import (
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN
)

# authorization of consumer key and consumer secret 
#auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)  
# set access to user's access key and access secret  
#auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)   
# calling the api  
#api = tweepy.API(auth)

# create twitter instance
cleint=tweepy.Client(TWITTER_BEARER_TOKEN,TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)


def chunker(iterable, size):
    for pos in range(0, len(iterable), size):
        yield iterable[pos:pos + size]

# get text, date and language for tweets in the labelled data
def lookup(tweet_ids):
    texts, dates, languages = [], [], []
    for tweet_ids_chunk in chunker(tweet_ids, 100):
        #print(tweet_ids_chunk)
        sleep = 1
        while True:
            try:
                res = cleint.get_tweets(
                    ids=",".join([str(ID) for ID in tweet_ids_chunk]),
                    tweet_fields=["text","lang","created_at"]) 
                tweets = res.data
                break
            except (
                print("ConnectionError")
            ):
                sleep *= 2
            except simplejson.errors.JSONDecodeError:
                sleep *= 2
            sleep = min(sleep, 5 * 60)
            print(f'Connection error: sleeping for {sleep} seconds')
            time.sleep(sleep)
        tweets = {
            int(tweet['id']): tweet for tweet in tweets
        }
        for ID in tweet_ids_chunk:
            if ID in tweets:
                date = tweets[ID]['created_at']
                text = tweets[ID]['text']
                language = tweets[ID]['lang']
                if language == 'in':
                    language = 'id'
            else:
                date = 'NaN'
                text = 'NaN'
                language = 'NaN'
            texts.append(text)
            dates.append(date)
            languages.append(language)
    return texts, dates, languages


if __name__ == "__main__":
    df = pd.read_csv('data/labeled_data.csv')
    texts, dates, languages = lookup(df['ID'])
    df['text'] = texts
    df['date'] = dates
    df['language'] = languages

    df.to_csv('data/labeled_data_hydrated.csv')