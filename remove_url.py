import sys
from argparse import ArgumentParser
from pprint import pprint
import pandas as pd


pars = ArgumentParser()
pars.add_argument('--csv-file', required=True)
pars.add_argument('--url', required=True)
option = pars.parse_args(sys.argv[1:])

orig_df = pd.read_csv(option.csv_file)

df = orig_df[orig_df.url == option.url]
if df.empty:
    print('Tidak ada')
    sys.exit()
d = dict(df.iloc[0])
pprint(d)

df = orig_df[orig_df.url != option.url]
df.to_csv(option.csv_file, index=False)

print(option.url, 'sudah dihapus')
