from configparser import RawConfigParser


def config_from_dict(d: dict, prefix: str):
    i = len(prefix)
    r = dict()
    for key, value in d.items():
        if key.find(prefix) == 0:
            name = key[i:]
            r[name] = value
    return r


def create_numeric_columns(cf: dict):
    cf['numeric_columns'] = []
    for unit in cf['numeric_units']:
        suffix = '_' + unit
        i = len(suffix)
        for column in cf['columns']:
            if column[-i:] == suffix:
                cf['numeric_columns'].append(column)


def get_brands(d: dict) -> (list, dict):
    brands = list(d.keys())
    alias = dict()
    for key in d:
        alias[key] = key
        values = d[key].strip().split()
        for value in values:
            alias[value] = key
    return brands, alias


def create_brands(conf: RawConfigParser, cf: dict):
    r = dict()
    for section in conf.sections():
        if section[-5:] != 'brand':
            continue
        column = section
        keys, alias = get_brands(dict(conf.items(column)))
        r[column] = (keys, alias)
    if r:
        cf['brands'] = r


def read_conf(conf_file):
    def to_str(key):
        if (s := cf.get(key)) and (s := s.strip()):
            cf[key] = s

    def to_list(key):
        if (s := cf.get(key)) and (s := s.strip()) and (r := s.split()):
            cf[key] = r
            return True

    conf = RawConfigParser()
    # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
    conf.optionxform = str
    conf.read(conf_file)
    cf = dict(conf.items('main'))
    # Untuk downloader.py & to_category.py
    to_str('filter')
    if cf.get('filter', '').find('stock > 0') > -1:
        cf['is_ready_stock'] = True
    # Untuk to_category.py
    cf['prompt_template'] = cf['prompt_template'].strip()
    cf['columns'] = cf['columns'].strip().split()
    to_str('role')
    # Untuk repair.py
    to_list('not_null_columns')
    to_list('numeric_units') and create_numeric_columns(cf)
    create_brands(conf, cf)
    # Untuk check.py
    to_list('count_columns')
    to_list('min_max_columns')
    return cf
