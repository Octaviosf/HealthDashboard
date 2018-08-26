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


def time2radian(time_list):
    """
    :param time_list: list of date_times or seconds strings
    :return: list of radians
    """
    minutes_per_day = 24*60
    seconds_per_day = 24*60*60

    radians = []

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
    Interact with sleep logs:
        - request sleep logs
        - update sleep logs
        - create sleep.csv
        - capture explicit data from raw sleep logs
    """
    def __init__(self, sleep_file_path, sleep_series_file_path, tokens_file_path):
        """
        create and/or update sleep.csv
        capture sleep_logs using instance variable

        :param sleep_file_path: absolute file-path to sleep.csv
        :param tokens_file_path: absolute file-path to fitbit_tokens.txt
        """

        # assignments
        self.sleep_file_path = sleep_file_path
        self.sleep_series_file_path = sleep_series_file_path
        self.tokens_file_path = tokens_file_path
        self.today = dt.today().strftime("%Y-%m-%d")

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
        :return sleep_series:  up-to-date sleep series
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

        :param sleep_raw_logs: raw sleep data from Fitbit request
        :return sleep_logs: explicit sleep data captured from raw logs
        """

        # assignments
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

        for raw_log, date in zip(sleep_raw_logs["sleep"], dates):
            if date == raw_log["dateOfSleep"]:
                index += 1
                continue
            else:
                sleep_log = dict()
                sleep_log["dateOfSleep"] = [date]
                for label in dict_labels[1:]:
                    sleep_log[label] = [None]
                for label in stages_labels:
                    sleep_log[label] = [0]
                sleep_log["efficiency"] = [0]
                sleep_log["duration"] = [0]
                sleep_logs.insert(index, sleep_log)
                dates.remove(date)
                index += 1

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

        :param sleep_raw_logs: raw sleep data from Fitbit request
        :param date_range: tuple of a start and end date, respectively
        :return sleep_series: sleep series data captured from raw logs
        """

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
                index += 1

        """
        for raw_log, date in zip(sleep_raw_logs["sleep"], dates):
            series = copy.deepcopy(series_template)
            print("'date' == 'raw_log['dateOfSleep']:", date + ' == ' + raw_log["dateOfSleep"])
            if date == raw_log["dateOfSleep"]:
                series["dateOfSleep"] = raw_log["dateOfSleep"]
                for epoch in raw_log["levels"]["data"]:
                    series["data"][epoch["level"]]["start_times"].append(epoch["dateTime"])
                    series["data"][epoch["level"]]["epoch_durations"].append(epoch["seconds"])
                for epoch in raw_log["levels"]["shortData"]:
                    series["shortData"][epoch["level"]]["start_times"].append(epoch["dateTime"])
                    series["shortData"][epoch["level"]]["epoch_durations"].append(epoch["seconds"])
                sleep_series["sleep"].append(series)
            else:
                series["dateOfSleep"] = date
                for stage in stages:
                    series["data"][stage]["start_times"].append(0)
                    series["data"][stage]["epoch_durations"].append(0)
                series["shortData"]["wake"]["start_times"].append(0)
                series["shortData"]["wake"]["epoch_durations"].append(0)
                sleep_series["sleep"].append(series)

                series_next = copy.deepcopy(series_template)
                series_next["dateOfSleep"] = raw_log["dateOfSleep"]
                for epoch in raw_log["levels"]["data"]:
                    series_next["data"][epoch["level"]]["start_times"].append(epoch["dateTime"])
                    series_next["data"][epoch["level"]]["epoch_durations"].append(epoch["seconds"])
                for epoch in raw_log["levels"]["shortData"]:
                    series_next["shortData"][epoch["level"]]["start_times"].append(epoch["dateTime"])
                    series_next["shortData"][epoch["level"]]["epoch_durations"].append(epoch["seconds"])
                sleep_series["sleep"].append(series_next)
        """

        sleep_series["sleep"].reverse()
        return sleep_series

    def plot_efficiency(self, grid_shape, position, rowspan, colspan):
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
        x = self.sleep_logs.index.tolist()[-7:]
        y = self.sleep_logs['efficiency'].tolist()[-7:]
        xmin = self.sleep_logs.index.tolist()[0] - timedelta(days=1)
        xmax = self.sleep_logs.index.tolist()[-1] + timedelta(days=1)
        labelpad = 25
        labelfontsize = 20
        dateformat = "%a-%b-%d"

        # set parameters
        ax = plt.subplot2grid(grid_shape, position, rowspan=rowspan, colspan=colspan)
        ax.grid()
        ax.set_title('Sleep Efficiency', fontsize=30, pad=30)
        ax.set_ylabel('Efficiency', fontsize=labelfontsize, labelpad=labelpad)
        #ax.set_xlim(xmin, xmax)
        ax.set_ylim(min(y) - 0.1, 1.0)
        #ax.set_yticks(np.arange(0, 1.1, 0.1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))

        # annotate bars
        for date, height in zip(x, y):
            ax.text(date, height+0.02, height, fontsize=18,
                    fontweight='bold', horizontalalignment='center')

        ax.bar(x, y, edgecolor='k', width=0.2, linewidth=1.5)

        plt.tight_layout()

        return plt

    def plot_stages_percent(self, grid_shape, position, rowspan, colspan):

        # initialize graph params
        plt.rc('xtick', labelsize=18)
        plt.rc('ytick', labelsize=18)
        x = self.sleep_logs.index.tolist()[-7:]
        x = date2num(x)
        xmin = self.sleep_logs.index.tolist()[-7]
        xmax = self.sleep_logs.index.tolist()[-1]
        numdays = xmax-xmin
        median_array_shape = (1, len(x))
        xticks = [xmin + timedelta(days=d) for d in range(0, numdays.days+1)]
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

        # initialize y-axis data
        durations = self.sleep_logs.loc[xmin:xmax]['duration'].values
        durations_lifetime = self.sleep_logs['duration'].values
        awake_perc = np.around(self.sleep_logs.loc[xmin:xmax]['wake'].values / durations, 3) * 100
        rem_perc = np.around(self.sleep_logs.loc[xmin:xmax]['rem'].values / durations, 3) * 100
        light_perc = np.around(self.sleep_logs.loc[xmin:xmax]['light'].values / durations, 3) * 100
        deep_perc = np.around(self.sleep_logs.loc[xmin:xmax]['deep'].values / durations, 3) * 100

        awake_perc_lifetime = np.around(self.sleep_logs['wake'].values / durations_lifetime, 3) * 100
        rem_perc_lifetime = np.around(self.sleep_logs['rem'].values / durations_lifetime, 3) * 100
        light_perc_lifetime = np.around(self.sleep_logs['light'].values / durations_lifetime, 3) * 100
        deep_perc_lifetime = np.around(self.sleep_logs['deep'].values / durations_lifetime, 3) * 100

        awake_median = float(np.around(np.median(awake_perc_lifetime), 3))
        rem_median = float(np.around(np.median(rem_perc_lifetime), 3))
        light_median = float(np.around(np.median(light_perc_lifetime), 3))
        deep_median = float(np.around(np.median(deep_perc_lifetime), 3))

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
        ax = plt.subplot2grid(grid_shape, position, rowspan=rowspan, colspan=colspan)
        ax.grid()
        ax.set_title('Sleep Stage Percentage', fontsize=30, pad=30)
        ax.set_ylabel('Percentage %', fontsize=labelfontsize, labelpad=labelpad)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation = 0, ha='center', rotation_mode='anchor')
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
        """
        # TODO self.sleep_series is initialized from local sleep_series.json and/or from Fitbit response

        :param shape:
        :return:
        """

        #today = dt.strptime(self.today, "%Y-%m-%d")
        #days = [today - timedelta(days=d) for d in range(0, 7)].reverse()

        """
        for index in range(-8, -2):
            initial_day = dt.strptime(self.sleep_series["sleep"][index]["dateOfSleep"], "%Y-%m-%d")
            next_day = dt.strptime(self.sleep_series["sleep"][index+1]["dateOfSleep"], "%Y-%m-%d")

            num_blank_plots = next_day - initial_day + 1
            blank_plots = plot_blank_hypnogram(num_blank_plots)
        """


        plt0 = self.polar_hypnogram(self.sleep_series["sleep"][-8], shape, (3,0))
        plt1 = self.polar_hypnogram(self.sleep_series["sleep"][-7], shape, (3,1))
        plt2 = self.polar_hypnogram(self.sleep_series["sleep"][-6], shape, (3,2))
        plt3 = self.polar_hypnogram(self.sleep_series["sleep"][-5], shape, (3,3))
        plt4 = self.polar_hypnogram(self.sleep_series["sleep"][-4], shape, (3,4))
        plt5 = self.polar_hypnogram(self.sleep_series["sleep"][-3], shape, (3,5))
        plt6 = self.polar_hypnogram(self.sleep_series["sleep"][-2], shape, (3,6))
        plt7 = self.polar_hypnogram(self.sleep_series["sleep"][-1], shape, (3,7))

        plots = [plt0, plt1, plt2, plt3, plt4, plt5, plt6, plt7]

        plt.figtext(0.49, 0.225, "Polar Hypnograms", fontsize=30, horizontalalignment='center')

        return plots

    def polar_hypnogram(self, sleep_series, shape, position):
        """
        :param sleep_series: dictionary storing 'data' and 'shortData' for specific day ['dateOFSleep']
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
        start_times = {}
        epoch_durations = {}
        bar_height = 1
        date_datetime = dt.strptime(sleep_series["dateOfSleep"], "%Y-%m-%d")
        date_str = date_datetime.strftime("%a-%b-%d")
        sleep_logs = self.sleep_logs.copy(deep=True)
        sleep_logs.index = sleep_logs.index.strftime("%Y-%m-%d")
        total_min = sleep_logs.loc[sleep_series["dateOfSleep"]]["duration"]
        hours = int(total_min/60)
        minutes = int(round((total_min/60 - hours)*60, 2))
        duration = time(hours, minutes).strftime("%H:%M")

        title = date_str

        for stage in stages:
            start_times[stage] = time2radian(sleep_series['data'][stage]['start_times'])
            epoch_durations[stage] = time2radian(sleep_series['data'][stage]['epoch_durations'])

        start_times["wake"] = start_times["wake"] + \
                              time2radian(sleep_series["shortData"]["wake"]["start_times"])

        epoch_durations["wake"] = epoch_durations["wake"] + \
                                  time2radian(sleep_series["shortData"]["wake"]["epoch_durations"])


        ax = plt.subplot2grid(shape, position, polar=True)
        ax.barh(0, width=0)
        ax.barh(1, width=0)
        #ax.barh(2, width=0)
        ax.barh(2, left=start_times['wake'], width=epoch_durations['wake'], color='m', label='Awake', height=bar_height)
        ax.barh(4, left=start_times['rem'], width=epoch_durations['rem'], color='c', label='REM', height=bar_height)
        ax.barh(3, left=start_times['light'], width=epoch_durations['light'], color='C0', label='Light', height=bar_height)
        ax.barh(4, left=start_times['deep'], width=epoch_durations['deep'], color='b', label='Deep', height=bar_height)
        # ax.barh(2, left=median_start, width=median_duration, color='k', alpha=0.3, label='Median', height=bar_height)

        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticks(np.linspace(0, 2 * pi, 24, endpoint=False))
        ax.set_xticklabels(range(0, 24))

        ax.set_rlabel_position(0)
        ax.set_rgrids([2, 3, 4], labels=["", "", "", ""], color='k',
                      fontsize=12, fontweight='bold', verticalalignment='center')
        ax.set_title(label=title, pad=-265, fontsize=18)
        ax.set_xlabel(xlabel=duration, labelpad=-138.5, fontsize=18)
        plt.tight_layout()

        # plt.legend(loc='upper right')

        ax.grid(False)

        return plt


# assignments
tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'
sleep_series_fp = '/home/sosa/Documents/IoTHealth/sleep_series.json'

# fig parameters
grid_shape = (4, 8)
eff_plt_pos = (2, 0)
stages_plt_pos = (0, 0)

# capture sleep data
sleep = Sleep(sleep_logs_fp, sleep_series_fp, tokens_fp)
#print(sleep.sleep_series["sleep"][0])

"""
with pd.option_context("display.max_rows", 11, "display.max_columns", 10):
    print(sleep.sleep_logs)
"""

# set fig shape and show
plt.figure(figsize=(30,20))
stages_plot = sleep.plot_stages_percent(grid_shape, stages_plt_pos, rowspan=2, colspan=8)
efficiency_plot = sleep.plot_efficiency(grid_shape, eff_plt_pos, rowspan=1, colspan=8)
polar_hypnograms = sleep.plot_polar_hypnograms(grid_shape)
stages_plot.show()
efficiency_plot.show()
for plt in polar_hypnograms:
    plt.show()


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
