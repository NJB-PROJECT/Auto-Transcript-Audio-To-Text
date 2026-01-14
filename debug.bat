@echo off
TITLE DEBUG MODE - Audio to Text
echo ========================================================
echo   MODE DEBUG - Cek Error Langkah demi Langkah
echo ========================================================
echo.

echo 1. Mengecek lokasi folder (Path)...
echo    Anda berada di: %CD%
echo.
echo    [PENTING] Jika path ini terlalu panjang, ERROR akan terjadi.
pause

echo.
echo 2. Mengecek Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak terdeteksi!
) else (
    echo [OK] Python terdeteksi.
)
pause

echo.
echo 3. Mencoba membuat Virtual Environment (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo [FATAL ERROR] Gagal membuat venv!
    echo Kemungkinan path terlalu panjang atau akses ditolak.
    echo SOLUSI: Pindahkan folder project ini ke C:\AudioApp lalu coba lagi.
) else (
    echo [OK] venv berhasil dibuat.
)
pause

echo.
echo 4. Mengaktifkan venv...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Gagal aktivasi venv.
) else (
    echo [OK] venv aktif.
)
pause

echo.
echo 5. Install Library...
pip install -r requirements.txt
echo [INFO] Selesai install standard library.

echo.
echo 6. Cek & Install Audio Driver (Zoom Loopback)...
pip install pyaudiowpatch
if %errorlevel% neq 0 (
    echo [INFO] Gagal install pyaudiowpatch. Fallback ke pyaudio standard...
    pip install pyaudio
)
pause

echo.
echo 7. Menjalankan Aplikasi...
python src/main.py
if %errorlevel% neq 0 (
    echo [ERROR] Aplikasi crash / error saat dijalankan.
    echo Lihat pesan error di atas.
)

echo.
echo Selesai. Tekan tombol apa saja untuk keluar.
pause
