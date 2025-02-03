import os
import re
import json
import unicodedata
from hashlib import md5
from datetime import datetime
import pandas as pd


# https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).\
                encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


SUFFIX_PROBLEMS = [',}']


# https://kevinquinn.fun/blog/a-real-world-solution-to-escape-embedded-double-quotes-in-json/
def sanitize_json_str(s: str, strict=False) -> dict:
    s = s.lstrip("```json").rstrip("```").strip()
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


def nice_str(s: str, ref: list):
    lower_ref = [x.lower() for x in ref]
    lower_s = s.lower()
    if lower_s in lower_ref:
        index = lower_ref.index(lower_s)
        return ref[index]
    return s


def clean_data(data: dict, column: str, nice_names: list, back_ref=dict()):
    if pd.isnull(data[column]):
        return
    data[column] = nice_str(data[column], nice_names)
    for key, value in back_ref.items():
        if data[column].find(key) > -1:
            data[column] = value


def file_time(filename: str) -> datetime:
    mtime = os.path.getmtime(filename)
    return datetime.fromtimestamp(mtime)


def md5sum_file(filename: str):
    hash_md5 = md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def value2keys(d: dict):
    r = dict()
    for key in d:
        r[key] = key
        for value in d[key]:
            r[value] = key
    return r
