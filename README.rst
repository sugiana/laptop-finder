Laptop Finder
=============

Tujuan aplikasi ini adalah mendapatkan laptop sesuai spesifikasi dan harga yang
diharapkan. Misalkan untuk menjawab ini:

*Cari laptop dengan GPU NVIDIA VRAM 12 GB dengan anggaran 30 juta*

Oleh karena itu **diperlukan tabel** yang memuat berbagai spesifikasi laptop
seperti harga, merek GPU, jumlah memori GPU (VRAM), jumlah memori CPU (RAM),
merek laptop, dst.

Adapun prosesnya sebagai berikut:

1. ``downloader.py``: pengunduh HTML setiap produk dari toko online
2. ``to_csv.py``: pembaca HTML untuk mengambil deskripsi, harga, stok, dan
   lainnya untuk disimpan ke file CSV
3. ``to_category.py``: penerjemah file CSV tadi menjadi fitur-fitur sesuai
   kategori laptop seperti berapa RAM-nya, apa merek kartu grafis, berapa VRAM,
   dst. Di sini AI digunakan.
4. ``laptop_repair.py``: memperbaiki data yang diberikan AI
5. ``laptop_finder.py``: aplikasi `Streamlit <https://streamlit.io>`_ sebagai
   web server untuk kenyamanan memilih laptop sesuai kebutuhan


Buatlah Python Virtual Environment::

    $ python3.12 -m venv ~/env
    $ ~/env/bin/pip install -r requirements.txt

Untuk mengunduh HTML maka kita membutuhkan
`Google Chrome <https://www.google.com/intl/id_id/chrome/>`_. Kalau sudah
terpasang jalankan::

    $ mkdir -p /home/sugiana/tmp/tokopedia-nvidiageforcelt
    $ ~/env/bin/python downloader.py --download-dir=/home/sugiana/tmp/tokopedia-nvidiageforcelt --url=https://www.tokopedia.com/nvidiageforcelt/product

Setiap produk akan tersimpan di sebuah file HTML.

Selanjutnya seluruh file HTML itu akan disimpan dalam sebuah file CSV dengan cara::

    $ ~/env/bin/python to_csv.py --download-dir=/home/sugiana/tmp/tokopedia-nvidiageforcelt --parser=tokopedia --output-file=tokopedia-nvidiageforcelt.csv

Untuk mendapatkan spesifikasi laptop secara terstruktur maka kita akan
**bertanya ke AI** yaitu `Ollama <https://ollama.com>`_. Pastikan Anda sudah
memasangnya. Adapun model yang digunakan adalah
`gemma2:9b <https://ollama.com/library/gemma2:9b>`_.

Jalankan::

    $ ~/env/bin/python to_category.py --category=laptop --input-file=tokopedia-nvidiageforcelt.csv --output-file=laptop-nvidiageforcelt.csv

Gunakan opsi ``--help`` untuk melihat kemungkinan lainnya. Misalkan ingin tanya ke Gemini.

Setelah selesai lakukan bersih-bersih agar konsisten, contoh:

1. Terkait brand, contoh: LENOVO menjadi Lenovo
2. Terkait angka maka diuji dengan ``float()``, jika gagal maka dihapus nilainya

Untuk melakukannya jalankan::

    $ ~/env/bin/python laptop_repair.py laptop-nvidiageforcelt.csv

Untuk melihat hasil berikut ringkasannya::

    $ ~/env/bin/python laptop_check.py laptop-nvidiageforcelt.csv

Setelah selesai aktifkan web server::

    $ ~/env/bin/streamlit run laptop_finder.py laptop-nvidiageforcelt.csv

Nanti otomatis Chrome aktif membuka
`http://localhost:8501 <http://localhost:8501>`_. Selanjutnya pilih kriteria laptop yang dibutuhkan.


Menggabungkan File CSV
----------------------

Sekarang kita unduh daftar laptop dari **toko lainnya**, masih di Tokopedia::

    $ mkdir /home/sugiana/tmp/tokopedia-lenovojakarta
    $ ~/env/bin/python downloader.py --download-dir=/home/sugiana/tmp/tokopedia-lenovojakarta --url=https://www.tokopedia.com/lenovojakarta/product
    $ ~/env/bin/python to_csv.py --download-dir=/home/sugiana/tmp/tokopedia-lenovojakarta --parser=tokopedia --output-file=tokopedia-lenovojakarta.csv
    $ ~/env/bin/python to_category.py --category=laptop --input-file=tokopedia-lenovojakarta.csv --output-file=laptop-lenovojakarta.csv
    $ ~/env/bin/python laptop_repair.py laptop-lenovojakarta.csv

Gabungkan dengan yang tadi::

    $ ~/env/bin/python csv_concat.py laptop 

Dia akan menggabungkan seluruh file dengan pola ``laptop-*.csv`` dan menyimpannya ke ``laptop.csv``. Dengan begitu perintah web servernya menjadi::

    $ ~/env/bin/streamlit run laptop_finder.py laptop.csv


Tanya Gemini
------------

Jika VRAM pada GPU terbatas yang bisa membuat AI lama menjawab maka kita bisa
gunakan `Gemini <https://ai.google.dev/gemini-api/docs/api-key?hl=id>`_. Ia
menawarkan gratis pemakaian selama 1 bulan.

Simpanlah API Key di file ``gemini-key.txt`` lalu jalankan::

    $ ~/env/bin/python to_category_by_gemini.py --category=laptop --input-file=tokopedia-nvidiageforcelt.csv --output-file=laptop-nvidiageforcelt.csv --key=gemini-key.txt

