---
task: sektor-bilgi-paketi-plan2
written: 2026-09-23
---

# Resume From

**SIRADAKİ İŞ (TASK Open Problems):**
1. ~~Modele giden K-129 metinleri~~ — KAPANDI: dış depo `7fb81c3` + otomaix pin/`synthesis.py`
   (TASK Open Problems). Tam takım 4802 passed / 0 failed / 403,8 s. Canlıda sınanmadı.
2. **`kosu-23e19d03` düzeltme turu** — kör yargı kararlarıyla (`K134-KOR-YARGI-23e19d03.md` özet
   tablosu). Önce `duzeltme-baslat`'ın ön koşulunu OKU (koşu `blocked`; K-72 "reddedilmiş koşu" diyor —
   ölçülmedi). Sorulmayan ayrıntılar bu turda Eray'a senaryolu sorulur: 8 Mart ve Babalar Günü görsel
   vurgu · Ramazan/Kurban "birikim" · Öğretmenler Günü `alma` CTA'ları. CTA ≥ 5 eşik kararı turun
   sonucuyla verilir.

**Bugün (2026-09-23) ne oldu:** iki canlı koşu (ikisi de sentezi tek denemede geçti — 22 Eylül onarımları
canlıda ilk kez sınandı); kör yargı alındı; motor `blocked`. Beş kusur kapandı, hepsi push'suz dalda:
`3fc7ad8` sayaç (10 soru 30 sayılıyordu) · `1892375` onay özeti açık soruları kesmez · `218c886` denetçi
alan anahtarı (8 video kodunun 8'i düşüyordu) · `f9443c7` bağ kuralları sentezde, düzeltme hakkıyla ·
`6fd7416` K-129 ortak kural (Eray kararı; sektör sözlüğü ölçülüp düşürüldü).

# Verification

| Ne | Taze çıktı |
|---|---|
| Tam takım (`6fd7416`) | **4802 passed / 0 failed / 406,0 s** (ara commit'lerde 4770 · 4771 · 4774 · 4780, hepsi 0 failed) |
| Mutasyon | sayaç 7/7 · onay 1/1 · alan anahtarı 5/5 · bağ kapısı 7/7 · K-129 8/8; kaynaklar yedekle bayt bayt geri döndü |
| Motor yeniden düzenleme (`f9443c7`) | üç gerçek koşunun `decide()` çıktısı öncesi/sonrası **bayt bayt aynı** |
| Sentez kapısı = motor | üç gerçek koşuda (birim, sebep) kümesi birebir aynı (1 · 1 · 52) |
| K-129 önce/sonra (yazmadan oynatma) | `23e19d03` ve `2851dc22`: kanıt-türü reddi 5 → 0, motorun kendi açık sorusu 6 → 1, yeni ret yok; `222706dc` değişmedi |
| Canlı: `2851dc22` | denetim 21,5 dk · sentez 7 dk 49 sn · 1,77 USD · 52.465 çıktı jetonu · araç çağrısı 0 · düzeltme 0 |
| Canlı: `23e19d03` | denetim 18,5 dk · sentez 9 dk 22 sn · 2,09 USD · 69.741 çıktı jetonu · araç çağrısı 0 · düzeltme 0 |
| Katman-1 (`1892375`) | `pytest tests/prompt_regression/ -q` 124 passed; tasdik actor eray |

**DENENMEYEN / DOĞRULANMAYAN:**
- `f9443c7`'nin düzeltme yolu CANLIDA hiç çalışmadı: iki koşunun sentezi de bu kapı yazılmadan önce
  üretildi. Kapı o çıktılara uygulansaydı ikisinde de 1 bağ hatası (yetki belgesi) → 1 düzeltme çağrısı.
- `6fd7416` canlı koşuda sınanmadı; ölçüm yazmadan oynatma + 109 araştırma iddiası + 12 sektör rehberi.
- Beş commit'i bağımsız hakem GÖRMEDİ (Eray: review yükü). `/security-review-claude-codex` evi merge öncesi.
- Sektör sözlüğü yalnız kuyumculuk verisiyle ölçüldü; başka sektör verisi yok.
- DB'deki `23e19d03` motor sonucu düzeltmelerden önceki motorun ürünü.

**TUZAKLAR:**
- Mutasyonda `__pycache__` sil + `python -B`; geri dönüşü dosya yedeğiyle yap (`git checkout` değil).
- Tam takımı sentez/denetim koşarken başlatma (sahne dizinine dokunan test olabilir — ölçülmedi).
- Yazmadan motor oynatma yöntemi: `_kos_motor`'un girdi kurulumu, salt-okunur işlem, `record_result`
  YOK (betik scratchpad'deydi, kalıcı değil — gerekirse yeniden yaz).
- Sahipsiz koşular: `kosu-2851dc22…` ve `kosu-7705437…` `calisiyor`.
- `~/.claude/settings.json`'da Eray'ın commit'lenmemiş değişiklikleri — dokunulmadı.

# Risks

- Yeni sentez kapısı bir bağ hatasında +1 çağrı açar (tahmin: bugünkü tek çağrı ölçümü 9 dk 22 sn ·
  2,09 USD kadar; düzeltme çağrısı ölçülmedi).
- K-129 ortak kuralının yanlış-negatifi: işaretsiz hukuki iddia içerik sınıfında kalır (ölçüldü: 25
  mevzuat iddiasının 9'u, 5'i yasak alanında); "yasal" demeyen "2 yıl garanti" normal sayılır.
- Model artık motorla aynı K-129 okumasını görüyor (`7fb81c3`); modelin bu okumayla sınıflandırması
  canlıda henüz görülmedi — ilk koşuda sentez günlüğündeki `kaynaksız:` notlarına bak.

# Notes For Claude

- **Kör yargı ve karar soruları:** her seçenek için somut senaryo + ham kanıt; Eray soyut soruyu
  "clarify" ile geri çeviriyor (bu oturumda 6 kez). Önce örnek, sonra soru.
- **Yeni alt sistem önermeden önce ihtiyacı ölç:** sözlük önerisi 302 maddelik ölçümle düştü.
- Motor ↔ sentez tutarlılığı artık `engine.ekle_bagini_coz` üzerinden; bağ kuralı eklenirse orada
  eklenir, sentez kendiliğinden görür.
- Codex kotası uzun turdan önce `_cqg_read` ile ölçülür.

# Notes For Codex

Güvenlik review'ı (merge öncesi) dikkat listesi: sentezin geçici sahne dizini (`_denemeyi_kos`) ve ham
akışın hata yolunda koşu köküne yazılması (önceki not) · `f9443c7`: sentezin motoru çağrı anında içe
aktarması ve düzeltme turunda önceki denemeye dönüş yolu (`yedek`) · `6fd7416`: `_HUKUKI_DIL_RE` ve
`_NICEL_IDDIA_RE` düzenli ifadelerinin karmaşıklığı (girdi araştırma metni; felaket geri izleme
ölçülmedi).
