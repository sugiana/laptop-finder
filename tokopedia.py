import time
from urllib.parse import urlparse
from itertools import product
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from parsel import Selector
from parser import (
    HTML2Text,
    BaseListParser,
    BaseProductParser,
    UrlNotFound,
    DescriptionNotFound,
    )


XPATH_LIST = '//div[@class="css-79elbk"]//a'
XPATH_NEXT = '//a[@data-testid="btnShopProductPageNext"]'
XPATH_VARIANT = "//b[contains(text(), 'Pilih ')]"
XPATH_VARIANT_LABEL = f".{XPATH_VARIANT}"
XPATH_VARIANT_GROUPS = f"{XPATH_VARIANT}/../.."


class ListParser(BaseListParser):
    def get_product_urls(self) -> list:
        self.is_stock = True
        urls = []
        for xs in self.driver.find_elements(By.XPATH, XPATH_LIST):
            # Apakah hanya membaca produk yang ada stoknya ?
            if self.is_ready_stock:
                html = xs.get_attribute('innerHTML')
                if html.lower().find('stok habis') > -1:
                    # Nanti dibaca next_page_urls(). Jika ketemu produk yang
                    # tidak ada stoknya maka jangan dilanjutkan karena
                    # produk-produk berikutnya pasti juga sudah habis.
                    self.is_stock = False
                    return urls
            url = xs.get_attribute('href')
            if url not in urls and url[-7:] != '/review' and \
                    len(url) > len(self.driver.current_url):
                p = urlparse(url)
                # Hapus query string
                url = f"{p.scheme}://{p.netloc}{p.path}"
                urls.append(url)
        return urls

    def next_page_url(self):
        try:
            if not self.is_stock:
                return
        except AttributeError:
            raise Exception(f'Hapus {self.driver.current_url} dari daftar.')
        try:
            xs = self.driver.find_element(By.XPATH, XPATH_NEXT)
            return xs.get_attribute('href')
        except NoSuchElementException:
            return

    def is_product_list(self) -> bool:
        return self.driver.page_source.lower().find(
                'jumlah produk per halaman') > -1

    def is_page_not_found(self) -> bool:
        return self.driver.page_source.lower().find(
                'toko ini belum memiliki produk') > -1

    def has_variant(self) -> bool:
        try:
            return self.driver.find_element(By.XPATH, XPATH_VARIANT)
        except NoSuchElementException:
            return

    def get_variants(self) -> list:
        script = 'window.scrollTo(0, 0);'  # Agar kelihatan saat memilih
        self.driver.execute_script(script)
        # Cari container variant groups
        groups = self.driver.find_elements(By.XPATH, XPATH_VARIANT_GROUPS)
        # Dapatkan daftar opsi untuk setiap grup varian
        all_group_options = []
        group_names = []
        for idx, group in enumerate(groups):
            # Ambil nama grup varian dari label <b>
            label_el = group.find_element(By.XPATH, XPATH_VARIANT_LABEL)
            label_text = label_el.text
            group_names.append(label_text)
            buttons = group.find_elements(By.XPATH, ".//button")
            # Filter hanya tombol yang memiliki teks (opsi valid)
            opts = [btn.text for btn in buttons if btn.text]
            all_group_options.append(opts)
        # Hitung semua kombinasi menggunakan itertools.product
        combinations = list(product(*all_group_options))
        results = []
        # Iterasi melalui setiap kombinasi tuple,
        # misal ('RAM 8GB', 'STORAGE 128GB')
        for combo_idx, combo in enumerate(combinations, 1):
            variant = [
                (name.lstrip("Pilih ").rstrip(":"), val)
                for name, val in zip(group_names, combo)]
            variant = dict(variant)
            # Klik opsi pada tiap grup secara berurutan
            for group_idx, option_text in enumerate(combo):
                # Cari ulang groups untuk menghindari
                # StaleElementReferenceException
                groups = self.driver.find_elements(
                        By.XPATH, XPATH_VARIANT_GROUPS)
                if group_idx >= len(groups):
                    break
                group = groups[group_idx]
                buttons = group.find_elements(By.XPATH, ".//button")
                target_btn = None
                for btn in buttons:
                    if btn.text == option_text:
                        target_btn = btn
                        break
                if target_btn:
                    self.driver.execute_script(
                        "arguments[0].click();", target_btn)
                    time.sleep(1)  # jeda singkat setelah klik
            # Berikan waktu agar URL di address bar terupdate setelah seluruh
            # opsi dalam kombinasi terpilih
            time.sleep(1.2)
            current_url = self.driver.current_url
            print(f"Pilihan {variant} -> {current_url}")
            results.append((variant, current_url, self.driver.page_source))
        return results


XPATH_TITLE = '//h1/text()'
XPATH_PRICE = '//div[@class="price"]/text()'
XPATH_SHOP_NAME = '//div[@data-testid="llbPDPFooterShopName"]/h2/text()'
XPATH_INFO = '//ul[@data-testid="lblPDPInfoProduk"]/li'
XPATH_DESC = '//div[@data-testid="lblPDPDescriptionProduk"]'
XPATH_STOCK = '//p[@data-testid="stock-label"]'

EVERY_LINE = 2


