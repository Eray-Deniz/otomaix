"""Eray'ın kör okuma dosyası (C): durum + A/B metinleri, anahtarsız.
Koşum: python3 kor_okuma.py <senaryo.json> <sonuc_dizini> <hedef.md>"""
import json, sys
from pathlib import Path
scns = json.load(open(sys.argv[1], encoding="utf-8"))
res = Path(sys.argv[2])
b = {r["id"]: r for r in json.load(open(res / "b-sonuc.json", encoding="utf-8"))["sonuclar"]}
key = json.load(open(res / "b-anahtar.json", encoding="utf-8"))
kanal = {"M": "yalnız fiziksel mağazası var", "MW": "mağazası, WhatsApp hattı ve randevu sistemi var",
         "E": "yalnız internet sitesi var (mağazası yok)", "H": "mağazası, WhatsApp'ı, randevusu ve internet sitesi var"}
L = ["# Kör okuma — Kuyumculuk paketi sınavı (2026-09-25)", "",
     "Her durumda aynı istek için yazılmış iki Instagram metni var: **A** ve **B**. Biri sektör paketiyle, "
     "biri paketsiz yazıldı; hangisinin hangisi olduğu burada yazmıyor.", "",
     "**Yapacağın:** Her durumun sonundaki satırlara yaz.", "",
     "- **Seçimin:** bu markanın sahibi olsan hangisini yayınlardın → `A` / `B` / `ikisi de olmaz`",
     "- **Not (isteğe bağlı):** gözüne batan bir şey (uydurma bilgi, olmayan kanala çağrı, kuyumcu böyle "
     "konuşmaz, yazım hatası…)", "",
     "Görsel talimatı, yapay zekânın resmi çizmesi için yazdığı tariftir (İngilizce olabilir); istersen ona da bak.",
     "", "---", ""]
for s in scns:
    d = s.get("special_day"); p = s.get("product")
    L += [f"## {s['id']} — {s['baslik']}", "",
          f"- **Marka:** {kanal[s['kanal']]}",
          f"- **Özel gün:** {d['name']}" if d else "- **Özel gün:** —",
          f"- **Ürün:** {p['name']} — {p['description']}" if p else "- **Ürün:** —",
          f"- **Markanın isteği:** {s.get('user_prompt')}", ""]
    for side in ("A", "B"):
        r = b[s["id"]][key[s["id"]][side]]
        L += [f"### {side}", "", (r["caption"].strip() or ("[Model metin YAZMADI, şu yanıtı verdi:] " + str(r["ham"].get("message", "")) if r["ham"].get("error") else "[boş]")), "", f"> _Görsel talimatı:_ {r['image_prompt']}", ""]
    L += ["**Seçimin:** ", "", "**Not:** ", "", "---", ""]
Path(sys.argv[3]).write_text("\n".join(L), encoding="utf-8")
print("yazıldı:", sys.argv[3])
