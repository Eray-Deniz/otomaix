---
title: Plan 2 — Codex adversarial plan review (disposition ledger)
date: 2026-08-27
plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
turns: 6 (biri kanıtsız — aşağıda)
verdict: approve (tur 6)
ham_kanit: /root/.claude/logs/otomaix--ffc87809/2026-08-27-sektor-bilgi-paketi-plan2-plan.md
  (bu makinede, bu kökten — MUTLAK yol; ham Codex çıktısı byte-exact orada)
---

# Plan 2 — Codex adversarial plan review: disposition ledger

Bu dosya **özet ve tahkim kaydıdır**; ham Codex çıktısı yukarıdaki log dosyasındadır
(shell-append, model tarafından yeniden yazılmamıştır).

## Tur özeti

| Tur | Sonuç | Bulgu |
|---|---|---|
| 1 | needs-attention | 14 high (13 contract-level + 1 mechanics) + 2 medium |
| 2 | **kanıtsız — review ÜRETİLMEDİ** | Substrat sır tarayıcısı plan dosyasını dışladı; hakem planı hiç görmedi ve bunu "kanıt yetersiz, onay değil" diye raporladı. Sebep: plana yazılan taze ölçümün komutu bir kimlik başlığı adı içeriyordu. Metin düzeltildi, tur tekrar koşuldu. |
| 2 (tekrar) | needs-attention | 15/17 kapandı; F7 · F10 kapanmadı; F18 · F19 · F20 yeni |
| 3 | needs-attention | F7 · F10 · F20 kapandı; F18 · F19 kısmi; K-99 üretici + NEW-1 yeni |
| 4 | needs-attention | F18 · F19 · K-99 kapandı; NEW-1 kapanmadı (kardinalite) |
| 5 | needs-attention | NEW-1 + kapı-girdisi sınıfı kapandı; NEW-2 · NEW-3 yeni |
| 6 | **approve** | NEW-2 · NEW-3 kapandı; contract-level bulgu YOK; 30/30 teknik kalem bağlı |

## Disposition ledger

Tüm bulgular `claude-confirmed` → Auto-Fix Policy gereği otonom Mode A1 refine döngüsü.
**Reddedilen bulgu YOK.** Üç bulgu kabul edilmeden ÖNCE bağımsız ölçüldü (aşağıda).

| id | severity | konu | disposition |
|---|---|---|---|
| F1 | high | Pilot kendi şemasından/kodundan önce koşuyordu | fixed — Task 18 (dağıtım) eklendi, pilot 19'a, kapanış 20'ye kaydı |
| F2 | high | K-94 ilk aktivasyonu ifade edemiyordu | fixed — `expected_no_active` |
| F3 | high | K-99 kapalı olay kümesine çarpıyordu | fixed — 036 CHECK + 033 pin sürüm-farkında |
| F4 | high | K-128 hem pasif hem koşulsuz | fixed — K-125 / K-128 yolları ayrıldı |
| F5 | high | Köken ispatı yalnız tip düzeyinde | fixed — kanıt DB'den, işlem içinde |
| F6 | high | K-106 kapı atlatabiliyordu | fixed — public `update_draft` kaldırıldı |
| F7 | high | Kaldırılan `attempt` uzayı Task 8'de yaşıyordu | fixed (tur 3) |
| F8 | high | K-09 indeksi 032'nin donmuş manifestini düşürüyordu | fixed — sürüm-farkında beklenti |
| F9 | high | K-100 `gerekce` alanını ve tamlık kapısını kaybetmiş | fixed |
| F10 | high | K-107 not satırına bağlanmıştı | fixed (tur 3) |
| F11 | high | K-85/K-153 gereksiz ilan edilmişti | fixed — iddia GERİ ALINDI, kararlar açık bırakıldı |
| F12 | high | K-134 kalibrasyon körlüğü bozuluyordu | fixed |
| F13 | high | K-45 üreticisiz ve müşteri yüzeysiz | fixed |
| F14 | high | 035 geri alması dönem satırını bozuyordu | fixed |
| F15 | high (mechanics) | K-103 ölçümü yanlış "yetki yok" verebilirdi | fixed — mechanics etiketli olmasına rağmen alındı (yanlış ölçüm iddiası üretirdi) |
| F16 | medium | Dağıtım listesi dış artefaktları kurmuyordu | fixed (accepted_risk yapılmadı) |
| F17 | medium | Test komutları çalışma dizini kurmuyordu | fixed |
| F18 | high | Onay çağırandan alınıyordu, kapı kanıtı yoktu | fixed (tur 4) — tek doğrulayıcı + basılan snapshot |
| F19 | high | Güncelleme yolu eski kapı listesinde kalmıştı | fixed (tur 4) |
| F20 | high | 036 geri alması pilot verisiyle güvensizdi | fixed (tur 3) |
| K-99 | high | Python olay üreticisi genişletilmemişti | fixed (tur 4) |
| NEW-1 | high | Benzersizlik kısıtı K-106'yı imkânsız kılıyordu | fixed (tur 5) — kardinalite + düzeltme soyağacı |
| NEW-2 | high | Yarıda kalan düzeltme kurtarılamıyordu | fixed (tur 6) — dışlama kaldırıldı, devralma |
| NEW-3 | high | Paralel düzeltme onaylanmamış içeriği aktive edebilirdi | fixed (tur 6) — tek açık düzeltme + aktivasyonda içerik hash bağı |

