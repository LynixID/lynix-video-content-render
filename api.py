import os
import shutil
import tempfile
from typing import List, Optional

import httpx
import subprocess
import traceback
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from video_utils import (
    make_header_image,
    make_comments_image,
    make_comments_image_html,
    compose_video_ffmpeg,
    ensure_ffmpeg_exists,
)

from PIL import Image


APP_DIR = os.path.dirname(__file__)
BACKGROUND_DIR = os.path.join(APP_DIR, "backgrounds")

TARGET_W = 1080
TARGET_H = 1920
CONTENT_W = int(TARGET_W * 0.90)


class Comment(BaseModel):
    author: str
    text: str
    likes: Optional[int] = 0
    time: Optional[str] = ""
    replies: Optional[str] = ""
    highlight: Optional[bool] = False
    avatar_url: Optional[str] = None


class RenderRequest(BaseModel):
    content_url: str
    background_option: Optional[int] = 1
    header_text: Optional[str] = ""
    comments: Optional[List[Comment]] = []
    use_html_renderer: Optional[bool] = False
    scale: Optional[float] = 1.0
    max_duration: Optional[float] = None


app = FastAPI(title="Shorts Composer API")


def ensure_background_templates():
    """Create 3 simple background image templates if not present."""
    os.makedirs(BACKGROUND_DIR, exist_ok=True)
    for i, color in enumerate([(240, 248, 255), (245, 237, 221), (230, 245, 255)], start=1):
        p = os.path.join(BACKGROUND_DIR, f"bg{i}.png")
        if not os.path.exists(p):
            img = Image.new("RGB", (TARGET_W, TARGET_H), color)
            img.save(p)


def download_file(url: str, dst_path: str, max_bytes: int = 150 * 1024 * 1024, timeout: int = 60):
    """Download from URL into dst_path with simple size limit and timeout."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url) as r:
                r.raise_for_status()
                total = 0
                with open(dst_path, "wb") as fh:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        if not chunk:
                            continue
                        fh.write(chunk)
                        total += len(chunk)
                        if total > max_bytes:
                            raise HTTPException(status_code=413, detail="File terlalu besar")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Gagal mendownload file: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Gagal menghubungi URL: {e}")


def download_avatar(url: str, dst_path: str, max_bytes: int = 5 * 1024 * 1024, timeout: int = 30):
    """Download avatar image from URL. Smaller size limit than video files."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url) as r:
                r.raise_for_status()
                # Check content type
                content_type = r.headers.get("content-type", "").lower()
                if not any(ct in content_type for ct in ["image/jpeg", "image/jpg", "image/png", "image/webp"]):
                    print(f"Warning: Avatar URL mungkin bukan gambar: {content_type}")
                total = 0
                with open(dst_path, "wb") as fh:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        if not chunk:
                            continue
                        fh.write(chunk)
                        total += len(chunk)
                        if total > max_bytes:
                            raise HTTPException(status_code=413, detail="Avatar terlalu besar")
                return True
    except httpx.HTTPStatusError as e:
        print(f"Warning: Gagal download avatar: {e}")
        return False
    except httpx.RequestError as e:
        print(f"Warning: Gagal menghubungi avatar URL: {e}")
        return False


