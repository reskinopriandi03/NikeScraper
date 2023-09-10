


import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import json
import os

# Inisialisasi browser Selenium
url = "https://www.nike.com/id/w/kids-hats-55olazv4dh"
driver = webdriver.Chrome()  # Anda perlu mengunduh driver sesuai dengan browser yang Anda gunakan
driver.get(url)

# Scrolling ke bawah untuk memuat semua produk
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Tunggu beberapa detik untuk memuat produk tambahan
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Jika file hat_response.html sudah ada, hapus dan buat baru
if os.path.exists("hat_response.html"):
    os.remove("hat_response.html")
with open("hat_response.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

# Buka file hat_response.html dan lakukan proses scraping pada file tersebut
with open("hat_response.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Mengambil link produk
product_links = [link["href"] for link in soup.find_all("a", class_="product-card__link-overlay")]

# Jika file hat.csv sudah ada, hapus dan buat baru dengan header
if os.path.exists("hat.csv"):
    os.remove("hat.csv")
with open("hat.csv", mode="w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Nama Produk", "Kategori", "Harga", "Harga Asli", "Diskon", "Image URLs", "Ukuran", "Ulasan", "Jumlah Reviewer", "Varian"])

# Jika file hat.json sudah ada, hapus dan buat baru dengan data kosong
if os.path.exists("hat.json"):
    os.remove("hat.json")
with open("hat.json", mode="w", encoding="utf-8") as json_file:
    json.dump([], json_file, ensure_ascii=False, indent=4)

# Loop melalui setiap link produk
for index, product_link in enumerate(product_links, start=1):
    if product_link.startswith("https://www.nike.com"):
        product_url = product_link
    else:
        product_url = f"https://www.nike.com{product_link}"
    print(f"Attempting to navigate to {product_url}")
    try:
        driver.get(product_url)
    except Exception as e:
        print(f"Failed to navigate to {product_url}. Error: {e}")
        continue

    # Parsing HTML dengan BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Mengambil informasi produk seperti yang Anda lakukan sebelumnya
    nama_produk_element = soup.find("h1")
    if nama_produk_element:
        nama_produk = nama_produk_element.text.strip()
    else:
        nama_produk = "Nama Produk Tidak Ditemukan"
    kategori = soup.find("h2", class_="headline-5 pb1-sm d-sm-ib").text.strip()

    # Coba temukan harga dengan class_="product-price css-11s12ax is--current-price css-tpaepq"
    harga_element = soup.find("div", class_="product-price css-11s12ax is--current-price css-tpaepq")
    if harga_element:
        harga = harga_element.text.strip()
        ori_price = "-"
        discount = "-"
    else:
        # Jika tidak dapat menemukan harga dengan class_="product-price css-11s12ax is--current-price css-tpaepq",
        # coba temukan harga dengan class_="product-price is--current-price css-s56yt7 css-xq7tty"
        harga_element = soup.find("div", class_="product-price is--current-price css-s56yt7 css-xq7tty")
        if harga_element:
            harga = harga_element.text.strip()
            ori_price_element = soup.find("span", class_="visually-hidden")
            if ori_price_element:
                ori_price = ori_price_element.next_sibling.strip()
            else:
                ori_price = "-"
            discount_element = soup.find("span", class_="css-1umcwok")
            if discount_element:
                discount = discount_element.text.strip()
            else:
                discount = "-"
        else:
            # Jika masih tidak dapat menemukan harga, tetapkan sebagai "Harga Tidak Ditemukan"
            harga = "Harga Tidak Ditemukan"
            ori_price = "-"
            discount = "-"

    # Mengambil informasi varian dari fieldset dengan class "colorway-images ta-sm-c d-lg-t"
    variant_fieldset = soup.find("fieldset", class_="colorway-images ta-sm-c d-lg-t")
    if variant_fieldset:
        variant_elements = variant_fieldset.find_all("img", {"alt": True})
        variant_list = []
        for variant_element in variant_elements:
            variant_text = variant_element["alt"]
            variant_list.append(variant_text)
        variants = ", ".join(variant_list)
    else:
        variants = "Varian Tidak Ditemukan"

    image_urls = [img["src"] for img in soup.find_all("img", {"alt": True})]
    size_header_element = soup.find("span", class_="sizeHeader")
    if size_header_element and size_header_element.text.strip() == "ONE SIZE":
        sizes = "ONE SIZE"
    elif size_header_element and size_header_element.text.strip() == "Select Size":
        size_elements = soup.find_all("input", class_="visually-hidden")
        size_list = []
        for size_element in size_elements:
            if not size_element.has_attr("disabled"):
                # Find the corresponding label element
                label_element = soup.find("label", class_="css-xf3ahq")
                if label_element:
                    # Extract and append the text from the label element
                    size_text = label_element.text.strip()
                    size_list.append(size_text)
        sizes = ", ".join(size_list)
    else:
        sizes = "Ukuran Tidak Ditemukan"
    ulasan = soup.find("p", class_="d-sm-ib pl4-sm").text.strip()
    jumlah_reviewer = soup.find("h3", class_="headline-4 css-xd87ek").text.strip()

    # Tampilkan nomor produk dan nama produk di terminal
    print(f"Produk ke-{index}: {nama_produk}")

    # Simpan hasil dalam file CSV
    with open("hat.csv", mode="a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([nama_produk, kategori, harga, ori_price, discount, image_urls, sizes, ulasan, jumlah_reviewer, variants])

    # Buka file hat.json dan tambahkan data baru
    with open("hat.json", mode="r+", encoding="utf-8") as json_file:
        data = json.load(json_file)
        data.append({
            "Nama Produk": nama_produk,
            "Kategori": kategori,
            "Harga": harga,
            "Harga Asli": ori_price,
            "Diskon": discount,
            "Image URLs": image_urls,
            "Ukuran": sizes,
            "Ulasan": ulasan,
            "Jumlah Reviewer": jumlah_reviewer,
            "Varian": variants
        })
        json_file.seek(0)
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"Data produk {nama_produk} telah disimpan.")

# Tutup browser Selenium
driver.quit()
