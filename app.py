import streamlit as st
from video_utils import (
    ensure_ffmpeg_exists,
    make_header_image,
    make_comment_image,
    make_comments_image,
    make_comments_image_html,
    _HAS_PLAYWRIGHT,
    compose_video_ffmpeg,
)
import tempfile
import os

st.set_page_config(page_title="Short Template Generator", layout="centered")

st.title("Generator Video Template (ffmpeg)")
st.markdown("Upload video konten, pilih background (image/video), masukkan header dan top comment, lalu klik Generate.")

ensure_ffmpeg_exists()

with st.form("generator"):
    content = st.file_uploader("Upload content video (MP4/MOV)", type=["mp4", "mov", "webm"], accept_multiple_files=False)
    background = st.file_uploader("Upload background image/video (optional)", type=["jpg","jpeg","png","mp4","mov"], accept_multiple_files=False)
    header_text = st.text_input("Header hook text", value="Manusia serigala juga ikut demo")
    comment_author = st.text_input("Top comment: nama penulis", value="Nur Hidayat Aguz")
    comment_text = st.text_area("Top comment: isi komentar", value="ga ngaruh.. udh bayar promosi masih aj ga ngaruh..")
    comment_likes = st.text_input("Likes (contoh: 23)", value="23")
    comment_time = st.text_input("Waktu (contoh: 2 h)", value="2 h")
    comment_replies = st.text_input("Lihat balasan (contoh: 13)", value="13")
    # second top comment
    st.markdown("---")
    comment2_author = st.text_input("Top comment 2: nama penulis", value="Geminii")
    comment2_text = st.text_area("Top comment 2: isi komentar", value="SINI AKU BACK SELURUH TIKTOK AFFILIATE \n‼️ AMANAH ‼️🔥🔥🔥💯💯💯💯")
    comment2_likes = st.text_input("Top comment 2: Likes", value="1")
    comment2_time = st.text_input("Top comment 2: Waktu (contoh: 2 j)", value="2 j")
    comment2_replies = st.text_input("Top comment 2: Lihat balasan (contoh: 2)", value="2")
    duration_limit = st.number_input("Max duration (detik, 0 = pakai durasi asli)", min_value=0, value=0)
    submit = st.form_submit_button("Generate video")

if submit:
    if content is None:
        st.error("Silakan upload content video terlebih dahulu.")
    else:
        tmpdir = tempfile.mkdtemp()
        content_path = os.path.join(tmpdir, "content.mp4")
        with open(content_path, "wb") as f:
            f.write(content.read())

        bg_path = None
        if background is not None:
            bg_path = os.path.join(tmpdir, "background" + os.path.splitext(background.name)[1])
            with open(bg_path, "wb") as f:
                f.write(background.read())

        header_img = os.path.join(tmpdir, "header.png")
        comment_img = os.path.join(tmpdir, "comment.png")
        make_header_image(header_text, header_img)
        comments = [
            {"author": comment_author, "text": comment_text, "likes": comment_likes, "time": comment_time, "replies": comment_replies},
            {"author": comment2_author, "text": comment2_text, "likes": comment2_likes, "time": comment2_time, "replies": comment2_replies, "highlight": True},
        ]
        # Prefer exact HTML rendering if Playwright is available
        if _HAS_PLAYWRIGHT:
            try:
                make_comments_image_html(comments, comment_img, width=720)
            except Exception:
                # fallback
                make_comments_image(comments, comment_img)
        else:
            make_comments_image(comments, comment_img)

        out_path = os.path.join(tmpdir, "output.mp4")

        with st.spinner("Membuat video... (ffmpeg akan berjalan, ini mungkin butuh beberapa detik)"):
            try:
                compose_video_ffmpeg(
                    content_path,
                    bg_path,
                    header_img,
                    comment_img,
                    out_path,
                    max_duration=(duration_limit if duration_limit > 0 else None),
                )
            except Exception as e:
                st.error(f"Terjadi error saat memproses video: {e}")
                raise

        if os.path.exists(out_path):
            st.success("Video selesai dibuat — unduh di bawah")
            with open(out_path, "rb") as f:
                st.download_button("Download MP4", data=f, file_name="short_template_output.mp4", mime="video/mp4")
        else:
            st.error("Gagal: output tidak ditemukan.")
