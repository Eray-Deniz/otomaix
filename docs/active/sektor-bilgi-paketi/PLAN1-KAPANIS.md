# Plan 1 Kapanış — Kabul Eşlemesi + Plan 2 Arayüz Teslimi

> **Ne olduğu:** Plan 1'in (`docs/plans/2026-08-23-sektor-bilgi-paketi.md`) kapanış
> raporu. Spec'in kabul kriterlerini onları KANITLAYAN test adlarına eşler, kapsam
> dışında kalanları adlandırır, kabul edilen riskleri açıkça yazar.
>
> **Ne olmadığı:** "sistem doğrulandı" beyanı DEĞİLDİR. Aşağıdaki her satır bir
> otomatik testin kapsadığı kadarını iddia eder. Arayüz yüzeyleri ve canlı ortam
> adımları bu kapanışta DOĞRULANMAMIŞTIR — nedeni ve evi "Ertelenen doğrulamalar"
> bölümündedir.

- **Plan:** `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- **Spec:** `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- **Dal:** `feat/sektor-bilgi-paketi`
- **Tarih:** 2026-08-25

---

## 0. Ölçüm — bu raporun dayandığı taze koşumlar

Her satır, YANINDAKİ komutun taze koşumundan gelir. Komutlar depo kökünden birebir
kopyalanıp çalıştırılabilir; sır (bağlantı dizesi) belgeye GİRMEZ, ayarlardan okunur.

| İddia | Komut (birebir koşulabilir) | Çıktı |
|---|---|---|
| Tüm arka uç testleri geçiyor | `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` | `577 passed` |
| Katman-1 byte-exact kapısı yeşil | `cd apps/social/backend && .venv/bin/python -m pytest tests/prompt_regression/ -q` | `121 passed` |
| Marka → kök sektör sweep'i temiz | aşağıdaki iki adım | `differences: 0` (rc=0), hedef doğrulandı |

**Sweep — hedefe BAĞLI ve çıkış kodunu KORUYAN komut.** İki ayrı arıza yolu var ve
komut ikisini de kapatmak zorunda: (1) çıplak koşum "canlıya bakıldı"ı kanıtlamaz —
bağlantı dizesi ayarlardan gelir, yanlış yapılandırılmış temiz bir veritabanı da `rc=0`
döner; (2) çıktıyı boruya verip hedefi `grep`'le aramak sweep'in KENDİ çıkış kodunu
yutar — ihlal bulan bir sweep (`differences: 1`, rc=1) doğru hedefi bastığı için
"temiz" görünür. İkincisi ölçüldü: eski boru hattı biçimi bu senaryoda `rc=0` veriyordu.

```
cd apps/social/backend && out=$(.venv/bin/python -c "
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
from app.core.config import settings
import sector_sweep
raise SystemExit(sector_sweep.main(['--database-url', settings.DATABASE_URL, '--dry-run']))") ; rc=$?
printf '%s\n' "$out"
[ "$rc" -eq 0 ] && printf '%s\n' "$out" | grep -qFx "target: 7626046209338777641/16384/otomaix@127.0.0.1:5433/otomaix~10.0.1.9:5432"
```

Üç çıkış-kodu kontrolü ÖLÇÜLDÜ:

| Senaryo | Beklenen | Ölçülen |
|---|---|---|
| temiz + doğru hedef | `rc=0` | `rc=0` |
| ihlal (`differences: 1`) + doğru hedef | `rc≠0` | `rc=1` |
| temiz + yanlış hedef | `rc≠0` | `rc=1` |

İhlal senaryosu, doğru hedefi basıp 1 ile çıkan bir vekil üreticiyle kurgulandı: canlı
veritabanında ihlal YOK (`differences: 0`) ve oraya kasten ihlal yazılmadı. Yani ölçülen
şey komutun BİÇİMİDİR, canlı verinin bozulması değil — dürüst sınır.

Ölçülen hedef: `7626046209338777641/16384/otomaix@127.0.0.1:5433/otomaix~10.0.1.9:5432`.
Sunucu adresi değişirse (kap yeniden başlar, yeni IP alır) komut BAŞARISIZ olur — bu
fail-closed yöndür, taban yeniden alınır.

Sweep CANLI veritabanına karşı koşuldu (salt-okunur transaction). Test koşumları
`otomaix_test` üstünde.

---

## 1. Spec §14.1 — deterministik çekirdek (dört uçtan uca kriter + ekler)