class ProductParser(BaseProductParser):
    def __init__(self, html):
        super().__init__(html)
        title = self.get_title()
        if not title:
            raise DescriptionNotFound('title tidak ditemukan')
        info = self.get_info()
        is_new = info['Kondisi'] == 'Baru' and 1 or 0
        self.data = dict(
            shop_name=self.get_shop_name(),
            title=title,
            price=self.get_price(),
            info=info,
            is_new=is_new,
            stock=self.get_stock(),
            description=self.get_description())

    def get_shop_name(self) -> str:
        r = self.sel.xpath(XPATH_SHOP_NAME).extract()
        return r and r[0] or None

    def get_title(self) -> str:
        r = self.sel.xpath(XPATH_TITLE).extract()
        return r and r[0] or None

    def get_price(self) -> str:
        s = self.sel.xpath(XPATH_PRICE).extract()[0].lstrip('Rp')
        s = s.replace('.', '')
        return float(s)

    def get_info(self) -> dict:
        lines = []
        for xs in self.sel.xpath(XPATH_INFO):
            s = xs.extract()
            p = HTML2Text()
            p.feed(s)
            lines += p.lines
        numbers = range(0, len(lines), EVERY_LINE)
        lines = [lines[x:x+EVERY_LINE] for x in numbers]
        d = dict()
        for t in lines:
            key = t[0]
            val = t[-1]
            key = key.split(':')[0]
            d[key] = val
        return d

    def get_description(self) -> str:
        xs = self.sel.xpath(XPATH_DESC)
        s = xs.extract()
        if not s:
            raise DescriptionNotFound()
        s = s[0]
        p = HTML2Text()
        p.feed(s)
        variant = self.get_variant()
        if variant:
            lines = [f"{key}: {val}" for key, val in variant.items()]
        else:
            lines = []
        lines.extend(p.lines)
        return '\n'.join(lines)

    def get_stock(self) -> int:
        xs = self.sel.xpath(XPATH_STOCK)
        s = xs.extract()
        if not s:
            return 1
        s = s[0]
        p = HTML2Text()
        p.feed(s)
        if p.lines[-1].lower().find('tidak') > -1:
            return 0
        s = p.lines[-1].split()[-1]
        s = s == 'Habis' and '0' or s.replace('.', '')
        try:
            return int(s)
        except ValueError:
            return 1

    def get_variant(self) -> dict:
        groups = self.sel.xpath(XPATH_VARIANT_GROUPS)
        if not groups:
            return
        d = dict()
        for idx, group in enumerate(groups, 1):
            # Mengambil label grup varian, misalnya:
            # "Pilih memory ram: " -> "memory ram"
            label_el = group.xpath("string(.//b[contains(text(), 'Pilih ')])")
            label_el = label_el.extract_first()
            group_name = label_el.replace("Pilih ", "").strip(" :")
            # Mencari semua tombol varian (Chip)
            buttons = group.xpath(".//button")
            selected_option = None
            for btn in buttons:
                option_text = btn.xpath("string(.)").extract_first()
                if option_text:
                    option_text = option_text.strip()
                # Memeriksa class tombol untuk menentukan apakah terpilih.
                # Berdasarkan analisis, class terpilih mengandung '1pxi8to'
                cls = btn.xpath("../@data-testid").extract_first() or ""
                if "btnVariantChipActiveSelected" in cls or \
                        "btnVariantChipInactiveSelected" in cls:
                    selected_option = option_text
                    break
            if selected_option:
                d[group_name] = selected_option
        if not d:
            msg = "Penanda varian yang dipilih berubah, perbaiki script."
            raise Exception(msg)
        return d


if __name__ == '__main__':
    import sys
    import os
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    from tools import nice_filename

    url = sys.argv[1]

    if os.path.exists(url):
        with open(url) as f:
            html = f.read()
        p = ProductParser(html)
        variant = p.get_variant()
        print("Variant:", variant)
        print("Data:", p.data)
        sys.exit()

    opt = Options()
    # opt.add_argument('--headless')
    opt.add_argument('--disable-gpu')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')
    # Gunakan User-Agent standar agar tidak terblokir oleh Tokopedia
    opt.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
        "Safari/537.36")
    driver_manager = ChromeDriverManager()
    installer = driver_manager.install()
    service = Service(installer)
    driver = webdriver.Chrome(service=service, options=opt)

    # Contoh 1: Produk dengan 2 jenis varian (RAM & GPU)
    # url = "https://www.tokopedia.com/onelinegamepc/pc-editing-design-gaming-intel-core-i9-13900-ddr5-1tb-nvidia-16gb-ddr5-gtx-1660-super-03791"

    # Contoh 2: Produk dengan 1 jenis varian (Extra Packing Bubble)
    # url = "https://www.tokopedia.com/pcrakitanofficial/extra-packing-bubble-motherboard-2-1735373836543493182-1735981791761957950"

    # Contoh 3: Tanpa varian
    # url = "https://www.tokopedia.com/gamingpcstore/pc-build-amd-ryzen-9-9950x3d-64gb-ddr5-ssd-4tb-gen5-vga-geforce-rtx-5090-32gb-rog-render-editing-gaming-1730137751442195621"

    driver.get(url)

    # Scroll
    max_count = 7
    delay = 2
    height = 200
    x = 0
    while x < max_count:
        script = f'window.scrollTo(0, {height});'
        driver.execute_script(script)
        time.sleep(delay)
        x += 1
        height += height

    p = ListParser(driver)
    if p.is_product_list():
        urls = p.get_product_urls()
        for url in urls:
            print(url)
        sys.exit()
    if p.has_variant():
        variants = p.get_variants()
        for variant, url, html in variants:
            filename = nice_filename(url)
            with open(filename, "w") as f:
                f.write(html)
            print(f"{variant} -> {url} -> {filename}")
            p = ProductParser(html)
            print(p.data)
    else:
        filename = nice_filename(url)
        with open(filename, "w") as f:
            f.write(driver.page_source)
        print(f"{url} -> {filename}")
        p = ProductParser(driver.page_source)
        print(p.data)
