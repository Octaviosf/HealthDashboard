import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
from IoTHealth.sleep import Sleep
from IoTHealth.body_composition import BodyComposition

plt.rcParams.update({'figure.autolayout': True})


class HealthDashboard(tk.Tk):
    """
    create HealthDashboard gui using inherited TK attributes
    """

    def __init__(self, *args, **kwargs):
        """
        setup gui parameters
        """

        # setup gui parameters
        tk.Tk.__init__(self, *args, **kwargs)
        self.attributes("-fullscreen", True)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        # append frames to frames dictionary
        for F in (SleepMetrics, BodyMetrics):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # show startup frame
        self.show_frame(SleepMetrics)

    def show_frame(self, cont):
        """
        raises container to front
        :param cont: container to be raised
        """

        frame = self.frames[cont]
        frame.tkraise()


class SleepMetrics(tk.Frame):
    """
    create frame displaying sleep metrics for last 15 days
    """

    def __init__(self, parent, controller):
        """
        initialize frame parameters
        :param parent: parent
        :param controller: controller
        """

        # setup container parameters
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Sleep", font=("verdana", 12))
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Body Composition",
                             command=lambda: controller.show_frame(BodyMetrics))
        button1.pack()

        # initialize Sleep object parameters
        tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
        sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'
        sleep_series_fp = '/home/sosa/Documents/IoTHealth/sleep_series.json'
        grid_shape = (4, 15)
        eff_plt_pos = (2, 0)
        stages_plt_pos = (0, 0)

        # capture sleep data
        sleep = Sleep(sleep_logs_fp, sleep_series_fp, tokens_fp)

        # plot data to class figure
        sleep.plot_stages_percent(grid_shape, stages_plt_pos, rowspan=2, colspan=15)
        sleep.plot_efficiency(grid_shape, eff_plt_pos, rowspan=1, colspan=15)
        plt.tight_layout()
        sleep.plot_polar_hypnograms(grid_shape)

        # embed plot into HealthDashboard gui
        canvas = FigureCanvasTkAgg(sleep.sleep_fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class BodyMetrics(tk.Frame):
    """
    create frame displaying available body composition data
    """
    def __init__(self, parent, controller):
        """
        initialize frame parameters
        :param parent: parent
        :param controller: controller
        """

        # setup container parameters
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Body Composition", font=("Verdana", 12))
        label.pack(pady=10, padx=10)
        button1 = ttk.Button(self, text="Sleep",
                             command=lambda: controller.show_frame(SleepMetrics))
        button1.pack()

        # initialize BodyComposition object parameters
        spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
        sheet_range = 'Sheet1'
        col_labels = ['date_time', 'weight_lb', 'fat_%', 'water_%', 'bone_lb',
                      'muscle_lb', 'BMI', 'fat_lb', 'bone_%', 'muscle_%']
        index = 'date_time'
        index_type = 'datetime64[ns]'
        grid = (5, 2)

        # plot data to class figure
        body = BodyComposition(spreadsheet_id, sheet_range, col_labels, index, index_type)
        body.plot_total_mass(grid, plot_position=(0, 0), column_span=2, figure=body.body_fig)
        body.plot_muscle(grid, plot_position=(1, 0), column_span=2, figure=body.body_fig)
        body.plot_fat(grid, plot_position=(2, 0), column_span=2, figure=body.body_fig)
        body.plot_bone(grid, plot_position=(3, 0), column_span=2, figure=body.body_fig)
        body.plot_water_percent(grid, plot_position=(4, 0), column_span=1, figure=body.body_fig)
        body.plot_bmi(grid, plot_position=(4, 1), column_span=1, figure=body.body_fig)

        # embed plot into HealthDashboard gui
        canvas = FigureCanvasTkAgg(body.body_fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# draw gui
app = HealthDashboard()
app.mainloop()

# TODO Dev
"""
    DONE 1. Create buttons for body comp and sleep data
    DONE 2. Add all axes to self.sleep_fig
    DONE 3. Display last 15 days of sleep data
    DONE 4. Clean up sleep graph text params
    DONE 5. Clean up body comp graph params
         6. create GoogleSheets() class for google sheets requests
         7. create body.py to define Body() class and use OOP approach
    --
    
    Future TODO
    
    1. Create Body() class with attributes:
            a. write body.csv file if nonexistent
            b. update body.csv
            etc ...
            
    2. Create IotHealth() class with attributes:
            a. write all .csv files if nonexistent
            b. update all .csv files
            etc ...

"""
