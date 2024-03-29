from crawler import Crawler
from bukalapak import HP as Bukalapak
from tokopedia import HP as Tokopedia
from shopee import HP as Shopee


PARSERS = {
    'www.bukalapak.com': Bukalapak,
    'www.tokopedia.com': Tokopedia,
    'shopee.co.id': Shopee,
    }

URLs = [
    'https://www.bukalapak.com/infinix-official-store-official/label/hp',
    'https://www.bukalapak.com/u/joel_phone',
    'https://www.bukalapak.com/oppo-authorized-dealer-official/label/oppo-handphone',
    'https://www.bukalapak.com/realme-authorized-dealer-official',
    'https://www.bukalapak.com/samsung-official-store-official/label/mobile',
    'https://www.bukalapak.com/users/10817823',
    'https://www.bukalapak.com/users/11624412',
    'https://www.bukalapak.com/users/36778377',
    'https://www.bukalapak.com/xiaomi-official/label/smartphones',
    'https://www.bukalapak.com/u/dumacommstore',
    'https://www.bukalapak.com/u/dumagama',
    'https://shopee.co.id/oppo.id?page=0&shopCollection=155314759',
    'https://shopee.co.id/oppo.id?page=0&shopCollection=155314762',
    ]


class HP(Crawler):
    name = 'hp'
    start_urls = URLs
    parser_classes = PARSERS
