"""Medya işleme servisi.

İki ana işlev:
1. add_logo_overlay  — Pillow ile görsel üzerine logo ekle
2. add_intro_video   — FFmpeg ile intro/outro video birleştir

Her iki fonksiyon da:
- Kaynak dosyaları R2'den indirir
- İşlemi yapar
- Sonucu R2'ye yükler ve public URL döner
- Gerekli kütüphane/araç yoksa sessizce None döner (üretim kesintisiz devam eder)
"""

import io
import os
import subprocess
import tempfile
from pathlib import Path
from uuid import UUID

import httpx

from app.services.storage import r2


# ─── Logo Overlay ────────────────────────────────────────────────────────────

async def add_logo_overlay(
    image_url: str,
    logo_url: str,
    post_id: UUID,
    brand_id: UUID,
    position: str = "bottom-right",
    opacity: float = 0.8,
) -> str | None:
    """
    Görsel üzerine logo bindirme.

    position: top-left | top-right | bottom-left | bottom-right
    opacity:  0.0 – 1.0

    Başarısız olursa None döner (orijinal URL kullanılmaya devam edilir).
    """
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return None

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            img_resp = await client.get(image_url)
            logo_resp = await client.get(logo_url)
            img_resp.raise_for_status()
            logo_resp.raise_for_status()

        base = Image.open(io.BytesIO(img_resp.content)).convert("RGBA")
        logo = Image.open(io.BytesIO(logo_resp.content)).convert("RGBA")

        # Logo boyutunu görselin %20'si ile sınırla
        max_logo_w = int(base.width * 0.20)
        max_logo_h = int(base.height * 0.20)
        logo.thumbnail((max_logo_w, max_logo_h), Image.LANCZOS)

        # Opaklık uygula
        if opacity < 1.0:
            r_ch, g_ch, b_ch, a_ch = logo.split()
            a_ch = a_ch.point(lambda x: int(x * opacity))
            logo = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

        # Konum hesapla
        margin = 20
        lw, lh = logo.size
        bw, bh = base.size

        positions = {
            "top-left":     (margin, margin),
            "top-right":    (bw - lw - margin, margin),
            "bottom-left":  (margin, bh - lh - margin),
            "bottom-right": (bw - lw - margin, bh - lh - margin),
        }
        paste_x, paste_y = positions.get(position, positions["bottom-right"])

        # Yapıştır
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        overlay.paste(logo, (paste_x, paste_y), logo)
        result = Image.alpha_composite(base, overlay).convert("RGB")

        # Bytes'a çevir
        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=92)
        buf.seek(0)

        dest_path = f"brands/{brand_id}/posts/generated/{post_id}_logo.jpg"
        return r2.upload(buf.read(), dest_path, "image/jpeg")

    except Exception:
        return None


# ─── Intro Video ─────────────────────────────────────────────────────────────

async def add_intro_video(
    main_video_url: str,
    intro_video_url: str,
    post_id: UUID,
    brand_id: UUID,
    position: str = "start",
) -> str | None:
    """
    FFmpeg ile intro/outro video birleştirme.

    position: start | end | both

    Başarısız olursa None döner (orijinal URL kullanılmaya devam edilir).
    """
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        if result.returncode != 0:
            return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            main_resp = await client.get(main_video_url)
            intro_resp = await client.get(intro_video_url)
            main_resp.raise_for_status()
            intro_resp.raise_for_status()

        with tempfile.TemporaryDirectory() as tmpdir:
            main_path = os.path.join(tmpdir, "main.mp4")
            intro_path = os.path.join(tmpdir, "intro.mp4")
            output_path = os.path.join(tmpdir, "output.mp4")
            concat_list = os.path.join(tmpdir, "concat.txt")

            Path(main_path).write_bytes(main_resp.content)
            Path(intro_path).write_bytes(intro_resp.content)

            # concat.txt oluştur
            if position == "start":
                segments = [intro_path, main_path]
            elif position == "end":
                segments = [main_path, intro_path]
            else:  # both
                segments = [intro_path, main_path, intro_path]

            with open(concat_list, "w") as f:
                for seg in segments:
                    f.write(f"file '{seg}'\n")

            # FFmpeg concat (re-encode ile uyumluluk garantisi)
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_list,
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac",
                "-movflags", "+faststart",
                output_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, timeout=120)
            if proc.returncode != 0:
                return None

            video_bytes = Path(output_path).read_bytes()

        dest_path = f"brands/{brand_id}/posts/generated/{post_id}_final.mp4"
        return r2.upload(video_bytes, dest_path, "video/mp4")

    except Exception:
        return None


# ─── Post-generation pipeline ────────────────────────────────────────────────

async def apply_brand_processing(
    post_id: UUID,
    brand_id: UUID,
    output_url: str,
    content_type: str,
    brand_kit: dict,
    logo_url: str | None,
    intro_video_url: str | None,
) -> str:
    """
    Fal.ai üretimi sonrası marka işlemlerini uygula.

    1. Görsel ise + logo_overlay aktifse → logo ekle
    2. Video ise + intro_video_url varsa → intro/outro ekle

    İşlenen URL döner; herhangi bir adım başarısız olursa orijinal URL korunur.
    """
    final_url = output_url
    logo_overlay = brand_kit.get("logo_overlay", {})
    intro_video = brand_kit.get("intro_video", {})

    is_image = content_type in ("image", "carousel")
    is_video = content_type in ("video", "faceless_video", "ugc_video")

    # Logo overlay — sadece görseller için
    if is_image and logo_overlay.get("enabled") and logo_url:
        processed = await add_logo_overlay(
            image_url=output_url,
            logo_url=logo_url,
            post_id=post_id,
            brand_id=brand_id,
            position=logo_overlay.get("position", "bottom-right"),
            opacity=float(logo_overlay.get("opacity", 0.8)),
        )
        if processed:
            final_url = processed

    # Intro video — sadece videolar için
    if is_video and intro_video_url:
        merged = await add_intro_video(
            main_video_url=final_url,
            intro_video_url=intro_video_url,
            post_id=post_id,
            brand_id=brand_id,
            position=intro_video.get("position", "start"),
        )
        if merged:
            final_url = merged

    return final_url
