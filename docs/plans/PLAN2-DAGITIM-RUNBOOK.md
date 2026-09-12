# Plan 2 — Ön-Pilot Dağıtım Runbook'u

> **Kaynak görev:** `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` Task 18.
> **Bağlayıcı ek:** `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md` (R1).
> Çelişkide EK GEÇERLİDİR.

**Bu belge yazıldığı anda HİÇBİR ADIM KOŞULMAMIŞTIR.** Aşağıdaki her adımın
"Ölçüm" satırı dağıtımı yapan kişi tarafından TAZE çıktıyla doldurulur;
"koşmalı" / "geçmeli" bir ölçüm değildir (İlke 3 + İlke 9).

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
- **Ölçüm:** _(doldurulacak — üç koşumun da rc'si)_

### Adım 2 — Canlıya uygula

Aynı komut biçimi, dosya dosya. **Geri dönüş noktası:** uygulamadan hemen önce
alınan `pg_dump` ve o anın HEAD sha'sı buraya yazılır.

- Geri alma: §4'e bak — hangi rejimde olduğun veriye bağlıdır.
- **Ölçüm:** _(doldurulacak — geri dönüş noktası + iki dosyanın rc'si)_

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
- **Ölçüm:** _(doldurulacak — iki komutun canlıdaki çıktısı)_

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
- **Ölçüm:** _(doldurulacak)_

### Adım 5 — Operatör adaptörü

`~/.claude/commands/sektor-paket.md` kurulur ve **bir alt komut gerçekten
çağrılarak** sınanır. Kurulu ama çalışmayan adaptör sessiz arızadır.

**Not (2026-09-12 ölçümü):** dosya geliştirme makinesinde MEVCUT. Bu, dağıtım
ortamında da kurulu olduğunu göstermez — adaptör operatörün makinesinde yaşar
ve dağıtım hedefine göre ayrıca doğrulanır.

- Geri alma: dosyayı kaldır.
- **Ölçüm:** _(doldurulacak — çağrılan alt komut + çıktısı)_

### Adım 6 — Takvim ucu

Takvim ucunun dönem alanını döndürdüğü ve önbelleğin bayat kalmadığı ölçülür.

- **Ölçüm:** _(doldurulacak)_

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
- **Ölçüm:** _(doldurulacak — üç import + iki smoke)_

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
- **Ölçüm:** _(doldurulacak)_

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
- **Ölçüm:** _(doldurulacak — tablo başına ayrı)_

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
