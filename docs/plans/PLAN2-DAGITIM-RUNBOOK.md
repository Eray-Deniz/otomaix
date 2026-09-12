# Plan 2 — Ön-Pilot Dağıtım Runbook'u

> **Kaynak görev:** `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` Task 18.
> **Bağlayıcı ek:** `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md` (R1).
> Çelişkide EK GEÇERLİDİR.

**KOŞUM DURUMU — 2026-09-12.** Adım 1·2·3(CLI ayağı)·4·8b KOŞULDU ve ölçümleri
aşağıda taze çıktıyla yazılıdır. Adım 3'ün SERVİS ayağı · Adım 5 · 6 · 7 ve
Adım 9'un yetki KALDIRMA ayağı KOŞULMADI; her biri kendi satırında sebebiyle
etiketlidir. "koşmalı" / "geçmeli" bir ölçüm DEĞİLDİR (İlke 3 + İlke 9).

**ORTAM ÖLÇÜMÜ (bloker çıktı, çözüldü):** veritabanı sunucusu **PostgreSQL
18.3** (Docker: `pgvector/pgvector:pg18`, 5433'e eşlenmiş); host üzerindeki
istemci araçları **16.15**. `pg_dump` daha yeni sunucuyu **reddeder**
(`server version: 18.3; pg_dump version: 16.15`) — yani host'un `pg_dump`'ı ile
geri dönüş noktası ALINAMAZ. Çözüm: döküm ve klon işlemleri konteynerin KENDİ
araçlarıyla (`docker exec … pg_dump/createdb/pg_restore`) koşulur. `psql` ile
migration UYGULAMAK 16→18 yönünde sorunsuzdur (ölçüldü). Host'a 18 istemcisi
kurmak da bir seçenektir; kurulmadı.

---

## 0. Neden bu görev pilottan ÖNCE gelir

Pilot (Task 19) kuyumculuğun ilk `active` paketini **035/036 tablolarıyla ve
yeni CLI ile** üretmek zorundadır. İkisi de o noktada canlıda kurulu değilse:
atılabilir bir test veritabanında koşmak vaat edilen canlı paketi ÜRETMEZ,
canlıda koşmak ise kurulu olmayan şema yüzünden DÜŞER. Bu bir **sıra
bağımlılığıdır**, uygulama ayrıntısı değil.

## 1. Dağıtım öncesi kalite kapısı (Step 0)

Dördü de geçmeden Adım 2'ye geçilmez.

| # | Kapı | Nasıl ölçülür | Durum |
|---|------|----------------|-------|
| a | Tam test kümesi TAZE | `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` | geçen/kalan sayısı YAZILIR |
| b | Katman-1 tam sweep | `.venv/bin/python -m pytest tests/prompt_regression/ -q` | tek bayt fark YOK |
| c | Sözleşme pin'i | `.venv/bin/python -m pytest tests/test_contract_pin.py -q` | dış depo ile monorepo aynı sürümde |
| d | `/review-claude-codex` + `/security-review-claude-codex` KOŞMUŞ; açık `critical`/`high` YOK | raporlar `docs/reviews/` ve `docs/security-reviews/` | açık kalemler aşağıda |

**(d) kapısının bilinen durumu (2026-09-12):** S-7 (critical) Eray kararıyla
`accepted_risk` etiketlidir — çözülmedi, PARK EDİLMEDİ, açık risk kabulüdür;
gerekçe ve yeniden açılma koşulu `docs/active/sektor-bilgi-paketi-plan2/TASK.md`
Open Problems'ın ilk kaleminde. S-6 (medium, kanıt boşluğu) **Adım 7'den ÖNCE**
karara bağlanır: takvim workflow'u SQL'i string birleştirmeyle kuruyor ve o
workflow bu runbook'un Adım 7'sinde import ediliyor.

---

## 2. Sıra — BAĞLAYICIDIR

Geri alma TERS sıradadır. **"git revert" veritabanı için geri alma DEĞİLDİR.**

### Adım 1 — Prova (canlı klonda, canlıda DEĞİL)

```bash
# 035 ve 036 DOSYA DOSYA, tek işlemde:
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 --single-transaction \
  -f shared/db/migrations/035_holiday_periods.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 --single-transaction \
  -f shared/db/migrations/036_package_runs.sql
# up-down-up:
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f shared/db/migrations/rollback/036_down.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f shared/db/migrations/rollback/035_down.sql
# ...ardından ikisini tekrar ileri koş.
```

- **Bu prova YALNIZ pilot-ÖNCESİ rejimi kanıtlar** (§4 (a)).
- Veri varken aynı yolun fail-closed durduğu Task 6'nın testlerinde kanıtlanır,
  burada DEĞİL.
- Geri alma: prova klonu atılır.
- **Ölçüm (2026-09-12, KOŞULDU — PROVA GEÇTİ):** klon canlının `pg_dump -Fc` +
  `pg_restore` kopyasıdır (242 nesne, `social` şemasında 31 tablo — canlıyla aynı).
  İleri `035`→`036` rc=0/0 · geri `036_down`→`035_down` rc=0/0 · tekrar ileri
  rc=0/0. **Toplam 6 koşum, 6'sı da rc=0.**
  Yapısal doğrulama: ileri sonrası `sector_package_runs` · `package_rollback_plans` ·
  `brand_sub_sector_history` VAR → geri sonrası ÜÇÜ DE YOK → tekrar ileri sonrası
  ÜÇÜ DE VAR. 035'in kolon ayağı ayrıca ölçüldü: `public_holidays.end_date`
  1 → 0 → 1 (geri alma kolonu gerçekten DÜŞÜRÜYOR, sessizce bırakmıyor).

### Adım 2 — Canlıya uygula

Aynı komut biçimi, dosya dosya. **Geri dönüş noktası:** uygulamadan hemen önce
alınan `pg_dump` ve o anın HEAD sha'sı buraya yazılır.

- Geri alma: §4'e bak — hangi rejimde olduğun veriye bağlıdır.
- **Ölçüm (2026-09-12, KOŞULDU):** geri dönüş noktası
  `/root/otomaix-deploy-backups/canli-035-036-oncesi-20260912-145056.dump`
  (188 KB, 0600, `pg_restore -l` ile 242 nesne okunabilir doğrulandı); o andaki
  HEAD `ab91495`, dal `feat/sektor-bilgi-paketi-plan2`.
  `035` rc=0 · `036` rc=0 (yalnız üç `NOTICE: trigger … does not exist, skipping`).
  Canlı doğrulama: beş tablonun beşi de VAR · `public_holidays.end_date` VAR ·
  üç tetikleyicinin üçü de kurulu · artefakt tür kümesi dört değerli
  (`research`/`review`/`synthesis`/`mechanical_gate`).

### Adım 3 — Arka uç + CLI dağıtımı

Coolify servisi `otomaix-social-backend` (bkz. `apps/social/backend/CLAUDE.md`).

**DSN ARGV'YE YAZILMAZ** (S-3 güvenlik düzeltmesi): CLI bağlantı dizesini
`--database-url-file <0600 dosya>` ya da `--database-url-env <DEĞİŞKEN ADI>`
ile alır; düz `--database-url` argümanı YOKTUR ve ortamdan sessiz miras da yok.

```bash
python scripts/sector_pipeline_cli.py --help
# Bağlantıyı fiilen kuran salt-okunur smoke — henüz koşu yokken bile geçerli:
python scripts/sector_pipeline_cli.py --database-url-env DATABASE_URL \
    durum --run-id <koşu-kimliği>
```

Henüz hiç koşu açılmadıysa var olmayan bir kimlik `koşu satırı yok: <id>` ile
fail-closed döner — **bu çıktının kendisi bağlantının kurulduğunu kanıtlar**;
"bağlandı" varsayımı DEĞİL, ölçümdür. Alternatif salt-okunur smoke:
`python scripts/sector_sweep.py --database-url-env DATABASE_URL --dry-run`.

- Geri alma: önceki imaja dön (şemaya DOKUNMAZ).
- **Ölçüm (2026-09-12, CLI ayağı KOŞULDU):** `--help` rc=0 ·
  `durum --run-id 2026-09-12-yok-0001` → `koşu yok: 2026-09-12-yok-0001`
  (fail-closed çıktı, bağlantının kurulduğunun KANITI) ·
  `sector_sweep.py --dry-run` → `differences: 0`, iki marka eşlendi.
- **KOŞULMADI — SERVİS AYAĞI.** Coolify servisi (`otomaix-social-backend`) hâlâ
  ESKİ imajı koşuyor: bu dal push EDİLMEDİ ve deploy TETİKLENMEDİ. Yukarıdaki
  ölçümler CLI'yi çalışma ağacından canlı VERİTABANINA karşı koşar; canlı API'nin
  yeni kodu taşıdığını GÖSTERMEZ.

### Adım 4 — Dış sözleşme deposu

Dış araştırma deposu pinlenen commit'e getirilir; doğrulama **dağıtılmış
kullanıcı bağlamından** koşulur (geliştirme makinesinden DEĞİL):

```python
from app.services.sector_pipeline import contracts
contracts.require_pin(PIN_PATH, REPO_ROOT)   # sessiz dönüş = geçti
```

- Pin manifesti: `shared/contracts/research-contracts.pin.json`.
- **Pin dış deponun HEAD commit'ini de karşılaştırır** — depoda yapılan HER
  commit pin'i bayatlatır ve `commit` alanı güncellenmeden koşu başlamaz.
- Geri alma: dış depoyu önceki commit'e al + pin'i geri çevir.
- **Ölçüm (2026-09-12, KOŞULDU):** `contracts.require_pin(pin, /root/otomaix-sosyal-medya-arastirmasi)`
  → sessiz dönüş = GEÇTİ. Pin commit'i `c3f0d30` (yeniden türetilen brief).

### Adım 5 — Operatör adaptörü

`~/.claude/commands/sektor-paket.md` kurulur ve **bir alt komut gerçekten
çağrılarak** sınanır. Kurulu ama çalışmayan adaptör sessiz arızadır.

**Not (2026-09-12 ölçümü):** dosya geliştirme makinesinde MEVCUT. Bu, dağıtım
ortamında da kurulu olduğunu göstermez — adaptör operatörün makinesinde yaşar
ve dağıtım hedefine göre ayrıca doğrulanır.

- Geri alma: dosyayı kaldır.
- **KOŞULMADI.** Adaptör geliştirme makinesinde mevcut ama dağıtım hedefinde
  doğrulanmadı; hedef, servis ayağı dağıtılana kadar belirsizdir.

### Adım 6 — Takvim ucu

Takvim ucunun dönem alanını döndürdüğü ve önbelleğin bayat kalmadığı ölçülür.

- **KOŞULMADI.** Takvim ucu dağıtılmış SERVİSTE yaşar; servis ayağı henüz
  dağıtılmadı (Adım 3).

### Adım 7 — n8n workflow'ları

Üç workflow import + aktive edilir:
`turkey-calendar-update.json` (dönem-farkında yeni sürüm) ·
`sector-package-admin-events.json` (`errorWorkflow` bağlı) ·
`n8n-error-notifier.json`.

- **ÖN KOŞUL:** S-6 kararı (takvim workflow'unun SQL'i) bu adımdan ÖNCE verilir.
- **DEPO ↔ CANLI SAPMASI GERÇEKTİR** (2026-09-12 ölçümü): körlemesine import
  canlıdaki ayarı siler. n8n'e yazmadan ÖNCE canlıyı oku, düğüm bazında
  karşılaştır, yalnız `nodes` + `connections` yükle, sonra tek tek doğrula.
- Sentetik bir olayla TEK teslim smoke'u, sentetik bir hatayla TEK
  hata-bildirimi smoke'u koşulur.
- Geri alma: workflow'ları pasife al + önceki JSON'u geri yükle.
- **KOŞULMADI — ÖN KOŞUL AÇIK.** S-6 kararı verilmedi; takvim workflow'u bu
  adımda import ediliyor. Ayrıca depo↔canlı sapması düğüm bazında
  karşılaştırılmadan import YAPILMAZ.

### Adım 8 — `git` ikilisi ve ortam değişkenleri (Step 8b)

`contracts.verify_pin` dış deponun commit'ini `git rev-parse` ile okur. İkili
yoksa **resmî koşuyu başlatan HER CLI alt komutu** ilk adımda patlar.

```bash
git --version
env | grep -E '^(GIT_DIR|GIT_WORK_TREE)=' && echo "SET — pin YABANCI depoyu okur" || echo "set DEGIL"
```

- `GIT_DIR`/`GIT_WORK_TREE` set ise `rev-parse` yanlış depoyu okur ve pin
  yabancı bir commit'e karşı karşılaştırılır. İkili yoksa bu bir **dağıtım
  blokeridir**, sessizce geçilmez.
- **Ölçüm (2026-09-12, KOŞULDU):** `git version 2.43.0` — ikili VAR.
  `GIT_DIR` / `GIT_WORK_TREE` **set DEĞİL** (pin kendi deposunu okur). Bu adım
  bloker üretmedi.

### Adım 9 — Yazma yetkisinin kaldırılması (K-103 (b))

Task 15 Step 6'nın etkin-yetki ölçümü "yetki var" dediyse API rolünün yazma
yetkisi kaldırılır ve **negatif yazma denemesiyle** doğrulanır.

**KAPSAM — ÜÇ TABLO (arayüz eki A2):** `social.sector_packages` ·
`social.sector_package_runs` · `social.package_rollback_plans`. Son ikisinde
**jeton kolonları** (`kanit_jetonu` · `kanit_jetonu_parmakizi` ·
`kanit_jetonu_basildi_at` · `kanit_jetonu_harcandi_at`) özellikle sınanır —
o iki tabloya `UPDATE` edebilen kod **kendi kanıtı için jeton basabilir**.

- Negatif deneme **her tablo için AYRI** koşulur; çıktısı buraya yazılır.
- Ölçüm "yetki yok" dediyse kaldıracak bir şey yoktur; bu da **ölçülmüş çıktı
  olarak** kaydedilir ("varsayıldı" DEĞİL).
- Önceki ölçüm: `docs/research/2026-09-10-k103b-etkin-yetki-olcumu.md`
  (M-1: uygulama için superuser OLMAYAN rol · M-2: 036 dağıtıldıktan SONRA
  ölçüm yeniden koşulur).
- **Ölçüm (2026-09-12, M-2 gereği 036 DAĞITILDIKTAN SONRA koşuldu):**
  - (a) API kimliği `otomaix`; **`rolsuper = True`**; `social.sector_packages`
    tablosunun **sahibi de aynı rol**.
  - (b) Katalog grant'ları üç tabloda da tam küme
    (`DELETE,INSERT,REFERENCES,SELECT,TRIGGER,TRUNCATE,UPDATE`).
  - (c) Jeton kolonlarının dördü de her iki tabloda YERİNDE.
  - (d) Negatif yazma denemesi (geri alınan işlem + eşleşmeyen `WHERE`), tablo
    başına AYRI: **üçü de KABUL EDİLDİ** → yazma yetkisi ETKİN olarak VAR.
- **YETKİ KALDIRMA AYAĞI KOŞULMADI — ve `REVOKE` ile KOŞULAMAZ.** Rol hem
  **superuser** hem **tablo sahibi**: superuser grant denetimini atlar, sahip
  zaten tam haklıdır. Yani "API rolünün yazma yetkisini kaldır" hükmü bu kimlikle
  uygulanamaz; gereken şey **M-1**'dir — uygulama için superuser OLMAYAN, tabloların
  sahibi OLMAYAN ayrı bir rol ve DSN değişikliği. Bu, canlı kimliği değiştirir ve
  uygulamanın TAMAMINI etkiler; **Eray kararı gerektirir**, yürütücü tek başına
  uygulamaz.
- **KARAR (2026-09-12, Eray):** M-1 `repo-public-exposed-live-credentials` turunda
  yapılacak — ikisi de canlı kimliği oynatır, tek seferde değiştirilir. Yetki
  dağılımı ölçüldü ve aktif katmanda yazılı (22 tablo yazma · 4 kanıt tablosu
  yalnız okuma · şema düzeyi yetki yok). Uygulamadan önce **klonda tam tur**
  zorunludur. Bu adım Task 18'i bloklamaz; ölçüm yapıldı, kaldırma TARİHLİ eve bağlandı.

---

## 3. Sözleşme deposu da bir dağıtım kalemidir

`require_pin` dış depoyu pinlenen commit'te bekler. Depo yoksa ya da bayatsa
CLI **fail-closed** durur — yani kurulum yapılmadan komut ailesi hiç çalışmaz.
Bu bir "opsiyonel ortam hazırlığı" değil, dağıtımın kendisidir.

---

## 4. F20 — İKİ AYRI GERİ ALMA REJİMİ (karıştırılmaz)

İlk yazım koşulsuz ters-sıra geri alma vaat ediyordu. Ama pilot bir onay/ret
olayı ya da koşu satırı ürettikten SONRA şemayı geri almak ya teknik olarak
başarısız olur (daraltılan CHECK mevcut satıra takılır) ya da denetim izini
imha eder.

### (a) PİLOT ÖNCESİ — şema geri alması GEÇERLİDİR

Plan 2 verisi henüz yoktur; `036_down` → `035_down` temiz koşar. Adım 1'in
provası tam olarak bunu kanıtlar.

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f shared/db/migrations/rollback/036_down.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f shared/db/migrations/rollback/035_down.sql
```

Ters sıra bağlayıcıdır. `036_down` kendi preflight'ında Plan 2 verisi sayar ve
veri varsa **hiçbir şeye dokunmadan** durur.

### (b) PİLOT SONRASI — şema geri alması BİR SEÇENEK DEĞİLDİR

**Bu rejimde "şema geri alma YOK" hükmü geçerlidir.** `036_down` veri varken
fail-closed durur (Task 6); zorlamak denetim izini imha etmek olurdu.

Geri dönüş yolu **veri-koruyan İLERİ DÜZELTME migration'ıdır**:

1. Kusur tespit edilir ve kapsamı ölçülür (hangi satırlar, hangi koşular).
2. Yeni numaralı bir migration yazılır; mevcut satırları **korur**, gerekiyorsa
   yeni kolon/kısıt ekler ya da mevcut veriyi dönüştürür.
3. Kendi geri alması yine bu iki rejime göre sınıflanır.
4. Uygulama tarafı (kod) ayrıca geri alınabilir — kod geri alması şema geri
   alması DEĞİLDİR ve şemayı bozmaz.

**Burada sessiz bir vaat BIRAKILMAZ:** pilot koştuktan sonra "her şeyi geri
alırız" cümlesi YANLIŞTIR ve bu belge onu açıkça reddeder.

---

## 5. Bu runbook ne KANITLAMAZ

- Hiçbir adımın koşulduğunu (yazıldığı an hepsi boştur).
- Canlı ortamın hazır olduğunu.
- S-6 ve S-7'nin çözüldüğünü — ikisi de açık, biri risk kabulü etiketli.
