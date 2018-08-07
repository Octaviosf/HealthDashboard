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
    xmax = df.index.tolist()[-1]+2
    lim_pads = 0.25
    y_t_min = float(df[['weight_lb']].min()-1)
    y_t_max = float(df[['weight_lb']].max()+1)
    y_m_min = float(df[['muscle_lb']].min()-lim_pads)
    y_m_max = float(df[['muscle_lb']].max()+lim_pads)
    y_f_min = float(df[['fat_lb']].min()-lim_pads)
    y_f_max = float(df[['fat_lb']].max()+lim_pads)
    y_b_min = float(df[['bone_lb']].min()-lim_pads)
    y_b_max = float(df[['bone_lb']].max()+lim_pads)
    y_w_min = float(df[['water_%']].min()-lim_pads)
    y_w_max = float(df[['water_%']].max()+lim_pads)
    y_B_min = float(df[['BMI']].min()-lim_pads)
    y_B_max = float(df[['BMI']].max()+lim_pads)
    labelpad = 25
    labelfontsize = 20
    linewidth = 2
    rotation = 0
    dateformat = '%a-%b-%d'

    # Total Mass plot
    ax0 = plt.subplot2grid((8,2), (4,0), rowspan=2, colspan=2)
    ax0.grid()
    ax0.set_ylabel('Total Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax0.set_xlim(xmin, xmax)
    ax0.set_ylim(y_t_min, y_t_max)
    ax0.tick_params(axis='x', rotation=rotation)
    ax0.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    ax0.plot(x, df[['weight_lb']], '--ko', label='Total Mass', linewidth=linewidth)

    # Muscle Mass plot
    ax1 = plt.subplot2grid((8,2), (0,0), rowspan=2, colspan=2)
    ax1.grid()
    ax1.set_title('Body Composition', fontsize=30, pad=30)
    ax1.set_ylabel('Muscle Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax1.set_ylim(y_m_min, y_m_max)
    ax1.tick_params(axis='x', rotation=rotation)
    lin0 = ax1.plot(x, df[['muscle_lb']], '--ro', label='Muscle Mass', linewidth=linewidth)

    # Muscle % plot
    ax2 = ax1.twinx()
    ax2.set_ylabel('Muscle %', fontsize=labelfontsize, labelpad=labelpad)
    ax2.set_xlim(xmin, xmax)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    lin1 = ax2.plot(x, df[['muscle_%']], '--mo', label='Muscle %', linewidth=linewidth)

    # Muscle Mass / Percentage legend
    lns0 = lin0+lin1
    labels0 = [l.get_label() for l in lns0]
    ax2.legend(lns0, labels0, prop={'size': 20})

    # Fat Mass plot
    ax3 = plt.subplot2grid((8,2), (2,0), rowspan=2, colspan=2)
    ax3.grid()
    ax3.set_ylabel('Fat Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax3.set_ylim(y_f_min, y_f_max)
    ax3.tick_params(axis='x', rotation=rotation)
    lin2 = ax3.plot(x, df[['fat_lb']], '--bo', alpha=1.0, label='Fat Mass', linewidth=linewidth)

    # Fat % plot
    ax4 = ax3.twinx()
    ax4.set_ylabel('Fat %', fontsize=labelfontsize, labelpad=labelpad)
    ax4.set_xlim(xmin, xmax)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    lin3 = ax4.plot(x, df[['fat_%']], '--co', alpha=1.0, label='Fat %', linewidth=linewidth)

    # Fat Mass / Percentage legend
    lns1 = lin2+lin3
    labels1 = [l.get_label() for l in lns1]
    ax4.legend(lns1, labels1, prop={'size': 20})

    # Bone Mass plot
    ax5 = plt.subplot2grid((8,2), (6,0), rowspan=1, colspan=2)
    ax5.grid()
    ax5.set_ylabel('Bone Mass (lb)', fontsize=labelfontsize, labelpad=labelpad)
    ax5.set_ylim(y_b_min, y_b_max)
    lin4 = ax5.plot(x, df[['bone_lb']], '-ro', label='Bone Mass', linewidth=linewidth)

    ax6 = ax5.twinx()
    ax6.set_ylabel('Bone %', fontsize=labelfontsize, labelpad=labelpad)
    ax6.set_xlim(xmin, xmax)
    ax6.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    lin5 = ax6.plot(x, df[['bone_%']], '-mo', alpha=1.0, label='Bone %', linewidth=linewidth)

    # Bone Mass / Percentage legend
    lns2 = lin4+lin5
    labels2 = [l.get_label() for l in lns2]
    ax6.legend(lns2, labels2, prop={'size': 20})

    # Water % plot
    ax7 = plt.subplot2grid((8,2), (7,0), rowspan=1, colspan=1)
    ax7.grid()
    ax7.set_ylabel('Water %', fontsize=labelfontsize, labelpad=labelpad)
    ax7.set_xlim(xmin, xmax)
    ax7.set_ylim(y_w_min, y_w_max)
    ax7.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    ax7.plot(x, df[['water_%']], '-bo', label='Water %', linewidth=linewidth)

    # BMI plot
    ax8 = plt.subplot2grid((8,2), (7,1), rowspan=1, colspan=1)
    ax8.grid()
    ax8.set_ylabel('BMI', fontsize=labelfontsize, labelpad=labelpad)
    ax8.set_xlim(xmin, xmax)
    ax8.set_ylim(y_B_min, y_B_max)
    ax8.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
    ax8.plot(x, df[['BMI']], '-ko', label='BMI', linewidth=linewidth)

    plt.tight_layout()

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

        spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
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


