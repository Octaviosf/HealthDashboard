from IoTHealth.google_sheet import GoogleSheet
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


class BodyComposition(object):

    def __init__(self, spreadsheet_id, sheet_range, labels, index, index_type):

        self.sheet = GoogleSheet(spreadsheet_id, sheet_range)
        self.df = self.sheet.sheet2df(labels, index, index_type)

        # down-sample data by day
        # convert values to numeric or nan
        self.df = self.df.apply(pd.to_numeric, errors='coerce')

        # capture all columns except index column and convert
        cols = self.df.columns.difference([index])
        self.df[cols] = self.df[cols].astype(float)



# TODO Future Dev
"""
    1. create csv from df
    2. update csv when new data available
"""
