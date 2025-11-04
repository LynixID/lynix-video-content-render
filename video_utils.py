import shutil
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import math
from io import BytesIO
try:
    from playwright.sync_api import sync_playwright
    _HAS_PLAYWRIGHT = True
except Exception:
    _HAS_PLAYWRIGHT = False


def ensure_ffmpeg_exists():
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg tidak ditemukan di PATH. Silakan install ffmpeg dan pastikan dapat diakses dari terminal.")
    return ffmpeg


def get_duration(path):
    """Dapatkan durasi video (detik) menggunakan ffprobe."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise RuntimeError("ffprobe tidak ditemukan. ffprobe biasanya termasuk dalam paket ffmpeg.")
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe error: {p.stderr}")
    try:
        return float(p.stdout.strip())
    except:
        return None


def make_header_image(text, out_path, width=1080, height=160, bg_color=(245, 237, 221), text_color=(0, 0, 0)):
    # simple header: rectangle with text centered
    img = Image.new("RGBA", (width, height), bg_color + (255,))
    draw = ImageDraw.Draw(img)
    
    # choose font (try bold then regular)
    try:
        # try bold Windows font first
        font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "arialbd.ttf"), 56)
    except Exception:
        try:
            font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "arial.ttf"), 56)
        except Exception:
            font = ImageFont.load_default()

    def text_size(txt, fnt):
        # cross-version compatible text size (Pillow >=8: textbbox; older: textsize)
        try:
            bbox = draw.textbbox((0, 0), txt, font=fnt)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        except Exception:
            try:
                return draw.textsize(txt, font=fnt)
            except Exception:
                try:
                    return fnt.getsize(txt)
                except Exception:
                    return (0, 0)

    # wrap text if needed
    max_width = width - 40
    lines = []
    words = text.split()
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_size(test, font)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    total_h = sum(text_size(l, font)[1] for l in lines)
    y = (height - total_h) // 2
    for l in lines:
        w, h = text_size(l, font)
        x = (width - w) // 2
        draw.text((x, y), l, font=font, fill=text_color)
        y += h

    img.save(out_path)


def round_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def make_comment_image(author, text, likes, out_path, width=460, height=220, bg=(255,255,255,230)):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # rounded background
    round_rect(draw, (0, 0, width, height), radius=16, fill=bg)

    try:
           name_font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "arialbd.ttf"), 28)
           text_font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "arial.ttf"), 22)
    except Exception:
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    def text_size_comment(txt, fnt):
        try:
            bbox = draw.textbbox((0, 0), txt, font=fnt)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        except Exception:
            try:
                return draw.textsize(txt, font=fnt)
            except Exception:
                try:
                    return fnt.getsize(txt)
                except Exception:
                    return (0, 0)

    padding = 14
    x = padding
    y = padding
    draw.text((x, y), author, font=name_font, fill=(0,0,0))
    y += text_size_comment(author, name_font)[1] + 6

    # wrap comment text
    max_w = width - padding*2
    lines = []
    words = text.split()
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_size_comment(test, text_font)[0] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    for l in lines[:6]:  # limit lines
        draw.text((x, y), l, font=text_font, fill=(20,20,20))
        y += text_size_comment(l, text_font)[1] + 4

    # likes at bottom-right
    likes_text = f"{likes}"
    lw, lh = text_size_comment(likes_text, text_font)
    draw.text((width - lw - padding, height - lh - padding), likes_text, font=text_font, fill=(100,100,100))

    img.save(out_path)


def get_emoji_font(size=24):
    """Try to get a font that supports emoji. Falls back to default if not available."""
    # Try common emoji-supporting fonts (order matters)
    emoji_font_paths = [
        "C:/Windows/Fonts/seguiemj.ttf",  # Windows Segoe UI Emoji
        "C:/Windows/Fonts/msyh.ttc",      # Windows Microsoft YaHei (supports emoji)
        "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux Noto Color Emoji
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux DejaVu (partial emoji)
    ]
    for font_path in emoji_font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    # Fallback to default font
    return ImageFont.load_default()


def is_emoji(char):
    """Check if a character is an emoji."""
    # Simple emoji detection - covers most common emoji ranges
    code = ord(char)
    return (
        (0x1F600 <= code <= 0x1F64F) or  # Emoticons
        (0x1F300 <= code <= 0x1F5FF) or  # Misc Symbols and Pictographs
        (0x1F680 <= code <= 0x1F6FF) or  # Transport and Map
        (0x1F1E0 <= code <= 0x1F1FF) or  # Regional indicators
        (0x2600 <= code <= 0x26FF) or    # Misc symbols
        (0x2700 <= code <= 0x27BF) or    # Dingbats
        (0xFE00 <= code <= 0xFE0F) or    # Variation Selectors
        (0x1F900 <= code <= 0x1F9FF) or  # Supplemental Symbols
        (0x1FA00 <= code <= 0x1FAFF)     # Chess Symbols and Extended
    )


def draw_text_with_emoji(draw, position, text, text_font, emoji_font, fill=(0,0,0)):
    """Draw text with proper emoji rendering using composite font.
    Uses text_font for regular text and emoji_font for emoji characters.
    """
    x, y = position
    current_x = x
    
    # Render character by character or word by word, using appropriate font for each
    i = 0
    while i < len(text):
        char = text[i]
        
        # Check if this is an emoji (could be multi-byte)
        # Handle emoji sequences (some emojis are 2-char sequences)
        emoji_char = char
        emoji_len = 1
        
        # Check if next character is part of emoji sequence (variation selector, skin tone, etc)
        if i + 1 < len(text):
            next_char = text[i + 1]
            if ord(next_char) in (0xFE00, 0xFE0F) or (0x1F3FB <= ord(next_char) <= 0x1F3FF):
                emoji_char = char + next_char
                emoji_len = 2
        
        if is_emoji(char):
            # Render emoji with emoji font
            try:
                draw.text((current_x, y), emoji_char, font=emoji_font, fill=fill)
                # Get width of emoji
                try:
                    bbox = draw.textbbox((0, 0), emoji_char, font=emoji_font)
                    char_width = bbox[2] - bbox[0]
                except:
                    try:
                        char_width = emoji_font.getlength(emoji_char)
                    except:
                        char_width = text_font.getlength(emoji_char)
                current_x += char_width
                i += emoji_len - 1  # Skip processed characters
            except Exception:
                # Fallback to text font if emoji font fails
                try:
                    draw.text((current_x, y), emoji_char, font=text_font, fill=fill)
                    try:
                        bbox = draw.textbbox((0, 0), emoji_char, font=text_font)
                        char_width = bbox[2] - bbox[0]
                    except:
                        char_width = text_font.getlength(emoji_char)
                    current_x += char_width
                    i += emoji_len - 1
                except:
                    # Last resort: skip character
                    i += emoji_len
        else:
            # Render regular text with text font
            # Find the end of the current word/sequence (non-emoji sequence)
            end = i + 1
            while end < len(text) and not is_emoji(text[end]):
                end += 1
            
            word = text[i:end]
            if word:
                try:
                    draw.text((current_x, y), word, font=text_font, fill=fill)
                    try:
                        bbox = draw.textbbox((0, 0), word, font=text_font)
                        word_width = bbox[2] - bbox[0]
                    except:
                        try:
                            word_width = text_font.getlength(word)
                        except:
                            word_width = len(word) * 10  # Fallback estimate
                    current_x += word_width
                except:
                    pass
            i = end
        
        i += 1


def make_comments_image(comments, out_path, width=972, padding=14, bg=(255,255,255,255), scale=1.5, tmpdir=None):
    """Render up to 2 comments in a Twitter-like column style.
    comments: list of dicts with keys 'author','text','likes','avatar_path'
    scale: scale factor to apply to all geometry and typography (1.0 = native, 1.5 = 150%)
    tmpdir: temporary directory for avatar files (optional)
    """
    s = float(scale)

    # scaled font sizes
    name_fs = max(10, int(28 * s))
    handle_fs = max(8, int(20 * s))
    text_fs = max(10, int(22 * s))
    
    # Try to get fonts with emoji support
    emoji_font = get_emoji_font()
    try:
        name_font = ImageFont.truetype("arialbd.ttf", name_fs)
        handle_font = ImageFont.truetype("arial.ttf", handle_fs)
        text_font = ImageFont.truetype("arial.ttf", text_fs)
    except Exception:
        name_font = ImageFont.load_default()
        handle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # compute per-comment height by measuring wrapped text
    draw_dummy = ImageDraw.Draw(Image.new("RGBA", (10,10)))

    def text_size_local(txt, fnt):
        try:
            bbox = draw_dummy.textbbox((0,0), txt, font=fnt)
            return (bbox[2]-bbox[0], bbox[3]-bbox[1])
        except Exception:
            try:
                return draw_dummy.textsize(txt, font=fnt)
            except Exception:
                try:
                    return fnt.getsize(txt)
                except Exception:
                    return (0,0)

    per_comment_heights = []
    wrapped_texts = []
    av_d = int(64 * s)
    likes_space = int(80 * s)  # reserve space on right for likes/heart
    # Lebar maksimal template komentar = 90% dari lebar layar (TARGET_W = 1080px)
    # width yang dipassing sudah 90% dari TARGET_W (972px)
    # PENTING: width template TIDAK di-scale, hanya font dan spacing yang di-scale
    max_allowed_width = int(width)  # FIXED WIDTH - tidak di-scale, tetap 90% dari TARGET_W
    pad = int(padding * s)
    name_text_gap = int(6 * s)
    line_spacing_unit = int(4 * s)
    
    # Calculate available width for text (fixed, tidak tergantung panjang teks)
    # Struktur: pad(kiri) + avatar + pad + text_area + pad + likes_space + pad(kanan) = max_allowed_width
    # text_area = max_allowed_width - (pad*4 + av_d + likes_space)
    text_area_width = max_allowed_width - (pad*4 + av_d + likes_space)

    MAX_TEXT_LINES = 3  # Maksimal 3 baris untuk text komentar
    
    for c in comments[:2]:
        full_text = c.get("text", "")
        
        # Always wrap text to fit within text_area_width
        # Split text into words and wrap them
        lines = []
        words = full_text.split() if full_text else []
        
        if words:
            cur = ""
            for w in words:
                # Jika sudah mencapai maksimal 3 baris, stop wrapping
                if len(lines) >= MAX_TEXT_LINES:
                    break
                
                test = (cur + " " + w).strip() if cur else w
                # Measure text width (try to account for emoji)
                test_w = text_size_local(test, text_font)[0]
                # Add some buffer for emoji (they might be wider)
                if test_w <= text_area_width * 0.95:  # 95% to leave some buffer
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                        if len(lines) >= MAX_TEXT_LINES:
                            break
                    # If single word is too long, split it (for very long words)
                    if text_size_local(w, text_font)[0] > text_area_width * 0.95:
                        # Word is too long, try to split it character by character
                        word_cur = ""
                        for char in w:
                            if len(lines) >= MAX_TEXT_LINES:
                                break
                            word_test = word_cur + char
                            if text_size_local(word_test, text_font)[0] <= text_area_width * 0.95:
                                word_cur = word_test
                            else:
                                if word_cur:
                                    lines.append(word_cur)
                                    if len(lines) >= MAX_TEXT_LINES:
                                        break
                                word_cur = char
                        cur = word_cur
                        if len(lines) >= MAX_TEXT_LINES:
                            break
                    else:
                        cur = w
            
            # Add current line if we haven't reached max lines
            if cur:
                if len(lines) < MAX_TEXT_LINES:
                    # Masih ada slot, tambahkan baris baru
                    lines.append(cur)
                elif len(lines) == MAX_TEXT_LINES:
                    # Sudah mencapai max, append ke baris terakhir dengan ellipsis jika perlu
                    # Tapi jika cur terlalu panjang, kita skip saja (tidak perlu ellipsis di baris terakhir)
                    # Atau kita bisa tambahkan ellipsis ke baris terakhir yang sudah ada
                    last_line = lines[-1] if lines else ""
                    # Cek apakah baris terakhir perlu ellipsis
                    if last_line and not last_line.endswith("..."):
                        # Tambahkan ellipsis ke baris terakhir jika masih ada space
                        ellipsis = "..."
                        test_line = last_line + ellipsis
                        if text_size_local(test_line, text_font)[0] <= text_area_width * 0.95:
                            lines[-1] = test_line
        else:
            lines = [""]
        
        # Pastikan maksimal 3 baris (safety check)
        lines = lines[:MAX_TEXT_LINES]

        wrapped_texts.append(lines)
        header_h = text_size_local(c.get("author",""), name_font)[1]
        text_h = sum(text_size_local(l, text_font)[1] + line_spacing_unit for l in lines)
        comment_h = pad*2 + header_h + name_text_gap + text_h
        if comment_h < int(100 * s):
            comment_h = int(100 * s)
        per_comment_heights.append(comment_h)

    # Image width selalu sama dengan max_allowed_width (FIXED WIDTH)
    img_width = max_allowed_width

    total_h = sum(per_comment_heights) + (len(per_comment_heights)-1)*int(8 * s) + pad*2
    img = Image.new("RGBA", (img_width, total_h), bg)
    draw = ImageDraw.Draw(img)

    y = pad
    for idx, c in enumerate(comments[:2]):
        # avatar circle
        av_x = pad
        av_y = y
        # av_d already scaled above
        
        # Load avatar image if provided
        avatar_img = None
        avatar_path = c.get("avatar_path")
        if avatar_path and os.path.exists(avatar_path):
            try:
                avatar_img = Image.open(avatar_path)
                # Convert to RGBA if needed
                if avatar_img.mode != "RGBA":
                    avatar_img = avatar_img.convert("RGBA")
                # Resize to square
                avatar_img = avatar_img.resize((av_d, av_d), Image.LANCZOS)
            except Exception as e:
                print(f"Warning: Gagal load avatar: {e}")
                avatar_img = None
        
        # Draw avatar background / placeholder
        draw.ellipse((av_x, av_y, av_x+av_d, av_y+av_d), fill=(230,230,230))
        
        # Draw avatar image if available (create circular mask)
        if avatar_img:
            # Create circular mask
            mask = Image.new("L", (av_d, av_d), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, av_d, av_d), fill=255)
            # Apply mask to avatar
            avatar_img.putalpha(mask)
            # Paste avatar onto main image
            img.paste(avatar_img, (av_x, av_y), avatar_img)
        
        # if highlighted (like second comment), draw border
        if c.get("highlight"):
            draw.ellipse((av_x-int(3*s), av_y-int(3*s), av_x+av_d+int(3*s), av_y+av_d+int(3*s)), outline=(14,165,233), width=max(1,int(4*s)))
        
        # author name
        name_x = av_x + av_d + int(12 * s)
        name_y = y
        draw.text((name_x, name_y), c.get("author",""), font=name_font, fill=(0,0,0))
        name_h = text_size_local(c.get("author",""), name_font)[1]

        # comment text (increased gap after name and line spacing) with emoji support
        tx = name_x
        ty = name_y + name_h + int(12 * s)
        emoji_font_scaled = get_emoji_font(int(22 * s))  # Match text font size
        for line in wrapped_texts[idx]:
            # Render text with proper emoji support
            draw_text_with_emoji(draw, (tx, ty), line, text_font, emoji_font_scaled, fill=(20,20,20))
            ty += text_size_local(line, text_font)[1] + int(8 * s)

        # bottom row: show only likes (heart + count) aligned to the right
        bottom_y = y + per_comment_heights[idx] - int(24 * s)
        likes = c.get("likes", "")
        lw, lh = text_size_local(str(likes), handle_font)
        heart_size = int(18 * s)
        right_x = img_width - lw - heart_size - pad - int(6 * s)

        # vertical align heart to text
        heart_top = bottom_y + (lh - heart_size) // 2

        def draw_heart(d, x, y, szz, fill):
            # draw two circles and a triangle to approximate a heart
            r = szz * 0.28
            left_cx = x + szz * 0.28
            right_cx = x + szz * 0.72
            cy = y + szz * 0.28
            # circles
            d.ellipse((left_cx - r, cy - r, left_cx + r, cy + r), fill=fill)
            d.ellipse((right_cx - r, cy - r, right_cx + r, cy + r), fill=fill)
            # triangle below
            tri = [(x + szz*0.05, cy + r*0.2), (x + szz*0.95, cy + r*0.2), (x + szz*0.5, y + szz*0.98)]
            d.polygon(tri, fill=fill)

        draw_heart(draw, right_x, heart_top, heart_size, fill=(220,20,60))
        draw.text((right_x + heart_size + int(6 * s), bottom_y), str(likes), font=handle_font, fill=(80,80,80))

        y += per_comment_heights[idx] + int(8 * s)
        if idx < len(comments[:2]) - 1:
            # divider
            draw.line((pad, y-int(4 * s), img_width-pad, y-int(4 * s)), fill=(230,230,230), width=max(1, int(1 * s)))

    img.save(out_path)


def make_comments_image_html(comments, out_path, width=972, scale=1.5):
    """Render the exact HTML/Tailwind template using Playwright (headless Chromium) and save as PNG.
    Falls back to make_comments_image if Playwright not available.
    scale: final scale factor to apply to the resulting PNG (if Playwright used, image will be resized)
    """
    if not _HAS_PLAYWRIGHT:
        # fallback (pass scale to PIL renderer)
        return make_comments_image(comments, out_path, width=width, scale=scale)

    # build HTML using the provided template structure
    # simple inline Tailwind from CDN is used
    html_comments = ""
    for idx, c in enumerate(comments[:2]):
        border = "border-b border-gray-100" if idx == 0 else ""
        highlight_border = "border-2 border-sky-400" if c.get("highlight") else ""
        # Use avatar_url if provided, otherwise use placeholder
        avatar_src = c.get("avatar_url") or "https://via.placeholder.com/40"
        html_comments += f'''
        <div class="p-4 {border}">
            <div class="flex items-start space-x-3">
                <img src="{avatar_src}" class="w-10 h-10 rounded-full {highlight_border}" alt="profile" onerror="this.src='https://via.placeholder.com/40'">
                <div class="flex-1">
                    <div class="font-semibold text-sm">{c.get('author','')}</div>
                    <div class="text-[15px] leading-snug mt-0.5 {'font-semibold' if c.get('highlight') else ''}">{c.get('text','')}</div>
                    <div class="flex justify-end items-center mt-2">
                        <div class="flex items-center space-x-2 text-gray-500">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 6 3.99 4 6.5 4c1.74 0 3.41 1.01 4.13 2.44h.75C13.09 5.01 14.76 4 16.5 4 19.01 4 21 6 21 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                            </svg>
                            <span class="text-sm text-gray-700">{c.get('likes','')}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
'''

        html = f"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com"></script>
    <style> body {{ margin:0; padding:0; background:transparent; }} </style>
</head>
<body>
    <div class="w-[390px] bg-white min-h-screen shadow-lg rounded-xl overflow-hidden border border-gray-200">
        {html_comments}
    </div>
</body>
</html>
"""

        # render with playwright
        with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": width, "height": 800})
                page.set_content(html, wait_until="networkidle")
                # get height
                height = page.evaluate('document.querySelector(".w-[390px]").scrollHeight')
                page.set_viewport_size({"width": width, "height": int(height)})
                page.screenshot(path=out_path, full_page=False)
                browser.close()

        # if scale != 1, resize the saved PNG to scale it
        try:
            s = float(scale)
            if s != 1.0:
                img = Image.open(out_path)
                nw = int(img.width * s)
                nh = int(img.height * s)
                img = img.resize((nw, nh), Image.LANCZOS)
                img.save(out_path)
        except Exception:
            # silently ignore resize failures
            pass


