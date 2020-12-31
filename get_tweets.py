from __future__ import print_function
import tweepy
import json
from pymongo import MongoClient

# Hashtags
WORDS = ['#covid','#coronavirus','#covid19','#corona']

# Users
USERS = ['sebastiankurz','martinschulz','SWagenknecht','GregorGysi',
    'JunckerEU','MartinSonneborn','c_lindner','nicosemsrott']

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
    """This is a class provided by tweepy to access the Twitter Streaming API."""

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        # Connect to mongoDB and stores the tweet
        try:
            client = MongoClient('mongodb+srv://kevinhuestis:' + 
                str(MONGO_PASSWORD) + '@cluster0.ahwbn.mongodb.net/' + 
                str(MONGO_DB_NAME) + '?retryWrites=true&w=majority')
            
            # Use test database
            db = client.test
    
            # Decode the JSON from Twitter
            datajson = json.loads(data)
            
            # Grab the 'created_at' data from the Tweet to use for display
            created_at = datajson['created_at']
            username = datajson['user']['screen_name']

            # Print out a message to the screen that we have collected a tweet
            print("Tweet collected at " + str(created_at) + " from user @" + username)
            
            # Insert the data into the mongoDB
            db.twitterSpain.insert_one(datajson)
			
			# How many tweets were saved
            print(db.twitterSpain.count_documents({}))

        except Exception as e:
           print(e)



class SearchTwitter():
    """Search for Tweets using the api"""

    def __init__(self, api):
        self.api = api
        self.START_DATE = 2020

        # Connect to mongoDB and stores the tweet
        try:
            self.client = MongoClient('mongodb+srv://kevinhuestis:' + 
                str(MONGO_PASSWORD) + '@cluster0.ahwbn.mongodb.net/' + 
                str(MONGO_DB_NAME) + '?retryWrites=true&w=majority')

            # Use test database
            self.db = self.client.test

        except Exception as e:
            print(e)

    def search_by_hashtag(self, words):
        """Search by Hashtag"""
        for data in api.search(q=words):
            try:      
                # Decode the Tweet
                datajson = json.loads(data)
                
                # Insert the data into the mongoDB
                self.db.userTweets.insert_one(datajson)

            except Exception as e:
                print(e)  

    
    def search_by_user(self, user):
        """ Search by User"""
        for status in self.limit_handled(tweepy.Cursor(api.user_timeline, id=user).items()):

            # Only search for tweets in 2020
            if status.created_at.year < self.START_DATE:
                break

            try:      
                # Decode the Tweet
                datadump = json.dumps(status._json)
                datajson = json.loads(datadump)
                
                # Insert the data into the mongoDB
                self.db.userTweets.insert_one(datajson)

            except Exception as e:
                print(e)     


    @classmethod
    def limit_handled(self, cursor):
        """Handles Twitter limit"""
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                time.sleep(15 * 60)
            except Exception as e:
                print(e)


if __name__ == "__main__":

    # Login
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    """Searching starts here"""
    searcher = SearchTwitter(api)

    for user in USERS:
        searcher.search_by_user(user)
        print("Finished collecting Tweets from user " + user)

    """Streamer starts here"""
    # listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
    # streamer = tweepy.Stream(auth=auth, listener=listener)
    
    # # Listen to the defined Hashtags
    # print("Tracking: " + str(WORDS))
    # streamer.filter(track=WORDS)


