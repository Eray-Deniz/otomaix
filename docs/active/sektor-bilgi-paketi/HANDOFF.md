# Handoff

## Context
- Task: sektor-bilgi-paketi — **faz: 45/45 ürün kararı kapandı + spec ONAYLANDI;
  sırada sentez deposu sweep'i ve sıfırdan plan**
- Last updated: 2026-08-23 (karar kapanış turu oturumu)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (status: `spec-approved`;
  tüm K-ID satırları kapanış statüsünde)
- Karar listesi: `docs/active/sektor-bilgi-paketi/KARAR-KAPANIS-LISTESI.md`
  (Durum sütunu dolu — arşivlik; kanonik kayıt TASK Decisions Log + spec)
- Review log: `docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-spec.md` (3 tur SHIP)
- ⚠️ Eski spec (2026-07-11) ve plan (2026-07-12) **superseded** — dikkate alınmaz.

## Current State
- **Karar turu bitti:** 45 karar Eray'la TEK TEK kapatıldı (toplu kapanış
  kullanılmadı; her soru somut akış/senaryo özetiyle soruldu — kalıcı format tercihi).
- **Öneriden farklı 3 karar:** K-71 açık sorular aktivasyonu BLOKLAR · K-45 çift
  yönlü bakım bildirimi (yönetici + müşteri mesaj çifti, metinler sabit) · K-56
  olay-bazlı ANINDA uyarı (eşik değil — paketsiz düşen her üretimde bildirim).
- **Genişlemeli kapanışlar:** K-26 sektör-başına periyot alanı + VADE BİLDİRİMİ ·
  K-69 hazırlık kapısı (K-70 sorumlusu=operatör dahil) · K-82 (K-83 dahil) ·
  K-142 (K-143 hiç doğmadı).
- **Faz 1'e eklenen iş kalemi:** bildirim mekanizması — K-45 + K-26 vade + K-56
  uyarı aynı altyapıda (plan görevi olacak).
- **Spec onayı:** Eray verdi; frontmatter `spec-approved` + `approved:` satırı.
- Kayıt üçlemesi tamam: liste Durum sütunu + spec K-ID kapanışları (kardeş-site
  sweep'li) + TASK Decisions Log tam döküm.

## Resume From (sıra)
1. **Sentez deposu sweep borcu:** kapanan 45 karar kanonik kaynakta
   (`/root/otomaix-sosyal-medya-arastirmasi`, Bölüm 17 + Ek B) hâlâ açık görünüyor.
   Kaynak güncellenince snapshot yeniden alınır (kural snapshot başlığında).
   Codex oturumu: `codex resume 01a02e3f-9ff3-7ad3-b493-ac4cb070a8d3`.
2. **`/write-plan-claude-codex`** — plan SIFIRDAN (eski plan superseded). Girdi:
   yalnız yeni spec + snapshot. K-32…K-37 (pilot genişleme şartları) plan sırasında
   ayrıca gelecek.

## Verification (bu oturum)
- **Passed:** 45 kararın üç-yer kaydı (liste/spec/TASK) her kararda ayrı ayrı
  yapıldı · listede açık satır kalmadığı grep ile doğrulandı (`| |$` → 0 eşleşme) ·
  spec'te her kapanan K-ID'nin TÜM geçişleri grep'le bulunup güncellendi (kardeş-site
  sweep; K-38'in 13.3'teki dolaylı izi dahil) · K-26 vade-uyarısı sorusu spec'e karşı
  ölçüldü (uyarı mekanizması yoktu — kararla eklendi).
- **Passed (oturum sonu):** commit `8ce26f7` + push origin/main — 7 dosya; working
  tree temiz (git status ile doğrulandı).
- **Not run:** Codex kapanış-doğrulaması bu oturumda KOŞULMADI (spec'e ~45 noktada
  kapanış metni eklendi; review zinciri bunları henüz sınamadı) · sentez deposu
  sweep'i yapılmadı · canlı hiçbir şey çalıştırılmadı.
- **Kalan risk:** kapanış metinleri tek elden yazıldı — Codex doğrulama turu
  (`/review-claude-codex` veya plan öncesi hızlı kapanış-sweep'i) drift'i yakalar;
  iki-depo statü farkı (Resume 1) kapanana kadar snapshot bayat.

## Notes For Claude
- HANDOFF rolling; karar izi TASK Decisions Log'da (bu oturumun tam dökümü orada).
- **Karar sorma formatı kalıcı:** tek karar/soru + somut akış-senaryo düzeyinde
  mimari özet (hafıza: decision-review-one-by-one). Soyut kavram listesi YETMEZ —
  zaman damgalı/örnekli anlatım.
- K-56'yı Eray yeniden çerçeveledi: "eşik" kavramı reddedildi, olay-bazlı model
  kuruldu — plan yazarken alarm tasarımını eşiksiz kur.
- Liste dosyası işlevini bitirdi; task kapanışında arşive gider, silinmez.

## Notes For Codex
- Plan review'ında eski planın hiçbir hükmü referans alınmaz; kaynak yalnız yeni
  spec (spec-approved) + snapshot.
- Spec'teki ~45 kapanış eki tek elden yazıldı — plan öncesi kapanış-sweep
  doğrulaması değerli (occurrence tutarlılığı + K-ID çapraz atıfları).
