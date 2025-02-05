import sys
from glob import glob
import pandas as pd


def summary(category: str):
    csv_files = glob(f'{category}-*.csv')
    print('Menggabungkan', ', '.join(csv_files))
    df_list = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df_list.append(df)
    orig_df = pd.concat(df_list, ignore_index=True)
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
    summary(category)


if __name__ == '__main__':
    main()
