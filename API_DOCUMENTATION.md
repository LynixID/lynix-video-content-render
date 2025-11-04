# Dokumentasi API Video Render

## Endpoint
```
POST /render
```

## Authentication
API menggunakan Bearer Token authentication. Token harus disertakan dalam header.

**Token:** `LynixVideoContentGenerate88288`

**Header yang didukung:**
- `Authorization: Bearer <token>`
- `X-API-Key: <token>`

---

## Request Body (JSON)

### Parameter Wajib

#### `content_url` (string, **WAJIB**)
- URL video konten yang akan digunakan (format: MP4, MOV, WebM)
- Video akan didownload dan digunakan sebagai konten utama
- Contoh: `"https://v16m.tiktokcdn-us.com/.../video.mp4"`

---

### Parameter Opsional

#### `background_option` (integer, default: `1`)
- Pilihan background template
- **Nilai yang valid:** `1`, `2`, atau `3`
- Sistem akan mencari file di folder `backgrounds/` dengan nama:
  - `bg1.*` (png/jpg/mp4/webm/mov/mkv)
  - `bg2.*`
  - `bg3.*`
- Jika tidak ditemukan, akan dibuat background solid color

#### `header_text` (string, default: `""`)
- Teks header yang akan ditampilkan di bagian atas video
- Teks akan otomatis di-wrap jika terlalu panjang
- Contoh: `"Manusia serigala juga ikut demo"`

#### `comments` (array of objects, default: `[]`)
- Array komentar yang akan ditampilkan (maksimal 2 komentar)
- Setiap komentar adalah object dengan property:
  
  **Property Wajib:**
  - `author` (string): Nama penulis komentar
  - `text` (string): Isi komentar (support emoji dan karakter khusus)
  
  **Property Opsional:**
  - `likes` (integer, default: `0`): Jumlah likes
  - `time` (string, default: `""`): Waktu posting (contoh: "2 h", "2 j")
  - `replies` (string, default: `""`): Jumlah balasan (contoh: "13")
  - `highlight` (boolean, default: `false`): Jika `true`, komentar akan ditampilkan dengan border biru
  - `avatar_url` (string, default: `null`): URL gambar avatar (jpg/png/webp). Avatar akan di-download dan ditampilkan dalam bentuk lingkaran

#### `use_html_renderer` (boolean, default: `false`)
- Jika `true`, akan menggunakan Playwright untuk render komentar dengan HTML/Tailwind CSS
- Jika `false`, akan menggunakan PIL (Python Imaging Library) untuk render
- **Catatan:** Playwright harus terinstall dan browser Chromium harus tersedia

#### `scale` (float, default: `1.0`)
- Faktor skala untuk ukuran komentar
- `1.0` = ukuran normal
- `1.5` = 150% ukuran normal
- `2.0` = 200% ukuran normal
- Mempengaruhi font size, spacing, dan dimensi komentar

#### `max_duration` (float, default: `null`)
- Durasi maksimal video output (dalam detik)
- Jika konten lebih panjang, akan dipotong
- Jika `null` atau tidak diisi, akan menggunakan durasi konten asli
- Contoh: `30` = video maksimal 30 detik

---

## Contoh Request CURL

### 1. Request Minimal (Hanya Content URL)
```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4"
  }' \
  --output result.mp4 \
  --max-time 600
```

### 2. Request dengan Semua Parameter (termasuk Avatar dan Emoji)
```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 2,
    "header_text": "Contoh Header - Testing Video",
    "comments": [
      {
        "author": "UserA",
        "text": "Keren banget kontennya, kasih tipsnya dong! 🔥🔥",
        "likes": 128,
        "time": "2 h",
        "replies": "13",
        "highlight": true,
        "avatar_url": "https://example.com/avatar1.jpg"
      },
      {
        "author": "UserB",
        "text": "Wah ini useful, terima kasih sharingnya. 💯👍",
        "likes": 42,
        "time": "3 j",
        "replies": "5",
        "highlight": false,
        "avatar_url": "https://example.com/avatar2.png"
      }
    ],
    "use_html_renderer": false,
    "scale": 1.5,
    "max_duration": 30
  }' \
  --output result.mp4 \
  --max-time 600
```

### 3. Request dengan HTML Renderer
```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 1,
    "header_text": "Header dengan HTML Renderer",
    "comments": [
      {
        "author": "John Doe",
        "text": "Komentar pertama dengan HTML rendering",
        "likes": 256,
        "highlight": true
      }
    ],
    "use_html_renderer": true,
    "scale": 1.5,
    "max_duration": 45
  }' \
  --output result.mp4 \
  --max-time 600
```

### 4. Request dengan Satu Komentar
```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 3,
    "header_text": "Video Singkat",
    "comments": [
      {
        "author": "Penonton123",
        "text": "Mantap sekali!",
        "likes": 99,
        "highlight": false
      }
    ],
    "scale": 1.0,
    "max_duration": 15
  }' \
  --output result.mp4 \
  --max-time 600
```

### 5. Request Tanpa Header dan Komentar (Hanya Background)
```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 1
  }' \
  --output result.mp4 \
  --max-time 600
```

