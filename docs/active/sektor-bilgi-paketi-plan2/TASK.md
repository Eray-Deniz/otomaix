---
title: Sektör Bilgi Paketi — Plan 2 (işletim hattı)
status: active
started: 2026-08-27
last-touched: 2026-08-27
blocked-by: null
source_plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
---

# Goal

Sektör bilgi paketini ÜRETEN ve AKTİVE EDEN işletim hattını kurmak: sözleşme düzeltmeleri →
`brief-doctor` → iki kör denetçi orkestrasyonu → sentez → politika motoru → onay yüzeyi →
komut ailesi → migration'lar → kuyumculuk pilotu. Plan 1 runtime çekirdeğini kurdu ve
main'de; Plan 2 onun "Plan 2'ye teslim edilen arayüzler" listesini tüketir.

Şu anki aşama: **planın kendisi henüz yazılmadı.** Hazırlık (boşluk taraması + karar turu)
tamamlandı.

# References

- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **kanonik**;
  spec damıtmadır, çelişkide girdi esastır
- Plan 1: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`, yürütüldü, arşiv
  `docs/task-archive/2026/08/sektor-bilgi-paketi/`)
- **Boşluk raporu:** `docs/research/2026-08-27-spec-input-bosluk-raporu.md` (`d16f228`)
- **Karar turu:** `docs/research/2026-08-27-plan2-karar-turu.md` (`a1bdc0c`, `cb7accf`)
- Codex ön-analizi: `~/.claude/logs/otomaix--ffc87809/2026-08-27-sektor-bilgi-paketi-plan2.md`
- Kanonik sözleşmeler (ayrı depo): `/root/otomaix-sosyal-medya-arastirmasi/` —
  `_SABLON.md` · `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`

# Current Status

**Plan yazıldı ve onaylandı** (2026-08-27):
`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` — 20 görev, `plan-approved`.
Codex adversarial review 6 turda kapandı (son tur: approve, contract-level bulgu yok);
tahkim kaydı `docs/reviews/codex/2026-08-27-sektor-bilgi-paketi-plan2.md`.
Sıradaki adım: yürütme (`/execute-plan-claude-codex`). Henüz KOD YAZILMADI.

- Eksik-aktarma taraması koşuldu: girdideki 162 karar kartından **32'si spec'e hiç
  geçmemiş**; ayrıca 3 düşen öneri ve 9 "teknik olarak çözülecekti, çözülmedi" kalemi.
- **13 Eray-seviyesi karar kapandı** (aşağıda Decisions Log).
- 6 karar sorulmadı çünkü cevabı kaynakta bağlı; 6'sı Plan 2'yi etkilemiyor (genişleme
  kapıları, pilot sonrası).
- Plan 2 **tek planda** yazılacak; ikinci bölme reddedildi.

# Decisions Log

- **2026-08-27 — K-84 = A:** kalıp kimliği sürümler arası korunur. Değeri eşleştirmek
  değil, sentez ajanının atladıklarını motorun yakalayabilmesi. Doğurduğu teknik kalemler
  K-151/K-152/K-86/K-154 planın işi.
- **2026-08-27 — K-23 = B:** motorun kararsız kaldığı madde güvenli varsayılana düşer
  (kalıp korunur) + rapora yazılır; aktivasyonu bloklamaz. Gerçek çelişkiler zaten sentezin
  açık soruları olarak gelip K-71 gereği bloklar. Önce A seçildi, üç kademeli yapı
  gösterilince B'ye çevrildi.
- **2026-08-27 — K-125 + K-100 = benimsendi:** denetçiler her turda aktif paketin her karar
  birimini de tarar (beş statü); motor `guncelle`/`cikar` için iki denetçi uyumu arar.
  Denetçi sözleşmesinin yeni sürümü gerekiyor.
- **2026-08-27 — K-133 = kurulmasın:** kuru mod ayrı koşu kipi olarak yazılmaz. Provenans
  ölçüldü: dokuz kaynak dosyanın hiçbirinde yok, tek hakemden geliyor. Çözdüğü temizlik
  sorunu K-106 (yerinde güncelleme) ile kapatılır. Yeniden açılma: motor ikinci sektöre
  yayıldığında.
- **2026-08-27 — K-130 · K-131 · K-132 = mekanizma kurulsun, eşik boş:** üç bariyerin kodu
  yazılır, değerleri pilot kalibrasyonunda konur. Ölçüldü: hiçbir kaynakta önerilmiş sayısal
  eşik YOK.
- **2026-08-27 — K-41 = eşik yok:** onay özeti "Çıkarılanlar: N" der, tam liste bir tık
  derinde. "Eşik üstü" boyutu hiçbir katmanda tanımlı değil.
- **2026-08-27 — K-42 = sıralama + aktivasyon süresi metriği:** özet riskli sınıfları nötr
  sayıların önüne koyar; onaya kaç saniyede basıldığı kaydedilir (R-21 tespit göstergesi).
  Geçmişe karşı anormallik tespiti dışarıda — geçmiş birikince.
- **2026-08-27 — K-134 = pilotta paralel, sonra tek geçiş:** pilot turlarında operatör önce
  sentez çıktısına bakıp yargısını kaydeder, sonra motorla karşılaştırılır — spec §15.2'nin
  istediği kalibrasyon verisi böyle doğar.
- **2026-08-27 — K-01a · K-146 · K-147 = üçü de eklensin:** 10 Kasım · 24 Kasım Öğretmenler
  Günü · okula dönüş. Sebep mekanik: sistem takviminde olmayan dönem pakete giremiyor.
  K-147 dönem taşıdığı için migration gerektiriyor.
- **2026-08-27 — Plan 2 tek planda yazılır.** Codex'in kademeli bölme önerisi reddedildi;
  ama kuralı korundu: sentez tek başına `draft` yazamaz, kanonik sıra sentez → motor → draft.
- **2026-08-27 — Komut ailesi: iş mantığı repoda CLI, `~/.claude/commands/` ince çağırıcı.**
  Kaynak sözleşmeler araştırma deposunda kalır; monorepo tarafında pin manifesti.

# Open Problems

- **Plan yazılırken 30 teknik kalem plan tarafından bağlanacak** (K-151 · K-152 · K-86 ·
  K-154 · K-100 · K-106 · K-17 · K-14 · K-24 mekanizması · K-74 · K-75 · K-76 · K-78 ·
  K-83 · K-87 · K-88 · K-89 · K-90…K-99 · K-103 · K-107 · K-108). Liste karar turu
  dosyasının sonunda.
- **§8.7'nin beş sözleşme düzeltmesi resmî turu BLOKLUYOR**; Codex altıncısını buldu
  (spec §12.2 kanal anahtar uzayının dört değerle kapatılması). Plan'ın ilk görevi.
- **Task 15'in elle arayüz doğrulaması** (`sector-package-assignment-ui-live-verification`,
  CURRENT.md) Plan 2 planının pilot görevinin kabul adımına YAZILACAK — evi burası.
- **n8n hata bildirimi hâlâ yok** (`n8n-credential-host-drift` (b)); Plan 2 n8n'e
  dokunuyorsa o turda kurulur.
- Plan 1 bölümlerinin kart geçişi taranmadı (boşluk raporu kapsam sınırı) — Plan 1 alanında
  kusur çıkarsa koşulur.
