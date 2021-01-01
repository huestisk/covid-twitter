import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from pymongo import MongoClient

# Own functions
from analyze_covid import rateOfChange, sevenDayAverage, makePlot
from analyze_tweets import covidHashtags


def compareData(critical_dates, covid_tweet_dates, title, xlabel, ylabel):
    """Function to create plots for the COVID-19 data

    Parameters
    ----------
    data : array, first column contains the dates, second column contains the data
    title : str
    xlabel : str
    ylabel : str
    """
    # Make copies
    critical_dates_cp = critical_dates.copy()
    covid_tweet_dates_cp = covid_tweet_dates.copy()

    # Convert
    critical_dates_cp = [int(d[5:7])-1+int(d[-2:])/32 for d in critical_dates_cp]
    covid_tweet_dates_cp[:,0] = [int(d[5:7])-1+int(d[-2:])/32 for d in covid_tweet_dates_cp[:,0]]

    # Create Matrix with all Dates
    data = np.array((np.arange(1,12,1/32), np.newaxis, np.newaxis), dtype=object)

    # Add counts to Matrix
    data[1] = np.zeros(data[0].shape)
    for d, cnt in covid_tweet_dates_cp:
        data[1][data[0]==d] = cnt

    # Add critical dates to Matrix
    data[2] = [d in critical_dates_cp for d in data[0]]
    assert(np.sum(data[2])==len(critical_dates_cp))
    
    # Create Figure
    fig, ax = plt.subplots()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlim(1, 12)
    ax.grid(True)

    # Plot
    ax.plot(data[0], data[1], label="Frequency of Tweets")
    background = np.max(data[1])*np.ones(data[1].shape)
    ax.bar(data[0][data[2]], background[data[2]], color='red', width =1/32, label="Critical Dates")
    plt.legend(loc='best')
    plt.show()


# Connect to mongoDB
MONGO_DB_NAME = None
MONGO_PASSWORD = None

with open('mongodb.txt') as keys:
    MONGO_DB_NAME = keys.readline().replace('\n', '')
    MONGO_PASSWORD = keys.readline().replace('\n', '')

# Hashtags
HASHTAGS = ['corona','coronavirus','coronakrise','covid','covid19']


"""COVID Analysis"""
# Read COVID Data
data = pd.read_csv('data/owid-covid-data.csv', header=0)

# Filter data for Germany
data_ger = data.loc[data['location'] == 'Germany']

# Convert to matrix
new_cases_smoothed = data_ger[['date','new_cases_smoothed']].values

# Get Rates of Change
vel_cases, acc_cases = rateOfChange(new_cases_smoothed)

# Smooth
vel_cases_smoothed = sevenDayAverage(vel_cases)
acc_cases_smoothed = sevenDayAverage(acc_cases)

# Get critical dates
MIN_DAILY_CASES = 1800
MIN_DAILY_DEATHS = 50
MIN_VELOCITY = 125
MIN_ACCELERATION = 15

# Get days with high values
mask = (data_ger['new_cases_smoothed'] > MIN_DAILY_CASES) | \
    (data_ger['new_deaths_smoothed'] > MIN_DAILY_DEATHS)

high_dates = data_ger['date'].loc[mask].values

# Get days with high rates
rate_mask = (vel_cases_smoothed[:,1] > MIN_VELOCITY)[:-1] & \
    (acc_cases_smoothed[:,1] > MIN_ACCELERATION)

rate_dates = acc_cases_smoothed[rate_mask,0]

# Find matching dates
crit_dates_idx = [date in rate_dates for date in high_dates]
critical_dates = high_dates[crit_dates_idx]


"""Tweet Analysis"""
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

# makePlot(covid_tweet_dates, 'Covid Tweet Dates', 'Date [Months]', 'Number of Tweets')

compareData(critical_dates, covid_tweet_dates, 'title', 'xlabel', 'ylabel')