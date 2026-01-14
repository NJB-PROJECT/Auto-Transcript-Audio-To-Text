# Panduan Instalasi dan Pembuatan EXE (Windows)

Aplikasi ini menggunakan **Faster Whisper** (AI Offline), **Flet** (UI Modern), dan **PyAudioWPatch** (Perekam Audio System/Loopback).

## 1. Persiapan Lingkungan (Environment)

Pastikan Anda sudah menginstal **Python 3.10 atau lebih baru**.

### Langkah Instalasi
1.  Buka folder proyek ini di Terminal / Command Prompt / VS Code.
2.  Buat virtual environment (opsional tapi disarankan):
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Instal library yang dibutuhkan:
    ```powershell
    pip install -r requirements.txt
    ```
    *Jika terjadi error pada instalasi `pyaudiowpatch`, pastikan Anda memiliki build tools C++ atau coba instal manual via wheel yang sesuai.*

4.  **PENTING: FFmpeg**
    Faster Whisper dan MoviePy membutuhkan FFmpeg.
    - Download FFmpeg dari https://ffmpeg.org/download.html
    - Extract dan masukkan folder `bin` FFmpeg ke dalam **System Environment Variables (PATH)** Windows Anda.
    - Cek dengan mengetik `ffmpeg -version` di terminal.

## 2. Menjalankan Aplikasi
Untuk menjalankan aplikasi secara langsung (mode development):
```powershell
python src/main.py
```
Saat pertama kali dijalankan, aplikasi akan mendownload model AI (sekitar 500MB - 1GB) ke folder cache.

## 3. Membuat File EXE (Executable)

Agar aplikasi bisa dijalankan tanpa membuka VS Code, kita bisa menjadikannya file `.exe`.

1.  Instal PyInstaller:
    ```powershell
    pip install pyinstaller
    ```

2.  Jalankan perintah build:
    ```powershell
    pyinstaller --name "AudioToText" --onefile --windowed --add-data "src;src" src/main.py
    ```
    *Catatan: Parameter `--add-data` mungkin perlu disesuaikan tergantung lokasi file `src` Anda. Jika error, coba jalankan dari dalam folder `src`:*

    ```powershell
    cd src
    pyinstaller --name "AudioToText" --onefile --windowed main.py
    ```

3.  Tunggu proses selesai. File `.exe` akan muncul di folder `dist`.

## Troubleshooting
- **Error "System Loopback not found"**: Pastikan speaker laptop Anda aktif dan tidak di-mute total (kalau mute output speaker masih oke, tapi device harus aktif).
- **Aplikasi lambat**: Model `small` membutuhkan CPU yang lumayan. Jika terlalu berat, edit file `src/main.py` dan ubah `model_size="small"` menjadi `model_size="base"` atau `model_size="tiny"`.
