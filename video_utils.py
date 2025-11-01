import shutil
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import math
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
        font = ImageFont.truetype("arialbd.ttf", 56)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", 56)
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
           name_font = ImageFont.truetype("arialbd.ttf", 28)
           text_font = ImageFont.truetype("arial.ttf", 22)
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


def make_comments_image(comments, out_path, width=972, padding=14, bg=(255,255,255,255), scale=1.5):
    """Render up to 2 comments in a Twitter-like column style.
    comments: list of dicts with keys 'author','text','likes'
    scale: scale factor to apply to all geometry and typography (1.0 = native, 1.5 = 150%)
    """
    s = float(scale)

    # scaled font sizes
    name_fs = max(10, int(28 * s))
    handle_fs = max(8, int(20 * s))
    text_fs = max(10, int(22 * s))
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
    per_comment_widths = []
    av_d = int(64 * s)
    likes_space = int(80 * s)  # reserve space on right for likes/heart
    max_allowed_width = int(width * s)  # treat 'width' as a maximum cap
    pad = int(padding * s)
    name_text_gap = int(6 * s)
    line_spacing_unit = int(4 * s)

    for c in comments[:2]:
        full_text = c.get("text", "")
        # measure full text without wrapping
        full_w = text_size_local(full_text, text_font)[0]
        # available width for text if unwrapped
        available_if_unwrapped = max_allowed_width - pad*4 - av_d - likes_space

        lines = []
        if full_text and full_w <= available_if_unwrapped:
            # no wrap needed
            lines = [full_text]
            max_line_w = full_w
        else:
            # wrap to available width (or to a sane minimum)
            wrap_width = max(available_if_unwrapped, int(200 * s))
            words = full_text.split()
            cur = ""
            for w in words:
                test = (cur + " " + w).strip()
                if text_size_local(test, text_font)[0] <= wrap_width:
                    cur = test
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            max_line_w = max((text_size_local(l, text_font)[0] for l in lines), default=0)

        wrapped_texts.append(lines)
        header_h = text_size_local(c.get("author",""), name_font)[1]
        text_h = sum(text_size_local(l, text_font)[1] + line_spacing_unit for l in lines)
        comment_h = pad*2 + header_h + name_text_gap + text_h
        if comment_h < int(100 * s):
            comment_h = int(100 * s)
        per_comment_heights.append(comment_h)

        comment_total_w = pad*3 + av_d + max_line_w + likes_space
        per_comment_widths.append(int(comment_total_w))

    # decide final image width based on widest comment, but cap to provided width
    img_width = int(min(max(per_comment_widths) if per_comment_widths else max_allowed_width, max_allowed_width))
    if img_width < int(300 * s):
        img_width = int(300 * s)

    total_h = sum(per_comment_heights) + (len(per_comment_heights)-1)*int(8 * s) + pad*2
    img = Image.new("RGBA", (img_width, total_h), bg)
    draw = ImageDraw.Draw(img)

    y = pad
    for idx, c in enumerate(comments[:2]):
        # avatar circle
        av_x = pad
        av_y = y
        # av_d already scaled above
        # avatar background / placeholder
        draw.ellipse((av_x, av_y, av_x+av_d, av_y+av_d), fill=(230,230,230))
        # if highlighted (like second comment), draw border
        if c.get("highlight"):
            draw.ellipse((av_x-int(3*s), av_y-int(3*s), av_x+av_d+int(3*s), av_y+av_d+int(3*s)), outline=(14,165,233), width=max(1,int(4*s)))
        # author name
        name_x = av_x + av_d + int(12 * s)
        name_y = y
        draw.text((name_x, name_y), c.get("author",""), font=name_font, fill=(0,0,0))
        name_h = text_size_local(c.get("author",""), name_font)[1]

        # comment text (increased gap after name and line spacing)
        tx = name_x
        ty = name_y + name_h + int(12 * s)
        for line in wrapped_texts[idx]:
            draw.text((tx, ty), line, font=text_font, fill=(20,20,20))
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
                html_comments += f'''
        <div class="p-4 {border}">
            <div class="flex items-start space-x-3">
                <img src="https://via.placeholder.com/40" class="w-10 h-10 rounded-full {highlight_border}" alt="profile">
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
