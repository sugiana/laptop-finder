import sys
import pandas as pd


csv_file = sys.argv[1]
df = pd.read_csv(csv_file)

print(len(df), 'produk')

columns = ['shop_name', 'is_new']
for column in columns:
    field = getattr(df, column)
    tmp_df = df[field.notnull()]
    field = getattr(tmp_df, column)
    tmp_list = [x for x in field.drop_duplicates()]
    print(column, tmp_list)

tmp_list = df.url.drop_duplicates()
print(len(tmp_list))
