import os
import sys
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title='Cari PC storage')


def get_list(column: str, cast_func=None):
    c = getattr(orig_df, column)
    tmp_df = orig_df[c.notnull()]
    c = getattr(tmp_df, column)
    if cast_func:
        list_ = [cast_func(x) for x in c.drop_duplicates()]
    else:
        list_ = [x for x in c.drop_duplicates()]
    list_.sort()
    if column in DEFAULT:
        index = -1
        for val in list_:
            index += 1
            if val >= DEFAULT[column]:
                break
    else:
        index = 0
    return list_, index


def filter_name(column, label):
    list_, index = get_list(column)
    choice = st.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c == choice]


def filter_min(column: str, label: str, cast_func=None) -> pd.DataFrame:
    list_, index = get_list(column, cast_func)
    choice = st.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c >= choice]


def get_title(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'\
           f'<br/><em>{cols.time}</em>'


def get_is_new(is_new: int, stock: int):
    if not stock:
        return 'HABIS'
    if is_new == 1:
        return 'BARU'
    return 'BEKAS'


def get_price(cols):
    s = '{:0,}'.format(int(cols.price))
    s = s.replace(',', '.')
    s = f'Rp {s}'
    label = get_is_new(cols.is_new, cols.stock)
    if label:
        cls = ['c-label']
        if cols.stock:
            if cols.is_new:
                cls.append('c-label--green')
        else:
            cls.append('c-label--pink')
        cls = ' '.join(cls)
        s += f'<div class="{cls}">{label}</div>'
    return s


def get_capacity(cols):
    if pd.isnull(cols.capacity_gb) or not cols.capacity_gb:
        return ''
    return f'{int(cols.capacity_gb)} GB'


def get_warranty(cols):
    if pd.isnull(cols.warranty_year) or not cols.warranty_year:
        return ''
    return f'{int(cols.warranty_year)} tahun'


def get_pcie(cols):
    if pd.isnull(cols.pcie_version) or not cols.pcie_version:
        return ''
    return f'PCIe {int(cols.pcie_version)}'


def sort_by_label(key):
    return SORT_BY[key]


COLUMNS = ['title', 'price', 'capacity_gb', 'warranty_year', 'pcie_version']
SORT_BY = dict(
        price='Price', capacity_gb='Capacity', warranty_year='Warranty',
        pcie_version='PCIe')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(
        price=True, capacity_gb=False, warranty_year=False, pcie_version=False)
DEFAULT = dict(
        price=5000000, capacity_gb=1000, warranty_year=5, pcie_version=4)

csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
            'storage.csv',
            'http://warga.web.id/files/dijual/storage.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break


@st.cache_data(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()
orig_df = orig_df[orig_df.category == 'storage']
df = orig_df.copy()

st.title('PC Storage')
if st.checkbox('Brand'):
    df = filter_name('brand_name', 'Brand')

if st.checkbox('Minimum capacity'):
    df = filter_min('capacity_gb', 'GB', int)

if st.checkbox('PCIe'):
    df = filter_min('pcie_version', 'Version', int)

if st.checkbox('Minimum warranty'):
    df = filter_min('warranty_year', 'Year', int)

if st.checkbox('Maximum price'):
    step = 500000
    tmp_df = orig_df[orig_df.stock > 0]
    min_ = int(tmp_df.price.min() / step + 1) * step
    max_ = int(tmp_df.price.max() / step + 1) * step
    choice = st.slider('Rp', min_, max_, DEFAULT['price'], step)
    df = df[df.price <= choice]

if st.checkbox('New'):
    df = df[df.is_new == 1]

if st.checkbox('Stock'):
    df = df[df.stock > 1]

choice = st.selectbox(
        'Sort by', options=SORT_BY_KEYS, format_func=sort_by_label)
if choice != 'price':
    c = getattr(df, choice)
    df = df[c.notnull()]
df = df.sort_values(by=[choice], ascending=[ASC[choice]])

count = len(df)
if count:
    df = df.replace(np.nan, '', regex=True)
    tmp_df = df[COLUMNS].copy()
    tmp_df['title'] = df.apply(get_title, axis='columns')
    tmp_df['price'] = df.apply(get_price, axis='columns')
    tmp_df['capacity_gb'] = df.apply(get_capacity, axis='columns')
    tmp_df['pcie_version'] = df.apply(get_pcie, axis='columns')
    tmp_df['warranty_year'] = df.apply(get_warranty, axis='columns')
    st.write(f'Found {count} rows')
    css = '''
    <style>
    .block-container {max-width: 100rem}
    th {display: none}
    td {vertical-align: top}
    .c-label {
        height: 18px;
        padding: 1px 6px;
        margin: 0;
        overflow: visible;
        line-height: 14px;
        vertical-align: middle;
        background-color: #fafafa;
        border: 1px solid #ddd;
        border-radius: 2px;
    }
    .c-label--pink {
        background-color: #ff566a;
    }
    .c-label--green {
        background-color: #3cff33;
    }
    </style>'''
    st.markdown(css, unsafe_allow_html=True)
    st.write(tmp_df.to_html(escape=False), unsafe_allow_html=True)
else:
    st.write('No result')
