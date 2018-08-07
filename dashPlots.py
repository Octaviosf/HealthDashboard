import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import pandas as pd
from pprint import pprint

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
    df = df[['date_time', 'weight_lb', 'fat_%', 'water_%', 'bone_lb',
             'muscle_lb', 'BMI', 'fat_lb', 'bone_%', 'muscle_%']]
    df['date_time'] = df['date_time'].astype('datetime64[ns]')
    df = df.set_index('date_time')

    # down-sample data by day
    df = df.apply(pd.to_numeric, errors='coerce')
    cols = df.columns.difference(['date_time'])
    df[cols] = df[cols].astype(float)
    df = df.resample('d').mean().dropna(how='all')
    df[cols] = df[cols].round(decimals=2)

    return df

def create_plot(df):
    """
    creates and  formats  a plot using data from df
    :param df: dataframe
    :return: None
    """
    import matplotlib.dates as mdates

    # global plot format
    fig = plt.figure(figsize=(17, 12), dpi=100)
    plt.rc('xtick', labelsize=18)
    plt.rc('ytick', labelsize=18)

    # parameter init
    x = df.index
    xmin = df.index.tolist()[0]-1
    xmax = df.index.tolist()[-1]+4
    y_t_min = float(df[['weight_lb']].min()-0.25)
    y_t_max = float(df[['weight_lb']].max()+0.25)
    y_l_min = float(df[['muscle_lb']].min()-0.25)
    y_l_max = float(df[['muscle_lb']].max()+0.25)
    labelpad = 25
    labelfontsize = 20
    linewidth = 2
    rotation = 0
    dateformat = '%a-%b-%d'

    # Total Mass plot
    ax0 = plt.subplot2grid((4,1), (0,0), rowspan=2)
    ax0.grid()
    ax0.set_title('Body Composition', fontsize=30, pad=30)
    ax0.set_ylabel('Total Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax0.set_xlim(xmin, xmax)
    ax0.set_ylim(y_t_min, y_t_max)
    ax0.tick_params(axis='x', rotation=rotation)
    ax0.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    ax0.plot(x, df[['weight_lb']], '--bo', label='Total Mass', linewidth=linewidth)

    # Muscle Mass plot
    ax1 = plt.subplot2grid((4,1), (2,0), rowspan=1)
    ax1.grid()
    ax1.set_ylabel('Muscle Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(y_l_min, y_l_max)
    ax1.tick_params(axis='x', rotation=rotation)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    ax1.plot(x, df[['muscle_lb']], '--go', label='Muscle Mass', linewidth=linewidth)

    # Fat Mass plot
    ax2 = plt.subplot2grid((4,1), (3,0), rowspan=1)
    ax2.grid()
    ax2.set_ylabel('Fat Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax2.tick_params(axis='x', rotation=rotation)
    lin2 = ax2.plot(x, df[['fat_mass_lb']], '--ro', alpha=1.0, label='Fat Mass', linewidth=linewidth)

    # Fat % plot
    ax3 = ax2.twinx()
    ax3.set_ylabel('Fat %', fontsize=labelfontsize, labelpad=labelpad)
    ax3.set_xlim(xmin, xmax)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    lin3 = ax3.plot(x, df[['fat_%']], '--ko', alpha=1.0, label='Fat %', linewidth=linewidth)

    # Fat Mass / Percentage legend
    lns1 = lin2+lin3
    labels1 = [l.get_label() for l in lns1]
    ax3.legend(lns1, labels1, prop={'size': 20})

    return fig

class SmartMirror(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.attributes("-fullscreen", True)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenu, HealthDashboard):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class MainMenu(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Smart Mirror", font=("Verdana", 12))
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Health Dashboard",
                             command=lambda: controller.show_frame(HealthDashboard))
        button1.pack()

class HealthDashboard(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Health Dashboard", font=("Verdana", 12))
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Main Menu",
                             command=lambda: controller.show_frame(MainMenu))
        button1.pack()

        spreadsheet_id = '10pFtYAvmRedAWNU1vB-JDZRGKiRD4EZDH6zGzkghpZ0'
        range_ = 'Sheet1'
        sheet_obj = access_sheet(spreadsheet_id, range_)

        df = sheet_to_df(sheet_obj)

        fig = create_plot(df)

        # embed plot into SmartMirror gui
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


#draw gui
app = SmartMirror()
app.mainloop()


