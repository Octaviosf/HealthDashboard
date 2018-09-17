import tkinter as tk
from tkinter import ttk
import pandas as pd
import datetime as dt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
from IoTHealth.sleep import Sleep
from IoTHealth.body_composition import BodyComposition
from IoTHealth.google_sheet import GoogleSheet

plt.rcParams.update({'figure.autolayout': True})


class SmartMirror(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.attributes("-fullscreen", True)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (SleepMetrics, BodyComposition):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SleepMetrics)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class SleepMetrics(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Sleep", font=("verdana", 12))
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Body Composition",
                             command=lambda: controller.show_frame(BodyComposition))
        button1.pack()

        # sleep plots
        tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
        sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'
        sleep_series_fp = '/home/sosa/Documents/IoTHealth/sleep_series.json'

        # fig parameters
        grid_shape = (4, 15)
        eff_plt_pos = (2, 0)
        stages_plt_pos = (0, 0)

        # capture sleep data
        sleep = Sleep(sleep_logs_fp, sleep_series_fp, tokens_fp)

        # set fig shape and show
        sleep.plot_stages_percent(grid_shape, stages_plt_pos, rowspan=2, colspan=15)
        sleep.plot_efficiency(grid_shape, eff_plt_pos, rowspan=1, colspan=15)
        plt.tight_layout()
        sleep.plot_polar_hypnograms(grid_shape)

        # embed plot into SmartMirror gui
        canvas = FigureCanvasTkAgg(sleep.sleep_fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class BodyComposition(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Body Composition", font=("Verdana", 12))
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Sleep",
                             command=lambda: controller.show_frame(SleepMetrics))
        button1.pack()

        spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
        range_ = 'Sheet1'
        sheet_obj = access_sheet(spreadsheet_id, range_)
        df = sheet_to_df(sheet_obj)
        body_fig = bodycomp_plots(df)

        # embed plot into frame
        canvas = FigureCanvasTkAgg(body_fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# draw gui
app = SmartMirror()
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
