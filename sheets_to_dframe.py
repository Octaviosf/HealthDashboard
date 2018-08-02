from pprint import pprint
from googleapiclient import discovery

credentials = None

service = discovery.build.('sheets', 'v4', credentials=credentials)

spreadsheet_id = '10pFtYAvmRedAWNU1vB-JDZRGKiRD4EZDH6zGzkghpZ0'
range_ = 'Sheet1'
value_render_option = 'ValueRenderOption.FORMATTED_VALUE'
date_time_render_option = '[DateTimeRenderOption.SERIAL_NUMBER]'

request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
response = request.execute()

pprint(response)
