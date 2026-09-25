"""A + B sonuçlarını tek okunabilir Markdown rapora ve ham veri klasörüne döker.

Koşum: python3 olcum_rapor.py <senaryo.json> <sonuc_dizini> <hedef_dizin> <etiket>
Hedefte: `<etiket>.md` (okunur rapor) + `<etiket>/` (a-rapor.json, b-sonuc.json,
istemler/*.txt — ham test verisi).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from olcum_b_tarama import tara  # noqa: E402

KANAL_AD = {"M": "yalnız mağaza", "MW": "mağaza + WhatsApp + randevu",
            "E": "yalnız e-ticaret", "H": "dört kanal"}


def main(scn_path: str, res_dir: str, target: str, label: str) -> None:
    scns = json.load(open(scn_path, encoding="utf-8"))
    res = Path(res_dir)
    a = {r["id"]: r for r in json.load(open(res / "a-rapor.json", encoding="utf-8"))}
    bdata = json.load(open(res / "b-sonuc.json", encoding="utf-8"))
    b = {r["id"]: r for r in bdata["sonuclar"]}

    out = Path(target)
    raw = out / label
    raw.mkdir(parents=True, exist_ok=True)
    for f in ("a-rapor.json", "b-sonuc.json"):
        shutil.copy2(res / f, raw / f)
    shutil.copy2(scn_path, raw / "senaryolar.json")
    if (res / "istemler").is_dir():
        shutil.copytree(res / "istemler", raw / "istemler", dirs_exist_ok=True)

    a_fail = sum(1 for r in a.values() for c in r["kontroller"] if not c["gecti"])
    marks = {"paketli": 0, "paketsiz": 0}
    for s in scns:
        for side in marks:
            marks[side] += len(tara(s, b[s["id"]][side]["caption"]))

    L = [
        f"# Kuyumculuk paketi ölçümü — {label}",
        "",
        f"Paket `66654971…` sürüm 1 · marka kurgu test markası · platform Instagram, tek görsel · "
        f"üretim modeli `claude-opus-4-6` (üretim kodu değiştirilmeden). Kaynak betikler: otomaix deposu "
        f"`docs/active/sektor-bilgi-paketi-plan2/olcum/`. Ham veri: `{label}/`.",
        "",
        "**A — yazmasız istem kontrolü:** modele gidecek talimat üretimin kendi koduyla kuruldu, model "
        "çağrılmadı (ücretsiz); kurallı kontroller talimat üzerinde.",
        "**B — model değerlendirmesi:** aynı senaryo paketli ve paketsiz gerçek modele yazdırıldı; gönderi "
        "kaydı, görsel üretimi yok. Tarama işaretleri kural tabanlıdır ve bir ŞÜPHEDİR — kesin karar metni "
        "okuyarak verilir.",
        "",
        "## Özet",
        "",
        f"- Senaryo: {len(scns)} · A'da kalan kontrol: {a_fail}",
        f"- B: {bdata['cagri']} çağrı · {bdata['toplam_usd']} USD (her çağrının `usage`'ından)",
        f"- B tarama işareti: paketli {marks['paketli']} · paketsiz {marks['paketsiz']}",
        "",
    ]
    for s in scns:
        sid = s["id"]
        day = s.get("special_day")
        prod = s.get("product")
        L += [f"## {sid} — {s['baslik']}", "",
              f"- **Kanal:** {s['kanal']} ({KANAL_AD[s['kanal']]})",
              f"- **Özel gün:** {day['name']} ({day['category']})" if day else "- **Özel gün:** —",
              f"- **Ürün:** {prod['name']} — {prod['description']}" if prod else "- **Ürün:** —",
              f"- **İstek:** {s.get('user_prompt')}",
              "- **Beklenen:** " + " · ".join(s["beklenen"]),
              "- **Hata ölçütü:** " + " · ".join(s["hata_olcutleri"]), "",
              "**A kontrolleri:**", ""]
        for c in a[sid]["kontroller"]:
            L.append(f"- {'✓' if c['gecti'] else '✗'} `{c['kod']}` — {c['detay']}")
        L.append("")
        for side in ("paketli", "paketsiz"):
            r = b[sid][side]
            flags = tara(s, r["caption"]) + (["FALLBACK"] if r["fallback"] else [])
            L += [f"### {side.capitalize()} metin ({r['maliyet_usd']} USD)", "",
                  r["caption"].strip() or "_(boş)_", "",
                  f"_Görsel talimatı:_ {r['image_prompt']}", "",
                  f"_Hashtag:_ {' '.join(r.get('hashtags') or [])}", "",
                  f"_Tarama işaretleri:_ {', '.join(flags) or '—'}", ""]
        L += ["---", ""]
    (out / f"{label}.md").write_text("\n".join(L), encoding="utf-8")
    print(f"yazıldı: {out / (label + '.md')} + {raw}/")


if __name__ == "__main__":
    main(*sys.argv[1:5])
