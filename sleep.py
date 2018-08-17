from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import timedelta

class Sleep(object):
    def __init__(self, sleep_file_path):

        # assignments
        self.dict_labels = ["dateOfSleep", "minutesAfterWakeup",
                               "minutesToFallAsleep", "startTime"]

        self.stages_labels = ["deep", "light", "rem", "wake"]

        self.sleep_logs = None

        self.sleep_file_path = sleep_file_path

    def essentials(self, sleep_logs_raw):
        """
        Capture data essential for plots

        :param sleep_logs_raw: original sleep data from Fitbit request
        :return: list of sleep logs with essential data
        """

        sleep_logs = []

        for sleep_raw in sleep_logs_raw:
            sleep_log = {}
            duration_sleep = 0
            duration_total = 0

            for label in self.dict_labels:
                sleep_log[label] = sleep_raw[label]

            for label in self.stages_labels:
                sleep_log[label] = sleep_raw["levels"]["summary"][label]["minutes"]
                duration_total += sleep_log[label]

            for label in self.stages_labels[:-1]:
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
                a. write sleep.txt file if nonexistent
                b. update sleep.txt
                c. create sleep_logs_dataframe
                d. create fig, capturing plots, using sleep_logs_dataframe
                etc ...
    """
