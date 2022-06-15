from selenium_crawler import App as BaseApp
from tokopedia import Crawler as Tokopedia


PARSERS = {
    'www.tokopedia.com': Tokopedia,
    }

URLs = [
    'https://www.tokopedia.com/nokia-mobile/etalase/nokia-smartphone',
    ]


class App(BaseApp):
    category = 'hp'
    start_urls = URLs
    parser_classes = PARSERS


if __name__ == '__main__':
    a = App()
    a.run()
