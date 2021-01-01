import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

def makePlot(data, title, xlabel, ylabel):
    """Function to create plots for the COVID-19 data

    Parameters
    ----------
    data : array, first column contains the dates, second column contains the data
    title : str
    xlabel : str
    ylabel : str
    """
    
    # Create Figure
    fig, ax = plt.subplots()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)

    # Convert dates
    date = [int(d[5:7])-1+int(d[-2:])/32 for d in data[:,0]]
    ax.set_xlim(1, 12)

    # Plot
    ax.plot(date, data[:,1])
    plt.show()


def rateOfChange(data):
    """Function to create plots for the COVID-19 data

    Parameters
    ----------
    data : array, first column contains the dates, second column contains the data

    Output
    ------
    velocity : array, N-1 entries
    acceleration : array, N-2 entries
    """

    # Get velocity
    vel = np.array([(data[idx,0],data[idx+1,1]-value) 
        for idx,value in enumerate(data[:-1,1])], dtype=object)

    # Get acceleration
    acc = np.array([(data[idx,0],vel[idx+1,1]-value) 
        for idx,value in enumerate(vel[:-1,1])], dtype=object)

    return vel, acc


def sevenDayAverage(data):
    """Smooth using the seven day average"""
    smooth = data.copy()
    for idx in range(len(data)):
        try:
            smooth[idx,1] = np.mean(data[idx-3:idx+3,1])
        except ZeroDivisionError:
            smooth[idx,1] = np.nan
        
    return smooth


if __name__=="__main__":

    # Read COVID Data
    data = pd.read_csv('data/owid-covid-data.csv', header=0)

    # Filter data for Germany
    data_ger = data.loc[data['location'] == 'Germany']

    # Convert to matrix
    new_cases_smoothed = data_ger[['date','new_cases_smoothed']].values

    # Plot
    # makePlot(new_cases_smoothed, 'Smoothed Daily Cases Germany', 'Date [Months]', 'Daily Cases')

    # Get Rates of Change
    vel_cases, acc_cases = rateOfChange(new_cases_smoothed)

    # Plot
    # makePlot(vel_cases, 'Rate of Change Daily Cases Germany', 'Date [Months]', 'Rate of Change')

    # Smooth
    vel_cases_smoothed = sevenDayAverage(vel_cases)
    acc_cases_smoothed = sevenDayAverage(acc_cases)

    # Plot
    # makePlot(vel_cases_smoothed, 'Velocity of Daily Cases Germany', 'Date [Months]', 'Rate of Change')

    # Get critical dates
    MIN_DAILY_CASES = 2000
    MIN_DAILY_DEATHS = 50
    MIN_VELOCITY = 135
    MIN_ACCELERATION = 25

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

    """pause"""

