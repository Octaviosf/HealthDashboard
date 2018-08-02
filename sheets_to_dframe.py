from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from pprint import pprint
from googleapiclient import discovery

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
store = oauth_file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = discovery.build('sheets', 'v4',http=creds.authorize(Http()))

spreadsheet_id = '10pFtYAvmRedAWNU1vB-JDZRGKiRD4EZDH6zGzkghpZ0'
range_ = 'Sheet1'
value_render_option = 'FORMATTED_VALUE'
date_time_render_option = 'SERIAL_NUMBER'

request = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option,
    dateTimeRenderOption=date_time_render_option)
response = request.execute()

pprint(response)
