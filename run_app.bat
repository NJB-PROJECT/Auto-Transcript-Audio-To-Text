@echo off
TITLE Audio to Text Installer
CLS

echo ========================================================
echo   AUDIO TO TEXT - INSTALLER & RUNNER
echo ========================================================
echo.

:: 1. Check Path Length Warning
set "CURRENT_DIR=%CD%"
if "%CURRENT_DIR:~60%" neq "" (
    echo [WARNING] Path folder Anda terlihat sangat panjang!
    echo "%CURRENT_DIR%"
    echo.
    echo Masalah ini sering menyebabkan GAGAL saat membuat Virtual Environment.
    echo SANGAT DISARANKAN untuk memindahkan folder ini ke:
    echo    C:\AudioToText
    echo atau lokasi pendek lainnya sebelum melanjutkan.
    echo.
    pause
)

:: 2. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak terdeteksi! Mohon instal Python 3.10+ terlebih dahulu.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b
)

:: 3. Setup Venv
if not exist "venv" (
    echo [INFO] Membuat Virtual Environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [FATAL ERROR] Gagal membuat venv.
        echo Mohon pindahkan folder project ke lokasi yang lebih pendek (misal C:\Project) dan coba lagi.
        pause
        exit /b
    )
)

echo [INFO] Mengaktifkan Venv...
call venv\Scripts\activate

:: 4. Install Requirements
echo [INFO] Menginstal library dasar...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Ada masalah saat install library dasar. Mencoba lanjut...
)

:: 5. Install Audio Library (Smart Try)
echo [INFO] Menginstal driver audio...
pip show pyaudiowpatch >nul 2>&1
if %errorlevel% neq 0 (
    echo    Mencoba install pyaudiowpatch (untuk rekam Zoom)...
    pip install pyaudiowpatch
    if %errorlevel% neq 0 (
        echo    [X] Gagal install pyaudiowpatch (Mungkin tidak support versi Windows/Python ini).
        echo    [!] Mencoba fallback ke PyAudio standar...
        pip install pyaudio
    ) else (
        echo    [OK] Driver Zoom berhasil diinstal.
    )
)

:: 6. Run App
echo.
echo ========================================================
echo   MEMULAI APLIKASI...
echo ========================================================
echo.
python src/main.py

pause
