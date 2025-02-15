import sys
from argparse import ArgumentParser
import pandas as pd
from tools import read_conf


help_boolean = 'lebih dari satu pisahkan dengan koma'
help_filter = 'contoh: stock >= 1'

pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--csv-file')
pars.add_argument('--filter', help=help_filter)
option = pars.parse_args(sys.argv[1:])

cf = read_conf(option.conf)

orig_df = pd.read_csv(option.csv_file)
orig_df = orig_df[orig_df.category == cf['category']]
if option.filter:
    orig_df = orig_df.query(option.filter)

columns = ['url', 'title'] + list(cf['columns']) + \
          ['is_new', 'stock', 'time', 'ai_duration']
for index, row in orig_df.iterrows():
    print(f'#{index}')
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

# Group by
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
    df = orig_df[field.notnull()]
    field = getattr(df, column)
    min_ = field.min()
    max_ = field.max()
    if column in cf.get('numeric_columns', []):
        print(f'{column}: {min_:,} - {max_:,}')
    else:
        print(f'{column}: {min_} - {max_}')
