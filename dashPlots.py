from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from pprint import pprint
import pandas as pd
from googleapiclient import discovery

def access_sheet(spreadsheet_id, range_):
    """
    :param spreadsheet_id: spreadsheet id found between d/ and /edit in google sheets url
    :param range: range of cells to access (A1 format)
    :return: object detailing
    """
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = discovery.build('sheets', 'v4',http=creds.authorize(Http()))

    value_render_option = 'FORMATTED_VALUE'
    date_time_render_option = 'SERIAL_NUMBER'

    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option,
        dateTimeRenderOption=date_time_render_option)
    response = request.execute()

    return response


spreadsheet_id = '10pFtYAvmRedAWNU1vB-JDZRGKiRD4EZDH6zGzkghpZ0'
range_ = 'Sheet1'

response = access_sheet(spreadsheet_id, range_)
rows = response['values']
labels = rows[0]
data = rows[1:]
df = pd.DataFrame.from_records(data, columns=labels)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    pprint(df)

#create new_df using only lb measurements

#plot new_df using matplotlib

#embed plot into tkinter gui

#show gui