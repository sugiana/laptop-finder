from html.parser import HTMLParser
from parsel import Selector


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


class BaseProductParser:
    def __init__(self, html):
        self.sel = Selector(html)
        self.data = dict(
            url=None, shop_name=None, title=None, price=None, info=None,
            is_new=1, stock=1, description=None)
