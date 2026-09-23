---
task: sektor-bilgi-paketi-plan2
written: 2026-09-23
---

# Resume From

**SIRADAKİ İŞ (TASK Open Problems):** `kosu-23e19d03` ONAYLANDI (taslak `66654971…` sürüm 1, snapshot
`ac1a062b…`). Kalan tek adım `aktive-et` — Eray'ın AYRI onayıyla; sonra Task 19 Step 11 (marka
öneri/teyit + arayüz doğrulaması). Açık: yetki belgesi numarası marka ayarlarında yok (evi yok, tarih Eray'da).

**Bugün (2026-09-23) ne oldu:** iki canlı koşu (ikisi de sentezi tek denemede geçti — 22 Eylül onarımları
canlıda ilk kez sınandı); kör yargı alındı; motor `blocked`. Beş kusur kapandı, hepsi push'suz dalda:
`3fc7ad8` sayaç (10 soru 30 sayılıyordu) · `1892375` onay özeti açık soruları kesmez · `218c886` denetçi
alan anahtarı (8 video kodunun 8'i düşüyordu) · `f9443c7` bağ kuralları sentezde, düzeltme hakkıyla ·
`6fd7416` K-129 ortak kural (Eray kararı; sektör sözlüğü ölçülüp düşürüldü). Sonra: `6c2276e` modele giden
K-129 metinleri (dış depo `7fb81c3`) · **operatör kararları yolu** (Decisions Log): "düzeltme turu" bu
koşuya uygulanamıyordu — `blocked` koşunun açık sorularını kapatan giriş YOKTU; Eray "spec atla, direkt
çöz" dedi; `operator-karar` + migration 037 yazıldı, canlıya uygulandı, `23e19d03`'e yazıldı.

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
| Katman-1 (`1892375`) | `pytest tests/prompt_regression/ -q` 124 passed; tasdik actor eray — `6c2276e` sonrası BAYAT |
| Tam takım (operatör kararları) | **4836 passed / 0 failed / 408,1 s** (33 yeni test) |
| Mutasyon (operatör kararları) | 10/10 yakalandı (kapsam · diğer-engel · bayrak · takvim · koru→guncelle · ekle→reddedilen-aday · no_change · soru_basi · HUKUKİ etiketi · görüntü alanı); kaynaklar bayt bayt geri döndü |
| `23e19d03` kuru + yazım | `operator-karar --kuru` rc=0 → yazım rc=0: `activation_eligible`, açık soru 11 → 0, 78 birim işlemi (hukuki 4); `motor_ilk_sonucu.sonuc=blocked`; `load_verified_run` yedi kapıdan geçti |
| Katman-1 tazeleme | `pytest tests/prompt_regression/ -q` @ `fa52d9d` → 124 passed; tasdik PASS |
| Taslak + Katman-2 + onay | `yazim` rc=0 (sürüm 1) · Katman-2 8 çağrı 0,273 USD, kör seçim paketli 2/4 · `onay` rc=0, 252 sn |
| Migration 037 canlı | `psql --single-transaction -f 037_operator_decisions.sql` → `CREATE TABLE`; `\d` beklenen şekil |

**DENENMEYEN / DOĞRULANMAYAN:**
- `f9443c7`'nin düzeltme yolu CANLIDA hiç çalışmadı: iki koşunun sentezi de bu kapı yazılmadan önce
  üretildi. Kapı o çıktılara uygulansaydı ikisinde de 1 bağ hatası (yetki belgesi) → 1 düzeltme çağrısı.
- `6fd7416` canlı koşuda sınanmadı; ölçüm yazmadan oynatma + 109 araştırma iddiası + 12 sektör rehberi.
- Beş commit'i bağımsız hakem GÖRMEDİ (Eray: review yükü). `/security-review-claude-codex` evi merge öncesi.
- Sektör sözlüğü yalnız kuyumculuk verisiyle ölçüldü; başka sektör verisi yok.
- Operatör kararları kodu (`operator_decisions.py`, `runs.record_operator_resolution`, CLI, onay
  görüntüsü şema 3) bağımsız hakem GÖRMEDİ ve spec'siz yazıldı (Eray kararı; ⚠️ tasarım hatası riski).
- Operatörün eklediği metinleri Claude yazdı; üretimde (caption/görsel) nasıl davrandıkları ölçülmedi.
- `037_down.sql` testle sınanmadı (yalnız ileri yön migration testlerinden geçti).

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
- Operatör kararı TEK SEFERDİR; yanlış yazılmışsa geri dönüş taslağı reddedip düzeltme turu açmaktır.
- Kaynaksız operatör eklemeleri (ör. bayram girdileri, hizmet CTA'ları) araştırma kanıtı taşımaz;
  onay özeti onları listeler, ama doğrulukları Eray'ın bilgisine dayanır.
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
ölçülmedi) · operatör kararları: `record_operator_resolution`'ın f-string SQL'i (kolon adları sabit
eşlemeden gelir, değerler parametreli) · karar dosyası dış girdi olarak — işlem kümesi kapalı mı,
bir işlem motorun başka kapısını aşabiliyor mu.
