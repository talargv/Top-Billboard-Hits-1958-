import pandas as pd


class UnexpectedFormatException(Exception):
    def __init__(self):
        super().__init__('Unsupported format')


title_format = 'hits_data_{year}.csv'
cols = ['Top ten entry date', 'Single', 'Artist(s)', 'Peak', 'Peak date', 'Weeks in top ten']
master_df = []
#   rename columns

for y in range(1958, 2024):
    df = pd.read_csv(title_format.format(year=y))

    if df.shape[1] < 6:
        raise UnexpectedFormatException
    if df.shape[1] == 7:
        col_name = list(df.columns)[-1]
        df.drop(col_name, axis=1, inplace=True)

    master_df.extend(df.values.tolist())

output = pd.DataFrame(master_df, columns=cols)
output.to_csv('hits_data.csv')