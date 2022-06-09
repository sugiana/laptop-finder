import sys
import pandas as pd


csv_file = sys.argv[1]

valid_vals = [
    ('brand', ['acer', 'apple', 'asus', 'dell', 'hp', 'lenovo', 'msi']),
    ('processor', [
        'alder lake', 'amd', 'apple m1', 'comet lake', 'core i', 'i7', 'intel',
        'ryzen', 'tiger lake']),
    ('graphic', [
        'amd', 'core gpu', 'geforce', 'intel', 'iris', 'nvidia', 'radeon',
        'rtx', 'uhd']),
    ]
dict_valid_vals = dict(valid_vals)

orig_df = pd.read_csv(csv_file)

for key, ref_vals in valid_vals:
    for index, row in orig_df.iterrows():
        found = False
        for ref_val in ref_vals:
            if isinstance(row[key], float):
                continue
            if row[key].lower().find(ref_val) > -1:
                found = True
                break
        if not found:
            print(f'{key} {row[key]} tidak dikenal, {row["url"]}')

for brand in dict_valid_vals['brand']:
    df = orig_df[orig_df.brand.str.contains(brand, na=False, case=False)]
    if not len(df[df.weight_kg.notnull()]):
        for index, row in df.iterrows():
            print(row['url'])
            break
        print(f'Semua brand {brand} tidak ada weight')
        break
