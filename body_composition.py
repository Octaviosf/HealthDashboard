from IoTHealth.google_sheet import GoogleSheet
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class BodyComposition(object):

    def __init__(self, spreadsheet_id, sheet_range, labels, index, index_type):

        # format df
        self.sheet = GoogleSheet(spreadsheet_id, sheet_range)
        df = self.sheet.sheet2df(labels, index, index_type)
        df = df.apply(pd.to_numeric, errors='coerce')
        cols = df.columns.difference([index])
        df[cols] = df[cols].astype(float)
        df = df.resample('d').mean().dropna(how='all')
        df[cols] = df[cols].round(decimals=2)
        self.df = df

        # initialize plot parameters
        self.body_fig = plt.figure(dpi=100)
        self.title_pad = 20
        self.title_font_size = 30
        self.label_font_size = 20
        self.label_pad = 10
        self.line_width = 2
        self.date_format = '%a-%b-%d'
        self.x_min = df.index.tolist()[0] - dt.timedelta(days=1)
        self.x_max = df.index.tolist()[-1] + dt.timedelta(days=1)

    def plot_total_mass(self, grid, position, column_span, figure):

        # initialize parameters
        y_min = float(self.df[['weight_lb']].min()-1)
        y_max = float(self.df[['weight_lb']].max()+1)

        # setup plot
        ax = plt.subplot2grid(grid, position, colspan=column_span, fig=figure)
        ax.grid()
        ax.set_title('Total Mass', fontsize=self.title_font_size, pad=self.title_pad)
        ax.set_ylabel('Mass (lb)', fontsize=self.label_font_size, labelpad=self.label_pad)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(self.date_format))
        ax.set_xlim(self.x_min, self.x_max)
        ax.set_ylim(y_min, y_max)
        ax.plot(self.df.index, self.df[['weight_lb']], '--ko', label='Total Mass', linewidth=self.line_width)



spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
sheet_range = 'Sheet1'
col_labels = ['date_time', 'weight_lb', 'fat_%', 'water_%', 'bone_lb',
              'muscle_lb', 'BMI', 'fat_lb', 'bone_%', 'muscle_%']
index = 'date_time'
index_type = 'datetime64[ns]'

body = BodyComposition(spreadsheet_id, sheet_range, col_labels, index, index_type)





# TODO Future Dev
"""
    1. create csv from df
    2. update csv when new data available
"""
