"""Ölçüm B — ücretli model değerlendirmesi (gönderi kaydı YOK).

Her senaryo `generate_captions` ile paketli ve paketsiz GERÇEK modelle yazdırılır.
Çağrı yolu: fonksiyon doğrudan çağrılır; router atlanır → `generation_stamps`,
paket olayı, gönderi kaydı yazılmaz (kod okundu; `caption_generator.py` içinde DB
yazımı yok). Görsel ÜRETİLMEZ — yalnız görsel talimatı (image_prompt) metni gelir.
Veritabanı: yalnız OKUMA (aktif paket satırı).

Anahtar: `ANTHROPIC_API_KEY` süreç ortamından (/root/.anthropic-key), dosyaya yazılmaz.
Maliyet: her çağrının `usage`'ı kaydedilir, 23 Eylül fiyatlarıyla (girdi 5 · önbellek
yazma 6,25 · okuma 0,5 · çıktı 25 USD/M token) toplanır.

Kör çıktı: her senaryoda paketli/paketsiz sırası sabit tohumla karıştırılır;
`b-kor.md` anahtarsızdır, anahtar `b-anahtar.json`'dadır.
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import olcum_a as A  # noqa: E402  (yol + paket bağlamı + senaryo kurulumu ortak)

import anthropic  # noqa: E402

from app.core.caption_generator import generate_captions  # noqa: E402

PRICE = {"input": 5.0, "cache_write": 6.25, "cache_read": 0.5, "output": 25.0}
USAGE: list[dict] = []
_RealAnthropic = anthropic.Anthropic


class _Recording(_RealAnthropic):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        real_create = self.messages.create

        def create(**kwargs):
            msg = real_create(**kwargs)
            u = msg.usage
            USAGE.append({
                "input": u.input_tokens,
                "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0,
                "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                "output": u.output_tokens,
            })
            return msg

        self.messages.create = create


def _cost(u: dict) -> float:
    return sum(u[k] * PRICE[k] for k in PRICE) / 1_000_000


async def _generate(scn: dict, ctx) -> dict:
    day = scn.get("special_day") or {}
    before = len(USAGE)
    res = await generate_captions(
        brand={"id": A.BRAND_ID, "name": "Deniz Kuyumculuk", "sector_slug": A.SECTOR_SLUG},
        brand_kit={"channels": {k: True for k in A.PROFILES[scn["kanal"]]}},
        template=None, template_fields=None,
        user_prompt=scn.get("user_prompt"), rag_context=None,
        platforms=["instagram"], product=scn.get("product"), content_type="image",
        special_day_name=day.get("name"), special_day_category=day.get("category"),
        package_context=ctx,
    )
    calls = USAGE[before:]
    fallback = len(calls) == 0 or res.get("default_caption", "") == (scn.get("user_prompt") or "")
    caption = res.get("default_caption") or (
        (res.get("platform_captions") or {}).get("instagram") or {}).get("caption", "")
    return {
        "caption": caption,
        "ham": res,
        "image_prompt": res.get("image_prompt", ""),
        "hashtags": res.get("hashtags", []),
        "usage": calls, "maliyet_usd": round(sum(_cost(c) for c in calls), 5),
        "fallback": fallback,
    }


async def main(scn_path: str, out_dir: str, seed: int) -> None:
    anthropic.Anthropic = _Recording
    scenarios = json.loads(Path(scn_path).read_text(encoding="utf-8"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ctx = await A._load_context()
    rng = random.Random(seed)
    results, key, blind = [], {}, []
    for scn in scenarios:
        packed = await _generate(scn, ctx)
        plain = await _generate(scn, None)
        results.append({"id": scn["id"], "paketli": packed, "paketsiz": plain})
        order = ["paketli", "paketsiz"]
        rng.shuffle(order)
        key[scn["id"]] = {"A": order[0], "B": order[1]}
        pair = {"A": packed if order[0] == "paketli" else plain,
                "B": plain if order[0] == "paketli" else packed}
        blind.append((scn, pair))
        print(f"{scn['id']} tamam · paketli {packed['maliyet_usd']} $ · paketsiz {plain['maliyet_usd']} $"
              + (" · FALLBACK!" if packed["fallback"] or plain["fallback"] else ""), flush=True)

    total = sum(_cost(u) for u in USAGE)
    (out / "b-sonuc.json").write_text(json.dumps(
        {"cagri": len(USAGE), "toplam_usd": round(total, 4), "tohum": seed, "sonuclar": results},
        ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "b-anahtar.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# Kör okuma — hangi metin paketli bilinmiyor", ""]
    for scn, pair in blind:
        lines += [f"## {scn['id']} — {scn['baslik']}", f"*İstek:* {scn.get('user_prompt')}", ""]
        for side in ("A", "B"):
            lines += [f"**{side}:**", "", pair[side]["caption"], "",
                      f"_Görsel talimatı:_ {pair[side]['image_prompt']}", ""]
        lines += ["**Seçimin:** A / B  ·  **Not:**", "", "---", ""]
    (out / "b-kor.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"TOPLAM: {len(USAGE)} çağrı · {total:.4f} USD")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3])))
