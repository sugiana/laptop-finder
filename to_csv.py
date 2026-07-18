import sys
import os
import json
from argparse import ArgumentParser
from datetime import datetime
from glob import glob
import pandas as pd
from parser import BaseError
from tokopedia import ProductParser as TokopediaProductParser
from macstore import ProductParser as MacstoreProductParser


PARSER_CLASSES = dict(
    tokopedia=TokopediaProductParser,
    macstore=MacstoreProductParser)


def file_time(filename: str) -> datetime:
    mtime = os.path.getmtime(filename)
    return datetime.fromtimestamp(mtime)


def to_csv(parser: str, download_dir: str, output_file: str):
    parser_class = PARSER_CLASSES[parser]
    if os.path.exists(output_file):
        orig_df = pd.read_csv(output_file)
    else:
        orig_df = None
    is_first = True
    no = 0
    pattern = os.path.join(download_dir, '*.html')
    for html_file in glob(pattern):
        html_file = os.path.join(download_dir, html_file)
        print(html_file)
        with open(html_file) as f:
            html = f.read()
        try:
            parser = parser_class(html)
        except BaseError as e:
            print(f'  {e}')
            continue
        except KeyError:
            raise Exception(
                f'  hapus file {html_file} '
                'lalu jalankan kembali pengunduhnya.')
        d = dict(parser.data)
        json_file, ext = os.path.splitext(html_file)
        json_file = json_file + '.json'
        with open(json_file) as f:
            metadata = json.load(f)
        d['url'] = metadata['url']
        if not d['description']:
            print('  tidak ada description')
            continue
        d['info'] = json.dumps(d['info'])
        d['time'] = file_time(html_file).strftime('%Y-%m-%d %H:%M:%S')
        data = {column: [d[column]] for column in d}
        df = pd.DataFrame(data)
        if orig_df is None:
            if is_first:
                msg = 'CREATE'
                df.to_csv(output_file, index=False)
                is_first = False
            else:
                msg = 'INSERT'
                df.to_csv(output_file, index=False, mode='a', header=False)
        else:
            key_df = orig_df[orig_df.url == d['url']]
            if key_df.empty:
                msg = 'INSERT'
                df.to_csv(output_file, index=False, mode='a', header=False)
            else:
                msg = 'UPDATE'
                for column in orig_df.columns:
                    orig_df.loc[orig_df.url == d['url'], column] = d[column]
                orig_df.to_csv(output_file, index=False)
        no += 1
        print(f'#{no} {msg} {d["url"]}')
    print(f'Sudah tersimpan di {output_file}')


def main(argv=sys.argv[1:]):
    parser_names = list(PARSER_CLASSES.keys())
    parser = parser_names[0]
    help_parser = f'default {parser}'

    home_dir = os.path.expanduser('~')
    base_download_dir = os.path.join(home_dir, 'tmp')
    download_dir = os.path.join(base_download_dir, parser)
    help_tmp = f'default {download_dir}'

    output_file = f'{parser}.csv'
    help_output = f'default {output_file}'

    pars = ArgumentParser()
    pars.add_argument('--download-dir', default=download_dir, help=help_tmp)
    pars.add_argument(
        '--parser', default=parser, help=help_parser, choices=parser_names)
    pars.add_argument('--output-file', default=output_file, help=help_output)
    option = pars.parse_args(sys.argv[1:])

    to_csv(option.parser, option.download_dir, option.output_file)


if __name__ == '__main__':
    main()
