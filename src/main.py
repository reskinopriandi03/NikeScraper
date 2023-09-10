#this code is scraping kids shoes but still error, scraping from url search query kids shoes then scraping product name, categories, price, original price, and then get in to product link to scrap img url, size, review||revewer, but img url, size and review||reviewer still eror...

import os
import pandas as pd
from bs4 import BeautifulSoup
import csv
import time

# Buka situs web dan ambil respons HTML
from selenium import webdriver

# Inisialisasi URL
url = 'https://www.nike.com/id/w?q=kids%20shoes&vst=kids%20shoes'

# Inisialisasi WebDriver dengan jalur ke chromedriver.exe
driver = webdriver.Chrome(executable_path='C:/Users/User/Downloads/chromedriver.exe')


driver.get(url)

# Scroll ke bawah hingga akhir halaman untuk memuat semua produk
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Tunggu beberapa detik untuk memuat konten baru
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Ambil konten HTML setelah semua produk dimuat
page_source = driver.page_source

# Simpan respons HTML ke file response.html
with open('response.html', 'w', encoding='utf-8') as response_file:
    response_file.write(page_source)

# Tutup browser
driver.quit()

# Baca konten HTML dari file response.html
with open('response.html', 'r', encoding='utf-8') as response_file:
    page_source = response_file.read()

# Parse konten HTML dengan BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')
product_cards = soup.find_all('div', class_='product-card')

products = []

# Inisialisasi variabel counter
counter = 0

for product in product_cards:
    counter += 1  # Menambahkan 1 pada counter
    print(f'Processing product {counter}')

    product_title = product.find('div', class_='product-card__title').get_text(strip=True)
    product_subtitle = product.find('div', class_='product-card__subtitle').get_text(strip=True)
    product_link = product.find('a', class_='product-card__link-overlay')['href']

    # Cek apakah ada elemen harga produk dalam product-card__price-wrapper
    price_wrapper = product.find('div', class_='product-card__price-wrapper')

    if price_wrapper:
        current_price_elem = price_wrapper.find('div', class_='product-price id__styling is--current-price css-11s12ax')
        current_price = current_price_elem.get_text(strip=True) if current_price_elem else None

        original_price_elem = price_wrapper.find('div', class_='product-price id__styling is--striked-out css-0')
        original_price = original_price_elem.get_text(strip=True) if original_price_elem else None

        # Jika ada harga produk dalam product-card__price-wrapper, gunakan harga tersebut
        if current_price:
            product_price = current_price.replace("\xa0", "").replace(",", "")
        else:
            reduced_price_elem = price_wrapper.find('div', class_='product-price is--current-price css-1ydfahe')
            reduced_price = reduced_price_elem.get_text(strip=True) if reduced_price_elem else None
            if reduced_price:
                product_price = reduced_price.replace("\xa0", "").replace(",", "")
            else:
                product_price = "Tidak Tersedia"
        
        # Periksa apakah ada harga asli, jika tidak, isi dengan "-"
        if original_price:
            product_original_price = original_price.replace("\xa0", "").replace(",", "")
        else:
            product_original_price = "-"

    else:
        product_price_elem = product.find('div', class_='product-price is--current-price css-1ydfahe')
        product_price = product_price_elem.get_text(strip=True).replace("\xa0", "").replace(",", "") if product_price_elem else "Tidak Tersedia"

        # Periksa apakah ada harga asli, jika tidak, isi dengan "-"
        original_price_elem = product.find('div', class_='product-price id__styling is--striked-out css-0')
        if original_price_elem:
            product_original_price = original_price_elem.get_text(strip=True).replace("\xa0", "").replace(",", "")
        else:
            product_original_price = "-"

    # Klik tautan produk untuk masuk ke halaman produk
    driver.get(product_link)

    # Tunggu beberapa detik untuk memastikan halaman produk sudah dimuat
    time.sleep(2)

    # Selanjutnya, Anda dapat mengambil informasi yang Anda perlukan dari halaman produk,
    # seperti image URLs, sizes, dan review||reviewers

    # Image URLs
    image_elements = product.find_all('img', class_='image-component u-full-width')
    image_urls = [img['src'] for img in image_elements]

    # Jika image_urls tidak ditemukan, cari link image dari elemen button
    if not image_urls:
        image_button = product.find('button', class_='ncss-col-sm-12 ncss-col-lg-6 prl0-sm prl2-lg mt4-lg va-sm-t')
        if image_button:
            image_urls = [image_button.find('img')['src']]

    # Sizes
    size_elements = product.find_all('div', class_='css-xf3ahq')
    sizes = [size.text for size in size_elements]

    # Jika sizes tidak ditemukan, cari tautan Size Guide
    if not sizes:
        size_guide_link = product.find('a', href=True, text='Size Guide')
        if size_guide_link:
            sizes = [size_guide_link['href']]

    # Review and Reviewers
    review_data = "Review data not available"  # Inisialisasi dengan pesan default
    details_element = product.find('details', {'data-nr-comp': 'details'})

    if details_element:
        div_element = details_element.find('div', class_='reviews-component')
        if div_element:
            # Ulasan
            review_title = div_element.find('h4', class_='review-title').text
            review_stars = div_element.find('div', class_='star-rating').text
            review_author = div_element.find('p', class_='responsive-body-3-2').text
            review_text = div_element.find('div', {'style': 'overflow-wrap: break-word;'}).text

            # Gabungkan informasi ulasan
            review_data = f'{review_title}\n{review_stars}\n{review_author}\n{review_text}'

    # Kembali ke halaman sebelumnya (produk)
    driver.back()

    products.append({'Product Name': product_title, 'Category': product_subtitle, 'Price': product_price, 'Original Price': product_original_price, 'Product Link': product_link, 'Image URLs': '||'.join(image_urls), 'Sizes': '||'.join(sizes), 'Review||Reviewers': review_data})

# Simpan ke dalam file CSV
# Periksa apakah file CSV sudah ada
if os.path.isfile(product.csv):
    # File CSV sudah ada, buka dalam mode append
    with open(product.csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Product Name', 'Category', 'Price', 'Original Price', 'Product Link', 'Image URLs', 'Sizes', 'Review||Reviewers'])
        for product in products:
            writer.writerow(product)
else:
    # File CSV belum ada, buat file baru
    with open(product.csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Product Name', 'Category', 'Price', 'Original Price', 'Product Link', 'Image URLs', 'Sizes', 'Review||Reviewers'])
        writer.writeheader()
        for product in products:
            writer.writerow(product)

print('Data extraction complete. Product details saved to products.csv.')





