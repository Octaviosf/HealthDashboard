from IoTHealth.google_sheet import GoogleSheet
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


class BodyComposition(object):

    def __init__(self, spreadsheet_id, sheet_range, labels, index, index_type):

        self.sheet = GoogleSheet(spreadsheet_id, sheet_range)
        df = self.sheet.sheet2df(labels, index, index_type)

        # format df
        df = df.apply(pd.to_numeric, errors='coerce')
        cols = df.columns.difference([index])
        df[cols] = df[cols].astype(float)

        # down sample data using mean
        df = df.resample('d').mean().dropna(how='all')
        df[cols] = df[cols].round(decimals=2)

        self.df = df


spreadsheet_id = '136gvJHeQOirtmTendXnpb19Pa96Tit7Hkt8RR3N2pEI'
sheet_range = 'Sheet1'
col_labels = ['date_time', 'weight_lb', 'fat_%', 'water_%', 'bone_lb',
              'muscle_lb', 'BMI', 'fat_lb', 'bone_%', 'muscle_%']
index = 'date_time'
index_type = 'datetime64[ns]'

body = BodyComposition(spreadsheet_id, sheet_range, col_labels, index, index_type)

print(body.df)

# TODO Future Dev
"""
    1. create csv from df
    2. update csv when new data available
"""
