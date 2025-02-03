import sys
import pandas as pd


csv_file = sys.argv[1]
orig_df = pd.read_csv(csv_file)

columns = ['category', 'url', 'title', 'price', 'brand', 'processor',
           'processor_brand', 'graphic', 'graphic_brand', 'graphic_gb',
           'memory', 'memory_gb', 'storage', 'storage_gb', 'monitor',
           'monitor_inch', 'weight', 'weight_kg']
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

orig_df = orig_df[orig_df.category == 'laptop']
print('RINGKASAN LAPTOP')

columns = ['brand', 'processor_brand', 'graphic_brand', 'memory_gb',
           'storage_gb', 'monitor_inch', 'is_new']
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
columns = ['stock']
for column in columns:
    field = getattr(orig_df, column)
    df = orig_df[field > 0]
    count = len(df)
    print(f'{column} = {count} unit')
