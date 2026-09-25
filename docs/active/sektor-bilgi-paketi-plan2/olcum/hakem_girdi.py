"""Kör hakem girdisi: senaryo + beklenen + hata ölçütü + A/B metinleri (anahtarsız).
Koşum: python3 hakem_girdi.py <senaryo.json> <sonuc_dizini>  → <sonuc_dizini>/hakem-girdi.md"""
import json, sys
from pathlib import Path
scns = json.load(open(sys.argv[1], encoding="utf-8"))
res = Path(sys.argv[2])
b = {r["id"]: r for r in json.load(open(res / "b-sonuc.json", encoding="utf-8"))["sonuclar"]}
key = json.load(open(res / "b-anahtar.json", encoding="utf-8"))
kanal = {"M": "yalnız fiziksel mağaza", "MW": "mağaza + WhatsApp hattı + randevu sistemi",
         "E": "yalnız e-ticaret sitesi", "H": "mağaza + WhatsApp + randevu + e-ticaret sitesi"}
L = ["# Kör hakem girdisi", ""]
for s in scns:
    d = s.get("special_day"); p = s.get("product")
    L += [f"## {s['id']} — {s['baslik']}",
          f"- Markanın kanalları: {kanal[s['kanal']]}",
          f"- Özel gün: {d['name']}" if d else "- Özel gün: —",
          f"- Ürün: {p['name']} — {p['description']}" if p else "- Ürün: —",
          f"- Markanın isteği: {s.get('user_prompt')}",
          "- Beklenen: " + " | ".join(s["beklenen"]),
          "- Hata ölçütleri: " + " | ".join(f"H{i+1}: {h}" for i, h in enumerate(s["hata_olcutleri"])), ""]
    for side in ("A", "B"):
        r = b[s["id"]][key[s["id"]][side]]
        L += [f"### Metin {side}", "", (r["caption"].strip() or ("[Model metin YAZMADI, şu yanıtı verdi:] " + str(r["ham"].get("message", "")) if r["ham"].get("error") else "[boş]")), "", f"Görsel talimatı: {r['image_prompt']}", ""]
(res / "hakem-girdi.md").write_text("\n".join(L), encoding="utf-8")
print(res / "hakem-girdi.md", len("\n".join(L)))
