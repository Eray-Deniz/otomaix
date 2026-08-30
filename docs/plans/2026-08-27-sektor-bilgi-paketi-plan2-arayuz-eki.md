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

**Alıntı kuralı (fix turu 1, 2026-08-30).** Bu ekteki HER `plan <satır>` · `<dosya>:<satır>` ·
`spec-input satır <n>` alıntısı fix turu 1'de **tek tek yeniden ölçüldü** ve plan gövdesinin
**bu turdaki** hâline göre güncellendi (plan gövdesine bu turda görev-başına "Arayüz eki
bağlar" satırları eklendiği için tüm satır numaraları kaydı). Satır çapası kırılgan olan
yerlerde çapa **sembole · test adına · başlığa** çevrildi (ör.
`sector_package_lifecycle.py::_require_evidence`, `Task 6 Produces → sector_package_runs`).
**Plan gövdesi bir daha düzenlenirse bu numaralar yeniden kayar** — bu bilinen ve kabul
edilen bir sınırdır; kayma riski taşımayan çapa sembol adıdır, satır numarası değildir.

---

## R1 — Koşu klasörleri pinlenen dış depoya ASLA commit edilmez

**Kusur (plan satırları):** `runs.run_folder(run_id) -> <arastirma-deposu>/kosu/<run_id>/`
(plan 1011) her koşunun artefaktını, pin kapısının **commit sha**'sını karşılaştırdığı depoya
(plan 423-426) yazar; Task 18 Step 4 o depoyu sabit bir commit'e getirir (plan 2007), Task 19
klasörü orada yaratır (plan 2034). "Monorepo'ya düzenlenebilir ikinci kopya ALINMAZ"
kısıtı (plan 76-78) ile birlikte okununca plan, klasörün commit edilip edilmeyeceğini
hiç söylemez.

**Ölçüm (2026-08-30, `verify_pin`'in plan metni, plan 423-426):** kapı kümesi TAM OLARAK
dörttür — dosya yok · hash uyuşmuyor · commit uyuşmuyor · depo dizini yok. Çalışma ağacının
temizliği **kontrol edilmez** ve doğrulama açıkça salt-okunurdur (plan 426). Yani izlenmeyen
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

`verify_pin` invariantları — pozitif küme DEĞİŞMEZ (dört kapı, plan 423-426), üstüne
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

**Etkilenen görev · geçersiz kılınan satırlar:** Task 1 (invariant listesi plan 422-426
üzerine EKLENİR) · Task 2 (Files listesine `.gitignore` eklenir; plan 450-455) ·
Task 8 `run_folder` yeri DEĞİŞMEZ (plan 1011 geçerli kalır) · Task 18 Step 4 / Task 19
belirsizliği (plan 2007 · 2034) bu hükümle kapanır.

**Kanıt testi · sahibi:**
- `test_verify_passes_with_dirty_external_worktree` — sahte depoda pinlenen üç dosya
  eşleşiyor, yanında izlenmeyen `kosu/<run_id>/x.md` var → `verify_pin` **boş liste** döner.
  **Sahip: Task 1**, `tests/test_contract_pin.py`.
- `test_external_repo_gitignores_run_folder` — gerçek dış deponun `.gitignore`'u `kosu/`
  satırını taşır. **Sahip: Task 2**, `tests/test_contract_pin.py` (Step 5'te eklenir).

---

## R2 — Her NOT NULL kolonun ve her kapı kolonunun ADI KONMUŞ bir üreticisi olur

**Kusur (plan satırları):** (a) `kosu_turu text NOT NULL` (plan 793) ama
`open_run(db, *, sector_id, run_id, parent_run_id=None)` (plan 986) böyle bir parametre
taşımıyor; (b) `durum='tamamlandi'`, `load_verified_run`'ın **1. kapısıdır** (plan 341) ama
onu yazan bir üretici yok; (c) `engine_version` · `engine_config_sha` · `content_sha` ·
`decision_log_sha` · `policy_report` · `engine_diff` koşu satırına yalnız isimsiz
`**report_fields` üzerinden ulaşıyor (plan 1001-1002). Bu, planın `barrier_report` için
zaten uyguladığı düzeltmenin (plan 1003-1007) kardeşlerine **süpürülmemiş** hâlidir.
(d) `engine_version`/`engine_config_sha` `load_verified_run`'ın 3. ve 4. kapısı ve
`affected_packages`'ın kapalı dörtlüsünün yarısı (plan 341-344 · 1024-1029) olmasına rağmen
`EngineResult`'ta YOK (plan 1469-1471) ve `engine_config_sha`'yı (K-97) hesaplayan yer
adlandırılmamış. **(e) Fix turu 1 bulgusu (yüksek, KABUL):** `record_result` HER sonuçta
`policy_report` istiyor (Task 6 Produces → `sector_package_runs.policy_report jsonb`, K-95),
oysa `EngineResult` yalnız `kararsizlar` taşıyor (plan 1469-1471) ve `policy_report`'u ÜRETEN
bir **tip ya da fonksiyon hiçbir görevde adlandırılmamış**. Bu, R2'nin kapatmak için var
olduğu **isimsiz-üretici** sınıfının ta kendisidir: Task 16'nın motor çağırıcısı serbest bir
sözlük İCAT etmek zorunda kalırdı ve iki görev ayrışırdı.

**Kural (kontrolör):** `open_run` zorunlu `kosu_turu` parametresi kazanır (kapalı küme).
`record_result` **yazdığı HER alanı adı konmuş, tipi kapalı bir kaynaktan** alır ve
`**report_fields` SİLİNİR: motor türevi alanların TAMAMI tek bir `EngineResult`
parametresinden gelir, serbest sözlük hiçbir yerde kalmaz. `durum='tamamlandi'`'yi yazan
`record_result`'tır — açıkça yazılır. `engine_version` + `engine_config_sha`
`EngineResult`'a eklenir; hesaplandıkları yer adlandırılır. **`policy_report` KAPALI bir
tip kazanır (`PolicyReport`), tek üreticisi `decide`'dır ve `record_result` onu
`EngineResult`'tan OKUR — ayrı bir parametre olarak KABUL ETMEZ.** `kararsizlar`
`EngineResult`'tan ÇIKAR; tek yeri `policy_report.kararsizlar`'dır (iki kaynak yasağı).

**Bağlayıcı sözleşme:**

```python
# runs.py  (Task 8)
KOSU_TURLERI: tuple[str, ...] = ("ilk", "periyodik", "duzeltme")     # KAPALI
DURUMLAR:    tuple[str, ...] = ("calisiyor", "tamamlandi", "tamamlanmadi")  # KAPALI
# SONUCLAR burada TANIMLANMAZ: motor sözleşmesine aittir ve `engine_contract.py`'de
# (yine Task 8) durur — aşağıya bakınız. `runs.py` onu import eder, ikinci kopya YOKTUR.

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
  gerektirir (036 CHECK, plan 847-848) ve onu yalnız `open_correction_run` yazar.
- `parent_run_id` DOLU ise (yeniden koşum, K-83) satır ana koşudan **`kosu_turu` ·
  `duzeltilen_run_id` · `package_id` üçlüsünü DEVRALIR** (plan 855-857 devralma hükmü);
  açıkça verilen `kosu_turu` ana koşununkinden farklıysa çağrı REDDEDİLİR.

```python
# runs.py  (Task 8)
async def record_result(
    db,
    *,
    run_id: str,
    result: EngineResult,            # Task 13'ün KAPALI tipi — TEK motor-türevi girdi
) -> None: ...
```

- **`**report_fields` YOKTUR.** Fonksiyonun imzasında hiçbir `*args`/`**kwargs` bulunmaz.
- **Serbest sözlük parametresi de YOKTUR.** İlk yazım on iki alanı tek tek sayıyordu; o
  biçim `policy_report: dict` gibi **tipi olmayan** bir alanı imzada meşrulaştırıyordu —
  yani isimsiz-üretici deliği parametre adı kazanmış hâlde duruyordu. Bağlanan hüküm:
  koşu satırına yazılan HER motor-türevi kolon, `EngineResult`'ın **adı konmuş ve kapalı**
  bir alanından okunur. Alanın sessizce düşmesi artık imza sorunu değil, **alan-kümesi
  testi** sorunudur ve o test aşağıda adıyla sabittir.
- **Eşleme BİREBİRDİR (on bir alan → on bir kolon):** `sonuc` · `sebep` · `engine_version` ·
  `engine_config_sha` · `policy_report` · `barrier_report` · `engine_diff` ·
  `final_candidate` · `final_decision_log` · `content_sha` · `decision_log_sha`.
  `EngineResult`'ta bulunup koşu satırına yazılmayan alan YOKTUR; koşu satırında bulunup
  `EngineResult`'tan gelmeyen motor-türevi kolon da YOKTUR.
- **`record_result` aynı ifadede `durum='tamamlandi'` yazar.** `load_verified_run`'ın
  1. kapısını (plan 341) sağlanabilir kılan tek üretici budur.
- `result.sonuc == 'activation_eligible'` iken `final_candidate` · `final_decision_log` ·
  `content_sha` · `decision_log_sha` DÖRDÜ de dolu olmak ZORUNDADIR; biri eksikse yazım
  REDDEDİLİR (plan 1009-1010 F19 hükmü). Diğer iki sonuçta bu dördü `None` olabilir;
  `engine_version` · `engine_config_sha` · `policy_report` · `barrier_report` üç sonuçta da
  ZORUNLUDUR — `policy_report` en kötü hâlde **boş demetli** bir `PolicyReport`'tur,
  `None` DEĞİL.
- `kararsizlar` için ayrı kolon YOKTUR: plan 1486-1487 gereği "koşu raporuna girer" —
  yani `policy_report.kararsizlar` içinde taşınır.

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
    policy_report: dict          # PolicyReport'un jsonb'den okunmuş hâli
    barrier_report: dict
    engine_diff: dict
    approval_snapshot: dict | None
    approval_karar: str | None
    snapshot_sha: str | None
    katman1_attestation: dict | None
    katman2_attestation: dict | None
    readiness_attestation: dict | None
```

`VerifiedRun` yalnız YEDİ kapının tamamı geçtiğinde üretilir (plan 341-344); bu yüzden
`engine_version` · `engine_config_sha` · `content_sha` · `decision_log_sha` ·
`final_candidate` · `final_decision_log` alanları `| None` DEĞİLDİR — kapıdan geçmiş bir
satırda dolu olmaları garantidir.

**Tipler NEREDE doğar — R9'un mekanik sonucu.** `record_result` (Task 8) artık
`EngineResult`'ı TÜKETİYOR; oysa `decide` Task 13'te doğar ve **R9 bir görevin sonraki
görevde doğan yüzeyi tüketmesini YASAKLAR.** Bu yüzden motor sözleşmesinin **veri tipleri**
(mantığı değil) Task 8'de doğan ayrı bir sözleşme modülüne alınır:

```python
# apps/social/backend/app/services/sector_pipeline/engine_contract.py   (Task 8 CREATE)
# YALNIZ kapalı değer kümeleri ve dataclass tanımları. Fonksiyon YOK, DB YOK, import
# yönü tek yönlüdür: engine.py buradan okur, burası engine.py'yi GÖRMEZ.

SONUCLAR: tuple[str, ...] = ("activation_eligible", "no_change", "blocked")   # KAPALI
BULGU_SINIFLARI: tuple[str, ...] = (
    "kapsam_ihlali", "mevzuat_uyusmazligi", "mevzuat_dogrulanamadi",
    "regresyon_kapisi", "ikinci_aktif", "acik_soru",
)   # KAPALI — altı değer (R7)
```

```python
# engine_contract.py  (Task 8) — tip tanımları
ENGINE_VERSION: str = "..."          # engine.py'de (Task 13); sözleşme değişince artar

def config_sha(config: PolicyConfig) -> str:      # policy_config.py (Task 13) — K-97 üreticisi
    """PolicyConfig'in kanonik hash'i. identity.canonical_sha'yı ÇAĞIRIR (K-92),
    ikinci bir hash kuralı yazmaz."""

UYGULANMAMA_SEBEPLERI: tuple[str, ...] = (
    "kanit-yok",        # spec girdisi satır 1189: kanıt yoksa karar uygulanmaz
    "mutabakat-yok",    # K-125: iki denetçi uyuşmuyor
    "cogunluk-yok",     # yeni öğe 2-3 yapısal çoğunluk kuralı
)   # KAPALI — üç değer; kaynağı Task 12'nin bağlayıcı kontrol kümesidir (plan 1376-1381)
    # ve spec girdisi satır 1189; UYDURULMUŞ değer YOKTUR

@dataclass(frozen=True)
class KararsizMadde:
    """K-23=B — motorun karar veremediği birim. Aktivasyonu BLOKLAMAZ (plan 1486-1487)."""
    unit_id: str
    sebep: str                       # serbest metin; kapalı küme DEĞİL (dürüst etiket)

@dataclass(frozen=True)
class BulguIzi:
    """run_checks'in ürettiği bulgunun kalıcı izi."""
    sinif: str                       # BULGU_SINIFLARI içinden — KAPALI KÜME (R7, altı değer)
    unit_id: str | None              # birime bağlanamayan bulguda None
                                     # (ör. `regresyon_kapisi`, `ikinci_aktif`)
    detay: str                       # bulguyu doğuran ölçümün tek cümlelik ifadesi

@dataclass(frozen=True)
class UygulanmayanKarar:
    """Aday karar KANITSIZ/MUTABAKATSIZ olduğu için uygulanmadı, kalıp KORUNDU."""
    unit_id: str
    karar: str                       # identity'nin karar türü enum'undan (Task 3;
                                     # plan teknik karar 5: BEŞ değerli, KAPALI)
    sebep: str                       # UYGULANMAMA_SEBEPLERI içinden — KAPALI

@dataclass(frozen=True)
class PolicyReport:
    """K-95 politika raporu — koşu satırının `policy_report` kolonuna yazılan KAPALI tip.

    **TEK ÜRETİCİSİ `engine.decide`'dır.** Başka hiçbir modül bu sınıfı KURMAZ; serbest
    sözlükten üretilen bir politika raporu yolu YOKTUR (R2'nin isimsiz-üretici yasağı).
    Dört alanın dördü de ZORUNLUDUR; boş rapor `PolicyReport((), (), (), ())` biçiminde
    **boş demetlerle** ifade edilir, `None` ile DEĞİL.
    """
    kararsizlar: tuple[KararsizMadde, ...]
    bulgular: tuple[BulguIzi, ...]
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...]
    acik_soru_kimlikleri: tuple[str, ...]   # R7: `acik_soru` bulgusunu doğuran birimler;
                                            # sayaç DEĞİL, iz — K-71 kapısı R8'in yolunda

@dataclass(frozen=True)
class EngineResult:
    sonuc: str                       # SONUCLAR — KAPALI
    sebep: str | None
    final_candidate: dict | None
    final_decision_log: list[dict] | None
    engine_diff: dict
    policy_report: PolicyReport      # YENİ — K-95'in adı konmuş üreticisi;
                                     # `kararsizlar` alanı BURAYA taşındı
    barrier_report: dict
    content_sha: str | None
    decision_log_sha: str | None
    engine_version: str              # YENİ — load_verified_run kapı 3'ün kaynağı
    engine_config_sha: str           # YENİ — kapı 4'ün kaynağı; config_sha() üretir
```

- **`kararsizlar: list[dict]` alanı `EngineResult`'tan SİLİNDİ** (plan 1471 geçersiz).
  İki kaynak olsaydı hangisinin koşu satırına yazıldığı görev-başına review'a görünmezdi —
  R2'nin kapattığı sınıfın ta kendisi. Tek yer: `result.policy_report.kararsizlar`.
- `decide` her üç sonuçta da `engine_version=ENGINE_VERSION` ve
  `engine_config_sha=config_sha(config)` damgalar (K-97, plan 150-152) **ve her üç sonuçta
  da bir `PolicyReport` üretir** — `blocked`/`no_change` koşuları dahil (K-93).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — plan 986 (`open_run` imzası)
ve plan 1001-1002 (`record_result` imzası) GEÇERSİZ, yerine yukarıdakiler. Task 8'in Files
listesine **`Create: apps/social/backend/app/services/sector_pipeline/engine_contract.py`**
EKLENİR (plan 979-981) ve Produces listesine `SONUCLAR` · `BULGU_SINIFLARI` ·
`UYGULANMAMA_SEBEPLERI` · `KararsizMadde` · `BulguIzi` · `UygulanmayanKarar` ·
`PolicyReport` · `EngineResult` girer. Consumes satırı (plan 984) DEĞİŞMEZ — Task 8
sonraki hiçbir görevden yüzey tüketmez (R9 korunur). **Task 12** — `BULGU_SINIFLARI` artık
Task 12'de TANIMLANMAZ, `engine_contract`'tan **import edilir** ve Task 12 onun
**değerlerini üretir**; R7'nin Produces satırı bu biçimde okunur. **Task 13** — plan
1469-1471 (`EngineResult` alan listesi) `policy_report` ile genişler, `kararsizlar` ÇIKAR;
`decide` · `config_sha` · `ENGINE_VERSION` Task 13'ün Produces listesinde kalır ve
`PolicyReport`/`EngineResult` **tek üreticisi** Task 13'tür — tanım Task 8'de, **üretim**
Task 13'te (R5'in amacı tipin adının konması, R9'unki ileri-tüketimin yasaklanması;
tanım/üretim ayrımı ikisini birden karşılar).

**Kanıt testi · sahibi:**
- `test_open_run_requires_kosu_turu` · `test_kosu_turu_value_set_is_closed` ·
  `test_open_run_rejects_duzeltme_type` · `test_retry_inherits_type_target_and_package`
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_record_result_sets_durum_tamamlandi` ·
  `test_record_result_persists_every_engine_result_field` (on bir alanın on biri de satırda
  okunur — R2'nin sessiz-düşme kapısı) ·
  `test_record_result_signature_has_no_var_keyword_arguments` (yapısal: `inspect.signature`
  ile `VAR_KEYWORD` YOK) ·
  `test_record_result_takes_no_free_form_dict_parameter` (yapısal: `db` · `run_id` ·
  `result` DIŞINDA parametre YOK) ·
  `test_record_result_rejects_eligible_result_missing_f19_fields`
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_engine_result_carries_version_and_config_sha` ·
  `test_engine_result_field_set_is_closed` (alan adları yukarıdaki on birle **birebir**;
  fazlası da eksiği de RED — `kararsizlar` alanının VAR OLMAMASI da bu testin konusudur) ·
  `test_config_sha_changes_when_config_changes` ·
  `test_config_sha_uses_identity_canonical_rule` — **Sahip: Task 13**,
  `tests/test_policy_engine_outcome.py`.
- **`PolicyReport`'un kapısı (H2'nin ispatı):**
  `test_policy_report_field_set_is_closed` (dört alan adı birebir; fazlası da eksiği de RED)
  · `test_policy_report_constructed_only_in_engine_module` (yapısal depo-geneli tarama:
  `PolicyReport(` çağrısı YALNIZ `engine.py`'de; tanım dosyası ve `tests/` dizini açıkça
  muaftır, muafiyet testin içinde yazılıdır) ·
  `test_decide_returns_policy_report_for_every_outcome` (üç sonucun üçünde de dolu tip) ·
  `test_bulgu_izi_class_values_are_closed` (`BULGU_SINIFLARI` dışında `sinif` RED) ·
  `test_uygulanmama_sebepleri_are_closed` — **Sahip: Task 13**,
  `tests/test_policy_engine_outcome.py`.

---

## R3 — Onay olayı paket kimliğini TAŞIR

**Kusur (plan satırları):** planın kendi teknik kararı 14(c) (plan 178-181) şunu bağlıyor:
olaylar yaşam döngüsü kapsam sınıfındadır ve `033 F21` gereği `sector_id` + `package_id` +
`actor` ister, *"bu yüzden `record_decision` koşu kimliğinin yanında paket kimliğini de
taşır"*. Ölçüldü (`package_events.py::log_package_event`, yaşam döngüsü dalı, satır 221-223): yaşam döngüsü olayı `sector_id`,
`package_id` ve `actor` yoksa `PackageEventContractError` ile düşer. Buna rağmen plan
1555 satırındaki imza paket kimliği taşımıyor — yani `approval`/`rejection` olayı **yazılamadan
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
  kimliği koşununkiyle çelişebilirdi; TEK KAPI doktrini (plan 345-347) ve F18 bunu yasaklar.
  Bu yüzden imzaya **çağıran-taraflı `package_id` parametresi EKLENMEZ** — hükmün istediği
  "olayın paket kimliğini taşıması"dır, çağırandan alması değil.
- Olay çağrısı: `log_package_event(db, event_type=("approval" if karar == "onay" else
  "rejection"), sector_id=run.sector_id, package_id=run.package_id, actor=actor, detail=...)`.
- `run.package_id` boşsa (taslak henüz yazılmamışsa) onay REDDEDİLİR — onay yüzeyi yalnız
  `activation_eligible` koşuda çalıştığı için taslak her zaman vardır (plan 180-181).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 14** — plan 1555-1559 imzası bu
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

**Kusur (plan satırları):** Task 6 (migration 036) Step 1 test listesi (plan 880-912) üç
tane **servis davranışı** testi taşıyor — konusu Task 8/Task 15 kodudur — ama Task 6 Step 5
(plan 923-924) onlardan PASS bekliyor. O kod o noktada YOKTUR.

**Kural (kontrolör):** bu üç test, konusunu kuran göreve taşınır. Task 6 yalnız
**migration'ın kendi** testlerini tutar: kolonlar · kısıtlar · CHECK'ler · geri alma.

**Bağlayıcı sözleşme — taşınan testler:**

| Test | Plan satırı | Konusu | YENİ sahip · dosya |
|---|---|---|---|
| `test_second_write_for_same_run_returns_existing_draft` | 906 | `writeback.write_draft_from_run` idempotency'si | **Task 15**, `tests/test_pipeline_writeback.py` — Task 15'in mevcut `test_replay_returns_existing_draft_without_new_version` (plan 1704) testiyle **AYNI iddiadır**; ikinci bir ad yazılmaz, Task 6'dan SİLİNİR ve Task 15'in mevcut adı kanonik sahiptir |
| `test_concurrent_write_for_same_run_yields_one_draft` | 907 | aynı yolun yarış hâli | **Task 15** — mevcut `test_concurrent_writes_yield_single_draft` (plan 1705) ile aynı iddia; Task 6'dan SİLİNİR |
| `test_retry_of_correction_inherits_target_and_type` | 905 | `runs.open_run(parent_run_id=…)` devralması (R2) | **Task 8**, `tests/test_pipeline_runs.py` — R2'nin `test_retry_inherits_type_target_and_package` testiyle birleşir |

Task 6'da **KALAN** kardeşleri (şema seviyesi, migration'ın kendi konusu, taşınmaz):
`test_package_id_is_not_unique` · `test_correction_run_may_share_package_id_with_parent` ·
`test_kosu_turu_and_duzeltilen_run_id_check_consistent` ·
`test_retry_of_correction_may_carry_both_links` (plan 901-904) — bunlar CHECK/kardinalite
testleridir, servis davranışı değil.

