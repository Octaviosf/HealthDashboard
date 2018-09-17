from IoTHealth.google_sheet import GoogleSheet
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class BodyComposition(object):
    """
    Interact with body composition dataFrame
    """

    def __init__(self, spreadsheet_id, sheet_range, labels, index, index_type):
        """
        :param spreadsheet_id: string of id located after '/d/' in
                               url 'https://docs.google.com/spreadsheets/d/'
        :param sheet_range: string specifying Google sheet range in A1 notation
        :param labels: list of strings of dataFrame labels
        :param index: string of dataFrame index
        :param index_type: string of dataFrame index type
        """

        # format df
        self.sheet = GoogleSheet(spreadsheet_id, sheet_range)
        df = self.sheet.sheet2df(labels, index, index_type)
        df = df.apply(pd.to_numeric, errors='coerce')
        cols = df.columns.difference([index])
        df[cols] = df[cols].astype(float)
        df = df.resample('d').mean().dropna(how='all')
        df[cols] = df[cols].round(decimals=2)
        self.df = df

        # initialize plot attributes
        self.body_fig = plt.figure(dpi=100)
        plt.rc('xtick', labelsize=18)
        plt.rc('ytick', labelsize=18)
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

    def plot_single(self, y_index, grid_shape, plot_position,
                    column_span, figure, title, y_label, line_style):
        """
        :param y_index: string of dataFrame y-axis index
        :param grid_shape: tuple of (row, column) form
        :param plot_position: tuple of (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        :param title: string of title
        :param y_label: string of y-axis label
        :param line_style: string of line style
        """

        # initialize y-axis limits
        y_min = float(self.df[[y_index]].min()-1)
        y_max = float(self.df[[y_index]].max()+1)

        # setup plot
        ax = plt.subplot2grid(grid_shape, plot_position, colspan=column_span, fig=figure)
        ax.grid()
        ax.set_title(title, fontsize=self.title_font_size, pad=self.title_pad)
        ax.set_ylabel(y_label, fontsize=self.label_font_size, labelpad=self.label_pad)
        ax.set_xlim(self.x_min, self.x_max)
        ax.set_ylim(y_min, y_max)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(self.date_format))
        ax.plot(self.df.index, self.df[[y_index]], line_style, label=y_label, linewidth=self.line_width)

    def plot_twin(self, index_mass, index_percent, grid_shape, plot_position,
                  column_span, figure, title, line_style_mass, line_style_percent):

        """
        :param index_mass: string of dataFrame index for mass data
        :param index_percent: string of dataFrame index for percent data
        :param grid_shape: tuple of (row, column) form
        :param plot_position: tuple of (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        :param title: string of title
        :param line_style_mass: string of line style for mass plot
        :param line_style_percent: string of line style for percentage plot
        """

        # initialize y-axis limits
        y_min = float(self.df[[index_mass]].min()-0.25)
        y_max = float(self.df[[index_mass]].max()+0.25)

        # setup mass plot
        ax_mass = plt.subplot2grid(grid_shape, plot_position, colspan=column_span, fig=figure)
        ax_mass.grid()
        ax_mass.set_title(title, fontsize=self.title_font_size, pad=self.title_pad)
        ax_mass.set_ylabel('Mass (lb)', fontsize=self.label_font_size, labelpad=self.label_font_size)
        ax_mass.set_ylim(y_min, y_max)
        line_mass = ax_mass.plot(self.df.index, self.df[[index_mass]], line_style_mass,
                                 label='Mass (lb)', linewidth=self.line_width)

        # setup percentage plot
        ax_percent = ax_mass.twinx()
        ax_percent.set_ylabel('Percentage', fontsize=self.label_font_size,
                              labelpad=self.twin_label_pad, rotation=self.twin_label_rotation)
        ax_percent.set_xlim(self.x_min, self.x_max)
        ax_percent.xaxis.set_major_formatter(mdates.DateFormatter(self.date_format))
        line_percent = ax_percent.plot(self.df.index, self.df[[index_percent]], line_style_percent,
                                       label='Percentage', linewidth=self.line_width)

        # setup legend
        lines = line_mass + line_percent
        labels = [line.get_label() for line in lines]
        ax_percent.legend(lines, labels, prop={'size': self.legend_size}, loc=self.legend_loc)

    def plot_total_mass(self, grid_shape, plot_position, column_span, figure):
        """
        :param grid_shape: tuple in (row, column) form
        :param plot_position: tuple in (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        """

        # initialize args
        y_index = 'weight_lb'
        title = 'Total Mass'
        y_label = 'Mass (lb)'
        line_style = '--ko'

        self.plot_single(y_index, grid_shape, plot_position,
                         column_span, figure, title, y_label, line_style)

    def plot_muscle(self, grid_shape, plot_position, column_span, figure):
        """
        :param grid_shape: tuple in (row, column) form
        :param plot_position: tuple in (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        """

        # initialize args
        index_mass = 'muscle_lb'
        index_percent = 'muscle_%'
        title = 'Muscle Composition'
        line_style_mass = '--ko'
        line_style_percent = '--mo'

        self.plot_twin(index_mass, index_percent, grid_shape, plot_position,
                       column_span, figure, title, line_style_mass, line_style_percent)

    def plot_fat(self, grid_shape, plot_position, column_span, figure):
        """
        :param grid_shape: tuple in (row, column) form
        :param plot_position: tuple in (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        """

        # initialize args
        index_mass = 'fat_lb'
        index_percent = 'fat_%'
        title = 'Fat Composition'
        line_style_mass = '--ko'
        line_style_percent = '--co'

        self.plot_twin(index_mass, index_percent, grid_shape, plot_position,
                       column_span, figure, title, line_style_mass, line_style_percent)

    def plot_bone(self, grid_shape, plot_position, column_span, figure):
        """
        :param grid_shape: tuple in (row, column) form
        :param plot_position: tuple in (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        """

        # initialize args
        index_mass = 'bone_lb'
        index_percent = 'bone_%'
        title = 'Bone Composition'
        line_style_mass = '--ko'
        line_style_percent = '--o'

        self.plot_twin(index_mass, index_percent, grid_shape, plot_position,
                       column_span, figure, title, line_style_mass, line_style_percent)

    def plot_water_percent(self, grid_shape, plot_position, column_span, figure):
        """
        :param grid_shape: tuple in (row, column) form
        :param plot_position: tuple in (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        """

        # initialize args
        y_index = 'water_%'
        title = 'Water Percentage'
        y_label = 'Percentage'
        line_style = '--bo'

        self.plot_single(y_index, grid_shape, plot_position,
                         column_span, figure, title, y_label, line_style)

    def plot_bmi(self, grid_shape, plot_position, column_span, figure):
        """
        :param grid_shape: tuple in (row, column) form
        :param plot_position: tuple in (row, column) form
        :param column_span: integer of column span
        :param figure: figure object
        """

        # initialize args
        y_index = 'BMI'
        title = 'Body Mass Index'
        y_label = 'BMI'
        line_style = '--ko'

        self.plot_single(y_index, grid_shape, plot_position,
                         column_span, figure, title, y_label, line_style)


# EXAMPLE using BodyComposition()
"""
# initialize parameters
spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
sheet_range = 'Sheet1'
col_labels = ['date_time', 'weight_lb', 'fat_%', 'water_%', 'bone_lb',
              'muscle_lb', 'BMI', 'fat_lb', 'bone_%', 'muscle_%']
index = 'date_time'
index_type = 'datetime64[ns]'
grid = (5, 2)
plt.rcParams.update({'figure.autolayout': True})

# plot data
body = BodyComposition(spreadsheet_id, sheet_range, col_labels, index, index_type)
body.plot_total_mass(grid, plot_position=(0, 0), column_span=2, figure=body.body_fig)
body.plot_muscle(grid, plot_position=(1, 0), column_span=2, figure=body.body_fig)
body.plot_fat(grid, plot_position=(2, 0), column_span=2, figure=body.body_fig)
body.plot_bone(grid, plot_position=(3, 0), column_span=2, figure=body.body_fig)
body.plot_water_percent(grid, plot_position=(4, 0), column_span=1, figure=body.body_fig)
body.plot_bmi(grid, plot_position=(4, 1), column_span=1, figure=body.body_fig)

plt.show()
"""

# TODO Future Dev
"""
    1. create csv from df
    2. update csv when new data available
"""
