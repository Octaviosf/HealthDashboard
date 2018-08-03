from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt

def access_sheet(spreadsheet_id, range_):
    """
    :param spreadsheet_id: spreadsheet id found between d/ and /edit in google sheets url
    :param range: range of cells to access (A1 format)
    :return: object detailing
    """

    from httplib2 import Http
    from oauth2client import file as oauth_file, client, tools
    from googleapiclient import discovery

    # create service instance
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = discovery.build('sheets', 'v4',http=creds.authorize(Http()))

    # call to access sheet data
    value_render_option = 'FORMATTED_VALUE'
    date_time_render_option = 'FORMATTED_STRING'

    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option,
        dateTimeRenderOption=date_time_render_option)
    sheet_obj = request.execute()

    return sheet_obj

def sheet_to_df(sheet_obj):
    """
    :param sheet_obj: sheet object returned when requesting values of spreadsheet
    :return: dataframe with down-sampled data by day
    """
    # create df instance
    rows = sheet_obj['values']
    labels = rows[0]
    data = rows[1:]
    df = pd.DataFrame.from_records(data, columns=labels)

    # format df
    df = df[['date_time', 'weight_lb', 'lean_body_mass_lb', 'fat_mass_lb', 'body_fat_%']]
    df['date_time'] = df['date_time'].astype('datetime64[ns]')
    df = df.set_index('date_time')

    # down-sample data by day
    cols = df.columns.difference(['date_time'])
    df[cols] = df[cols].astype(float)
    df = df.resample('d').mean().dropna(how='all')

    return df

def format_plot(df):
    import matplotlib.dates as mdates

    df.plot(style='o')
    plt.grid()
    plt.legend(prop={'size': 20})

    plt.title('Body Composition', fontsize=30)
    plt.xlabel('Date', fontsize=24)

    xaxis_range = (df.index.tolist()[0], df.index.tolist()[-1])
    plt.xlim(xaxis_range)
    plt.tick_params(axis='x',which='minor', labelsize=16)
    plt.tick_params(axis='x',which='major', labelsize=16)

#    ax = plt.gca()
#    dates_fmt = mdates.DateFormatter('%m-%d-%Y')
#    ax.xaxis.set_major_formatter(dates_fmt)

    return None

spreadsheet_id = '10pFtYAvmRedAWNU1vB-JDZRGKiRD4EZDH6zGzkghpZ0'
range_ = 'Sheet1'

sheet_obj = access_sheet(spreadsheet_id, range_)
df = sheet_to_df(sheet_obj)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    pprint(df)

format_plot(df)

plt.show()

#embed plot into tkinter gui

#show gui