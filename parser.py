import os
import re
import json
from time import time
from html.parser import HTMLParser
from parsel import Selector
import pandas as pd


class BaseError(Exception):
    pass


class UrlNotFound(BaseError):
    pass


class DescriptionNotFound(BaseError):
    pass


class HttpErr(Exception):
    pass


class HTML2Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []

    def handle_data(self, data):
        s = data.strip()
        if s:
            s = ' '.join(s.split())
            self.lines.append(s)


class BaseProductParser:
    def __init__(self, html):
        self.sel = Selector(html)
        self.data = dict(
            url=None, shop_name=None, title=None, price=None, info=None,
            is_new=1, stock=1, description=None)


SUFFIX_PROBLEMS = [',}']
JSON_PATTERN = r'```json(.*?)```'


# https://kevinquinn.fun/blog/a-real-world-solution-to-escape-embedded-double-quotes-in-json/
def sanitize_json_str(s: str, strict=False) -> dict:
    if s[0] != '{':
        s = re.findall(JSON_PATTERN, s, flags=re.DOTALL)
        s = s[0].strip()
    s = s.replace('\\', '')
    while s.find(' \n') > -1:
        s = s.replace(' \n', '\n')
    while s.find('\n}') > -1:
        s = s.replace('\n}', '}')
    for suffix in SUFFIX_PROBLEMS:
        p = len(suffix)
        if s[-p:] == suffix:
            s = s[:-p] + '}'
            break
    js_str = s
    prev_pos = -1
    curr_pos = 0
    while curr_pos > prev_pos:
        prev_pos = curr_pos
        try:
            return json.loads(js_str, strict=strict)
        except json.JSONDecodeError as err:
            curr_pos = err.pos
            if curr_pos <= prev_pos:
                raise err
            prev_quote_index = js_str.rfind('"', 0, curr_pos)
            js_str = js_str[:prev_quote_index] + "\\" + \
                js_str[prev_quote_index:]


class AI:
    def __init__(
            self, conf: dict, input_file: str, output_file: str, limit=0,
            filter_url=''):
        self.conf = conf
        self.input_file = input_file
        self.output_file = output_file
        self.limit = limit
        self.filter_url = filter_url

    # Override, please
    def ask(self, prompt) -> str:
        pass

    def parse(self):
        input_df = pd.read_csv(self.input_file)
        if self.limit:
            input_df = input_df[:self.limit]
        if self.filter_url:
            input_df = input_df[input_df.url == self.filter_url]
        if os.path.exists(self.output_file):
            output_df = pd.read_csv(self.output_file)
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
            prompt = self.conf['prompt_template'].format(desc=desc)
            awal = time()
            print(prompt)
            s = self.ask(prompt)
            print(s)
            durasi = time() - awal
            data['ai_duration'] = durasi
            if durasi > 0.009:
                print(format(durasi, '.2f'), 'detik')
            d = sanitize_json_str(s)
            for index, column in enumerate(self.conf['columns']):
                key = str(index+1)
                data[column] = d.get(key)
            if data['category'].lower().find('ya') == 0:
                data['category'] = self.conf['category']
            else:
                data['category'] = 'lainnya'
            data = {key: [data[key]] for key in data}
            df = pd.DataFrame(data)
            if output_df is not None or not is_first:
                # Tambahkan
                df.to_csv(
                    self.output_file, index=False, mode='a', header=False)
            elif is_first:
                # Buat file baru
                df.to_csv(self.output_file, index=False)
                is_first = False
        print(f'Sudah disimpan di {self.output_file}')