## Kabul edilmeden önce bağımsız ölçülen üç bulgu (çıkarım körlemesine kabul edilmedi)

1. **K-99 olay kümesi** — `033_package_events.sql` `package_events_type_check` dokuz değer
   sayıyor ve 033 kendi doğrulama bloğunda CHECK metnini **birebir pinliyor** (satır 115, 184).
   `package_events.py` tarafında `LIFECYCLE_EVENTS = frozenset({"activation","rollback","deactivation"})`.
   → Hakemin dediğinden **ağır** çıktı: hem DB hem Python üreticisi genişlemek zorunda.
2. **K-09 indeksi** — `032_sector_packages.sql` satır 419-420 `sector_research_artifacts`
   indeks kümesini *"kapalı"* diye tam metinle pinliyor. Satır 421-422 aynı şeyi
   `sector_packages` **kısıt kümesi** için yapıyor → NEW-1'in bağının neden 036 tarafında
   kurulduğunu bu ölçüm belirledi.
3. **K-100 envanteri** — kanonik spec-input satır 1031: *"Her satır karar birimi anahtarı,
   denetçi statüsü, kanıt referansı ve **tek cümle gerekçe** taşır."* Plan `gerekce`'yi
   düşürmüştü. Spec bu ayrıntıyı taşımıyor; **girdi kanoniktir**.

## Execute'a devredilen (EXECUTE-NOTES — İlke 7 adlandırılmış ev)

1. Canonical JSON normalizasyonu anahtarlar VE string değerler üzerinde özyinelemeli olmalı.
2. Onay anlık görüntüsü değişmezliği OLD/NEW karşılaştırmalı olmalı; ilgisiz karar kolonları
   güncellenebilir kalmalı.
3. Adaptör argümanları kabuk yorumu olmadan aktarılmalı; veritabanı adresi çıktıya/istisnaya
   sızmamalı.
4. `unit_id` üretimi çakışma yeniden denemesi taşımalı; benzersizlik tüm aday üzerinde
   doğrulanmalı.
5. Küresel kilit sırası: koşu → (varsa) ana koşu → sektör → paket. Bu kilitler CLI alt
   süreçleri, sunum veya operatör beklemesi boyunca TUTULMAZ.

## Sayaç ve statü notu (P4)

`codex_plan_review_iterations: 5` — limit (3) aşıldı. **Final tur temiz** (approve,
unresolved NONE) olduğu için P4 kuralı gereği statü `approved` yazıldı;
`approved-by-iteration-limit` YALNIZ gerçek medium/low residual kalsaydı kullanılırdı.
`unresolved_high_severity_override: false` — hiçbir bulgu risk kabulüyle geçilmedi.

## Plan'ın KAPATMADIĞI açık ürün kararları (Eray'a ait)

K-85 (kalıp semantik eşleştirme ölçütü) · K-153 (yöntem: deterministik mi hakemli mi) ·
K-128 (doğrulanamayan mevzuat bloklaması) · K-52 (DNA verisi motora girsin mi) ·
K-11(a/b) · K-32…K-37 (genişleme kapıları).
Plan bunların hiçbirini kapatmaz; belirsiz vakalar açık soruya düşer ve K-71 gereği
aktivasyonu bloklar.
