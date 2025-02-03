import sys
import os
import json
from argparse import ArgumentParser
from time import time
from ollama import Client
import pandas as pd
import requests
from tools import sanitize_json_str


ROLE = 'Kamu adalah seorang yang pendiam. Jawabanmu selalu singkat dan '\
        'tanpa asesoris kata seperti tambahan 2 karakter bintang ( ** ) '\
        'untuk menebalkan, dan sejenisnya.'
SYSTEM_ROLE = dict(role='system', content=ROLE)

PROMPTS = dict(
    laptop=dict(
        template='''\
Berikut ini diduga spesifikasi laptop.

{desc}

Jawab pertanyaan berikut dalam bentuk JSON sesuai nomor urut.

1. Apakah ini sebuah laptop ? Jawab "ya" atau "bukan".

Jika "ya" maka lanjut jawab ini:

2. Apa mereknya ? Satu kata saja.
3. Kalimat mana yang menunjukkan processor ? Singkat saja.
4. Apa brand prosesornya ? Satu kata saja.
5. Kalimat mana yang menunjukkan graphic adapter ? Singkat saja.
6. Memori graphic adapter berapa gigabyte ? Tampilkan angka saja.
7. Apa brand graphic adaptor-nya ? Satu kata saja.
8. Kalimat mana yang menunjukkan kapasitas memori ? Singkat saja.
9. Memori berapa gigabyte ? Tampilkan angka saja.
10. Kalimat mana yang menunjukkan kapasitas storage ? Singkat saja.
11. Storage berapa gigabyte ? Tampilkan angka saja.
12. Kalimat mana yang menunjukkan ukuran monitor ? Singkat saja.
13. Monitornya berapa inchi ? Tampilkan angka saja.
14. Kalimat mana yang menunjukkan berat ? Singkat saja.
15. Beratnya berapa kilogram ? Sebut angka saja.''',
        columns=[
            'category', 'brand', 'processor', 'processor_brand', 'graphic',
            'graphic_gb', 'graphic_brand', 'memory', 'memory_gb', 'storage',
            'storage_gb', 'monitor', 'monitor_inch', 'weight', 'weight_kg']),
    hp=dict(
        template='''\
Berikut ini diduga spesifikasi handphone.

{desc}

Jawab pertanyaan berikut dalam bentuk JSON sesuai nomor urut.

1. Apakah ini sebuah handphone ? Jawab "ya" atau "bukan".

Jika "ya" maka lanjut jawab ini:

2. Apa mereknya ? Satu kata saja.
3. Kalimat mana yang menunjukkan CPU ? Singkat saja.
4. Apa brand prosesornya ? Satu kata saja.
5. Kalimat mana yang menunjukkan graphic adapter ? Singkat saja.
6. Apa brand graphic adaptor-nya ? Satu kata saja.
7. Kalimat mana yang menunjukkan RAM ? Singkat saja.
8. RAM berapa gigabyte ? Tampilkan angka saja.
9. Kalimat mana yang menunjukkan kapasitas storage ? Singkat saja.
10. Storage berapa gigabyte ? Tampilkan angka saja.
11. Kalimat mana yang menunjukkan ukuran monitor ? Singkat saja.
12. Monitornya berapa inchi ? Tampilkan angka saja.
13. Kalimat mana yang menunjukkan jenis USB ?
14. Apakah ada USB type-C ? Jawab "ya, ada" atau "tidak ada".
15. Kalimat mana yang menunjukkan sensor kompas ?
16. Kalimat mana yang menunjukkan kapasitas baterai ?
17. Baterainya berapa mAh ? Tampilkan angka saja.
18. Apakah ada NFC ? Jawab "ya, ada" atau "tidak ada".
19. Apakah ada dukungan terhadap network 5G ? Jawab "ya, ada" atau "tidak ada".
20. Kalimat mana yang menunjukkan berat ? Singkat saja.
21. Beratnya berapa kilogram ? Sebut angka saja.''',
        columns=[
            'category', 'brand', 'processor', 'processor_brand', 'graphic',
            'graphic_brand', 'memory', 'memory_gb', 'storage', 'storage_gb',
            'monitor', 'monitor_inch', 'usb', 'usb_c', 'compass', 'battery',
            'battery_mah', 'nfc', 'network_5g', 'weight', 'weight_kg']))


class HttpErr(Exception):
    pass


