# 🐠 MoniQuarium - Monitoring Aquarium Pintar

Aplikasi web modern, cantik, dan elegan bertema **Glassmorphic Dark Mode** untuk memantau data sensor ADC dari mikrokontroler (Arduino, ESP32, Raspberry Pi) ke database MySQL/SQLite. Data divisualisasikan dalam bentuk grafik interaktif, tabel log historis, dan didukung fitur ekspor file (CSV & PNG).

---

## 🚀 Fitur Utama
1. **Penyimpanan Data Sensor**: Menerima data dari IoT (ESP32/Arduino/Raspberry Pi) melalui endpoint API HTTP POST dan menyimpannya ke MySQL.
2. **Fallback Cerdas**: Jika MySQL tidak dikonfigurasi, sistem otomatis beralih ke database SQLite lokal (`aquarium.db`) agar aplikasi dapat langsung dijalankan tanpa setup database yang rumit.
3. **Visualisasi Grafik Real-time**: Grafik interaktif menggunakan Chart.js untuk memantau tren suhu, pH, kejernihan, dan ketinggian air secara real-time.
4. **Export to PNG**: Menyimpan tangkapan gambar grafik visualisasi ke dalam file PNG resolusi tinggi.
5. **Export to CSV**: Mengunduh seluruh tabel data sensor historis ke dalam bentuk file spreadsheet CSV.
6. **Integrasi IoT**: Panduan endpoint API yang interaktif beserta contoh kode device untuk ESP32 (Arduino C++) dan Raspberry Pi (Python).

---

## 📁 Struktur Folder
```text
aquarium-monitoring/
├── public/                 # File Front-end Statis
│   ├── index.html          # Struktur Dashboard Halaman Utama
│   ├── style.css           # Styling Glassmorphism & Animasi Bubble
│   └── app.js              # Logika Chart, Tabel, Fetching & Ekspor
├── device-codes/           # Contoh Program Mikrokontroler/Klien
│   ├── esp32_arduino.ino   # Sketch ESP32 (Arduino IDE)
│   └── raspberry_pi.py     # Script Python Raspberry Pi
├── app.py                  # Server Backend Flask (Python)
├── simulator.py            # Script Simulator IoT (Sangat Membantu Testing!)
├── schema.sql              # Skema Inisialisasi Database MySQL
├── .env                    # Konfigurasi Database & Port
└── README.md               # Dokumentasi Panduan Ini
```

---

## 🛠️ Cara Menjalankan Aplikasi

### 1. Prasyarat
Pastikan komputer Anda sudah terinstal **Python 3**.

### 2. Menginstal Dependencies
Buka terminal/PowerShell di direktori proyek ini, lalu jalankan perintah:
```bash
python -m pip install flask flask-cors mysql-connector-python
```

### 3. Mengatur Database (Opsional - Jika Ingin Menggunakan MySQL)
1. Buat database baru bernama `aquarium_db` di server MySQL Anda menggunakan tools seperti phpMyAdmin atau MySQL Workbench, atau jalankan kode dari file `schema.sql`.
2. Buka file `.env` di proyek ini dan lengkapi detail koneksi MySQL Anda:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=password_mysql_anda
   DB_NAME=aquarium_db
   ```
*Catatan: Jika variabel ini dikosongkan, sistem otomatis membuat dan menggunakan database SQLite lokal bernama `aquarium.db`.*

### 4. Menjalankan Server Backend
Jalankan server menggunakan perintah:
```bash
python app.py
```
Server akan aktif di alamat: `http://localhost:5000`

Buka browser Anda dan akses `http://localhost:5000` untuk melihat dashboard.

### 5. Menjalankan Simulator Data Sensor (Untuk Menguji Grafik & Tabel)
Agar grafik langsung terisi dengan kurva fluktuasi air yang indah dan dinamis, buka terminal baru di direktori yang sama, lalu jalankan script simulator:
```bash
python simulator.py
```
Script ini akan:
- Menyemai (*seed*) 30 data historis awal ke database agar grafik langsung terisi.
- Mengirim data sensor simulasi baru setiap 3 detik untuk memperlihatkan animasi grafik dan indikator kartu yang bergerak secara real-time.

---

## 🔌 Cara Menghubungkan Mikrokontroler (ESP32 / Raspberry Pi)
1. Sambungkan sensor (Suhu, pH, Turbidity, Ultrasonic/Water Level) ke pin ADC mikrokontroler Anda.
2. Gunakan contoh program yang ada di dalam folder `device-codes/`.
3. Sesuaikan alamat IP Server Web di dalam kode device ke alamat IP server lokal laptop/PC Anda yang menjalankan `app.py`.
4. Unggah kode tersebut. Mikrokontroler akan mengirim data dengan format JSON via HTTP POST ke:
   `http://[IP_SERVER_ANDA]:5000/api/data`
