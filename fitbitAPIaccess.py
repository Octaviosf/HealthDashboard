import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
import datetime

CLIENT_ID = '22CXZR'
CLIENT_SECRET = 'e2f4370b9bce7138faad9093accfd245'

server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True,
                             access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

yesterday = datetime.datetime.now()

#fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=yesterday, detail_level='1min')
#print(fit_statsHR)

sleep_stats = auth2_client.get_sleep(date=yesterday)

print(sleep_stats)
#yester_sleep_level = sleep_stats['levels']
#print(yester_sleep_level)
