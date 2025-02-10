import sys
import os
from glob import glob
import pandas as pd


def summary(orig_df: pd.DataFrame):
    count = orig_df.groupby('category').size()
    df = count.reset_index()
    for index, row in df.iterrows():
        name, count = row.values
        print(f'{name} = {count} unit')
    count = len(orig_df)
    detik = orig_df.ai_duration.sum()
    detik_produk = detik / count
    jam = detik / 3600
    print(format(jam, '.2f'), 'jam /', count, 'produk')
    print(format(detik_produk, '.2f'), 'detik / produk')


def main(argv=sys.argv[1:]):
    category = argv[0]
    if os.path.exists(category):
        df = pd.read_csv(category)
    else:
        csv_files = glob(f'{category}-*.csv')
        print('Menggabungkan', ', '.join(csv_files))
        df_list = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
    summary(df)


if __name__ == '__main__':
    main()
