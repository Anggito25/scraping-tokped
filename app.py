from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Input URL
url = input("Masukkan URL review Tokopedia: ")

# Setup browser
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get(url)

# Scroll pelan-pelan untuk memicu lazy-loading review
SCROLL_PAUSE_TIME = 3
last_height = driver.execute_script("return document.body.scrollHeight")

for i in range(10):  # scroll 10 kali (bisa diubah)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Setelah semua ulasan dimuat, ambil source-nya
soup = BeautifulSoup(driver.page_source, "html.parser")
containers = soup.find_all("article")

data = []

for container in containers:
    try:
        nama_tag = container.find("span", class_="name")
        nama = nama_tag.text.strip() if nama_tag else "Tidak ditemukan"

        tipe = container.find("p", class_="css-d2yr2-unf-heading e1qvo2ff8") or container.find("p", class_="css-ra461b-unf-heading")
        tipe_barang = tipe.text.strip() if tipe else "Tidak ditemukan"

        ulasan_tag = container.find("span", attrs={"data-testid": "lblItemUlasan"})
        ulasan = ulasan_tag.text.strip() if ulasan_tag else "Tidak ditemukan"

        try:
            rating_div = container.find("div", {'data-testid': 'icnStarRating'})
            rating = rating_div['aria-label'].split()[1] if rating_div else "Tidak ditemukan"
        except:
            rating = "Tidak ditemukan"

        tanggal = container.find("p", class_="css-1rpz5os-unf-heading e1qvo2ff8")
        tanggal = tanggal.text.strip() if tanggal else "Tidak ditemukan"

        data.append({
            "Nama": nama,
            "Tipe Barang": tipe_barang,
            "Ulasan": ulasan,
            "Rating": rating,
            "Tanggal": tanggal
        })
    except:
        continue

driver.quit()

# Simpan ke file
df = pd.DataFrame(data)
df.to_csv("tokopedia_reviews.csv", index=False, encoding="utf-8-sig")

print(f"🎉 Scraping selesai. Total ulasan berhasil dikumpulkan: {len(df)}")
