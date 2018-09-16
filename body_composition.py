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
        self.twin_label_pad = 30
        self.twin_label_rotation = 270
        self.line_width = 2
        self.date_format = '%a-%b-%d'
        self.x_min = df.index.tolist()[0] - dt.timedelta(days=1)
        self.x_max = df.index.tolist()[-1] + dt.timedelta(days=1)

        # initialize legend parameters
        self.legend_size = 20
        self.legend_loc = 'upper right'

    def plot_total_mass(self, grid_shape, plot_position, column_span, figure):

        # initialize parameters
        y_min = float(self.df[['weight_lb']].min()-1)
        y_max = float(self.df[['weight_lb']].max()+1)

        # setup plot
        ax_mass = plt.subplot2grid(grid_shape, plot_position, colspan=column_span, fig=figure)
        ax_mass.grid()
        ax_mass.set_title('Total Mass', fontsize=self.title_font_size, pad=self.title_pad)
        ax_mass.set_ylabel('Mass (lb)', fontsize=self.label_font_size, labelpad=self.label_pad)
        ax_mass.xaxis.set_major_formatter(mdates.DateFormatter(self.date_format))
        ax_mass.set_xlim(self.x_min, self.x_max)
        ax_mass.set_ylim(y_min, y_max)
        ax_mass.plot(self.df.index, self.df[['weight_lb']], '--ko',
                     label='Total Mass', linewidth=self.line_width)

    def plot_muscle(self, grid_shape, plot_position, column_span, figure):

        # initialize parameters
        y_min = float(self.df[['muscle_lb']].min()-0.25)
        y_max = float(self.df[['muscle_lb']].max()+0.25)

        # setup mass plot
        ax_mass = plt.subplot2grid(grid_shape, plot_position, colspan=column_span, fig=figure)
        ax_mass.grid()
        ax_mass.set_title('Muscle Composition', fontsize=self.title_font_size, pad=self.title_pad)
        ax_mass.set_ylabel('Mass (lb)', fontsize=self.label_font_size, labelpad=self.label_pad)
        ax_mass.set_ylim(y_min, y_max)
        line_mass = ax_mass.plot(self.df.index, self.df[['muscle_lb']], '--ko',
                                 label='Mass (lb)', linewidth=self.line_width)

        # setup percentage plot
        ax_percent = ax_mass.twinx()
        ax_percent.set_ylabel('Percentage', fontsize=self.label_font_size,
                              labelpad=self.twin_label_pad, rotation=self.twin_label_rotation)
        ax_percent.set_xlim(self.x_min, self.x_max)
        ax_percent.xaxis.set_major_formatter(mdates.DateFormatter(self.date_format))
        line_percent = ax_percent.plot(self.df.index, self.df[['muscle_%']], '--mo',
                                       label='Percentage', linewidth=self.line_width)

        # setup legend
        lines = line_mass + line_percent
        labels = [line.get_label() for line in lines]
        ax_percent.legend(lines, labels, prop={'size': self.legend_size}, loc=self.legend_loc)

    def plot_fat(self, grid_shape, plot_position, column_span, figure):

        # initialize parameters
        y_min = float(self.df[['fat_lb']].min()-0.25)
        y_max = float(self.df[['fat_lb']].max()+0.25)

        # setup mass plot
        ax_mass = plt.subplot2grid(grid_shape, plot_position, colspan=column_span, fig=figure)
        ax_mass.grid()
        ax_mass.set_title('Fat Composition', fontsize=self.title_font_size, pad=self.title_pad)
        ax_mass.set_ylabel('Mass (lb)', fontsize=self.label_font_size, labelpad=self.label_pad)
        ax_mass.set_ylim(y_min, y_max)
        line_mass = ax_mass.plt(self.df.index, self.df[['fat_lb']], '--ko',
                                label='Mass (lb)', linewidth=self.line_width)

        # setup percentage plot
        ax_percent = ax_mass.twinx()
        ax_percent.set_ylabel('Percentage', fontsize=self.label_font_size,
                              labelpad=self.twin_label_pad, rotation=self.twin_label_rotation)
        ax_percent.set_xlim(self.x_min, self.x_max)
        ax_percent.xaxis.set_major_formatter(mdates.DateFormatter(self.date_format))
        line_percent = ax_percent.plt(self.df.index, self.df[['fat_%']], '--co',
                                      label='Percentage', linewidth=self.line_width)

        # setup legend
        lines = line_mass + line_percent
        labels = [line.get_label() for line in lines]
        ax_percent.legend(lines, labels, prop={'size': self.legend_size}, loc=self.legend_loc)


spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
sheet_range = 'Sheet1'
col_labels = ['date_time', 'weight_lb', 'fat_%', 'water_%', 'bone_lb',
              'muscle_lb', 'BMI', 'fat_lb', 'bone_%', 'muscle_%']
index = 'date_time'
index_type = 'datetime64[ns]'

grid = (5, 2)

body = BodyComposition(spreadsheet_id, sheet_range, col_labels, index, index_type)
body.plot_total_mass(grid, plot_position=(0, 0), column_span=2, figure=body.body_fig)
body.plot_muscle(grid, plot_position=(1, 0), column_span=2, figure=body.body_fig)
body.plot_fat(grid, plot_position=(2, 0), column_span=2, figure=body.body_fig)

plt.show()





# TODO Future Dev
"""
    1. create csv from df
    2. update csv when new data available
"""