**Ek düzeltme (Row-D D5, aynı sınıf):** `test_content_written_without_decision_log_rejected`
(plan 892) şemada bulunmayan bir `content` kolonuna iddia ediyor; 036'nın kolonları
`final_candidate` / `final_decision_log`'dur (plan 780-781). Test adı ve iddiası
**`test_final_candidate_written_without_decision_log_rejected`** olarak düzeltilir.
Sahip DEĞİŞMEZ (Task 6).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 6** — plan 905 · 906 · 907
listeden ÇIKAR, plan 892 yeniden adlandırılır; Step 5 (plan 923-924) beklentisi böylece
karşılanabilir hâle gelir. **Task 8** ve **Task 15** — listeleri R2/R4 ile eşlenir.

---

## R5 — İmzada kullanılan her tip, onu ilk üreten görevde TANIMLANIR

**Kusur (plan satırları):** `EngineInputs` (plan 1373 · 1469), `AuditReport` (plan 1221),
`PacketRef` (plan 1167 · 1220) imzalarda kullanılıyor, hiçbir görevde tanımlanmıyor.
Sonuç: Karar Kapıları K-52'nin *"motor girdileri §9.1 ile sınırlıdır; DNA okuma yolu
açılmaz"* hükmünün (plan 97) **denetlenebileceği bir artefakt yok.**

**Kural (kontrolör):** üçü de tam alan listesiyle tanımlanır. `EngineInputs` Task 12'nin
malıdır ve en az şunları taşır: sentez aday kümesi · doğrulanmış denetçi envanteri · aktif
paket birim eşlemesi · bariyer paydası · K-91 ilk-koşu bayrağı · takvim anahtarları.
`PacketRef` ve `AuditReport` Task 9'un malıdır.

**Bağlayıcı sözleşme — Task 9 tipleri:**

```python
# auditors.py  (Task 9)
STATU_DEGERLERI: tuple[str, ...] = (
    "supported", "not_observed", "needs_update", "contradicted", "risk_unverified",
)   # KAPALI — beş değer (K-100, spec-input satır 1025-1029)

DENETCI_ROLLERI: tuple[str, ...] = ("denetci-1", "denetci-2")   # KAPALI (rol adı; ARAÇ adı DEĞİL — K-137)

BOLUM_ANAHTARLARI: tuple[str, ...]   # BEŞ anahtar; değerleri Task 4'ün pinlenmiş
                                     # sözleşme v2 metninden ÖLÇÜLEREK doldurulur, burada UYDURULMAZ (İlke 9)
                                     # Doldurma kuralı ve sıra kapısı: aşağıdaki "M1" bloğu

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

**M1 — beş bölüm anahtarı ŞİMDİ bağlanmaz; bağımlılık bağlanır (fix turu 1, KISMEN RED).**
Fix turu 1'de bağımsız hakem *"beş bölüm anahtarını şimdi sabitle"* dedi. **REDDEDİLDİ.**
Gerekçe ölçülü: o anahtarlar **Task 4'ün henüz YAZILMAMIŞ** sözleşme v2 metninden ölçülür
(plan 643-644: *"dört bölüm → beş bölüm (yeniden doğrulama eklendi). Biçim kapısı (Task 9)
bu beşi arar."*); bugün burada beş ad yazmak, planın kendine bağladığı **ölçülmemiş-değer
yasağını** (İlke 9, plan 68-70) çiğnemek olurdu — yazılan adlar sonra sözleşmeye
UYDURULURDU, tersi değil. **Bu satır bilerek boştur; ileride okuyan biri "yardımcı olmak
için" değer İCAT ETMEZ.**

Boşluğun yerine **bağlayıcı ve test edilebilir** olan şudur:

1. **Sıra kapısı:** **Task 9, Task 4 tamamlanmadan BAŞLAYAMAZ.** Ölçüt mekaniktir: Task 4
   Step 5 (`chore: repin research contracts at v2`, plan 667) atılmış ve
   `shared/contracts/research-contracts.pin.json` v2 hash'lerini taşıyor olmalıdır. Task 9
   ilk iş olarak `contracts.require_pin` çağırır; pin v2 değilse görev DURUR (fail-closed).
2. **Doldurma kuralı:** `BOLUM_ANAHTARLARI`, pinlenmiş `hakem-denetci-gorevi.md`'nin **çıktı
   bölümü başlıkları ÖLÇÜLEREK** doldurulur — sıra ve sayı dosyadaki hâliyle aynıdır.
   Ölçüm komutu ve taze çıktısı Task 9'un adım notuna yazılır (İlke 9).
3. **Kapı testi:** `test_bolum_anahtarlari_match_pinned_contract_headings` — pin
   manifestinden dosya yolunu ve sha256'sını okur, dosyayı **hash doğrulayarak** açar,
   çıktı bölümü başlıklarını çıkarır ve `BOLUM_ANAHTARLARI` ile **birebir** (sıra dâhil)
   karşılaştırır. Sözleşme değişip anahtarlar güncellenmezse test DÜŞER; anahtarlar
   uydurulup sözleşmede karşılığı yoksa da DÜŞER. **Sahip: Task 9**,
   `tests/test_auditor_packaging.py`.
4. `test_bolum_anahtarlari_has_five_entries` — beş sayısı sözleşmenin kendi hükmüdür
   (plan 643-644), ölçülmemiş bir tahmin değildir. **Sahip: Task 9.**

**Etkilenen görev (M1):** **Task 4** — Step 5'in pin yenilemesi artık Task 9'un **açık ön
koşuludur**; Task 4'ün Interfaces "Produces" satırı bunu belirtir. **Task 9** — Consumes
satırına (plan 1165) *"Task 4 sözleşme v2 **pinlenmiş** hâli"* yazılır ve yukarıdaki iki
test eklenir.

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
    """Motor girdileri — ALAN KÜMESİ KAPALIDIR (K-52, plan 97; spec §9.1).
    Marka DNA'sı için alan YOKTUR ve eklenmesi sözleşme revizyonu ister."""
    sentez: SynthesisResult                              # §9.1: sentez aday paketi + karar günlüğü
    aktif_paket: dict | None                             # §9.1: aktif paket (ilk koşuda None)
    aktif_schema_version: int | None                     # §9.1: şema sürümü
    aktif_birimler: dict[str, dict]                      # identity.decision_units (Task 3) — karar kapsamı kontrolü
    mevcut_birim_sayisi: int                             # bariyer paydası (K-130); ilk koşuda 0
    ilk_kosu: bool                                       # K-91
    son_turlarin_cikarmalari: list[dict]                 # §9.1: son turların çıkarma kararları (K-122)
    denetci_envanterleri: ValidatedAuditPair              # §9.1: iki denetçi tablosu + URL örneklemi.
                                                          # TİP ZORUNLUDUR: ham `AuditReport` KABUL EDİLMEZ
                                                          # (R6'nın H3 düzeltmesi; K-150: tam iki rapor)
    mekanik_eleme: RoundGate                             # §9.1: mekanik eleme sonucu (Task 7)
    takvim_anahtarlari: frozenset[str]                   # §9.1: sistem özel gün listesi (normalize anahtarlar)
    otomatik_kapilar: GateResults                        # §9.1: otomatik kapı sonuçları
```

- **`PolicyConfig` `EngineInputs`'a GİRMEZ** — `decide(inputs, config)` onu ayrı alır
  (plan 1469); tek kanonik yer korunur.
- `mevcut_birim_sayisi == len(aktif_birimler)` invariantı yapımda zorlanır.
- **`denetci_envanterleri` tipi YAPIMDA zorlanır** (Plan 1'in `_require_evidence`
  doktrininin motor ayağı — ördek tiplemesi kabul edilmez):

