---
title: Sektör Bilgi Paketi — Plan 2/2 Arayüz Eki (BAĞLAYICI)
status: binding-addendum
date: 2026-08-30
binds_plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
source_spec: docs/specs/2026-08-21-sektor-bilgi-paketi.md
canonical_input: docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md
preflight_scan: .superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/preflight-scan.md
rulings: 14
---

# Plan 2 — Arayüz Eki: 14 hükmün sözleşme metni

## Bu belge neden var

Plan 2'nin 20 görevi tek tek uygulanır ve **her biri kendi brief'ine karşı** gözden geçirilir.
Bunun kaçınılmaz kör noktası şudur: **iki görevin birbirinden bağımsız olarak FARKLI icat
edeceği bir sözleşme, görev-başına review'a görünmez.** Task 8 `record_result`'ı yazarken
kendi brief'ine uyar, Task 13 `EngineResult`'ı yazarken kendi brief'ine uyar; ikisi
buluşmadığında hiçbir görev review'ı "burada bir uyuşmazlık var" diyemez — çünkü uyuşmazlık
görevlerin *arasındadır*, içinde değil.

Bu ek tam olarak o **paylaşılan sözleşmeleri** — imzalar, tip tanımları, kapalı değer
kümeleri, test sahipliği — **önden** sabitler; böylece iki görev ayrışamaz.

**BAĞLAYICIDIR: bu belge ile plan gövdesi çeliştiğinde BU BELGE GEÇERLİDİR.** Her hüküm,
geçersiz kıldığı plan satırlarını adıyla sayar. Ek hiçbir yeni kapsam açmaz; yalnız
kontrolörün 2026-08-30'da verdiği 14 hükmü test edilebilir sözleşme metnine çevirir.

**Kaynak hiyerarşisi:** spec girdisi (`docs/research/2026-08-21-...-spec-input.md`) spec'e
ÜSTÜNDÜR; çeliştikleri yerde girdi satırı alıntılanır ve o kazanır.

**Okuma kuralı (İlke 8):** bu belgenin gövdesi teknik seviyedir — doğrulaması Eray onayı
değil, review zinciri + adı konmuş testlerdir.

---

## R1 — Koşu klasörleri pinlenen dış depoya ASLA commit edilmez

**Kusur (plan satırları):** `runs.run_folder(run_id) -> <arastirma-deposu>/kosu/<run_id>/`
(plan 981) her koşunun artefaktını, pin kapısının **commit sha**'sını karşılaştırdığı depoya
(plan 403-406) yazar; Task 18 Step 4 o depoyu sabit bir commit'e getirir (plan 1959), Task 19
klasörü orada yaratır (plan 1984). "Monorepo'ya düzenlenebilir ikinci kopya ALINMAZ"
kısıtı (plan 67-69) ile birlikte okununca plan, klasörün commit edilip edilmeyeceğini
hiç söylemez.

**Ölçüm (2026-08-30, `verify_pin`'in plan metni, satır 403-406):** kapı kümesi TAM OLARAK
dörttür — dosya yok · hash uyuşmuyor · commit uyuşmuyor · depo dizini yok. Çalışma ağacının
temizliği **kontrol edilmez** ve doğrulama açıkça salt-okunurdur (plan 406). Yani izlenmeyen
koşu klasörü yazmak pini DÜŞÜRMEZ; onu **commit etmek** düşürür (HEAD kayar → commit
uyuşmazlığı → fail-closed).

**Kural (kontrolör):** koşu klasörü kanonun koyduğu yerde KALIR — spec girdisi satır 2318:
*"Yeniden üretimde sorun ortadan kalkar — **brief kopyası koşu klasörüne yazılır** (**K-17**,
Bölüm 7.2)."* Bu satır kanoniktir ve spec'in sessizliğini yener. `kosu/` dış deponun
`.gitignore`'una **Task 2'de** eklenir (o görev zaten orada commit atıyor), ve `verify_pin`
açık bir **NEGATİF invariant** kazanır.

**Bağlayıcı sözleşme:**

```python
# apps/social/backend/app/services/sector_pipeline/contracts.py  (Task 1)
def verify_pin(pin: ContractPin, repo_root: Path) -> list[str]: ...
```

`verify_pin` invariantları — pozitif küme DEĞİŞMEZ (dört kapı, plan 403-406), üstüne
**negatif invariant** eklenir:

- **Kirli çalışma ağacı TEK BAŞINA pini DÜŞÜRMEZ.** Manifestte adı geçmeyen hiçbir dosya
  veya dizin — izlenmeyen `kosu/<run_id>/` klasörleri dâhil — uyuşmazlık üretmez.
- Kapı yalnız şunlara bakar: (a) pinlenen ÜÇ dosyanın (`_SABLON.md` ·
  `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`) sha256'sı, (b) dış deponun HEAD
  commit sha'sı, (c) depo dizininin varlığı.
- `verify_pin` `git status`/`git diff` çağırmaz ve dış depoda hiçbir şey değiştirmez.
- Pinlenen üç dosyanın baytı değişirse kapı zaten (a) ile düşer; bu **kirlilik değil içerik
  drift'idir** ve iki hâl karıştırılmaz.

Dış depo `.gitignore` kalemi (Task 2, `/root/otomaix-sosyal-medya-arastirmasi/.gitignore`):

```
kosu/
```

**Etkilenen görev · geçersiz kılınan satırlar:** Task 1 (invariant listesi plan 402-406
üzerine EKLENİR) · Task 2 (Files listesine `.gitignore` eklenir; plan 428-433) ·
Task 8 `run_folder` yeri DEĞİŞMEZ (plan 981 geçerli kalır) · Task 18 Step 4 / Task 19
belirsizliği (plan 1959 · 1984) bu hükümle kapanır.

**Kanıt testi · sahibi:**
- `test_verify_passes_with_dirty_external_worktree` — sahte depoda pinlenen üç dosya
  eşleşiyor, yanında izlenmeyen `kosu/<run_id>/x.md` var → `verify_pin` **boş liste** döner.
  **Sahip: Task 1**, `tests/test_contract_pin.py`.
