"""Ölçüm A — yazmasız istem kontrolü (model çağrısı YOK, ücretsiz).

Her senaryo için üretimin KENDİ yolu (`generate_captions`) paketli ve paketsiz
çalıştırılır; Anthropic çağrısı Katman-1'in yakalama aracıyla kesilir, modele
gidecek talimat bayt bayt kaydedilir ve kuralla denetlenir.

Veritabanı: yalnız OKUMA (aktif paket satırı). Yazım yok.

Koşum (backend dizininden):
    .venv/bin/python -B ../../../docs/active/sektor-bilgi-paketi-plan2/olcum/olcum_a.py \
        <senaryo.json> <cikti_dizini>
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from uuid import UUID

BACKEND = Path(__file__).resolve().parents[4] / "apps" / "social" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

import asyncpg  # noqa: E402
from _pytest.monkeypatch import MonkeyPatch  # noqa: E402

from app.core.caption_generator import generate_captions  # noqa: E402
from app.core.templates_data import SECTOR_GUIDANCE  # noqa: E402
from app.services.sector_packages import (  # noqa: E402
    SectorPackageContext,
    filter_channel_dependent,
    normalize_special_day_key,
)
from tests.prompt_regression.capture import capture_anthropic_calls  # noqa: E402

PACKAGE_ID = "66654971-d90e-4cec-92da-61e723a8ec8f"
BRAND_ID = "cb1dd79e-5ed4-452e-90cb-9ae1e88a5319"
SECTOR_SLUG = "e-ticaret-perakende"
PROFILES = {
    "M": ["fiziksel_magaza"],
    "MW": ["fiziksel_magaza", "whatsapp_hatti", "randevu_sistemi"],
    "E": ["eticaret_sitesi"],
    "H": ["fiziksel_magaza", "whatsapp_hatti", "randevu_sistemi", "eticaret_sitesi"],
}
NO_DIGITS_RULE = "caption'da rakamı yazma"


def _db_url() -> str:
    for line in (BACKEND / ".env").read_text().splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip().strip('"').replace("+asyncpg", "")
    raise SystemExit("DATABASE_URL yok")


async def _load_context() -> SectorPackageContext:
    conn = await asyncpg.connect(_db_url())
    try:
        row = await conn.fetchrow(
            "SELECT p.id, p.version, p.content, s.slug FROM social.sector_packages p "
            "JOIN social.sectors s ON s.id = p.sector_id WHERE p.id = $1",
            UUID(PACKAGE_ID),
        )
    finally:
        await conn.close()
    return SectorPackageContext(
        package_id=row["id"], version=row["version"],
        content=json.loads(row["content"]), sub_sector_slug=row["slug"],
    )


async def _capture(scn: dict, context: SectorPackageContext | None) -> str:
    mp = MonkeyPatch()
    try:
        calls = capture_anthropic_calls(mp)
        day = scn.get("special_day") or {}
        await generate_captions(
            brand={"id": BRAND_ID, "name": "Deniz Kuyumculuk", "sector_slug": SECTOR_SLUG},
            brand_kit={"channels": {k: True for k in PROFILES[scn["kanal"]]}},
            template=None,
            template_fields=None,
            user_prompt=scn.get("user_prompt"),
            rag_context=None,
            platforms=["instagram"],
            product=scn.get("product"),
            content_type="image",
            special_day_name=day.get("name"),
            special_day_category=day.get("category"),
            package_context=context,
        )
    finally:
        mp.undo()
    if len(calls) != 1:
        raise RuntimeError(f"{scn['id']}: {len(calls)} çağrı yakalandı, 1 bekleniyordu")
    return calls[0].rendered


def _alternatives(cta: str) -> list[str]:
    return [a.strip() for a in cta.split("·") if a.strip()]


def _checks(scn: dict, ctx: SectorPackageContext, packed: str, plain: str) -> list[dict]:
    content = ctx.content
    channels = {k: True for k in PROFILES[scn["kanal"]]}
    out: list[dict] = []

    def add(kod: str, ok: bool, detay: str) -> None:
        out.append({"kod": kod, "gecti": ok, "detay": detay})

    add("A1-paket-blogu", "SEKTÖR PAKETİ" in packed or ctx.sub_sector_slug in packed,
        "paket bloğu talimatta")
    add("A8-etiket-sizintisi", "kanal-bağımlı" not in packed,
        "ham `[kanal-bağımlı: …]` etiketi modele gitmiyor")

    # Liste CTA: alternatif-farkında beklenen ile basılan
    eligible = filter_channel_dependent(content.get("cta_kaliplari", []), channels)
    add("A4-cta-listesi", True, f"kanala uygun liste CTA sayısı: {len(eligible)}")

    day = scn.get("special_day")
    if day:
        key = normalize_special_day_key(day["name"])
        entry = (content.get("ozel_gun") or {}).get(key)
        if entry is None:
            add("A2-donem-blogu", "DÖNEM KALIPLARI" not in packed,
                f"pakette `{key}` yok → dönem bloğu basılmamalı")
        else:
            add("A2-donem-blogu", "DÖNEM KALIPLARI" in packed, f"`{key}` dönem bloğu talimatta")
            alts = _alternatives(entry.get("cta", ""))
            ok_alts = [a for a in alts if filter_channel_dependent([a], channels)]
            has_cta_line = "\nCTA:" in packed
            if ok_alts:
                add("A3-donem-cta", has_cta_line,
                    f"kanala uygun {len(ok_alts)}/{len(alts)} alternatif var → CTA satırı "
                    + ("VAR" if has_cta_line else "YOK (alternatif kayboldu)"))
            gv = entry.get("gorsel_vurgu", "")
            add("A9-donem-gorsel", bool(gv) and gv[:40] in packed,
                "günün görsel vurgusu talimatta " + ("VAR" if gv[:40] in packed else "YOK"))

    prod = scn.get("product") or {}
    if prod.get("description") and re.search(r"\d", prod["description"]):
        conflict = NO_DIGITS_RULE in packed
        add("A5-gramaj-celiskisi", not conflict,
            "paket 'ayar, gramaj açıkça söylenir' derken genel kural '" + NO_DIGITS_RULE + "' "
            + ("AYNI talimatta" if conflict else "yok"))

    guidance = SECTOR_GUIDANCE.get(SECTOR_SLUG, "")
    add("A6-rehber-kaybi", guidance not in packed,
        f"paketsizde perakende rehberi {'VAR' if guidance in plain else 'YOK'}, "
        f"paketlide {'VAR' if guidance in packed else 'YOK'} ({len(guidance)} kr) — "
        "bilgi amaçlı: kayıp beklenen tasarım, içeriği ayrıca incelenir")
    add("A7-yasaklar", "Yasaklar ve hassasiyetler" in packed, "yasaklar bloğu talimatta")
    return out


async def main(scn_path: str, out_dir: str) -> None:
    scenarios = json.loads(Path(scn_path).read_text(encoding="utf-8"))
    out = Path(out_dir)
    (out / "istemler").mkdir(parents=True, exist_ok=True)
    ctx = await _load_context()
    report = []
    for scn in scenarios:
        packed = await _capture(scn, ctx)
        plain = await _capture(scn, None)
        (out / "istemler" / f"{scn['id']}-paketli.txt").write_text(packed, encoding="utf-8")
        (out / "istemler" / f"{scn['id']}-paketsiz.txt").write_text(plain, encoding="utf-8")
        checks = _checks(scn, ctx, packed, plain)
        report.append({"id": scn["id"], "baslik": scn["baslik"], "kanal": scn["kanal"],
                       "paketli_kr": len(packed), "paketsiz_kr": len(plain), "kontroller": checks})
    (out / "a-rapor.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in report:
        fails = [c for c in r["kontroller"] if not c["gecti"]]
        mark = "KALDI" if fails else "geçti"
        print(f"{r['id']} {r['kanal']:2} {mark:5} {r['baslik']}")
        for c in fails:
            print(f"      ✗ {c['kod']}: {c['detay']}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
