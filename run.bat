@echo off
title MoniQuarium Starter
echo ===================================================
echo             MONIQUARIUM AUTOMATIC RUNNER
echo ===================================================
echo.

:: 1. Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak terdeteksi! Silakan instal Python 3 terlebih dahulu.
    pause
    exit /b
)

:: 2. Instal dependencies
echo [1/4] Menginstal dependencies Python yang diperlukan...
python -m pip install flask flask-cors mysql-connector-python requests
if %errorlevel% neq 0 (
    echo [WARNING] Gagal menginstal beberapa package. Pastikan Anda terhubung ke internet.
)
echo.

:: 3. Jalankan server Flask di background
echo [2/4] Menjalankan Server Backend (app.py) di jendela baru...
start "MoniQuarium Server" cmd /k "python app.py"

:: Tunggu 2 detik agar server menyala terlebih dahulu
ping 127.0.0.1 -n 3 >nul

:: 4. Jalankan Simulator IoT di background
echo [3/4] Menjalankan Simulator Sensor (simulator.py) di jendela baru...
start "MoniQuarium Simulator" cmd /k "python simulator.py"

:: 5. Buka Browser
echo [4/4] Membuka Dashboard di Web Browser...
start http://localhost:5000

echo.
echo ===================================================
echo [SUKSES] Semua service telah dijalankan!
echo - Server: http://localhost:5000
echo - Anda dapat menutup jendela ini.
echo ===================================================
ping 127.0.0.1 -n 6 >nul
