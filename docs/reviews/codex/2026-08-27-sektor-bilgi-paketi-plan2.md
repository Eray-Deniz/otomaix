---
title: Plan 2 — Codex adversarial plan review (disposition ledger)
date: 2026-08-27
plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
turns: 7 (biri kanıtsız — aşağıda) + 2 bağımsız hakem turu
verdict: RİSK KABULÜYLE ONAY (Eray, 2026-08-27) — hakem zinciri onayı DEĞİL
plan_status: plan-approved / approved-by-iteration-limit
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


---

# DUR — otonom döngü durduruldu (2026-08-27, tur 7)

**Durum:** `plan-draft` + `pending`. Tur 6'daki `approve` GEÇERSİZ — bağımsız hakemin 10
itirazı onaydan sonra işlendi, tur 7 bunların **dördünü kapanmamış** buldu.

| itiraz | tur 7 |
|---|---|
| O1 kimlik modeli | **kapanmadı** — `kirp` semantiği, aynı metnin iki kez geçmesi, özel gün anahtarı ve ilk paket eşlenmiyor |
| O2 Katman-2 | **kapanmadı** — kolon ve üretici var; aktivasyon kapısı, komut ve pilot sırası bağlanmamış |
| O3 gerçek çalıştırıcı | **kapanmadı** — sınıf adlandırıldı; komut satırı ve hata→durum sahipliği tanımsız |
| O5 K-145 | **kapanmadı** — kanıt ölçütleri hâlâ ileriye dönük vaat; hedef sürüm ve tekrar güvenliği yok |
| O4 · O6 · O8 · O9 · O10 | kapandı |
| O7 | kapanmadı (orta) — davranış anlatılıyor, uygulayan görev yok |
| yeni (orta) | yerel tur arızası bildirimi üreticisiz · K-24 ölçüm zinciri kalıcı değil |

**Narrowing-vs-spawning yargısı: SAÇILIYOR.** Tur 3-6 tek eksende daralıyordu; tur 7 iki
YENİ eksende bulgu üretti (bildirim zinciri, K-24 kalıcılığı). Daralma bitti.

**Çerçeve teşhisi.** Kalan dört kalem artık *karar* değil *uygulama mekaniği*: birim
sayım sözleşmesi (konum/çokluk anahtarları), alt süreç komut satırı eşlemesi, olay geri
alma planlayıcısı (hedef sürüm sabitleme + tekrar güvenliği). Bunlar koşturulabilen bir
ortamda tek başarısız testle 20 dakikada kapanır; kâğıt üstünde beş turda kapanmaz.
Tekrarlanan kusur da bunu gösteriyor: **karar katmanını yazıp tüketicilerini bağlamamak** —
aynı hata O2/O3/O5/O7'de bir arada.

**Maliyet (ölçülü):** bu plan için 8 Codex çağrısı; biri kanıtsız (substrat dışlaması).

**Karar Eray'a gitti.**


---

# Kök tasarım turu (2026-08-27) — genel review DURDURULDU

**Kapsam kararı (Eray):** plan yeni bir genel review turuna sokulmadı. Yalnız iki kök
tasarım sorunu uçtan uca kapatıldı. **Dürüst etiket: durdurmak KAPANMAK DEĞİL** — son üç
bağımsız tur her seferinde yeni eksende bulgu çıkarmıştı; kalan risk ölçülmedi, **bilinçle
kabul edildi**. Bu, tur 6'daki hatanın (bir "dur" işaretini "onay" diye okumak) tekrarı
olmasın diye buraya yazılıyor.

## 1. K-145 tek ve kapalı sözleşme hâline getirildi

| Kalem | Kapanış |
|---|---|
| Olay girdisi kapalı dörtlü | `affected_packages(engine_version, engine_config_sha, kural_kimligi, kural_surumu)`; CLI `etki-analizi` aynı dörtlüyü ister · `test_etki_analizi_requires_full_quad` |
| Sınıflandırma yalnız yaşayan satırlara bakıyordu | **Kök kusur.** Küme artık *uygulanmış motor kararlarının TAMAMI*; `cikar` ve `kirp` dahil · `test_cikar_decision_makes_package_kanitli` · `test_kirp_decision_makes_package_kanitli` |
| İki "yaşayan" kümesinin karışması | Ayrı adlandırıldı: **karar birimi kümesi** (`cikar`/`kirp` düşürür) ≠ **uygulanmış motor kararı kümesi** (hepsi dahil); plan metnine uyarı kondu |
| Sürüm ayrımı | `test_same_rule_different_version_not_matched` |
| Uygulanan ↔ reddedilen kaynak ayrımı | Uygulanan → `final_decision_log` · reddedilen → `engine_diff` · `test_applied_motor_rows_carry_rule_stamp` |
| Hedef yalnız arşivlenmiş + güvenli | `test_target_is_highest_archived_version_without_faulty_stamp` · `test_clean_draft_is_never_chosen_as_target` |
| `hedefsiz` kalıcı temsil | Migration: `durum='hedefsiz'` + `target_version NULL` + **iki yönlü CHECK** · `test_hedefsiz_requires_null_target_version` · `test_non_hedefsiz_requires_target_version` |
| Planlayıcı hedefsiz satırı yazar | `test_no_safe_archived_version_yields_persisted_hedefsiz_row` |
| Yürütücü hatasız atlar | `test_executor_skips_hedefsiz_without_error` |
| Tekrar koşumda korunur | `test_rerun_preserves_hedefsiz_outcome` |
| CLI ayrı raporlar | `test_olay_geri_al_reports_hedefsiz_separately` |
| Task 13'teki artık testler | Task 8'e taşındı; Task 13'te sıfır kaldı |
| Doğrulayıcı damga testleri | `test_motor_row_without_rule_id_rejected` · `test_motor_row_without_rule_version_rejected` · `test_non_motor_row_carrying_rule_stamp_rejected` |

