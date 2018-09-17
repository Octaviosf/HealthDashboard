from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import time
from datetime import timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import numpy as np
import numpy.ma as ma
from numpy import pi
import json
import copy
from math import isnan


def time2radian(time_list):
    """
    convert datetimes to radians
    :param time_list: list of date_times or seconds strings
    :return: list of radians
    """

    # initialize parameters
    minutes_per_day = 24*60
    seconds_per_day = 24*60*60
    radians = []

    # calculate and append radians for seconds, minutes, and hours
    for time in time_list:
        if isinstance(time, (str,)):
            time = dt.strptime(time[:10] + ' ' + time[11:], "%Y-%m-%d %H:%M:%S.%f")
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
    interact with sleep logs
    """
    def __init__(self, sleep_file_path, sleep_series_file_path, tokens_file_path):
        """
        create and/or update sleep.csv
        capture sleep_logs using instance variable
        :param sleep_file_path: string of absolute file-path to sleep.csv
        :param tokens_file_path: string of absolute file-path to fitbit_tokens.txt
        """

        # initialize data attributes
        self.sleep_file_path = sleep_file_path
        self.sleep_series_file_path = sleep_series_file_path
        self.tokens_file_path = tokens_file_path
        self.today = dt.today().strftime("%Y-%m-%d")

        # initialize plot attributes
        self.sleep_fig = plt.figure(dpi=100)
        plt.rc("xtick", labelsize=18)
        plt.rc("ytick", labelsize=18)

        # capture up-to-date sleep logs
        if os.path.isfile(self.sleep_file_path) and os.access(self.sleep_file_path, os.R_OK):
            self.sleep_logs = self.update_local_logs()
        else:
            self.sleep_logs = self.initialize_csv()

        # capture up-to-date sleep time series
        if os.path.isfile(sleep_series_file_path) and os.access(self.sleep_series_file_path, os.R_OK):
            self.sleep_series = self.update_local_series()
        else:
            self.sleep_series = self.initialize_json()

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
            raw_logs = fitbit.sleep_logs_range(date_range)

            # update sleep_logs and sleep.csv, depending on logs returned from Fitbit
            if not raw_logs['sleep']:
                sleep_logs = local_logs
            else:
                # capture explicit data from raw logs and append to local_logs
                api_logs = self.capture_log_data(raw_logs, date_range)
                frames = [local_logs, api_logs]
                sleep_logs = pd.concat(frames)

                # update sleep.csv
                sleep_logs.to_csv(path_or_buf=self.sleep_file_path, mode='w')
        sleep_logs.index = pd.to_datetime(sleep_logs.index)

        return sleep_logs

    def update_local_series(self):
        """
        update sleep_series.json and sleep_series
        :return: up-to-date sleep_series
        """

        # read sleep_series.json and capture data
        with open(self.sleep_series_file_path) as series_file:
            local_series = json.load(series_file)

        latest_date_local = local_series["sleep"][-1]["dateOfSleep"]

        # update sleep_series, depending on latest local entry
        if latest_date_local == self.today:
            sleep_series = local_series
        else:
            # request missing logs from Fitbit
            latest_date_local = dt.strptime(latest_date_local, "%Y-%m-%d")
            next_date_local = (latest_date_local + timedelta(days=1)).strftime("%Y-%m-%d")
            date_range = (next_date_local, self.today)
            fitbit = Fitbit(self.tokens_file_path)
            raw_logs = fitbit.sleep_logs_range(date_range)

            # update sleep_series and sleep_series.json, depending on logs returned from Fitbit
            if not raw_logs["sleep"]:
                sleep_series = local_series
            else:
                # capture series data from raw logs and append to local_series
                api_series = self.capture_series_data(raw_logs, date_range)
                for series in api_series["sleep"]:
                    local_series["sleep"].append(series)
                sleep_series = copy.deepcopy(local_series)

                # update sleep_series.json
                with open(self.sleep_series_file_path, 'w') as series_file:
                    json.dump(sleep_series, series_file)

        return sleep_series

    def initialize_csv(self):
        """
        initialize sleep.csv with up-to-date sleep logs
        :return sleep_logs: up-to-date sleep logs
        """

        # request all sleep logs from Fitbit
        date_range = ("2018-08-07", self.today)
        fitbit = Fitbit(self.tokens_file_path)
        raw_logs = fitbit.sleep_logs_range(date_range)

        # capture explicit data from raw logs
        sleep_logs = self.capture_log_data(raw_logs, date_range)
        sleep_logs.to_csv(path_or_buf=self.sleep_file_path, mode='w+', date_format="%Y-%m-%d")

        sleep_logs.index = pd.to_datetime(sleep_logs.index)

        return sleep_logs

    def initialize_json(self):
        """
        initialize sleep_series.json with up-to-date time series
        :return sleep_series: up-to-date sleep_series
        """

        # request all sleep series from Fitbit
        date_range = ("2018-08-07", self.today)
        fitbit = Fitbit(self.tokens_file_path)
        raw_logs = fitbit.sleep_logs_range(date_range)

        # capture explicit data from raw series
        sleep_series = self.capture_series_data(raw_logs, date_range)
        with open(self.sleep_series_file_path, 'w+') as series_file:
            json.dump(sleep_series, series_file)

        return sleep_series

    def capture_log_data(self, sleep_raw_logs, date_range):
        """
        capture explicit data from raw sleep logs
        :param sleep_raw_logs: json object of raw sleep data from Fitbit request
        :param date_range: tuple of (start_date, end_date) form
        :return sleep_logs: dataFrame of explicit sleep data captured from raw logs
        """

        # initialize parameters
        dict_labels = ["dateOfSleep", "minutesAfterWakeup",
                       "minutesToFallAsleep", "startTime"]
        stages_labels = ["deep", "light", "rem", "wake"]
        sleep_logs = []
        frames = []
        start_date = dt.strptime(date_range[0], "%Y-%m-%d")
        end_date = dt.strptime(date_range[1], "%Y-%m-%d")
        num_days = end_date - start_date
        index = 0
        dates = [(end_date - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(0, num_days.days + 1)]

        # create dictionary list to capture explicit data
        for raw_log in sleep_raw_logs["sleep"]:
            sleep_log = dict()
            duration_sleep = 0
            duration_total = 0
            for label in dict_labels:
                sleep_log[label] = [raw_log[label]]
            for label in stages_labels:
                sleep_log[label] = [raw_log["levels"]["summary"][label]["minutes"]]
                duration_total += sleep_log[label][0]
            for label in stages_labels[:-1]:
                duration_sleep += sleep_log[label][0]
            sleep_log["efficiency"] = [round(duration_sleep / duration_total, 2)]
            sleep_log["duration"] = [duration_total]
            sleep_logs.append(sleep_log)

        # append missing data to sleep logs
        for raw_log, date in zip(sleep_raw_logs["sleep"], dates):
            if date == raw_log["dateOfSleep"]:
                index += 1
                continue
            else:
                sleep_log = dict()
                sleep_log["dateOfSleep"] = [date]
                for label in dict_labels[1:]:
                    sleep_log[label] = [float('nan')]
                for label in stages_labels:
                    sleep_log[label] = [float('nan')]
                sleep_log["efficiency"] = [float('nan')]
                sleep_log["duration"] = [float('nan')]
                sleep_logs.insert(index, sleep_log)
                dates.remove(date)
                index += 2

        sleep_logs.reverse()

        # create DataFrame list from dictionary list
        for log in sleep_logs:
            df = pd.DataFrame.from_dict(data=log)
            frames.append(df)

        # concatenate DataFrames and set index
        sleep_logs = pd.concat(frames)
        sleep_logs = sleep_logs.set_index('dateOfSleep')

        return sleep_logs

    def capture_series_data(self, sleep_raw_logs, date_range):
        """
        capture series data from raw sleep logs
        :param sleep_raw_logs: json object of raw sleep data from Fitbit request
        :param date_range: tuple of (start_date, end_date) form
        :return sleep_series: dataFrame of sleep series data captured from raw logs
        """

        # initialize parameters
        start_date = dt.strptime(date_range[0], "%Y-%m-%d")
        end_date = dt.strptime(date_range[1], "%Y-%m-%d")
        num_days = end_date - start_date
        stages = ['deep', 'light', 'rem', 'wake']
        index = 0
        dates = [(end_date - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(0, num_days.days + 1)]
        sleep_series = {"sleep": []}
        series_template = {"dateOfSleep": None,
                           "data": {"deep": {"start_times": [],
                                             "epoch_durations": []},
                                    "light": {"start_times": [],
                                              "epoch_durations": []},
                                    "rem": {"start_times": [],
                                            "epoch_durations": []},
                                    "wake": {"start_times": [],
                                             "epoch_durations": []}},
                           "shortData": {"wake": {"start_times": [],
                                                  "epoch_durations": []}}}

        # create json format dictionary to capture sleep series data
        for raw_log in sleep_raw_logs["sleep"]:
            series = copy.deepcopy(series_template)
            series["dateOfSleep"] = raw_log["dateOfSleep"]
            for epoch in raw_log["levels"]["data"]:
                series["data"][epoch["level"]]["start_times"].append(epoch["dateTime"])
                series["data"][epoch["level"]]["epoch_durations"].append(epoch["seconds"])
            for epoch in raw_log["levels"]["shortData"]:
                series["shortData"][epoch["level"]]["start_times"].append(epoch["dateTime"])
                series["shortData"][epoch["level"]]["epoch_durations"].append(epoch["seconds"])
            sleep_series["sleep"].append(series)

        # append missing data to series
        for raw_log, date in zip(sleep_raw_logs["sleep"], dates):
            if date == raw_log["dateOfSleep"]:
                index += 1
                continue
            else:
                series = copy.deepcopy(series_template)
                series["dateOfSleep"] = date
                for stage in stages:
                    series["data"][stage]["start_times"].append(0)
                    series["data"][stage]["epoch_durations"].append(0)
                series["shortData"]["wake"]["start_times"].append(0)
                series["shortData"]["wake"]["epoch_durations"].append(0)
                sleep_series["sleep"].insert(index, series)
                dates.remove(date)
                index += 2

        sleep_series["sleep"].reverse()
        return sleep_series

    def plot_stages_percent(self, grid_shape, position, rowspan, colspan):
        """
        plot percentages of four sleep stages for each of last 15 days using grouped bar graph
        :param grid_shape: tuple of (row, column) form
        :param position: tuple of (row, column) form
        :param rowspan: integer of row span
        :param colspan: integer of column span
        """

        # initialize graph params
        plt.rc('xtick', labelsize=18)
        plt.rc('ytick', labelsize=18)
        x = self.sleep_logs.index.tolist()[-15:]
        x = date2num(x)
        xmin = self.sleep_logs.index.tolist()[-15]
        xmax = self.sleep_logs.index.tolist()[-1]
        numdays = xmax-xmin
        median_array_shape = (1, len(x))
        xticks = [xmin + timedelta(days=d) for d in range(0, numdays.days+1)]
        bar_width = 0.2
        labelpad = 12.5
        labelfontsize = 20
        dateformat = '%a-%b-%d'
        alpha = 0.3
        medians_color = 'k'
        annotate_height = 0.5
        annotate_fontsize = 18
        annotate_fontweight = 'heavy'
        annotate_align = 'center'
        annotate_color = 'w'

        # initialize y-axis data
        durations = self.sleep_logs.loc[xmin:xmax]['duration'].values
        durations_lifetime = self.sleep_logs['duration'].values

        awake_perc = np.around(self.sleep_logs.loc[xmin:xmax]['wake'].values / durations, 3) * 100
        rem_perc = np.around(self.sleep_logs.loc[xmin:xmax]['rem'].values / durations, 3) * 100
        light_perc = np.around(self.sleep_logs.loc[xmin:xmax]['light'].values / durations, 3) * 100
        deep_perc = np.around(self.sleep_logs.loc[xmin:xmax]['deep'].values / durations, 3) * 100

        # convert nan to 0
        awake_perc = np.nan_to_num(awake_perc)
        rem_perc = np.nan_to_num(rem_perc)
        light_perc = np.nan_to_num(light_perc)
        deep_perc = np.nan_to_num(deep_perc)

        # store percentage values of each sleep stage in array
        awake_perc_lifetime = np.around(self.sleep_logs['wake'].values / durations_lifetime, 3) * 100
        rem_perc_lifetime = np.around(self.sleep_logs['rem'].values / durations_lifetime, 3) * 100
        light_perc_lifetime = np.around(self.sleep_logs['light'].values / durations_lifetime, 3) * 100
        deep_perc_lifetime = np.around(self.sleep_logs['deep'].values / durations_lifetime, 3) * 100

        # compute lifetime medians for each sleep stage
        awake_median = float(np.around(np.nanmedian(awake_perc_lifetime), 3))
        rem_median = float(np.around(np.nanmedian(rem_perc_lifetime), 3))
        light_median = float(np.around(np.nanmedian(light_perc_lifetime), 3))
        deep_median = float(np.around(np.nanmedian(deep_perc_lifetime), 3))

        # create repeating array of medians for each sleep stage
        awake_median_array = np.full(median_array_shape, awake_median)[0]
        rem_median_array = np.full(median_array_shape, rem_median)[0]
        light_median_array = np.full(median_array_shape, light_median)[0]
        deep_median_array = np.full(median_array_shape, deep_median)[0]

        # initialize masks for medians and percentage values
        mask_awake_perc = ma.where(awake_perc>=awake_median_array)
        mask_awake_median = ma.where(awake_median_array>=awake_perc)
        mask_rem_perc = ma.where(rem_perc>=rem_median_array)
        mask_rem_median = ma.where(rem_median_array>=rem_perc)
        mask_light_perc = ma.where(light_perc>=light_median_array)
        mask_light_median = ma.where(light_median_array>=light_perc)
        mask_deep_perc = ma.where(deep_perc>=deep_median_array)
        mask_deep_median = ma.where(deep_median_array>=deep_perc)

        # setup plot
        ax = plt.subplot2grid(grid_shape, position, rowspan=rowspan, colspan=colspan, fig=self.sleep_fig)
        ax.grid(axis='y')
        ax.set_title('Sleep Stage Percentages', fontsize=30, pad=15)
        ax.set_ylabel('Percentage', fontsize=labelfontsize, labelpad=labelpad)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center', rotation_mode='anchor')
        ax.set_xticks(xticks)
        ax.set_yticks(np.arange(0, 110, 5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))

        # annotate bars
        for x_pos, awake_p, rem_p, light_p, deep_p in zip(x, awake_perc, rem_perc, light_perc, deep_perc):
            if awake_p == 0 and rem_p == 0 and light_p == 0 and deep_p == 0:
                ax.text(x_pos, annotate_height, 'nan', fontsize=annotate_fontsize,
                        fontweight='normal', horizontalalignment=annotate_align, color=annotate_color)
            else:
                ax.text(x_pos-0.3, annotate_height, int(round(awake_p, 0)), fontsize=annotate_fontsize,
                        fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)
                ax.text(x_pos-0.1, annotate_height, int(round(rem_p, 0)), fontsize=annotate_fontsize,
                        fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)
                ax.text(x_pos+0.1, annotate_height, int(round(light_p, 0)), fontsize=annotate_fontsize,
                        fontweight=annotate_fontweight, horizontalalignment=annotate_align, color=annotate_color)
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

    def plot_efficiency(self, grid_shape, position, rowspan, colspan):
        """
        plot sleep efficiency for last 15 days using bar graph
        :param grid_shape: tuple of (row, column) form
        :param position: tuple of (row, column) form
        :param rowspan: integer of row span
        :param colspan: integer of column span
        """

        # initialize parameters
        x = self.sleep_logs.index.tolist()[-15:]
        y = np.nan_to_num(self.sleep_logs['efficiency'].values[-15:])
        labelpad = 10
        labelfontsize = 20
        dateformat = "%a-%b-%d"

        # setup plot
        ax = plt.subplot2grid(grid_shape, position, rowspan=rowspan, colspan=colspan, fig=self.sleep_fig)
        ax.grid(axis='y')
        ax.set_title('Sleep Efficiency', fontsize=30, pad=15)
        ax.set_ylabel('Efficiency', fontsize=labelfontsize, labelpad=labelpad)
        ax.set_xticks(x)
        ax.set_ylim(np.nanmin(np.asarray(y)), 1.0)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))

        # annotate bars
        for date, height in zip(x, y):
            if height == 0.0:
                ax.text(date, height+0.02, 'nan', fontsize=18, horizontalalignment='center',
                        fontweight='normal')
            else:
                ax.text(date, height+0.02, height, fontsize=18,
                        fontweight='heavy', horizontalalignment='center')

        ax.bar(x, y, width=0.3)

    def plot_polar_hypnograms(self, grid_shape):
        """
        plot 15 polar hypnograms horizontally
        :param grid_shape: tuple of form (rows, columns)
        """

        # plot hypnograms horizontally
        for series_index, col_index in zip(range(-15, 0), range(0, 15)):
            self.polar_hypnogram(self.sleep_series["sleep"][series_index], grid_shape, (3, col_index))

        # set title
        plt.figtext(0.51, 0.185, "Hypnograms", fontsize=30, horizontalalignment='center')

    def polar_hypnogram(self, sleep_series, grid_shape, position):
        """
        plot single hypnogram
        :param sleep_series: dictionary in json form storing sleep time series
        :param grid_shape: tuple of (rows, columns) form
        :param position: tuple of (row, column) form
        """

        # initialize parameters
        stages = ['deep', 'light', 'rem', 'wake']
        start_times = {}
        epoch_durations = {}
        bar_height = 1
        date_datetime = dt.strptime(sleep_series["dateOfSleep"], "%Y-%m-%d")
        date_str = date_datetime.strftime("%a-%b-%d")
        sleep_logs = self.sleep_logs.copy(deep=True)
        sleep_logs.index = sleep_logs.index.strftime("%Y-%m-%d")
        total_min = sleep_logs.loc[sleep_series["dateOfSleep"]]["duration"]
        if isnan(total_min):
            duration = 'nan'
        else:
            hours = int(total_min/60)
            minutes = int(round((total_min/60 - hours)*60, 2))
            duration = time(hours, minutes).strftime("%H:%M")

        title = date_str

        # convert dateTimes to radians
        for stage in stages:
            start_times[stage] = time2radian(sleep_series['data'][stage]['start_times'])
            epoch_durations[stage] = time2radian(sleep_series['data'][stage]['epoch_durations'])
        start_times["wake"] = start_times["wake"] + time2radian(sleep_series["shortData"]["wake"]["start_times"])
        epoch_durations["wake"] = epoch_durations["wake"] + time2radian(sleep_series["shortData"]["wake"]["epoch_durations"])

        # setup plot
        ax = plt.subplot2grid(grid_shape, position, polar=True, fig=self.sleep_fig)
        ax.barh(0, width=0)
        ax.barh(1, width=0)
        ax.barh(2, left=start_times['wake'], width=epoch_durations['wake'], color='m', label='Awake', height=bar_height)
        ax.barh(4, left=start_times['rem'], width=epoch_durations['rem'], color='c', label='REM', height=bar_height)
        ax.barh(3, left=start_times['light'], width=epoch_durations['light'], color='C0', label='Light', height=bar_height)
        ax.barh(4, left=start_times['deep'], width=epoch_durations['deep'], color='b', label='Deep', height=bar_height)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticks(np.linspace(0, 2 * pi, 24, endpoint=False))
        ax.set_xticklabels(range(0, 24), fontsize=14)
        ax.tick_params(axis='x', which='major', pad=1)
        ax.set_rlabel_position(0)
        ax.set_rgrids([2, 3, 4], labels=["", "", "", ""], color='k',
                      fontsize=12, fontweight='bold', verticalalignment='center')
        ax.set_title(label=title, pad=-180, fontsize=18)
        ax.grid(False)

        # annotate plot
        if duration == 'nan':
            ax.text(0, 0, duration, fontsize=15, fontweight='normal',
                    verticalalignment='top', horizontalalignment='center')
        else:
            ax.text(0, 0, duration, fontsize=15, fontweight='heavy',
                    verticalalignment='top', horizontalalignment='center')


# EXAMPLE using Sleep()
"""
# sleep plots
tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'
sleep_series_fp = '/home/sosa/Documents/IoTHealth/sleep_series.json'

