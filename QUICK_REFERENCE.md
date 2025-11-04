# Quick Reference - API Video Render

## Endpoint
```
POST /render
Authorization: Bearer LynixVideoContentGenerate88288
```

## Request Body (JSON)

```json
{
  "content_url": "string (WAJIB)",
  "background_option": 1|2|3,
  "header_text": "string",
  "comments": [
    {
      "author": "string (WAJIB)",
      "text": "string (WAJIB) - support emoji",
      "likes": 0,
      "time": "",
      "replies": "",
      "highlight": false,
      "avatar_url": "string (opsional)"
    }
  ],
  "use_html_renderer": false,
  "scale": 1.0,
  "max_duration": null
}
```

## Parameter Summary

| Parameter | Type | Default | Wajib | Deskripsi |
|-----------|------|---------|-------|-----------|
| `content_url` | string | - | ✅ | URL video konten |
| `background_option` | int | 1 | ❌ | Pilihan background (1,2,3) |
| `header_text` | string | "" | ❌ | Teks header |
| `comments` | array | [] | ❌ | Array komentar (max 2) |
| `use_html_renderer` | bool | false | ❌ | Gunakan HTML renderer |
| `scale` | float | 1.0 | ❌ | Skala komentar (1.0-2.0) |
| `max_duration` | float | null | ❌ | Durasi maks (detik) |

## Comment Object

| Property | Type | Default | Wajib | Deskripsi |
|----------|------|---------|-------|-----------|
| `author` | string | - | ✅ | Nama penulis |
| `text` | string | - | ✅ | Isi komentar (support emoji) |
| `likes` | int | 0 | ❌ | Jumlah likes |
| `time` | string | "" | ❌ | Waktu (contoh: "2 h") |
| `replies` | string | "" | ❌ | Jumlah balasan |
| `highlight` | bool | false | ❌ | Border biru |
| `avatar_url` | string | null | ❌ | URL avatar (jpg/png/webp) |

## CURL Template (Minimal)

```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "YOUR_VIDEO_URL"
  }' \
  --output result.mp4 \
  --max-time 600
```

## CURL Template (Lengkap)

```bash
curl -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LynixVideoContentGenerate88288" \
  -d '{
    "content_url": "YOUR_VIDEO_URL",
    "background_option": 1,
    "header_text": "Header Text",
    "comments": [
      {
        "author": "User",
        "text": "Komentar dengan emoji 🔥",
        "likes": 10,
        "highlight": true,
        "avatar_url": "https://example.com/avatar.jpg"
      }
    ],
    "scale": 1.5,
    "max_duration": 30
  }' \
  --output result.mp4 \
  --max-time 600
```

## PowerShell Template

```powershell
$body = @{
    content_url = "YOUR_VIDEO_URL"
    background_option = 1
    header_text = "Header Text"
    comments = @(
        @{
            author = "User"
            text = "Komentar"
            likes = 10
            highlight = $true
        }
    )
    scale = 1.5
    max_duration = 30
} | ConvertTo-Json -Depth 10

curl.exe -X POST "https://159l88z0-8000.asse.devtunnels.ms/render" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer LynixVideoContentGenerate88288" `
  -d $body `
  --output result.mp4 `
  --max-time 600
```

## Response Codes

- `200 OK` - Success, video file
- `400 Bad Request` - Parameter tidak valid
- `401 Unauthorized` - Token tidak valid
- `413 Payload Too Large` - File terlalu besar (>150MB)
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - Download/processing error

## Tips

- **Timeout**: Gunakan `--max-time 600` (10 menit)
- **Max Comments**: Hanya 2 komentar pertama yang digunakan
- **Scale**: 1.0 = normal, 1.5 = besar, 2.0 = sangat besar
- **Background**: File harus ada di `backgrounds/bg1.*`, `bg2.*`, `bg3.*`
- **Video Output**: 1080x1920 (Portrait), MP4 format
- **Avatar**: Format JPG/PNG/WebP, max 5MB, akan ditampilkan lingkaran
- **Emoji**: Support emoji dan Unicode, lebih baik di HTML renderer

