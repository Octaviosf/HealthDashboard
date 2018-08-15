import requests
import base64

"""
# copy auth_url to browser for authorization of this computer
auth_url = 
https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=22CXZR&redirect_uri=https%3A%2F%2Flocalhost%2Fcallback&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight

"""

class Fitbit(object):

    def __init__(self, client_id, client_secret, auth_code):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = auth_code
        self.token_url = 'https://api.fitbit.com/oauth2/token'

        data = {'code': auth_code,
            'redirect_uri': 'https://localhost/callback',
            'client_id': client_id,
            'grant_type': 'authorization_code'}

        b64_str = base64.b64encode((client_id + ":" + client_secret).encode("utf-8"))
        self.token_headers = {'Authorization': 'Basic ' + b64_str.decode(),
                   'Content-Type': 'application/x-www-form-urlencoded'}

        request = requests.post(url=self.token_url, data=data, headers=self.token_headers)
        response = request.json()

        try:
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            self.tokens_recieved = True
        except Exception as e:
            self.tokens_recieved = False
            print('Unable to exchange authorization for tokens:', str(e))

    def refresh_tokens(self):

        refresh_data = {'grant_type': 'refresh_token',
                        'refresh_token': str(self.refresh_token)}

        request = requests.post(self.token_url, data=refresh_data, headers=self.token_headers)
        response = request.json()

        try:
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            self.tokens_recieved = True
        except Exception as e:
            self.tokens_recieved = False
            print('Unable to exchange authorization for tokens:', str(e))

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
                self.get_request(self, url)

        return response

client_id = '22CXZR'
client_secret = 'e2f4370b9bce7138faad9093accfd245'
# code returned after visiting auth_url
auth_code = ''

# make sleep request
sleep_url = 'https://api.fitbit.com/1.2/user/-/sleep/date/2018-08-09.json'

fitbit = Fitbit(client_id, client_secret, auth_code)

sleep_stats = fitbit.get_request(url=sleep_url)
print(sleep_stats)


"""
token_url = 'https://api.fitbit.com/oauth2/token'

data = {'code': auth_code,
            'redirect_uri': 'https://localhost/callback',
            'client_id': client_id,
            'grant_type': 'authorization_code'}

b64_str = base64.b64encode((client_id + ":" + client_secret).encode("utf-8"))
headers = {'Authorization': 'Basic ' + b64_str.decode(),
           'Content-Type': 'application/x-www-form-urlencoded'}

request = requests.post(url=token_url, data=data, headers=headers)
response = request.json()

access_token = response['access_token']
refresh_token = response['refresh_token']
"""


### TO DO ###

# create fnc for trading auth_code for tokens which returns True if tokens exist (prevents need to visit auth_url repeatedly)

# create fnc to acquire refresh tokens

# create a fitbit class with methods that make specific GET requests

# arrange sleep data into csv file




