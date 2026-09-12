---
task: sektor-bilgi-paketi-plan2
written: 2026-09-12
---

# Resume From

**Sıradaki iş: Task 18 (ön-pilot dağıtım) — ama canlıya dokunan adımları KAPALI.**
Task 18'in kendi Step 0(d) kapısı "açık critical varken dağıtım başlamaz" diyor ve **S-7 açık**
(aşağıda). Canlıya dokunmayan kısımlar serbest ve sıradaki iş oradan başlar:
dağıtım runbook'u (`docs/plans/PLAN2-DAGITIM-RUNBOOK.md`, henüz YOK) · migration uygulama ve
**iki ayrı geri alma rejimi** (F20: pilot-öncesi şema geri alması · pilot-sonrası veri-koruyan
ileri düzeltme) · mekanik kapı raporunun artefakt türü · köken jetonu (M-1/M-2) · F6 ·
`kuyumculuk.md`'nin şablondan yeniden türetilmesi. Canlıya girme kararı Eray'da.

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → beklenen `4404 passed`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Push durumu buraya YAZILMAZ, ölç:
`git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`
(oturum sonunda origin'in ÖNÜNDE, push edilmedi — Eray onayı olmadan push yok).
**Yürütme durumu:** kip `inline` · başlangıç çapası `a806e29` · defter penceresi `a806e29`.

**Bu oturumun commit'leri (6):** `b7e3fd8` defter düzeltmesi · `e2b3396` güvenlik düzeltmeleri ·
`608cc25` güvenlik raporu · `60a62b4` kapanış turu düzeltmeleri · `bc5ea96` kapanış kaydı ·
`0389ef0` telegram arıza ölçümü. Defter kapısı her commit sonrası `rc=0`.

**Güvenlik raporu:** `docs/security-reviews/2026-09-12-feat-sektor-bilgi-paketi-plan2.md`
(dual, attempt-2 kapanışıyla birlikte). Ham kanıt: `~/.claude/logs/otomaix--ffc87809/`
`2026-09-12-secreview-*-1.md` (Codex tur 1) · `-1.claude.md` (alt-hakem tur 1) · `-2.md` (Codex kapanış).

## Bu oturum ne yaptı — tek cümle

Task 18'in Step 0(d) kapısı olarak dual güvenlik review'ı koştu; bir critical + üç high bulundu,
Eray kararıyla aynı oturumda düzeltildi, kapanış turu iki kalemi hâlâ açık ölçtü ve düzeltmenin
kendi açtığı gerilemeyi buldu — üçü de kapatıldı; ayrıca Telegram onay akışının Nisan'dan beri
canlıda çalışmadığı ölçüldü.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları:**

- Tam takım `.venv/bin/python -m pytest tests/ -q`:
  - `b7e3fd8` (defter düzeltmesi) → **4379 passed**, 320 s
  - `e2b3396` (güvenlik düzeltmeleri) → **4397 passed**, 320 s
  - `60a62b4` (kapanış düzeltmeleri) → **4404 passed in 322.65s**, 0 failed
- Katman-1 sweep + pin testleri (`tests/prompt_regression/` + `test_contract_pin.py`) → **156 passed**,
  tek bayt fark yok (Task 18 Step 0(b)+(c)).
- **Mutasyon:** birinci parti 6/6 · ikinci parti 7/7 kapı düştü (toplam 13/13). Betik:
  scratchpad'de, kapılar üretimden tek tek susturulup ilgili test koşuldu.
- **Hakem turları:** attempt-1 dual (alt-hakem 66 araç / 671 s; Codex ilk çağrı `rc=124` timeout →
  120 s canlılık probu `PROBE-OK` → 1200 s tekrar `rc=0`) · attempt-2 dual kapanış (alt-hakem
  51 araç / 793 s; Codex `rc=0`, 91 komut).
- **Sertleştirilmiş denetçi komutu gerçekten koşuldu** (3 prob): paket içi dosya OKUNDU, göreli
  (`../disarida.txt`) ve mutlak (`/etc/hostname`) paket dışı hedefler ENGELLENDİ — aracın kendi
  metni: *"is outside <cwd>; --restricted confines the file tools to the working directory"*.
- **Canlı n8n ölçümü (API, salt-okunur + iki yazma):** `Telegram İçerik Onay` son gerçek koşum
  **2026-04-13**, o tarihten beri yok · canlı webhook başlıksız ve yanlış başlıklı isteği de
  kabul etti (ikisi de `200`) · CRM-1/2/3 `active=False` (defter doğru) · `Telegram Onayla` ve
  `Telegram Reddet` **`active=True`** (S-7 canlı) · `Otomaix Telegram Approval Key` kimliği
  YARATILDI (`qbPEK2DKQgMmFor8`), düğüme **bağlanmadı**.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **`60a62b4` (kapanış düzeltmeleri) bağımsız hakem GÖRMEDİ** — stop-rule otomatik üçüncü pas
  açmaz, karar insana bırakılır. Üçüncü tur istenirse dar kapsamlı koşulur.
- **S-7 kapatılmadı** (aşağıda) · **S-6 kanıt-boşluğu kararı verilmedi**.
- **`queryReplacement` bağlaması canlı n8n'de koşularak doğrulanmadı** (yerel n8n yok) — CRM-3
  import edildikten sonra tırnaklı bir `account_id` ile tek prob şart.
- **Telegram arızasının hangi kapıda kırıldığı BELİRLENEMEDİ** — Eray o sırada onay gönderemedi
  (arayüz düzenleniyor). Dört aday aktif katmanda yazılı.
- **DSN kanalının canlı veritabanına bağlandığı uçtan uca koşulmadı** (`.env` okuması izin
  kurallarınca reddediliyor).
- **Uçtan uca CLI koşumu YOK**; yeni sözleşme biçiminde gerçek araştırma çıktısı YOK (ilk ölçüm Task 19).
- `ruff`/`pyright` ortamda YOK.

# Risks

- **S-7 (critical, AÇIK, canlıda aktif)** — `tg-approve` / `tg-reject` uçları kimliksiz GET ve
  n8n'in yetkili kimliğiyle sahiplik denetlenmeden yayına alma/reddetme yaptırıyor. **Task 18'in
  Step 0(d) kapısını kapalı tutan tek kalem budur.** Üç seçenek kayıtlı: (a) iki workflow'u
  pasife al — dakikalar, defterde "gerçek müşteride koşmuyor" ölçümü var; (b) imzalı/süreli/tek
  kullanımlık bağlantı jetonu — tasarım turu ister; (c) explicit risk kabulü.
- **Canlı kurulum eksik (deploy ön koşulu):** `N8N_TELEGRAM_APPROVAL_SECRET` (değer
  `/root/otomaix-tg-approval.secret`, 0600) + kimliğin düğüme bağlanması. Bu dal deploy edilir de
  değişken set edilmezse onay isteği **503** döner (sessiz kayıp DEĞİL, açık hata). CRM tarafı
  (kimlik + `N8N_CRM_EVENT_SECRET` + import) **Eray kararıyla ertelendi** — o üç workflow canlıda
  zaten pasif, maliyetsiz.
- **S-2 kalıntısı** — denetçi hapsi CLI düzeyindedir, işletim sistemi değil; alt süreç aynı
  kullanıcı altında koşar. Gerçek süreç izolasyonu (kapsayıcı/ad-alanı ya da araçsız
  yapılandırılmış-çıktı API'si) YAPILMADI.
- **S-6 (medium, kanıt boşluğu)** — takvim workflow'u SQL'i string birleştirmeyle kuruyor;
  mekanizma doğrulandı, istismar doğrulanmadı. **Task 18 Step 6 o dosyayı import ediyor** → karar
  o adımdan önce gerekli.
- **`repo-public-exposed-live-credentials`** — depo public, anahtarlar ilk commit'ten beri açıkta
  ve bugünkülerle aynı (2026-09-06 ölçümü). Evi verilmiş: **Plan 2 yürütmesi biter bitmez, ilk iş.**
- Önceki oturumlardan devralınan kabul edilmiş riskler aynen (N1/1 · F6 · çok günlü bayramlar ·
  normalize edicinin `î` düşürmesi · 035 dağıtılana kadar üç dönem "sistemde yok" · attest_readiness
  prob sonuçlarını görmez · kilit sözleşmesi · `recovered` bakım penceresi · migration 036 yerinde ·
  commit geçmişi tek-commit TDD modeline uymuyor · plan hakem görmeden onaylandı).

# Notes For Claude/Codex

**Sonraki oturumun girdisi:** Task 18'in canlıya dokunmayan kalemleri (runbook + F20 iki rejim +
artefakt türü + köken jetonu + F6 + `kuyumculuk.md` yeniden türetme). Canlı adımlar S-7 kararına bağlı.

**Bu oturumda öğrenilenler:**
1. **Hakem kapsamını docs'tan ayırmak giderim kaydını kör eder.** "docs/ içinde bulgu arama"
   talimatı yüzünden iki hakem de Telegram token'ının 2026-09-06'da döndürüldüğünü göremedi ve
   yanlış bir high üretti. Kontrolör "bu daha önce çözüldü mü" taramasını KENDİ yapmalı.
2. **Sınıf kapısı varyant yamamaktan fazlasını bulur.** CRM webhook'u için yazılan kapı üç webhook
   daha buldu (ikisi diff dışındaydı, iki hakem de görmemişti) — biri düzeltildi, ikisi S-7 oldu.
3. **Yasak listesi açık uçludur.** İlk sertleştirme `Read`/`Glob`/`Grep`/`Skill` + 20 aracı açık
   bıraktı; kapanış turu bunu koşarak ölçtü. Pozitif küme (`--tools`) + `--restricted` gerekti.
4. **Ad sezgisi kimlik taşıyan URL'leri kaçırır.** `REDIS_URL` maskelenmiyordu; sınıflandırma
   değerin biçimine de bakmalı.
5. **Fail-closed kapı, çağıranın durum mutasyonundan ÖNCE gelmeli.** Aksi hâlde "gönderildi"
   görünen ama gitmemiş ve kurtarılamayan kayıt üretir (kapanış turu bunu yakaladı).
6. **Depo↔canlı sapması gerçek:** `telegram-content-approval.json` canlıdan farklıydı; körlemesine
   import canlıdaki ayarı silerdi. n8n'e yazmadan ÖNCE canlıyı oku, düğüm bazında karşılaştır.
7. **Canlı uca prob atmak yan etki üretir** — iki hatalı koşum (`55910`, `55911`) benim probumdur;
   kayda geçirildi.

**Codex çağrısı kurarken:** COMPANION + PROMPT çağıran kabukta; prompt dosyası SETUP fence sonrası
Write ile; uzun turlar arka planda 1200 s; çağrı sonrası `rc` + koşum sayısı + son cümle üçünü
kontrol et. 480 s'de `rc=124` alırsan reflekssel degrade etme — önce canlılık probu.
