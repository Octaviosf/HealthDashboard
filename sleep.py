from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import timedelta
import os
import pandas as pd
from pprint import pprint

class Sleep(object):
    def __init__(self, sleep_file_path, tokens_file_path):

        # assignments
        self.sleep_file_path = sleep_file_path
        self.tokens_file_path = tokens_file_path
        self.logs_uptodate = False
        self.sleep_logs = self.update_logs()

    def update_logs(self):

        today = dt.today().strftime("%Y-%m-%d")

        if os.path.isfile(self.sleep_file_path) and os.access(self.sleep_file_path, os.R_OK):
            local_logs = pd.read_csv(self.sleep_file_path)

            # test if local_logs are up to date
            print("local_logs.index.max():", local_logs.index.max())
            latest_date_local = (local_logs.index.max()).strftime("%Y-%m-%d")

            if latest_date_local == today:
                sleep_logs = local_logs
                self.logs_uptodate = True
                print("sleep_logs are up-to-date")
        else:
            # create .csv file
            date_range = ("2018-08-07", today)

            fitbit = Fitbit(self.tokens_file_path)
            raw_logs = fitbit.sleeplogs_range(date_range)

            # create df from raw_logs using essentials()
            sleep_logs = self.essentials(raw_logs)
            sleep_logs.to_csv(path_or_buf=self.sleep_file_path, mode='w+', date_format="%Y-%m-%d")

            self.logs_uptodate = True

        if not self.logs_uptodate:
            latest_date_local = dt.strptime(latest_date_local, "%Y-%m-%d")
            next_date_local = (latest_date_local + timedelta(days=1)).strftime("%Y-%m-%d")

            date_range = (next_date_local, today)

            fitbit = Fitbit(self.tokens_file_path)
            raw_logs = fitbit.sleeplogs_range(date_range)
            api_logs = self.essentials(raw_logs)

            frames = [local_logs, api_logs]
            sleep_logs = pd.concat(frames)

            # overwrite .csv file
            sleep_logs.to_csv(path_or_buf=self.sleep_file_path, mode='w')
            self.logs_uptodate = True

        return sleep_logs

    def essentials(self, sleep_logs_raw):
        """
        Capture data essential for plots

        :param sleep_logs_raw: original sleep data from Fitbit request
        :return: DataFrame of sleep logs with essential data
        """

        dict_labels = ["dateOfSleep", "minutesAfterWakeup",
                       "minutesToFallAsleep", "startTime"]

        stages_labels = ["deep", "light", "rem", "wake"]

        sleep_logs = []
        frames = []

        # create list of sleep logs
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

        # create list of DateFrames
        for log in sleep_logs:
            df = pd.DataFrame.from_dict(data=log)
            df = df.set_index("dateOfSleep")
            frames.append(df)

        # concatenate DataFrames
        sleep_logs = pd.concat(frames)

        return sleep_logs


# assignments
tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep.csv'

# recieve sleep data
sleep = Sleep(sleep_logs_fp, tokens_fp)

print("type(sleep.sleep_logs):", type(sleep.sleep_logs))
with pd.option_context("display.max_rows", 10, "display.max_columns", 9):
    print(sleep.sleep_logs)

# TODO Dev

"""
    1. Create Sleep() class with attributes:
       DONE a. essentials() returns pandas df
       DONE a. create are_logs_uptodate boolean
       DONE a. write sleep.csv file if nonexistent
       DONE b. update sleep.csv
       DONE c. create sleep_logs_dataframe
            d. create fig, capturing plots, using sleep_logs_dataframe
            etc ...
"""
