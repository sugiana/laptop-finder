import sys
from argparse import ArgumentParser
import pandas as pd
from tools import read_conf


help_boolean = 'lebih dari satu pisahkan dengan koma'

pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--csv-file')
pars.add_argument('--filter-url')
pars.add_argument('--filter-boolean', help=help_boolean)
option = pars.parse_args(sys.argv[1:])

cf = read_conf(option.conf)

orig_df = pd.read_csv(option.csv_file)
orig_df = orig_df[orig_df.category == cf['category']]
if option.filter_url:
    orig_df = orig_df[orig_df.url == option.filter_url]
if option.filter_boolean:
    for column in option.filter_boolean.split(','):
        field = getattr(orig_df, column)
        orig_df = orig_df[field.notnull()]

columns = ['url', 'title'] + list(cf['columns']) + \
          ['stock', 'time', 'ai_duration']
for index, row in orig_df.iterrows():
    print(f'#{index+1}')
    for column in columns:
        value = row[column]
        print(f'{column}: {[value]}')
    print()

print('RINGKASAN')
orig_df = orig_df[orig_df.category == cf['category']]
orig_df = orig_df[orig_df.stock > 0]
count = len(orig_df)
print(f'stock = {count} unit')

# Boolean
for column in orig_df.columns:
    if column.find('is_') != 0:
        continue
    field = getattr(orig_df, column)
    df = orig_df[field.notnull()]
    count = len(df)
    print(f'{column} = {count} unit')

for column in cf.get('count_columns', []):
    field = getattr(orig_df, column)
    df = orig_df[field.notnull()]
    count = df.groupby(column).size()
    df = count.reset_index()
    print(column)
    for index, row in df.iterrows():
        name, count = row.values
        count = int(count)
        print(f'  {name} = {count} unit')

# Min & Max
for column in cf.get('min_max_columns', []):
    field = getattr(orig_df, column)
    df = orig_df[field > 0]
    field = getattr(df, column)
    min_ = field.min()
    max_ = field.max()
    print(f'{column}: {min_:,} - {max_:,}')