```python
    def __post_init__(self) -> None:
        if type(self.denetci_envanterleri) is not ValidatedAuditPair:
            raise TypeError(
                "denetci_envanterleri ValidatedAuditPair olmalı "
                f"({type(self.denetci_envanterleri).__name__} verildi) — ham denetçi "
                "raporu motora GİRMEZ; doğrulayıcı ve tur-seviyesi mutabakat atlanamaz"
            )
        if self.mevcut_birim_sayisi != len(self.aktif_birimler):
            raise ValueError("mevcut_birim_sayisi aktif_birimler ile tutarsız")
```

  İki `AuditReport`'tan oluşan bir demet, aynı alan adlarını taşısa bile REDDEDİLİR:
  `ValidatedAuditPair`'ı **yalnız** tur seviyesindeki mutabakat fonksiyonu üretir (R6),
  dolayısıyla motora ulaşan her envanter hem doğrulayıcıdan hem mutabakat kapısından
  geçmiştir. **Bu, planın *"girdi yalnız Task 9'un doğrulanmış envanteridir"* hükmünün
  (plan 1389-1390) tipe dönüşmüş hâlidir** — prose değil, kapı.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 9** — Produces listesine
`PacketRef` · `AuditReport` · `InventoryRow` · `UrlCheck` · `STATU_DEGERLERI` ·
`BOLUM_ANAHTARLARI` EKLENİR; `build_packet` imzası (plan 1167) yukarıdakiyle değişir.
**Task 4** — pin yenilemesi Task 9'un ön koşulu olarak beyan edilir (M1).
**Task 12** — Produces listesine `EngineInputs` · `GateResults` EKLENİR (plan 1372-1374);
`EngineInputs` **Task 10'un `ValidatedAuditPair` tipini TÜKETİR** (Task 10 < Task 12,
R9 korunur).
**Task 13** — `decide(inputs: EngineInputs, …)` (plan 1469) artık tanımlı bir tipe işaret
eder.