| # | Kriter | Kanıtlayan test |
|---|---|---|
| 1 | Ham artefakt `UPDATE`/`DELETE` → istisna | `test_artifacts_append_only_update_raises` · `test_artifacts_append_only_delete_raises` |
| 2 | `INSERT` başarılı, `run_id` altında sorgulanabilir | `test_artifacts_insert_and_query_by_run_id` |
| 3 | İkinci `active` → indeks hatası | `test_packages_single_active_partial_index` · `test_migration_raises_when_single_active_index_is_not_unique` · `test_migration_raises_when_single_active_index_is_invalid` |
| 4 | Yazım-öncesi şema + boyut doğrulaması | `test_validator_accepts_reference_content` · `test_validator_rejects_unknown_field` · `test_validator_rejects_missing_field` · `test_validator_size_warning_not_rejection` (boyut UYARI'dır, kapı değil — İlke 9) · `test_insert_draft_requires_valid_content` |
| E1 | `(sector_id, version)` ihlali hata verir | `test_packages_version_unique` · `test_migration_raises_when_sector_version_unique_is_missing` |
| E2 | `sub_sector_id` NULL kalabilir; kök REDDEDİLİR | `test_sub_sector_id_accepts_child_and_null` · `test_sub_sector_id_rejects_root_sector` · `test_package_sector_id_rejects_root` |
| E3 | Geri doldurma yok (mevcut satırlar dokunulmaz) | `test_sectors_list_unchanged_after_sub_sector_insert` · `test_brand_sector_mappings_full_sweep_unchanged` |
| E4 | Migration geri alınabilir; sıra doğru | `test_rollback_clean_path_full_teardown` · `test_rollback_refuses_when_package_data_exists` · `test_rollback_refuses_data_committed_while_it_waits` · `test_runner_glob_covers_canonical_dir_in_order` · `test_runner_stops_on_sql_error` |
| E5 | Marka kök-sektör TAM sweep'i (spot yetmez) | `test_sector_sweep_readonly_and_deterministic` · `test_sweep_baseline_detects_root_to_root_remap` · `test_sweep_rejects_baseline_from_another_target` · `test_sweep_target_distinguishes_physical_clone` (+ yukarıdaki canlı koşum) |

**Kapsam notu (E4):** geri alma script'i YALNIZ 032 için var. 033 ve 034'ün geri alma
script'i YOKTUR — plan istemedi, uydurulmadı. Bkz. "Kabul edilen riskler".

---

## 2. Spec §14.2 — test katmanları (Plan 1 kapsamındakiler)

### Katman-1 (byte-exact prompt kapısı)

| Sözleşme | Kanıtlayan test |
|---|---|
| Yüzey kümesi ölçümle kapalı; tek bayt = RED | `test_caption_single_no_special_day_matches_fixture` · `test_caption_single_special_day_matches_fixture` · `test_caption_carousel_matches_fixture` · `test_ideas_surface_matches_fixture` · `test_script_request_matches_fixture` · `test_still_prompt_*_matches_fixture` (4 mod) · `test_legacy_short_video_*` · `test_motion_pool_bytes_pinned` |
| Re-runnable (dondurma kazara yeşil üretemez) | `test_update_flag_must_be_unset_for_verification` |
| Yakalama sözleşmesi (blok biçimi kapalı küme) | `tests/prompt_regression/test_capture_contract.py` (9 test) |
| Paketsiz marka bayt-değişmez kalır | `test_unpackaged_fixtures_still_byte_exact` · `test_unpackaged_still_untouched_in_every_branch` · `test_unpackaged_path_returns_no_package_motion` |

### Veri/API regresyonu (spec §5.3 üçlüsü)

`test_sectors_list_unchanged_after_sub_sector_insert` · `test_brand_sector_mappings_full_sweep_unchanged` ·
`test_package_stamp_pair_is_never_half_written` · `tests/test_taxonomy_guards.py` (5 test: çözümleyici alt
sektör satırlarını görmez, uç noktası alt sektörleri listelemez, trend taraması kök-only).

### İş kuralı senaryoları

| Senaryo | Kanıtlayan test |
|---|---|
| Yerine-geçme (paket kök rehberin YERİNE geçer) | `test_packaged_caption_replaces_sector_guidance` · `test_packaged_idea_prompt_replaces_guidance` |
| Yan-yana yasağı — BASIM anı | yukarıdaki ikisi + `test_usage_instruction_prefixes_package_block` |
| Yan-yana yasağı — AKTİVASYON GEÇİŞ anı (spec §14.2 bunu ayrıca ister) | `test_activate_archives_previous_then_activates` · `test_two_step_activation_in_single_transaction_succeeds` · `test_wrong_order_activation_rejected_by_partial_index` |
| Draft paket → mevcut yol sınırı (yalnız `active` okunur) | `test_resolver_none_for_non_active_with_stale_log` · `test_candidates_live_query_reflects_deactivation` |
| Özel gün eşleşme / eşleşmezlik + log | `test_special_day_match_injects_period_block` · `test_special_day_mismatch_silent_fallthrough_with_log` · `test_special_day_mismatch_records_the_event` · `test_malformed_special_day_falls_through_silently` |
| `anma` kısıtı (K-119: yasak kullanıcı isteğini de ezer) | `test_anma_sales_ban_overrides_user_request` |
| Aday liste kapalılığı (boş liste → boş dönüş) | `test_empty_candidate_set_returns_empty_list` · `test_analyze_website_suggestion_empty_when_no_candidates` · `test_website_less_suggestion_empty_when_no_candidates` |
| Öneri kapalı listeden çıkar | `test_analyze_website_suggestion_must_be_in_candidates` · `test_analyze_website_prompt_embeds_closed_candidate_list` · `test_website_less_suggestion_uses_same_closed_list` |
| Sürtünmesizlik (üretim yolu aday sorgusu YAPMAZ) | `test_generation_path_never_queries_candidates` |
| K-04 talimat varlığı | `test_usage_instruction_prefixes_package_block` |
| K-05 etiket korunumu + kanal filtresi (§12.2) | `test_packaged_caption_cta_respects_channel_filter` · `test_special_day_cta_respects_channel_filter` · `test_non_ascii_bracket_tag_is_filtered_but_not_stripped` · `tests/test_channel_inventory.py` (43 test) |
| Sürüm ilişkisi var/yok (K-07 damgası) | `test_persist_writes_recorded_stamp_verbatim` · `test_unpackaged_post_stamp_null` · `test_stamp_half_null_rejected` · `test_stamp_mismatched_version_rejected` |
| Tek-aktif | `test_packages_single_active_partial_index` · `test_concurrent_activation_of_same_draft_single_winner` · `test_concurrent_activation_of_different_drafts_is_serializable` |

### Yaşam döngüsü + kapı kanıtı (Task 13)

`test_activate_rejects_unsatisfied_gate` (K-71 açık-soru sayısı + K-28'in Plan-1 ayağı; kanıt
alanlarının her biri ayrı ayrı parametrelenir) · `test_raw_transition_not_publicly_exported` ·
`test_rollback_rejects_activation_evidence` · `test_activate_rejects_lookalike_evidence` ·
`test_rollback_rejects_lookalike_evidence` · `test_activation_rejects_sector_reassignment_under_lock` ·
`test_deactivation_rejects_sector_reassignment_under_lock` · `test_event_insert_failure_rolls_back_transition`.

> **Eşleme sapması (dürüst kayıt):** plan Task 16 Step 3, K-71 mekanik red kapısı için
> `test_activate_rejects_open_questions` adını veriyor. Depoda BU ADLA bir test YOKTUR;
> kapıyı kanıtlayan test `test_activate_rejects_unsatisfied_gate`'tir ve açık-soru sayısını
> parametre olarak kapsar (docstring K-71'i adıyla anar). Ad sapmasıdır, kapsam boşluğu
> değil — ama plan metni bu haliyle bayattır.

### Bildirim (Task 14 — K-56 olay-bazlı + K-45 devre-dışı ayağı)

`test_admin_event_committed_with_business_transaction` · `test_admin_event_every_occurrence_no_threshold`
(eşik YOK — her olay tek başına uyarı) · `test_duplicate_dispatch_deduped_by_idempotency_key` ·
`test_send_fails_closed_without_webhook_secret` · `test_workflow_webhook_requires_authentication` ·
`test_concurrent_dispatchers_single_delivery` · `test_package_status_maintenance_message_exact`.

---

## 3. Plan 2'ye teslim edilen arayüzler — madde madde doğrulama

Planın "Plan 2'ye teslim edilen arayüzler" bölümü KANONİK listedir. Her maddesi
`apps/social/backend/tests/test_plan2_interface_contract.py` içinde belgelenen argümanlarla
import edilip ÇAĞRILIR (13 test, hepsi PASS).

| # | Teslim maddesi | Sözleşme testi |
|---|---|---|
| 1 | Migration 032 şeması — üç ilişkinin TAM katalog manifesti (kolon+varsayılan · kısıt+birincil/yabancı anahtar · indeks · tetikleyici; KAPALI küme) | `test_migration_032_relation_manifest_is_closed` (ilişki başına parametreli) |
| 1a | Taşıyıcı tabloların 032-ait yüzeyi (`brands.sub_sector_id` + FK · `posts` damga çifti + MATCH FULL · iki tetikleyici) | `test_migration_032_carrier_surface_delivered` |
| 1b | K-135: Plan 2 yalnız `draft` yazar, yalnız `insert_draft` üzerinden | `test_plan2_write_surface_produces_draft_only` |
| 2 | `normalize_special_day_key(name) -> str` | `test_normalize_special_day_key_documented_signature` |
| 3 | `validate_package_content(content, *, banned_brand_names, holiday_keys)` | `test_validate_package_content_documented_signature` |
| 4 | `insert_draft(db, *, sector_id, content, schema_version, run_id=None, actor)` | `test_insert_draft_and_activate_chain_end_to_end` |
| 5a | `activate_package(db, *, package_id, evidence, actor)` | `test_insert_draft_and_activate_chain_end_to_end` |
| 5b | `rollback_package(db, *, sector_id, to_version, evidence, actor)` — AYRI kanıt | `test_rollback_package_takes_its_own_evidence` |
| 5c | `deactivate_package(db, *, package_id, actor)` — kanıt istemez | `test_deactivate_package_documented_signature` |
| 6 | `record_admin_event(db, *, kind, payload, idempotency_key) -> uuid` | `test_record_admin_event_documented_signature` |
| 7 | Katman-1 harness (`tests/prompt_regression/`) | `test_katman1_harness_is_delivered_and_live` |
| 8 | `video_kodlar` İKİ HAVUZ (`hareket` + `sahne`, ikisi de liste) | `test_video_kodlar_delivers_two_pools` |

**Pozitif kontrol.** ON mutasyonun HEPSİ, `de04ede` commit'indeki SON hâle (13 test)
karşı yeniden koşuldu — eski ölçümden taşınan sayı YOKTUR (bir önceki sürümde tablo ona
çıkmışken metin dokuz diyordu; bağımsız hakem yakaladı). Ortak komut:
`cd apps/social/backend && .venv/bin/python -m pytest tests/test_plan2_interface_contract.py -q`

| # | Mutasyon (uygulanan tam değişiklik) | Sonuç | Yakalayan |
|---|---|---|---|
| M1 | `sector_packages.py`: `VIDEO_POOL_KEYS` → `("hareket",)` | `6 failed, 7 passed` | sözleşme testi |
| M2 | `sector_packages.py`: `_check_special_day_keys(...)` çağrısı kaldırıldı | `1 failed, 12 passed` | sözleşme testi |
| M3 | `capture.py`: `assert_matches_fixture` başına erken `return` | `1 failed, 12 passed` | sözleşme testi |
| M4 | `sector_packages.py`: `insert_draft` `'draft'` yerine `'active'` yazdı | `4 failed, 9 passed` | sözleşme testi |
| M5 | `032_*.sql`: `content_md` → `content_markdown` | `1 failed, 12 passed` | manifest (kolon) |
| M6 | `032_*.sql`: `sector_packages.id` `PRIMARY KEY` → `UNIQUE` | `1 failed, 12 passed` | manifest (kısıt) |
| M7 | `032_*.sql`: `decision_log` `DEFAULT '[]'` kaldırıldı | `1 failed, 12 passed` | manifest (varsayılan) |
| M8 | `032_*.sql`: `sector_id` `REFERENCES social.sectors(id)` kaldırıldı | `1 failed, 12 passed` | manifest (yabancı anahtar) |
| M9 | `032_*.sql`: `brands` tetikleyicisi `BEFORE INSERT OR UPDATE` → `BEFORE INSERT` | `4 passed, 9 errors` | migration'ın KENDİ garanti bloğu |
| M10 | `032_*.sql`: `sector_research_artifacts` → `CREATE UNLOGGED TABLE` | `1 failed, 12 passed` | manifest (tablo imzası) |

**Tablo imzası neden ayrı bir yüzey.** M10'u başka HİÇBİR kapı yakalamıyor: kısıt, indeks ve tetikleyici tanımlarının hiçbiri tablonun kalıcı mı geçici mi olduğunu taşımaz, kolon imzası da taşımaz. `UNLOGGED` bir tablo çökmede BOŞALIR. Yüzey listesi kendi icadım değil — migration 034'ün tablo-imzası standardıyla aynı beş alan (relkind · kalıcılık · bölüm · satır güvenliği · zorlanmış satır güvenliği). Aynı mutasyon `sector_packages` üstünde denendiğinde PostgreSQL'in KENDİSİ reddediyor (kalıcı `posts` tablosundan ona yabancı anahtar var), o yüzden ölçüm gelen yabancı anahtarı olmayan tabloyla yapıldı.

**Hangi eksende asıl kapı kim — dürüst ayrım.** M9 ve daha önce ölçülen üç mutasyon
(indeks UNIQUE'liği · tetikleyici adı · damga FK'sının MATCH FULL'ü) sözleşme testine
ULAŞMADAN migration'ın kendi garanti bloğunca reddedilir (veritabanı hiç kurulamaz).
Kolon imzası · birincil anahtar · varsayılan · yabancı anahtar eksenlerinde ise garanti
bloğu SESSİZ kalıyor (bilinen boşluk: `CURRENT.md` →
`migration-guarantee-block-signature-gap`) ve yakalayan tek şey bu manifesttir.

**Neden liste değil manifest.** İki bağımsız review turu üst üste AYNI ekseni buldu
("şu özelliği de denetlemiyorsun" — önce tablo/kolon, sonra birincil anahtar/varsayılan/
yabancı anahtar). Elle uzatılan özellik listesi her turda yeni bir varyant üretir ve
kapanmaz. Manifest ekseni SEÇMEZ: her ilişkinin kolon · kısıt · indeks · tetikleyici
kümesi kataloğdan okunup beklenenle kapalı küme olarak karşılaştırılır; eksik olan da
fazla olan da bulgudur.

**Manifestin dürüst sınırı.** Manifest kataloğdan üretildi ve `032_sector_packages.sql`'e
karşı okunarak doğrulandı; yani migration'ın YAZDIĞINI değil, uygulandığında ORTAYA
ÇIKANI pinler. Migration'ın kendisi yanlışsa manifest o yanlışı dondurur — koruduğu şey
sonraki SESSİZ sapmadır. `NOT NULL` kısıt satırları manifestten dışlandı (PG17+ bunları
kısıt olarak listeler, PG16 listelemez; null'lanabilirlik zaten kolon imzasında).

**Kapsam sınırı (dürüst etiket):** bu testler arayüzlerin VAR ve ÇAĞRILABİLİR olduğunu
kanıtlar; Plan 2'nin onları doğru KULLANACAĞINI kanıtlamaz.

---

## 4. Kapsam DIŞI — "Plan 2 / pilot" etiketiyle

Bunlar eksik değil, **bilinçli olarak bu planın dışında**:

- **Motor testleri (Faz 1)** — snapshot §13.2(b) maddeleri. Paketi ÜRETEN hat
  (araştırma → hakemlik → sentez → motor → komut ailesi) Plan 2'nin kapsamı.
- **Katman-2 (kör değerlendirme)** — örneklem, rubrik, çapraz sektör testi. Geçme eşiği
  YOK (K-11 (b) açık). Pilot işi.
- **K-71 açık-soru DURUMUNUN üretimi** — durumu üreten hat Plan 2'de. Mekanik RED kapısının
  kendisi Plan 1'de kanıtlandı (yukarıda, §2 yaşam döngüsü).
- **Kişisel-veri doğrulaması (spec §3.7)** — gerçek veri yazımı + ilk aktivasyondan ÖNCE
  koşulur; bu planda gerçek paket yazılmadı.
- **K-45 geri-dönüş bildirimi** — `recovered` bandı + atama-geçmişi kanıtı (F23 devri).
  Devre-dışı ayağı ve olay altyapısı Plan 1'de kuruldu; geri-dönüş mesajı Plan 2'de.
- **Brief/sentez hattının İKİ HAVUZ üretmesi** — sözleşme (şekil) Plan 1'de pinlendi;
  havuzları gerçekten DOLDURAN hat Plan 2'de. Asgari eleman sayısı brief biçim
  sözleşmesinin işidir ve ölçülmemiş bir sayı kapı yapılmaz (İlke 9).
- **Alt sektör satırlarının AÇILMASI** — korumalar ve sweep mekanizması hazır; satır açma
  pilot/Plan 2 adımı (spec §13.2 adım 4).

---

## 5. Ertelenen doğrulamalar — evi belli, "yapıldı" DEĞİL

**Eray kararı (2026-08-25):** Plan 1'in tüm manuel doğrulamaları TEK bir turda, **Plan 2
bittikten sonra** koşulacak. Bu kapanış raporu bu yüzden arayüz yüzeyleri için
"doğrulandı" İDDİA ETMEZ.

| Ertelenen | Ev / tetik |
|---|---|
| Task 15 arayüz doğrulaması (onayla/değiştir/boşalt · boş-aday hâli · kanal doldurma · sitesiz öneri düğmesi) | Plan 2 sonrası tek doğrulama turu |
| Canlı n8n workflow importu + aktivasyon + TEK Telegram teslimi smoke'u | aynı tur |
| Gerçek arayüzde uçtan uca üretim (gerçek sektör paketiyle) | aynı tur |
| Öneri uçlarının GERÇEK model çağrısıyla koşulması (bugün hepsi sahte istemciyle) | aynı tur |

---

## 6. MANUEL ADIMLAR (koşulmadı — Plan 2 sonrası tura devredildi)

Aşağıdakilerin HİÇBİRİ bu oturumda yapılmadı. Liste, yapılacak işin kendisidir.

1. **Migration'ları canlıya uygula:** 032 · 033 · 034, numara sırasıyla, DOSYA DOSYA:

   ```
   psql "<canlı DSN>" -v ON_ERROR_STOP=1 --single-transaction \
        -f shared/db/migrations/032_sector_packages.sql
   ```
   (aynısı 033 ve 034 için).

   **İKİ bayrak da zorunludur:** yalnız `ON_ERROR_STOP=1` atomiklik SAĞLAMAZ — reddeden bir
   doğrulama bloğu kendinden önceki DDL'i commit edilmiş bırakır (ölçüldü).

   **Dağıtım runner'ı (`run-migrations.sh`) bu iş için KULLANILMAZ.** Runner uygulanmış
   migration DEFTERİ tutmaz; 001'den başlayıp hepsini yeniden koşar ve zaten göçmüş bir
   veritabanında 003'ün koşulsuz `ADD CONSTRAINT`ine takılıp 032'ye HİÇ ULAŞMAZ (final
   review'ın orta bulgusu; ilk yazdığım talimat bu yüzden yanlıştı). Runner sıfırdan yerel
   kurulum içindir.
2. **`N8N_ADMIN_EVENT_SECRET` canlıya kurulmalı.** Ayrıca
   `apps/social/backend/.env.example` dosyasına bu satır **ELLE** eklenmeli — sır-dosyası
   yazma kapısı agent'ı engelliyor, bu yüzden depoda örnek satır YOK.
3. **`OTOMAIX_ADMIN_TELEGRAM_BOT_TOKEN` + `OTOMAIX_ADMIN_TELEGRAM_CHAT_ID`** env'leri kurulmalı.
4. **n8n workflow:** `shared/n8n-workflows/sector-package-admin-events.json` import edilir,
   header-auth kimlik bilgisi yaratılır, workflow'daki yer tutucu gerçek kimlikle değiştirilir,
   workflow aktive edilir, sentetik bir olayla TEK Telegram teslimi smoke'u koşulur.
5. **Task 15 arayüz doğrulaması** (§5 tablosu).
6. **Alt sektör satırı AÇILMAZ** — korumalar hazır, açma adımı pilot/Plan 2'ye ait.

---

## 7. Kabul edilen riskler (açıkça — İlke 3, mutlaklık iddiası YOK)

- **F17 (Eray, 2026-08-23):** K-07 damgası **edited-lineage atfıdır** — düzenlenmiş bir
  üretimin hangi paket sürümünden türediğini söyler, düzenlenmemiş olduğunu söylemez.
  Yeniden açtırma kararı Eray'a aittir.
- **On-prem PG16 ↔ 032'nin PG18 kolonu (Eray risk kabulü):** çözülmedi + park edildi.
  `IS JSON OBJECT` ve `conenforced` yalnız PostgreSQL 18.3'te ÖLÇÜLDÜ; PG16'daki varlıkları
  BELGEYE dayanıyor, ölçüme değil.
- **033 ve 034 için geri alma script'i YOK** — plan istemedi, uydurulmadı.
- ~~Başarısız migration yarım şema bırakır~~ → **KAPATILDI (2026-08-25, final review F-H2).**
  `ON_ERROR_STOP=1` yalnız AKIŞI durduruyordu, YAPILANI geri almıyordu; ölçüldü — reddeden
  bir doğrulama bloğundan önceki DDL commit edilmiş kalıyordu. Dağıtım runner'ı artık her
  dosyayı `--single-transaction` ile uyguluyor ve test altyapısı AYNI anlambilimi kullanıyor
  (üretimde olmayan bir garantiyi testte varmış gibi göstermemek için).
  **İki dosya muaf ve ikisinin de gerekçesi ölçülü:** 011 `CREATE INDEX CONCURRENTLY`
  içerir (transaction bloğunda koşamaz; atomik DEĞİL, yeniden koşum tamamlar), 017 kendi
  `BEGIN/COMMIT`ini taşır (sarmak garantiyi ZAYIFLATIRDI — içteki COMMIT dıştakini erken
  kapatıyor, ölçüldü). Muafiyet listesi gerçekle iki yönlü test edilir.
- **[accepted_risk — final review, orta]** `record_admin_event` aynı idempotency anahtarıyla
  gelen FARKLI bir olayı sessizce yutar: mevcut satırın kimliğini döner, `kind`/`payload`
  karşılaştırmaz. Bu BİLİNÇLİ bir karardır ("outbox bir denetim kaydıdır, sonradan gelen bir
  çağrı gerçekliği yeniden yazamaz") ve testle pinlidir. Değiştirmek bir tasarım kararıdır,
  düzeltme değil. Bugünkü çağıran anahtarı UUID'den türetiyor, yani çakışma yolu dar.
- **[accepted_risk — final review, orta]** `resolve_package_context` marka sözlüğünde
  `sub_sector_id` anahtarının YOKLUĞUNU, açık `NULL` ile aynı sayar: eksik projeksiyon sessizce
  "paketsiz" dalına düşer ve beklenen `package_read_error` olayı yazılmaz. Bugün tüm çağıranlar
  alanı taşıyor; ayırt etmek tip sözleşmesi işidir ve çözümleyicinin bloklamama kuralıyla
  birlikte tasarlanmalı.
- ~~Migration 032/033'ün garanti blokları kolon/tablo imzasını denetlemiyor~~ →
  **KAPATILDI (2026-08-25, final review F1).** 034'ün deseni 032 ve 033'e taşındı: dört
  tablonun (`sector_research_artifacts` · `sector_packages` · `generation_stamps` ·
  `package_events`) tablo imzası + attnum sıralı kolon imzası + birincil anahtarı
  doğrulanıyor. Tuzak testleriyle ölçüldü (yanlış tip · PK'sız · UNLOGGED · satır
  güvenliği açık); kapılar kaldırılınca aynı tuzaklar GEÇİYOR — yani testler yeni
  kapıları ölçüyor, öncekileri değil. **İkinci turda genişletildi:** madde madde kontrol
  POZİTİF bir izin listesiydi — adı geçmeyen nesne hakkında hiçbir şey söylemiyordu. Artık
  kısıt · tetikleyici · indeks kümeleri KAPALI karşılaştırılıyor; fazladan bir `CHECK (false)`,
  fazladan bir UNIQUE ya da yazımı reddeden bir tetikleyici de yakalanıyor (üçü de ayrı
  tuzakla ölçüldü — üçü de eskiden GEÇİYORDU).
- ~~Migration 011 yarım kalmış eşzamanlı indeks kalıntısını sessizce geçer~~ →
  **KAPATILDI.** `IF NOT EXISTS` geçersiz bir indeksin ADINI görüp DDL'i atlıyordu: migration
  başarılı biterken indeks kullanılamaz kalıyor, planlayıcı onu kullanmıyor ve hiçbir hata
  görünmüyordu. 011 artık beklenen indekslerin varlığını VE uygulanır olduğunu denetliyor;
  onarımı OTOMATİK yapmıyor (üretimde indeks düşürmek bilinçli karardır), ne yapılacağını
  söyleyip DURUYOR. Testle ölçüldü. **Üçüncü turda genişletildi:** ilk yazdığım blok indeksi
  ADA göre eşliyordu; aynı adda ama başka tabloya/kolona kurulmuş GEÇERLİ bir indeks geçerdi
  (`IF NOT EXISTS` o adı görüp DDL'i atlar, migration "başarılı" der, beklenen indeks hiç var
  olmaz; benzersiz bir taklit ayrıca meşru yazımları reddeder). Kimlik artık TAM TANIMDIR —
  032/033'ün indeks manifestlerinde de öyle. Üç taklitle ölçüldü (yanlış kolon · benzersiz
  taklit · başka tablo); üçü de `indisvalid=true` olduğu için geçerlilik kontrolüne takılmıyordu.
- ~~032'nin TAŞIYICI sözleşmesi (brands kolonu + yabancı anahtarı + indeksi) denetlenmiyor~~ →
  **KAPATILDI (final review tur 4).** 032 `brands.sub_sector_id`'yi ve `posts` damga çiftini
  EKLER, ama `ADD COLUMN IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS` var olanı DEĞİŞTİRMEZ ve
  doğrulayıcı yalnız tetikleyiciye bakıyordu. Yabancı anahtarsız bir kolonda migration rc=0 ile
  geçerdi (sektör silinince marka ataması ÖKSÜZ kalır); aynı adda benzersiz bir indeks taklidi
  ise aynı alt sektöre ikinci markayı atamayı reddederken "başarılı" derdi. Üç tuzakla ölçüldü.
- ~~Migration dizininin symlink OLMASI~~ → **KAPATILDI.** Dosya adına bakan kapı bunu
  göremiyordu: `shared/db` symlink olduğunda her çocuk düz dosya görünür. Runner ve test
  altyapısı artık dizin zincirini FİZİKSEL yolla karşılaştırıyor; depo dışına çıkan yol
  ilk veritabanı dokunuşundan ÖNCE reddediliyor.
- **`sector_packages.sector_id` değişmez değil** — yaşam döngüsü geçişleri uyuşmazlıkta
  fail-closed durur, ama kolonu değişmez kılan migration yazılmadı. Ölçüldü: depoda bu
  kolonu güncelleyen üretim yolu YOK. Ev: `CURRENT.md` →
  `sector-package-sector-id-immutability`.
- **Öneri ucunun kota kapısı Redis yokken fail-open'dır** — ev kuralının belgeli kararı;
  tek uç için ayrı politika uydurulmadı.
- **Alt sektör YAZIM kapısı aktif paket ŞARTI ARAMAZ** — yalnız "alt sektör satırı mı" diye
  sorar. K-43 gereği paketi arşivlenen markanın ataması korunur; paketsiz alt sektör meşru
  bir kayıtlı değerdir. Bilinçli tasarım kararı, bulgu değil.
- **Site analizi ucunun "model hatası → boş şablonla HTTP başarı" davranışı** bu partiden
  ÖNCE de vardı ve değiştirilmedi. YENİ öneri ucunda aynı sınıf kapatıldı (arıza → 503).
- **Senkron sağlayıcı çağrısı gerçekten kesilemiyor** — süre sınırı yalnız beklemeyi keser,
  çalışan çağrı iş parçacığını tutmaya devam eder. Kod tabanı GENELİ bir desen, bu partinin
  kusuru değil. Ev: `CURRENT.md` → `sync-provider-calls-not-cancellable`.
- **Marka ayarları otomatik kaydetmesinin dört kayıp yolu açık** — MÜŞTERİ yüzeyi.
  Ev: `CURRENT.md` → `brand-settings-save-integrity`. Tetik: bu kapanıştan sonra, canlıya
  müşteri alınmadan ÖNCE. Önyüz test altyapısı bu işin ÖN KOŞULU.
- **Sunucudaki koşullu yazım kapısı ve 5 testi depoda UYKUDA** — hiçbir çağıran sürüm
  göndermiyor, davranış Task 15 sonrasıyla aynı. Uyanmadan tek başına bir şey garanti ETMEZ.
- **Kütüphane yoklaması terminal başarısız satırları sınırsız yokluyor** (checkpoint 12).
- **Test altyapısı:** eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür · migration
  keşfi tekrarlı numarayı reddetmiyor · `db` fixture geri sarma testi yok ·
  `sector_research_artifacts` TRUNCATE regresyonu yok.
- **Belgeli sınırlar (testle pinli, borç DEĞİL):** ayraçsız kanal işareti yakalanmaz ·
  tam genişlikli ayraçlı etiket tanınır ama basımdan çıkarılamaz · CTA içinde serbest
  köşeli ayraç yok · `brand_kit` anahtarı silinemez.
- **Prompt enjeksiyonu savunması (K-10, Eray 2026-08-23):** Faz 1'de KURULMAZ — bilinçli
  risk kabulü. Yeniden açılma tetiği: paket sayısı / kaynak çeşitliliği artışı.

---

## 8. Kapanış cümlesi

Plan 1'in 16 görevinin 16'sı yazıldı. Otomatik kapılar yeşil (577 arka uç testi · 121
byte-exact fixture · canlı sweep farkı 0). **Arayüz yüzeyleri ve canlı ortam adımları
DOĞRULANMADI** — ertelendi, evi ve tetiği §5-6'da yazılı. Bu rapor "sistem çalışıyor"
demez; "şu kapılar şu komutlarla ölçüldü ve şunlar ölçülmedi" der.
