import requests
import base64
import os

class Fitbit(object):

    def __init__(self, client_id, client_secret, token_file_path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = 'https://api.fitbit.com/oauth2/token'

        b64_str = base64.b64encode((client_id + ":" + client_secret).encode("utf-8"))
        self.token_headers = {'Authorization': 'Basic ' + b64_str.decode(),
                              'Content-Type': 'application/x-www-form-urlencoded'}
        self.token_file_path = token_file_path

    def token_request(self, auth_code):

        self.auth_code = auth_code
        self.auth_data = {'code': self.auth_code,
                          'redirect_uri': 'https://localhost/callback',
                          'client_id': self.client_id,
                          'grant_type': 'authorization_code'}

        request = requests.post(url=self.token_url, data=self.auth_data, headers=self.token_headers)
        response = request.json()

        try:
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            self.tokens_recieved = True

            with open(self.token_file_path, 'w+') as token_file:
                token_file.write(str(self.refresh_token)+'\n')
                token_file.write(str(self.access_token))

        except Exception as e:
            self.tokens_recieved = False
            print('\nUnable to exchange authorization for tokens:', str(e))
            print('Current file path:', os.path.abspath(os.curdir))

    def refresh_tokens(self):

        with open(self.token_file_path, 'r') as token_file:
            self.refresh_token = token_file.readline()[:-1]

        refresh_data = {'grant_type': 'refresh_token',
                        'refresh_token': str(self.refresh_token)}

        request = requests.post(self.token_url, data=refresh_data, headers=self.token_headers)
        response = request.json()

        try:
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            self.tokens_recieved = True

            with open(self.token_file_path, 'w') as token_file:
                token_file.write(str(self.refresh_token)+'\n')
                token_file.write(str(self.access_token))

        except Exception as e:
            self.tokens_recieved = False
            print('\nUnable to exchange authorization for tokens:', str(e))

        return (self.access_token, self.refresh_token)

    def get_request(self, url):

        header = {'Authorization': 'Bearer ' + str(self.access_token)}

        request = requests.get(url=url, headers=header)
        response = request.json()
        try:
            error = response['errors'][0]['errorType']
            if error == 'expired_token':
                # may not work due to syntax of self.refresh_tokens()
                (self.access_token, self.refresh_token) = self.refresh_tokens()
                self.get_request(url)
        except KeyError:
            return response

### TO DO ###
"""
1. Create file directory: ~/Documents/IoTHealth

2. Assign 'token_file_path' below to absolute file path through above directory 
    (i.e. /home/sosa/Documents/IoTHealth/fitbit_tokens.txt)

3. visit 'auth_url' and copy-paste 'auth_code' from end of callback url to assignment below
    auth_url = https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=22CXZR&redirect_uri=https%3A%2F%2Flocalhost%2Fcallback&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight
"""

# code returned after visiting auth_url
auth_code = '6cc12427bae4b0bf4adf6102eb827e5713d4f578'

client_id = '22CXZR'
client_secret = 'e2f4370b9bce7138faad9093accfd245'
token_file_path = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
# make sleep request
sleep_url = 'https://api.fitbit.com/1.2/user/-/sleep/date/2018-08-09.json'

fitbit = Fitbit(client_id, client_secret, token_file_path)

if os.path.isfile(fitbit.token_file_path) and os.access(fitbit.token_file_path, os.R_OK):
    print('fitbit_tokens.txt exists')
else:
    print('"fitbit_tokens.txt" does not exist')
    print('initializing "fitbit_tokens.txt" ...')
    fitbit.token_request(auth_code)
    print('"fitbit_tokens.txt" initialized')

sleep_stats = fitbit.get_request(url=sleep_url)
print(sleep_stats)


### TO DO ###

# create fnc for trading auth_code for tokens which returns True if tokens exist (prevents need to visit auth_url repeatedly)

# create fnc to acquire refresh tokens

# create a fitbit class with methods that make specific GET requests

# arrange sleep data into csv file




