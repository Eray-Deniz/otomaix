---
title: Politika motoru — kontrol başına mutasyon ölçümü (Task 12 Step 5)
status: done
date: 2026-09-09
kaynak: Plan 2 Task 12 Step 5
yontem: Her kontrol `CHECKS` demetinden TEK TEK düşürüldü (pytest eklentisiyle,
  üretim dosyasına dokunmadan); K-112'nin iki dikişi ise dosya üzerinde mutasyona
  uğratılıp `git checkout` ile geri alındı. Her satırın yanında onu üreten komut
  ve TAZE çıktı var (İlke 9).
baglayicilik: YOK — bu not bir kapı DEĞİLDİR; test kapısının sahte olmadığının kanıtıdır.
---

# Motor kontrol kümesinin mutasyon ölçümü

**Soru:** `engine.CHECKS`'teki on üç kontrolün her biri GERÇEKTEN bir testin
kırmızısıyla korunuyor mu? Kırılmayan kontrol = test kapısı sahte (plan Task 12
Step 5).

## Yöntem

Kontroller üretim dosyası düzenlenmeden düşürüldü — mutasyon, `CHECKS` demetini
koşum anında filtreleyen bir pytest eklentisidir. Böylece ölçüm, ölçtüğü kodu
değiştirmez ve geri alma adımı hata payı taşımaz:

```python
# mutasyon_plugin.py (geçici; koşumdan sonra silindi)
import os
from app.services.sector_pipeline import engine

def pytest_configure(config):
    hedef = os.environ.get("MUTASYON_KONTROL", "")
    if hedef:
        engine.CHECKS = tuple(k for k in engine.CHECKS if k.ad != hedef)
```

```
cd apps/social/backend && source .venv/bin/activate
for ad in <on uc kontrol adi>; do
  MUTASYON_KONTROL=$ad python -m pytest tests/test_policy_engine_checks.py -q -p mutasyon_plugin
done
```

**Sayımdan DÜŞÜLEN iki test:** `test_checks_set_matches_the_binding_list` ve
`test_every_check_has_a_description` her mutasyonda düşer — kümenin KENDİSİNİ
pinlerler, tek tek kontrolleri değil. Onları saymak her kontrolü "korunuyor"
gösterirdi; aranan şey kontrolün DAVRANIŞINI ölçen testtir.

## Taze çıktı (2026-09-09) — on üç kontrol

| Kontrol düşürüldü | Kırmızıya dönen test(ler) |
|---|---|
| `sema_ve_boyut` | `test_malformed_candidate_fails_closed` · `test_size_is_measured_but_never_blocks` |
| `karar_kapsami` | `test_missing_unit_result_emits_kapsam_ihlali_finding` · `test_unknown_unit_id_emits_kapsam_ihlali_finding` |
| `kimlik_benzersizligi` | `test_duplicate_new_identity_emits_kapsam_ihlali_finding` · `test_yerine_gecer_must_point_to_an_active_unit` |
| `kanit` | `test_guncelle_without_evidence_is_recorded_as_unapplied` · `test_unreachable_url_does_not_count_as_evidence` |
| `mutabakat` | `test_guncelle_without_two_auditor_agreement_keeps_pattern` · `test_cikar_without_two_auditor_agreement_keeps_pattern` · `test_legislation_disagreement_emits_mevzuat_uyusmazligi_finding` · `test_number_claim_outside_the_field_list_is_legislation` · `test_unverified_legislation_emits_mevzuat_dogrulanamadi_finding` |
| `yeni_oge_cogunlugu` | `test_new_item_needs_two_of_three` · `test_single_source_exception_requires_official_and_live_url` · `test_yerel_degil_flag_closes_the_single_source_exception` |
| `bayrak_tuketimi` | `test_unconsumed_flag_becomes_an_open_question` |
| `geri_ekleme_celiskisi` | `test_readd_conflict_emits_acik_soru_finding` |
| `kategori_cakismasi` | `test_category_conflict_is_recorded_and_package_type_wins` · `test_matching_type_label_records_no_conflict` |
| `ozel_gun_anahtari` | `test_notes_pass_the_decision_log_schema` · `test_unmatched_holiday_key_emits_note` |
| `diff_sayilari` | `test_diff_counts_are_measured` (KeyError) · `test_diff_counts_follow_the_log` |
| `regresyon_kapisi` | `test_regression_gate_failure_emits_finding` |
| `tek_aktif_on_kontrolu` | `test_second_active_precheck_emits_finding` |

