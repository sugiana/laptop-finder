import sys
import os
from glob import glob
import pandas as pd


def concat(category: str):
    output = f'{category}.csv'
    if os.path.exists(output):
        os.remove(output)
    csv_files = glob(f'{category}-*.csv')
    print('Menggabungkan', ', '.join(csv_files))
    df_list = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df = df[df.category == category]
        df_list.append(df)
    df = pd.concat(df_list, ignore_index=True)
    df.to_csv(output, index=False)
    print('Tersimpan di', output)


def main(argv=sys.argv[1:]):
    category = argv[0]
    concat(category)


if __name__ == '__main__':
    main()
