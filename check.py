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
df = orig_df[orig_df.category == cf['category']]
if option.filter:
    df = df.query(option.filter)

columns = ['url', 'title'] + list(cf['columns']) + \
          ['is_new', 'stock', 'time', 'ai_duration']
for index, row in df.iterrows():
    print(f'#{index}')
    for column in columns:
        value = row[column]
        print(f'{column}: {[value]}')
    print()

print('RINGKASAN')
df = df[df.stock > 0]
count = len(df)
print(f'stock = {count} unit')

# Boolean
for column in df.columns:
    if column.find('is_') != 0:
        continue
    field = getattr(df, column)
    tmp_df = df[field.notnull()]
    count = len(tmp_df)
    print(f'{column} = {count} unit')

# Group by
count = orig_df.groupby('category').size()
tmp_df = count.reset_index()
print('category')
for index, row in tmp_df.iterrows():
    name, count = row.values
    count = int(count)
    print(f'  {name} = {count} unit')

for column in cf.get('count_columns', []):
    field = getattr(df, column)
    tmp_df = df[field.notnull()]
    count = tmp_df.groupby(column).size()
    tmp_df = count.reset_index()
    print(column)
    for index, row in tmp_df.iterrows():
        name, count = row.values
        count = int(count)
        print(f'  {name} = {count} unit')

# Min & Max
for column in cf.get('min_max_columns', []):
    field = getattr(df, column)
    tmp_df = df[field.notnull()]
    field = getattr(tmp_df, column)
    min_ = field.min()
    max_ = field.max()
    if column in cf.get('numeric_columns', []) or column == 'price':
        print(f'Column {column}: {[min_]}')
        print(f'{column}: {min_:,} - {max_:,}')
    else:
        print(f'{column}: {min_} - {max_}')
