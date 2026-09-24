# 🛒 Proyek Analisis Data: E-Commerce Public Dataset (Olist Brazil)

> **Proyek Akhir:** Belajar Analisis Data dengan Python – Dicoding  
> **Nama:** Salsabila Yufli Ramadhani  
> **Dataset:** [E-Commerce Public Dataset (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## 📋 Deskripsi Proyek

Proyek ini melakukan analisis mendalam terhadap dataset e-commerce publik dari Olist (Brazil) untuk menjawab 5 pertanyaan bisnis SMART, termasuk analisis lanjutan menggunakan **RFM Analysis** dan **Geospatial Analysis**.

### Pertanyaan Bisnis yang Dijawab:
1. 📈 Bagaimana tren jumlah order dan revenue bulanan (Jan 2017 – Agust 2018)?
2. 📦 Kategori produk mana yang menghasilkan revenue dan order terbanyak?
3. 🚚 Berapa persentase keterlambatan pengiriman dan dampaknya terhadap review score?
4. 🎯 Bagaimana segmentasi pelanggan berdasarkan RFM Analysis?
5. 🗺️ State/kota mana yang memiliki pelanggan dan revenue tertinggi?

---

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── dashboard.py        ← Streamlit web app
│   └── main_data.csv       ← Dataset gabungan yang sudah dibersihkan
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb          ← Notebook analisis lengkap
├── README.md               ← File ini
├── requirements.txt        ← Daftar library yang digunakan
└── url.txt                 ← Link Streamlit Cloud deployment
```

---

## ⚙️ Setup & Instalasi

### 1. Clone / Download proyek ini

### 2. Buat virtual environment (opsional tapi disarankan)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install semua dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Dashboard

Pastikan kamu berada di folder `submission/`, lalu jalankan:

```bash
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`

### Fitur Dashboard:
- 🔍 **Filter interaktif** (date range, state, kategori produk) di sidebar
- 📊 **5 KPI Cards** (Total Orders, Revenue, Rating, Customers, Late Delivery %)
- 📈 **Tab Tren Penjualan** – Line chart & bar chart bulanan dengan highlight puncak
- 📦 **Tab Kategori Produk** – Top N kategori by revenue/order (adjustable slider)
- 🚚 **Tab Performa Pengiriman** – Pie chart + distribusi hari pengiriman
- 🎯 **Tab RFM Analysis** – Segmentasi 5 kelompok pelanggan + scatter plot
- 🗺️ **Tab Geospatial** – Heatmap folium interaktif + bar chart revenue per state

---

## 📊 Menjalankan Notebook Analisis

Buka `notebook.ipynb` menggunakan Jupyter:
```bash
jupyter notebook notebook.ipynb
```
atau buka di Google Colab dengan mengupload file notebook-nya.

---

## 🌐 Live Demo

Dashboard tersedia di Streamlit Cloud:  
👉 [Link Streamlit Cloud](url.txt)

---

## 📚 Libraries yang Digunakan

| Library | Kegunaan |
|---------|----------|
| `pandas` | Manipulasi & analisis data |
| `numpy` | Komputasi numerik |
| `matplotlib` | Visualisasi data |
| `seaborn` | Visualisasi statistik |
| `folium` | Peta interaktif geospatial |
| `streamlit` | Web app dashboard |
| `streamlit-folium` | Integrasi folium di Streamlit |

---

## 👤 Author

**Salsabila Yufli Ramadhani**  
Mahasiswa Informatika  
Proyek Akhir: Belajar Analisis Data dengan Python – Dicoding 2026
