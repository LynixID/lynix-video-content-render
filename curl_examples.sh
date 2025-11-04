#!/bin/bash
# Contoh-contoh penggunaan CURL untuk API Video Render

# ============================================
# CONFIGURATION
# ============================================
API_URL="https://159l88z0-8000.asse.devtunnels.ms/render"
API_TOKEN="LynixVideoContentGenerate88288"
OUTPUT_FILE="result.mp4"

# ============================================
# CONTOH 1: Request Minimal
# ============================================
echo "=== Contoh 1: Request Minimal ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4"
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 2: Dengan Header Text
# ============================================
echo "=== Contoh 2: Dengan Header Text ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 1,
    "header_text": "Manusia serigala juga ikut demo"
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 3: Dengan Satu Komentar
# ============================================
echo "=== Contoh 3: Dengan Satu Komentar ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 1,
    "header_text": "Video Singkat",
    "comments": [
      {
        "author": "Penonton123",
        "text": "Mantap sekali!",
        "likes": 99
      }
    ]
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 4: Dengan Dua Komentar Lengkap + Avatar + Emoji
# ============================================
echo "=== Contoh 4: Dengan Dua Komentar Lengkap + Avatar + Emoji ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
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
    "scale": 1.5,
    "max_duration": 30
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 5: Dengan HTML Renderer
# ============================================
echo "=== Contoh 5: Dengan HTML Renderer ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
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
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 6: Video Pendek (15 detik)
# ============================================
echo "=== Contoh 6: Video Pendek (15 detik) ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 3,
    "header_text": "Video Singkat 15 Detik",
    "comments": [
      {
        "author": "QuickView",
        "text": "Cepat sekali!",
        "likes": 50,
        "highlight": false
      }
    ],
    "scale": 1.0,
    "max_duration": 15
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 7: Komentar Besar (Scale 2.0)
# ============================================
echo "=== Contoh 7: Komentar Besar (Scale 2.0) ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 1,
    "header_text": "Komentar Besar",
    "comments": [
      {
        "author": "BigText",
        "text": "Ini komentar dengan ukuran besar",
        "likes": 200,
        "highlight": true
      }
    ],
    "scale": 2.0,
    "max_duration": 30
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

# ============================================
# CONTOH 8: Tanpa Header dan Komentar
# ============================================
echo "=== Contoh 8: Tanpa Header dan Komentar ==="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "content_url": "https://v16m.tiktokcdn-us.com/.../video.mp4",
    "background_option": 1
  }' \
  --output "$OUTPUT_FILE" \
  --max-time 600

