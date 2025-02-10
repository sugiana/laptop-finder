import sys
from argparse import ArgumentParser
from tools import (
    read_conf,
    config_from_dict,
    )
from ask_gemini import Gemini
from ask_ollama import Ollama


PARSERS = dict(ollama=Ollama, gemini=Gemini)


def parse(
        conf: dict, input_file: str, output_file: str, limit=0, filter_url=''):
    ai = 'gemini_url' in conf and 'gemini' or 'ollama'
    prefix = ai + '_'
    conf['ai'] = config_from_dict(conf, prefix)
    cls = PARSERS[ai]
    p = cls(conf, input_file, output_file, limit, filter_url)
    p.parse()


def main(arg=sys.argv[1:]):
    input_file = 'tokopedia.csv'
    help_input = f'default {input_file}'

    output_file = 'laptop.csv'
    help_output = f'default {output_file}'

    help_limit = 'Jumlah produk yang diproses, isi dengan 5 untuk uji coba'
    help_filter = 'Hanya tautan tertentu saja'

    pars = ArgumentParser()
    pars.add_argument('conf')
    pars.add_argument('--input-file', default=input_file, help=help_input)
    pars.add_argument('--output-file', default=output_file, help=help_output)
    pars.add_argument('--limit', type=int, help=help_limit)
    pars.add_argument('--filter-url', help=help_filter)
    option = pars.parse_args(sys.argv[1:])

    cf = read_conf(option.conf)
    parse(
        cf, option.input_file, option.output_file, option.limit,
        option.filter_url)


if __name__ == '__main__':
    main()
