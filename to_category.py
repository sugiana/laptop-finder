import sys
from argparse import ArgumentParser
from tools import (
    read_conf,
    config_from_dict,
    )
from parser import AI


def parse(
        conf: dict, input_file: str, output_file: str, limit=0, filter_url=''):
    p = AI(conf, input_file, output_file, limit, filter_url)
    p.parse()


def main(arg=sys.argv[1:]):
    help_input = f'File CSV hasil dari to_csv.py'
    help_output = f'File CSV usai bertanya ke AI'
    help_limit = 'Jumlah produk yang diproses, isi dengan 5 untuk uji coba'
    help_filter = '''Sesuai kondisi, contoh: "url=='https://...'"'''

    pars = ArgumentParser()
    pars.add_argument('conf')
    pars.add_argument('--input-file', required=True, help=help_input)
    pars.add_argument('--output-file', required=True, help=help_output)
    pars.add_argument('--limit', type=int, help=help_limit)
    pars.add_argument('--filter', help=help_filter)
    option = pars.parse_args(sys.argv[1:])

    cf = read_conf(option.conf)
    parse(
        cf, option.input_file, option.output_file, option.limit, option.filter)


if __name__ == '__main__':
    main()
