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


def power_value(cols):
    if pd.isnull(cols.power_watt):
        return ''
    return f'{int(cols.power_watt)} Watt'


csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
            'psu.csv',
            'http://warga.web.id/files/dijual/psu.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break

COLUMNS = [
    'brand_name', 'title', 'price', 'is_new', 'time', 'stock', 'description',
    'power_watt', 'model_name']

SORT_BY = dict(price='Price', power_watt='Watt')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(price=True, power_watt=False)

DEFAULT = dict(price=100000, power=1000, model='Platinum')

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
orig_df = orig_df[orig_df.category == 'psu']

df = orig_df[orig_df.brand_name.notnull()]
brand_list = [x for x in df.brand_name.drop_duplicates()]
brand_list.sort()

df = orig_df[orig_df.power_watt.notnull()]
df = df[df.power_watt > 0]
power_list = [int(x) for x in df.power_watt.drop_duplicates()]
power_index = default_index('power')

df = orig_df[orig_df.model_name.notnull()]
model_list = [x for x in df.model_name.drop_duplicates()]
model_index = default_index('model')

price_step = 500000
price_min = int(orig_df.price.min() / price_step + 1) * price_step
price_max = int(orig_df.price.max() / price_step + 1) * price_step

df = orig_df[COLUMNS].copy()
df['title'] = orig_df.apply(clickable, axis='columns')
df.insert(3, 'price_rp', orig_df.apply(price_value, axis='columns'))
df.insert(9, 'power', orig_df.apply(power_value, axis='columns'))
df = df.sort_values(by=['price'])

# Kolom
# 1 nomor, 2 brand_name, 3 title, 4 price, 5 price_rp, 6 is_new, 7 time,
# 8 stock, 9 description, 10 power_watt, 11 power, 12 model_name

# Sembunyikan nomor, dan lainnya yang tidak nyaman
hide_columns = [2, 4, 6, 7, 8, 9, 10]
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

st.title('PSU Finder')
if st.checkbox('Brand'):
    choice = st.selectbox('Brand', brand_list)
    df = df[df.brand_name == choice]
if st.checkbox('Minimum power'):
    choice = st.selectbox('Watt', power_list, index=power_index)
    df = df[df.power_watt >= choice]
if st.checkbox('Model'):
    choice = st.selectbox('Name', model_list, index=model_index)
    df = df[df.model_name == choice]
if st.checkbox('Maximum price'):
    choice = st.slider(
        'Rp', price_min, price_max, DEFAULT['price'], price_step)
    df = df[df.price <= choice]
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
