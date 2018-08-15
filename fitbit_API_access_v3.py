import requests
import base64

"""
# copy auth_url to browser for authorization of this computer
auth_url = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=22CXZR&redirect_uri=https%3A%2F%2Flocalhost%2Fcallback&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight'
"""

client_id = '22CXZR'
client_secret = 'e2f4370b9bce7138faad9093accfd245'

# code returned after going to auth_url ('#_=_' may need to be excluded)
auth_code = 'c5ae8b69a1d66736a174a83db4a053a9653b533b'


token_url = 'https://api.fitbit.com/oauth2/token'

data = {'code': auth_code,
            'redirect_uri': 'https://localhost/callback',
            'client_id': client_id,
            'grant_type': 'authorization_code'}

b64_str = base64.b64encode((client_id + ":" + client_secret).encode("utf-8"))
headers = {'Authorization': 'Basic ' + b64_str.decode(),
           'Content-Type': 'application/x-www-form-urlencoded'}

req = requests.post(url=token_url, data=data, headers=headers)

print(req.json())


