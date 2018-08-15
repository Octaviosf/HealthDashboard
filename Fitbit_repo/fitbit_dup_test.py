import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
from datetime import datetime as datetime
from datetime import timedelta

Client_ID = '22CXZR'
Client_Secret = 'e2f4370b9bce7138faad9093accfd245'

server = Oauth2.OAuth2Server(Client_ID, Client_Secret)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

auth2_client = fitbit.Fitbit(Client_ID, Client_Secret, oauth2=True,
                             access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

ninth = datetime.strptime("2018-08-09", "%Y-%m-%d")

print('day:', ninth.day)
print('month:', ninth.month)

S_stats = auth2_client.get_sleep(ninth)
S_stages = S_stats['summary']['stages']
print(S_stats)
print(S_stages)

# heart rate

ninth = ninth.strftime("%Y-%m-%d")
print(type(ninth), ninth)
HR_stats = auth2_client.heart(date=ninth, data=None)
print(HR_stats)



