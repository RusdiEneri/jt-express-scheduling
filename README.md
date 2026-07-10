# 🚚 Sistem Automatic Scheduling J&T Express

**Perancangan Sistem Automatic Scheduling untuk Penjadwalan Libur dan Shift Piket Karyawan Menggunakan Metode Algoritma Genetika**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![OpenPyXL](https://img.shields.io/badge/Excel%20Export-OpenPyXL-green)
![License](https://img.shields.io/badge/License-Academic%20Use-orange)

## 📖 Tentang Proyek

Proyek ini merupakan implementasi sistem penjadwalan otomatis untuk departemen GSK08 di J&T Express. Penjadwalan manual seringkali memakan waktu dan rentan terhadap pelanggaran aturan operasional maupun ketidakpuasan karyawan. 

Sistem ini menggunakan **Algoritma Genetika (Genetic Algorithm)** untuk mengoptimalkan pembagian hari libur dan shift piket karyawan. Algoritma ini dirancang untuk mematuhi *Hard Constraints* (aturan mutlak operasional) dan memaksimalkan *Soft Constraints* (permintaan libur spesifik dari karyawan).

## ✨ Fitur Utama

- 📝 **CRUD Data Karyawan Interaktif:** Mengelola data karyawan dan preferensi libur langsung dari antarmuka web menggunakan *dynamic data editor*. Data dapat disimpan secara permanen ke file CSV.
- 🔒 **Algoritma Genetika dengan Gene Locking:** Menangani permintaan libur mutlak (misal: "SETIAP HARI" untuk posisi tertentu) tanpa merusak proses evolusi algoritma.
- ⚖️ **Penyeimbangan Constraints:** 
  - *Hard Constraints:* Memastikan jatah libur yang adil (2 hari/minggu) dan menjaga jumlah minimum karyawan piket per hari.
  - *Soft Constraints:* Memaksimalkan pemenuhan *request* libur hari spesifik (Senin - Minggu).
- 🖥️ **Antarmuka Web Interaktif (Streamlit):** Memungkinkan pengguna (HRD) mengubah parameter algoritma (Populasi, Generasi, Mutation Rate) secara *real-time* tanpa menyentuh kode.
- 📊 **Visualisasi & Analisis:** Menyediakan grafik konvergensi *fitness* dan statistik distribusi piket per hari.
- 📑 **Export Excel Terformat:** Mengunduh hasil penjadwalan dalam format `.xlsx` dengan *styling* profesional (pewarnaan sel otomatis untuk status LIBUR, PIKET, dan LOCKED).

## 📁 Struktur Direktori
```text
jt-express-scheduling/
├── src/ # Source code utama
│ ├── app.py # Aplikasi Web Streamlit (UI, CRUD, Integrasi)
│ ├── genetic_algorithm/ # Logika inti Algoritma Genetika (Engine, Fitness, Chromosome)
│ ├── preprocessing/ # Script pembersihan & transformasi data (Matrix Builder)
│ ├── services/ # Business logic & utilities
│ └── utils/ # Helper functions & visualizations
├── data/ # Penyimpanan dataset
│ ├── raw/ # Data mentah (dataset_clean.csv)
│ └── processed/ # Data hasil preprocessing
├── results/ # Output dari sistem
│ ├── schedules/ # File Excel/CSV hasil penjadwalan
│ └── visualizations/ # Grafik PNG
├── docs/ # Dokumentasi, laporan skripsi, & slide
├── requirements.txt # Daftar dependensi Python
└── README.md # Dokumentasi proyek ini
```

## ⚙️ Prasyarat

Sebelum menjalankan proyek ini, pastikan Anda telah menginstal:
1. **Python** versi 3.8 atau lebih baru ([Download Python](https://www.python.org/downloads/)).
2. **Git** (Opsional, untuk clone repository).
3. **Text Editor** seperti Visual Studio Code (Disarankan).

## 🚀 Instalasi dan Cara Menjalankan

Ikuti langkah-langkah berikut untuk menjalankan sistem di komputer lokal Anda:

### 1. Clone Repository
```bash
git clone https://github.com/RusdiEneri/jt-express-scheduling.git
cd jt-express-scheduling
```

### 2. Buat Virtual Environment (Sangat Disarankan)
```bash
# Untuk Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate

# Untuk macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi Web
Jalankan aplikasi Streamlit dari folder utama proyek:
```bash
streamlit run src/app.py
```

Aplikasi akan otomatis terbuka di browser Anda pada alamat `http://localhost:8501`.

## 📱 Cara Menggunakan Sistem
Aplikasi dibagi menjadi 3 Tab utama untuk memudahkan penggunaan:
1. **Tab 1 - Data Master (CRUD)**:
 - Kelola data karyawan. Tambah, edit, atau hapus baris karyawan langsung di tabel.
 - Atur preferensi libur (Bebas, Hari Spesifik, atau SETIAP HARI).
 - Klik 💾 Simpan Permanen ke CSV untuk menyimpan perubahan ke file database.
2. **Tab 2 - Generate Jadwal**:
 - Atur parameter Algoritma Genetika di sidebar kiri (Populasi, Generasi, Mutation Rate, Min. Piket).
 - Klik 🚀 MULAI GENERATE JADWAL dan pantau proses evolusi melalui progress bar dan status real-time.
3. **Tab 3 - Hasil & Analisis**:
 - Tinjau Tabel Jadwal yang telah diwarnai (Merah = LIBUR, Hijau = PIKET, Abu-abu = LOCKED).
 - Analisis Grafik Konvergensi untuk melihat performa algoritma.
 - Unduh hasil melalui tombol 📥 Download Hasil (Excel .xlsx) atau CSV.

## 📚 Teknologi yang Digunakan
- **Python**: Bahasa pemrograman utama.
- **Streamlit**: Framework untuk membangun antarmuka web interaktif dengan cepat.
- **Pandas & NumPy**: Pengolahan, manipulasi data, dan operasi matriks.
- **Matplotlib**: Visualisasi data dan grafik konvergensi.
- **OpenPyXL**: Mengekspor hasil penjadwalan ke format Excel dengan styling dan formatting profesional.

## 👨‍💻 Penulis

Dikembangkan oleh **Opsional Team** sebagai bagian dari Tugas Akhir.
- **Institusi:** Universitas Internasional Semen Indonesia
- **Program Studi:** Informatika

## 📄 Lisensi

Proyek ini dibuat untuk tujuan akademis dan portofolio. Silakan gunakan dan modifikasi sesuai kebutuhan.