**Sonuç: on üçün ON ÜÇÜ korunuyor.** Kırılmayan kontrol YOK.

## K-112'nin iki dikişi — ayrı mutasyon

Bu ikisi `CHECKS` üyesi DEĞİLDİR (motor kontrolü değil, üretim ve yazım
yüzeyindeki davranış), o yüzden dosya üzerinde mutasyona uğratıldı ve
`git checkout -- <dosya>` ile geri alındı.

**(a) Üretim yolu — zorunlu maskeli log düşürüldü** (`app/routers/calendar.py`
içindeki `logger.warning(...)` çağrısı silindi):

```
python -m pytest tests/prompt_regression/test_special_day_calendar_unavailable.py -q
-> 2 failed, 1 passed
   FAILED ...::test_calendar_unavailable_yields_empty_special_day_context_and_logs
   FAILED ...::test_calendar_unavailable_log_is_masked
```

Üçüncü test (`test_empty_special_day_context_keeps_layer_one_byte_identical`)
mutasyonda da YEŞİL kaldı — doğrusu budur: o testin konusu logun varlığı değil,
bağlam boşaldığında Katman-1'in tek bayt değişmemesidir.

**(b) Yazım kapısı — tipli fail-closed düşürüldü** (`insert_draft`'taki
`try/except` kaldırılıp ham `db.fetch` geri kondu):

```
python -m pytest tests/test_package_lifecycle.py -q -k calendar
-> 2 failed, 1 passed
   FAILED ...::test_calendar_unavailable_fails_draft_write_closed
   FAILED ...::test_calendar_unavailable_error_keeps_the_original_cause
```

Pozitif kontrol (`test_calendar_available_still_writes_the_draft`) mutasyonda da
yeşil: kapı yalnız ERİŞİLEMEZLİKTE kapanıyor, normal yazımı engellemiyor.

## Kapsam sınırı — dürüst etiket

