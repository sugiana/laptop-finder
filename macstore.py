from parser import Parser


XPATH_TITLE = '//h1/text()'
XPATH_PRICE = '//p[@class="price"]/ins/span[contains('\
              '@class,"woocommerce-Price-amount")]/bdi/text()'
XPATH_PRODUCT = '//a[contains(@class,"woocommerce-LoopProduct-link")]/@href'


class Laptop(Parser):
    XPATH_DESC = '//div[@class='\
                 '"woocommerce-product-details__short-description"]'

    @classmethod
    def get_product_urls(cls, response) -> list:
        urls = response.xpath(XPATH_PRODUCT).extract()
        r = []
        for url in urls:
            if url.find('macbook') > -1:
                r.append(url)
        return r

    def get_info(self):
        if self.response.url.find('macbook') > -1:
            return dict(Kategori='laptop')
        return dict()

    def get_brand(self) -> str:  # Override
        return 'Apple'

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:  # Override
        s = self.response.xpath(XPATH_PRICE).extract()[0].lstrip()
        return s.replace('.', '').replace(',', '.')