# fig parameters
grid_shape = (4, 15)
eff_plt_pos = (2, 0)
stages_plt_pos = (0, 0)
plt.rcParams.update({'figure.autolayout': True})

# capture sleep data
sleep = Sleep(sleep_logs_fp, sleep_series_fp, tokens_fp)

# set fig shape and show
sleep.plot_stages_percent(grid_shape, stages_plt_pos, rowspan=2, colspan=15)
sleep.plot_efficiency(grid_shape, eff_plt_pos, rowspan=1, colspan=15)
plt.tight_layout()
sleep.plot_polar_hypnograms(grid_shape)

plt.show()
"""

# TODO Dev

"""
    1. Create Sleep() class with attributes:
       DONE a. capture_log_data() returns pandas df
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
       DONE j. create radial (hypnogram) bar plot for each day, with clock y-axis, and plotting bedtime, stages, out-of-bedtime
       DONE k. create fig, capturing plots, using sleep_logs_dataframe
            l. create masks to display lifetime medians of sleep efficiency
            m. center hypnograms by adjusting ax.set_title(label='') and instead using ax.text()
"""

# TODO Dev Future

"""
    1. create sleep_%YYYY-%mm-%dd.csv backup file every month on 1st
        - may be useful to create datetime class variable which updates to current
            date each month and date is posted to filename 

"""
