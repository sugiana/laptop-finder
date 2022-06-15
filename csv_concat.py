import sys
import os
from glob import glob
import pandas as pd


category = sys.argv[1]
output = f'{category}-all.csv'
if os.path.exists(output):
    os.remove(output)
csv_files = glob(f'{category}*csv')
df_list = [pd.read_csv(x) for x in csv_files]
df = pd.concat(df_list, ignore_index=True)
df.to_csv(output)
