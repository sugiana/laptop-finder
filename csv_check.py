import sys
from argparse import ArgumentParser
import pandas as pd


pars = ArgumentParser()
pars.add_argument("csv_file")
pars.add_argument("--filter")
option = pars.parse_args(sys.argv[1:])

df = pd.read_csv(option.csv_file)
if option.filter:
    print("Filter", option.filter)
    df = df.query(option.filter)

for index, row in df.iterrows():
    no = index + 1
    print(f"#{no}")
    for column in df.columns:
        val = row[column]
        print(f"  {column}: {[val]}")
