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
    df = df[['date_time', 'weight_lb', 'lean_body_mass_lb', 'fat_mass_lb', 'fat_%']]
    df['date_time'] = df['date_time'].astype('datetime64[ns]')
    df = df.set_index('date_time')

    # down-sample data by day
    df = df.apply(pd.to_numeric, errors='coerce')
    cols = df.columns.difference(['date_time'])
    df[cols] = df[cols].astype(float)
    df = df.resample('d').mean().dropna(how='all')

    return df

def format_plot(df):
    import matplotlib.dates as mdates
#    import matplotlib.artist as m_art

#    art = m_art.Artist.set_label()
    x = df.index
    xmin = df.index.tolist()[0]-1
    xmax = df.index.tolist()[-1]+4
    plt.rc('xtick', labelsize=16)
    plt.rc('ytick', labelsize=16)
    labelpad = 25
    labelfontsize = 18
    linewidth=2
    """
    xticks = []
    d = xmin
    while d <= xmax:
        xticks.append(d)
        d += 1
    """
    plt.figure(1)
    ax0 = plt.subplot(211)
    ax0.grid()
    ax0.set_title('Body Composition', fontsize=30, pad=30)
    ax0.set_ylabel('Total / Lean Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
#    ax0.set_xticks(xticks)
    ax0.set_xlim(xmin, xmax)
#    ax0.set_xticklabels({'fontsize': 24})
    ax0.tick_params(axis='x', rotation=45)
    ax0.xaxis.set_major_formatter(mdates.DateFormatter('%B-%d'))
    ax0.plot(x, df[['weight_lb']], '--bo', label='Total Mass', linewidth=linewidth)
    ax0.plot(x, df[['lean_body_mass_lb']], '--ro', label='Lean Mass', linewidth=linewidth)
    ax0.legend(prop={'size': 20})

    ax1 = plt.subplot(212)
    ax1.grid()
#    ax1.legend(art, ['fat mass', 'fat %'])
    ax1.set_xlabel('Date', fontsize=labelfontsize, labelpad=labelpad)
    ax1.set_ylabel('Fat Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax1.tick_params(axis='x', rotation=45)
    lin1 = ax1.plot(x, df[['fat_mass_lb']], '--co', alpha=1.0, label='Fat Mass', linewidth=linewidth)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Fat (%)', fontsize=labelfontsize, labelpad=labelpad)
#    ax2.set_xticks(xticks)
    ax2.set_xlim(xmin, xmax)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%B-%d'))
    lin2 = ax2.plot(x, df[['fat_%']], '--ko', alpha=1.0, label='Fat %', linewidth=linewidth)

    lns = lin1+lin2
    labels = [l.get_label() for l in lns]
    ax2.legend(lns, labels, prop={'size': 20})
#    fig.tight_layout()

#    df.plot()

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