**Ölçülmüş düzeltme (hakemin ciddiyeti abartılıydı):** "temiz görünen taslak hedef seçilemez"
maddesi onaylanmamış içeriğin aktive edilebileceğini ima ediyordu. **Edilemez** —
`sector_package_lifecycle.py::rollback_package` hedefin durumunu okuyup `archived` değilse
hata veriyor. Gerçek kusur daha küçük: planlayıcı kısıtlamazsa **yürütmede ölecek** bir plan
satırı yazar. Plana bu ayrım doğru yazıldı; yanlış risk iddiası içeri alınmadı.

## 2. Task 12 / Task 13 sonuç sahipliği ayrıldı

- **Task 12 (`run_checks`) yalnız TİPLİ BULGU üretir**; hiçbir testi `blocked` beklemez.
  Sözleşme kapısı: `test_run_checks_never_returns_a_run_outcome`.
- **Task 13 (`decide`) bulguyu sonuca çevirir:** `test_kapsam_ihlali_finding_becomes_blocked` ·
  `test_mevzuat_uyusmazligi_always_becomes_blocked` (K-125 — bayraktan bağımsız) ·
  `test_mevzuat_dogrulanamadi_does_not_block_by_default` (K-128 pasif) ·
  `test_mevzuat_dogrulanamadi_blocks_when_flag_enabled` · `test_regression_gate_finding_prevents_activation_eligible` ·
  `test_second_active_finding_becomes_blocked`.
- Task 12'nin **invariant metni** de düzeltildi — testleri düzeltip gövdeyi bırakmak bu
  oturumun tekrarlayan kusuruydu; kardeş taraması onu yakaladı.

## Kardeş taraması (12 kavram + 1 ekleme)

`kural_kimligi` · `kural_surumu` · `affected_packages` · `AffectedSet` · `final_decision_log` ·
`engine_diff` · `hedefsiz` · `target_version` · `archived` · `run_checks` · `decide` ·
`blocked` — **artı** "yaşayan" (iki farklı kümeyi adlandırıyordu).
Yakaladığı iki kalıntı: Task 12 invariant metninde `run_checks`'in bloklaması (iki yerde).
Düzeltildi; taramanın son hâlinde kalıntı yok.


---

# ONAY — risk kabulüyle (2026-08-27, Eray kararı)

**Bu bir hakem zinciri onayı DEĞİLDİR.** Kayda geçen gerçek durum:

- Zincirin son yargısı `needs-attention`'dı (tur 7).
- Ondan sonra üç bağımsız hakem turu daha koşuldu (10 + 9 + 6 bulgu); hepsi ölçülerek
  doğrulandı ve düzeltildi.
- **Son iki düzeltme partisi (kök tasarım turu + K-145 evren düzeltmesi) hiçbir hakem
  tarafından İNCELENMEDİ.**
- Genel review turu Eray kararıyla durdurulmuştu; kalan risk **ölçülmedi**.

**Eray bu bilgiyle planı onayladı ve yürütmeye açtı (2026-08-27).**

Frontmatter bunu yansıtır:
`status: plan-approved` · `codex_plan_review_status: approved-by-iteration-limit`
(gerçek residual var — düz `approved` yanlış olurdu) ·
`unresolved_high_severity_override: true` (onay, temiz zincirle değil risk kabulüyle alındı) ·
`codex_plan_review_iterations: 7`.

## Kabul edilen riskler (açıkça)

1. **Son iki parti incelenmedi.** K-145'in kapalı sözleşmesi, `hedefsiz` kalıcı temsili,
   Task 12/13 sonuç sahipliği ayrımı ve evrenin aktif-paket üzerinden yeniden tanımı —
   hiçbiri bağımsız bir hakem görmedi.
2. **Yakınsama gözlenmedi.** Dört ardışık bağımsız tur da "gerçek düzeltme var ama eksik"
   dedi; her düzeltme yeni bir kalan boşluk doğurdu. Durma sebebi yakınsama değil, karar.
3. **Kalan alan uygulama mekaniğidir** (birim sayımı · komut satırı · geri alma
   planlayıcısı · kanıt sınıflandırması). Kusurlar yazım anında çıkacaktır.
4. **Hiçbir kod yazılmadı, hiçbir test koşulmadı.** Plandaki 300+ test adı henüz var olmayan
   dosyalara aittir; kırmızı-yeşil döngüsü yürütmede kurulacak.
5. Plan hiçbir açık ÜRÜN kararını kapatmıyor: K-85 · K-153 · K-128 · K-52 · K-11(a/b) ·
   K-32…K-37. Belirsiz vakalar açık soruya düşüp aktivasyonu blokluyor.

## Yürütmede ilk kapı

Task 2'nin altı sözleşme düzeltmesi resmî turu BLOKLAR; Task 18'in Step 0 kalite kapısı
(tam test · Katman-1 · pin · review + security zinciri) canlı dağıtımdan ÖNCE koşar.
