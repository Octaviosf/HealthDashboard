import fitbit
import gather_keys_oauth2.py as Oauth2
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

