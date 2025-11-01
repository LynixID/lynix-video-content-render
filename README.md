# Short Template Generator (ffmpeg)

Prototipe Streamlit untuk menghasilkan video portrait (1080x1920) ala YouTube Shorts dari template yang direkam di screenshot.

Fitur prototipe:
- Upload content video (utama)
- Upload background (image/video) optional
- Input header hook text
- Input top-comment (author, text, likes)
- Menghasilkan MP4 via ffmpeg

Persyaratan
- Python 3.8+
- ffmpeg (harus terinstall dan ada di PATH)

Install (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Setelah meng-install paket, jika Anda menambahkan rendering HTML (Playwright) jalankan instalasi browser:

```powershell
python -m pip install playwright
python -m playwright install
```

Jalankan aplikasi:
```powershell
streamlit run app.py
```

Catatan
- ffmpeg harus tersedia di PATH. Jika tidak, install dari https://ffmpeg.org dan pastikan `ffmpeg` dan `ffprobe` bisa dipanggil dari terminal.
- Prototipe ini menggunakan ffmpeg filtergraph sederhana. Anda dapat menyesuaikan ukuran frame atau posisi overlay di `video_utils.py`.
