import sys
import os
from glob import glob
import pandas as pd


def concat(category: str):
    csv_files = glob(f'{category}-*.csv')
    all_df = pd.DataFrame()
    for csv_file in csv_files:
        print('Gabung file', csv_file)
        df = pd.read_csv(csv_file)
        df = df[df.category == category]
        all_df = pd.concat([all_df, df], ignore_index=True)
    output = f'{category}.csv'
    if os.path.exists(output):
        os.remove(output)
    all_df.to_csv(output, index=False)
    print('Tersimpan di', output)


def concat_columns(categories: list):
    all_df = pd.DataFrame()
    for category in categories:
        csv_file = f'{category}.csv'
        if not os.path.exists(csv_file):
            continue
        print('Gabung file', csv_file)
        df = pd.read_csv(csv_file)
        all_df = pd.concat([all_df, df], ignore_index=True)
    if os.path.exists('all.csv'):
        os.remove('all.csv')
    all_df.to_csv('all.csv', index=False)
    print('Tersimpan di all.csv')


def main(argv=sys.argv[1:]):
    if argv[1:]:
        concat_columns(argv)
    else:
        concat(argv[0])


if __name__ == '__main__':
    main()
