import requests
import base64
import os


class Fitbit(object):
    """
    Interact with Fitbit API:
        -request and refresh tokens
        -request data
    """
    def __init__(self, client_id, client_secret, token_file_path):
        """
        initialize data for Fitbit API requests

        :param client_id: given after Fitbit app is made
        :param client_secret: given after Fitbit app is made
        :param token_file_path: absolute file path from /home to /IoTHealth
        """

        # assignments
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = 'https://API.fitbit.com/oauth2/token'
        self.token_file_path = token_file_path
        self.auth_code = None

        # create data for tokens request
        self.auth_data = {'code': self.auth_code,
                          'redirect_uri': 'https://localhost/callback',
                          'client_id': self.client_id,
                          'grant_type': 'authorization_code'}

        # create headers for tokens request
        b64_str = base64.b64encode((client_id + ":" + client_secret).encode("utf-8"))
        self.token_headers = {'Authorization': 'Basic ' + b64_str.decode(),
                              'Content-Type': 'application/x-www-form-urlencoded'}

        # test fitbit_tokens.txt existence, if not create file
        while True:
            # test existence of file and readability
            if os.path.isfile(token_file_path) and os.access(token_file_path, os.R_OK):
                # capture tokens from file
                with open(token_file_path, 'r') as token_file:
                    self.refresh_token = token_file.readline()[:-1]
                    self.access_token = token_file.readline()[:-1]
                break
            else:
                # prompt for auth_code
                print('\n"fitbit_tokens.txt" does not exist')
                self.auth_code = str(input("Enter authorization code: "))
                try:
                    # request tokens and create file to capture them
                    self.token_request()
                    print('\n"fitbit_tokens.txt" initialized')
                except Exception as e:
                    print('\nFrom __init__():', str(e))
                    print('Try again')

    def token_request(self):
        """
        request tokens and create file to capture them
        """

        # request tokens and capture response
        request = requests.post(url=self.token_url, data=self.auth_data, headers=self.token_headers)
        response = request.json()

        try:
            # capture tokens
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']

            # create "fitbit_tokens.txt"
            with open(self.token_file_path, 'w+') as token_file:
                token_file.write(str(self.refresh_token)+'\n')
                token_file.write(str(self.access_token))
        except Exception as e:
            print('\nFrom token_request():', str(e))
            print('Current file path:', os.path.abspath(os.curdir))

    def refresh_tokens(self):
        """
        refresh the tokens

        :return: tuple capturing access and refresh tokens, respectively
        """

        # read refresh token from "fitbit_tokens.txt"
        with open(self.token_file_path, 'r') as token_file:
            self.refresh_token = token_file.readline()[:-1]

        # create data for refresh token request
        refresh_data = {'grant_type': 'refresh_token',
                        'refresh_token': str(self.refresh_token)}

        # request refresh token and capture response
        request = requests.post(self.token_url, data=refresh_data, headers=self.token_headers)
        response = request.json()

        try:
            # capture tokens
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']

            # overwrite file with new tokens
            with open(self.token_file_path, 'w') as token_file:
                token_file.write(str(self.refresh_token)+'\n')
                token_file.write(str(self.access_token))
        except Exception as e:
            print('\nFrom refresh_tokens():', str(e))

        return self.access_token, self.refresh_token

    def get_request(self, url):
        """
        request data from Fitbit API

        :param url: url request for data - formatted according to API
        :return: response from data request
        """

        # create headers for data request
        header = {'Authorization': 'Bearer ' + str(self.access_token)}

        # request data and capture response
        request = requests.get(url=url, headers=header)
        response = request.json()

        # handle expired token error
        try:
            error = response['errors'][0]['errorType']
            if error == 'invalid_token':
                # refresh tokens
                (self.access_token, self.refresh_token) = self.refresh_tokens()
                # request data using new tokens and capture response
                response = self.get_request(url)
        except KeyError:
            pass

        return response


"""
User to-do 

1. Create file directory: ~/Documents/IoTHealth

2. Assign 'token_file_path' below to absolute file path through above directory 
    (i.e. token_file_path = "/home/sosa/Documents/IoTHealth/fitbit_tokens.txt")

3. Visit 'auth_url' and input 'auth_code' from end of callback url to console prompt 

    auth_url = https://www.fitbit.com/oauth2/authorize?response_type=code&
               client_id=22CXZR&redirect_uri=https%3A%2F%2Flocalhost%2Fcallback&
               scope=activity%20nutrition%20heartrate%20location%20nutrition%20
               profile%20settings%20sleep%20social%20weight
"""

# assignments
ID = '22CXZR'
secret = 'e2f4370b9bce7138faad9093accfd245'
file_path = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
sleep_url = 'https://API.fitbit.com/1.2/user/-/sleep/date/2018-08-09.json'

# create instance for Fitbit API requests
fitbit = Fitbit(client_id=ID, client_secret=secret, token_file_path=file_path)

# request sleep data, capture response, and print response
sleep_data = fitbit.get_request(url=sleep_url)
print('\n'+str(sleep_data))

"""
Dev to-do

1. Create a fitbit class with methods that make specific GET requests

2. Arrange sleep data into csv file
"""