def compose_video_ffmpeg(content_path, bg_path, header_img, comment_img, out_path, target_w=1080, target_h=1920, max_duration=None):
    ffmpeg = ensure_ffmpeg_exists()
    # get content duration
    dur = get_duration(content_path)
    if max_duration is not None and max_duration > 0:
        dur = min(dur, float(max_duration)) if dur is not None else float(max_duration)

    inputs = []
    filter_inputs = []
    # Background: to ensure the background always fills the target frame and matches duration,
    # pre-process it into a temporary scaled video (bg_processed.mp4) that is exactly target size
    work_dir = os.path.dirname(out_path)
    bg_processed = os.path.join(work_dir, "bg_processed.mp4")

    if bg_path is None:
        # generate a solid color background video
        black = os.path.join(work_dir, "black_bg.png")
        Image.new("RGB", (target_w, target_h), (10,10,10)).save(black)
        bg_path = black

    # choose processing based on extension
    ext = os.path.splitext(bg_path)[1].lower()
    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            # image -> create a looping video trimmed to duration
            t = str(dur or 5)
            proc_cmd = [
                ffmpeg, "-y", "-loop", "1", "-i", bg_path,
                "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                "-t", t, "-c:v", "libx264", "-pix_fmt", "yuv420p", bg_processed
            ]
            subprocess.run(proc_cmd, check=True, capture_output=True)
        else:
            # video background -> loop or trim to duration and scale/pad
            bg_dur = get_duration(bg_path)
            t = str(dur) if dur is not None else None
            if bg_dur is not None and dur is not None and bg_dur < dur:
                # loop source to cover duration
                proc_cmd = [
                    ffmpeg, "-y", "-stream_loop", "-1", "-i", bg_path,
                    "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                    "-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p", bg_processed
                ]
            else:
                # no need to loop; just trim/scale if necessary
                cmd = [ffmpeg, "-y", "-i", bg_path, "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1", "-c:v", "libx264", "-pix_fmt", "yuv420p"]
                if t:
                    cmd += ["-t", t]
                cmd += [bg_processed]
                proc_cmd = cmd
            subprocess.run(proc_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # if processing background failed, fall back to using the original bg_path as input
        # but log the error to help debugging
        try:
            err_txt = e.stderr.decode('utf-8') if e.stderr else str(e)
        except Exception:
            err_txt = str(e)
        print("Warning: background pre-processing failed, falling back. Error:\n", err_txt)
        if os.path.exists(bg_processed):
            os.remove(bg_processed)
        bg_processed = bg_path

    # use the processed background video (or fallback) as the first input
    inputs += ["-i", bg_processed]

    # content
    inputs += ["-i", content_path]

    # header image and comment image
    inputs += ["-i", header_img, "-i", comment_img]

    # compute content target width as 90% of background width
    content_w = int(math.floor(target_w * 0.90))

    # probe original content size to calculate the scaled height
    def get_size(path):
        ffprobe = shutil.which("ffprobe")
        if ffprobe is None:
            return None
        cmd = [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            path,
        ]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            return None
        try:
            parts = p.stdout.strip().split("x")
            return (int(parts[0]), int(parts[1]))
        except Exception:
            return None

    orig_size = get_size(content_path)
    if orig_size:
        orig_w, orig_h = orig_size
        content_h = int(math.floor(orig_h * (content_w / orig_w)))
    else:
        content_h = int(math.floor(content_w * (16/9)))

    # compute content position (centered)
    content_x = int((target_w - content_w) // 2)
    content_y = int((target_h - content_h) // 2)

    # header/comment image sizes
    try:
        header_w, header_h = Image.open(header_img).size
    except Exception:
        header_w, header_h = (target_w, 160)
    try:
        comment_w, comment_h = Image.open(comment_img).size
    except Exception:
        comment_w, comment_h = (460, 220)

    # default positions (attached to container)
    header_x_default = 0
    header_y_default = 20
    comment_x_default = int((target_w - comment_w) // 2)
    comment_y_default = int(target_h - comment_h - 20)

    # check content aspect to decide behavior: if content is "less vertical than 3:4" -> width/height > 3/4
    attach_to_content = False
    if orig_size:
        if (orig_w / orig_h) > (3/4):
            attach_to_content = True

    if attach_to_content:
        # header attached to top of content, comment attached to bottom of content
        header_x = int((target_w - header_w) // 2)
        header_y = int(max(0, content_y - header_h))
        comment_x = int((target_w - comment_w) // 2)
        comment_y = int(min(target_h - comment_h, content_y + content_h))
    else:
        header_x = header_x_default
        header_y = header_y_default
        comment_x = comment_x_default
        comment_y = comment_y_default

    # build filter_complex
    # indices: 0:bg, 1:content, 2:header, 3:comment
    # scale background to target, pad if needed
    fc = (
        f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1[bg];"
        f"[1:v]scale={content_w}:{content_h}:force_original_aspect_ratio=disable,setsar=1[vid];"
        f"[bg][vid]overlay={content_x}:{content_y}[tmp1];"
        f"[tmp1][2:v]overlay={header_x}:{header_y}[tmp2];"
        f"[tmp2][3:v]overlay={comment_x}:{comment_y}[outv]"
    )

    cmd = [ffmpeg, "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", "[outv]",
        "-map", "1:a?",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-shortest",
        out_path,
    ]

    # if duration known, add -t to force output length (ensure loops are trimmed)
    if dur is not None:
        cmd += ["-t", str(dur)]

    # run ffmpeg
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr}\nCMD: {' '.join(cmd)}")
