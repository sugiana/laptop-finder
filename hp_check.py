import sys
from argparse import ArgumentParser
import pandas as pd


pars = ArgumentParser()
pars.add_argument('csv_file')
pars.add_argument('--url')
option = pars.parse_args(sys.argv[1:])

orig_df = pd.read_csv(option.csv_file)
orig_df = orig_df[orig_df.category == 'hp']
if option.url:
    orig_df = orig_df[orig_df.url == option.url]

columns = ['category', 'url', 'title', 'price', 'brand', 'processor',
           'processor_brand', 'graphic', 'graphic_brand', 'memory',
           'memory_gb', 'storage', 'storage_gb', 'monitor', 'monitor_inch',
           'usb', 'usb_c', 'nfc', 'compass', 'network_5g', 'battery',
           'battery_mah', 'weight', 'weight_kg', 'stock', 'ai_duration']
for index, row in orig_df.iterrows():
    print(f'#{index+1}')
    for column in columns:
        value = row[column]
        print(f'{column}: {value}')
    print()


print('RINGKASAN KATEGORI')
count = orig_df.groupby('category').size()
df = count.reset_index()
for index, row in df.iterrows():
    name, count = row.values
    print(f'{name} = {count} unit')
print()

orig_df = orig_df[orig_df.category == 'hp']
print('RINGKASAN HP')

columns = ['brand', 'processor_brand', 'graphic_brand', 'memory_gb',
           'storage_gb', 'is_new', 'battery_mah']

for column in columns:
    field = getattr(orig_df, column)
    df = orig_df[field.notnull()]
    field = getattr(df, column)
    count = df.groupby(column).size()
    df = count.reset_index()
    print(column)
    for index, row in df.iterrows():
        name, count = row.values
        count = int(count)
        print(f'  {name} = {count} unit')

# Boolean
columns = ['nfc', 'network_5g', 'stock']

for column in columns:
    field = getattr(orig_df, column)
    df = orig_df[field > 0]
    count = len(df)
    print(f'{column} = {count} unit')

# Boolean str
columns = ['usb_c', 'compass']

for column in columns:
    field = getattr(orig_df, column)
    df = orig_df[field.notnull()]
    count = len(df)
    print(f'{column} = {count} unit')

# Min & Max
columns = ['weight_kg', 'price']

for column in columns:
    field = getattr(orig_df, column)
    df = orig_df[field > 0]
    min_ = field.min()
    max_ = field.max()
    print(f'{column}: {min_:,} - {max_:,}')
