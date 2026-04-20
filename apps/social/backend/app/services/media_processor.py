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


# ─── Logo variant selection (luminosity-based) ───────────────────────────────

def _compute_luminosity(image_bytes: bytes) -> float | None:
    """
    Görselin ortalama parlaklığını 0.0–1.0 aralığında döndürür.

    PIL ile grayscale moduna çevrilen **bellekte ayrı bir kopya** üzerinde
    ImageStat.mean hesaplanır; orijinal bytes asla değiştirilmez.
    Pillow yoksa veya bozuk görselse None döner.
    """
    try:
        from PIL import Image, ImageStat  # type: ignore
    except ImportError:
        return None

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        mean = ImageStat.Stat(img).mean[0]
        return mean / 255.0
    except Exception:
        return None


def _pick_logo_variant(
    background_bytes: bytes,
    logo_light_url: str | None,
    logo_dark_url: str | None,
) -> str | None:
    """
    Arka plan parlaklığına göre kontrast sağlayan logo varyantını seçer.

    Koyu arka plan (luminosity <= 0.5)  → logo_light_url
    Açık arka plan (luminosity >  0.5) → logo_dark_url

    Yalnızca bir varyant varsa o dönülür (fallback).
    Luminosity hesaplanamazsa light (varsa) veya dark (varsa) kullanılır.
    """
    if not logo_light_url and not logo_dark_url:
        return None
    if logo_light_url and not logo_dark_url:
        return logo_light_url
    if logo_dark_url and not logo_light_url:
        return logo_dark_url

    lum = _compute_luminosity(background_bytes)
    if lum is None:
        return logo_light_url

    return logo_dark_url if lum > 0.5 else logo_light_url


# ─── Logo Overlay ────────────────────────────────────────────────────────────

