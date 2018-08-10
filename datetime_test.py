import datetime

yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
#print(type(yesterday), yesterday.strftime('%Y-%m-%d'))
#.strftime("%Y-%m-%d")

yesterday = yesterday.strftime('%Y-%m-%d')
#yest_str = datetime.strptime(datetime.datetime.now() - datetime.timedelta(days=1), '%Y-%m-%d')
print(yesterday)

