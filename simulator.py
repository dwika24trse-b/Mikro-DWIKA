#!/usr/bin/env python3
"""
MoniQuarium - IoT Simulator Script
Simulator ini digunakan untuk menyuntikkan data sensor akuarium buatan ke server
sehingga grafik dan tabel dapat langsung diisi dengan data historis yang bervariasi.

Cara Penggunaan:
1. Pastikan server web sudah menyala (python app.py)
2. Jalankan simulator:
   python simulator.py
"""

import time
import random
import requests
import sys

SERVER_URL = "http://127.0.0.1:5000/api/data"

def generate_aquarium_data(time_offset_index=0):
    """
    Menghasilkan data sensor akuarium simulasi yang dinamis.
    Memanfaatkan sinusoid untuk membuat grafik terlihat mengalir dan alami.
    """
    # Gunakan fungsi sinus untuk membuat fluktuasi alami yang anggun
    sine_val = (time_offset_index % 60) / 60.0 * 2 * 3.14159
    
    # Suhu ideal: 24C, fluktuasi +- 1.5 derajat
    temperature = round(24.5 + 1.5 * (1.0 if random.random() > 0.8 else 0.0) + (1.2 * (0.5 + 0.5 * (1.0 if time_offset_index % 10 == 0 else 0.0))), 2)
    # Suhu fluktuasi
    temperature = round(24.5 + 1.2 * (0.5 * time_offset_index % 5 == 0) + random.uniform(-0.2, 0.2), 2)
    # Mari kita buat kurva halus
    import math
    temperature = round(25.0 + 1.5 * math.sin(sine_val) + random.uniform(-0.15, 0.15), 2)
    
    # pH ideal: 7.2, fluktuasi +- 0.4
    ph = round(7.3 + 0.3 * math.cos(sine_val * 1.5) + random.uniform(-0.05, 0.05), 2)
    
    # Kekeruhan (Turbidity) - persentase kejernihan air (Target: >80)
    # Terkadang ada penurunan kejernihan sesaat lalu pulih kembali
    turbidity = round(92.0 - 5.0 * abs(math.sin(sine_val / 2.0)) + random.uniform(-0.5, 0.5), 2)
    if turbidity > 100: turbidity = 100.0
    
    # Ketinggian air (Water Level) - persentase (Target: 70-95)
    # Mengalami penguapan lambat atau pengisian air mendadak
    water_level = round(82.0 + 3.0 * math.sin(sine_val / 4.0) + random.uniform(-0.2, 0.2), 2)
    
    return {
        "temperature": temperature,
        "ph": ph,
        "turbidity": turbidity,
        "water_level": water_level
    }

def seed_database(count=30):
    """Mengisi database dengan data historis awal agar grafik terlihat cantik saat pertama kali dibuka."""
    print(f"Menyemai (seeding) {count} data historis ke server...")
    
    # Jalankan request berurutan
    for i in range(count):
        data = generate_aquarium_data(i)
        try:
            # Mengirim data sensor ke API POST
            # Kita bisa memodifikasi server untuk membiarkan created_at disimulasikan, 
            # tetapi untuk kemudahan simulasi lokal, kita kirimkan data secara cepat.
            # Agar timestamp sedikit berbeda di database, kita beri jeda sangat kecil atau biarkan bertambah secara berurutan.
            response = requests.post(SERVER_URL, json=data, timeout=3)
            if response.status_code == 201:
                sys.stdout.write(".")
                sys.stdout.flush()
            else:
                print(f"\nGagal menyemai data ke-{i+1}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"\nKoneksi server gagal saat seeding: {e}")
            print("Harap nyalakan server terlebih dahulu dengan menjalankan: python app.py")
            return False
        time.sleep(0.05) # Jeda kecil agar ID / Timestamp terdistribusi berurutan
        
    print("\nPenyemaian database selesai!")
    return True

def main():
    print("=========================================")
    print("    SIMULATOR IOT MONITORING AQUARIUM    ")
    print("=========================================")
    
    # Pertama, lakukan seeding database agar grafik langsung terisi
    success = seed_database(30)
    if not success:
        print("Gagal menyemai database. Simulator dihentikan.")
        return

    print("\nMemulai loop simulasi real-time.")
    print("Mengirim data baru setiap 3 detik. Tekan Ctrl+C untuk berhenti.\n")
    
    step = 30
    try:
        while True:
            data = generate_aquarium_data(step)
            try:
                response = requests.post(SERVER_URL, json=data, timeout=3)
                if response.status_code == 201:
                    print(f"[{time.strftime('%H:%M:%S')}] Terkirim: Suhu={data['temperature']}°C, pH={data['ph']}, Keruh={data['turbidity']}%, Level={data['water_level']}% (Sukses)")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Gagal mengirim: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[{time.strftime('%H:%M:%S')}] Server tidak merespon: {e}")
                
            step += 1
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nSimulator dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
