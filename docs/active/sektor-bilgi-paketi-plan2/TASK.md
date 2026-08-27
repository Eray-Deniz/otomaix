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

Şu anki aşama: **plan ONAYLI, yürütme bekliyor.** Onay hakem zinciriyle değil **Eray'ın risk
kabulüyle** alındı (2026-08-27); son iki düzeltme partisi incelenmedi.

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

**Plan ONAYLANDI — risk kabulüyle** (Eray, 2026-08-27):
`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` — 20 görev,
**`plan-approved` + `approved-by-iteration-limit`**, `unresolved_high_severity_override: true`,
7 zincir turu + 4 bağımsız hakem turu.

Dört bağımsız hakem turu koşuldu (10 + 9 + 6 + 3 bulgu); hepsi ölçülerek doğrulandı ve
düzeltildi. **Son iki düzeltme partisi incelenmedi** ve zincirin son yargısı `needs-attention`'dı.
Eray bu bilgiyle onayladı. Kabul edilen riskler hakem kaydında tek tek yazılı.

Tahkim kaydı: `docs/reviews/codex/2026-08-27-sektor-bilgi-paketi-plan2.md`.
Sıradaki adım: **yürütme** (`/execute-plan-claude-codex`). Henüz KOD YAZILMADI.

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

- **2026-08-27 — Genel review turu DURDURULDU.** Plan yeni bir kapsamlı hakem turuna
  sokulmuyor; yalnız iki kök tasarım sorunu (K-145 sözleşmesi · Task 12/13 sonuç sahipliği)
  uçtan uca kapatıldı. **Kalan risk ölçülmedi, bilinçle kabul edildi** — durdurmak kapanmak
  değildir.
- **2026-08-27 — Plan RİSK KABULÜYLE ONAYLANDI (Eray).** Son iki düzeltme partisi hiçbir
  hakem görmedi; zincirin son yargısı `needs-attention`'dı. Onay bu bilgiyle verildi.
  Frontmatter bunu yansıtır: `approved-by-iteration-limit` + `unresolved_high_severity_override: true`.

# Open Problems

- **30 teknik kalem BAĞLANDI** (plan yazımında); bağlanma yerleri ve kanıtlayan test adları
  planın kendisinde. Kapanış görevi (Task 20) 30 teknik + 13 ürün kararını tek tek sweep eder.
- **§8.7'nin sözleşme düzeltmeleri planın ilk görevidir** (altı kalem: beşi spec'ten, altıncısı
  kanal anahtar uzayının kapatılması). Resmî turu hâlâ bloklarlar — plan onları Task 2'de kapatır.
- **Task 15'in elle arayüz doğrulaması EV BULDU:** planın pilot görevinde, ilk paket aktive
  edildikten sonraki kabul adımı. Plan onaylandı (2026-08-27) ama **tarih hâlâ YOK** —
  yürütme başlamadı, pilot koşulmadı. Dürüst etiket: *çözülmedi; evi var, tarihi pilot
  görevinin koşmasına bağlı.*
- **n8n hata bildirimi planda:** hem workflow tarafı hem yerel tur arızası bildirimi bağlandı;
  kapsam bilinçle dar (yalnız sektör paketi zinciri), kalan workflow'lar CRM turunda.
- **KABUL EDİLMİŞ RİSK — onay temiz zincirle alınmadı.** Ardışık bağımsız turlar her
  seferinde kalan teknik boşluk buldu; yakınsama gözlenmedi, durma sebebi karardı.
  Son iki parti incelenmedi. **Kalan kusurlar yazım anında çıkacak** — yürütmede
  kırmızı-yeşil döngüsü bunları yakalamalı. Tekrarlayan kusur sınıfı: bir invariantı yazıp
  onu TÜKETEN görevleri güncellememek; yürütmede de aynı disiplin gerekir.
- Plan 1 bölümlerinin kart geçişi taranmadı (boşluk raporu kapsam sınırı) — Plan 1 alanında
  kusur çıkarsa koşulur.
