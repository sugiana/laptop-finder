import sys
import os
from argparse import ArgumentParser
from time import sleep
import pandas as pd
from tools import md5sum_file
from to_category import parse as base_parse


DEFAULT_URL = 'https://generativelanguage.googleapis.com/v1beta/models/'\
              'gemini-1.5-flash:generateContent'


def parse(
        category: str, input_file: str, output_file: str, key: str,
        url=DEFAULT_URL, step=10, wait_seconds=20):
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        count = len(df)
        limit = count // step * step + step
    else:
        limit = step
    ai_info = dict(gemini=dict(url=url, key=key))
    while True:
        if os.path.exists(output_file):
            old_md5 = md5sum_file(output_file)
        else:
            old_md5 = None
        base_parse(category, input_file, output_file, ai_info, limit)
        new_md5 = md5sum_file(output_file)
        if old_md5 == new_md5:
            print('Selesai.')
            break
        sleep(wait_seconds)
        limit += step


def main(argv=sys.argv[1:]):
    categories = ['laptop', 'hp']
    url = 'https://generativelanguage.googleapis.com/v1beta/models/'\
          'gemini-1.5-flash:generateContent'
    help_url = f'default {url}'

    help_key = 'API Key, bisa file'

    step = 10
    help_step = 'jumlah produk dalam satu sesi agar terhindar dari '\
                f'quota error, default: {step}'

    wait_seconds = 20
    help_wait = 'berapa detik waktu tunggu setiap sesi agar terhindar dari '\
                f'quota error, default: {wait_seconds}'

    pars = ArgumentParser()
    pars.add_argument('--category', required=True, choices=categories)
    pars.add_argument('--input-file', required=True)
    pars.add_argument('--output-file', required=True)
    pars.add_argument('--url', default=url, help=help_url)
    pars.add_argument('--key', required=True, help=help_key)
    pars.add_argument('--step', type=int, default=step, help=help_step)
    pars.add_argument('--wait-seconds', default=wait_seconds, help=help_wait)
    option = pars.parse_args(sys.argv[1:])

    if os.path.exists(option.key):
        with open(option.key) as f:
            key = f.read()
    else:
        key = option.key
    parse(
        option.category, option.input_file, option.output_file, key,
        option.url, option.step, option.wait_seconds)


if __name__ == '__main__':
    main()
