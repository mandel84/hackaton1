import tweepy
import psycopg2
from psycopg2 import sql
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADo%2BugEAAAAAyC9lM5yAv9wL8B4XG6wgY7cC2%2Bc%3DwTESCAlTVqRPN57gvaMeOQZnIXMmgS140arLMix9co5r2a1LBs'

DB_NAME = 'antisemitism_db'
DB_USER = 'postgres'
DB_PASSWORD = 2384
DB_HOST = 'localhost'
DB_PORT = 5432


def fetch_tweets(keyword,max_results=10):
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    query =f'{keyword} lang:en'
    response = client.search_recent_tweets(query=query,max_results=max_results,tweet_fields=['id','text','author_id','created_at'])
    return response.data

def store_tweets(tweets):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    for tweet in tweets:
        cur.execute(
            sql.SQL("INSERT INTO antisemitic_tweets (tweet_id, tweet_text, user_name, created_at) VALUES (%s, %s, %s, %s)"),
            [tweet.id, tweet.text, tweet.author_id, tweet.created_at]
        )

    conn.commit()
    cur.close()
    conn.close()

def analyze_tweets():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute("SELECT tweet_text FROM antisemitic_tweets")
    tweets = cur.fetchall()

    all_words = []
    for tweet in tweets:
        words = word_tokenize(tweet[0])
        all_words.extend(words)

    word_counts = Counter(all_words)
    print("Most common words:", word_counts.most_common(10))

    cur.close()
    conn.close()

def main():
    keyword = 'antisemitism'
    tweets = fetch_tweets(keyword, max_results=100)
    if tweets:
        store_tweets(tweets)
        print(f"Stored {len(tweets)} tweets in the database.")
        analyze_tweets()
    else:
        print("No tweets found.")

if __name__ == "__main__":
    main()    
    