- `test_external_repo_gitignores_run_folder` — gerçek dış deponun `.gitignore`'u `kosu/`
  satırını taşır. **Sahip: Task 2**, `tests/test_contract_pin.py` (Step 5'te eklenir).

---

## R2 — Her NOT NULL kolonun ve her kapı kolonunun ADI KONMUŞ bir üreticisi olur

**Kusur (plan satırları):** (a) `kosu_turu text NOT NULL` (plan 764) ama
`open_run(db, *, sector_id, run_id, parent_run_id=None)` (plan 956) böyle bir parametre
taşımıyor; (b) `durum='tamamlandi'`, `load_verified_run`'ın **1. kapısıdır** (plan 323) ama
onu yazan bir üretici yok; (c) `engine_version` · `engine_config_sha` · `content_sha` ·
`decision_log_sha` · `policy_report` · `engine_diff` koşu satırına yalnız isimsiz
`**report_fields` üzerinden ulaşıyor (plan 971-972). Bu, planın `barrier_report` için
zaten uyguladığı düzeltmenin (plan 973-977) kardeşlerine **süpürülmemiş** hâlidir.
(d) `engine_version`/`engine_config_sha` `load_verified_run`'ın 3. ve 4. kapısı ve
`affected_packages`'ın kapalı dörtlüsünün yarısı (plan 323-326 · 994-999) olmasına rağmen
`EngineResult`'ta YOK (plan 1431-1433) ve `engine_config_sha`'yı (K-97) hesaplayan yer
adlandırılmamış.

**Kural (kontrolör):** `open_run` zorunlu `kosu_turu` parametresi kazanır (kapalı küme).
`record_result` **yazdığı HER alanı adı konmuş anahtar parametreyle** alır ve
`**report_fields` SİLİNİR. `durum='tamamlandi'`'yi yazan `record_result`'tır — açıkça
yazılır. `engine_version` + `engine_config_sha` `EngineResult`'a eklenir; hesaplandıkları
yer adlandırılır.

**Bağlayıcı sözleşme:**

```python
# runs.py  (Task 8)
KOSU_TURLERI: tuple[str, ...] = ("ilk", "periyodik", "duzeltme")     # KAPALI
DURUMLAR:    tuple[str, ...] = ("calisiyor", "tamamlandi", "tamamlanmadi")  # KAPALI
SONUCLAR:    tuple[str, ...] = ("activation_eligible", "no_change", "blocked")  # KAPALI

async def open_run(
    db,
    *,
    sector_id: UUID,
    run_id: str,
    kosu_turu: str,                 # KOSU_TURLERI içinden; varsayılan YOK
    parent_run_id: str | None = None,
) -> UUID: ...
```

- `open_run` satırı `durum='calisiyor'`, `sonuc=NULL` ile açar.
- `kosu_turu` ∈ {`ilk`, `periyodik`, `duzeltme`} — küme KAPALIDIR. `open_run`
  **`duzeltme` değerini KENDİ reddeder** (`ValueError`): o değer `duzeltilen_run_id`
  gerektirir (036 CHECK, plan 830-834) ve onu yalnız `open_correction_run` yazar.
- `parent_run_id` DOLU ise (yeniden koşum, K-83) satır ana koşudan **`kosu_turu` ·
  `duzeltilen_run_id` · `package_id` üçlüsünü DEVRALIR** (plan 830-836'nın devralma hükmü);
  açıkça verilen `kosu_turu` ana koşununkinden farklıysa çağrı REDDEDİLİR.

```python
# runs.py  (Task 8)
async def record_result(
    db,
    *,
    run_id: str,
    sonuc: str,                      # SONUCLAR içinden
    sebep: str | None,               # K-90 — varsayılan YOK, açıkça verilir
    engine_version: str,             # K-97 — her satıra damgalanır, NULL olamaz
    engine_config_sha: str,          # K-97 — NULL olamaz
    policy_report: dict,             # K-95 — kararsızlar + bulgu izi burada taşınır
    barrier_report: dict,            # K-24 — ZORUNLU (plan 973)
    engine_diff: dict,               # K-96
    final_candidate: dict | None,    # F19
    final_decision_log: list[dict] | None,   # F19
    content_sha: str | None,         # K-92
    decision_log_sha: str | None,    # F19
) -> None: ...
```

- **`**report_fields` YOKTUR.** Fonksiyonun imzasında hiçbir `*args`/`**kwargs` bulunmaz —
  yazdığı her kolonun adı imzada görünür.
- Hiçbir parametrenin varsayılanı yoktur: çağıran her alanı **açıkça** verir (bir alanın
  sessizce düşmesi bu sınıfın ta kendisidir).
- **`record_result` aynı ifadede `durum='tamamlandi'` yazar.** `load_verified_run`'ın
  1. kapısını (plan 323) sağlanabilir kılan tek üretici budur.
- `sonuc='activation_eligible'` iken `final_candidate` · `final_decision_log` ·
  `content_sha` · `decision_log_sha` DÖRDÜ de dolu olmak ZORUNDADIR; biri eksikse yazım
  REDDEDİLİR (plan 979-980 F19 hükmü). Diğer iki sonuçta bu dördü `None` olabilir;
  `engine_version` · `engine_config_sha` · `policy_report` · `barrier_report` üç sonuçta da
  ZORUNLUDUR.
- `kararsizlar` için ayrı kolon YOKTUR: plan 1448-1449 gereği "koşu raporuna girer" —
  yani `policy_report` içinde taşınır.

```python
# runs.py  (Task 8) — load_verified_run'ın döndürdüğü tip
@dataclass(frozen=True)
class VerifiedRun:
    id: UUID
    run_id: str
    parent_run_id: str | None
    sector_id: UUID
    package_id: UUID | None
    kosu_turu: str
    duzeltilen_run_id: UUID | None
    durum: str
    sonuc: str
    sebep: str | None
    engine_version: str
    engine_config_sha: str
    content_sha: str
    decision_log_sha: str
    final_candidate: dict
    final_decision_log: list[dict]
    policy_report: dict
    barrier_report: dict
    engine_diff: dict
    approval_snapshot: dict | None
    approval_karar: str | None
    snapshot_sha: str | None
    katman1_attestation: dict | None
    katman2_attestation: dict | None
    readiness_attestation: dict | None
```

`VerifiedRun` yalnız YEDİ kapının tamamı geçtiğinde üretilir (plan 323-326); bu yüzden
`engine_version` · `engine_config_sha` · `content_sha` · `decision_log_sha` ·
`final_candidate` · `final_decision_log` alanları `| None` DEĞİLDİR — kapıdan geçmiş bir
satırda dolu olmaları garantidir.

```python
# engine.py + policy_config.py  (Task 13)
ENGINE_VERSION: str = "..."          # modül sabiti; motor sözleşmesi değişince artar

def config_sha(config: PolicyConfig) -> str:      # policy_config.py — K-97 üreticisi
    """PolicyConfig'in kanonik hash'i. identity.canonical_sha'yı ÇAĞIRIR (K-92),
    ikinci bir hash kuralı yazmaz."""

@dataclass(frozen=True)
class EngineResult:
    sonuc: str                       # SONUCLAR — KAPALI
    sebep: str | None
    final_candidate: dict | None
    final_decision_log: list[dict] | None
    engine_diff: dict
    kararsizlar: list[dict]
    barrier_report: dict
    content_sha: str | None
    decision_log_sha: str | None
    engine_version: str              # YENİ — load_verified_run kapı 3'ün kaynağı
    engine_config_sha: str           # YENİ — kapı 4'ün kaynağı; config_sha() üretir
```

`decide` her üç sonuçta da `engine_version=ENGINE_VERSION` ve
`engine_config_sha=config_sha(config)` damgalar (K-97, plan 141-143).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — plan 956 (`open_run` imzası)
ve plan 971-972 (`record_result` imzası) GEÇERSİZ, yerine yukarıdakiler. **Task 13** — plan
1431-1433 (`EngineResult` alan listesi) iki alanla genişler; `config_sha` ve
`ENGINE_VERSION` Task 13'ün Produces listesine EKLENİR.

**Kanıt testi · sahibi:**
- `test_open_run_requires_kosu_turu` · `test_kosu_turu_value_set_is_closed` ·
  `test_open_run_rejects_duzeltme_type` · `test_retry_inherits_type_target_and_package`
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_record_result_sets_durum_tamamlandi` · `test_record_result_persists_every_named_field`
  (on iki alanın on ikisi de satırda okunur) ·
  `test_record_result_signature_has_no_var_keyword_arguments` (yapısal: `inspect.signature`
  ile `VAR_KEYWORD` YOK) · `test_record_result_rejects_eligible_run_missing_f19_fields`
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_engine_result_carries_version_and_config_sha` ·
  `test_config_sha_changes_when_config_changes` ·
  `test_config_sha_uses_identity_canonical_rule` — **Sahip: Task 13**,
  `tests/test_policy_engine_outcome.py`.

---

## R3 — Onay olayı paket kimliğini TAŞIR

**Kusur (plan satırları):** planın kendi teknik kararı 14(c) (plan 169-172) şunu bağlıyor:
olaylar yaşam döngüsü kapsam sınıfındadır ve `033 F21` gereği `sector_id` + `package_id` +
`actor` ister, *"bu yüzden `record_decision` koşu kimliğinin yanında paket kimliğini de
taşır"*. Ölçüldü (`package_events.py:216-221`): yaşam döngüsü olayı `sector_id`,
`package_id` ve `actor` yoksa `PackageEventContractError` ile düşer. Buna rağmen plan
1515'teki imza paket kimliği taşımıyor — yani `approval`/`rejection` olayı **yazılamadan
patlardı**.

**Kural (kontrolör):** eklenir; kaynağı **kilitli doğrulanmış koşudur.**

**Bağlayıcı sözleşme:**

```python
# approval.py  (Task 14)
KARARLAR: tuple[str, ...] = ("onay", "ret")          # KAPALI

async def record_decision(
    db,
    *,
    run_id: str,
    karar: str,                # KARARLAR içinden
    actor: str,
    seconds: int,              # K-42(b) — eşik YOK, yalnız kayıt
    snapshot_sha: str,         # F18 — karar dondurulmuş görüntünün hash'ine bağlanır
) -> None: ...
```

- Olay **`package_id` TAŞIR** ve o değer **çağırandan ALINMAZ**: `record_decision` ilk iş
  olarak `runs.load_verified_run(db, run_id=run_id, for_update=True)` çağırır ve
  `package_id` ile `sector_id`'yi **`VerifiedRun`'dan** okur. Çağıranın verdiği bir paket
  kimliği koşununkiyle çelişebilirdi; TEK KAPI doktrini (plan 327-329) ve F18 bunu yasaklar.
  Bu yüzden imzaya **çağıran-taraflı `package_id` parametresi EKLENMEZ** — hükmün istediği
  "olayın paket kimliğini taşıması"dır, çağırandan alması değil.
- Olay çağrısı: `log_package_event(db, event_type=("approval" if karar == "onay" else
  "rejection"), sector_id=run.sector_id, package_id=run.package_id, actor=actor, detail=...)`.
- `run.package_id` boşsa (taslak henüz yazılmamışsa) onay REDDEDİLİR — onay yüzeyi yalnız
  `activation_eligible` koşuda çalıştığı için taslak her zaman vardır (plan 171-172).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 14** — plan 1515-1519 imzası bu
metinle değiştirilir (parametre kümesi aynı kalır, gövde sözleşmesi bağlanır).

**Kanıt testi · sahibi:**
- `test_approval_event_carries_package_id_from_locked_run` ·
  `test_rejection_event_carries_package_id_from_locked_run` ·
  `test_record_decision_refuses_run_without_package_link` ·
  `test_record_decision_takes_no_caller_supplied_package_id` (yapısal: imzada
  `package_id`/`sector_id` parametresi YOK) — **Sahip: Task 14**,
  `tests/test_approval_surface.py`.

---

## R4 — Test, konusunu ÜRETEN görevde durur

**Kusur (plan satırları):** Task 6 (migration 036) Step 1 test listesi (plan 741-890) üç
tane **servis davranışı** testi taşıyor — konusu Task 8/Task 15 kodudur — ama Task 6 Step 5
(plan 895-896) onlardan PASS bekliyor. O kod o noktada YOKTUR.

**Kural (kontrolör):** bu üç test, konusunu kuran göreve taşınır. Task 6 yalnız
**migration'ın kendi** testlerini tutar: kolonlar · kısıtlar · CHECK'ler · geri alma.

**Bağlayıcı sözleşme — taşınan testler:**

| Test | Plan satırı | Konusu | YENİ sahip · dosya |
|---|---|---|---|
| `test_second_write_for_same_run_returns_existing_draft` | 878 | `writeback.write_draft_from_run` idempotency'si | **Task 15**, `tests/test_pipeline_writeback.py` — Task 15'in mevcut `test_replay_returns_existing_draft_without_new_version` (plan 1663) testiyle **AYNI iddiadır**; ikinci bir ad yazılmaz, Task 6'dan SİLİNİR ve Task 15'in mevcut adı kanonik sahiptir |
| `test_concurrent_write_for_same_run_yields_one_draft` | 879 | aynı yolun yarış hâli | **Task 15** — mevcut `test_concurrent_writes_yield_single_draft` (plan 1664) ile aynı iddia; Task 6'dan SİLİNİR |
| `test_retry_of_correction_inherits_target_and_type` | 877 | `runs.open_run(parent_run_id=…)` devralması (R2) | **Task 8**, `tests/test_pipeline_runs.py` — R2'nin `test_retry_inherits_type_target_and_package` testiyle birleşir |

Task 6'da **KALAN** kardeşleri (şema seviyesi, migration'ın kendi konusu, taşınmaz):
`test_package_id_is_not_unique` · `test_correction_run_may_share_package_id_with_parent` ·
`test_kosu_turu_and_duzeltilen_run_id_check_consistent` ·
`test_retry_of_correction_may_carry_both_links` (plan 873-876) — bunlar CHECK/kardinalite
testleridir, servis davranışı değil.

**Ek düzeltme (Row-D D5, aynı sınıf):** `test_content_written_without_decision_log_rejected`
(plan 864) şemada bulunmayan bir `content` kolonuna iddia ediyor; 036'nın kolonları
`final_candidate` / `final_decision_log`'dur (plan 756-758). Test adı ve iddiası
**`test_final_candidate_written_without_decision_log_rejected`** olarak düzeltilir.
Sahip DEĞİŞMEZ (Task 6).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 6** — plan 877 · 878 · 879
listeden ÇIKAR, plan 864 yeniden adlandırılır; Step 5 (plan 895-896) beklentisi böylece
karşılanabilir hâle gelir. **Task 8** ve **Task 15** — listeleri R2/R4 ile eşlenir.

---

## R5 — İmzada kullanılan her tip, onu ilk üreten görevde TANIMLANIR

**Kusur (plan satırları):** `EngineInputs` (plan 1337 · 1431), `AuditReport` (plan 1187),
`PacketRef` (plan 1135 · 1186) imzalarda kullanılıyor, hiçbir görevde tanımlanmıyor.
Sonuç: Karar Kapıları K-52'nin *"motor girdileri §9.1 ile sınırlıdır; DNA okuma yolu
açılmaz"* hükmünün (plan 88) **denetlenebileceği bir artefakt yok.**

**Kural (kontrolör):** üçü de tam alan listesiyle tanımlanır. `EngineInputs` Task 12'nin
malıdır ve en az şunları taşır: sentez aday kümesi · doğrulanmış denetçi envanteri · aktif
paket birim eşlemesi · bariyer paydası · K-91 ilk-koşu bayrağı · takvim anahtarları.
`PacketRef` ve `AuditReport` Task 9'un malıdır.

**Bağlayıcı sözleşme — Task 9 tipleri:**

```python
# auditors.py  (Task 9)
STATU_DEGERLERI: tuple[str, ...] = (
    "supported", "not_observed", "needs_update", "contradicted", "risk_unverified",
)   # KAPALI — beş değer (K-100, spec-input satır 1027-1031)

DENETCI_ROLLERI: tuple[str, ...] = ("denetci-1", "denetci-2")   # KAPALI (rol adı; ARAÇ adı DEĞİL — K-137)

BOLUM_ANAHTARLARI: tuple[str, ...]   # BEŞ anahtar; değerleri Task 4'ün pinlenmiş
                                     # sözleşme v2 metninden ÖLÇÜLEREK doldurulur, burada UYDURULMAZ (İlke 9)

@dataclass(frozen=True)
class InventoryRow:              # K-100 — dört alan; spec-input satır 1031 kanoniktir:
    unit_id: str                 # "karar birimi anahtarı, denetçi statüsü, kanıt referansı
    statu: str                   #  ve tek cümle gerekçe"
    kanit: str
    gerekce: str

@dataclass(frozen=True)
class UrlCheck:
    url: str
    kaynak: str
    erisildi: bool
    icerik_uyumlu: bool          # K-126'nın "canlı URL doğrulaması" ayağı
    not_metni: str

@dataclass(frozen=True)
class AuditReport:
    denetci: str                             # DENETCI_ROLLERI içinden
    ham_metin: str
    bolumler: dict[str, str]                 # anahtar kümesi = BOLUM_ANAHTARLARI (beş, kapalı)
    yeniden_dogrulama: tuple[InventoryRow, ...]
    url_orneklem: tuple[UrlCheck, ...]
    unit_snapshot_sha: str                   # raporun karşı raporladığı görüntünün hash'i (K-79/K-100)

@dataclass(frozen=True)
class PacketRef:
    run_id: str
    sector_id: UUID
    kok: Path                                # paket kök dizini
    kopyalar: dict[str, Path]                # anahtarlar = DENETCI_ROLLERI (iki, kapalı)
    kopya_shalari: dict[str, str]            # aynı anahtarlar; K-79: iki değer EŞİT olmak ZORUNDA
    unit_snapshot: dict[str, dict]           # identity.decision_units çıktısı (Task 3)
    unit_snapshot_sha: str                   # identity.canonical_sha(unit_snapshot)
```

`build_packet` imzası, anlık görüntüyü pakete **taşıyacak** biçimde bağlanır (R6(b)'nin
erişilebilirlik ayağı):

```python
def build_packet(
    *,
    brief: str,
    sources: list[str],
    doctor_reports: list[DoctorReport],
    active_package: dict | None,
    unit_snapshot: dict[str, dict],          # YENİ — Task 3 identity.decision_units
    run_id: str,
    sector_id: UUID,
    dest: Path,
) -> PacketRef: ...
```

**Bağlayıcı sözleşme — Task 12 tipleri:**

```python
# engine.py  (Task 12)
@dataclass(frozen=True)
class GateResults:
    katman1_passed: bool          # regresyon kapısı (spec §9.1: "prompt regresyonu zorunlu kapıdır")
    tek_aktif_ihlali: bool        # tek-aktif ön kontrolü

@dataclass(frozen=True)
class EngineInputs:
    """Motor girdileri — ALAN KÜMESİ KAPALIDIR (K-52, plan 88; spec §9.1).
    Marka DNA'sı için alan YOKTUR ve eklenmesi sözleşme revizyonu ister."""
    sentez: SynthesisResult                              # §9.1: sentez aday paketi + karar günlüğü
    aktif_paket: dict | None                             # §9.1: aktif paket (ilk koşuda None)
    aktif_schema_version: int | None                     # §9.1: şema sürümü
    aktif_birimler: dict[str, dict]                      # identity.decision_units (Task 3) — karar kapsamı kontrolü
    mevcut_birim_sayisi: int                             # bariyer paydası (K-130); ilk koşuda 0
    ilk_kosu: bool                                       # K-91
    son_turlarin_cikarmalari: list[dict]                 # §9.1: son turların çıkarma kararları (K-122)
    denetci_envanterleri: tuple[AuditReport, AuditReport] # §9.1: iki denetçi tablosu + URL örneklemi;
                                                          # YALNIZ Task 9'un doğrulanmış raporları (K-150: tam iki)
    mekanik_eleme: RoundGate                             # §9.1: mekanik eleme sonucu (Task 7)
    takvim_anahtarlari: frozenset[str]                   # §9.1: sistem özel gün listesi (normalize anahtarlar)
    otomatik_kapilar: GateResults                        # §9.1: otomatik kapı sonuçları
```

- **`PolicyConfig` `EngineInputs`'a GİRMEZ** — `decide(inputs, config)` onu ayrı alır
  (plan 1431); tek kanonik yer korunur.
- `mevcut_birim_sayisi == len(aktif_birimler)` invariantı yapımda zorlanır.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 9** — Produces listesine
`PacketRef` · `AuditReport` · `InventoryRow` · `UrlCheck` · `STATU_DEGERLERI` ·
`BOLUM_ANAHTARLARI` EKLENİR; `build_packet` imzası (plan 1135) yukarıdakiyle değişir.
**Task 12** — Produces listesine `EngineInputs` · `GateResults` EKLENİR (plan 1336-1338).
**Task 13** — `decide(inputs: EngineInputs, …)` (plan 1431) artık tanımlı bir tipe işaret
eder.

**Kanıt testi · sahibi:**
- `test_engine_inputs_field_set_is_closed` — `EngineInputs` alan adları yukarıdaki listeyle
  **birebir** eşleşir; fazlası da eksiği de RED. **K-52'nin denetlenebilir karşılığı budur**
  (preflight C12'yi kapatır). **Sahip: Task 12**, `tests/test_policy_engine_checks.py`.
- `test_engine_inputs_has_no_brand_dna_field` (K-52 negatif kontrol) — **Sahip: Task 12**.
- `test_packet_ref_carries_unit_snapshot_and_equal_copy_hashes` (K-79) ·
  `test_audit_report_inventory_rows_have_four_fields` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`.

---

## R6 — Veriyi kapılayan doğrulayıcı AYRIŞTIRILMIŞ NESNEYİ geri verir; çapraz denetçi karşılaştırması TUR seviyesindedir

**Kusur (plan satırları):** (a) `validate_report(...) -> list[str]` (plan 1138) yalnız hata
metni döner, oysa motorun girdisi *"Task 9'un **doğrulanmış** envanteridir"* (plan 1353-1354)
— ayrıştırılmış envanteri **hiçbir görev üretmiyor**; (b) `validate_report`'un ZORUNLU
`unit_snapshot` girdisinin (plan 1150-1153) adlandırılmış bir üreticisi yok ve Task 9'un
Consumes satırı (plan 1133) Task 3'ü hiç saymıyor; (c) TEK rapor alan bir doğrulayıcıdan
*"iki denetçi AYNI anlık görüntüye karşı raporlamış"* olduğunu kanıtlaması isteniyor
(plan 1153) ve testi (`test_inventory_rejects_divergent_snapshot_hash`, plan 1168) Task 9'a
dosyalanmış.

**Kural (kontrolör):** (a) `validate_report` **ayrıştırılmış envanter nesnesi + hata listesi**
döner — tip tanımlanır; (b) anlık görüntünün üreticisi adlandırılır: `identity.decision_units`
(Task 3) ve Task 9'un Consumes satırı Task 3'ü BEYAN EDER; (c) çapraz denetçi
snapshot-hash mutabakatı **iki raporu birden gören TUR seviyesi** bir fonksiyona taşınır
(Task 10) ve testi onunla birlikte gider.

**Bağlayıcı sözleşme:**

```python
# auditors.py  (Task 9)
@dataclass(frozen=True)
class ValidatedReport:
    rapor: AuditReport | None      # errors BOŞ DEĞİLSE None (geçersiz rapor nesneye dönüşmez)
    errors: list[str]

    @property
    def gecerli(self) -> bool:
        return not self.errors

def validate_report(
    text: str,
    *,
    unit_snapshot: dict[str, dict],     # identity.decision_units (Task 3) — TEK üretici
    denetci: str,                       # DENETCI_ROLLERI içinden
) -> ValidatedReport: ...
```

`validate_report`'un zorladıkları (plan 1146-1154 aynen geçerli, tek fark dönüş tipi):
beş bölüm · her envanter satırı dört alanlı · `statu` ∈ `STATU_DEGERLERI` · `unit_snapshot`
içindeki HER `unit_id` **tam bir kez** · tanınmayan kimlik YOK · tekrar YOK. **Çapraz
denetçi karşılaştırması BURADA YAPILMAZ** — tek rapor görür.

```python
# auditors.py  (Task 10) — TUR seviyesi
def check_snapshot_agreement(
    reports: list[AuditReport],
    *,
    expected_snapshot_sha: str,        # PacketRef.unit_snapshot_sha
) -> list[str]:
    """Boş liste = mutabakat. Dolu liste = tur GEÇERSİZ (K-79/K-100).
    İki koşul birden aranır: her raporun `unit_snapshot_sha`'sı pakete verilen
    değere EŞİT, ve raporlar birbirine eşit."""
```

`run_audit_round` (plan 1186) imzası DEĞİŞMEZ: anlık görüntü ve hash'i `packet`'in içinden
gelir (R5'teki `PacketRef`). Uyuşmazlıkta `AuditRound(gecerli=False, sebep=...)` döner →
K-150 gereği sentez BAŞLAMAZ (plan 1219-1221).

Motorun girdisi (plan 1353-1354'ün karşılığı): `EngineInputs.denetci_envanterleri` yalnız
`ValidatedReport.gecerli is True` olan iki rapordan kurulur; ham metin motora ULAŞMAZ.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 9** — plan 1138-1139 (dönüş tipi
`list[str]`) GEÇERSİZ; plan 1133'teki Consumes satırı **`Task 3 identity.decision_units +
identity.canonical_sha`** ile genişler; plan 1168'deki
`test_inventory_rejects_divergent_snapshot_hash` Task 9'dan ÇIKAR. **Task 10** — Produces
listesine `check_snapshot_agreement` EKLENİR (plan 1184-1187).

**Kanıt testi · sahibi:**
- `test_validate_report_returns_parsed_inventory_on_success` (pozitif kontrol) ·
  `test_invalid_report_yields_none_object_with_errors` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`. (Mevcut K-100 testleri plan 1165-1169 aynen kalır,
  yalnız dönüş tipine göre okunur.)
- `test_inventory_rejects_divergent_snapshot_hash` — **YENİ sahip: Task 10**,
  `tests/test_auditor_orchestration.py`.
- `test_round_rejects_report_snapshot_differing_from_packet` — **Sahip: Task 10**.

---

## R7 — Yalnız-bulgu üreten fonksiyona UYGULAMA iddiası test edilemez; her bulgu sınıfının bir tüketicisi olur

**Kusur (plan satırları):** Task 12 `run_checks`'i **saf bulgu üreticisi** olarak bağlıyor
ve bunun kapısı olarak `test_run_checks_never_returns_a_run_outcome` testini koyuyor
(plan 1337 · 1342 · 1381); aynı Step 1 listesinde ise **uygulama/uygulanmama** iddia eden
testler duruyor (plan 1385 · 1386 · 1393 · 1394 · 1395). İkisi aynı anda doğru olamaz.
Ayrıca `acik_soru` bulgusu (plan 1393, `test_readd_conflict_emits_acik_soru_finding`)
Task 13'ün dönüşüm listesinde (plan 1484-1490) **hiçbir tüketiciye** sahip değil.

**Kanonik dayanak (spec girdisi, satır 1187 kontrol tablosu — spec'e ÜSTÜNDÜR):**
*"`guncelle` ve `cikar` kararları denetçi satırı veya doğrulanmış URL referansı taşımalı;
**kanıt yoksa karar uygulanmaz, kalıp korunur**"*. "Uygulanmaz/korunur" bir **uygulama**
semantiğidir; uygulamayı yapan `decide`'dır, `run_checks` değil.

**Kural (kontrolör):** uygulama/uygulanmama testleri Task 13'e taşınır; `acik_soru`
bulgusuna `decide`'da açık bir tüketici verilir ve K-71 gereği açık soru aktivasyonu
BLOKLAR — sonuç `blocked`'tır.

**Bağlayıcı sözleşme:**

```python
# engine.py  (Task 12) — BULGU sınıfları, küme KAPALI
BULGU_SINIFLARI: tuple[str, ...] = (
    "kapsam_ihlali",
    "mevzuat_uyusmazligi",
    "mevzuat_dogrulanamadi",
    "regresyon_kapisi",
    "ikinci_aktif",
    "acik_soru",
)
```

`decide`'ın (Task 13) dönüşüm tablosu — **altı sınıfın altısı da tüketilir**:

| Bulgu | `decide` sonucu | Koşul |
|---|---|---|
| `kapsam_ihlali` | `blocked` | her zaman (plan 1484) |
| `mevzuat_uyusmazligi` | `blocked` | her zaman — K-125 benimsendi (plan 1485) |
| `mevzuat_dogrulanamadi` | `blocked` | YALNIZ `config.block_on_legislation is True`; varsayılan `False` (plan 1486-1487) |
| `regresyon_kapisi` | `activation_eligible` OLAMAZ | plan 1488 |
| `ikinci_aktif` | `blocked` | plan 1489 |
| **`acik_soru`** | **`blocked`, `sebep="acik-soru-var"`** | **YENİ** — bulgu VARSA ya da `inputs.sentez.acik_sorular` boş DEĞİLSE. K-71 gereği açık soru aktivasyonu bloklar (plan 94 · 1450-1451) |

Sınır (plan 1448-1449 aynen geçerli): K-23=B kararsızları **bloklamaz** — `kararsizlar`
listesine girer, `policy_report`'a yazılır. Açık soru yolu ondan AYRIDIR.

**Taşınan testler (Task 12 → Task 13, `tests/test_policy_engine_outcome.py`):**

| Test | Plan satırı | Neden taşınıyor |
|---|---|---|
| `test_guncelle_without_evidence_is_not_applied` | 1385 | "uygulanmaz" = uygulama semantiği |
| `test_cikar_without_two_auditor_agreement_keeps_pattern` | 1386 | "korunur" = uygulama semantiği (preflight listesinde adı geçmiyor, sınıfı aynı) |
| `test_flag_consumption_applied` | 1393 | "applied" |
| `test_new_item_needs_two_of_three` | 1393 | aday öğenin pakete GİRİP girmediği |
| `test_category_conflict_package_type_wins` | 1394 | hangi değerin nihai adaya yazıldığı |
| `test_unmatched_holiday_key_not_written` | 1395 | "not_written" |

Task 12'de KALAN: `test_readd_conflict_emits_acik_soru_finding` (plan 1393) — konusu
bulgunun ÜRETİLMESİDİR. Task 13'e YENİ eklenen tüketici testi:
`test_acik_soru_finding_becomes_blocked` + `test_synthesis_open_questions_become_blocked`
(iki kaynak da aynı sonuca çıkar).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 12** — plan 1385 · 1386 · 1393 ·
1394 · 1395 listeden ÇIKAR; `BULGU_SINIFLARI` Produces'a EKLENİR. **Task 13** — plan
1484-1490 dönüşüm listesi `acik_soru` satırıyla genişler.

**Kanıt testi · sahibi:** yukarıdaki tabloların tamamı; `test_acik_soru_finding_becomes_blocked`
ve `test_finding_classes_all_have_a_consumer` (yapısal: `BULGU_SINIFLARI`'nın her değeri
`decide`'ın dönüşüm tablosunda geçer) — **Sahip: Task 13**,
`tests/test_policy_engine_outcome.py`.

---

## R8 — Kanıt veritabanından OKUNUR, çağırandan alınmaz. İKİNCİ bir kurucu yoktur

**Kusur (plan satırları):** (a) Task 14 `Consumes: Task 13 EngineResult` (plan 1505) diyor,
oysa gövdesi her şeyi `load_verified_run`'dan **basıyor** (plan 1507-1512) ve planın kendi
doktrini kanıtın çağırandan alınmasını yasaklıyor (plan 301-307); Consumes ayrıca gerçekten
kullandığı yüzeyi (`runs.load_verified_run`) hiç saymıyor. (b) `approval.to_activation_evidence(
snapshot: dict) -> ActivationGateEvidence` (plan 1520-1523) **çağıranın verdiği bir sözlükten**
kanıt üreten İKİNCİ bir kurucudur — planın "TEK KAPI LİSTESİ" bölümünün (plan 316-341)
*"yolu yok"* dediği deliği tam olarak yeniden açar. Ölçüldü
(`sector_package_lifecycle.py:133-145`): `_require_evidence` yalnız SINIFI doğrular, kanıtın
KÖKENİNİ değil — yani uydurulmuş bir sözlükten kurulan kanıt kapıdan geçerdi.

**Kural (kontrolör):** `to_activation_evidence` TAMAMEN SİLİNİR. Tek kurulum yeri
aktivasyon yolunun içidir ve kilitli doğrulanmış koşudan kurulur. Task 14'ün Consumes satırı
düzeltilir. Yapısal test, kanıt tipinin yaşam döngüsü/aktivasyon yolu dışında hiçbir modülde
kurulmadığını kanıtlar.

**Bağlayıcı sözleşme:**

```python
# approval.py  (Task 14)
# approval.to_activation_evidence  →  SİLİNDİ. Modülde ActivationGateEvidence KURULMAZ,
# import bile edilmez.
```

```python
# writeback.py  (Task 15) — TEK kurulum yeri
async def activate_from_snapshot(db, *, run_id: str, actor: str) -> None:
    """`ActivationGateEvidence` YALNIZ burada kurulur; alanlarının HEPSİ kilitli
    `VerifiedRun`'dan ve kilitli taslak satırından okunur:

        activation_eligible = (run.sonuc == "activation_eligible")
        open_questions_count = len(run.approval_snapshot["acik_sorular"])
        katman1_passed       = run.katman1_attestation["sonuc"] == "PASS"
        checklist_approved   = run.readiness_attestation["onaylandi"] is True
        expected_active_version / expected_no_active  = K-94 taban durumu (plan 1643-1645)

    Hiçbir alan parametreden gelmez; fonksiyonun imzasında `evidence`, `snapshot`
    ya da herhangi bir `dict` parametresi YOKTUR."""
```

Task 14'ün düzeltilmiş Consumes satırı:

> `Consumes: Task 8 runs.load_verified_run (+ VerifiedRun); Task 6 sector_package_runs;
> package_events.log_package_event.` — `Task 13 EngineResult` **ÇIKARILDI**: Task 14 motor
> sonucunu nesne olarak DEĞİL, koşu satırından okur.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 14** — plan 1505 (Consumes) ve plan
1520-1523 (`to_activation_evidence`) GEÇERSİZ. **Task 15** — plan 1627-1642'nin F18
zinciri aynen geçerli, üstüne "tek kurulum yeri" hükmü EKLENİR.

**Kanıt testi · sahibi:**
- `test_no_module_constructs_activation_evidence_outside_writeback` — depo geneli yapısal
  tarama: `ActivationGateEvidence(` çağrısı YALNIZ `writeback.py`'de bulunur; tanım dosyası
  (`sector_package_lifecycle.py`) ve `tests/` dizini **açıkça muaftır** (muafiyet testin
  içinde yazılıdır). **Sahip: Task 15**, `tests/test_write_surface_authorization.py`.
- `test_approval_module_exposes_no_evidence_constructor` — `approval` modülünde
  `to_activation_evidence` adı YOK ve `ActivationGateEvidence` import EDİLMİYOR.
  **Sahip: Task 14**, `tests/test_approval_surface.py`.

---

## R9 — Bir görev, SONRAKİ görevde doğan yüzeyi tüketemez

**Kusur (plan satırları):** Task 15'in aktivasyonu `readiness_attestation`'ı doğruluyor
(plan 1635 · 1686), ama o alanın tek üreticisi `readiness.attest` **Task 17'de** doğuyor
(plan 1852-1854). Task 15'in pozitif kontrolü
`test_activation_succeeds_with_full_attestation_chain` (plan 1689) bu yüzden **yazıcısız**:
Task 15 kendi sırasında tamamlanamaz. Bu, planın `hazirlik-onayla` komutu için zaten
kapattığını söylediği sınıfın (plan 1848-1851) süpürülmemiş kardeşidir.

**Kural (kontrolör):** **YAZICI Task 15'in kapsamına taşınır.** Task 17 yirmi maddelik
listenin değerlendirmesini ve CLI alt komutunu TUTAR.

**Bağlayıcı sözleşme — TAŞINAN yüzey:**

```python
# runs.py  (Task 8'de doğar, Task 15 MODIFY eder) — attest_katman1/attest_katman2'nin kardeşi
async def attest_readiness(
    db,
    *,
    run_id: str,
    onaylandi: bool,
    kapi_maddeleri: tuple[str, ...],      # `kapi` sınıfındaki madde kimlikleri (K-69)
    sinyal_maddeleri: tuple[str, ...],    # `sinyal` sınıfındakiler — tamamlanma kapısına GİRMEZ
    actor: str,
) -> None:
    """F18: operatörün TEK onayını koşu satırının `readiness_attestation` alanına kalıcı
    yazar (kim · ne zaman · hangi maddeler). Aktivasyon bu kaydı okur; boolean uydurulamaz."""
```

- Parametreler **ilkel tiplerdir**, `ReadinessReport` DEĞİL: `ReadinessReport` Task 17'de
  doğar ve Task 15'in ona bağımlı olması bağımlılığı yine ters çevirirdi.
- `activate_from_snapshot` (Task 15) `readiness_attestation["onaylandi"] is True` arar;
  eksik ya da `False` → aktivasyon REDDEDİLİR.

**KALAN yüzeyler (Task 17, değişmez):** `readiness.CHECKLIST: tuple[Item, ...]` (plan 1845) ·
`readiness.evaluate(db) -> ReadinessReport` (plan 1846) · `kapi`/`sinyal` sınıflandırması
(plan 1863-1868 · 1874-1878) · CLI alt komutu **`hazirlik-onayla`** (plan 1847-1851) — komut
`readiness.evaluate`'i çağırır, operatörün TEK onayını alır ve **`runs.attest_readiness`**'e
yazdırır.

**SİLİNEN yüzey:** `readiness.attest(db, *, run_id, report, actor)` (plan 1852-1854) —
YOKTUR; yerine `runs.attest_readiness` geçer.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 15** — Files listesine
`Modify: apps/social/backend/app/services/sector_pipeline/runs.py` EKLENİR (plan 1576-1587).
**Task 17** — plan 1852-1854 GEÇERSİZ; Produces listesinden çıkar, Step 3b'nin komut testi
aynen kalır ama tasdik yazıcısı olarak `runs.attest_readiness` çağrılır.

**Kanıt testi · sahibi:**
- `test_attest_readiness_persists_actor_time_and_items` (F18 üretici testi — plan 1878'deki
  `test_attest_persists_actor_and_time` bu ada ve **Task 15**'e taşınır),
  `tests/test_pipeline_writeback.py`.
- `test_activation_succeeds_with_full_attestation_chain` (plan 1689) artık yazıcısı olan bir
  pozitif kontroldür — **Sahip: Task 15** (değişmedi).
- `test_hazirlik_onayla_writes_attestation` (plan 1893) — **Sahip: Task 17** (değişmedi;
  yalnız çağırdığı yüzeyin adı `runs.attest_readiness` olur).

---

## R10 — Operatörün koşmak zorunda olduğu her adımın CLI girişi olur

**Kusur (plan satırları):** kanonik sıra ve Task 19 Step 9 (plan 2021) **yazım kapısını**
koşmayı şart koşuyor, ama Task 16'nın alt komut listesinde (plan 1737-1753) taslak yazımını
ya da K-106 yerinde güncellemeyi çağıran hiçbir komut yok. `writeback.write_draft_from_run`
ve `update_draft_from_run` (plan 1593-1594) operatör tarafından ERİŞİLEMEZ.

**Kural (kontrolör):** eksik alt komutlar eklenir.

**Bağlayıcı sözleşme — Task 16 alt komut listesine EKLENEN:**

| Alt komut | Çağırdığı servis yüzeyi | Not |
|---|---|---|
| `yazim` | `writeback.write_draft_from_run(db, run_id=…, actor=…) -> UUID` | Yazım kapısı; düzeltme koşusunu REDDEDER (plan 1616-1618) |
| `duzeltme-yaz` | `writeback.update_draft_from_run(db, run_id=…, actor=…) -> None` | K-106 yerinde güncelleme; soyağacı ZORUNLU (plan 1618-1620) |
| `deaktive-et` | `sector_package_lifecycle.deactivate_package(db, package_id=…, actor=…)` | R11 — `hedefsiz` satırın TEK çıkışı (K-38) |

Üçü de Task 16'nın genel invariantına tabidir: resmî koşu başlatan her alt komut ilk iş
olarak `contracts.require_pin` çağırır (plan 1759-1760); argparse · açık `--database-url` ·
deterministik çıktı · anlamlı çıkış kodu (plan 1755-1756).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 16** — plan 1737-1753'teki liste üç
komutla genişler. **Task 19** — Step 9 (plan 2021) artık adı konmuş bir komuta işaret eder.

**Kanıt testi · sahibi:**
- `test_yazim_subcommand_calls_write_draft_from_run` ·
  `test_yazim_subcommand_refuses_correction_run` ·
  `test_duzeltme_yaz_subcommand_calls_update_draft_from_run` ·
  `test_deaktive_et_subcommand_calls_deactivate_package` ·
  `test_every_run_subcommand_requires_pin` (plan 1784 — yeni üç komut da kapsam içindedir)
  — **Sahip: Task 16**, `tests/test_pipeline_cli.py`.

---

## R11 — Geri alma kanıtının üreticisi olur; beyan edilen çıkışın komutu olur

**Kusur (plan satırları):** (a) `rollback_package(db, *, sector_id, to_version, evidence:
RollbackGateEvidence, actor)` (plan 263) iki boolean isteyen bir kanıt sınıfı taşıyor —
ölçüldü (`sector_package_lifecycle.py:118-131`): `RollbackGateEvidence(manager_approved: bool,
katman1_passed: bool)`, ikisi de `bool` olmak ZORUNDA ve `_require_evidence` yalnız SINIFI
doğruluyor. `execute_rollback_plan` (plan 1044-1049) ve CLI `olay-geri-al` (plan 1747-1752)
bu iki boolean'ı **uydurmak** zorunda kalırdı — F18'in aktivasyon yolunda kapattığı deliğin
kardeş yolda süpürülmemiş hâli. (b) `hedefsiz` satırın plan metninde yazılı TEK çıkışı
deaktivasyondur (plan 1042-1043) ama CLI listesinde (plan 1737-1753) deaktivasyon komutu
YOK.

**Kural (kontrolör):** geri alma kanıtını **veritabanından** kuran bir üretici adlandırılır —
kilitli koşu + kayıtlı yönetici onayı; çağıran-taraflı boolean ASLA. Deaktivasyon alt komutu
eklenir (R10'daki `deaktive-et`).

**Bağlayıcı sözleşme:**

```python
# runs.py  (Task 8)
class RollbackEvidenceUnavailable(RuntimeError):
    """Kanıt DB'den KURULAMADI — geri alma satırı `hata` olarak kapanır.
    Uydurulmuş boolean ile geçiş YOLU YOKTUR."""

async def build_rollback_evidence(
    db,
    *,
    incident_id: str,
    package_id: UUID,
) -> RollbackGateEvidence:
    """İki alanı da OKUR, hiçbirini kabul etmez:

    manager_approved — bu olay kimliği için kayıtlı yönetici onayı VAR MI (bkz. AÇIK-1;
        kayıt yüzeyi kapanana kadar üretici tek noktadan okur ve tek noktada değişir).
        Kayıt yoksa manager_approved üretilemez → RollbackEvidenceUnavailable.

    katman1_passed — plan satırının HEDEF sürümünü (`target_version`) üreten koşunun
        `katman1_attestation["sonuc"] == "PASS"` kaydı. Hedef paketin `run_id` bağı yoksa,
        koşu satırı yoksa, `durum != 'tamamlandi'` ise ya da tasdik yoksa
        → RollbackEvidenceUnavailable (F18: tasdik kanıttır, boolean değil).
    """
```

- `execute_rollback_plan` (plan 1044-1049) her paket için ÖNCE `build_rollback_evidence`
  çağırır; `RollbackEvidenceUnavailable` yakalanır ve o plan satırı **`durum='hata'`**
  (036'nın mevcut kapalı kümesinden — plan 769) + `reason` ile kapanır. **Yeni durum değeri
  ÜRETİLMEZ**; `hedefsiz` bu vaka için KULLANILMAZ (`hedefsiz` yalnız güvenli sürüm yokluğu
  demektir, plan 1042).
- `hedefsiz` satırların tek çıkışı `deaktive-et` alt komutudur (R10 tablosu); `olay-geri-al`
  onları ayrı başlıkta raporlar (plan 1748-1750) ve **kendiliğinden deaktive ETMEZ** —
  deaktivasyon operatörün ayrı kararıdır (K-38).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — Produces listesine
`build_rollback_evidence` + `RollbackEvidenceUnavailable` EKLENİR (plan 1044-1049 civarı);
`execute_rollback_plan`'ın gövde sözleşmesi bağlanır. **Task 16** — `deaktive-et` eklenir
(plan 1737-1753). **Plan 1 arayüzü DEĞİŞMEZ**: `RollbackGateEvidence` alan kümesine
dokunulmaz (ölçüldü, `sector_package_lifecycle.py:118-131`).

**Kanıt testi · sahibi:**
- `test_build_rollback_evidence_reads_manager_approval_from_db` ·
  `test_build_rollback_evidence_reads_katman1_from_target_run_attestation` ·
  `test_build_rollback_evidence_refuses_when_target_run_unprovable` ·
  `test_executor_marks_row_hata_when_evidence_unavailable` ·
  `test_executor_never_constructs_evidence_from_literals` (yapısal: `runs.py` içinde
  `RollbackGateEvidence(` çağrısı YALNIZ `build_rollback_evidence` gövdesinde)
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_deaktive_et_subcommand_calls_deactivate_package` ·
  `test_olay_geri_al_does_not_auto_deactivate_hedefsiz` — **Sahip: Task 16**,
  `tests/test_pipeline_cli.py`.

---

## R12 — Beyan edilen her dosya değişikliğinin onu YAPAN bir adımı olur

Üç ayrı vaka; her biri için karar ayrı verilir.

### R12(a) — Task 20: beyan DÜZELTİLİR

**Kusur:** Task 20 Files satırı `test_plan2_interface_contract.py` için *"(genişletilir)"*
diyor (plan 2042) ama Step 1-7'nin (plan 2044-2068) hiçbiri onu genişletmiyor.

**Karar: BEYAN DÜZELTİLİR** (adım eklenmez). Dosyanın Plan 2 satırlarının sahibi zaten
Task 3 (plan 481 · 581-583) ve Task 15'tir (plan 1582 · 1707-1710); Task 20 onu yalnız
**koşar** (Step 1'in tam suite'i içinde). Kapanış görevine yeni sözleşme satırı yazdırmak
kapsam eklemek olurdu.

Düzeltilmiş Files satırı:

> `- Test: apps/social/backend/tests/test_plan2_interface_contract.py` **(yalnız koşulur —
> satırlarının sahibi Task 3 ve Task 15)**

**Geçersiz kılınan satır:** plan 2042.

### R12(b) — Task 5: ADIM EKLENİR

**Kusur:** Task 5 `shared/n8n-workflows/turkey-calendar-update.json`'ı değiştiriyor
(plan 653) ama bu workflow mevcut sözleşme testlerinden HİÇ geçmiyor; Task 16 Step 7b
(plan 1815-1821) aynı üçlüyü **yalnız yeni hata-bildirimi workflow'u** için ekliyor.
Ölçüldü (`tests/test_notifications.py:818 · 838 · 855`): `test_workflow_reads_no_process_env` ·
`test_workflow_carries_a_stable_id` · `test_workflow_credentials_are_bound` üçü de
`_admin_workflow()` üzerinde koşuyor — takvim workflow'u kapsam DIŞI.

**Karar: TASK 5'E ADIM EKLENİR.**

> - [ ] **Step 4b:** Değiştirilmiş takvim workflow'unu mevcut sözleşme testlerine SOK —
>   `tests/test_notifications.py`'a aynı üçlü: `test_calendar_workflow_carries_stable_id` ·
>   `test_calendar_workflow_reads_no_process_env` ·
>   `test_calendar_workflow_credentials_are_bound`. Koş:
>   `cd apps/social/backend && python -m pytest tests/test_notifications.py -v`
>   — Beklenen: PASS. Gerekçe ölçülü: canlı kurulumda `$env` kapalı ve import sabit kimlik
>   istiyor ([[decisions/2026-08-26-n8n-credential-over-env]]).

**Etkilenen görev:** Task 5 — Files listesine
`Modify: apps/social/backend/tests/test_notifications.py` EKLENİR (plan 650-654).
**Kanıt testi · sahibi:** üç test, **Task 5**.

### R12(c) — Task 2: `_SABLON.md` beyanı DOĞRUDUR, kalemin İNİŞ YERİ yazılır

**Kusur:** Task 2 `_SABLON.md`'yi Modify diye sayıyor (plan 431) ama altı düzeltmenin ve
yedi sweep kaleminin hiçbiri oraya indiğini SÖYLEMİYOR (plan 439-457).

**Ölçüm (2026-08-30, dış depo):** `_SABLON.md:49-51` · `hakem-sentez-gorevi.md:78` ·
`hakem-denetci-gorevi.md:74` — üçü de serbest `[kanal-bağımlı: X]` etiketini taşıyor.
Yani 6. düzeltme kalemi (kanal anahtar uzayının dört değerle KAPATILMASI, plan 447-450)
**üç dosyaya birden** iner ve `_SABLON.md` beyanı DOĞRUDUR.

**Karar: BEYAN KORUNUR, kalem 6 iniş yerlerini AÇIKÇA yazar.** Düzeltilmiş kalem metni:

> 6. **Kanal anahtar uzayı dört değerle KAPATILIR** — `whatsapp_hatti` · `fiziksel_magaza` ·
>    `randevu_sistemi` · `eticaret_sitesi`. **İniş yerleri (ölçüldü 2026-08-30):**
>    `_SABLON.md:49-51` · `hakem-sentez-gorevi.md:78` · `hakem-denetci-gorevi.md:74` —
>    üçünde de serbest `X` yer alıyor. Kod tarafı Plan 1'de
>    `sector_packages.py::CHANNEL_KEYS` olarak zaten kapalı; sözleşme ona hizalanır.

**Geçersiz kılınan satırlar:** plan 447-450. **Kanıt:** Task 2 Step 1/Step 3 sweep raporunun
6. kalemi artık üç dosya + satır işaretiyle ölçülür (test değil, ölçülmüş rapor kalemi —
dürüst etiket).

---

## R13 — Ölçüm adımının sonucu ÖNCEDEN KARARLAŞTIRILMIŞ olamaz

**Kusur (plan satırları):** Task 5 Step 1 (plan 695-697) K-112 için *"Bulguya göre Task
12'nin özel gün kontrolü hizalanır. Ölçmeden bağlama"* diyor; oysa Task 12 aynı davranışı
ZATEN bağlıyor (plan 233 · 1320-1330): üretim yolunda sessiz düşüş + zorunlu maskeli log,
yazım kapısında tipli hata ile fail-closed.

**Kural (kontrolör):** **BAĞLAMA KALIR** — spec türevidir, ölçüm türevi değildir. Task 5'in
adımı dürüst şekilde yeniden adlandırılır: bugünkü davranışı, hata-enjeksiyon testinin karşı
koşacağı **regresyon TABANI** olarak kaydeder.

**Bağlayıcı sözleşme — Task 5 Step 1'in YENİ metni (plan 695-697'nin yerine):**

> - [ ] **Step 1:** **BUGÜNKÜ DAVRANIŞI KAYDET (K-112 regresyon tabanı — bağlama DEĞİL):**
>   takvim erişilemezken (a) özel gün enjeksiyon yolunun ve (b)
>   `sector_package_lifecycle.insert_draft`'ın bugün ne yaptığını fixture ile ölç; sonucu
>   `docs/research/2026-08-27-k112-takvim-erisilemezlik-taban.md`'ye yaz — komut + taze çıktı
>   ile (İlke 9). **Bu adım hiçbir davranışı BAĞLAMAZ ve Task 12'nin bağladığı davranışı
>   değiştirmez** (plan 221-233 · 1320-1330: bağlama spec §11/§3.4 türevidir). Ölçümün tek
>   işlevi, Task 12'nin hata-enjeksiyon testlerinin karşı koşacağı tabanı vermektir. Ölçülen
>   davranış bağlanan davranıştan farklı çıkarsa bu bir REGRESYON DEĞİL, planın istediği
>   değişikliktir ve taban notunda öyle etiketlenir.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 5** — plan 695-697 GEÇERSİZ.
**Task 12** — plan 1320-1330 ve plan 1397-1400'deki üç K-112 testi AYNEN geçerli; bağlama
onlarındır.

**Kanıt testi · sahibi:** yeni test yok. Kapıyı kanıtlayan testler Task 12'nindir:
`test_calendar_unavailable_yields_empty_special_day_context_and_logs` ·
`test_calendar_unavailable_fails_draft_write_closed` ·
`test_calendar_unavailable_log_is_masked` (plan 1397-1400). Task 5'in çıktısı ölçülmüş bir
taban notudur, kapı değildir.

---

## R14 — Pin'in negatif invariantının sözleşme testi

Bu hüküm **R1'e katlanır** ve burada bir kez daha yazılmaz: negatif invariantın metni
(*"kirli çalışma ağacı tek başına pini düşürmez"*), onu kanıtlayan test
(`test_verify_passes_with_dirty_external_worktree`, **Sahip: Task 1**) ve commit yolunu
kapatan kalem (`kosu/` → dış depo `.gitignore`,
`test_external_repo_gitignores_run_folder`, **Sahip: Task 2**) R1'de tam metinle bağlanmıştır.

Tek ek hüküm — **çift kayıt yasağı:** aynı invariant için ikinci bir test yazılmaz ve
`verify_pin`'in kapı kümesi (plan 403-406, DÖRT kapı) **genişletilmez**; negatif invariant
bir kapı değil, kapı kümesinin **kapalılığının** ifadesidir.

---

## AÇIK-1 KAPANDI — kontrolör kararı, 2026-08-30

**Karar: B seçeneği, olay düzeyinde onay.** `social.package_rollback_plans` iki kolon kazanır:

```sql
onay_actor   text        NULL,   -- onayı veren yönetici kimliği
onaylandi_at timestamptz NULL,   -- onay zamanı
CONSTRAINT package_rollback_plans_onay_butun
  CHECK ((onay_actor IS NULL) = (onaylandi_at IS NULL))   -- ikisi birlikte dolar, birlikte boşalır
```

**Gerekçe — kanonik kayıt seçeneği C'yi zaten eliyor.** Spec girdisi satır 1409 geri alma
kararını *"yöneticiye/operatöre"* verir ve satır 1977 aktivasyon/geri alma olayının
kaydedilmesini **her katmanda ortak, açık-olmayan yükümlülük** sayar. "Komutu çalıştırmak
onaydır" bu yüzden yol değildir: kaydı olmayan onay, R11'in yasakladığı uydurulmuş
boolean'ın adı değişmiş hâlidir.

**Neden A değil B.** Outbox (`social.admin_events`) bir bildirim kuyruğudur; onay deposu
yapılırsa (a) yürütücü, zaten KİLİTLEDİĞİ plan satırının yanında ikinci bir tabloyu okumak
zorunda kalır — kanıt kurulumu artık tek satırdan atomik değildir; (b) kuyruk kaydının
yaşam döngüsü (tüketim, budama) onay kaydının yaşam döngüsünden farklıdır ve onayı bir
temizlik işi sessizce yok edebilir. Onay, onayladığı planın yanında durur.

**Maliyet ölçüldü ve SIFIRA yakın:** Task 6 henüz uygulanmadı (migration 036 yazılmadı,
ölçüldü — `shared/db/migrations/` en yüksek numara 034). İki nullable kolon + bir CHECK
şimdi ücretsizdir; karar Task 6'dan SONRA verilseydi migration 037 gerekirdi.

**Granülerlik — onay OLAY düzeyindedir, paket düzeyinde DEĞİL.** K-145 bir kural sürümünün
etkilediği TÜM paketleri geri alır; paket başına ayrı onay istemek tek operatörlü işletimde
(K-54 · K-77) taşınamaz bir yüktür ve K-153'ün operasyon-yükü kaygısını doğrudan büyütür.
Bu yüzden:

```python
# sector_pipeline_cli.py  (Task 16) — yeni alt komut
#   olay-onayla --incident-id <id> --actor <kimlik>
# runs.py  (Task 8)
async def approve_incident_rollback(db, *, incident_id: str, actor: str) -> int:
    """O olay kimliğine ait BEKLEYEN plan satırlarının TAMAMINI tek işlemde damgalar
    (`onay_actor`, `onaylandi_at`); damgalanan satır sayısını döner.

    - `durum='bekliyor'` OLMAYAN satırlar damgalanmaz (tamamlanmış/hatalı/hedefsiz iş
      geriye dönük onaylanamaz).
    - Zaten damgalı satır TEKRAR damgalanmaz — ilk onay korunur (idempotent).
    - Hiç satır damgalanmadıysa 0 döner; çağıran bunu hata olarak raporlar.
    """
```

Böylece operatör TEK komut çalıştırır, N satır damgalanır, ve yürütücünün satır-başına
okuması yerel ve atomik kalır.

**`build_rollback_evidence`'ın `manager_approved` ayağı bağlanır:** kilitli plan satırının
`onay_actor` **ve** `onaylandi_at` alanları dolu ise `True`; biri boşsa
`RollbackEvidenceUnavailable` (uydurma YOK). Alan `bool`'a çevrilirken herhangi bir
varsayılan/`.get` düşüşü KULLANILMAZ.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 6** — `package_rollback_plans`
şemasına iki kolon + bir CHECK (plan 767-772'yi genişletir). **Task 8** —
`approve_incident_rollback` Produces listesine eklenir; `build_rollback_evidence`'ın
`manager_approved` kaynağı bu kolonlardır. **Task 16** — `olay-onayla` alt komutu eklenir
(plan 1737-1753).

**Kanıt testi · sahibi:**
- `test_rollback_plan_approval_columns_exist_and_nullable` ·
  `test_rollback_plan_approval_check_requires_both_or_neither` — **Sahip: Task 6**,
  `tests/test_migration_036.py`.
- `test_approve_incident_stamps_only_bekliyor_rows` ·
  `test_approve_incident_is_idempotent_and_keeps_first_approver` ·
  `test_approve_incident_returns_zero_when_nothing_pending` ·
  `test_build_rollback_evidence_refuses_when_plan_row_unapproved` (negatif kontrol) ·
  `test_build_rollback_evidence_true_only_when_both_approval_fields_set` — **Sahip: Task 8**,
  `tests/test_pipeline_runs.py`.
- `test_olay_onayla_subcommand_stamps_incident` — **Sahip: Task 16**,
  `tests/test_pipeline_cli.py`.

---

## AÇIK — kontrolörün kararı gerekiyor

> **Bu bölümde açık kalem KALMADI.** AÇIK-1 yukarıda kapatıldı; aşağıdaki gövde kararın
> dayanağı olarak korunuyor.

### AÇIK-1 (KAPANDI — yukarıya bakınız): Olay geri alması için yönetici onayı NEREDE kayıtlanır?

**Neden açık:** R11 kanıt üreticisinin *"kayıtlı yönetici onayı"*ndan okumasını bağlıyor,
ama planın hiçbir yerinde bir olay-geri-alma onayını **kaydeden** yüzey yok: `olay-plani`
plan satırlarını yazar (plan 1745-1747), `olay-geri-al` yürütür (plan 1747-1752); arada
kayıtlı bir onay adımı yoktur. Üretici bir yerden okumak zorunda, ve o yerin seçimi maliyet
farkı taşıyor — kendi başıma kapatmıyorum.

| Seçenek | Nasıl | Maliyet / etki |
|---|---|---|
| **A — Outbox kaydı** | Yeni CLI alt komutu `olay-onayla` → `notifications.record_admin_event(kind="sektor_paketi.olay_geri_alma_onayi", idempotency_key=<incident_id>)`; üretici `social.admin_events`'ten okur | Migration DEĞİŞMEZ; mevcut idempotency sözleşmesi yeniden kullanılır. Ama outbox bir **bildirim kuyruğudur**, onay deposu olarak kullanılması amacının biraz dışıdır |
| **B — Plan satırında kolon** | `social.package_rollback_plans`'e `onay_actor text NULL` + `onaylandi_at timestamptz NULL`; `olay-onayla` onları yazar, üretici tek satırdan okur | Anlamsal olarak en temiz (onay, onayladığı planın yanında durur) ve tek-satır okuması atomik. Ama **Task 6'nın migration 036 şemasını değiştirir** (plan 767-772) ve Task 6'nın test listesine iki CHECK testi ekler |
| **C — Onay adımı YOK** | `execute_rollback_plan` yönetici onayını komutun kendisinin çalıştırılmasından sayar | R11'in *"çağıran-taraflı boolean ASLA"* hükmüyle ÇELİŞİR — kaydı olmayan onay, uydurulmuş boolean'ın adı değişmiş hâlidir. Bu yüzden burada yalnız tamlık için sayılıyor |

**Bloklama etkisi:** karar verilene kadar `build_rollback_evidence`'ın `manager_approved`
ayağı tek noktada (fonksiyonun içinde) okunur ve karar kapanınca **yalnız o nokta** değişir;
R11'in geri kalanı (katman1 ayağı, `hata` düşüşü, `deaktive-et` çıkışı) karardan bağımsız
olarak bağlıdır. Karar Task 8 uygulanmadan ÖNCE gerekir; B seçilirse Task 6'dan önce
gerekir.
