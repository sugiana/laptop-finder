from selenium_crawler import App as BaseApp
from tokopedia import Crawler as Tokopedia


PARSERS = {
    'www.tokopedia.com': Tokopedia,
    }

URLs = [
    'https://www.tokopedia.com/nvidiageforcelt/product',
    ]


class App(BaseApp):
    category = 'laptop'
    start_urls = URLs
    parser_classes = PARSERS


if __name__ == '__main__':
    a = App()
    a.run()