Ölçülen mutasyon türü **kontrolün tamamen düşürülmesidir** (plan: "kontrol
başına bir mutasyon"). Bir kontrolün İÇİNDEKİ yüklemin ters çevrilmesi ya da
sınır değerinin kaydırılması ÖLÇÜLMEDİ; yani "bu kontrol var mı" sorusu
kanıtlandı, "bu kontrolün her dalı test edilmiş mi" sorusu kanıtlanmadı.
Kontrol başına en az bir pozitif + bir negatif test kuralı o boşluğu daraltır
ama kapatmaz.

---

## Ek ölçüm — checkpoint 9 fix'lerinin kapıları (2026-09-09)

Bağımsız hakem turu beş yüksek bulgu üretti; beşi de kontrolörün KENDİ probuyla
doğrulandı (ölçümler aşağıda), düzeltildi ve her düzeltmenin kapısı ayrıca
mutasyona uğratıldı. Mutasyon, düzeltilmiş dosyanın kopyası üzerinden yapıldı ve
her turda geri yüklendi.

**Düzeltmeden ÖNCE ölçülen davranış (kontrolörün kendi probu, hakemin iddiası
olduğu gibi kabul edilmedi):**

```
F1 bayat çift kabul edildi -> b51aeebfff3d9edc vs 24c2a5bf6aa33eda
F2 uydurma KAYNAK-99 ile sebepler: []            (boş = fail-open)
F4 katman1_passed='false' ile bulgular: []       (boş = fail-open)
F5 doğrulanmış referans kümesi: ['KAYNAK-1', 'https://resmi.example/mevzuat-2026']
   -> denetçi SATIRI kolu hiç çözülemiyordu
```

**Fix kapılarının mutasyon ölçümü:**

| Mutasyon | Kırmızıya dönen test(ler) |
|---|---|
| F1 görüntü bağı kaldırıldı | `test_stale_audit_pair_is_rejected` |
| F2 kabul edilen kaynak süzgeci kaldırıldı | `test_invented_source_label_does_not_count` · `test_eliminated_source_does_not_count` |
| F3 tek-kaynak istisnası geri kondu | `test_single_source_exception_is_closed_until_officiality_is_typed` |
| F4 bool kapısı kaldırıldı | `test_gate_results_reject_non_bool_values` (beş parametre) |
| F4 `RoundGate` kimlik kapısı kaldırıldı | `test_engine_inputs_rejects_lookalike_round_gate` |
| F5 denetçi satırı kanıtı kaldırıldı | `test_auditor_row_reference_counts_as_evidence` |

Altı mutasyonun altısı hedeflediği testi kırdı; sahte kapı YOK.

**Kabul edilmiş riskler (orta — düzeltilmedi, dürüst etiket):** K-129 rakam kolu
sıradan sayısal metni de mevzuat sayar (yön fail-closed); alt-dize eşlemesi Türkçe
eklemeli olduğu için bilinçlidir (kelime-sınırı ankoru "ayarı/ayarında"yı kaçırır).

### Kapanış turu (round 2) — çoğunluk kapısının SINIF kapanışı

Kapanış-doğrulama turu F1/F3/F4/F5'i kapalı buldu; F2'yi AÇIK bıraktı ve yeni bir
yüksek bulgu (F8) ekledi. İkisi de aynı ekseni gösteriyordu: *serbest metinden yapı
çıkarma* ve *ad uzayı karıştırma*. Varyant yamamak yerine eksen tek kanonik
ayrıştırıcıyla kapatıldı (`engine.sayilan_kaynaklar`) ve kapanış ELLE SEÇİLMİŞ
örnekle değil ÜRETİLMİŞ matrisle kanıtlandı.

| Mutasyon | Kırmızıya dönen test(ler) |
|---|---|
| tam-parça kuralı alt-dizeye çevrildi | matrisin dört sarmalayıcı kolu (`önünde-düzyazı` · `arkasında-düzyazı` · `olumsuz-cümle` · `ayraç-içinde`) + `test_negated_prose_does_not_pass_the_majority_gate` |
| kör etiket konumdan değil addan türetildi | `test_eliminated_source_does_not_count` |

Matrisin boş-küme kontrol kolu ayrıca ölçülür (`test_source_parser_empty_arm_is_measured`):
boş metin, boş etiket kümesi ve `None` hiçbir kaynak saymaz.

**Kapanmayan ayak — dürüst etiket:** `EngineInputs` paket/koşu bağı taşımaz (R5 alan
kümesi kapalı), yani başka bir koşunun mekanik kapısı bu koşuya verilirse motor bunu
göremez. F1'in görüntü bağına denk gelen bağ burada YOKTUR; kurulması arayüz eki
revizyonu ister ve bu katmanda kapatılamaz. Açık borç olarak TASK.md'ye yazıldı.

### Üçüncü tur — eksen kapalı dilbilgisiyle kapatıldı

Üçüncü kapanış turu F8'i kapalı buldu; F2 aynı eksende ÜÇÜNCÜ varyantı üretti:
bileşen bazlı süzme, bir bileşendeki olumsuz düzyazının KOMŞU bileşenlerdeki
çıplak etiketleri kurtarmasına izin veriyordu (hakemin taze probu: *"Bu kaynaklar
iddiayı desteklemiyor: KAYNAK-1, KAYNAK-2, KAYNAK-3"* iki kaynak sayıyordu).

Üç varyant tek eksendir — *serbest düzyazıdan yapı çıkarma*. Dördüncü bir yama
yerine alan BÜTÜN olarak kapalı bir dilbilgisine bağlandı: virgülle ayrılmış her
bileşen ya geçerli kör etiket, ya URL, ya denetçi satır atfıdır; dilbilgisi dışı
tek bileşen alanın tamamını düşürür. Olumsuzlama ARANMAZ — düzyazı zaten
dilbilgisi dışıdır, ne dediğine bakılmaz.

Matris artık düzyazının KONUMUNU (baş · orta · son) × düzyazı biçimini ×
etiket sayısını (iki · üç) çarpım olarak ÜRETİR; önceki matris tek etiketi
sarmaladığı için bu sınıfı görmüyordu.

| Mutasyon | Kırmızıya dönen test(ler) |
|---|---|
| alan-bütün kuralı kaldırıldı (bileşen bazlı süzmeye dönüş) | matrisin **yirmi** negatif kolu (üç konum × üç düzyazı × iki etiket-sayısı + iki yapışık kol) |

**Kabul edilen bedel (dürüst etiket):** meşru ama karışık yazılmış bir kanıt alanı
(etiketlerin yanına serbest not düşülmüş) da reddedilir. Yön bilinçlidir: reddedilen
karar uygulanmaz, kalıp korunur. Kalıcı çözüm serbest metni tipli bir destek alanına
çevirmektir — arayüz eki revizyonu, açık borç.

### Dördüncü tur — URL kolunun sıkı doğrulanması (zincirin son turu)

Dördüncü kapanış turu F2'yi yine açık buldu: kapalı dilbilgisinin URL kolu
gevşekti (*"`://` içerir ve ASCII boşluk yok"*), yani düzyazıyı GERİ ALIYORDU.
Hakemin probu ölçüldü ve kontrolörün kendi probuyla doğrulandı:

```
"KAYNAK-1, KAYNAK-2, https://ornek.example\nDESTEKLEMIYOR" -> ['KAYNAK-1','KAYNAK-2']
"KAYNAK-1, KAYNAK-2, javascript://x"                        -> ['KAYNAK-1','KAYNAK-2']
"KAYNAK-1, , KAYNAK-2"                                      -> ['KAYNAK-1','KAYNAK-2']
```

URL kolu artık biçimin TAMAMINI arar (şema + boş olmayan konak + boşluksuz kalan)
ve boş bileşen alanı düşürür. Aynı problar düzeltmeden sonra boş küme döndü.

| Mutasyon | Kırmızıya dönen test(ler) |
|---|---|
| URL kolu `"://" in parca`'ya geri çevrildi | `test_malformed_url_component_drops_the_whole_field` üç kolu (geçersiz-şema · şema-yok · konak-yok) |
| boş bileşen sessizce düşürüldü | `test_empty_component_drops_the_whole_field` dört kolu |
| **boşluk kontrolü söküldü** | **HİÇBİRİ** — aşağıya bakınız |

**Dürüst etiket:** boşluk kontrolü bugün TEK BAŞINA erişilebilir bir dal DEĞİLDİR
(mutasyon hiçbir testi kırmadı); URL biçimi zaten boşluk taşıyamaz, etiket ve satır
atfı biçimleri de boşluksuzdur. Kodda durmasının sebebi savunma derinliğidir ve bu,
"kendi testi var" diye okunmaz. Emsal: `auditors.check_snapshot_agreement`'in
dördüncü koşulu aynı biçimde etiketlidir.

**Zincir burada DURDU (kullanıcı kararı, 2026-09-09):** beşinci hakem turu
AÇILMADI. Yani bu turun kapanışı kontrolörün ölçümüne dayanır, bağımsız hakem
doğrulamasına değil — kapanış doğrulaması sonraki kapanış turlarına kalmıştır.
Kalan kök sorun (kanıtın düz yazı olması) kod tarafında değil veri akışında:
denetçinin denetim tablosu tipli okunmuyor. Adlandırılmış evi aktif katmanda
açıldı.
