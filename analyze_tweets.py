from __future__ import division
from pymongo import MongoClient
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import operator

from analyze_covid import makePlot

# Connect to mongoDB
MONGO_DB_NAME = None
MONGO_PASSWORD = None

with open('mongodb.txt') as keys:
    MONGO_DB_NAME = keys.readline().replace('\n', '')
    MONGO_PASSWORD = keys.readline().replace('\n', '')

# Hashtags
HASHTAGS = ['corona','coronavirus','coronakrise','covid','covid19']


# Plot of Languages (autodetected by Twitter)
def plotLanguages(my_tweets):
    my_tweets.rewind() #Reset cursor
    langsList = []
    for t in my_tweets:
        langsList.append(t['lang'])
        D = Counter(langsList)

    # ----------- Bar Plot ------------------------
    plt.bar(range(len(D)), D.values(), align='center')
    plt.xticks(range(len(D)), D.keys())
    plt.title('Languages spoken in the tweets captured')
    plt.show()


# Plot how many of them are retweets, replies, quotations or original tweets
def plotTweetTypes(my_tweets):
    my_tweets.rewind() #Reset cursor
    retweets = replies = quotations = originals = 0
    for t in my_tweets:
        if t.get('retweeted_status') is not None:
            retweets=retweets+1
        elif t['is_quote_status'] is not False:
            quotations = quotations+1
        elif t.get('in_reply_to_status_id') is not None:
            replies = replies+1
        else:
            originals = originals+1

    # ----------- Pie Chart ------------------~------
    labels = 'Original Content', 'Retweets', 'Quotations', 'Replies'
    sizes = [originals, retweets, quotations, replies]
    frequencies = [x/numTweets for x in sizes]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0.1, 0, 0, 0) # explode 1st slice
    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Percentage of Tweets depending on how the content is generated')
    plt.show()


# Plot hashtags
def plotHashtags(my_tweets):
    my_tweets.rewind() #Reset cursor
    hashList = []
    for t in my_tweets:
        for e in t['entities']['hashtags']:
            h = e['text']
            hashList.append(h)
            
    D = Counter(hashList)
    subset = dict(D.most_common(25))
    sorted_subset = sorted(subset.items(), key=operator.itemgetter(1))

    # ----------- Horizontal Bar Plot ------------------------
    pos = range(len(sorted_subset))
    plt.barh(pos, [val[1] for val in sorted_subset], align = 'center', color =
    'yellowgreen')
    plt.yticks(pos, [val[0] for val in sorted_subset])
    plt.tight_layout()
    plt.title('Top 25 of hashtags captured')
    plt.show()


# Plot COVID hashtags
def covidHashtags(my_tweets):
    my_tweets.rewind() #Reset cursor
    hashList = []
    for t in my_tweets:
        for e in t['entities']['hashtags']:
            # Filter by hashtag
            if e['text'].lower() in HASHTAGS:
                # Convert date to YYYY-MM-DD
                tmp_Month = t['created_at'][4:7]
                tmp_DD = t['created_at'][8:10]
                tmp_YYYY = t['created_at'][-4:]
                # Convert month and append
                if tmp_Month=='Jan':
                    hashList.append(tmp_YYYY + "-01-" + tmp_DD)
                elif tmp_Month=='Feb':
                    hashList.append(tmp_YYYY + "-02-" + tmp_DD)
                elif tmp_Month=='Mar':
                    hashList.append(tmp_YYYY + "-03-" + tmp_DD)
                elif tmp_Month=='Apr':
                    hashList.append(tmp_YYYY + "-04-" + tmp_DD)
                elif tmp_Month=='May':
                    hashList.append(tmp_YYYY + "-05-" + tmp_DD)
                elif tmp_Month=='Jun':
                    hashList.append(tmp_YYYY + "-06-" + tmp_DD)
                elif tmp_Month=='Jul':
                    hashList.append(tmp_YYYY + "-07-" + tmp_DD)
                elif tmp_Month=='Aug':
                    hashList.append(tmp_YYYY + "-08-" + tmp_DD)
                elif tmp_Month=='Sep':
                    hashList.append(tmp_YYYY + "-09-" + tmp_DD)
                elif tmp_Month=='Oct':
                    hashList.append(tmp_YYYY + "-10-" + tmp_DD)
                elif tmp_Month=='Nov':
                    hashList.append(tmp_YYYY + "-11-" + tmp_DD)
                elif tmp_Month=='Dec':
                    hashList.append(tmp_YYYY + "-12-" + tmp_DD)
                else:
                    raise Exception("Invalid Month: " + str(tmp_Month))
                # So each tweet is only added once
                break
    
    # Convert to counts
    date_count = Counter(hashList)

    # Convert to array
    dictList = [np.array((key, value),dtype=object) for key, value in date_count.items()]
            
    return np.array(dictList)



if __name__ == "__main__":

    try:
        # Connect to client
        client = MongoClient('mongodb+srv://kevinhuestis:' + 
            str(MONGO_PASSWORD) + '@cluster0.ahwbn.mongodb.net/' + 
            str(MONGO_DB_NAME) + '?retryWrites=true&w=majority')
        # Use test database
        db = client.test
        # Collection
        col = db.userTweets
    except Exception as e:
        print(e)

    # Retrieve Tweets
    my_tweets = col.find({},{'lang':1, '_id':0, 'text':1, 'created_at':1,
        'entities.hashtags':1, 'in_reply_to_status_id':1, 'is_quote_status':1,
        'retweeted_status':1, 'user.screen_name':1})

    numTweets = col.count()

    # Plot Hashtags
    covid_tweet_dates = covidHashtags(my_tweets)

    makePlot(covid_tweet_dates, 'Covid Tweet Dates', 'Date [Months]', 'Number of Tweets')


