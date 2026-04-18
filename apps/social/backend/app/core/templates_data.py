"""Phase 7 — Sektör-Spesifik Şablon Tanımları (backend tek kaynak).

Sprint 1: Boş iskelet — TEMPLATES ve SECTOR_GUIDANCE boş dict.
Sprint 2: 22 şablon + 11 sektör rehberi eklenecek.

Frontend bu veriyi `GET /templates` endpoint'i üzerinden çeker ve 1 saat cache eder.
Tek doğruluk kaynağı burasıdır; frontend'de hard-coded liste tutulmaz.
"""
from app.models.templates import Template


# ─── Şablon kataloğu ────────────────────────────────────────────────────────
# Anahtar: globally unique template_id (ör. "eticaret-urun-karti")
# Sprint 2'de doldurulacak.
TEMPLATES: dict[str, Template] = {}


# ─── Sektör rehberi (prompt enjeksiyonu için) ───────────────────────────────
# Anahtar: social.sectors.slug (ör. "e-ticaret-perakende")
# Değer: Claude'a gönderilecek sektöre özel Türkçe rehber.
# Sprint 2'de doldurulacak.
SECTOR_GUIDANCE: dict[str, str] = {}


# ─── Helper fonksiyonlar ────────────────────────────────────────────────────

def get_all_templates(
    sector: str | None = None,
    content_type: str | None = None,
) -> list[Template]:
    """
    Tüm şablonları filtreleyerek döndürür.

    - sector=None → tüm şablonlar
    - sector="e-ticaret-perakende" → bu sektöre ait + `["*"]` (genel) şablonlar
    - content_type="image" → sadece bu içerik tipini destekleyen şablonlar
    """
    results: list[Template] = []
    for tpl in TEMPLATES.values():
        if sector is not None:
            if sector not in tpl.sectors and "*" not in tpl.sectors:
                continue
        if content_type is not None:
            if content_type not in tpl.content_types:
                continue
        results.append(tpl)
    return results


def get_template_by_id(template_id: str) -> Template | None:
    """Tekil şablon getir. Bulunamazsa None döner."""
    return TEMPLATES.get(template_id)


def get_sector_guidance(sector_slug: str | None) -> str:
    """Sektör rehberini getir. Eşleşme yoksa boş string döner (prompt'ta no-op)."""
    if not sector_slug:
        return ""
    return SECTOR_GUIDANCE.get(sector_slug, "")