**Kanıt testi · sahibi:**
- `test_engine_inputs_field_set_is_closed` — `EngineInputs` alan adları yukarıdaki listeyle
  **birebir** eşleşir; fazlası da eksiği de RED. **K-52'nin denetlenebilir karşılığı budur**
  (preflight C12'yi kapatır). **Sahip: Task 12**, `tests/test_policy_engine_checks.py`.
- `test_engine_inputs_has_no_brand_dna_field` (K-52 negatif kontrol) — **Sahip: Task 12**.
- **H3'ün negatif kapıları:** `test_engine_inputs_refuses_bare_audit_report_tuple`
  (iki ham `AuditReport`'tan oluşan demet → `TypeError`; planın `test_engine_consumes_only_validated_inventory`
  testi, plan 1424, artık bu tipe karşı okunur) ·
  `test_engine_inputs_refuses_lookalike_pair` (aynı alan adlarını taşıyan sahte nesne → RED) ·
  `test_engine_inputs_accepts_only_validated_pair` (pozitif kontrol) — **Sahip: Task 12**,
  `tests/test_policy_engine_checks.py`.
- `test_packet_ref_carries_unit_snapshot_and_equal_copy_hashes` (K-79) ·
  `test_audit_report_inventory_rows_have_four_fields` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`.

---

## R6 — Veriyi kapılayan doğrulayıcı AYRIŞTIRILMIŞ NESNEYİ geri verir; çapraz denetçi karşılaştırması TUR seviyesindedir

**Kusur (plan satırları):** (a) `validate_report(...) -> list[str]` (plan 1170) yalnız hata
metni döner, oysa motorun girdisi *"Task 9'un **doğrulanmış** envanteridir"* (plan 1389-1390)
— ayrıştırılmış envanteri **hiçbir görev üretmiyor**; (b) `validate_report`'un ZORUNLU
`unit_snapshot` girdisinin (plan 1182-1185) adlandırılmış bir üreticisi yok ve Task 9'un
Consumes satırı (plan 1165) Task 3'ü hiç saymıyor; (c) TEK rapor alan bir doğrulayıcıdan
*"iki denetçi AYNI anlık görüntüye karşı raporlamış"* olduğunu kanıtlaması isteniyor
(plan 1185) ve testi (`test_inventory_rejects_divergent_snapshot_hash`, plan 1200) Task 9'a
dosyalanmış. **(d) Fix turu 1 bulgusu (yüksek, KABUL):** ilk yazımın `ValidatedReport`'u
`ValidatedReport(rapor=None, errors=[])` biçiminde KURULABİLİYORDU — `gecerli` özelliği o
nesnede `True` döner ve **raporsuz bir "geçerli" envanter** doğardı; ayrıca
`EngineInputs.denetci_envanterleri` ham `AuditReport` kabul ettiği için çağıran hem
doğrulayıcıyı hem tur seviyesindeki mutabakat kapısını **atlayabiliyordu**. Yani motorun
*"yalnız doğrulanmış envanter"* şartının hiçbir tipte veya kapıda karşılığı YOKTU — prose
olarak yazılıydı, kod olarak değil.

**Kural (kontrolör):** (a) `validate_report` **ayrıştırılmış envanter nesnesi + hata listesi**
döner — tip tanımlanır; (b) anlık görüntünün üreticisi adlandırılır: `identity.decision_units`
(Task 3) ve Task 9'un Consumes satırı Task 3'ü BEYAN EDER; (c) çapraz denetçi
snapshot-hash mutabakatı **iki raporu birden gören TUR seviyesi** bir fonksiyona taşınır
(Task 10) ve testi onunla birlikte gider; (d) **`ValidatedReport` tutarsız kurulamaz** ve
motorun kabul ettiği envanter, yalnız tur seviyesinde üretilen **kapalı bir çift tipidir**
(`ValidatedAuditPair`) — ham rapor motora ULAŞAMAZ.

**Bağlayıcı sözleşme:**

```python
# auditors.py  (Task 9)
@dataclass(frozen=True)
class ValidatedReport:
    rapor: AuditReport | None      # errors BOŞ DEĞİLSE None (geçersiz rapor nesneye dönüşmez)
    errors: list[str]

    def __post_init__(self) -> None:
        """İKİ HÂL VARDIR, üçüncüsü YOKTUR — yapımda zorlanır.

        (rapor dolu, errors boş)  = geçerli
        (rapor None, errors dolu) = geçersiz

        Diğer iki kombinasyon YAPIM HATASIDIR: `ValidatedReport(None, [])` `gecerli`
        özelliğini `True` döndürüp **raporsuz bir geçerli envanter** üretirdi;
        `ValidatedReport(rapor, ["..."])` ise hatalı bir raporu geçerli gibi taşırdı.
        """
        if (self.rapor is None) != bool(self.errors):
            raise ValueError(
                "ValidatedReport tutarsız: `rapor is None` ile `errors` doluluğu AYNI "
                f"olmak ZORUNDA (rapor={'None' if self.rapor is None else 'dolu'}, "
                f"errors={len(self.errors)}) — yarım doğrulama sonucu yazılmaz"
            )

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

`validate_report`'un zorladıkları (plan 1178-1186 aynen geçerli, tek fark dönüş tipi):
beş bölüm · her envanter satırı dört alanlı · `statu` ∈ `STATU_DEGERLERI` · `unit_snapshot`
içindeki HER `unit_id` **tam bir kez** · tanınmayan kimlik YOK · tekrar YOK. **Çapraz
denetçi karşılaştırması BURADA YAPILMAZ** — tek rapor görür.

```python
# auditors.py  (Task 10) — TUR seviyesi
@dataclass(frozen=True)
class ValidatedAuditPair:
    """Motorun kabul ettiği TEK envanter tipi (K-150: tam iki denetçi).

    **TEK ÜRETİCİSİ `check_snapshot_agreement`'tır.** Sınıf başka hiçbir modülde
    KURULMAZ; kurulsaydı doğrulayıcıyı ve mutabakat kapısını atlayan ikinci bir yol
    doğardı — R6'nın kapattığı sınıfın ta kendisi.
    """
    birinci: AuditReport           # DENETCI_ROLLERI[0] ("denetci-1") raporu
    ikinci: AuditReport            # DENETCI_ROLLERI[1] ("denetci-2") raporu
    unit_snapshot_sha: str         # ikisinin de üzerinde mutabık kaldığı görüntü hash'i

@dataclass(frozen=True)
class SnapshotAgreement:
    cift: ValidatedAuditPair | None
    errors: list[str]

    def __post_init__(self) -> None:
        # ValidatedReport ile AYNI iki-hâl kuralı — üçüncü hâl yapım hatasıdır.
        if (self.cift is None) != bool(self.errors):
            raise ValueError("SnapshotAgreement tutarsız: cift ile errors birlikte karar verir")

    @property
    def gecerli(self) -> bool:
        return not self.errors

def check_snapshot_agreement(
    validated: tuple[ValidatedReport, ValidatedReport],
    *,
    expected_snapshot_sha: str,        # PacketRef.unit_snapshot_sha
) -> SnapshotAgreement:
    """Girdi HAM rapor DEĞİL, `validate_report`'un dönüşüdür. DÖRT koşul birden aranır:

    (1) iki `ValidatedReport`'un İKİSİ de `gecerli` — biri değilse `cift=None` ve
        hataları `errors`'a birleştirilir (K-150 fail-closed);
    (2) iki raporun `denetci` alanları `DENETCI_ROLLERI`nin ikisini de TAM BİR KEZ kapsar
        (aynı rolden iki rapor REDDEDİLİR);
    (3) her raporun `unit_snapshot_sha`'sı `expected_snapshot_sha`'ya EŞİT;
    (4) iki raporun `unit_snapshot_sha`'ları birbirine EŞİT (K-79/K-100).

    Dördü de geçerse `ValidatedAuditPair` üretilir — BAŞKA ÜRETİCİ YOKTUR. Bir koşul
    düşerse `cift` `None`'dır ve tur GEÇERSİZDİR.
    """
```

`run_audit_round` (plan 1220) imzası DEĞİŞMEZ: anlık görüntü ve hash'i `packet`'in içinden
gelir (R5'teki `PacketRef`). Uyuşmazlıkta `AuditRound(gecerli=False, sebep=...)` döner →
K-150 gereği sentez BAŞLAMAZ (plan 1253-1255).

Motorun girdisi (plan 1389-1390 karşılığı): `EngineInputs.denetci_envanterleri`
**tipi gereği** yalnız `check_snapshot_agreement`'ın ürettiği `ValidatedAuditPair` olabilir
(R5'teki `__post_init__` kapısı); ham metin de ham `AuditReport` da motora ULAŞMAZ.
Zincir tek yönlü ve atlanamazdır:

`validate_report` → `ValidatedReport` → `check_snapshot_agreement` → `ValidatedAuditPair`
→ `EngineInputs` → `run_checks`/`decide`

Ara halkanın atlanabildiği hiçbir imza YOKTUR.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 9** — plan 1170-1171 (dönüş tipi
`list[str]`) GEÇERSİZ; plan 1165 satırındaki Consumes satırı **`Task 3 identity.decision_units +
identity.canonical_sha`** ile genişler; plan 1200 satırındaki
`test_inventory_rejects_divergent_snapshot_hash` Task 9'dan ÇIKAR. **Task 10** — Produces
listesine `check_snapshot_agreement` · `ValidatedAuditPair` · `SnapshotAgreement` EKLENİR
(plan 1218-1221). **Task 12** — `EngineInputs` bu tipi tüketir (R5).

**Kanıt testi · sahibi:**
- `test_validate_report_returns_parsed_inventory_on_success` (pozitif kontrol) ·
  `test_invalid_report_yields_none_object_with_errors` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`. (Mevcut K-100 testleri plan 1197-1201 aynen kalır,
  yalnız dönüş tipine göre okunur.)
- `test_inventory_rejects_divergent_snapshot_hash` — **YENİ sahip: Task 10**,
  `tests/test_auditor_orchestration.py`.
- `test_round_rejects_report_snapshot_differing_from_packet` — **Sahip: Task 10**.
- **H3'ün negatif kapıları — `ValidatedReport` (Sahip: Task 9,
  `tests/test_auditor_packaging.py`):**
  `test_validated_report_rejects_none_report_with_empty_errors`
  (`ValidatedReport(None, [])` → `ValueError`; bu, hükmün ana ispatıdır) ·
  `test_validated_report_rejects_report_carrying_errors`
  (`ValidatedReport(<rapor>, ["x"])` → `ValueError`) ·
  `test_valid_report_object_reports_gecerli_true` (pozitif kontrol).
- **H3'ün negatif kapıları — çift (Sahip: Task 10,
  `tests/test_auditor_orchestration.py`):**
  `test_snapshot_mismatch_yields_no_pair` (hash uyuşmazlığı → `cift is None`) ·
  `test_invalid_report_yields_no_pair` (bir rapor geçersizse çift ÜRETİLMEZ) ·
  `test_same_role_twice_yields_no_pair` (iki rapor da `denetci-1` → RED) ·
  `test_validated_pair_constructed_only_in_check_snapshot_agreement` (yapısal depo-geneli
  tarama: `ValidatedAuditPair(` çağrısı YALNIZ `auditors.py::check_snapshot_agreement`
  gövdesinde; tanım satırı ve `tests/` dizini açıkça muaftır) ·
  `test_agreement_yields_pair_when_all_four_conditions_hold` (pozitif kontrol).

---

## R7 — Yalnız-bulgu üreten fonksiyona UYGULAMA iddiası test edilemez; her bulgu sınıfının bir tüketicisi olur

**Kusur (plan satırları):** Task 12 `run_checks`'i **saf bulgu üreticisi** olarak bağlıyor
ve bunun kapısı olarak `test_run_checks_never_returns_a_run_outcome` testini koyuyor
(plan 1373 · 1378 · 1417); aynı Step 1 listesinde ise **uygulama/uygulanmama** iddia eden
testler duruyor (plan 1420 · 1421 · 1428 · 1430 · 1431). İkisi aynı anda doğru olamaz.
Ayrıca `acik_soru` bulgusu (plan 1429, `test_readd_conflict_emits_acik_soru_finding`)
Task 13'ün dönüşüm listesinde (plan 1522-1528) **hiçbir tüketiciye** sahip değil.

**Kanonik dayanak (spec girdisi, satır 1189 kontrol tablosu — spec'e ÜSTÜNDÜR):**
*"`guncelle` ve `cikar` kararları denetçi satırı veya doğrulanmış URL referansı taşımalı;
**kanıt yoksa karar uygulanmaz, kalıp korunur**"*. "Uygulanmaz/korunur" bir **uygulama**
semantiğidir; uygulamayı yapan `decide`'dır, `run_checks` değil.

**Kural (kontrolör):** uygulama/uygulanmama testleri Task 13'e taşınır; `acik_soru`
bulgusuna `decide`'da açık bir tüketici verilir ve K-71 gereği açık soru aktivasyonu
BLOKLAR — sonuç `blocked`'tır.

**Bağlayıcı sözleşme:**

```python
# engine_contract.py  (Task 8'de TANIMLI — R2'nin H2 düzeltmesi) — BULGU sınıfları, KAPALI
BULGU_SINIFLARI: tuple[str, ...] = (
    "kapsam_ihlali",
    "mevzuat_uyusmazligi",
    "mevzuat_dogrulanamadi",
    "regresyon_kapisi",
    "ikinci_aktif",
    "acik_soru",
)
# Task 12 bu kümeyi IMPORT eder ve DEĞERLERİNİ üretir; Task 13 `BulguIzi.sinif` alanında
# ve dönüşüm tablosunda tüketir. Tanımın Task 8'de olmasının sebebi R2/H2'de yazılıdır:
# `PolicyReport` Task 8'in `record_result`'ında imza tipidir ve R9 ileri-tüketimi yasaklar.
```

`decide`'ın (Task 13) dönüşüm tablosu — **altı sınıfın altısı da tüketilir**:

| Bulgu | `decide` sonucu | Koşul |
|---|---|---|
| `kapsam_ihlali` | `blocked` | her zaman (plan 1522) |
| `mevzuat_uyusmazligi` | `blocked` | her zaman — K-125 benimsendi (plan 1523) |
| `mevzuat_dogrulanamadi` | `blocked` | YALNIZ `config.block_on_legislation is True`; varsayılan `False` (plan 1524-1525) |
| `regresyon_kapisi` | `activation_eligible` OLAMAZ | plan 1526 |
| `ikinci_aktif` | `blocked` | plan 1527 |
| **`acik_soru`** | **`blocked`, `sebep="acik-soru-var"`** | **YENİ** — bulgu VARSA ya da `inputs.sentez.acik_sorular` boş DEĞİLSE. K-71 gereği açık soru aktivasyonu bloklar (plan 103 · 1488-1489) |

Sınır (plan 1486-1487 aynen geçerli): K-23=B kararsızları **bloklamaz** — `kararsizlar`
listesine girer, `policy_report`'a yazılır. Açık soru yolu ondan AYRIDIR.

**Taşınan testler (Task 12 → Task 13, `tests/test_policy_engine_outcome.py`):**

| Test | Plan satırı | Neden taşınıyor |
|---|---|---|
| `test_guncelle_without_evidence_is_not_applied` | 1420 | "uygulanmaz" = uygulama semantiği |
| `test_cikar_without_two_auditor_agreement_keeps_pattern` | 1421 | "korunur" = uygulama semantiği (preflight listesinde adı geçmiyor, sınıfı aynı) |
| `test_flag_consumption_applied` | 1428 | "applied" |
| `test_new_item_needs_two_of_three` | 1428 | aday öğenin pakete GİRİP girmediği |
| `test_category_conflict_package_type_wins` | 1430 | hangi değerin nihai adaya yazıldığı |
| `test_unmatched_holiday_key_not_written` | 1431 | "not_written" |

Task 12'de KALAN: `test_readd_conflict_emits_acik_soru_finding` (plan 1429) — konusu
bulgunun ÜRETİLMESİDİR. Task 13'e YENİ eklenen tüketici testi:
`test_acik_soru_finding_becomes_blocked` + `test_synthesis_open_questions_become_blocked`
(iki kaynak da aynı sonuca çıkar).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 12** — plan 1420 · 1421 · 1428 ·
1430 · 1431 listeden ÇIKAR; `BULGU_SINIFLARI` Task 12'nin Produces satırında **tanım olarak
DEĞİL, tüketim olarak** görünür (tanımı `engine_contract.py`'de, Task 8 — bkz. R2/H2).
**Task 13** — plan 1522-1528 dönüşüm listesi `acik_soru` satırıyla genişler; `acik_soru`
bulgusunun izi `PolicyReport.acik_soru_kimlikleri`'ne yazılır (R2).

**Kanıt testi · sahibi:** yukarıdaki tabloların tamamı; `test_acik_soru_finding_becomes_blocked`
ve `test_finding_classes_all_have_a_consumer` (yapısal: `BULGU_SINIFLARI`'nın her değeri
`decide`'ın dönüşüm tablosunda geçer) — **Sahip: Task 13**,
`tests/test_policy_engine_outcome.py`.

---

## R8 — Kanıt veritabanından OKUNUR, çağırandan alınmaz. İKİNCİ bir kurucu yoktur

**Kusur (plan satırları):** (a) Task 14 `Consumes: Task 13 EngineResult` (plan 1545) diyor,
oysa gövdesi her şeyi `load_verified_run`'dan **basıyor** (plan 1547-1552) ve planın kendi
doktrini kanıtın çağırandan alınmasını yasaklıyor (plan 319-325); Consumes ayrıca gerçekten
kullandığı yüzeyi (`runs.load_verified_run`) hiç saymıyor. (b) `approval.to_activation_evidence(
snapshot: dict) -> ActivationGateEvidence` (plan 1560-1563) **çağıranın verdiği bir sözlükten**
kanıt üreten İKİNCİ bir kurucudur — planın "TEK KAPI LİSTESİ" bölümünün (plan 334-359)
*"yolu yok"* dediği deliği tam olarak yeniden açar. Ölçüldü
(`sector_package_lifecycle.py::_require_evidence`, satır 133-144): `_require_evidence` yalnız SINIFI doğrular, kanıtın
KÖKENİNİ değil — yani uydurulmuş bir sözlükten kurulan kanıt kapıdan geçerdi.

**(c) Fix turu 1 bulgusu — EN ÖNEMLİSİ (yüksek, KABUL).** İlk yazımın R8'i yalnız bir
**kolaylık kurucusunu** sildi; kapının kendisine dokunmadı. **Ölçüldü (2026-08-30):**

- `ActivationGateEvidence` ve `RollbackGateEvidence` **public, `frozen=True` dataclass**'tır
  (`sector_package_lifecycle.py`, satır 83-113 ve 116-130); herkes literal değerlerle
  kurabilir.
- `_require_evidence` (aynı dosya, satır 133-144) **YALNIZ** `type(evidence) is expected`
  kontrolü yapar — kanıtın KÖKENİNE bakmaz.
- Plan 1'in kendi testleri bunu **yapıyor ve geçişleri tamamlıyor**:
  `tests/test_package_lifecycle.py::_activation_evidence` (satır 134-142) ve
  `::_rollback_evidence` (satır 145-148) kanıtı literalden kurar;
  `test_first_activation_single_step` (satır 268) · `test_rollback_restores_previous_version`
  (satır 420) o kanıtla **başarıyla** geçiş yapar.
- İlk yazımın kapısı **yapısal grep**'ti; grep `tests/` dizinini ve tanım dosyasını AÇIKÇA
  muaf tutar, ayrıca takma ad (`E = ActivationGateEvidence`) ve dinamik kurulumu
  (`globals()[...]`, `dataclasses.replace`) GÖREMEZ.

Sonuç: planın çekirdek doktrini — *"kanıt veritabanından okunur, çağırandan alınmaz"* —
**yazılıydı ama ZORLANMIYORDU.**

**Kural (kontrolör):** `to_activation_evidence` TAMAMEN SİLİNİR. Tek kurulum yeri
aktivasyon yolunun içidir ve kilitli doğrulanmış koşudan kurulur. Task 14'ün Consumes satırı
düzeltilir. **Ve kapı grep'ten ALINIP kabul fonksiyonunun İÇİNE konur:** her iki kanıt
sınıfı, yalnız veritabanı destekli bir fabrikanın üretebileceği **tek kullanımlık bir köken
jetonu** taşır; `activate_package` ve `rollback_package` bu jetonu **kendi işlemleri
içinde, kilitli satıra karşı** doğrular ve **harcar**. Yapısal tarama KALIR ama artık tek
kapı değildir — yardımcı bir hijyen kontrolüdür.

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
        expected_active_version / expected_no_active  = K-94 taban durumu (plan 1685-1687)

    Hiçbir alan parametreden gelmez; fonksiyonun imzasında `evidence`, `snapshot`
    ya da herhangi bir `dict` parametresi YOKTUR."""
```

### R8(c) — KÖKEN JETONU: kapı grep'te değil, kabul fonksiyonunun içinde

**Dürüst sınır önce (İlke 3 · İlke 9).** Python'da **kriptografik anlamda taklit edilemez**
bir jeton, aynı süreçte koşan koda karşı KURULAMAZ: aynı süreçteki kod fabrikayı çağırabilir,
`dataclasses.replace` kullanabilir, `object.__setattr__` ile donmuş alanı yazabilir ya da
jetonu doğrudan veritabanından okuyabilir. Bunu iddia ETMİYORUZ. **Ulaşılabilir en güçlü
garanti** ve **adı konmuş sınırı** şudur:

> **Garanti:** Bir kanıt nesnesi kapıdan ancak, o kanıtın **alan değerleri** üzerinde
> hesaplanmış bir parmak izi ile birlikte, ilgili **kilitli veritabanı satırında** basılmış
> ve **henüz harcanmamış** bir jeton varsa geçer. Yani hiçbir kanıt, **veritabanına gidip
> gelmeden** ve **o gidiş gelişte kilitli satıra yazmadan** kabul edilemez. Literal
> değerlerle kurulmuş bir kanıt — Plan 1'in bugünkü testlerinin kurduğu türden — **her iki
> geçişte de REDDEDİLİR.**
>
> **Sınırın adı:** `social.sector_package_runs` ve `social.package_rollback_plans`
> tablolarına **UPDATE yetkisi olan** kod, uydurma bir parmak izi üzerine jeton basabilir.
> Bu artık bir *tip* sorunu değil, bir **veritabanı yetkisi** sorunudur ve planın K-103 etkin
> yetki ölçümünün (Task 15 Step 6) konusudur. Kalan risk **kabul edilmiş ve adlandırılmıştır**;
> "kapatıldı" DENMEZ.

**Şema ayağı (Task 6, migration 036).** İki tablo da aynı DÖRT kolonu kazanır:

```sql
-- social.sector_package_runs  VE  social.package_rollback_plans
kanit_jetonu             text        NULL,   -- 64 hex karakter; harcanınca NULL'lanır
kanit_jetonu_parmakizi   text        NULL,   -- kanıt alanlarının kanonik sha256'sı
kanit_jetonu_basildi_at  timestamptz NULL,
kanit_jetonu_harcandi_at timestamptz NULL,
CONSTRAINT <tablo>_kanit_jetonu_butun
  CHECK (kanit_jetonu IS NULL
         OR (kanit_jetonu_parmakizi IS NOT NULL AND kanit_jetonu_basildi_at IS NOT NULL))
```

Jeton **türü kolonu YOKTUR**: jetonun türünü taşıdığı TABLO belirler
(`sector_package_runs` → aktivasyon, `package_rollback_plans` → geri alma). İkinci bir
enum açmak, R2'nin kapattığı isimsiz-değer sınıfını geri getirirdi.

**Tip ayağı — Plan 1 arayüzünde BEYAN EDİLEN değişiklik (Task 15).** Bu değişiklik planın
*"Bu planın Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER"* bölümüne, `expected_no_active` ve
`_update_draft_row` kalemlerinin YANINA yazılır — gizli bir arayüz kırılması bırakılmaz.

```python
# apps/social/backend/app/services/sector_package_lifecycle.py   (Task 15 MODIFY)
from dataclasses import dataclass, field

class EvidenceProvenanceInvalid(GateNotSatisfied):
    """Kanıtın köken jetonu kilitli satırda YOK, eşleşmiyor ya da ZATEN harcanmış."""


class EvidenceMintRefused(RuntimeError):
    """Jeton BASILAMADI — satır yok ya da jeton basmaya uygun durumda değil."""


def _require_token(value: Any, label: str) -> None:
    """Jeton 64 karakterlik küçük harf hex `str` olmalı — boş/whitespace/`None` RED."""
    if (type(value) is not str or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value)):
        raise TypeError(f"{label} 64 karakterlik hex jeton olmalı — köken kanıtı uydurulamaz")


def _evidence_fingerprint(evidence: Any) -> str:
    """Kanıtın kanonik parmak izi: SINIF ADI + (alan adı, değer) çiftleri, alan adına
    göre ARTAN sırada, `provenance_token` HARİÇ; `identity.canonical_sha` (Task 3, K-92)
    kuralıyla hash'lenir. İkinci bir hash kuralı YAZILMAZ."""


@dataclass(frozen=True)
class ActivationGateEvidence:
    activation_eligible: bool
    open_questions_count: int
    katman1_passed: bool
    checklist_approved: bool
    expected_active_version: int | None = None
    expected_no_active: bool = False                  # planın zaten beyan ettiği alan
    run_id: str = field(kw_only=True)                 # YENİ — jetonun basıldığı koşu
    provenance_token: str = field(kw_only=True)       # YENİ — 64 hex, TEK KULLANIMLIK

    def __post_init__(self) -> None:
        ...                                           # mevcut dört `_require_*` kapısı AYNEN
        _require_flag(self.expected_no_active, "expected_no_active")
        if not isinstance(self.run_id, str) or not self.run_id.strip():
            raise ValueError("run_id zorunlu — kökensiz kanıt kurulamaz")
        _require_token(self.provenance_token, "provenance_token")


@dataclass(frozen=True)
class RollbackGateEvidence:
    manager_approved: bool
    katman1_passed: bool
    incident_id: str = field(kw_only=True)            # YENİ — jetonun basıldığı olay
    package_id: UUID = field(kw_only=True)            # YENİ — geri alınan paket
    provenance_token: str = field(kw_only=True)       # YENİ — 64 hex, TEK KULLANIMLIK

    def __post_init__(self) -> None:
        _require_flag(self.manager_approved, "manager_approved")
        _require_flag(self.katman1_passed, "katman1_passed")
        if not isinstance(self.incident_id, str) or not self.incident_id.strip():
            raise ValueError("incident_id zorunlu")
        if type(self.package_id) is not UUID:
            raise TypeError("package_id UUID olmalı")
        _require_token(self.provenance_token, "provenance_token")
```

`field(kw_only=True)` seçilmesinin sebebi ölçülmüştür: yeni alanlar **varsayılansız**
olmalı, ama `expected_active_version` zaten varsayılanlı olduğu için konumsal sırada
öncelerine konamazlar. Ölçüldü — depoda kanıt sınıflarını kuran **her** çağrı anahtar
argüman kullanıyor (`tests/test_package_lifecycle.py` satır 134-148 · 704-726;
`tests/test_plan2_interface_contract.py` satır 476 · 496 · 519 · 539), yani konumsal
kurulumun kalkması mevcut hiçbir çağrıyı kırmaz.

**Üretici ayağı (jeton basımı).**

```python
# runs.py  (Task 8)
async def mint_evidence_token(
    db,
    *,
    table: str,                 # "sector_package_runs" | "package_rollback_plans" — KAPALI
    run_id: str | None,         # aktivasyon yolunda dolu, geri alma yolunda None
    incident_id: str | None,    # geri alma yolunda dolu, aktivasyon yolunda None
    package_id: UUID | None,    # geri alma yolunda dolu, aktivasyon yolunda None
    fingerprint: str,
) -> str:
    """Kilitli satıra 64 hex'lik YENİ bir jeton + parmak izi basar ve jetonu döner.

    Satır ÇAĞIRAN tarafından ZATEN kilitlenmiş olmalıdır (`FOR UPDATE`); fonksiyon kendi
    kilidini ALMAZ — kilit · basım · tüketim aynı işlemde kalsın diye. Basılamazsa
    (satır yok · koşu `durum != 'tamamlandi'` · plan satırı `durum != 'bekliyor'`)
    `EvidenceMintRefused` fırlatır; **boş dönüş YOKTUR.**
    """
```

```python
# writeback.py  (Task 15) — aktivasyon fabrikası
async def build_activation_evidence(db, *, run_id: str) -> ActivationGateEvidence:
    """`activate_from_snapshot`'ın İÇİNDEN, onun işleminde çağrılır. Sırayla:

      1. `run = await runs.load_verified_run(db, run_id=run_id, for_update=True)`
      2. dört boolean/sayaç + K-94 taban durumu yukarıdaki gövdedeki gibi TÜRETİLİR
      3. `fingerprint = _evidence_fingerprint_from_payload(ActivationGateEvidence, payload)`
      4. `token = await runs.mint_evidence_token(db, table="sector_package_runs",
             run_id=run_id, incident_id=None, package_id=None, fingerprint=fingerprint)`
      5. `return ActivationGateEvidence(**payload, run_id=run_id, provenance_token=token)`

    İmzasında `evidence`, `snapshot` ya da herhangi bir `dict` parametresi YOKTUR.
    """
```

Geri alma fabrikası R11'in `runs.build_rollback_evidence`'ıdır; oraya **aynı 3-4-5 adımı**
eklenir (`table="package_rollback_plans"`, `incident_id`/`package_id` dolu, `run_id=None`).

**Tüketici ayağı — kapı BURADA (Plan 1'in kabul fonksiyonlarının İÇİ).**

```python
# sector_package_lifecycle.py  (Task 15 MODIFY)
async def _consume_provenance(db, *, table: str, evidence: Any, keys: dict) -> None:
    """Kilitli satırdaki jetonu ATOMİK olarak tüketir — okuma ile yazma AYRILMAZ,
    dolayısıyla iki eşzamanlı geçişten yalnız biri kazanır."""
    consumed = await db.fetchval(
        f"UPDATE social.{table} "
        "   SET kanit_jetonu = NULL, kanit_jetonu_harcandi_at = now() "
        " WHERE " + " AND ".join(f"{k} = ${i + 1}" for i, k in enumerate(keys)) +
        f"   AND kanit_jetonu = ${len(keys) + 1} "
        f"   AND kanit_jetonu_parmakizi = ${len(keys) + 2} "
        "   AND kanit_jetonu_harcandi_at IS NULL "
        " RETURNING id",
        *keys.values(), evidence.provenance_token, _evidence_fingerprint(evidence),
    )
    if consumed is None:
        raise EvidenceProvenanceInvalid(
            "kanıt kökeni doğrulanamadı: jeton yok, eşleşmiyor, kanıt alanları jetonun "
            "basıldığı andakinden farklı, ya da jeton ZATEN harcanmış — literal kurulmuş "
            "kanıt kabul edilmez"
        )
```

`activate_package` — mevcut gövdesi DEĞİŞMEZ, tek ekleme yapılır (tam imza):

```python
async def activate_package(
    db, *, package_id: UUID, evidence: ActivationGateEvidence, actor: str,
) -> None:
    _require_evidence(evidence, ActivationGateEvidence)     # AYNEN (sınıf kapısı)
    owner = _require_actor(actor)
    ...                                                     # mevcut dört alan kontrolü AYNEN
    async with db.transaction():
        sector_id, target = await _lock_and_load(db, package_id)
        ...                                                 # durum + expected_* kontrolleri AYNEN
        await _consume_provenance(                          # YENİ — geçişten hemen ÖNCE
            db, table="sector_package_runs", evidence=evidence,
            keys={"run_id": evidence.run_id, "package_id": package_id},
        )
        await _apply_status_transition(...)                 # AYNEN
```

`rollback_package` — aynı desen, anahtarlar farklı:

```python
async def rollback_package(
    db, *, sector_id: UUID, to_version: int, evidence: RollbackGateEvidence, actor: str,
) -> None:
    _require_evidence(evidence, RollbackGateEvidence)       # AYNEN
    owner = _require_actor(actor)
    ...                                                     # mevcut iki alan kontrolü AYNEN
    async with db.transaction():
        ...                                                 # hedef ve `current` çözümü AYNEN
        if evidence.package_id != current["id"]:            # YENİ — jeton HEDEFE bağlıdır
            raise EvidenceProvenanceInvalid(
                "kanıt başka bir paket için basılmış — olay/paket bağı tutmuyor"
            )
        await _consume_provenance(                          # YENİ
            db, table="package_rollback_plans", evidence=evidence,
            keys={"incident_id": evidence.incident_id, "package_id": evidence.package_id},
        )
        await _apply_status_transition(...)                 # AYNEN
```

**Kapının NE YAPMADIĞI (kapsam sınırı, dürüst etiket).** Jeton **fabrikanın koştuğunu**
kanıtlar; **yedi kapıyı YENİDEN KONTROL ETMEZ.** `load_verified_run`'ın yedi kapısı
tek yerde kalır ve burada TEKRARLANMAZ — ikinci bir kapı listesi yazmak, planın
"TEK KAPI LİSTESİ" bölümünün yasakladığı şeydir.

**Jeton tek kullanımlıktır ve HEDEFE bağlıdır.** `package_id`/`incident_id` anahtarları
`WHERE` yan tümcesinde olduğu için A koşusu için basılmış bir jeton B paketini aktive
edemez; `kanit_jetonu_harcandi_at IS NULL` koşulu tekrar oynatmayı kapatır.

**Güncellenmesi ZORUNLU Plan 1 testleri — sahip: Task 15.** Plan zaten bu iki dosyayı
Task 15'in *"DAVRANIŞ DEĞİŞİKLİĞİ — Plan 1 testleri"* kaleminde sayıyor ve Step 5b'de
koşuyor; kapsam o kalemin altında genişler:

| Dosya · yer | Ne değişir |
|---|---|
| `tests/test_package_lifecycle.py::_activation_evidence` (satır 134-142) | Fabrikaya dönüşür: `pkg_db` + gerçek koşu satırı alır, `mint_evidence_token` ile jeton basar, kanıtı onunla kurar |
| `tests/test_package_lifecycle.py::_rollback_evidence` (satır 145-148) | Aynısı, `package_rollback_plans` satırı üzerinden |
| `tests/test_package_lifecycle.py` — geçişi BAŞARIYLA tamamlayan her test (`test_first_activation_single_step` 268 · `test_activate_archives_previous_then_activates` 284 · `test_activate_accepts_matching_base_version` 349 · `test_rollback_restores_previous_version` 420 · `test_rollback_allowed_while_candidate_activation_gates_fail` 475 · `test_concurrent_activation_of_same_draft_single_winner` 813 · `test_concurrent_activation_of_different_drafts_is_serializable` 952) | İki fabrikadan geçtikleri için imza değişikliğini **kendiliğinden** devralır; ek düzenleme YALNIZ jeton kurulumu gerektiren yerlerdedir |
| `tests/test_package_lifecycle.py::test_activation_evidence_rejects_loose_values` (704) · `::test_rollback_evidence_rejects_loose_values` (721) | Parametre listesine jeton vakaları eklenir (boş · kısa · büyük harf hex · `None`) |
| `tests/test_package_lifecycle.py::test_rollback_evidence_is_not_the_activation_evidence` (461) | **Ölçüldü: kırılmaz.** Testin `activation_only` kümesi dört adı sayıyor; `provenance_token` iki sınıfta da bulunduğu için kesişim boş kalır |
| `tests/test_plan2_interface_contract.py` satır 476 · 496 · 519 · 539 | Dört kanıt kurulumu jetonlu fabrikadan geçer |

**Kanıt testi · sahibi (R8(c)):**
- **Ana ispat — literal kanıt her İKİ geçişte de reddedilir:**
  `test_activation_refuses_literal_constructed_evidence` (gerçek `run_id`, uydurma
  `provenance_token="0"*64` → `EvidenceProvenanceInvalid`; paket `draft` KALIR ve
  `package_events`'e satır YAZILMAZ) ·
  `test_rollback_refuses_literal_constructed_evidence` (aynısı `rollback_package` için;
  aktif sürüm DEĞİŞMEZ) — **Sahip: Task 15**, `tests/test_package_lifecycle.py`.
- `test_activation_token_is_single_use` (aynı kanıtla ikinci aktivasyon RED) ·
  `test_rollback_token_is_single_use` ·
  `test_activation_token_is_bound_to_its_package` (A koşusunun jetonu B paketini aktive
  edemez) · `test_rollback_token_is_bound_to_its_incident_and_package` ·
  `test_tampered_evidence_field_breaks_fingerprint` (jeton gerçek, ama
  `checklist_approved` `False`→`True` çevrilmiş → RED) — **Sahip: Task 15**.
- Pozitif kontroller: `test_activation_succeeds_with_minted_evidence` ·
  `test_rollback_succeeds_with_minted_evidence` — **Sahip: Task 15**.
- `test_evidence_token_minted_only_inside_the_two_factories` (yapısal depo-geneli tarama:
  `mint_evidence_token(` çağrısı YALNIZ `writeback.build_activation_evidence` ve
  `runs.build_rollback_evidence` gövdelerinde; `tests/` muaf) — **Sahip: Task 15**,
  `tests/test_write_surface_authorization.py`.
- Şema kapıları: `test_evidence_token_columns_present_and_nullable` (iki tabloda da dört
  kolon) · `test_evidence_token_check_requires_fingerprint_and_mint_time` (jeton dolu ama
  parmak izi/basım zamanı boş → CHECK RED) — **Sahip: Task 6**,
  `tests/test_migration_036.py`.

Task 14'ün düzeltilmiş Consumes satırı:

> `Consumes: Task 8 runs.load_verified_run (+ VerifiedRun); Task 6 sector_package_runs;
> package_events.log_package_event.` — `Task 13 EngineResult` **ÇIKARILDI**: Task 14 motor
> sonucunu nesne olarak DEĞİL, koşu satırından okur.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 14** — plan 1545 (Consumes) ve plan
1560-1563 (`to_activation_evidence`) GEÇERSİZ. **Task 15** — plan 1669-1684 aralığındaki F18
zinciri aynen geçerli, üstüne "tek kurulum yeri" hükmü EKLENİR; Files listesindeki
`Modify: sector_package_lifecycle.py` kalemi (plan 1619-1620) **kanıt sınıflarının köken
jetonu alanları + `_consume_provenance` + `EvidenceProvenanceInvalid`** ile genişler;
Produces listesine `writeback.build_activation_evidence` EKLENİR.
**Task 6** — 036 şemasına iki tabloya birden DÖRT jeton kolonu + bir CHECK eklenir.
**Task 8** — Produces listesine `mint_evidence_token` + `EvidenceMintRefused` EKLENİR.
**Plan gövdesi** — *"Bu planın Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER"* bölümüne köken
jetonu kalemi `expected_no_active`'in yanına yazılmıştır (bu fix turunda uygulandı).

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
(plan 1677 · 1728), ama o alanın tek üreticisi `readiness.attest` **Task 17'de** doğuyor
(plan 1898-1900). Task 15'in pozitif kontrolü
`test_activation_succeeds_with_full_attestation_chain` (plan 1731) bu yüzden **yazıcısız**:
Task 15 kendi sırasında tamamlanamaz. Bu, planın `hazirlik-onayla` komutu için zaten
kapattığını söylediği sınıfın (plan 1894-1897) süpürülmemiş kardeşidir.

**Kural (kontrolör):** **YAZICI Task 15'in kapsamına taşınır.** Task 17 yirmi maddelik
listenin değerlendirmesini ve CLI alt komutunu TUTAR.

**Kusur (fix turu 1, yüksek, KABUL) — R9'un KENDİ açtığı delik.** İlk yazımın imzası
`attest_readiness(..., onaylandi: bool, kapi_maddeleri, sinyal_maddeleri, actor)` biçimindeydi:
**onay boolean'ını ve madde demetlerini doğrudan ÇAĞIRANDAN alıyordu.** Yani herhangi bir iç
çağıran `onaylandi=True, kapi_maddeleri=()` yazıp K-69 kapısını atlayabilirdi — ekin her yerde
yasakladığı **uydurulmuş boolean**'ın ta kendisi, üstelik F18'in kapatmak için var olduğu yolda.

**Kural (kontrolör):** **YAZICI Task 15'in kapsamına taşınır** ve **`onaylandi` PARAMETRE
OLMAKTAN ÇIKAR — YAZICI onu TÜRETİR.** Türetmenin dayandığı kanonik madde kümesi, yazıcıdan
ÖNCE var olan paylaşılan bir modüle alınır. Task 17 yirmi maddelik listenin
**değerlendirmesini** ve CLI alt komutunu TUTAR (R9'un sıra düzeltmesi AYNEN geçerlidir).

**Bağlayıcı sözleşme — kanonik madde kümesi (Task 8 CREATE):**

```python
# apps/social/backend/app/services/sector_pipeline/readiness_items.py   (Task 8 CREATE)
# YALNIZ kimlik + sınıflandırma. Değerlendirme mantığı YOK (o Task 17'nindir), DB YOK.

MADDE_SINIFLARI: tuple[str, ...] = ("kapi", "sinyal")   # KAPALI — iki değer

@dataclass(frozen=True)
class ChecklistItem:
    madde_id: str        # kanonik madde kimliği
    sinif: str           # MADDE_SINIFLARI içinden — KAPALI
    otomatik: bool       # otomatik ön-kontrolle ölçülebiliyor mu (Task 17 tüketir)

MADDELER: tuple[ChecklistItem, ...]
# YİRMİ madde. Kimlikler ve sınıflar spec §13.4'ün YİRMİ maddesinden ÖLÇÜLEREK
# doldurulur — burada UYDURULMAZ (İlke 9, M1 ile aynı disiplin). Küme KAPALIDIR.
# Bağlayıcı olan iki şey ölçüm gerektirmez ve şimdiden yazılıdır:
#   (a) madde sayısı YİRMİ'dir (plan 1891: "spec §13.4'ün 20 maddesi");
#   (b) 15. madde ("kör değerlendirmede sektörel ayrışma gözlendi") `sinif="sinyal"`dir
#       ve tamamlanma kapısına GİRMEZ (plan 1919-1921 · 1924-1925).

KAPI_MADDELERI:   frozenset[str]   # {i.madde_id for i in MADDELER if i.sinif == "kapi"}
SINYAL_MADDELERI: frozenset[str]   # {i.madde_id for i in MADDELER if i.sinif == "sinyal"}
```

**Bağlayıcı sözleşme — DÜZELTİLMİŞ yazıcı (tam imza):**

```python
# runs.py  (Task 8'de doğar, Task 15 MODIFY eder) — attest_katman1/attest_katman2'nin kardeşi
class ReadinessAttestationRefused(ValueError):
    """Onay TÜRETİLEMEDİ — verilen kapı kümesi kanonik kümeyle örtüşmüyor. Kayıt YAZILMAZ."""


async def attest_readiness(
    db,
    *,
    run_id: str,
    kapi_maddeleri: tuple[str, ...],      # operatörün işaretlediği `kapi` madde kimlikleri
    sinyal_maddeleri: tuple[str, ...],    # `sinyal` sınıfındakiler — tamamlanma kapısına GİRMEZ
    actor: str,
) -> None:
    """F18: operatörün TEK onayını koşu satırının `readiness_attestation` alanına kalıcı
    yazar (kim · ne zaman · hangi maddeler).

    **`onaylandi` PARAMETRE DEĞİLDİR — burada TÜRETİLİR:**

        onaylandi = (set(kapi_maddeleri) == readiness_items.KAPI_MADDELERI)

    ve aşağıdaki BEŞ koşuldan biri düşerse kayıt hiç YAZILMAZ
    (`ReadinessAttestationRefused`; sessiz `onaylandi=False` kaydı da ÜRETİLMEZ):

      (1) `kapi_maddeleri` BOŞ;
      (2) `KAPI_MADDELERI`nin bir üyesi `kapi_maddeleri`'nde YOK          → eksik madde;
      (3) `kapi_maddeleri`'nde `MADDELER`de bulunmayan bir kimlik var     → tanınmayan madde;
      (4) `kapi_maddeleri`'nde sınıfı `sinyal` olan bir kimlik var, ya da
          `sinyal_maddeleri`'nde sınıfı `kapi` olan bir kimlik var        → yanlış sınıf;
      (5) iki demetten birinde TEKRAR EDEN kimlik var (küme boyu ≠ demet boyu).

    `actor` Plan 1'in KANONİK aktör kapısından geçer:
    `sector_package_lifecycle._require_actor` (ölçüldü, satır 147-150 — `str` değilse ya da
    `strip()` sonrası boşsa `ValueError`). İkinci bir aktör kuralı YAZILMAZ.

    Yazılan kayıt:
        {"onaylandi": True, "actor": <doğrulanmış>, "at": <now>,
         "kapi_maddeleri": [...], "sinyal_maddeleri": [...],
         "madde_kumesi_sha": identity.canonical_sha(readiness_items.MADDELER)}
    """
```

- **Kayıt YALNIZ onay hâlinde doğar; `onaylandi` yazılan her kayıtta `True`'dur** — dürüst
  etiket: onaylanmamış hâlin kaydı YOKTUR, çünkü aktivasyon "kayıt yok" hâlini zaten RED
  sayar. Alan yine de yazılır, çünkü aktivasyonun okuduğu sözleşme odur.
- `madde_kumesi_sha`, kaydın hangi kanonik liste sürümüne karşı verildiğini damgalar:
  liste sonradan değişirse eski onay **sessizce yeni listeye geçmez**.
- Parametreler **ilkel tiplerdir**, `ReadinessReport` DEĞİL: `ReadinessReport` Task 17'de
  doğar ve Task 15'in ona bağımlı olması bağımlılığı yine ters çevirirdi. `readiness_items`
  ise Task 8'de doğduğu için ileri-bağımlılık YOKTUR (R9'un kendi kuralı).
- `activate_from_snapshot` (Task 15) `readiness_attestation["onaylandi"] is True` arar;
  eksik ya da `False` → aktivasyon REDDEDİLİR.

**KALAN yüzeyler (Task 17, değişmez):** `readiness.CHECKLIST: tuple[Item, ...]` (plan 1891) ·
`readiness.evaluate(db) -> ReadinessReport` (plan 1892) · `kapi`/`sinyal` sınıflandırması
(plan 1909-1914 · 1920-1925) · CLI alt komutu **`hazirlik-onayla`** (plan 1893-1897) — komut
`readiness.evaluate`'i çağırır, operatörün TEK onayını alır ve **`runs.attest_readiness`**'e
yazdırır. **Tek fark (H5):** `readiness.CHECKLIST` ikinci bir liste DEĞİLDİR — kimlik ve
sınıf bilgisini `readiness_items.MADDELER`'den **kurar**; Task 17 üstüne yalnız
değerlendirme (`otomatik ön-kontrol` sonucu, `elle` etiketi) ekler. Çift kayıt YASAK.

**SİLİNEN yüzey:** `readiness.attest(db, *, run_id, report, actor)` (plan 1898-1900) —
YOKTUR; yerine `runs.attest_readiness` geçer.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — Files listesine
`Create: apps/social/backend/app/services/sector_pipeline/readiness_items.py` EKLENİR
(plan 979-981); Produces listesine `MADDELER` · `MADDE_SINIFLARI` · `KAPI_MADDELERI` ·
`SINYAL_MADDELERI` · `ChecklistItem` · `attest_readiness` · `ReadinessAttestationRefused`
girer. **Task 15** — Files listesine
`Modify: apps/social/backend/app/services/sector_pipeline/runs.py` EKLENİR (plan 1618-1629);
Task 15 yazıcıyı **tüketir**, türetme mantığı Task 8'de doğar.
**Task 17** — plan 1898-1900 GEÇERSİZ; Produces listesinden çıkar, Step 3b'nin komut testi
aynen kalır ama tasdik yazıcısı olarak `runs.attest_readiness` çağrılır; `readiness.py`
`readiness_items`'ı IMPORT eder.

**Kanıt testi · sahibi:**
- **H5'in negatif kapıları — `onaylandi` uydurulamaz (Sahip: Task 8,
  `tests/test_pipeline_runs.py`):**
  `test_attest_readiness_takes_no_onaylandi_parameter` (yapısal: `inspect.signature`'da
  `onaylandi` YOK — hükmün ana ispatı) ·
  `test_attest_readiness_refuses_empty_gate_set` (boş küme) ·
  `test_attest_readiness_refuses_missing_gate_item` (eksik madde) ·
  `test_attest_readiness_refuses_unknown_item` (tanınmayan kimlik) ·
  `test_attest_readiness_refuses_signal_item_in_gate_set` (yanlış sınıf) ·
  `test_attest_readiness_refuses_gate_item_in_signal_set` (yanlış sınıf, ayna vaka) ·
  `test_attest_readiness_refuses_duplicate_item` (tekrar) ·
  `test_attest_readiness_refuses_blank_actor` (Plan 1 aktör kapısı) ·
  **pozitif kontrol:** `test_attest_readiness_persists_actor_time_and_items` — tam kapı
  kümesiyle çağrılınca kayıt DOĞAR, `onaylandi is True` ve `madde_kumesi_sha` yazılıdır.
  (Bu ad plan 1937 satırındaki `test_attest_persists_actor_and_time`'ın yerine geçer;
  **R9'un ilk yazımı bu testi Task 15'e vermişti — H5 ile yazıcının doğduğu göreve,
  Task 8'e taşınır.** R9'un SIRA düzeltmesi değişmez: yazıcı hâlâ Task 15'ten ÖNCEDİR ve
  Task 17 hâlâ değerlendirme + CLI'yi tutar.)
- **Madde kümesinin kapıları (Sahip: Task 8, `tests/test_pipeline_runs.py`):**
  `test_checklist_item_set_has_twenty_items` · `test_item_classes_are_closed`
  (`MADDE_SINIFLARI` dışında `sinif` RED) ·
  `test_gate_and_signal_sets_partition_the_item_set` (kesişim boş, birleşim tam) ·
  `test_item_ids_are_unique` ·
  `test_katman2_signal_item_is_not_a_gate_item` (15. madde `sinyal`, plan 1919-1921).
- `test_activation_succeeds_with_full_attestation_chain` (plan 1731) artık yazıcısı olan bir
  pozitif kontroldür — **Sahip: Task 15** (değişmedi).
- `test_hazirlik_onayla_writes_attestation` (plan 1943) — **Sahip: Task 17** (değişmedi;
  yalnız çağırdığı yüzeyin adı `runs.attest_readiness` olur).
- `test_checklist_is_built_from_readiness_items` (çift kayıt yasağı: `readiness.CHECKLIST`
  kimlikleri `readiness_items.MADDELER` ile birebir) · `test_checklist_has_twenty_items`
  (plan 1929'daki mevcut test, artık `readiness_items` üzerinden okur) — **Sahip: Task 17**,
  `tests/test_readiness_checklist.py`.

---

## R10 — Operatörün koşmak zorunda olduğu her adımın CLI girişi olur

**Kusur (plan satırları):** kanonik sıra ve Task 19 Step 9 (plan 2071) **yazım kapısını**
koşmayı şart koşuyor, ama Task 16'nın alt komut listesinde (plan 1781-1797) taslak yazımını
ya da K-106 yerinde güncellemeyi çağıran hiçbir komut yok. `writeback.write_draft_from_run`
ve `update_draft_from_run` (plan 1635-1636) operatör tarafından ERİŞİLEMEZ.

**Kural (kontrolör):** eksik alt komutlar eklenir.

**Bağlayıcı sözleşme — Task 16 alt komut listesine EKLENEN:**

| Alt komut | Çağırdığı servis yüzeyi | Not |
|---|---|---|
| `yazim` | `writeback.write_draft_from_run(db, run_id=…, actor=…) -> UUID` | Yazım kapısı; düzeltme koşusunu REDDEDER (plan 1658-1660) |
| `duzeltme-yaz` | `writeback.update_draft_from_run(db, run_id=…, actor=…) -> None` | K-106 yerinde güncelleme; soyağacı ZORUNLU (plan 1660-1662) |
| `deaktive-et` | `sector_package_lifecycle.deactivate_package(db, package_id=…, actor=…)` | R11 — `hedefsiz` satırın TEK çıkışı (K-38) |

Üçü de Task 16'nın genel invariantına tabidir: resmî koşu başlatan her alt komut ilk iş
olarak `contracts.require_pin` çağırır (plan 1803-1804); argparse · açık `--database-url` ·
deterministik çıktı · anlamlı çıkış kodu (plan 1799-1800).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 16** — plan 1781-1797 aralığındaki liste üç
komutla genişler. **Task 19** — Step 9 (plan 2071) artık adı konmuş bir komuta işaret eder.

**Kanıt testi · sahibi:**
- `test_yazim_subcommand_calls_write_draft_from_run` ·
  `test_yazim_subcommand_refuses_correction_run` ·
  `test_duzeltme_yaz_subcommand_calls_update_draft_from_run` ·
  `test_deaktive_et_subcommand_calls_deactivate_package` ·
  `test_every_run_subcommand_requires_pin` (plan 1828 — yeni üç komut da kapsam içindedir)
  — **Sahip: Task 16**, `tests/test_pipeline_cli.py`.

---

## R11 — Geri alma kanıtının üreticisi olur; beyan edilen çıkışın komutu olur

**Kusur (plan satırları):** (a) `rollback_package(db, *, sector_id, to_version, evidence:
RollbackGateEvidence, actor)` (plan 272) iki boolean isteyen bir kanıt sınıfı taşıyor —
ölçüldü (`sector_package_lifecycle.py::RollbackGateEvidence`, satır 116-130): `RollbackGateEvidence(manager_approved: bool,
katman1_passed: bool)`, ikisi de `bool` olmak ZORUNDA ve `_require_evidence` yalnız SINIFI
doğruluyor. `execute_rollback_plan` (plan 1074-1079) ve CLI `olay-geri-al` (plan 1791-1796)
bu iki boolean'ı **uydurmak** zorunda kalırdı — F18'in aktivasyon yolunda kapattığı deliğin
kardeş yolda süpürülmemiş hâli. (b) `hedefsiz` satırın plan metninde yazılı TEK çıkışı
deaktivasyondur (plan 1072-1073) ama CLI listesinde (plan 1781-1797) deaktivasyon komutu
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
    """İki boolean'ı da OKUR, hiçbirini kabul etmez; jetonu da BURADA basar.

    Çağıran, plan satırını `FOR UPDATE` ile ZATEN kilitlemiş olmalıdır.

    manager_approved — bu olay kimliği için kayıtlı yönetici onayı VAR MI (AÇIK-1'in
        ÜÇ koşulu: `onay_actor` · `onaylandi_at` · `onay_kapsam_sha` dolu VE kapsam
        parmak izi bugünkü satır kümesiyle EŞLEŞİYOR).
        Herhangi biri düşerse → RollbackEvidenceUnavailable.

    katman1_passed — plan satırının HEDEF sürümünü (`target_version`) üreten koşunun
        `katman1_attestation["sonuc"] == "PASS"` kaydı. Hedef paketin `run_id` bağı yoksa,
        koşu satırı yoksa, `durum != 'tamamlandi'` ise ya da tasdik yoksa
        → RollbackEvidenceUnavailable (F18: tasdik kanıttır, boolean değil).

    Köken jetonu (R8(c)) — iki boolean türetildikten SONRA:
        fingerprint = _evidence_fingerprint_from_payload(RollbackGateEvidence, payload)
        token = await mint_evidence_token(db, table="package_rollback_plans",
                    run_id=None, incident_id=incident_id, package_id=package_id,
                    fingerprint=fingerprint)
        return RollbackGateEvidence(**payload, incident_id=incident_id,
                                    package_id=package_id, provenance_token=token)
    Basım başarısızsa `EvidenceMintRefused` → çağıran onu `RollbackEvidenceUnavailable`
    gibi ele alır ve plan satırını `durum='hata'` ile kapatır.
    """
```

- `execute_rollback_plan` (plan 1074-1079) her paket için ÖNCE `build_rollback_evidence`
  çağırır; `RollbackEvidenceUnavailable` yakalanır ve o plan satırı **`durum='hata'`**
  (036'nın mevcut kapalı kümesinden — plan 797) + `reason` ile kapanır. **Yeni durum değeri
  ÜRETİLMEZ**; `hedefsiz` bu vaka için KULLANILMAZ (`hedefsiz` yalnız güvenli sürüm yokluğu
  demektir, plan 1072).
- `hedefsiz` satırların tek çıkışı `deaktive-et` alt komutudur (R10 tablosu); `olay-geri-al`
  onları ayrı başlıkta raporlar (plan 1792-1794) ve **kendiliğinden deaktive ETMEZ** —
  deaktivasyon operatörün ayrı kararıdır (K-38).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — Produces listesine
`build_rollback_evidence` + `RollbackEvidenceUnavailable` EKLENİR (plan 1074-1079 civarı);
`execute_rollback_plan`'ın gövde sözleşmesi bağlanır. **Task 16** — `deaktive-et` eklenir
(plan 1781-1797).

**DÜZELTME (fix turu 1):** ilk yazımın *"Plan 1 arayüzü DEĞİŞMEZ; `RollbackGateEvidence`
alan kümesine dokunulmaz"* cümlesi **ARTIK GEÇERSİZDİR.** R8(c) her iki kanıt sınıfına da
köken jetonu alanları ekliyor; `RollbackGateEvidence` `incident_id` · `package_id` ·
`provenance_token` kazanır (ölçülen bugünkü hâli:
`sector_package_lifecycle.py::RollbackGateEvidence`, satır 116-130 — yalnız iki `bool`).
Bu değişiklik planın *"Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER"* bölümünde **beyan
edilmiştir**; sessiz bir arayüz kırılması bırakılmaz.

**Kanıt testi · sahibi:**
- `test_build_rollback_evidence_reads_manager_approval_from_db` ·
  `test_build_rollback_evidence_reads_katman1_from_target_run_attestation` ·
  `test_build_rollback_evidence_refuses_when_target_run_unprovable` ·
  `test_executor_marks_row_hata_when_evidence_unavailable` ·
  `test_executor_never_constructs_evidence_from_literals` (yapısal: `runs.py` içinde
  `RollbackGateEvidence(` çağrısı YALNIZ `build_rollback_evidence` gövdesinde) ·
  `test_build_rollback_evidence_mints_a_single_use_token` (R8(c) ayağı: dönen kanıtın
  `provenance_token`'ı plan satırındaki `kanit_jetonu` ile aynı ve `kanit_jetonu_harcandi_at`
  hâlâ NULL) — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_deaktive_et_subcommand_calls_deactivate_package` ·
  `test_olay_geri_al_does_not_auto_deactivate_hedefsiz` — **Sahip: Task 16**,
  `tests/test_pipeline_cli.py`.

---

## R12 — Beyan edilen her dosya değişikliğinin onu YAPAN bir adımı olur

Üç ayrı vaka; her biri için karar ayrı verilir.

### R12(a) — Task 20: beyan DÜZELTİLİR · Task 6: SAHİPLİK VERİLİR

**Kusur:** Task 20 Files satırı `test_plan2_interface_contract.py` için *"(genişletilir)"*
diyor (plan 2094) ama Step 1-7'nin (plan 2096-2120) hiçbiri onu genişletmiyor.

**Karar: BEYAN DÜZELTİLİR** (kapanış görevine adım eklenmez). Dosyanın Plan 2 satırlarının
sahibi Task 3 (plan 503 · 603-605), **Task 6 (aşağıda)** ve Task 15'tir
(plan 1624 · 1742-1745); Task 20 onu yalnız **koşar** (Step 1'in tam suite'i içinde).
Kapanış görevine yeni sözleşme satırı yazdırmak kapsam eklemek olurdu.

Düzeltilmiş Files satırı:

> `- Test: apps/social/backend/tests/test_plan2_interface_contract.py` **(yalnız koşulur —
> satırlarının sahibi Task 3, Task 6 ve Task 15)**

**Geçersiz kılınan satır:** plan 2094.

#### R12(a2) — 032 MANİFESTİ: sahibi TASK 6'dır (fix turu 1, yüksek, KABUL)

**Kusur (R12(a)'nın ilk yazımının açtığı boşluk):** ilk yazım Task 20'nin sahipliğini
kaldırdı ama **hiçbir göreve vermedi.** Oysa Task 6 (migration 036) bu Python dosyasını
**kırıyor.**

**Ölçüm (2026-08-30, taze okuma):**
- `apps/social/backend/tests/test_plan2_interface_contract.py` satır 110'da
  `EXPECTED_032_MANIFEST` tanımlı; `"sector_research_artifacts"` → `"indexes"` anahtarı
  **TAM İKİ** kayıt taşıyor (satır 131-140): `sector_research_artifacts_pkey` ve
  `idx_sector_research_artifacts_slug_run`.
- `test_migration_032_relation_manifest_is_closed` (satır 350-371) kümeleri
  `observed[facet] == expected[facet]` ile **KAPALI** karşılaştırır: *"habersiz eklenmesi
  de bu testi düşürür"* (satır 355).
- 036, aynı tabloya K-09 için `UNIQUE (run_id, source, kind)` ekliyor (plan 804) → **üçüncü
  indeks** doğar → **bu Python testi DÜŞER.**
- Planın Task 6 Files satırı yalnız **SQL** dosyalarını sürüm-farkında yapıyor
  (plan 756-757); **032 SQL doğrulayıcısını sürüm-farkında yapmak bu Python manifestini
  DÜZELTMEZ** — ayrı iki artefakttır.

**Karar: TASK 6'YA SAHİPLİK VERİLİR.** Task 6 Files listesine EKLENİR:

> `- Modify: apps/social/backend/tests/test_plan2_interface_contract.py`
>   **(`EXPECTED_032_MANIFEST` indeks beklentisi sürüm-farkında yapılır — 036'nın kırdığı
>   dosyayı 036'yı yazan görev onarır)**

**İndeks adı sözleşmeyle SABİTLENİR** (katalogdan tahmin edilmez): 036'daki kısıt
`CONSTRAINT sector_research_artifacts_run_source_kind_key UNIQUE (run_id, source, kind)`
adıyla yazılır; PostgreSQL aynı adla indeks üretir.

**Task 6'ya EKLENEN adım:**

> - [ ] **Step 4c:** `tests/test_plan2_interface_contract.py`'ın 032 manifestini
>   **SÜRÜM-FARKINDA** yap. Bağlanan davranış:
>   (a) `EXPECTED_032_MANIFEST[...]["indexes"]` **iki kayıtla KALIR** — 032 tek başına
>       uygulandığında beklenen küme budur ve değişmez;
>   (b) `test_migration_032_relation_manifest_is_closed` `indexes` yüzeyini karşılaştırırken
>       **yalnız adı geçen** `sector_research_artifacts_run_source_kind_key` indeksini
>       **ek olarak kabul eder** (036 uygulanmışsa);
>   (c) **başka HERHANGİ bir fazla indeks hâlâ REDDEDİLİR** — kapalılık vaadi zayıflamaz,
>       muafiyet **tek ada** yazılır, "036 sonrası her şey serbest" DEĞİL;
>   (d) diğer dört yüzey (`columns` · `constraints` · `triggers` · `relation`) **hiç
>       gevşemez.**
>   Koş: `cd apps/social/backend && python -m pytest tests/test_plan2_interface_contract.py -v`
>   — Beklenen: PASS.

**Kanıt testi · sahibi (hepsi Task 6,
`apps/social/backend/tests/test_plan2_interface_contract.py`):**
- `test_032_manifest_alone_expects_exactly_two_artifact_indexes` — 036 uygulanmadan beklenti
  hâlâ iki kayıttır (davranışın geri uyumu).
- `test_032_manifest_accepts_named_k09_index_after_036` — 036 sonrası
  `sector_research_artifacts_run_source_kind_key` kabul edilir (pozitif kontrol).
- `test_032_manifest_still_rejects_unnamed_extra_index` — muafiyet listesinde OLMAYAN
  fazladan bir indeks eklenince test hâlâ DÜŞER (kapalılığın ispatı; Task 6 Step 2'nin
  `test_unnamed_extra_index_still_rejected` testinin Python manifest karşılığı).
- Task 6 Step 6 (plan 925-927) zaten `test_plan2_interface_contract.py`'ı adıyla sayarak
  koşuyor — bu adım o beklentiyi karşılanabilir hâle getirir.

### R12(b) — Task 5: ADIM EKLENİR

**Kusur:** Task 5 `shared/n8n-workflows/turkey-calendar-update.json`'ı değiştiriyor
(plan 679) ama bu workflow mevcut sözleşme testlerinden HİÇ geçmiyor; Task 16 Step 7b
(plan 1859-1865) aynı üçlüyü **yalnız yeni hata-bildirimi workflow'u** için ekliyor.
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
`Modify: apps/social/backend/tests/test_notifications.py` EKLENİR (plan 676-680).
**Kanıt testi · sahibi:** üç test, **Task 5**.

### R12(c) — Task 2: `_SABLON.md` beyanı DOĞRUDUR, kalemin İNİŞ YERİ yazılır

**Kusur:** Task 2 `_SABLON.md`'yi Modify diye sayıyor (plan 453) ama altı düzeltmenin ve
yedi sweep kaleminin hiçbiri oraya indiğini SÖYLEMİYOR (plan 461-479).

**Ölçüm (2026-08-30, dış depo):** `_SABLON.md:49-51` · `hakem-sentez-gorevi.md:78` ·
`hakem-denetci-gorevi.md:74` — üçü de serbest `[kanal-bağımlı: X]` etiketini taşıyor.
Yani 6. düzeltme kalemi (kanal anahtar uzayının dört değerle KAPATILMASI, plan 469-472)
**üç dosyaya birden** iner ve `_SABLON.md` beyanı DOĞRUDUR.

**Karar: BEYAN KORUNUR, kalem 6 iniş yerlerini AÇIKÇA yazar.** Düzeltilmiş kalem metni:

> 6. **Kanal anahtar uzayı dört değerle KAPATILIR** — `whatsapp_hatti` · `fiziksel_magaza` ·
>    `randevu_sistemi` · `eticaret_sitesi`. **İniş yerleri (ölçüldü 2026-08-30):**
>    `_SABLON.md:49-51` · `hakem-sentez-gorevi.md:78` · `hakem-denetci-gorevi.md:74` —
>    üçünde de serbest `X` yer alıyor. Kod tarafı Plan 1'de
>    `sector_packages.py::CHANNEL_KEYS` olarak zaten kapalı; sözleşme ona hizalanır.

**Geçersiz kılınan satırlar:** plan 469-472. **Kanıt:** Task 2 Step 1/Step 3 sweep raporunun
6. kalemi artık üç dosya + satır işaretiyle ölçülür (test değil, ölçülmüş rapor kalemi —
dürüst etiket).

---

## R13 — Ölçüm adımının sonucu ÖNCEDEN KARARLAŞTIRILMIŞ olamaz

**Kusur (plan satırları):** Task 5 Step 1 (plan 721-723) K-112 için *"Bulguya göre Task
12'nin özel gün kontrolü hizalanır. Ölçmeden bağlama"* diyor; oysa Task 12 aynı davranışı
ZATEN bağlıyor (plan 242 · 1356-1366): üretim yolunda sessiz düşüş + zorunlu maskeli log,
yazım kapısında tipli hata ile fail-closed.

**Kural (kontrolör):** **BAĞLAMA KALIR** — spec türevidir, ölçüm türevi değildir. Task 5'in
adımı dürüst şekilde yeniden adlandırılır: bugünkü davranışı, hata-enjeksiyon testinin karşı
koşacağı **regresyon TABANI** olarak kaydeder.

**Bağlayıcı sözleşme — Task 5 Step 1'in YENİ metni (plan 721-723 yerine):**

> - [ ] **Step 1:** **BUGÜNKÜ DAVRANIŞI KAYDET (K-112 regresyon tabanı — bağlama DEĞİL):**
>   takvim erişilemezken (a) özel gün enjeksiyon yolunun ve (b)
>   `sector_package_lifecycle.insert_draft`'ın bugün ne yaptığını fixture ile ölç; sonucu
>   `docs/research/2026-08-27-k112-takvim-erisilemezlik-taban.md`'ye yaz — komut + taze çıktı
>   ile (İlke 9). **Bu adım hiçbir davranışı BAĞLAMAZ ve Task 12'nin bağladığı davranışı
>   değiştirmez** (plan 230-242 · 1356-1366: bağlama spec §11/§3.4 türevidir). Ölçümün tek
>   işlevi, Task 12'nin hata-enjeksiyon testlerinin karşı koşacağı tabanı vermektir. Ölçülen
>   davranış bağlanan davranıştan farklı çıkarsa bu bir REGRESYON DEĞİL, planın istediği
>   değişikliktir ve taban notunda öyle etiketlenir.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 5** — plan 721-723 GEÇERSİZ.
**Task 12** — plan 1356-1366 ve plan 1433-1435 satırlarındaki üç K-112 testi AYNEN geçerli; bağlama
onlarındır.

**Kanıt testi · sahibi:** yeni test yok. Kapıyı kanıtlayan testler Task 12'nindir:
`test_calendar_unavailable_yields_empty_special_day_context_and_logs` ·
`test_calendar_unavailable_fails_draft_write_closed` ·
`test_calendar_unavailable_log_is_masked` (plan 1433-1435). Task 5'in çıktısı ölçülmüş bir
taban notudur, kapı değildir.

---

## R14 — Pin'in negatif invariantının sözleşme testi

Bu hüküm **R1'e katlanır** ve burada bir kez daha yazılmaz: negatif invariantın metni
(*"kirli çalışma ağacı tek başına pini düşürmez"*), onu kanıtlayan test
(`test_verify_passes_with_dirty_external_worktree`, **Sahip: Task 1**) ve commit yolunu
kapatan kalem (`kosu/` → dış depo `.gitignore`,
`test_external_repo_gitignores_run_folder`, **Sahip: Task 2**) R1'de tam metinle bağlanmıştır.

Tek ek hüküm — **çift kayıt yasağı:** aynı invariant için ikinci bir test yazılmaz ve
`verify_pin`'in kapı kümesi (plan 423-426, DÖRT kapı) **genişletilmez**; negatif invariant
bir kapı değil, kapı kümesinin **kapalılığının** ifadesidir.

---

## AÇIK-1 KAPANDI — kontrolör kararı, 2026-08-30

**Karar: B seçeneği, olay düzeyinde onay.** `social.package_rollback_plans` ÜÇ kolon kazanır:

```sql
onay_actor      text        NULL,   -- onayı veren yönetici kimliği
onaylandi_at    timestamptz NULL,   -- onay zamanı
onay_kapsam_sha text        NULL,   -- onaylanan satır KÜMESİNİN kanonik parmak izi

CONSTRAINT package_rollback_plans_onay_butun
  CHECK (num_nonnulls(onay_actor, onaylandi_at, onay_kapsam_sha) IN (0, 3)),
  -- üçü BİRLİKTE dolar, BİRLİKTE boşalır

CONSTRAINT package_rollback_plans_onay_actor_dolu
  CHECK (onay_actor IS NULL OR btrim(onay_actor) <> '')
  -- boş/yalnız-boşluk kimlik onay SAYILMAZ
```

**Neden üç kolon ve iki CHECK — fix turu 1 bulgusu (yüksek, KABUL).** İlk yazımın tek
CHECK'i `(onay_actor IS NULL) = (onaylandi_at IS NULL)` idi ve **ölçüldü ki
`onay_actor = ''` değerini KABUL EDER**: iki kolon da NULL olmaz, kısıt geçer, ve
`build_rollback_evidence` **boş kimlikli bir onay** için `manager_approved=True` üretirdi —
R11'in yasakladığı uydurulmuş boolean'ın veri katmanından gelen hâli. İkinci kusur: onay
**onayladığı satırlara BAĞLI DEĞİLDİ** — onaydan sonra bir satırın `target_version`'ı
değişse bile satır "yönetici onaylı" görünmeye devam ederdi.

**Ayak (b) — servis katmanında fail-closed aktör doğrulaması, Plan 1'in KENDİ kapısıyla.**
Ölçüldü: Plan 1'in kanonik aktör kapısı `sector_package_lifecycle._require_actor`'dır
(`sector_package_lifecycle.py`, satır 147-150): `isinstance(actor, str)` değilse ya da
`actor.strip()` boşsa `ValueError("actor zorunlu — sahipsiz yaşam döngüsü işlemi yazılmaz")`
fırlatır, aksi hâlde **kırpılmış** kimliği döner. `runs.approve_incident_rollback` ve
`runs.attest_readiness` (R9) **bu kapıyı kullanır**; `runs.py` onu açıkça alır:

```python
from app.services.sector_package_lifecycle import _require_actor as require_actor
```

Ad modül-özeldir; buna rağmen **ikinci bir aktör kuralı yazmak yerine özel bir adı yeniden
kullanmak** bilinçli tercihtir — iki kapı iki davranış demektir ve ekin kapattığı sınıf tam
olarak budur. Kolona yazılan değer `require_actor`'ın döndürdüğü **kırpılmış** kimliktir,
dolayısıyla `btrim(onay_actor) <> ''` CHECK'i servis yolunda hiç tetiklenmez; CHECK, servis
dışı bir yazımın (elle SQL, gelecekteki ikinci çağıran) son savunmasıdır.

**Ayak (c) — onay, olayın KANONİK satır kümesine MÜHÜRLENİR.**

```python
# runs.py  (Task 8)
def incident_scope_sha(rows: Sequence[Mapping]) -> str:
    """Olayın kanonik satır kümesinin parmak izi.

    Girdi: o `incident_id`'ye ait `durum='bekliyor'` satırların
    `(package_id, observed_active_version, target_version, evidence_class)` dörtlüleri;
    `package_id` metnine göre ARTAN sıralanır ve `identity.canonical_sha` (Task 3, K-92)
    ile hash'lenir. İkinci bir hash kuralı YAZILMAZ.
    """
```

- `approve_incident_rollback` damgalayacağı satır kümesi üzerinde bu değeri hesaplar ve
  **damgaladığı HER satıra AYNI değeri** yazar.
- `build_rollback_evidence` kilitli plan satırını okuduğunda olayın **BUGÜNKÜ** kanonik
  satır kümesi üzerinde değeri **yeniden hesaplar**; satırdaki `onay_kapsam_sha` ile
  eşleşmiyorsa `RollbackEvidenceUnavailable` fırlatır. Yani onaydan sonra kümeye satır
  eklenmesi, satır çıkarılması ya da bir hedefin değişmesi onayı **geçersiz kılar** — yeni
  bir `olay-onayla` gerekir. Uydurma YOK, sessiz devam YOK.

**Ayak (d) — onaylanmış satırın kimlik/hedef alanları DEĞİŞMEZ (tetikleyici).** Mekanizma
032'nin `sector_research_artifacts_append_only` tetikleyicisinin aynısıdır (ölçüldü:
`032_sector_packages.sql`'de `BEFORE UPDATE OR DELETE ... FOR EACH ROW EXECUTE FUNCTION` deseni
`032_sector_packages.sql` satır 49-51'de zaten kullanılıyor):

```sql
CREATE FUNCTION social.reject_approved_rollback_plan_mutation() RETURNS trigger AS $$
BEGIN
  IF OLD.onay_actor IS NOT NULL AND (
       NEW.incident_id             IS DISTINCT FROM OLD.incident_id
    OR NEW.package_id              IS DISTINCT FROM OLD.package_id
    OR NEW.observed_active_version IS DISTINCT FROM OLD.observed_active_version
    OR NEW.target_version          IS DISTINCT FROM OLD.target_version
    OR NEW.evidence_class          IS DISTINCT FROM OLD.evidence_class
  ) THEN
    RAISE EXCEPTION 'onaylanmış geri alma planı satırının kimlik/hedef alanları değiştirilemez';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER package_rollback_plans_approved_immutable
  BEFORE UPDATE ON social.package_rollback_plans
  FOR EACH ROW EXECUTE FUNCTION social.reject_approved_rollback_plan_mutation();
```

**Aşırı kilitleme YOK:** `durum` · `reason` · `onay_*` · `kanit_jetonu_*` kolonları
onaydan SONRA da güncellenebilir — yürütücü onları yazar. Kilitlenen yalnız **neyin
onaylandığını tanımlayan beş alandır.**

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
    (`onay_actor`, `onaylandi_at`, `onay_kapsam_sha`); damgalanan satır sayısını döner.

    - `actor` **Plan 1'in kanonik kapısından** geçer: `require_actor` (yani
      `sector_package_lifecycle._require_actor`, satır 147-150). Boş/whitespace/`str`
      olmayan kimlikte `ValueError` fırlar ve **HİÇBİR satır damgalanmaz** (fail-closed;
      kısmi damgalama YOK — tek işlem).
    - `durum='bekliyor'` OLMAYAN satırlar damgalanmaz (tamamlanmış/hatalı/hedefsiz iş
      geriye dönük onaylanamaz).
    - `onay_kapsam_sha` = `incident_scope_sha(<damgalanacak satırlar>)`; damgalanan HER
      satıra AYNI değer yazılır.
    - Zaten damgalı satır TEKRAR damgalanmaz — ilk onay korunur (idempotent).
    - Hiç satır damgalanmadıysa 0 döner; çağıran bunu hata olarak raporlar.
    """
```

Böylece operatör TEK komut çalıştırır, N satır damgalanır, ve yürütücünün satır-başına
okuması yerel ve atomik kalır.

**`build_rollback_evidence`'ın `manager_approved` ayağı bağlanır — ÜÇ koşul birden:**
kilitli plan satırının `onay_actor` · `onaylandi_at` · `onay_kapsam_sha` alanlarının
**ÜÇÜ de** dolu VE `onay_kapsam_sha`, olayın **bugünkü** kanonik satır kümesi üzerinde
yeniden hesaplanan değere **EŞİT** ise `True`; biri düşerse
`RollbackEvidenceUnavailable` (uydurma YOK). Alan `bool`'a çevrilirken herhangi bir
varsayılan/`.get` düşüşü KULLANILMAZ. Boş/whitespace kimlik veri katmanına zaten giremez
(`package_rollback_plans_onay_actor_dolu` CHECK'i), servis katmanına da giremez
(`require_actor`) — **iki katmanda birden fail-closed.**

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 6** — `package_rollback_plans`
şemasına ÜÇ onay kolonu + İKİ CHECK + BİR değişmezlik tetikleyicisi, ve (R8(c) gereği)
DÖRT jeton kolonu + BİR CHECK eklenir (plan 795-800 aralığını genişletir). **Task 8** —
`approve_incident_rollback` · `incident_scope_sha` Produces listesine eklenir;
`build_rollback_evidence`'ın `manager_approved` kaynağı bu kolonlardır. **Task 16** —
`olay-onayla` alt komutu eklenir (plan 1781-1797).

**Kanıt testi · sahibi:**
- **Şema kapıları — Sahip: Task 6, `tests/test_migration_036.py`:**
  `test_rollback_plan_approval_columns_exist_and_nullable` (ÜÇ kolon) ·
  `test_rollback_plan_approval_requires_all_three_or_none`
  (`num_nonnulls(...) IN (0,3)`; bir ya da iki kolon dolu → CHECK RED) ·
  **`test_rollback_plan_approval_rejects_blank_actor`** (`onay_actor=''` ve `'   '` →
  CHECK RED — H7'nin ana ispatı) ·
  `test_approved_plan_row_target_version_is_immutable` ·
  `test_approved_plan_row_identity_is_immutable` (`incident_id` · `package_id` ·
  `observed_active_version` · `evidence_class`) ·
  `test_approved_plan_row_status_and_reason_still_updatable` (aşırı kilitleme YOK —
  pozitif kontrol) ·
  `test_unapproved_plan_row_fields_still_editable` (tetikleyici yalnız onaylı satırı
  kilitler — pozitif kontrol).
- **Servis kapıları — Sahip: Task 8, `tests/test_pipeline_runs.py`:**
  `test_approve_incident_stamps_only_bekliyor_rows` ·
  `test_approve_incident_is_idempotent_and_keeps_first_approver` ·
  `test_approve_incident_returns_zero_when_nothing_pending` ·
  **`test_approve_incident_refuses_blank_actor`** (`''` · `'   '` · `None` → `ValueError`,
  hiçbir satır damgalanmaz) ·
  `test_approve_incident_uses_plan1_actor_guard` (yapısal: `runs.py` `require_actor`
  DIŞINDA `strip()`-tabanlı ikinci bir aktör kontrolü içermez) ·
  `test_approve_incident_writes_same_scope_sha_to_every_stamped_row` ·
  `test_incident_scope_sha_uses_identity_canonical_rule` ·
  `test_build_rollback_evidence_refuses_when_plan_row_unapproved` (negatif kontrol) ·
  `test_build_rollback_evidence_true_only_when_all_three_approval_fields_set` ·
  **`test_build_rollback_evidence_refuses_when_incident_scope_grew`** (onaydan sonra
  bekleyen satır eklendi → RED) ·
  **`test_build_rollback_evidence_refuses_when_incident_scope_shrank`** (onaylı satır
  kümeden çıktı → RED) ·
  `test_build_rollback_evidence_accepts_unchanged_scope` (pozitif kontrol).
- `test_olay_onayla_subcommand_stamps_incident` ·
  `test_olay_onayla_subcommand_refuses_blank_actor` — **Sahip: Task 16**,
  `tests/test_pipeline_cli.py`.

---

## AÇIK — kontrolörün kararı gerekiyor

> **AÇIK-1 kapandı** (yukarıda; gövdesi kararın dayanağı olarak korunuyor).
> **AÇIK-2 fix turu 1'de açıldı, AYNI TURDA KAPANDI** (kontrolör kararı, 2026-08-30).

## AÇIK-2 KAPANDI — kontrolör kararı, 2026-08-30

**Karar: A seçeneği — `geri-al` olay kimliği İSTER.** Alt komut listede KALIR, ama imzası
`geri-al --incident-id <id> --package-id <id>` olur ve kanıtını R8(c) jetonundan, yani
`social.package_rollback_plans` satırından alır. Olay kimliği olmayan geri alma yolu YOKTUR.

**Gerekçe — B'nin maliyeti sanılandan büyük, A'nın maliyeti sanılandan küçük.**

*A'nın maliyeti küçük, çünkü acil kol ETKİLENMİYOR (ölçüldü — bu, kararı çeviren bulgudur).*
İlk değerlendirmemde "acil durumda üç komut koşturmak fazla" diye B'ye meylettim; bu YANLIŞTI.
K-38'in acil kolu `deaktive-et`'tir, kanıt zinciri İSTEMEZ ve bu kararla değişmez. Yani
"kötü aktif paketi hemen indir" hâlâ TEK komuttur. A'nın kapattığı tek şey *"önceki sürüme
kanıtsız dön"*dür — ve o acil bir hamle değil, sürüm seçimi içeren düşünülmüş bir hamledir.
Düşünülmüş hamlenin kanıt zincirinden geçmesi maliyet değil, kuralın kendisidir.

*B'nin maliyeti kalıcı ve büyüyen bir kirlilik.* Tek-paketlik sarmalayıcı olaylar `etki-analizi`
raporlarına gerçek K-145 olaylarıyla aynı uzayda düşer; "olay" terimi iki anlama gelir ve
zamanla hangi satırın gerçek bir kural-sürümü olayı olduğunu ayırmak için ikinci bir ayrım
kolonu gerekir. Bu, kaçınmaya çalıştığımız ikinci-kimlik-uzayı sınıfının aynısıdır (bkz.
teknik karar 23: `attempt` ikinci kimlik uzayı olduğu için KALDIRILMIŞTI).

*C reddedildi* çünkü tek-paketlik geri alma gerçek bir ihtiyaçtır (bir sektörün paketi kötü
çıkar, kural sürümü değil); komutu silmek o ihtiyacı `olay-plani` + `olay-geri-al` çiftine
zorlar ve hiçbir şey kazandırmaz — A zaten aynı zinciri, adı doğru komutla sunar.

**Bağlanan hüküm:**

- `geri-al` alt komutu KALIR; imzası `geri-al --incident-id <id> --package-id <id> --actor <kimlik>`.
- Tek-paketlik geri alma da bir olay planı satırı ister; onu `olay-plani` üretir.
  **Tek satırlık olay meşrudur** — `olay-plani` bir paketle çağrılabilir; sentetik/örtük
  olay ÜRETİLMEZ, operatör olayı açıkça açar.
- Onay adımı (`olay-onayla`) HER İKİ ölçekte de zorunludur — tek pakette de, N pakette de.
  Onay yolu tekildir; ikinci bir kapı listesi YOKTUR.
- **`deaktive-et` bu karardan ETKİLENMEZ** (K-38): kanıt zinciri istemez, tek komuttur,
  acil kol olarak kalır. Bu, A'nın kabul edilebilir olmasının SEBEBİDİR ve burada yazılıdır
  ki ileride "acil durumda üç komut" diye yanlış hatırlanmasın.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 16** — `geri-al` alt komutunun
imzası bağlanır (plan 1797 civarındaki listede adı KALIR, parametreleri EKLENİR).

**Kanıt testi · sahibi:**
- `test_geri_al_requires_incident_id` (olay kimliğisiz çağrı REDDEDİLİR) ·
  `test_geri_al_refuses_when_plan_row_unapproved` (negatif kontrol) ·
  `test_geri_al_succeeds_on_approved_single_row_incident` (pozitif kontrol) ·
  `test_deaktive_et_needs_no_incident_and_no_evidence` (acil kolun etkilenmediğinin kanıtı)
  — **Sahip: Task 16**, `tests/test_pipeline_cli.py`.

---

### AÇIK-2 (KAPANDI — kararı yukarıda): Olay planına bağlı OLMAYAN bir geri alma nasıl kanıt bulur?

**Neden açık — R8(c)'nin mekanik yan etkisi.** R8(c) `RollbackGateEvidence`'ın köken
jetonunu `social.package_rollback_plans` satırına bağlıyor; `rollback_package` jetonu
`(incident_id, package_id)` anahtarıyla tüketiyor. Bunun sonucu şudur: **plan satırı
OLMAYAN bir geri alma artık mümkün değildir.** Oysa Task 16'nın alt komut listesinde
(plan 1797) olay kimliğinden bağımsız bir **`geri-al`** komutu duruyor. İki ifade
çelişiyor ve seçim maliyet farkı taşıyor — kendi başıma kapatmıyorum.

| Seçenek | Nasıl | Maliyet / etki |
|---|---|---|
| **A — `geri-al` olay kimliği İSTER** | Operatör önce `olay-plani`, sonra `olay-onayla`, sonra `geri-al --incident-id`. Tek yol kalır, kanıt zinciri tekilleşir | Kanıt/onay/iz üçlüsü TEK yoldan geçer; acil durumda operatörün üç komut koşması gerekir. K-38 acil kolu (`deaktive-et`) zaten kanıtsızdır ve **etkilenmez** — yani "aktif sürümü hemen indirme" yolu kapanmaz, kapanan yalnız "önceki sürüme kanıtsız dönme"dir |
| **B — `geri-al` tek satırlık örtük olay planı yazar** | Komut kendi `incident_id`'sini üretir, tek satırlık plan yazar, onay adımını **yine ister** | Operatör tek komut koşar; ama "olay" kavramı iki anlama gelir (gerçek K-145 olayı ve tek-paketlik sarmalayıcı) ve `etki-analizi` raporları bu sentetik olaylarla kirlenir |
| **C — `geri-al` KALDIRILIR** | Tek geri alma yolu `olay-geri-al`'dır; `geri-al` alt komutu plan listesinden çıkar | En az yüzey; ama plan gövdesinde adı geçen bir komutu silmek Task 16'nın beyanını değiştirir ve tek-paketlik geri alma için ayrı bir kolaylık kalmaz |

**Bloklama etkisi:** karar **Task 16 uygulanmadan ÖNCE** gerekir. Karara kadar R8(c)'nin
tüketici sözleşmesi (jeton `(incident_id, package_id)` ile tüketilir) **bağlıdır ve
değişmez**; değişecek olan yalnız `geri-al` alt komutunun var olup olmadığı ve olay
kimliğini nereden aldığıdır. R11'in geri kalanı (katman1 ayağı, `hata` düşüşü,
`deaktive-et` çıkışı, kapsam mührü) karardan bağımsız olarak bağlıdır.

---

### AÇIK-1 (KAPANDI — kararı yukarıda): Olay geri alması için yönetici onayı NEREDE kayıtlanır?

**Neden açık:** R11 kanıt üreticisinin *"kayıtlı yönetici onayı"*ndan okumasını bağlıyor,
ama planın hiçbir yerinde bir olay-geri-alma onayını **kaydeden** yüzey yok: `olay-plani`
plan satırlarını yazar (plan 1789-1791), `olay-geri-al` yürütür (plan 1791-1796); arada
kayıtlı bir onay adımı yoktur. Üretici bir yerden okumak zorunda, ve o yerin seçimi maliyet
farkı taşıyor — kendi başıma kapatmıyorum.

| Seçenek | Nasıl | Maliyet / etki |
|---|---|---|
| **A — Outbox kaydı** | Yeni CLI alt komutu `olay-onayla` → `notifications.record_admin_event(kind="sektor_paketi.olay_geri_alma_onayi", idempotency_key=<incident_id>)`; üretici `social.admin_events`'ten okur | Migration DEĞİŞMEZ; mevcut idempotency sözleşmesi yeniden kullanılır. Ama outbox bir **bildirim kuyruğudur**, onay deposu olarak kullanılması amacının biraz dışıdır |
| **B — Plan satırında kolon** | `social.package_rollback_plans`'e `onay_actor text NULL` + `onaylandi_at timestamptz NULL`; `olay-onayla` onları yazar, üretici tek satırdan okur | Anlamsal olarak en temiz (onay, onayladığı planın yanında durur) ve tek-satır okuması atomik. Ama **Task 6'nın migration 036 şemasını değiştirir** (plan 795-800) ve Task 6'nın test listesine iki CHECK testi ekler |
| **C — Onay adımı YOK** | `execute_rollback_plan` yönetici onayını komutun kendisinin çalıştırılmasından sayar | R11'in *"çağıran-taraflı boolean ASLA"* hükmüyle ÇELİŞİR — kaydı olmayan onay, uydurulmuş boolean'ın adı değişmiş hâlidir. Bu yüzden burada yalnız tamlık için sayılıyor |

**Bloklama etkisi:** karar verilene kadar `build_rollback_evidence`'ın `manager_approved`
ayağı tek noktada (fonksiyonun içinde) okunur ve karar kapanınca **yalnız o nokta** değişir;
R11'in geri kalanı (katman1 ayağı, `hata` düşüşü, `deaktive-et` çıkışı) karardan bağımsız
olarak bağlıdır. Karar Task 8 uygulanmadan ÖNCE gerekir; B seçilirse Task 6'dan önce
gerekir.
