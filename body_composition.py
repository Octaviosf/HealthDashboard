# down-sample data by day
# convert values to numeric or nan
df = df.apply(pd.to_numeric, errors='coerce')

# capture all columns except index column and convert
cols = df.columns.difference([index_label])
df[cols] = df[cols].astype(float)





