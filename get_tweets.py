from __future__ import print_function
import tweepy
import json
from pymongo import MongoClient

# Hashtags
WORDS = ['#covid','#coronavirus']

# Twitter Access
CONSUMER_KEY = None
CONSUMER_SECRET = None
ACCESS_TOKEN = None
ACCESS_TOKEN_SECRET = None

with open('keys.txt') as keys:
    CONSUMER_KEY = keys.readline().replace('\n', '')
    CONSUMER_SECRET = keys.readline().replace('\n', '')
    ACCESS_TOKEN = keys.readline().replace('\n', '')
    ACCESS_TOKEN_SECRET = keys.readline().replace('\n', '')

# MongoDB 
MONGO_DB_NAME = None
MONGO_PASSWORD = None

with open('mongodb.txt') as keys:
    MONGO_DB_NAME = keys.readline().replace('\n', '')
    MONGO_PASSWORD = keys.readline().replace('\n', '')


class StreamListener(tweepy.StreamListener):    
    # This is a class provided by tweepy to access the Twitter Streaming API. 
    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        #This is the meat of the script...it connects to your mongoDB and stores the tweet
        try:
            client = MongoClient('mongodb+srv://kevinhuestis:' + 
                str(MONGO_PASSWORD) + '@cluster0.ahwbn.mongodb.net/' + 
                str(MONGO_DB_NAME) + '?retryWrites=true&w=majority')
            
            # Use test database. If it doesn't exist, it will be created.
            db = client.test
    
            # Decode the JSON from Twitter
            datajson = json.loads(data)
            
            # Grab the 'created_at' data from the Tweet to use for display
            created_at = datajson['created_at']
            username = datajson['user']['screen_name']

            # Print out a message to the screen that we have collected a tweet
            print("Tweet collected at " + str(created_at) + " from user @" + username)
            
            # Insert the data into the mongoDB into a collection called twitter_search
            # If twitter_search doesn't exist, it will be created.
            db.twitterSpain.insert_one(datajson)
			
			# How many tweets?
            print(db.twitterSpain.count_documents({}))

        except Exception as e:
           print(e)

class SearchTwitter(tweepy.Cursor):
    # This class uses tweepy.Cursor to search for hashtags
    pass


if __name__ == "__main__":

    # Login
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Search
    tweets = api.search(q=WORDS)
    print(tweets.num_tweets)
    # # Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    # listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
    # streamer = tweepy.Stream(auth=auth, listener=listener)
    
    # # Listen to the defined Hashtags
    # print("Tracking: " + str(WORDS))
    # streamer.filter(track=WORDS)