Perintah tersebut juga menjalankan ``to_category.py``. Tugas tambahannya adalah menjaga agar tidak terjadi *quota error*.

Lagi, perbaiki nilai-nilainya agar konsisten::

    $ ~/env/bin/python laptop_repair.py laptop-nvidiageforcelt.csv

Jangan lupa gabungkan dengan yang lain agar menjadi ``laptop.csv``::

    $ ~/env/bin/python csv_concat.py laptop 

Handphone
---------

Untuk kategori HP langkahnya juga mirip. Intinya mengganti kata ``laptop`` menjadi ``hp``. Contoh::

    $ mkdir /home/sugiana/tmp/tokopedia-oppo
    $ ~/env/bin/python downloader.py --url=https://www.tokopedia.com/oppo/product --download-dir=/home/sugiana/tmp/tokopedia-oppo
    $ ~/env/bin/python to_csv --download-dir=/home/sugiana/tmp/tokopedia-oppo --output-file=tokopedia-oppo.csv
    $ ~/env/bin/python to_category.py --category=hp --input-file=tokopedia-oppo.csv --output-file=hp-oppo.csv

Atau kalau tanya Gemini::

    $ ~/env/bin/python to_category_by_gemini.py --category=hp --input-file=tokopedia-oppo.csv --output-file=hp-oppo.csv --key=gemini-key.txt

Perbaiki nilainya agar konsisten::

    $ ~/env/bin/python hp_repair.py hp-oppo.csv

Lihat hasilnya::

    $ ~/env/bin/python hp_check.py hp-oppo.csv

Aktifkan web server::

    $ ~/env/bin/streamlit run hp_finder.py hp-oppo.csv

Cobalah unduh toko HP lainnya. Lihat Referensi di bawah untuk URL-nya. Jika sudah sampai
tahap ``hp_repair.py`` maka gabungkan::

    $ ~/env/bin/python csv_concat.py hp

Nanti akan terbentuk ``hp.csv``. Aktifkan web server::

    $ ~/env/bin/streamlit run hp_finder.py hp.csv


Rutinitas
---------

Seluruh langkah untuk mendapatkan ``laptop.csv`` tadi telah terangkum dalam ``crawler.py``. Salinlah file konfigurasinya::

    $ cp laptop.ini live-laptop.ini

Sesuaikanlah nilai ``base_download_dir``. Kemudian jalankan::

    $ ~/env/bin/python crawler.py live-laptop.ini

Untuk handphone ada di file ``hp.ini``.

Script ini hanya akan mengunduh HTML bila **direktori toko** terkait kosong. Contoh
direktori toko adalah ``/home/sugiana/tmp/tokopedia-nvidiageforcelt``. Jadi
bila ada kesalahan di proses selanjutnya - lalu kita jalankan kembali - maka
script tidak akan mengunduh lagi.

Jika Anda peduli dengan perubahan harga, stok, atau data lainnya maka
**keesokan harinya** hapus dulu semua data dengan cara (**HATI-HATI**)::

    $ ~/env/bin/python remove_all_data.py live-laptop.ini

Bila tidak dihapus maka script tidak akan memperbarui:

1. Saat proses unduh dia berpegang pada keterisian direktori toko.
2. Saat penerjemahan file HTML dia berpegang pada URL. Bila sudah ada di file
   CSV maka diabaikan, tidak ada proses bertanya ke AI.

Kadang AI memberikan format JSON yang kurang pas - misalnya kelebihan karakter
koma - maka cukup jalankan lagi. Biasanya AI memberi jawaban berbeda dengan
format JSON yang benar.

Semoga berhasil.


Referensi
---------

Kategori ``laptop``:

- `NVIDIA Geforce Laptop <https://www.tokopedia.com/nvidiageforcelt/product>`_
- `Lenovo Authorized Jakarta Pusat <https://www.tokopedia.com/lenovojakarta/product>`_
- `Dell Premium Official <https://www.tokopedia.com/dell-premium-official/product>`_
- `ASUS Official Store <https://www.tokopedia.com/asus/product>`_
- `Mac Store Indonesia <https://macstore.id/product-category/macbook>`_
- `MSI Official Store <https://www.tokopedia.com/msi-official/product>`_
- `HP Official <https://www.tokopedia.com/hp/etalase/semua-laptop>`_
- `Acer Authorized Store Jakarta <https://www.tokopedia.com/acer-jakarta/product>`_
- `Axioo Indonesia <https://www.tokopedia.com/axioo-indonesia/product>`_
- `Zyrex Official Store <https://www.tokopedia.com/zyrex/product>`_
- `Glory Computerr <https://www.tokopedia.com/glorycomputerr/product>`_ (ada Toshiba)

Kategori ``hp``:

- `Oppo Official Store <https://www.tokopedia.com/oppo/product>`_
- `Samsung Official Store <https://www.tokopedia.com/samsung/etalase/mobiles>`_
- `Infinix Official Store <https://www.tokopedia.com/officialinfinix/product>`_
- `Xiaomi Official Store <https://www.tokopedia.com/xiaomi/etalase/mobile>`_
- `realme Official Store <https://www.tokopedia.com/realme/product>`_
- `vivo Indonesia <https://www.tokopedia.com/vivo/product>`_
- `ASUS Mobile Indonesia <https://www.tokopedia.com/asus-mobile>`_
- `HUAWEI Official Store <https://www.tokopedia.com/huawei/etalase/smartphone>`_
- `Nokia Mobile Official <https://www.tokopedia.com/nokia-mobile/product>`_
- `NerdBoss Gadget <https://www.tokopedia.com/nerdbossgadget/product>`_ (ada Iphone)
