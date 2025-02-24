import sys
import re
from argparse import ArgumentParser
import pandas as pd
from jaccard_index.jaccard import jaccard_index
from tools import read_conf


C_ALPHABET_PATTERN = re.compile('[a-z]')
MIN_J_INDEX = 0.3


def j_index(a: str, b: str) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0
    if C_ALPHABET_PATTERN.search(b):
        return jaccard_index(a, b)
    return 0


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
        if pd.isnull(value) or isinstance(value, str) and \
                value.lower().find('tidak') > -1:
            data['category'] = 'lainnya'


# Nama awal sebagai bekal Jaccard Index
names = dict()


def clean_name(data: dict, column: str, nice_names: list, back_ref=dict()):
    if pd.isnull(data[column]):
        return
    data[column] = nice_str(data[column], nice_names)
    for key, value in back_ref.items():
        if data[column].lower().find(key.lower()) > -1:
            data[column] = value
            return
    if column not in names:
        names[column] = [data[column]]
        return
    best_index = 0
    for name in names[column]:
        index = j_index(name.lower(), data[column].lower())
        if index < MIN_J_INDEX:
            continue
        if best_index > index:
            continue
        best_index = index
        best_name = name
    if best_index:
        data[column] = best_name
    else:
        names[column].append(data[column])


OTHERS = ('tidak', 'unknown', 'none', 'lainnya', '-')


def clean_names(data: dict, cf: dict):
    for column, items in cf.get('names', {}).items():
        keys, alias = items
        value = data[column]
        if value and not pd.isnull(value):
            is_unknown = False
            for other in OTHERS:
                if value.lower().find(other) > -1:
                    data[column] = None
                    is_unknown = True
                    break
            if not is_unknown:
                data[column] = value.strip().replace('.', '')
        clean_name(data, column, keys, alias)


def clean_str(data: dict):
    for column, value in data.items():
        if isinstance(value, str):
            value = value.strip()
            if not value:
                data[column] = None


def clean_numeric(data: dict, cf: dict):
    def clean_orig_column():
        orig_column = '_'.join(column.split('_')[:-1])
        if orig_column in data:
            data[orig_column] = None

    for column in cf.get('numeric_columns', []):
        if pd.isnull(data[column]) or not data[column]:
            clean_orig_column()
        else:
            try:
                data[column] = float(data[column])
            except ValueError:
                data[column] = None
                clean_orig_column()


def clean_range_value(data: dict, cf: dict):
    for column in cf.get('range_values', []):
        if data[column] is None:
            continue
        min_, max_ = cf['range_values'][column]
        if min_ <= data[column] <= max_:
            continue
        data[column] = None


NEGATIVE_BOOLEAN = ['tidak', 'no']


def clean_boolean(data: dict):
    def update_if_false():
        for word in value.lower().split():
            for ref in NEGATIVE_BOOLEAN:
                if word.find(ref) > -1:
                    data[column] = None
                    return

    for column, value in data.items():
        if column.find('is_') != 0:
            continue
        if pd.isnull(value):
            continue
        if not isinstance(value, str):
            continue
        value = value.strip()
        if not value:
            data[column] = None
            continue
        update_if_false()


def repair(cf, csv_file):
    df = pd.read_csv(csv_file)
    rows = dict()
    for column in df.columns:
        rows[column] = []
    for index, row in df.iterrows():
        data = dict(row)
        clean_str(data)
        clean_category(data, cf)
        clean_names(data, cf)
        clean_numeric(data, cf)
        clean_range_value(data, cf)
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