def ask(prompt: str, ai_info: dict) -> str:
    print(prompt)
    if 'gemini' in ai_info:
        url = ai_info['gemini']['url'] + '?key=' + ai_info['gemini']['key']
        d = dict(contents=[dict(parts=[dict(text=prompt)])])
        r = requests.post(url, json=d)
        if r.status_code != 200:
            raise HttpErr(r.status_code, r.text)
        d = r.json()
        s = d['candidates'][0]['content']['parts'][0]['text']
        s = s.rstrip()
    else:
        d = dict(role='user', content=prompt)
        messages = [SYSTEM_ROLE, d]
        c = Client(host=ai_info['ollama']['url'])
        r = c.chat(model=ai_info['ollama']['model'], messages=messages)
        s = r['message']['content'].rstrip()
    print(s)
    return s


def parse(
        category: str, input_file: str, output_file: str, ai_info=dict(),
        limit=None):
    input_df = pd.read_csv(input_file)
    if limit:
        input_df = input_df[:limit]
    if os.path.exists(output_file):
        output_df = pd.read_csv(output_file)
    else:
        output_df = None
    is_first = True
    input_df = input_df.sort_values(by='url')
    for index, values in input_df.iterrows():
        if output_df is not None:
            cache_df = output_df[output_df.url == values['url']]
            if not cache_df.empty:
                continue
        data = dict()
        for column in list(input_df.columns):
            data[column] = values[column]
        print(values['url'])
        desc = '\n\n'.join([values['title'], values['description']])
        prompt = PROMPTS[category]['template'].format(desc=desc)
        awal = time()
        s = ask(prompt, ai_info)
        durasi = time() - awal
        data['ai_duration'] = durasi
        if durasi > 0.009:
            print(format(durasi, '.2f'), 'detik')
        d = sanitize_json_str(s)
        columns = PROMPTS[category]['columns']
        for index, column in enumerate(columns):
            key = str(index+1)
            if key not in d:
                break
            data[column] = d[key]
        if data['category'].lower().find('ya') == 0:
            data['category'] = category
        else:
            data['category'] = 'lainnya'
        data = {key: [data[key]] for key in data}
        df = pd.DataFrame(data)
        if output_df is not None or not is_first:
            # Tambahkan
            df.to_csv(output_file, index=False, mode='a', header=False)
        elif is_first:
            # Buat file baru
            df.to_csv(output_file, index=False)
            is_first = False
    print(f'Sudah disimpan di {output_file}')


def main(arg=sys.argv[1:]):
    categories = ['laptop', 'hp']
    category = categories[0]
    help_category = f'default: {category}'

    input_file = 'tokopedia.csv'
    help_input = f'default {input_file}'

    output_file = 'laptop.csv'
    help_output = f'default {output_file}'

    help_limit = 'Jumlah produk yang diproses, isi dengan 5 untuk uji coba'

    ollama_url = 'http://localhost:11434'
    help_ollama = f'default {ollama_url}'

    model = 'gemma2'
    help_model = f'default {model}'

    help_gemini = 'contoh: https://generativelanguage.googleapis.com/v1beta/'\
                  'models/gemini-1.5-flash:generateContent'
    help_key = 'bisa file'

    pars = ArgumentParser()
    pars.add_argument(
        '--category', default=category, help=help_category, choices=categories)
    pars.add_argument('--input-file', default=input_file, help=help_input)
    pars.add_argument('--output-file', default=output_file, help=help_output)
    pars.add_argument('--limit', type=int, help=help_limit)
    pars.add_argument('--ollama-url', default=ollama_url, help=help_ollama)
    pars.add_argument('--model', default=model, help=help_model)
    pars.add_argument('--gemini-url', help=help_gemini)
    pars.add_argument('--key', help=help_key)
    option = pars.parse_args(sys.argv[1:])

    ai_info = dict()
    if option.gemini_url:
        if option.key:
            if os.path.exists(option.key):
                with open(option.key) as f:
                    key = f.read()
            else:
                key = option.key
            ai_info['gemini'] = dict(url=option.gemini_url, key=key)
        else:
            print('--key harus diisi')
            sys.exit(1)
    else:
        ai_info['ollama'] = dict(url=option.ollama_url, model=option.model)
    parse(
        option.category, option.input_file, option.output_file, ai_info,
        option.limit)


if __name__ == '__main__':
    main()
