from crawler import Crawler
from macstore import Laptop as Macstore
from bukalapak import Laptop as Bukalapak
from tokopedia import Laptop as Tokopedia
from shopee import Laptop as Shopee


PARSERS = {
    'macstore.id': Macstore,
    'www.bukalapak.com': Bukalapak,
    'www.tokopedia.com': Tokopedia,
    'shopee.co.id': Shopee,
    }

URLs = [
    'https://macstore.id/product-category/macbook/',
    'https://www.bukalapak.com/acer-official-store-official',
    'https://www.bukalapak.com/asus-laptop-official',
    'https://www.bukalapak.com/dell-store-m2m-official',
    'https://www.bukalapak.com/gadget-heaven-laptop-official',
    'https://www.bukalapak.com/hp-official-store-official/label/laptop',
    'https://www.bukalapak.com/hp-official-store-official/label/business-notebook',
    'https://www.bukalapak.com/hp-official-store-official/label/premium-notebook',
    'https://www.bukalapak.com/hp-official-store-official/label/gaming-notebook',
    'https://www.bukalapak.com/lenovo-official/label/semua-notebook-laptop',
    'https://www.bukalapak.com/msi-store-official',
    'https://www.bukalapak.com/u/levacom',
    ]


class Laptop(Crawler):
    name = 'laptop'
    start_urls = URLs
    parser_classes = PARSERS
