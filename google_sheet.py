from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from googleapiclient import discovery
import pandas as pd


class GoogleSheet(object):
    def __init__(self, spreadsheet_id, sheet_range):
        """
        request spreadsheet object using Google Sheet API
        :param spreadsheet_id: string of id located after '/d/' in url 'https://docs.google.com/spreadsheets/d/'
        :param sheet_range: string specifying Google sheet range in A1 notation
        """

        # init params
        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_range
        self.scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        self.value_render_option = 'FORMATTED_VALUE'
        self.date_time_render_option = 'FORMATTED_STRING'

        # acquire tokens from existing file
        self.store = oauth_file.Storage('google_sheet_token.json')
        self.tokens = self.store.get()

        # acquire new tokens if nonexistent or invalid
        if not self.tokens or self.tokens.invalid:
            self.flow = client.flow_from_clientsecrets('google_sheet_credentials.json', self.scopes)
            self.tokens = tools.run_flow(self.flow, self.store)

        # build http address for data requests
        self.service = discovery.build('sheets', 'v4', http=self.tokens.authorize(Http()))

        # prepare request
        self.request = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=self.sheet_range,
            valueRenderOption=self.value_render_option,
            dateTimeRenderOption=self.date_time_render_option)

        # capture data from request
        self.sheet_obj = self.request.execute()

    def sheet2df(self, col_labels, index_label, index_type=str):
        """
        create and format dataFrame using sheet object
        :param col_labels: list of strings of labels used to create dataFrame
        :param index_label: string of dataFrame index
        :param index_type: string of dataFrame index type
        :return: dataFrame formatted for general purposes
        """

        # capture values from sheet_obj
        rows = self.sheet_obj['values']
        labels = rows[0]
        data = rows[1:]

        # create and format df
        df = pd.DataFrame.from_records(data=data, columns=labels)
        df = df[col_labels]
        df[index_label] = df[index_label].astype(index_type)
        df = df.set_index(index_label)

        return df
