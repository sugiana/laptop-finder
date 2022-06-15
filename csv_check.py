import os
import sys
import numpy as np
import pandas as pd
import laptop_parser
import hp_parser


csv_file = sys.argv[1]

filename = os.path.split(csv_file)[-1]
category = os.path.splitext(filename)[0].split('-')[0]

good_keys = dict(
    laptop=['processor', 'graphic', 'memory', 'storage', 'monitor'],
    hp=['processor', 'memory', 'storage', 'battery'])
good_keys = good_keys[category] + ['url']

valid_vals = dict(
    laptop=[
        ('brand', [x.lower() for x in laptop_parser.Parser.BRANDS]),
        ('processor', laptop_parser.Parser.VALID_VALUES['processor']),
        ('graphic', [
            'amd', 'core gpu', 'geforce', 'intel', 'iris', 'nvidia', 'radeon',
            'rtx', 'uhd']),
        ],
    hp=[
        ('brand', [x.lower() for x in hp_parser.Parser.BRANDS]),
        ('processor', hp_parser.Parser.VALID_VALUES['processor']),
        ('graphic', ['adreno', 'powervr']),
        ])
valid_vals = valid_vals[category]
dict_valid_vals = dict(valid_vals)

orig_df = pd.read_csv(csv_file)

df = orig_df[list(good_keys)].copy()
for key in good_keys:
    for index, row in df.iterrows():
        if pd.isna(row[key]):
            print(dict(row))
            print(f'{key} tidak ada')

for key, ref_vals in valid_vals:
    df = orig_df[orig_df[key].notnull()]
    for index, row in df.iterrows():
        found = False
        for ref_val in ref_vals:
            if isinstance(row[key], float):
                continue
            if row[key].lower().find(ref_val) > -1:
                found = True
                break
        if not found:
            print(f'{key} {row[key]} tidak dikenal, {row["url"]}')

brand_list = [x for x in orig_df.brand.drop_duplicates()]
for brand in brand_list:
    df = orig_df[orig_df.brand.str.contains(brand, na=False, case=False)]
    for key in good_keys:
        if not len(df[df[key].notnull()]):
            for index, row in df.iterrows():
                print(row['url'])
                break
            print(f'Semua brand {brand} tidak ada {key}')
