from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import time
import os
import pandas as pd

url = 'https://www.nike.com/id/w?q=kids%20shoes&vst=kids%20shoes'

# Inisialisasi WebDriver (pastikan Anda telah menginstal Selenium dan WebDriver yang sesuai)
driver = webdriver.Chrome()  # Ganti dengan driver yang sesuai jika Anda menggunakan browser lain

driver.get(url)

# Scroll ke bawah hingga akhir halaman untuk memuat semua produk
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(6)  # Tunggu beberapa detik untuk memuat konten baru
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Ambil konten HTML setelah semua produk dimuat
page_source = driver.page_source

# Parse konten HTML dengan BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')
product_cards = soup.find_all('div', class_='product-card')



data = {
    'Product Name': [],
    'Category': [],
    'Product Link': [],
    'Price': [],
    'Original Price': [],
}

for product in product_cards:
    try:
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

            if original_price:
                product_original_price = original_price.replace("\xa0", "").replace(",", "")
            else:
                product_original_price = "-"
        else:
            product_price_elem = product.find('div', class_='product-price is--current-price css-1ydfahe')
            product_price = product_price_elem.get_text(strip=True).replace("\xa0", "").replace(",", "") if product_price_elem else "Tidak Tersedia"

            original_price_elem = product.find('div', class_='product-price id__styling is--striked-out css-0')
            if original_price_elem:
                product_original_price = original_price_elem.get_text(strip=True).replace("\xa0", "").replace(",", "")
            else:
                product_original_price = "-"

        data['Product Name'].append(product_title)
        data['Category'].append(product_subtitle)
        data['Product Link'].append(product_link)
        data['Price'].append(product_price)
        data['Original Price'].append(product_original_price)

    except Exception as e:
        print(f"Error extracting product: {str(e)}")

# Simpan DataFrame ke file CSV
df = pd.DataFrame(data)

# Cek apakah file 'products.csv' sudah ada
file_exists = os.path.isfile('products.csv')

# Jika file sudah ada, tambahkan data baru ke DataFrame yang ada
if file_exists:
    existing_df = pd.read_csv('products.csv')
    df = pd.concat([existing_df, df], ignore_index=True)

df.to_csv('products.csv', index=False)

if file_exists:
    print(f'Data extraction complete. {len(data["Product Name"])} products appended to products.csv.')
else:
    print(f'Data extraction complete. {len(data["Product Name"])} products saved to products.csv.')


print('Data extraction complete. Products, categories, prices, and discounts saved to products.csv.')
