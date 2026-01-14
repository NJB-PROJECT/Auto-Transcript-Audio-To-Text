# Panduan Instalasi dan Pembuatan EXE (Windows)

Aplikasi ini menggunakan **Faster Whisper** (AI Offline), **Flet** (UI Modern), dan **PyAudioWPatch** (Perekam Audio System/Loopback).

## Cara Menjalankan (Paling Mudah)

1.  **Penting:** Jika folder ini berada di dalam folder yang sangat dalam (misal `Downloads/Compressed/...`), **Pindahkan folder ini ke lokasi pendek**, misalnya `C:\AudioToText`. Ini untuk mencegah error Windows.
2.  Klik dua kali file **`run_app.bat`**.
3.  Tunggu proses instalasi selesai otomatis. Aplikasi akan terbuka.

---

## Troubleshooting

- **Gagal saat instalasi (`venv` error)**:
  Pastikan Anda sudah memindahkan folder project ke `C:\` atau `D:\` langsung agar path tidak kepanjangan.

- **"System Loopback not found" / Peringatan di Aplikasi**:
  Jika tombol rekam berubah menjadi "Microphone Only", artinya driver khusus Zoom tidak kompatibel dengan komputer Anda. Aplikasi tetap bisa dipakai untuk merekam via Microphone (dekatkan speaker ke mic).

- **Aplikasi lambat**:
  Model `small` membutuhkan CPU yang lumayan. Jika terlalu berat, edit file `src/main.py` dan ubah `model_size="small"` menjadi `model_size="base"` atau `model_size="tiny"`.

## 3. Membuat File EXE (Manual)

Jika ingin membuat `.exe` sendiri:

1.  Masuk ke venv: `venv\Scripts\activate`
2.  Instal PyInstaller: `pip install pyinstaller`
3.  Build:
    ```powershell
    pyinstaller --name "AudioToText" --onefile --windowed --add-data "src;src" src/main.py
    ```
