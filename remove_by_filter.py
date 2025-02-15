import sys
from argparse import ArgumentParser
from pprint import pprint
import pandas as pd


pars = ArgumentParser()
pars.add_argument('--csv-file', required=True)
pars.add_argument('--filter', required=True)
option = pars.parse_args(sys.argv[1:])

orig_df = pd.read_csv(option.csv_file)
del_df = orig_df.query(option.filter)
if del_df.empty:
    print('Tidak ada')
    sys.exit()

for index, values in del_df.iterrows():
    d = dict(values)
    pprint(d)
    df = orig_df[orig_df.url != d['url']]
    df.to_csv(option.csv_file, index=False)
    print(d['url'], 'sudah dihapus')
