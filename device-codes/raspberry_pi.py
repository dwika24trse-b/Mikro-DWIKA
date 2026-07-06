#!/usr/bin/env python3
"""
MoniQuarium - Raspberry Pi IoT Client
Membaca data ADC (menggunakan MCP3008 / simulasi) dan mengirim data ke Web Backend Server.

Instalasi library pendukung:
pip install requests

Jika menggunakan chip ADC MCP3008 fisik:
pip install adafruit-circuitpython-mcp3008
"""

import time
import random
import requests

# Konfigurasi Server (Ubah [IP_ADDRESS_SERVER] dengan IP laptop/server Anda)
SERVER_URL = "http://localhost:5000/api/data"

# Jika Anda memiliki hardware ADC MCP3008 fisik yang terhubung di Raspberry Pi,
# Anda dapat menghapus komentar pada blok di bawah ini untuk membaca data sensor asli:
"""
import busio
import digitalio
import board
import adafruit_mcp3008.mcp3008 as MCP
from adafruit_mcp3008.analog_in import AnalogIn

# Inisialisasi SPI bus dan chip select
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5) # Gunakan pin GPIO 5 sebagai Chip Select
mcp = MCP.MCP3008(spi, cs)

# Hubungkan pin analog MCP3008 dengan pin sensor
chan_temp = AnalogIn(mcp, MCP.P0)  # Pin CH0 untuk Suhu
chan_ph = AnalogIn(mcp, MCP.P1)    # Pin CH1 untuk pH
chan_turb = AnalogIn(mcp, MCP.P2)  # Pin CH2 untuk Kekeruhan
chan_level = AnalogIn(mcp, MCP.P3) # Pin CH3 untuk Level Air
"""

def read_sensors():
    """
    Fungsi membaca data sensor.
    Menggunakan data simulasi secara default. Aktifkan blok di atas untuk membaca ADC fisik.
    """
    try:
        # CONTOH BACA DARI ADC FISIK (Uncomment jika menggunakan hardware):
        # adc_temp_voltage = chan_temp.voltage
        # temperature = (adc_temp_voltage * 100) # Contoh sensor LM35: 10mV/C
        # ph = (chan_ph.voltage * 3.5)           # Contoh kalibrasi pH
        # turbidity = (chan_turb.value / 65535.0) * 100.0
        # water_level = (chan_level.value / 65535.0) * 100.0
        
        # JIKA HARDWARE BELUM ADA, GUNAKAN SIMULASI DATA ADC DI BAWAH INI:
        temperature = round(random.uniform(23.0, 27.5), 2)  # Target: 22-28
        ph = round(random.uniform(6.8, 7.8), 2)             # Target: 6.5-8.5
        turbidity = round(random.uniform(85.0, 98.0), 2)     # Target: >80
        water_level = round(random.uniform(75.0, 90.0), 2)   # Target: 70-95
        
    except Exception as e:
        print(f"Error membaca hardware ADC: {e}. Menggunakan data fallback simulasi.")
        temperature = round(random.uniform(22.0, 29.0), 2)
        ph = round(random.uniform(6.0, 9.0), 2)
        turbidity = round(random.uniform(50.0, 100.0), 2)
        water_level = round(random.uniform(40.0, 98.0), 2)
        
    return {
        "temperature": temperature,
        "ph": ph,
        "turbidity": turbidity,
        "water_level": water_level
    }

def main():
    print("=== MoniQuarium Raspberry Pi Client Dimulai ===")
    print(f"Mengirim data ke: {SERVER_URL}")
    print("Tekan Ctrl+C untuk menghentikan program.")
    
    while True:
        sensor_data = read_sensors()
        print(f"\nMembaca data sensor: {sensor_data}")
        
        try:
            # Mengirim HTTP POST ke server Express/Flask
            response = requests.post(SERVER_URL, json=sensor_data, timeout=5)
            if response.status_code == 201:
                print("Berhasil mengirim data ke server.")
            else:
                print(f"Gagal mengirim data. Kode respon server: {response.status_code}")
                print(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error koneksi ke server: {e}")
            
        # Kirim data setiap 10 detik
        time.sleep(10)

if __name__ == "__main__":
    main()