async def add_logo_overlay(
    image_url: str,
    logo_url: str,
    post_id: UUID,
    brand_id: UUID,
    position: str = "bottom-right",
    opacity: float = 0.8,
) -> tuple[str, tuple[int, int, int, int]] | None:
    """
    Görsel üzerine logo bindirme.

    position: top-left | top-right | bottom-left | bottom-right
    opacity:  0.0 – 1.0

    Başarılı olursa (url, (x, y, w, h)) döner — bbox text overlay çakışma
    kontrolünde kullanılır. Başarısız olursa None (orijinal URL korunur).
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

        # Logo'yu görselin %20'sine aktif scale et (küçük logoyu da büyütür)
        target_w = int(base.width * 0.20)
        max_h = int(base.height * 0.20)
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        if target_h > max_h:
            ratio = max_h / logo.height
            target_w = int(logo.width * ratio)
            target_h = max_h
        logo = logo.resize((max(1, target_w), max(1, target_h)), Image.LANCZOS)

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
        uploaded_url = r2.upload(buf.read(), dest_path, "image/jpeg")
        return uploaded_url, (paste_x, paste_y, lw, lh)

    except Exception:
        return None


# ─── Text Overlay ────────────────────────────────────────────────────────────

_TEXT_OVERLAY_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _load_overlay_font(size: int):
    try:
        from PIL import ImageFont  # type: ignore
    except ImportError:
        return None
    for path in _TEXT_OVERLAY_FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size=size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


async def add_text_overlay(
    image_url: str,
    text_lines: list[str],
    position: str,
    post_id: UUID,
    brand_id: UUID,
    excluded_bbox: tuple[int, int, int, int] | None = None,
) -> str | None:
    """
    Görsel üzerine çok satırlı metin bindirme (template.imageTextOverlay için).

    - Font boyutu görsel genişliğinin ~%5.5'i; margin genişliğin ~%4'ü.
    - İlk satır (başlık) diğerlerinden %25 daha büyük render edilir.
    - Auto-shrink: en geniş satır usable alana sığana kadar font küçültülür.
    - Luminosity-aware: yazı bölgesinin ortalama parlaklığına göre fill/stroke
      beyaz-siyah veya siyah-beyaz seçilir (açık zeminde siyah yazı, koyu
      zeminde beyaz yazı).
    - excluded_bbox: aynı yatay şeritte logo varsa yazı alanı logo'dan kaçınır.
    """
    if not text_lines:
        return None

    try:
        from PIL import Image, ImageDraw, ImageStat  # type: ignore
    except ImportError:
        return None

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            img_resp = await client.get(image_url)
            img_resp.raise_for_status()

        base = Image.open(io.BytesIO(img_resp.content)).convert("RGBA")
        bw, bh = base.size

        max_body_size = max(24, int(bw * 0.055))
        min_body_size = max(20, int(bw * 0.03))
        margin = max(24, int(bw * 0.04))

        is_bottom = position.startswith("bottom")
        is_right = position.endswith("right")

        # Usable horizontal band — logo aynı yatay şeritteyse dışla
        text_left = margin
        text_right = bw - margin
        if excluded_bbox is not None:
            ex, ey, ew, eh = excluded_bbox
            logo_in_bottom_half = (ey + eh / 2) > (bh / 2)
            same_strip = logo_in_bottom_half == is_bottom
            if same_strip:
                pad = margin
                if is_right and ex < bw / 2:
                    text_left = max(text_left, ex + ew + pad)
                elif (not is_right) and (ex + ew) > bw / 2:
                    text_right = min(text_right, ex - pad)

        usable_w = max(min_body_size * 3, text_right - text_left)

        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        body_font_size = max_body_size
        title_font = None
        body_font = None
        rendered: list[tuple[str, int, int]] = []
        total_h = 0
        line_gap = 0
        max_w = 0

        while True:
            title_font_size = int(body_font_size * 1.25)
            title_font = _load_overlay_font(title_font_size)
            body_font = _load_overlay_font(body_font_size)
            if title_font is None or body_font is None:
                return None

            line_gap = int(body_font_size * 0.25)
            rendered = []
            total_h = 0
            max_w = 0

            for idx, line in enumerate(text_lines):
                font = title_font if idx == 0 else body_font
                bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                rendered.append((line, w, h))
                if w > max_w:
                    max_w = w
                total_h += h + (line_gap if idx < len(text_lines) - 1 else 0)

            if max_w <= usable_w or body_font_size <= min_body_size:
                break
            body_font_size = max(min_body_size, int(body_font_size * 0.9))

        y_start = bh - margin - total_h if is_bottom else margin
        x_start = (text_right - max_w) if is_right else text_left

        # Yazı bölgesinin luminosity'sini ölç → renk seçimi
        pad = 4
        sample_box = (
            max(0, x_start - pad),
            max(0, y_start - pad),
            min(bw, x_start + max_w + pad),
            min(bh, y_start + total_h + pad),
        )
        try:
            sample = base.crop(sample_box).convert("L")
            mean_lum = ImageStat.Stat(sample).mean[0] / 255.0
        except Exception:
            mean_lum = 0.3  # fallback: koyu kabul → beyaz yazı

        if mean_lum > 0.5:
            fill_color = (0, 0, 0, 255)
            stroke_color = (255, 255, 255, 255)
        else:
            fill_color = (255, 255, 255, 255)
            stroke_color = (0, 0, 0, 255)

        y = y_start
        for idx, (line, w, h) in enumerate(rendered):
            font = title_font if idx == 0 else body_font
            x = (text_right - w) if is_right else text_left
            draw.text(
                (x, y),
                line,
                font=font,
                fill=fill_color,
                stroke_width=3,
                stroke_fill=stroke_color,
            )
            y += h + line_gap

        result = Image.alpha_composite(base, overlay).convert("RGB")

        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=92)
        buf.seek(0)

        dest_path = f"brands/{brand_id}/posts/generated/{post_id}_text.jpg"
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
    logo_light_url: str | None,
    logo_dark_url: str | None,
    intro_video_url: str | None,
    text_overlay_lines: list[str] | None = None,
    text_overlay_position: str = "bottom-left",
) -> str:
    """
    Fal.ai üretimi sonrası marka işlemlerini uygula.

    1. Görsel ise + logo_overlay aktifse → arka plan parlaklığına göre
       uygun logo varyantını seçip ekle
    2. Video ise + intro_video_url varsa → intro/outro ekle

    İşlenen URL döner; herhangi bir adım başarısız olursa orijinal URL korunur.
    """
    final_url = output_url
    logo_overlay = brand_kit.get("logo_overlay", {})
    intro_video = brand_kit.get("intro_video", {})

    is_image = content_type in ("image", "carousel")
    is_video = content_type in ("video", "faceless_video", "ugc_video")

    # Logo overlay — sadece görseller için
    logo_bbox: tuple[int, int, int, int] | None = None
    if is_image and logo_overlay.get("enabled") and (logo_light_url or logo_dark_url):
        chosen_logo_url: str | None = None
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                bg_resp = await client.get(output_url)
                bg_resp.raise_for_status()
                chosen_logo_url = _pick_logo_variant(
                    bg_resp.content, logo_light_url, logo_dark_url
                )
        except Exception:
            chosen_logo_url = logo_light_url or logo_dark_url

        if chosen_logo_url:
            logo_result = await add_logo_overlay(
                image_url=output_url,
                logo_url=chosen_logo_url,
                post_id=post_id,
                brand_id=brand_id,
                position=logo_overlay.get("position", "bottom-right"),
                opacity=float(logo_overlay.get("opacity", 0.8)),
            )
            if logo_result:
                final_url, logo_bbox = logo_result

    # Template text overlay — sadece görseller için
    if is_image and text_overlay_lines:
        text_processed = await add_text_overlay(
            image_url=final_url,
            text_lines=text_overlay_lines,
            position=text_overlay_position,
            post_id=post_id,
            brand_id=brand_id,
            excluded_bbox=logo_bbox,
        )
        if text_processed:
            final_url = text_processed

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
