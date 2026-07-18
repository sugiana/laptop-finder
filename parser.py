import os
import re
import json
from time import time
from html.parser import HTMLParser
from parsel import Selector
import pandas as pd
import numpy as np
from ask_ai import AIProvider


class BaseError(Exception):
    pass


class UrlNotFound(BaseError):
    pass


class DescriptionNotFound(BaseError):
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


class BaseListParser:
    def __init__(self, driver, is_ready_stock=True):
        self.driver = driver
        self.is_ready_stock = is_ready_stock

    def has_variant(self) -> bool:
        return


class BaseProductParser:
    def __init__(self, html):
        self.sel = Selector(html)
        self.data = dict(
            url=None, shop_name=None, title=None, price=None, info={},
            is_new=1, stock=1, description=None)

    def get_variant(self) -> dict:
        return {}


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
            filter_=''):
        self.conf = conf
        self.input_file = input_file
        self.output_file = output_file
        self.limit = limit
        self.filter_ = filter_
        self.ai = AIProvider()

    def ask(self, prompt: str) -> str:
        return self.ai.ask(prompt)

    def read_output_file(self):
        df = pd.read_csv(self.output_file)
        new_columns = dict()
        for column in self.conf['columns']:
            if column not in df.columns:
                new_columns.update({column: np.nan})
        if new_columns:
            df = df.assign(**new_columns)
            df.to_csv(self.output_file, index=False)
        return df

    def parse(self):
        input_df = pd.read_csv(self.input_file)
        if self.conf.get('filter'):
            input_df = input_df.query(self.conf['filter'])
        if self.filter_:
            input_df = input_df.query(self.filter_)
        if self.limit:
            input_df = input_df[:self.limit]
        if os.path.exists(self.output_file):
            output_df = self.read_output_file()
        else:
            output_df = None
        is_first = True
        input_df = input_df.sort_values(by='url')
        is_saved = False
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
            r = self.ask(prompt)
            print(r['message'])
            log_msg = []
            if (durasi := time() - awal) > 0.009:
                log_msg.append(format(durasi, '.2f') + ' detik')
            data['ai_duration'] = durasi
            in_ = data['ai_token_input'] = r['token']["input"]
            out_ = data['ai_token_output'] = r['token']["output"]
            log_msg.append(f'Input {in_} token, Output {out_} token')
            print(', '.join(log_msg))
            d = sanitize_json_str(r['message'])
            for index, column in enumerate(self.conf['columns']):
                key = str(index+1)
                data[column] = d.get(key)
            category = data['category'].lower()
            for ref_category in self.conf['categories']:
                if category == ref_category:
                    data['category'] = self.conf['category']
                    break
            data = {key: [data[key]] for key in data}
            df = pd.DataFrame(data)
            if output_df is not None or not is_first:
                # Tambahkan
                df.to_csv(
                    self.output_file, index=False, mode='a', header=False)
                is_saved = True
            elif is_first:
                # Buat file baru
                df.to_csv(self.output_file, index=False)
                is_saved = True
                is_first = False
        if is_saved:
            print(f'Sudah disimpan di {self.output_file}')
        else:
            print(f"Tidak ada data")
