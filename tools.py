from configparser import RawConfigParser


def config_from_dict(d: dict, prefix: str):
    i = len(prefix)
    r = dict()
    for key, value in d.items():
        if key.find(prefix) == 0:
            name = key[i:]
            r[name] = value
    return r


def create_columns(cf: dict):
    columns = []
    ask_list = []
    no = 0
    for line in cf['columns'].strip().splitlines():
        t = line.split(':')
        columns.append(t[0])
        no += 1
        ask = ':'.join(t[1:])
        ask = ask.strip()
        ask = f'{no}. {ask}'
        ask_list.append(ask)
    cf['columns'] = columns
    ask_str = '\n'.join(ask_list)
    cf['prompt_template'] = cf['prompt_template'].replace('{columns}', ask_str)


def create_numeric_columns(cf: dict):
    cf['numeric_columns'] = []
    for unit in cf['numeric_units']:
        suffix = '_' + unit
        i = len(suffix)
        for column in cf['columns']:
            if column[-i:] == suffix:
                cf['numeric_columns'].append(column)


def create_range_values(cf: dict):
    r = dict()
    for line in cf['range_values']:
        column, values = line.split(':')
        min_, max_ = values.split(',')
        r[column] = float(min_), float(max_)
    cf['range_values'] = r


def get_names(d: dict) -> (list, dict):
    names = list(d.keys())
    alias = dict()
    for key in d:
        alias[key] = key
        values = d[key].strip().split()
        for value in values:
            alias[value] = key
    return names, alias


def create_names(conf: RawConfigParser, cf: dict):
    r = dict()
    for column in cf['columns']:
        if column[-5:] != '_name':
            continue
        r[column] = ([], dict())
    for section in conf.sections():
        if section[-5:] != '_name':
            continue
        column = section
        keys, alias = get_names(dict(conf.items(column)))
        r[column] = (keys, alias)
    if r:
        cf['names'] = r


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
    cf['categories'] = [x.strip() for x in cf['category'].split(',')]
    cf['category'] = cf['categories'][0]
    to_str('role')
    create_columns(cf)
    # Untuk repair.py
    to_list('not_null_columns')
    to_list('numeric_units') and create_numeric_columns(cf)
    to_list('range_values') and create_range_values(cf)
    create_names(conf, cf)
    # Untuk check.py
    to_list('count_columns')
    to_list('min_max_columns')
    return cf
