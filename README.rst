Laptop Finder
=============

Streamlit application for laptop finder. Usage::

    $ python3 -m venv ~/env
    $ ~/env/bin/pip install --upgrade pip wheel
    $ ~/env/bin/pip install -r requirements.txt
    $ ~/env/bin/streamlit run laptop_finder.py


Crawler
-------

Crawl and parse using Scrapy::

    $ ~/env/bin/scrapy runspider laptop_crawler.py -O laptop.csv

Crawl using Selenium (need desktop environment)::

    $ mkdir /tmp/www.tokopedia.com
    $ ~/env/bin/python tokopedia_crawler.py --tmp-dir=/tmp/www.tokopedia.com

Parse using Scrapy::

    $ ~/env/bin/scrapy runspider laptop_crawler.py -a product_url=file:///tmp/www.tokopedia.com -O laptop-www.tokopedia.com.csv

Merge all CSV files::

    $ ~/env/bin/python csv_concat.py laptop-all.csv

Edit ``laptop_finder.py``, change ``URL`` line::

    URL = 'laptop-all.csv'

Press Ctrl-C to stop ``streamlit`` and run again::

    $ ~/env/bin/streamlit run laptop_finder.py

Good luck.
