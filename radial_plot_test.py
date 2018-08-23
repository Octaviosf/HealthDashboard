import matplotlib.pyplot as plt
import numpy as np
from numpy import pi
from datetime import datetime as dt


def time2radian(time_list):
    """
    :param time_list: list of datetime.datetime or datetime.time
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


start_times = ['2018-08-19T00:00:00.000', '2018-08-19T03:00:00.000', '2018-08-19T06:00:00.000']
end_times = [7200, 3600, 37800]

median_start = [dt.strptime(string[:10]+' '+string[11:],
                            '%Y-%m-%d %H:%M:%S.%f') for string in ['2018-08-19T03:00:00.000']]
median_start = time2radian(median_start)
median_duration = time2radian([28800])

start_times = [dt.strptime(string[:10]+' '+string[11:], '%Y-%m-%d %H:%M:%S.%f') for string in start_times]
start_times = time2radian(start_times)
end_times = time2radian(end_times)
bar_height = 1

ax = plt.subplot2grid((1,3), (0,1), polar=True)

ax.barh(0, width=0)
ax.barh(1, width=0)
ax.barh(2, left=median_start, width=median_duration, color = 'k', alpha=0.3, label = 'Median', height=bar_height)
ax.barh(6, left=start_times, width=end_times, color='m', label='Awake', height=bar_height)
ax.barh(5, left=start_times, width=end_times, color='c', label='REM', height=bar_height)
ax.barh(4, left=start_times, width=end_times, color='C0', label='Light', height=bar_height)
ax.barh(3, left=start_times, width =end_times, color='b', label='Deep', height=bar_height)

ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_xticks(np.linspace(0, 2*pi, 24, endpoint=False))
ax.set_xticklabels(range(0, 24))

ax.set_rlabel_position(0)
ax.set_rgrids([2, 3, 4, 5, 6], labels=['Med', 'Deep', 'Light', 'REM', 'Awake'], color='k',
              fontsize=12, fontweight='bold', verticalalignment='center')

# plt.legend(loc='upper right')

ax.grid(axis='x')

plt.show()
