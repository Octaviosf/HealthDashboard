from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import timedelta
import os
import json

class Sleep(object):
    def __init__(self, sleep_file_path, tokens_file_path):

        # assignments
        self.sleep_file_path = sleep_file_path
        self.tokens_file_path = tokens_file_path
        self.logs_uptodate = False
        self.sleep_logs = self.update_logs()

        """
        if os.path.isfile(sleep_file_path) and os.access(sleep_file_path, os.R_OK):
            self.sleep_logs = pd.read_csv(sleep_file_path)
        else:
            print('"sleep.csv" does not exist')
            self.sleep_logs = self.update_logs()
        """

    def update_logs(self):

        today = dt.today().strftime("%Y-%m-%d")

        if os.path.isfile(self.sleep_file_path) and os.access(self.sleep_file_path, os.R_OK):
            local_logs = pd.read_csv(self.sleep_file_path)

            # test if local_logs are up to date
            latest_date_local = (local_logs.index.max()).strftime("%Y-%m-%d")

            if latest_date_local == today:
                sleep_logs = local_logs
                self.logs_uptodate = True
                print("sleep_logs are up-to-date")
        else:
            date_range = ("2018-08-07", today)

            fitbit = Fitbit(self.tokens_filepath)
            raw_logs = fitbit.sleeplogs_range(date_range)
            # create df from raw_logs
            sleep_logs = self.essentials(raw_logs)
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
            self.logs_uptodate = True

        return sleep_logs






    def essentials(self, sleep_logs_raw):
        """
        Capture data essential for plots

        :param sleep_logs_raw: original sleep data from Fitbit request
        :return: list of sleep logs with essential data
        """

        dict_labels = ["dateOfSleep", "minutesAfterWakeup",
                               "minutesToFallAsleep", "startTime"]

        stages_labels = ["deep", "light", "rem", "wake"]

        sleep_logs = []

        for sleep_raw in sleep_logs_raw:
            sleep_log = {}
            duration_sleep = 0
            duration_total = 0

            for label in dict_labels:
                sleep_log[label] = sleep_raw[label]

            for label in stages_labels:
                sleep_log[label] = sleep_raw["levels"]["summary"][label]["minutes"]
                duration_total += sleep_log[label]

            for label in stages_labels[:-1]:
                duration_sleep += sleep_log[label]

            sleep_log["efficiency"] = round(duration_sleep / duration_total, 2)

            sleep_log["duration"] = duration_total
            sleep_logs.append(sleep_log)

        sleep_logs.reverse()

        return sleep_logs

    # assignments
    tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
    sleep_logs_fp = '/home/sosa/Documents/IoTHealth/sleep_logs_fp.txt'
    date_range = ('2018-08-07', '2018-08-15')

    # create interaction object with Fitbit API
    fitbit = Fitbit(tokens_fp)

    # recieve sleep data
    sleep_logs_raw = fitbit.sleeplogs_range(date_range)['sleep']

    # create Sleep() object
    sleep = Sleep(sleep_logs_fp)

    # capture data for sleep plots
    sleep_logs = sleep.essentials(sleep_logs_raw)

    if os.path.isfile(sleep_logs_fp) and os.access(sleep_logs_fp, os.R_OK):
        with open(sleep_logs_fp, 'r') as sleep_file:
            sleep_logs_local = exec(sleep_file.readline())

        # update sleep_logs_local using fitbit request

    else:
        sleep_logs_raw = fitbit.sleeplogs_range(date_range)['sleep']
        with open(sleep_logs_fp, 'w+') as sleep_file:
            sleep_file.write(sleep_logs_raw)

    print(sleep_plot_data)

    # TODO Dev

    """
        1. Create Sleep() class with attributes:
                a. essentials() returns pandas df
                a. create are_logs_uptodate boolean
                a. write sleep.csv file if nonexistent
                b. update sleep.csv
                c. create sleep_logs_dataframe
                d. create fig, capturing plots, using sleep_logs_dataframe
                etc ...
    """
