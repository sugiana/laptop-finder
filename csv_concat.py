import sys
import os
from glob import glob
import pandas as pd


output = sys.argv[1]
if os.path.exists(output):
    os.remove(output)
csv_files = glob('*.csv')
df_list = [pd.read_csv(x) for x in csv_files]
df = pd.concat(df_list, ignore_index=True)
df.to_csv(output)
