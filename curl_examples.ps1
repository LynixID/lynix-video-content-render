# Contoh-contoh penggunaan CURL untuk API Video Render (PowerShell)

# ============================================
# CONFIGURATION
# ============================================
$API_URL = "https://159l88z0-8000.asse.devtunnels.ms/render"
$API_TOKEN = "LynixVideoContentGenerate88288"
$OUTPUT_FILE = "result.mp4"

# ============================================
# CONTOH 1: Request Minimal
# ============================================
Write-Host "=== Contoh 1: Request Minimal ===" -ForegroundColor Green
$body1 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
} | ConvertTo-Json

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body1 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 2: Dengan Header Text
# ============================================
Write-Host "`n=== Contoh 2: Dengan Header Text ===" -ForegroundColor Green
$body2 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 1
    header_text = "Manusia serigala juga ikut demo"
} | ConvertTo-Json

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body2 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 3: Dengan Satu Komentar
# ============================================
Write-Host "`n=== Contoh 3: Dengan Satu Komentar ===" -ForegroundColor Green
$body3 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 1
    header_text = "Video Singkat"
    comments = @(
        @{
            author = "Penonton123"
            text = "Mantap sekali!"
            likes = 99
        }
    )
} | ConvertTo-Json -Depth 10

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body3 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 4: Dengan Dua Komentar Lengkap + Avatar + Emoji
# ============================================
Write-Host "`n=== Contoh 4: Dengan Dua Komentar Lengkap + Avatar + Emoji ===" -ForegroundColor Green
$body4 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 2
    header_text = "Contoh Header - Testing Video"
    comments = @(
        @{
            author = "UserA"
            text = "Keren banget kontennya, kasih tipsnya dong! 🔥🔥"
            likes = 128
            time = "2 h"
            replies = "13"
            highlight = $true
            avatar_url = "https://example.com/avatar1.jpg"
        },
        @{
            author = "UserB"
            text = "Wah ini useful, terima kasih sharingnya. 💯👍"
            likes = 42
            time = "3 j"
            replies = "5"
            highlight = $false
            avatar_url = "https://example.com/avatar2.png"
        }
    )
    scale = 1.5
    max_duration = 30
} | ConvertTo-Json -Depth 10

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body4 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 5: Dengan HTML Renderer
# ============================================
Write-Host "`n=== Contoh 5: Dengan HTML Renderer ===" -ForegroundColor Green
$body5 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 1
    header_text = "Header dengan HTML Renderer"
    comments = @(
        @{
            author = "John Doe"
            text = "Komentar pertama dengan HTML rendering"
            likes = 256
            highlight = $true
        }
    )
    use_html_renderer = $true
    scale = 1.5
    max_duration = 45
} | ConvertTo-Json -Depth 10

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body5 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 6: Video Pendek (15 detik)
# ============================================
Write-Host "`n=== Contoh 6: Video Pendek (15 detik) ===" -ForegroundColor Green
$body6 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 3
    header_text = "Video Singkat 15 Detik"
    comments = @(
        @{
            author = "QuickView"
            text = "Cepat sekali!"
            likes = 50
            highlight = $false
        }
    )
    scale = 1.0
    max_duration = 15
} | ConvertTo-Json -Depth 10

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body6 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 7: Komentar Besar (Scale 2.0)
# ============================================
Write-Host "`n=== Contoh 7: Komentar Besar (Scale 2.0) ===" -ForegroundColor Green
$body7 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 1
    header_text = "Komentar Besar"
    comments = @(
        @{
            author = "BigText"
            text = "Ini komentar dengan ukuran besar"
            likes = 200
            highlight = $true
        }
    )
    scale = 2.0
    max_duration = 30
} | ConvertTo-Json -Depth 10

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body7 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 8: Tanpa Header dan Komentar
# ============================================
Write-Host "`n=== Contoh 8: Tanpa Header dan Komentar ===" -ForegroundColor Green
$body8 = @{
    content_url = "https://v16m.tiktokcdn-us.com/.../video.mp4"
    background_option = 1
} | ConvertTo-Json

curl.exe -X POST $API_URL `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $API_TOKEN" `
  -d $body8 `
  --output $OUTPUT_FILE `
  --max-time 600

# ============================================
# CONTOH 9: Menggunakan Single Line (Escape Quotes)
# ============================================
Write-Host "`n=== Contoh 9: Single Line dengan Escape Quotes ===" -ForegroundColor Green
curl.exe -X POST $API_URL -H "Content-Type: application/json" -H "Authorization: Bearer $API_TOKEN" --data "{\"content_url\":\"https://v16m.tiktokcdn-us.com/.../video.mp4\",\"background_option\":1,\"header_text\":\"Test\",\"comments\":[{\"author\":\"User\",\"text\":\"Komentar\",\"likes\":10}],\"scale\":1.5,\"max_duration\":30}" --output $OUTPUT_FILE --max-time 600

Write-Host "`nSelesai! Semua contoh telah dijalankan." -ForegroundColor Cyan

