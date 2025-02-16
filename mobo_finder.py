import os
import sys
import numpy as np
import pandas as pd
import streamlit as st


def clickable(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'\
           f'<br/><em>{cols.time}</em>'


def is_new_value(is_new: int, stock: int):
    if not stock:
        return 'HABIS'
    if is_new == 1:
        return 'BARU'
    return 'BEKAS'


def price_value(cols):
    s = '{:0,}'.format(int(cols.price))
    s = s.replace(',', '.')
    s = f'Rp {s}'
    label = is_new_value(cols.is_new, cols.stock)
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


csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
            'mobo.csv',
            'http://warga.web.id/files/dijual/mobo.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break

COLUMNS = [
    'brand', 'title', 'price', 'is_new', 'time', 'stock', 'description',
    'pcie_x16', 'pcie_x16_count', 'pcie_x16_version']

SORT_BY = dict(
    price='Price',
    pcie_x16_count='PCIe x16')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(price=True, pcie_x16_count=False)

DEFAULT = dict(price=5000000, pcie_x16_count=4, pcie_x16_version=4)

MAIN = sys.modules[__name__]


def default_index(name):
    index = 0
    vals = getattr(MAIN, f'{name}_list')
    vals.sort()
    for val in vals:
        if val >= DEFAULT[name]:
            break
        index += 1
    return index


def sort_by_label(key):
    return SORT_BY[key]


@st.cache_data(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()
orig_df = orig_df[orig_df.category == 'mobo']

brand_list = [x for x in orig_df.brand.drop_duplicates()]
brand_list.sort()

df = orig_df[orig_df.pcie_x16_count.notnull()]
df = df[df.pcie_x16_count > 0]
pcie_x16_count_list = [int(x) for x in df.pcie_x16_count.drop_duplicates()]
pcie_x16_count_index = default_index('pcie_x16_count')

df = orig_df[orig_df.pcie_x16_version.notnull()]
df = df[df.pcie_x16_version > 0]
pcie_x16_version_list = [int(x) for x in df.pcie_x16_version.drop_duplicates()]
pcie_x16_version_index = default_index('pcie_x16_version')

price_step = 500000
price_min = int(orig_df.price.min() / price_step + 1) * price_step
price_max = int(orig_df.price.max() / price_step + 1) * price_step

df = orig_df[COLUMNS].copy()
df['title'] = orig_df.apply(clickable, axis='columns')
df.insert(3, 'price_rp', orig_df.apply(price_value, axis='columns'))
df = df.sort_values(by=['price'])

# Kolom
# 1 nomor, 2 brand, 3 title, 4 price, 5 price_rp, 6 is_new, 7 time, 8 stock,
# 9 description, 10 pcie_x16, 11 pcie_x16_count, 12 pcie_x16_version

# Sembunyikan nomor, dan lainnya yang tidak nyaman
hide_columns = [2, 4, 6, 7, 8, 9, 11, 12]
css = """
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
    """
for column in hide_columns:
    css += f'\n    tr>:nth-child({column})' + '{display: none}'
css += '\n</style>'
st.markdown(css, unsafe_allow_html=True)

st.title('Motherboard Finder')
if st.checkbox('Brand'):
    brand_choice = st.selectbox('Brand', brand_list)
    df = df[df.brand == brand_choice]
if st.checkbox('PCIe x16 count'):
    pcie_x16_count_choice = st.selectbox(
        'Amount', pcie_x16_count_list, index=pcie_x16_count_index)
    df = df[df.pcie_x16_count >= pcie_x16_count_choice]
if st.checkbox('PCIe x16 version'):
    pcie_x16_version_choice = st.selectbox(
        'Number', pcie_x16_version_list, index=pcie_x16_version_index)
    df = df[df.pcie_x16_version >= pcie_x16_version_choice]
if st.checkbox('Maximum price'):
    price_choice = st.slider(
            'Rp', price_min, price_max, DEFAULT['price'], price_step)
    df = df[df.price <= price_choice]
if st.checkbox('New'):
    df = df[df.is_new == 1]
if st.checkbox('Stock'):
    df = df[df.stock > 0]
sort_by = st.selectbox(
            'Sort by', options=SORT_BY_KEYS, format_func=sort_by_label)
df = df.sort_values(by=[sort_by], ascending=[ASC[sort_by]])
df = df.replace(np.nan, '', regex=True)
st.write(f'Found {len(df)} rows')
st.write(
    df.to_html(escape=False), unsafe_allow_html=True)
