from IoTHealth.fitbit import Fitbit
from datetime import datetime as dt
from datetime import timedelta

class Sleep(object):
    def __init__(self, sleep_file_path):

        # assignments
        self.dict_labels = ["dateOfSleep", "minutesAfterWakeup",
                               "minutesToFallAsleep", "startTime"]

        self.stages_labels = ["deep", "light", "rem", "wake"]

        self.sleep_data = None

    def essentials(self, sleep_data):
        """
        Capture data essential for plots

        :param sleep_data: original sleep data from Fitbit request
        :return: list of sleep logs with essential data
        """

        sleep_data_list = []

        for sleep in sleep_data:
            sleep_essentials = {}
            duration_sleep = 0
            duration_total = 0

            for label in self.dict_labels:
                sleep_essentials[label] = sleep[label]

            for label in self.stages_labels:
                sleep_essentials[label] = sleep["levels"]["summary"][label]["minutes"]
                duration_total += sleep_essentials[label]

            for label in self.stages_labels[:-1]:
                duration_sleep += sleep_essentials[label]

            sleep_essentials["efficiency"] = round(duration_sleep / duration_total, 2)

            sleep_essentials["duration"] = duration_total
            sleep_data_list.append(sleep_essentials)

        sleep_data_list.reverse()
        sleep_data = sleep_data_list

        return sleep_data

    # assignments
    tokens_fp = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
    sleep_data_fp = '/home/sosa/Documents/IoTHealth/sleep_data_fp.txt'
    date_range = ('2018-08-07', '2018-08-15')

    # create interaction object with Fitbit API
    fitbit = Fitbit(tokens_fp)

    # recieve sleep data
    sleep_data = fitbit.sleeplogs_range(date_range)['sleep']

    # capture data for sleep plots
    sleep_plot_data = sleep_data_essentials(sleep_data)

    if os.path.isfile(sleep_data_fp) and os.access(sleep_data_fp, os.R_OK):
        with open(sleep_data_fp, 'r') as sleep_file:
            sleep_data_local = exec(sleep_file.readline())

        # update sleep_data_local using fitbit request

    else:
        sleep_data = fitbit.sleeplogs_range(date_range)['sleep']
        with open(sleep_data_fp, 'w+') as sleep_file:
            sleep_file.write(sleep_data)

    print(sleep_plot_data)

    # TODO Dev

    """
        1. Create Sleep() class with attributes:
                a. write sleep.txt file if nonexistent
                b. update sleep.txt
                c. create sleep_data_dataframe
                d. create fig, capturing plots, using sleep_data_dataframe
                etc ...
    """
