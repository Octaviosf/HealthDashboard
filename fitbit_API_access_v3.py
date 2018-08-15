import requests
import base64

"""
# copy auth_url to browser for authorization of this computer
auth_url = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=22CXZR&redirect_uri=https%3A%2F%2Flocalhost%2Fcallback&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight'
"""

def fitbit_request(url, access_token):

    header = {'Authorization': 'Bearer ' + str(access_token)}

    request = requests.get(url=url, headers=header)
    response = request.json()

    return response

# trade auth_code for tokens
client_id = '22CXZR'
client_secret = 'e2f4370b9bce7138faad9093accfd245'
# code returned after visiting auth_url
auth_code = '3b929495e80b104da4d7f03e7680d57a3c088a3e'

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

# make sleep request
sleep_url = 'https://api.fitbit.com/1.2/user/-/sleep/date/2018-08-09.json'
sleep_stats = fitbit_request(sleep_url, access_token)
print(sleep_stats)

### TO DO ###

# create fnc for trading auth_code for tokens which returns True if tokens exist (prevents need to visit auth_url repeatedly)

# create fnc to acquire refresh tokens

# create a fitbit class with methods that make specific GET requests

# arrange sleep data into csv file