def has_video_stream(path: str):
    """Return True if the file contains at least one video stream (uses ffprobe)."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        # If ffprobe is not available, conservatively assume it's ok
        return True
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v",
        "-show_entries",
        "stream=codec_type",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return False
    out = p.stdout.strip()
    return bool(out)


def cleanup_path(path: str):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@app.on_event("startup")
def startup():
    # check ffmpeg availability and prepare backgrounds
    ensure_ffmpeg_exists()
    ensure_background_templates()


@app.post("/render")
def render(request: Request, req: RenderRequest, background_tasks: BackgroundTasks):
    # validate
    if not req.content_url:
        raise HTTPException(status_code=400, detail="content_url diperlukan")
    # simple one-layer API key protection (hardcoded per user request).
    # NOTE: hardcoding secrets in source is insecure for production. Remove or
    # switch to environment variables before sharing the repo.
    api_key = "LynixVideoContentGenerate88288"
    if api_key:
        auth_hdr = (request.headers.get("authorization") or "").strip()
        x_api = request.headers.get("x-api-key")
        valid = False
        if x_api and x_api == api_key:
            valid = True
        if auth_hdr.lower().startswith("bearer "):
            token = auth_hdr[7:].strip()
            if token == api_key:
                valid = True
        if not valid:
            raise HTTPException(status_code=401, detail="Unauthorized: invalid or missing API key")
    if req.background_option not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="background_option harus 1,2 atau 3")

    tmpdir = tempfile.mkdtemp(prefix="shorts_")
    background_tasks.add_task(cleanup_path, tmpdir)

    try:
        try:
            # download content
            content_path = os.path.join(tmpdir, "content.mp4")
            download_file(req.content_url, content_path)

            # validate downloaded file contains a video stream (avoid ffmpeg running on audio-only or HTML)
            if not has_video_stream(content_path):
                raise HTTPException(status_code=400, detail="content_url tidak berisi stream video yang valid (tidak ada video stream). Periksa URL atau upload file secara langsung.")

            # prepare header and comments images
            header_path = os.path.join(tmpdir, "header.png")
            make_header_image(req.header_text or "", header_path, width=TARGET_W, height=160)

            # download avatars for comments if provided
            comments_list = [c.dict() for c in (req.comments or [])][:2]
            for idx, comment in enumerate(comments_list):
                if comment.get("avatar_url"):
                    avatar_path = os.path.join(tmpdir, f"avatar_{idx}.jpg")
                    if download_avatar(comment["avatar_url"], avatar_path):
                        comment["avatar_path"] = avatar_path
                    else:
                        comment["avatar_path"] = None
                else:
                    comment["avatar_path"] = None

            comment_img_path = os.path.join(tmpdir, "comments.png")
            # Lebar template komentar maksimal 90% dari lebar layar (TARGET_W)
            comment_width = int(TARGET_W * 0.90)
            # prefer HTML renderer if requested and available
            if req.use_html_renderer:
                try:
                    make_comments_image_html(comments_list, comment_img_path, width=comment_width, scale=req.scale)
                except Exception:
                    # fallback to PIL renderer
                    make_comments_image(comments_list, comment_img_path, width=comment_width, scale=req.scale, tmpdir=tmpdir)
            else:
                make_comments_image(comments_list, comment_img_path, width=comment_width, scale=req.scale, tmpdir=tmpdir)

            # pick background asset: try multiple extensions so users can drop a video (mp4/webm/mov) or image
            bg_path = None
            base_name = f"bg{int(req.background_option)}"
            # prefer images first then videos, but allow either
            allowed_exts = [
                ".png",
                ".jpg",
                ".jpeg",
                ".mp4",
                ".webm",
                ".mov",
                ".mkv",
            ]
            for ext in allowed_exts:
                p = os.path.join(BACKGROUND_DIR, base_name + ext)
                if os.path.exists(p):
                    bg_path = p
                    break
            if bg_path is None:
                # fallback: try to find any file that starts with the base_name (bg1.*)
                for fname in os.listdir(BACKGROUND_DIR):
                    if fname.startswith(base_name + "."):
                        bg_path = os.path.join(BACKGROUND_DIR, fname)
                        break
            if bg_path is None:
                raise HTTPException(status_code=500, detail=f"Background template untuk opsi {req.background_option} tidak ditemukan. Silakan letakkan file bernama {base_name}.(png|jpg|mp4) di folder backgrounds.")

            out_path = os.path.join(tmpdir, "out.mp4")

            # compose video (this may take time)
            compose_video_ffmpeg(content_path, bg_path, header_path, comment_img_path, out_path, target_w=TARGET_W, target_h=TARGET_H, max_duration=req.max_duration)

            if not os.path.exists(out_path):
                raise HTTPException(status_code=500, detail="Gagal membuat video")

            # return file and schedule cleanup
            # Stream the file in chunks and set explicit headers so proxies/tunnels (e.g. n8n dev tunnels)
            # correctly detect EOF. StreamingResponse here avoids some sendfile/os-level streaming
            # mismatches that can cause client-side hangs in certain proxy setups.
            try:
                size = os.path.getsize(out_path)
            except Exception:
                size = None

            headers = {"Content-Disposition": f"attachment; filename=\"result.mp4\""}
            if size is not None:
                headers["Content-Length"] = str(size)
            # suggest closing the connection when done
            headers.setdefault("Connection", "close")

            def file_iterator(path, chunk_size=32 * 1024):
                with open(path, "rb") as fh:
                    while True:
                        chunk = fh.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk

            return StreamingResponse(file_iterator(out_path), media_type="video/mp4", headers=headers)
        except Exception as e:
            # capture traceback into a file inside tmpdir for inspection
            tb_text = traceback.format_exc()
            try:
                log_path = os.path.join(tmpdir, "render_error.log")
                with open(log_path, "w", encoding="utf-8") as lf:
                    lf.write(tb_text)
            except Exception:
                pass
            # also print to server stdout (uvicorn console)
            print("Error during /render:\n", tb_text)
            # raise HTTP 502 to indicate upstream processing failure with a short message
            raise HTTPException(status_code=502, detail="Processing failed on server. Check server logs or render_error.log in temporary folder.")
    finally:
        # cleanup will be performed by background task registered earlier
        pass
