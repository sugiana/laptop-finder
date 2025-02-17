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
   dst. Di sini **AI digunakan**.
4. ``repair.py``: memperbaiki data yang diberikan AI
5. ``laptop_finder.py``: aplikasi `Streamlit <https://streamlit.io>`_ sebagai
   web server untuk kenyamanan memilih laptop sesuai kebutuhan

Buatlah Python Virtual Environment::

    $ python3.12 -m venv ~/env
    $ ~/env/bin/pip install -r requirements.txt

Untuk mengunduh HTML maka kita membutuhkan
`Google Chrome <https://www.google.com/intl/id_id/chrome/>`_. Kalau sudah
terpasang jalankan::

    $ mkdir -p /home/sugiana/tmp/tokopedia-nvidiageforcelt
    $ ~/env/bin/python downloader.py --url=https://www.tokopedia.com/nvidiageforcelt/product --download-dir=/home/sugiana/tmp/tokopedia-nvidiageforcelt

Proses ini akan membuat:

1. File ``/home/sugiana/tmp/tokopedia-nvidiageforcelt.csv`` berisi daftar
   tautan produk. Tujuannya sebagai *cache* yaitu bila ada masalah di tengah
   proses maka tidak perlu lagi membaca halaman awal, cukup membaca file ini
   untuk mendapatkan daftarnya.
2. Setiap produk akan tersimpan di sebuah file HTML.

Selanjutnya seluruh file HTML itu akan disimpan dalam sebuah file CSV dengan cara::

    $ ~/env/bin/python to_csv.py --download-dir=/home/sugiana/tmp/tokopedia-nvidiageforcelt --parser=tokopedia --output-file=tokopedia-nvidiageforcelt.csv

Untuk mendapatkan spesifikasi laptop secara terstruktur maka kita akan
**bertanya ke AI** yaitu `Ollama <https://ollama.com>`_. Pastikan Anda sudah
memasangnya. Adapun model yang digunakan adalah
`gemma2:9b <https://ollama.com/library/gemma2:9b>`_. Model ini teruji lebih
memahami spesifikasi hardware ketimbang
`llama3.1:8b <https://ollama.com/library/llama3.1:8b>`_ atau
`deepseek-r1:8b <https://ollama.com/library/deepseek-r1:8b>`_.

Jalankan::

    $ ~/env/bin/python to_category.py laptop.ini --input-file=tokopedia-nvidiageforcelt.csv --output-file=laptop-nvidiageforcelt.csv

Gunakan opsi ``--help`` untuk melihat kemungkinan lainnya. Misalkan tambah
``--limit=5`` yang berarti hanya membaca 5 tautan saja. Pembatasan ini biasanya
dilakukan selama uji coba untuk memastikan apakah pertanyaan yang diajukan ke
AI dijawab dengan benar.

Setelah selesai lakukan bersih-bersih agar konsisten seperti:

1. Terkait brand yaitu mengubah LENOVO menjadi Lenovo
2. Terkait angka maka diuji dengan ``float()``, jika gagal maka dihapus nilainya

Untuk melakukannya jalankan::

    $ ~/env/bin/python repair.py laptop.ini --csv-file=laptop-nvidiageforcelt.csv

Untuk melihat hasil berikut ringkasannya::

    $ ~/env/bin/python check.py laptop.ini --csv-file=laptop-nvidiageforcelt.csv

Setelah selesai aktifkan web server::

    $ ~/env/bin/streamlit run laptop_finder.py laptop-nvidiageforcelt.csv

Nanti otomatis Chrome membuka `http://localhost:8501 <http://localhost:8501>`_.
Selanjutnya pilih kriteria laptop yang dibutuhkan.


Menggabungkan File CSV
----------------------

Sekarang kita unduh daftar laptop dari **toko lainnya**, masih di Tokopedia::

    $ mkdir /home/sugiana/tmp/tokopedia-lenovojakarta
    $ ~/env/bin/python downloader.py --url=https://www.tokopedia.com/lenovojakarta/product --download-dir=/home/sugiana/tmp/tokopedia-lenovojakarta
    $ ~/env/bin/python to_csv.py --download-dir=/home/sugiana/tmp/tokopedia-lenovojakarta --parser=tokopedia --output-file=tokopedia-lenovojakarta.csv
    $ ~/env/bin/python to_category.py laptop.ini --input-file=tokopedia-lenovojakarta.csv --output-file=laptop-lenovojakarta.csv
    $ ~/env/bin/python repair.py laptop.ini --csv-file=laptop-lenovojakarta.csv

Gabungkan dengan yang tadi::

    $ ~/env/bin/python csv_concat.py laptop 

Dia akan menggabungkan seluruh file dengan pola ``laptop-*.csv`` dan
menyimpannya ke ``laptop.csv``. Dengan begitu perintah web servernya menjadi::

    $ ~/env/bin/streamlit run laptop_finder.py laptop.csv

Atau cukup::

    $ ~/env/bin/streamlit run laptop_finder.py

yang secara default dia akan membaca ``laptop.csv``.


Tanya Gemini
------------

Jika VRAM pada GPU terbatas - yang bisa membuat AI terlalu lama untuk menjawab -
maka kita bisa gunakan `Gemini <https://ai.google.dev/gemini-api/docs/api-key?hl=id>`_.
Ia menawarkan gratis pemakaian selama 1 bulan.

Buatlah file ``live-laptop.ini``::

    $ cp laptop.ini live-laptop.ini

