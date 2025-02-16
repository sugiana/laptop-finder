import sys
from argparse import ArgumentParser
import pandas as pd
from tools import read_conf


def nice_str(s: str, ref: list):
    lower_ref = [x.lower() for x in ref]
    lower_s = s.lower()
    if lower_s in lower_ref:
        index = lower_ref.index(lower_s)
        return ref[index]
    return s


def clean_category(data: dict, cf: dict):
    if data['category'] != cf['category']:
        return
    for column in cf.get('not_null_columns', []):
        value = data[column]
        if pd.isnull(value) or value.lower().find('tidak') > -1:
            data['category'] = 'lainnya'


def clean_data(data: dict, column: str, nice_names: list, back_ref=dict()):
    if pd.isnull(data[column]):
        return
    data[column] = nice_str(data[column], nice_names)
    for key, value in back_ref.items():
        if data[column].lower().find(key.lower()) > -1:
            data[column] = value


def clean_brands(data: dict, cf: dict):
    for column, items in cf.get('brands', {}).items():
        keys, alias = items
        value = data[column]
        if value and not pd.isnull(value):
            if value.lower().find('tidak') > -1:
                s = 'lainnya'
            else:
                s = value.strip().replace('.', '')
            data[column] = s
        clean_data(data, column, keys, alias)


def clean_str(data: dict):
    for column, value in data.items():
        if isinstance(value, str):
            value = value.strip()
            if not value:
                data[column] = None


def clean_numeric(data: dict, cf: dict):
    for column in cf.get('numeric_columns', []):
        if data[column] is None:
            continue
        try:
            float(data[column])
        except ValueError:
            data[column] = None


NEGATIVE_BOOLEAN = ['tidak', 'no']


def clean_boolean(data: dict):
    for column, value in data.items():
        if column.find('is_') != 0:
            continue
        if pd.isnull(value):
            continue
        if not isinstance(value, str):
            continue
        for word in value.lower().split():
            for ref in NEGATIVE_BOOLEAN:
                if word.find(ref) > -1:
                    data[column] = None


def repair(cf, csv_file):
    df = pd.read_csv(csv_file)
    rows = dict()
    for column in df.columns:
        rows[column] = []
    for index, row in df.iterrows():
        data = dict(row)
        clean_str(data)
        clean_category(data, cf)
        clean_brands(data, cf)
        clean_numeric(data, cf)
        clean_boolean(data)
        for column in df.columns:
            value = data[column]
            rows[column].append(value)
    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False)


def main(argv=sys.argv[1:]):
    pars = ArgumentParser()
    pars.add_argument('conf')
    pars.add_argument('--csv-file', required=True)
    option = pars.parse_args(argv)
    cf = read_conf(option.conf)
    repair(cf, option.csv_file)


if __name__ == '__main__':
    main()
