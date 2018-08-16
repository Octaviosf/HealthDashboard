from IoTHealth.fitbit import Fitbit

# assignments
file_path = '/home/sosa/Documents/IoTHealth/fitbit_tokens.txt'
date_range = ('2018-08-07', '2018-08-15')

# create instance for Fitbit API interaction
fitbit = Fitbit(file_path)

# request sleep data, capture response, and print response
sleep_data = fitbit.sleeplogs_range(date_range)
print('\n'+str(sleep_data))
