from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
            df = df.set_index("dateOfSleep")
            frames.append(df)

        # concatenate DataFrames
        sleep_logs = pd.concat(frames)

        return sleep_logs

    def plot(self):

        # global plot format
        fig = plt.figure(figsize=(17,12), dpi=100)
        plt.rc("xtick", labelsize=18)
        plt.rc("ytick", labelsize=18)

        # parameter init
        x = self.sleep_logs.index
        xmin = self.sleep_logs.index.tolist()[0] - timedelta(days=1)



        return fig

# assignments
tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'

# capture sleep data
sleep = Sleep(sleep_logs_fp, tokens_fp)

with pd.option_context("display.max_rows", 11, "display.max_columns", 10):
    print(sleep.sleep_logs)

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
            h. create fig, capturing plots, using sleep_logs_dataframe
            etc ...
"""

# TODO Dev Future

"""
    1. create sleep_%YYYY-%mm-%dd.csv backup file every month on 1st
        - may be useful to create datetime class variable which updates to current
            date each month and date is posted to filename 

"""
