from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import numpy as np
import numpy.ma as ma


def time2radian(time_list):
    """
    :param time_list: list of dateTimes
    :return: list of radians
    """
    minutes_per_day = 24*60
    seconds_per_day = 24*60*60

    radians = []

    for time in time_list:
        if isinstance(time, (dt,)):
            proportion_of_day = time.hour/24
            proportion_of_day += time.minute/minutes_per_day
            proportion_of_day += time.second/seconds_per_day
            radian = 2*pi*proportion_of_day
            radians.append(radian)
        else:
            proportion_of_day = time/seconds_per_day
            radian = 2*pi*proportion_of_day
            radians.append(radian)

    return radians


class Sleep(object):
    """
    Interact with sleep logs:
        - request sleep logs
        - update sleep logs
        - create sleep.csv
        - capture explicit data from raw sleep logs
    """
    def __init__(self, sleep_file_path, tokens_file_path):
        """
        create and/or update sleep.csv
        capture sleep_logs using instance variable

        :param sleep_file_path: absolute file-path to sleep.csv
        :param tokens_file_path: absolute file-path to fitbit_tokens.txt
        """

        # assignments
        self.sleep_file_path = sleep_file_path
        self.tokens_file_path = tokens_file_path
        self.today = dt.today().strftime("%Y-%m-%d")

        # capture up-to-date sleep logs
        if os.path.isfile(self.sleep_file_path) and os.access(self.sleep_file_path, os.R_OK):
            self.sleep_logs = self.update_local_logs()
        else:
            self.sleep_logs = self.initialize_csv()

    def update_local_logs(self):
        """
        update sleep.csv and sleep_logs

        :return: up-to-date sleep_logs
        """

        # read sleep.csv and capture data
        local_logs = pd.read_csv(self.sleep_file_path)
        local_logs = local_logs.set_index("dateOfSleep")
        latest_date_local = local_logs.index.max()

        # update sleep_logs, depending on latest local entry
        if latest_date_local == self.today:
            sleep_logs = local_logs
        else:
            # request missing logs from Fitbit
            latest_date_local = dt.strptime(latest_date_local, "%Y-%m-%d")
            next_date_local = (latest_date_local + timedelta(days=1)).strftime("%Y-%m-%d")
            date_range = (next_date_local, self.today)
            fitbit = Fitbit(self.tokens_file_path)
            raw_logs = fitbit.sleeplogs_range(date_range)

            print(raw_logs) # TODO test

            # update sleep_logs and sleep.csv, depending on logs returned from Fitbit
            if not raw_logs['sleep']:
                sleep_logs = local_logs
            else:
                # capture explicit data from raw logs and append to local_logs
                api_logs = self.capture_explicit_data(raw_logs)
                frames = [local_logs, api_logs]
                sleep_logs = pd.concat(frames)

                # update sleep.csv
                sleep_logs.to_csv(path_or_buf=self.sleep_file_path, mode='w')

        sleep_logs.index = pd.to_datetime(sleep_logs.index)
        # sleep_logs = sleep_logs.index.astype('datetime64[ns]')

        return sleep_logs

    def initialize_csv(self):
        """
        initialize sleep.csv with up-to-date sleep logs

        :return sleep_logs: up-to-date sleep logs
        """

        # request all sleep logs from Fitbit
        date_range = ("2018-08-07", self.today)
        fitbit = Fitbit(self.tokens_file_path)
        raw_logs = fitbit.sleeplogs_range(date_range)

        # capture explicit data from raw logs
        sleep_logs = self.capture_explicit_data(raw_logs)
        sleep_logs.to_csv(path_or_buf=self.sleep_file_path, mode='w+', date_format="%Y-%m-%d")

        sleep_logs.index = pd.to_datetime(sleep_logs.index)

        return sleep_logs

    def capture_explicit_data(self, sleep_logs_raw):
        """
        capture explicit data from raw sleep logs

        :param sleep_logs_raw: raw sleep data from Fitbit request
        :return sleep_logs: explicit sleep data captured from raw logs
        """

        # assignments
        dict_labels = ["dateOfSleep", "minutesAfterWakeup",
                       "minutesToFallAsleep", "startTime"]
        stages_labels = ["deep", "light", "rem", "wake"]
        sleep_logs = []
        frames = []

        # create dictionary list to capture explicit data
        for log_raw in sleep_logs_raw["sleep"]:
            sleep_log = {}
            duration_sleep = 0
            duration_total = 0
            for label in dict_labels:
                sleep_log[label] = [log_raw[label]]
            for label in stages_labels:
                sleep_log[label] = [log_raw["levels"]["summary"][label]["minutes"]]
                duration_total += sleep_log[label][0]
            for label in stages_labels[:-1]:
                duration_sleep += sleep_log[label][0]
            sleep_log["efficiency"] = [round(duration_sleep / duration_total, 2)]
            sleep_log["duration"] = [duration_total]
            sleep_logs.append(sleep_log)
        sleep_logs.reverse()

        # create DataFrame list from dictionary list
        for log in sleep_logs:
            df = pd.DataFrame.from_dict(data=log)
            frames.append(df)

        # concatenate DataFrames and set index
        sleep_logs = pd.concat(frames)
        sleep_logs = sleep_logs.set_index('dateOfSleep')

        return sleep_logs

    def plot_efficiency(self, grid_shape, position, rowspan):
        """
        plot sleep efficiency

        :param grid_shape: grid shape
        :param position: position within grid
        :param rowspan: grid rows spanned by plot
        :return:
        """

        # global plot format
        plt.rc("xtick", labelsize=18)
        plt.rc("ytick", labelsize=18)

        # initialize parameter values
        x = self.sleep_logs.index
        y = self.sleep_logs['efficiency'].tolist()
        xmin = self.sleep_logs.index.tolist()[0] - timedelta(days=1)
        xmax = self.sleep_logs.index.tolist()[-1] + timedelta(days=1)
        labelpad = 25
        labelfontsize = 20
        dateformat = "%a-%b-%d"

        # set parameters
        ax = plt.subplot2grid(grid_shape, position, rowspan=rowspan)
        ax.grid()
        ax.set_title('Sleep Efficiency', fontsize=30, pad=30)
        ax.set_ylabel('Efficiency', fontsize=labelfontsize, labelpad=labelpad)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0, 1.1, 0.1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))

        # annotate bars
        for date, height in zip(x, y):
            ax.text(date, height+0.02, height, fontsize=18,
                    fontweight='bold', horizontalalignment='center')

        ax.bar(x, y, edgecolor='k', width=0.5, linewidth=1.5)

        plt.tight_layout()

        return plt

    def plot_stages_percent(self, grid_shape, position, rowspan):

        # initialize graph params
        plt.rc('xtick', labelsize=18)
        plt.rc('ytick', labelsize=18)
        x = self.sleep_logs.index
        x = date2num(x)
        xmin = self.sleep_logs.index.tolist()[0] - timedelta(days=1)
        xmax = self.sleep_logs.index.tolist()[-1] + timedelta(days=1)
        numdays = xmax-xmin
        median_array_shape = (1, len(x))
        xticks = [xmin + timedelta(days=d) for d in range(1, numdays.days)]
        bar_width = 0.2
        labelpad = 25
        labelfontsize = 20
        dateformat = '%a-%b-%d'
        alpha = 0.3
        medians_color = 'k'
        annotate_height = 1
        annotate_fontsize = 18
        annotate_fontweight = 'bold'
        annotate_align = 'center'
        annotate_color = 'w'

        # initialize graph data
        durations = self.sleep_logs['duration'].values
        awake_perc = np.around(self.sleep_logs['wake'].values / durations, 3) * 100
        rem_perc = np.around(self.sleep_logs['rem'].values / durations, 3) * 100
        light_perc = np.around(self.sleep_logs['light'].values / durations, 3) * 100
        deep_perc = np.around(self.sleep_logs['deep'].values / durations, 3) * 100
        awake_median = float(np.around(np.median(awake_perc), 3))
        rem_median = float(np.around(np.median(rem_perc), 3))
        light_median = float(np.around(np.median(light_perc), 3))
        deep_median = float(np.around(np.median(deep_perc), 3))
        awake_median_array = np.full(median_array_shape, awake_median)[0]
        rem_median_array = np.full(median_array_shape, rem_median)[0]
        light_median_array = np.full(median_array_shape, light_median)[0]
        deep_median_array = np.full(median_array_shape, deep_median)[0]


        # initialize masks
        mask_awake_perc = ma.where(awake_perc>=awake_median_array)
        mask_awake_median = ma.where(awake_median_array>=awake_perc)
        mask_rem_perc = ma.where(rem_perc>=rem_median_array)
        mask_rem_median = ma.where(rem_median_array>=rem_perc)
        mask_light_perc = ma.where(light_perc>=light_median_array)
        mask_light_median = ma.where(light_median_array>=light_perc)
        mask_deep_perc = ma.where(deep_perc>=deep_median_array)
        mask_deep_median = ma.where(deep_median_array>=deep_perc)


        # set graph params
        ax = plt.subplot2grid(grid_shape, position, rowspan=rowspan)
        ax.grid()
        ax.set_title('Sleep Stages', fontsize=30, pad=30)
        ax.set_ylabel('Percentage %', fontsize=labelfontsize, labelpad=labelpad)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation = -45, ha='left', rotation_mode='anchor')
        ax.set_xticks(xticks)
        ax.set_yticks(np.arange(0, 110, 5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
        plt.tight_layout()

        # annotate each stage with percentage
        for x_pos, awake_p in zip(x, awake_perc):
            ax.text(x_pos-0.3, annotate_height, int(round(awake_p, 0)), fontsize=annotate_fontsize,
                    fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)
        for x_pos, rem_p in zip(x, rem_perc):
            ax.text(x_pos-0.1, annotate_height, int(round(rem_p, 0)), fontsize=annotate_fontsize,
                    fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)
        for x_pos, light_p in zip(x, light_perc):
            ax.text(x_pos+0.1, annotate_height, int(round(light_p, 0)), fontsize=annotate_fontsize,
                    fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)
        for x_pos, deep_p in zip(x, deep_perc):
            ax.text(x_pos+0.3, annotate_height, int(round(deep_p, 0)), fontsize=annotate_fontsize,
                    fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)

        # plot stages with masks
        ax.bar((x-0.3)[mask_awake_median], awake_median_array[mask_awake_median], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar(x-0.3, awake_perc, color='m', width=bar_width, align='center', label='Awake')
        ax.bar((x-0.3)[mask_awake_perc], awake_median_array[mask_awake_perc], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar((x-0.1)[mask_rem_median], rem_median_array[mask_rem_median], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar(x-0.1, rem_perc, color='c', width=bar_width, align='center', label='REM')
        ax.bar((x-0.1)[mask_rem_perc], rem_median_array[mask_rem_perc], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar((x+0.1)[mask_light_median], light_median_array[mask_light_median], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar(x+0.1, light_perc, width=bar_width, align='center', label='Light')
        ax.bar((x+0.1)[mask_light_perc], light_median_array[mask_light_perc], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar((x+0.3)[mask_deep_median], deep_median_array[mask_deep_median], alpha=alpha,
               color=medians_color, width=bar_width, align='center')
        ax.bar(x+0.3, deep_perc, color='b', width=bar_width, align='center', label='Deep')
        ax.bar((x+0.3)[mask_deep_perc], deep_median_array[mask_deep_perc], alpha=alpha,
               color=medians_color, width=bar_width, align='center', label='Median')

        plt.legend(prop={'size': 15}, loc='upper right')

        return plt

    def plot_polar_hypnograms(self, shape):

        today = dt.strptime(self.today, "%Y-%m-%d")
        days = [today - timedelta(days=d) for d in range(0, 7)].reverse()

        plt0 = self.polar_hypnogram(self.sleep_time_series[days[0]], shape, (3,0))
        plt1 = self.polar_hypnogram(self.sleep_time_series[days[1]], shape, (3,1))
        plt2 = self.polar_hypnogram(self.sleep_time_series[days[2]], shape, (3,2))
        plt3 = self.polar_hypnogram(self.sleep_time_series[days[3]], shape, (3,3))
        plt4 = self.polar_hypnogram(self.sleep_time_series[days[4]], shape, (3,4))
        plt5 = self.polar_hypnogram(self.sleep_time_series[days[5]], shape, (3,5))
        plt6 = self.polar_hypnogram(self.sleep_time_series[days[6]], shape, (3,6))

        plots = [plt0, plt1, plt2, plt3, plt4, plt5, plt6]

        return plots

    def polar_hypnogram(self, sleep_time_series, shape, position):
        """
        :param sleep_time_series: dictionary storing 'data' and 'shortData' for specific day ['dateOFSleep']
        :param shape:
        :param position:
        :param rowspan:
        :return:

        j. create radial (hypnogram) bar plot for each day, with clock y-axis, and plotting bedtime, stages, out-of-bedtime
            -- plot each stage on own bar
                - inner bar is deep
                - outer is median duration (with regards to day-of-week) (perhaps superimpose with "awake")

        * "shortData" stores moments of "wake" of duration 3 min or less
        *
        """

        stages = ['deep', 'light', 'rem', 'wake']
        labels_stages = ['Deep', 'Light', 'REM', 'Awake']
        start_times = {}
        end_times = {}
        bar_height = 1

        for stage in stages:
            start_times[stage] = time2radian(sleep_time_series['data'][stage]['start_times'])
            end_times[stage] = time2radian(sleep_time_series['data'][stage]['end_times'])

        ax = plt.subplot2grid(shape, position, polar=True)
        ax.barh(0, width=0)
        ax.barh(1, width=0)
        ax.barh(5, left=start_times['wake'], width=end_times['wake'], color='m', label='Awake', height=bar_height)
        ax.barh(4, left=start_times['rem'], width=end_times['rem'], color='c', label='REM', height=bar_height)
        ax.barh(3, left=start_times['light'], width=end_times['light'], color='C0', label='Light', height=bar_height)
        ax.barh(2, left=start_times['deep'], width=end_times['deep'], color='b', label='Deep', height=bar_height)
        # ax.barh(2, left=median_start, width=median_duration, color='k', alpha=0.3, label='Median', height=bar_height)

        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticks(np.linspace(0, 2 * pi, 24, endpoint=False))
        ax.set_xticklabels(range(0, 24))

        ax.set_rlabel_position(0)
        ax.set_rgrids([2, 3, 4, 5], labels=labels_stages, color='k',
                      fontsize=12, fontweight='bold', verticalalignment='center')

        # plt.legend(loc='upper right')

        ax.grid(axis='x')

        return plt


# assignments
tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'

# fig parameters
grid_shape = (4, 1)
eff_plt_pos = (2, 0)
stages_plt_pos = (0, 0)
rowspan = 2

# capture sleep data
sleep = Sleep(sleep_logs_fp, tokens_fp)

"""
with pd.option_context("display.max_rows", 11, "display.max_columns", 10):
    print(sleep.sleep_logs)
"""

# set fig shape and show
plt.figure(figsize=(30,20))
efficiency_plot = sleep.plot_efficiency(grid_shape, eff_plt_pos, rowspan)
stages_plot = sleep.plot_stages_percent(grid_shape, stages_plt_pos, rowspan)
stages_plot.show()
efficiency_plot.show()





# TODO Dev

"""
    1. Create Sleep() class with attributes:
       DONE a. capture_explicit_data() returns pandas df
       DONE b. create are_logs_uptodate boolean
       DONE c. write sleep.csv file if nonexistent
       DONE d. update sleep.csv
       DONE e. create sleep_logs_dataframe
       DONE f. clean and comment sleep.py code
       DONE g. find out why minutesAfterWakeup and minutesToFallAsleep are mostly 0
                -- for minutesToFallAsleep = 0 makes sense as I've been staying awake till
                    im ready to KO
                -- for minutesAfterWakeup = 0 makes sense as I've pressed "awake" on app
                    when I get up from bed rather than pressing it as soon as I wake and press
                    "done" when I get up from bed
       DONE h. create efficiency_plot()
       DONE i. create stages_plot()
            j. create radial (hypnogram) bar plot for each day, with clock y-axis, and plotting bedtime, stages, out-of-bedtime
                -- plot each stage on own bar (inner bar is deep and outer is awake)
            k. plot efficiency using line graph 
            h. create fig, capturing plots, using sleep_logs_dataframe
            etc ...
"""

# TODO Dev Future

"""
    1. create sleep_%YYYY-%mm-%dd.csv backup file every month on 1st
        - may be useful to create datetime class variable which updates to current
            date each month and date is posted to filename 

"""