---

## Format CURL untuk Windows PowerShell

### Menggunakan Escape Quotes
```powershell
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer LynixVideoContentGenerate88288" `
  --data "{\"content_url\":\"https://v16m.tiktokcdn-us.com/.../video.mp4\",\"background_option\":1,\"header_text\":\"Test\",\"comments\":[{\"author\":\"User\",\"text\":\"Komentar\",\"likes\":10}],\"scale\":1.5,\"max_duration\":30}" `
  --output result.mp4 `
  --max-time 600
```

### Menggunakan Here-String (Lebih Mudah)
```powershell
$body = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 1
    header_text = "Test Header"
    comments = @(
        @{
            author = "UserA"
            text = "Komentar pertama"
            likes = 10
            highlight = $true
        }
    )
    scale = 1.5
    max_duration = 30
} | ConvertTo-Json -Depth 10

curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer LynixVideoContentGenerate88288" `
  -d $body `
  --output result.mp4 `
  --max-time 600
```

---

## Format CURL untuk N8N / HTTP Request Node

### JSON Body (dalam N8N)
```json
{
  "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
  "background_option": 1,
  "header_text": "Contoh Header",
  "comments": [
    {
      "author": "UserA",
      "text": "Komen pertama",
      "likes": 12,
      "highlight": true
    },
    {
      "author": "UserB",
      "text": "Komen dua",
      "likes": 5,
      "highlight": false
    }
  ],
  "use_html_renderer": false,
  "scale": 1.5,
  "max_duration": 30
}
```

### Headers (dalam N8N)
```
Content-Type: application/json
Authorization: Bearer LynixVideoContentGenerate88288
```

---

## Response

### Success (200 OK)
- Response berupa file video MP4
- Content-Type: `video/mp4`
- File akan di-download sebagai `result.mp4` (jika menggunakan `--output`)

### Error Responses

#### 400 Bad Request
- `"content_url diperlukan"` - Content URL tidak diisi
- `"background_option harus 1,2 atau 3"` - Background option tidak valid
- `"content_url tidak berisi stream video yang valid"` - URL tidak berisi video

#### 401 Unauthorized
- `"Unauthorized: invalid or missing API key"` - Token tidak valid atau tidak ada

#### 413 Payload Too Large
- `"File terlalu besar"` - File video terlalu besar (max 150MB)

#### 500 Internal Server Error
- `"Background template untuk opsi X tidak ditemukan"` - Background file tidak ditemukan
- `"Gagal membuat video"` - Proses rendering gagal

#### 502 Bad Gateway
- `"Gagal mendownload file"` - Gagal download content dari URL
- `"Gagal menghubungi URL"` - URL tidak dapat diakses
- `"Processing failed on server"` - Error saat processing (cek server logs)

---

## Catatan Penting

1. **Timeout**: Gunakan `--max-time 600` (10 menit) karena rendering video bisa memakan waktu
2. **File Size**: Video output akan di-streaming, pastikan memiliki cukup waktu untuk download
3. **Background Files**: Pastikan file background ada di folder `backgrounds/` dengan format:
   - `bg1.png`, `bg1.jpg`, `bg1.mp4`, dll
   - `bg2.png`, `bg2.jpg`, `bg2.mp4`, dll
   - `bg3.png`, `bg3.jpg`, `bg3.mp4`, dll
4. **Content URL**: URL harus dapat diakses dari server dan berisi video yang valid
5. **HTML Renderer**: Jika menggunakan `use_html_renderer: true`, pastikan Playwright dan Chromium sudah terinstall
6. **Max Comments**: Hanya 2 komentar pertama yang akan digunakan (comments[0] dan comments[1])
7. **Avatar URL**: 
   - Format yang didukung: JPG, PNG, WebP
   - Maksimal ukuran: 5MB
   - Avatar akan di-download dan ditampilkan dalam bentuk lingkaran
   - Jika avatar gagal di-download, akan menggunakan placeholder abu-abu
8. **Emoji Support**: 
   - Komentar mendukung emoji dan karakter khusus (Unicode)
   - Sistem akan mencoba menggunakan font yang mendukung emoji jika tersedia
   - Emoji akan ditampilkan dengan baik di HTML renderer (Playwright)

---

## Spesifikasi Video Output

- **Resolution:** 1080x1920 (Portrait - YouTube Shorts / TikTok format)
- **Format:** MP4 (H.264 video, AAC audio)
- **Content Width:** 90% dari lebar frame (972px)
- **Content Position:** Centered
- **Header Height:** 160px (default)
- **Background:** Scaled dan padded untuk memenuhi frame

---

## Tips Penggunaan

1. **Untuk video cepat**: Gunakan `max_duration: 15` atau `30` detik
2. **Untuk komentar lebih besar**: Gunakan `scale: 1.5` atau `2.0`
3. **Untuk kualitas lebih baik**: Gunakan `use_html_renderer: true` (jika tersedia)
4. **Untuk highlight komentar penting**: Set `highlight: true` pada komentar
5. **Untuk testing**: Gunakan background_option 1, 2, atau 3 sesuai preferensi

