from selenium_crawler import App as BaseApp
from tokopedia import Crawler as Tokopedia
from shopee import Crawler as Shopee


PARSERS = {
    'www.tokopedia.com': Tokopedia,
    'shopee.co.id': Shopee,
    }

URLs = [
    'https://www.tokopedia.com/nvidiageforcelt/product',
    'https://shopee.co.id/appleflagship?shopCollection=46775586',
    ]


class App(BaseApp):
    category = 'laptop'
    start_urls = URLs
    parser_classes = PARSERS


if __name__ == '__main__':
    a = App()
    a.run()
