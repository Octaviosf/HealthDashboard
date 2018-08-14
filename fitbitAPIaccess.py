import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
from datetime import datetime as datetime
from datetime import timedelta

"""
CLIENT_ID = '22CXZR'
CLIENT_SECRET = 'e2f4370b9bce7138faad9093accfd245'

server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True,
                             access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
"""
dates = []
start_day = datetime.strptime('2018-08-07', '%Y-%m-%d')

days_from_start = (datetime.now() - start_day).days

day = start_day

for d in range(days_from_start):
    dates.append(day)
    day += timedelta(days=1)

print(dates)

###

# initialize pandas dataframe and save as csv file
class fitbit_df(object):
    def __init__(self, Client_ID, Client_Secret):
        # request access and refresh tokens from Fitbit client
        server = Oauth2.OAuth2Server(Client_ID, Client_Secret)
        server.browser_authorize()

        self.Access_Token = str(server.fitbit.client.session.token['access_token'])
        self.Refresh_Token = str(server.fitbit.client.session.token['refresh_token'])

        self.auth2_client = fitbit.Fitbit(Client_ID, Client_Secret, oauth2=True,
                                     access_token=self.Access_Token, refresh_token=self.Refresh_Token)


        # init dates list for data request from Fitbit
        dates = []
        start_day = datetime.strptime('2018-08-07', '%Y-%m-%d')

        days_from_start = (datetime.now() - start_day).days

        day = start_day

        for d in range(days_from_start):
            dates.append(day)
            day += timedelta(days=1)

        # init S_data
        S_data = []

        for day in dates:
            S_stats = self.auth2_client.get_sleep(day)
            S_stages = S_stats['levels']
            S_efficiency = efficiency(S_stages)
            min_to_sleep = S_stats['minutessToFallAsleep']
            min_after_wake = S_stats['minutesAfterWakeup']
            # S_event_duration = S_stages['deep'] + 'light' + 'rem' + 'wake'
            S_data.append([day, S_efficiency, S_stages, min_to_sleep, min_after_wake])

        print(S_data)



# if csv file exists then request sleep logs from most recent entry in csv file onwards

# update csv file with new entries

# create pandas dataframe from updated csv file

# plot dataframe in GUI

###

#yesterday = datetime.datetime.now()

#fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=yesterday, detail_level='1min')
#print(fit_statsHR)

#sleep_stats = auth2_client.get_sleep(date=yesterday)

#print(sleep_stats)
#yester_sleep_level = sleep_stats['levels']
#print(yester_sleep_level)