Edit ``live-laptop.ini``, buka belenggu ``gemini_url``::

    gemini_url = https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR-API-KEY

Ubahlah ``YOUR-API-KEY`` dengan nilai yang diperoleh dari
`web Gemini <https://ai.google.dev/gemini-api/docs/api-key?hl=id>`_. Jika baris
ini aktif maka konfigurasi ``ollama_`` diabaikan.

Jalankan::

    $ ~/env/bin/python to_category.py live-laptop.ini --input-file=tokopedia-nvidiageforcelt.csv --output-file=laptop-nvidiageforcelt.csv

Jika mendapatkan pesan kesalahan terkait kuota maka tunggu sekitar satu menit,
lalu jalankan lagi.

Jika sudah selesai langkah selanjutnya masih sama::

    $ ~/env/bin/python repair.py live-laptop.ini --csv-file=laptop-nvidiageforcelt.csv

Jangan lupa gabungkan dengan yang lain agar menjadi ``laptop.csv``::

    $ ~/env/bin/python csv_concat.py laptop 


Handphone
---------

Untuk kategori HP langkahnya juga mirip. Intinya mengganti kata ``laptop`` menjadi ``hp``. Contoh::

    $ mkdir /home/sugiana/tmp/tokopedia-oppo
    $ ~/env/bin/python downloader.py --url=https://www.tokopedia.com/oppo/product --download-dir=/home/sugiana/tmp/tokopedia-oppo
    $ ~/env/bin/python to_csv.py --download-dir=/home/sugiana/tmp/tokopedia-oppo --output-file=tokopedia-oppo.csv
    $ ~/env/bin/python to_category.py hp.ini --input-file=tokopedia-oppo.csv --output-file=hp-oppo.csv

Perbaiki nilainya agar konsisten::

    $ ~/env/bin/python repair.py hp.ini --csv-file=hp-oppo.csv

Lihat hasilnya::

    $ ~/env/bin/python check.py hp.ini --csv-file=hp-oppo.csv

Aktifkan web server::

    $ ~/env/bin/streamlit run hp_finder.py hp-oppo.csv

Cobalah unduh toko HP lainnya. Lihat ``hp.ini`` untuk URL-nya. Jika sudah
sampai tahap ``repair.py`` maka gabungkan::

    $ ~/env/bin/python csv_concat.py hp

Nanti akan terbentuk ``hp.csv``. Aktifkan web server::

    $ ~/env/bin/streamlit run hp_finder.py hp.csv

Atau cukup::

    $ ~/env/bin/streamlit run hp_finder.py


Rutinitas
---------

Seluruh langkah untuk mendapatkan ``laptop.csv`` tadi telah terangkum dalam ``crawler.py``. Salinlah file konfigurasinya::

    $ cp laptop.ini live-laptop.ini

Sesuaikanlah nilai ``base_download_dir`` bila perlu. Kemudian jalankan::

    $ ~/env/bin/python crawler.py live-laptop.ini

Untuk kategori lainnya ada di file ``hp.ini``, ``mobo.ini``, ``gpu.ini``, dan
``storage.ini``. Tentu saja kita bisa membuat kategori lainnya. Tirulah.

Jika Anda peduli dengan perubahan harga, stok, atau data lainnya maka
**keesokan harinya** hapus dulu semua data dengan cara (**HATI-HATI**)::

    $ ~/env/bin/python remove_data.py live-laptop.ini

Bila tidak dihapus maka script tidak akan memperbarui.

Kadang AI memberikan format JSON yang kurang pas - misalnya kelebihan karakter
koma - maka cukup **jalankan lagi**. Biasanya AI memberi jawaban berbeda dengan
format JSON yang benar.

Hasilnya bisa dilihat di:

1. `Laptop Finder <https://s.id/laptop-dijual>`_
2. `HP Finder <https://s.id/hp-dijual>`_
3. `Motherboard Finder <https://s.id/mobo-dijual>`_
4. `GPU Finder <https://gpu-finder.streamlit.app>`_
5. `Storage Finder <https://storage-finder.streamlit.app>`_
6. `PSU Finder <https://psu-finder.streamlit.app>`_


Perbaikan
---------

Misalkan saat kita melihat-lihat data melalui web menemukan kesalahan.
**Setelah melakukan perbaikan** cobalah hapus salah satu tautan yang bermasalah tadi::

    $ ~/env/bin/python remove_by_filter.py --csv-file=hp-samsung.csv --filter="url == 'https://www.tokopedia.com/samsung/samsung-galaxy-a05s-6-128gb-silver-e3ea5'"

Tujuannya agar lebih cepat pembuktiannya. Kemudian jalankan lagi proses pembacaan spesifikasi::

    $ ~/env/bin/python to_category.py live-hp.ini --input-file=tokopedia-samsung.csv --output-file=hp-samsung.csv --filter="url == 'https://www.tokopedia.com/samsung/samsung-galaxy-a05s-6-128gb-silver-e3ea5'"
    $ ~/env/bin/python repair.py live-hp.ini --csv-file=hp-samsung.csv

Lihat hasilnya apa sudah sesuai::

    $ ~/env/bin/python check.py live-hp.ini --csv-file=hp-samsung.csv --filter="url == 'https://www.tokopedia.com/samsung/samsung-galaxy-a05s-6-128gb-silver-e3ea5'"

Kalau sudah sesuai gabungkan lagi semuanya::

    $ ~/env/bin/python csv_concat.py hp

Lalu lihat hasilnya di web::

    $ ~/env/bin/streamlit run hp_finder.py

Semoga berhasil.
