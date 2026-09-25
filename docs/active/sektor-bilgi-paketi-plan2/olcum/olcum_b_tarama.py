"""Ölçüm B — çıktı taraması (model çağrısı YOK).

`b-sonuc.json`daki her metni kural kümesine karşı tarar. Kurallar ayar koşusunda
KALİBRE edilir; sınav kümesinden ÖNCE sabitlenir (TASK madde 13 eşik yöntemi).
Kural bir "şüphe" işaretidir: kesin karar, işaretli metnin okunmasıyla verilir.

Koşum: python3 olcum_b_tarama.py <senaryo.json> <b-sonuc.json>
"""

from __future__ import annotations

import json
import re
import sys

KANAL_DESENI = {
    "eticaret_sitesi": r"\b(web ?sitemiz|sitemiz|online mağaza|link(i)? ?bio|bio'?daki|profildeki link|sipariş ver)",
    "fiziksel_magaza": r"\b(mağaza(mız|mıza|mızda|larımız)|showroom|ziyaret ed)",
    "whatsapp_hatti": r"\bwhats ?app",
    "randevu_sistemi": r"\brandevu",
}
PROFILES = {
    "M": {"fiziksel_magaza"},
    "MW": {"fiziksel_magaza", "whatsapp_hatti", "randevu_sistemi"},
    "E": {"eticaret_sitesi"},
    "H": {"fiziksel_magaza", "whatsapp_hatti", "randevu_sistemi", "eticaret_sitesi"},
}
GENEL = {
    # ADAY işareti: olumsuz cümleyi ("garanti taşımaz") ayıramaz — karar hakemde (ayar koşusu K17).
    "getiri-dili-aday": r"(kazandır|kazanın|değer kaybetme|güvenli yatırım|\byatırım|yatırım aracı|\bgetiri\b)",
    "sahte-aciliyet": r"(son gün|kaçırma|sınırlı sayıda|stoklarla sınırlı|acele edin|son \d+ adet|hemen şimdi)",
    "ucretsiz-vaat": r"ücretsiz|bedava",
    "yetki-belgesi": r"yetki belgesi",
    "abarti": r"(en iyi|en kaliteli|dünyanın|türkiye'nin en|rakipsiz|bir numara)",
}
SATIS = r"(satın al|sipariş|fiyat|indirim|kampanya|koleksiyon(umuz)?u keşfe|mağazamıza bekler|ziyaret edin)"


def _kanal_sapmasi(text: str, kanal: str) -> list[str]:
    var = PROFILES[kanal]
    return [k for k, d in KANAL_DESENI.items() if k not in var and re.search(d, text, re.I)]


def tara(scn: dict, text: str) -> list[str]:
    t = text.lower()
    bulgu = [f"{k}" for k, d in GENEL.items() if re.search(d, t, re.I)]
    bulgu += [f"kanal-disi:{k}" for k in _kanal_sapmasi(t, scn["kanal"])]
    day = scn.get("special_day") or {}
    # Paketin türü takvim kategorisinden üstündür (K-03): Yılbaşı `national` ama paket türü
    # ticari-fırsat (ayar koşusu K09). Paketsiz yolda kategori geçerlidir.
    satissiz = day.get("category") == "national" and day.get("name") != "Yılbaşı"
    if satissiz and re.search(SATIS, t, re.I):
        bulgu.append("anma-kutlama-gunu-satis")
    prod = scn.get("product") or {}
    desc = prod.get("description", "")
    if re.search(r"\d+ ?ayar", desc, re.I) and not re.search(r"\d+ ?ayar", t):
        bulgu.append("ayar-yok")
    if re.search(r"\d+[.,]?\d* ?gr(am)?\b", desc, re.I) and not re.search(r"\d+[.,]?\d* ?gr(am)?\b", t):
        bulgu.append("gramaj-yok")
    if re.search(r"\bTL\b", desc) and re.search(r"\d ?tl\b", t) and not re.search(r"gram(ı)? ?(fiyat|başı)|/ ?gr|gr(am)? başına", t):
        bulgu.append("gram-fiyati-yok")
    if re.search(r"laboratuvar|sentetik", desc, re.I) and not re.search(r"laboratuvar|sentetik", t):
        bulgu.append("sentetik-ibaresi-yok")
    if "925" in desc and re.search(r"\b(14|18|22|24) ?ayar|altın", t):
        bulgu.append("gumus-altin-karisik")
    return bulgu


def main(scn_path: str, sonuc_path: str) -> None:
    scns = {s["id"]: s for s in json.load(open(scn_path, encoding="utf-8"))}
    data = json.load(open(sonuc_path, encoding="utf-8"))
    ozet = {"paketli": 0, "paketsiz": 0}
    for r in data["sonuclar"]:
        scn = scns[r["id"]]
        line = [r["id"]]
        for side in ("paketli", "paketsiz"):
            b = tara(scn, r[side]["caption"])
            if r[side]["fallback"]:
                b.append("FALLBACK")
            ozet[side] += len(b)
            line.append(f"{side}: {', '.join(b) or '—'}")
        print(" | ".join(line))
    print(f"\nişaret sayısı → paketli {ozet['paketli']} · paketsiz {ozet['paketsiz']} "
          f"· {data['cagri']} çağrı · {data['toplam_usd']} USD")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
