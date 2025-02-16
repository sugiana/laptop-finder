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


def memory_value(cols):
    if pd.isnull(cols.memory_gb):
        return ''
    return f'{int(cols.memory_gb)} GB'


def pcie_value(cols):
    if pd.isnull(cols.pcie_version):
        return ''
    return f'PCIe {int(cols.pcie_version)}'


csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
            'gpu.csv',
            'http://warga.web.id/files/dijual/gpu.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break

COLUMNS = [
    'brand', 'title', 'price', 'is_new', 'time', 'stock', 'description',
    'processor_brand', 'processor_type', 'memory_gb', 'pcie_version']

SORT_BY = dict(price='Price', memory_gb='Memory', pcie_version='PCIe')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(price=True, memory_gb=False, pcie_version=False)

DEFAULT = dict(price=5000000, memory=8, pcie=4, processor='NVIDIA')

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
orig_df = orig_df[orig_df.category == 'gpu']

df = orig_df[orig_df.brand.notnull()]
brand_list = [x for x in df.brand.drop_duplicates()]
brand_list.sort()

df = orig_df[orig_df.processor_brand.notnull()]
processor_list = [x for x in df.processor_brand.drop_duplicates()]
processor_list.sort()
processor_index = default_index('processor')

df = orig_df[orig_df.memory_gb.notnull()]
df = df[df.memory_gb > 0]
memory_list = [int(x) for x in df.memory_gb.drop_duplicates()]
memory_index = default_index('memory')

df = orig_df[orig_df.pcie_version.notnull()]
pcie_list = [int(x) for x in df.pcie_version.drop_duplicates()]
pcie_index = default_index('pcie')

price_step = 500000
price_min = int(orig_df.price.min() / price_step + 1) * price_step
price_max = int(orig_df.price.max() / price_step + 1) * price_step

df = orig_df[COLUMNS].copy()
df['title'] = orig_df.apply(clickable, axis='columns')
df.insert(3, 'price_rp', orig_df.apply(price_value, axis='columns'))
df.insert(11, 'memory', orig_df.apply(memory_value, axis='columns'))
df.insert(13, 'pcie', orig_df.apply(pcie_value, axis='columns'))
df = df.sort_values(by=['price'])

# Kolom
# 1 nomor, 2 brand, 3 title, 4 price, 5 price_rp, 6 is_new, 7 time, 8 stock,
# 9 description, 10 processor_brand, 11 processor_type, 12 memory_gb,
# 13 memory, 14 pcie_version, 15 pcie

# Sembunyikan nomor, dan lainnya yang tidak nyaman
hide_columns = [2, 4, 6, 7, 8, 9, 12, 14]
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

st.title('GPU Finder')
if st.checkbox('Brand'):
    brand_choice = st.selectbox('Brand', brand_list)
    df = df[df.brand == brand_choice]
if st.checkbox('Processor brand'):
    processor_brand_choice = st.selectbox(
        'Brand', processor_list, index=processor_index)
    df = df[df.processor_brand == processor_brand_choice]
if st.checkbox('Processor type'):
    proc_type = st.text_input('Any text')
    df = df[df.processor_type.str.contains(proc_type, na=False, case=False)]
if st.checkbox('Minimum memory'):
    memory_choice = st.selectbox('GB', memory_list, index=memory_index)
    df = df[df.memory_gb >= memory_choice]
if st.checkbox('PCIe'):
    pcie_choice = st.selectbox('Version', pcie_list, index=pcie_index)
    df = df[df.pcie_version >= pcie_choice]
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
