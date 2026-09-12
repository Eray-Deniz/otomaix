# Security Review (dual): sektör bilgi paketi Plan 2 — dağıtım öncesi kapı — 2026-09-12

coverage_mode: diff
- Review aralığı: `d5d72e1a43260b6061c109f2ff298951a39d5470..b7e3fd8fcab72ae9de0ec57888946afd7cc32787`
  (BASE_REF `origin/main`; merge-base = BASE_SHA; 241 commit, 86 dosya, güvenlik yüzeyi 39 dosya)
Reviewers: fresh Claude subagent (general-purpose) + Codex (`adversarial-review --base`)
dual-review: true (claude_status: ran; codex_status: ran — ilk çağrı `rc=124` timeout, 120 s canlılık probu `PROBE-OK` sonrası 1200 s ile tekrar `rc=0`)
codex_breadth: full-diff
coverage_gap: false
Scan substrate: pinned worktree @ HEAD_SHA (`/tmp/secreview-wt.LUvV8U/wt`); untracked files: not reviewed
Secret exclusion: none (kapsamda sır taşıyan path yok — preflight ölçüldü)
secret-exposure-risk-accepted: false
Main tree at review: clean
Tetikleyen: Task 18 (ön-pilot dağıtım) Step 0(d) kalite kapısı — dağıtım bu review'dan ÖNCE başlamaz.

> **DÜZELTME TURU AYNI OTURUMDA KOŞTU (Eray kararı 2026-09-12).** Bu komut tasarım gereği
> rapor-üretir/kod-yazmaz; kullanıcı talimatıyla düzeltmeler bu oturumda yapıldı. Her bulgunun
> altında **Durum** satırı vardır. Düzeltme sonrası tam takım: **4397 passed, 0 failed**
> (komut: `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q`, 320 s; taban 4379).
> Kapanış hakem turu bu düzeltmelerin ARDINDAN koşar — "düzeltildi" iddiası henüz hakem görmedi.

---

## Critical

### S-1 — Kimlik doğrulamasız CRM webhook'ları, canlı veritabanı kimliğiyle SQL'e string olarak giren gövde alanı
- **severity: critical** · `[single-source: codex]` · **kontrolör ölçümüyle doğrulandı**
- `shared/n8n-workflows/crm-automations.json` — `CRM-1/2/3` webhook düğümleri; `CRM-3 → Add Payment Tag` postgres düğümü

**Ölçülen (kontrolörün kendi koşumu, artefakt düzeyinde):**
- Üç webhook düğümünde de `authentication` parametresi **YOK**: `crm/new-customer`, `crm/plan-upgrade`, `crm/payment-failed`.
- `Add Payment Tag` düğümü: `operation=executeQuery`, sorgu
  `INSERT INTO crm.account_tags (account_id, tag, added_by) VALUES ('{{ $json.body.account_id }}', ...)` —
  istek gövdesinden gelen değer **tırnaklı SQL literal'inin içine** gömülüyor, parametre bağlama yok.
- Kullanılan kimlik: `Postgres account` (canlı credential).
- Dosyadaki altı workflow da `active: true`.

**Bu dalın payı:** sınıf ÖNCEDEN VARDI (webhook'lar bu dalda yazılmadı), ancak `9a46948`
(`fix(n8n): pin the live postgres credential and read the webhook wrapper`) artefaktı
yer tutucu kimlikten **canlı** kimliğe taşıdı. Yani artefakt bugün import edilirse operasyoneldir.

**Neden critical:** internete açık, kimliksiz bir uçtan gelen gövde alanı, `crm` ve `social`
şemalarına erişebilen bir veritabanı rolü altında sorgu yapısını değiştirebilir.

**CANLI DURUM — defterden okundu (bu oturumda yeniden ölçülmedi):** üç workflow **2026-09-07'de
canlıda PASİFE ALINDI** ve o gün ölçüldü — üçü de `active=False`, `POST` artık `404`, n8n çalıştırma
geçmişinde bu üç workflow'un **sıfır** koşumu var (`docs/active/CURRENT.md`,
`crm-webhooks-unauthenticated-sql-interpolation`). Yani canlı maruziyet zaten kapatılmıştı; bugün
inen şey **onarımın kendisidir** (pasifleştirme bir kapatmadır, düzeltme değil — defterin kendi
ifadesi). Bu oturumda n8n API'sine bakılmadı: anahtar `.env` içinde ve `.env` okuması izin
kurallarınca koşulsuz reddediliyor.

**DURUM: KOD TARAFI KAPANDI (2026-09-12).** Üç webhook `headerAuth` + `Otomaix CRM Event Key`
credential'ı taşıyor; `Add Payment Tag` sorgusu `$1` + `options.queryReplacement` ile bağlandı;
çağıran (`billing._notify_crm_n8n`) kabul başlığını gönderiyor ve sır boşsa çağrıyı HİÇ yapmıyor
(fail-closed). Sınıf kapısı kuruldu: `test_no_webhook_node_is_unauthenticated` +
`test_no_postgres_query_embeds_an_n8n_expression` — dizindeki HER webhook ve HER Postgres düğümü,
elle seçilmiş örnek değil. 6/6 mutasyon kapıları düşürdü.
**CANLI TARAF AÇIK:** n8n'de iki credential yaratılmalı ve ortam değişkenleri set edilmeli
(aşağıdaki "Elle yapılacaklar"). Set edilene kadar CRM bildirimleri GİTMEZ — bilinçli fail-closed.

**Düzeltme (Codex önerisi + kontrolör notu):** üç webhook düğümüne `headerAuth` + ayrı credential;
çağıran tarafların o başlığı göndermesi; `account_id`'nin UUID olarak doğrulanması; sorgunun
parametreli hâle getirilmesi. Ayrıca artefakttaki `active: true` bayrağı, dosya import edildiğinde
otomatik açılmayacak şekilde ele alınmalı. Tarama deseni: **her** n8n webhook'u ve `{{...}}`
içeren **her** postgres sorgusu.

---

## High

### S-2 — Dış kaynaklı araştırma metni, kum havuzsuz ve ortamı miras alan kodlama ajanlarına veriliyor
- **severity: high** · `[both-agree]` · kontrolör ölçümüyle doğrulandı
- `apps/social/backend/app/services/sector_pipeline/auditors.py:1562-1577` (argv), `:1708-1734` (`SubprocessRunner.run`), `synthesis.py:730`

**Ölçülen:** `ARAC_KOMUTLARI` iki denetçiyi **asimetrik** kuruyor —
`denetci-2` → `codex exec --skip-git-repo-check --sandbox read-only ...` (kum havuzu açık);
`denetci-1` ve `sentez` → `claude -p --output-format text` (izin kipi yok, araç kısıtı yok,
ayar dosyası yok, kum havuzu yok). `subprocess.run` çağrısında `env=` verilmiyor → alt süreç
çağıranın **tüm** ortam değişkenlerini miras alıyor. Global ayar dosyasında `permissions.allow`
içinde çıplak `Bash`, `Write`, `Edit` var ve `defaultMode: auto`.

**Saldırı yolu:** araştırma turunda taranan bir web kaynağı `EK-*-KAYNAK-n.md` dosyasına talimat
düşürür → denetim/sentez turunda kısıtsız ajan o metni okur → şema doğrulaması **daha koşmadan**
dosya/ortam okuma, araç kullanımı veya ağ üzerinden sızdırma yapabilir. Hash pinleme ve yapısal
rapor doğrulaması bayt kimliğini kanıtlar, **talimat güvenilirliğini değil**.

**ÖLÇÜLMEDİ:** canlı bir enjeksiyon koşumu yapılmadı; argv kısıtsızlığı, `env=` yokluğu ve izin
listesi dosyadan okundu. Yani mekanizma ölçüldü, istismar uçtan uca gösterilmedi.

**DURUM: KAPANDI (2026-09-12).** `claude` argv'si artık `--permission-mode plan`
`--strict-mcp-config` `--disallowedTools Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch,Task`
taşıyor; `SubprocessRunner` alt sürece BEYAZ LİSTELİ ortam veriyor (PATH·HOME·LANG·LC_ALL·
LC_CTYPE·TERM·TMPDIR) — çağıranın sırları artık miras kalmıyor. Sınıf kapısı: her araç izolasyon
profilini beyan eder, bilinmeyen ikili fail-closed düşer. 4/4 mutasyon kapıları düşürdü.
Bayraklar kurulu CLI'ya karşı ölçüldü (mevcut tripwire her koşumda yeniden ölçer) VE sertleştirilmiş
komut gerçekten koşuldu (minimal ortamla, çıktı alındı) — "bayrak yardımda var" ile yetinilmedi.

**Düzeltme:** `claude` argv'sini `codex` ile simetrik sertleştir (kısıtlı izin kipi + araç yasak
listesi + sertleştirilmiş ayar dosyası) **veya** araçsız yapılandırılmış-çıktı API'sine geçir;
alt süreci beyaz listeli minimal ortamla (`env=`) doğur; kaynak/rapor bloklarını güvenilmez veri
olarak etiketle — ama prompt metnini güvenlik sınırı SAYMA. Kapı testi: kanarya fixture'ı
(paket dışı dosya/ortam okuma, iş dizini dışına yazma, yetkisiz geri çağrı) — üçü de düşmeli.

### S-3 — Veritabanı bağlantı dizesi zorunlu komut satırı argümanı
- **severity: high** · `[both-agree]` — ham severity ayrıştı (Claude: high · Codex: medium), **yükseltildi**
- `apps/social/backend/scripts/sector_pipeline_cli.py:142-146` (`required=True`), `:1335`

**Ölçülen:** `--database-url` zorunlu argüman; parola taşıyan DSN süreç `argv`'sine yazılıyor.
Bu makinede `/proc` `hidepid` **olmadan** bağlı (`proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)`)
→ `/proc/<pid>/cmdline` herkese okunabilir. Ayrıca kabuk geçmişine ve her `ps` çıktısına düşer.

**Severity uzlaştırması (mekanik max() DEĞİL):** iki gerekçenin premisi de ampirik doğrulandı.
Claude'un ek ayağı — S-2 ile zincirleme: `denetim`/`sentez` alt komutları bağlantı AÇIKKEN
kısıtsız alt süreci doğuruyor, o süreç `/proc/<ppid>/cmdline` okuyarak `.env`'e hiç dokunmadan
üretim parolasını alabilir — ve bu ayağın iki premisi de (hidepid yok · alt süreç kısıtsız)
ölçüldü. Doğrulama sonrası tereddütte güvenlik-temkinli taraf alındı: **high**.
(Bu bir YÜKSELTME olduğu için `severity_downgrade` kapısı gerekmez.)

**DURUM: KAPANDI (2026-09-12).** DSN argv'den çıkarıldı: `--database-url-env <DEĞİŞKEN ADI>`
ya da `--database-url-file <0600 dosya>`. Eski bayrak sessizce kaldırılmadı — kullanıldığında
sebebini söyleyerek reddediyor. Dosya kanalı grup/dünya okumasına karşı fail-closed. Korunan
tasarım kararı: `DATABASE_URL` hâlâ sessizce okunmaz. **Sınıf kapatıldı:** kardeş `sector_sweep.py`
da aynı kanala geçti (aynı delik oradaydı, review onu görmemişti) ve depo dışındaki operatör
adaptörü (`~/.claude/commands/sektor-paket.md`) hizalandı.
**ÖLÇÜLMEDİ:** kanalın canlı veritabanına gerçekten bağlandığı uçtan uca koşulmadı — DSN `.env`'de
ve `.env` okuması izin kurallarınca reddediliyor; birim testleri çözüm yolunu kapsıyor.

**Düzeltme:** DSN'i korumalı dosya tanıtıcısı/stdin ya da 0600 dosya üzerinden al; ortam
değişkeni ancak "alt süreç ortamı temizlenir" politikası belgeliyse kabul edilebilir —
ve model alt süreçlerine miras KALMAMALI.

### S-4 — Telegram bot token'ı git geçmişinde — ~~rotasyon yapılmamış~~ **PREMİS ÇÜRÜDÜ**
- **ham severity: high** → **final severity: low** · `[single-source: claude]`
- **Disposition: `rejected` (bulgunun bloklayan ayağı), kalanı `documented_residual`**
- `shared/n8n-workflows/crm-automations.json`, `turkey-calendar-update.json` (geçmiş)

**Ölçülen:** HEAD'de token deseni **0 eşleşme** (temiz). Geçmişte en az **4 commit**
(`cbf6c08`, `b815774`, `af1c7bc`, `bf726f6`) dosyada gerçek token desenini taşıyor; bu dalın
`dadb343` commit'i token'ı credential referansına taşıdı — doğru hamle, ama **geçmişten silmek
değil**. Depoya klon erişimi olan herkes (yedek, CI cache, eski worktree, ileride eklenecek
işbirlikçi) değeri geri okuyabilir. Token değeri bu raporda ve log dosyalarında **yok**.

**ÖLÇÜLMEDİ:** token'ın hâlâ geçerli olup olmadığı (canlı API'ye sır gönderilmedi).

**PREMİS ÇÜRÜTÜLDÜ (2026-09-12) — hakemin "rotasyon yapılmamış" ayağı YANLIŞTI.**
Kullanıcı düzeltti, ardından defterden ölçtüm: token **2026-09-06'da BotFather'dan döndürüldü** ve
**eskisinin öldüğü ölçüldü (`401 Unauthorized`)**; sekiz düğüm `telegramApi` credential'ına
bağlandı (`dadb343`), yedi workflow 2026-09-07'de canlıya import edildi ve yükleme sonrası tek tek
ölçüldü (çıplak token 0). Kaynak: `docs/active/CURRENT.md` — `n8n-workflow-sir-hijyeni` kalemi.

**Neden hakem bunu göremedi (kapsam dersi):** iki hakeme de "docs/ ve tests/ içinde bulgu arama"
talimatı verildi; oysa GİDERİM KAYDI tam orada, aktif katmanda yaşıyor. Güvenlik hakemine "bu
bulgu daha önce giderildi mi" sorusunun cevabının nerede durduğu ayrıca söylenmeli.

**KALAN (documented_residual, low):** ölü token git geçmişinde ve `docs/archive/
CLAUDE_crm_pre_cleanup.md` içinde duruyor; tarama kapısı yalnız `shared/n8n-workflows/`e bakar.
Token ölü olduğu için istismar değeri yok — temizlik hijyen kalemi, güvenlik kapısı değil.
**AÇIK KALAN AYRI BORÇ (defterde zaten kayıtlı):** `Telegram account` credential'ının YENİ tokenla
güncellenip güncellenmediği hiç ölçülmedi (`telegram-credential-live-token-unverified`) — token
ölüyse yönetici bildirim zinciri sessizdir ve kimse haberdar olmaz.

**Düzeltme:** BotFather'dan iptal/yenile (dosyadan silmek iptal etmez) → n8n credential'ını
güncelle → geçmiş temizliği isteniyorsa `git filter-repo`, istenmiyorsa rotasyonu kayıt altına al.

---

## Düzeltme turunun AÇTIĞI / ORTAYA ÇIKARDIĞI bulgular

Bu iki kalem hakem raporlarında YOKTUR — düzeltme sırasında kurulan sınıf kapıları ve kendi
ölçümüm ortaya çıkardı. Kaydedilmeseler "review temizdi" izlenimi yanlış olurdu.

### S-7 — Telegram onay/ret uçları: kimliksiz GET, yetkili kimlikle vekil işlem (YENİ, AÇIK)
- **severity: critical** · kaynak: **sınıf kapısının kendisi** (iki hakem de görmedi — dosyalar
  incelenen diff'in DIŞINDAydı) · kontrolör ölçümüyle doğrulandı
- `shared/n8n-workflows/telegram-onayla.json` (`tg-approve`), `telegram-reddet.json` (`tg-reject`)

**Ölçülen:** iki uç da `GET`, `authentication` YOK. `tg-approve`, sorgu dizesinden aldığı
`post_id` ile `POST https://api.otomaix.com/posts/{post_id}/publish-now` çağırıyor; `tg-reject`
aynı biçimde `PATCH .../internal/posts/{post_id}/status`. İkisi de n8n'in sakladığı
`httpHeaderAuth` kimliğini kullanıyor → **vekil karışıklığı (confused deputy)**: bağlantıyı
bilen/üreten herhangi biri, sahipliği hiç denetlenmeden herhangi bir gönderiyi yayına alabilir ya
da reddedebilir. Ayrıca ikisi de Telegram bot token'ını **sorgu dizesinden** alıp
`https://api.telegram.org/bot{{...}}/sendMessage` URL'ine gömüyor (URL yolunu çağıran belirliyor).

**Kısmen ZATEN KAYITLI:** bot şifresinin sorgu dizesinde dolaşması aktif katmanda
`telegram-approval-token-in-query-string` olarak duruyor (2026-09-06'da ölçülmüş, parked).
**Bu bulgunun YENİ ayağı yetkilendirmedir:** kimliksiz bir GET'in, n8n'in yetkili kimliğiyle
sahiplik denetlenmeden yayına alma/reddetme yaptırabilmesi — defterdeki kalem şifre sızıntısını
anlatıyor, bu ayağı değil.

**Neden bu turda KAPATILMADI — dürüst etiket:** uçları tarayıcı çağırıyor (Telegram mesajındaki
buton), yani `headerAuth` kapatılacak kapı değildir. Doğru kapanış imzalı/süreli bir bağlantı
jetonudur ve backend tarafını da değiştirir — tasarım kararı, tek başıma yapılmadı.
**Çözülmedi, park edildi; evi burasıdır** ve test kapısında gerekçeli bir istisna satırı olarak
görünür (`WEBHOOK_KIMLIK_ISTISNALARI`), sessiz muafiyet DEĞİL.

### S-8 — Ayar nesnesinin temsili bütün sırları basıyordu (YENİ, KAPANDI)
- **severity: high** · kaynak: kontrolörün kendi ölçümü (bir test hatası sırasında gözlendi)
- `apps/social/backend/app/core/config.py`

**Ölçülen:** pydantic'in varsayılan temsili tüm alanları basıyor; tek bir `AttributeError` metni
veritabanı parolasını, Supabase servis anahtarını, fal.ai · R2 · Upload-Post · ElevenLabs ·
HeyGen · Apify · YouTube · Serper anahtarlarını ve dâhilî API anahtarını birden yazdırdı. Aynı yol
her yığın izinde, her `print(settings)`'te ve hata izlemeye giden her çerçeve yerelinde açıktı.

**DURUM: KAPANDI (2026-09-12).** `Settings.__repr__`/`__str__` sır taşıyan alanları maskeliyor;
teşhis ölmüyor (alan adları ve sırsız değerler görünür). Maskeleme **alan adından türetiliyor**
(`_sir_alani_mi`), elle bakılan liste değil — yarın eklenen `YENI_API_KEY` de kendiliğinden
kapsanır; istisnalar (`R2_BUCKET_NAME`, `R2_PUBLIC_URL`) açıkça sayılı.

**KALAN RİSK — ölçülmüş bağlamıyla:** bu değerlerin bir kopyası, maskeleme eklenmeden ÖNCE bu
oturumun kaydına düştü. **Ancak yeni bir maruziyet sınıfı DEĞİL:** aktif katmandaki
`repo-public-exposed-live-credentials` kalemi, AYNI anahtarların (Supabase servis anahtarı · R2
çifti · fal.ai · Upload-Post · Redis) deponun ilk commit'inden beri **public GitHub'da** durduğunu
ve bugünkülerle aynı olduğunu 2026-09-06'da ölçmüş; rotasyonun evi de verilmiş (Plan 2 yürütmesi
biter bitmez, sıralı liste). Yani bu oturum kaydı o listeyi DEĞİŞTİRMEZ, yalnız aciliyetini
teyit eder. Yeni bir rotasyon kalemi AÇILMADI — var olanın kopyası olurdu.

---

## Elle yapılacaklar (kod değil — Eray)

1. **n8n'de iki YENİ kimlik yarat** (Header Auth — bunlar bugün doğdu, canlıda yoklar):
   `Otomaix CRM Event Key` (id `otomaixCrmEvtKey`), başlık adı `X-Crm-Event-Key`;
   `Otomaix Telegram Approval Key` (id `otomaixTgApprovalKey`), başlık adı `X-Telegram-Approval-Key`.
   **Karıştırmamak için:** bunlar webhook'un KABUL kontrolüdür; mesaj gönderen `Telegram account`
   (`VMbwUuFB8BzVhxEz`) bambaşka bir kimliktir ve zaten canlıda kurulu.
2. **Ortam değişkenlerini set et** (Coolify): `N8N_CRM_EVENT_SECRET` ve
   `N8N_TELEGRAM_APPROVAL_SECRET` — n8n'deki başlık değerleriyle AYNI.
   **Uyarı:** set edilene kadar CRM ve Telegram onay bildirimleri GİTMEZ (bilinçli fail-closed).
3. **Üç workflow dosyasını n8n'e yeniden import et** (`crm-automations.json`,
   `telegram-content-approval.json`) — dosya düzeltildi, canlı ORTAM değişmedi.
4. ~~Telegram bot token'ını yenile~~ — **GEREKMİYOR, 2026-09-06'da yapılmış** (kullanıcı
   düzeltmesi + defter kaydı; eski token ölü ölçüldü). Bu satır hatalı bir bulgudan doğmuştu.
5. **S-7 kararı:** imzalı bağlantı jetonu tasarımı mı, uçların kapatılması mı.
6. **Operatör alışkanlığı değişti (S-3):** `sector_pipeline_cli.py` ve `sector_sweep.py` artık
   `--database-url` KABUL ETMİYOR; `--database-url-env <DEĞİŞKEN ADI>` ya da
   `--database-url-file <0600 dosya>`. `/sektor-paket` adaptörü güncellendi.
7. **S-8 kalan riski:** ayrı bir iş DEĞİL — anahtar rotasyonu zaten
   `repo-public-exposed-live-credentials` kaleminde, tarihli eviyle (Plan 2 bitişi) duruyor.

---

## Medium / Low

Politika (`ch-only-v1`): doğrulanmış medium/low `accepted_risk` — fix zorunlu değil, zinciri bloke etmez.

### S-5 — (low, `accepted_risk`) `_require_run_id` `match` kullanıyor, `fullmatch` değil
- `apps/social/backend/app/services/sector_pipeline/runs.py:437-443` · `[single-source: claude]`
- Ölçüldü: `'kosu-abc\n'` → `match` True, `fullmatch` False. Dizin kaçışı ÜRETMEZ; etki satır
  sonu taşıyan bir dizin adı ve DB anahtarıyla sınırlı. Beyanı tutmayan şekil kapısı.
- Düzeltme (gönüllü): `match` → `fullmatch` + `"kosu-abc\n"` test vakası.

---

## Unverified medium (evidence gap) — ilerleme kapısı

### S-6 — Takvim iş akışı SQL'i üçüncü-taraf besleme verisinden string birleştirmeyle kuruyor
- **severity: medium** · `[single-source: claude]` · `evidence_confidence: partial`
- `shared/n8n-workflows/turkey-calendar-update.json` — `SQL Oluştur` (jsCode) + `Tatilleri Kaydet` (`query = ={{ $json.sql }}`)

**Ölçülen (mekanizma):** `escape = (s) => String(s || '').replace(/'/g, "''")` ile `date.nager.at`
ve `api.aladhan.com`'dan gelen değerler INSERT gövdesine gömülüyor; postgres düğümü
`executeQuery` ile ham string koşuyor. Parametre bağlama **yok**.

**ÖLÇÜLMEDİ (boşluk):** çalışan bir bypass gösterilmedi; hedef veritabanının
`standard_conforming_strings` değeri ölçülmedi. Yani "kanıtlanmış SQLi" değil, "kanıtı olmayan
savunma". Politika gereği bu bulgu **otonom `accepted_risk` ALAMAZ** — ya ek kanıtla
doğrulanır/çürütülür ya da kullanıcı açık `evidence_gap_acceptance` verir; bulgu `open` kalır.

**Task 18 bağlantısı:** bu dosya Task 18 Step 6'da n8n'e import + aktive edilecek üç workflow'dan
biridir. Yani karar dağıtımdan önce verilmeli.

---

## Excluded secret-bearing paths (metadata-only)

Yok — preflight kapsamda sır taşıyan path bulmadı.

## Disposition Ledger

| id | source | raw sev | final sev | disposition | gerekçe |
|---|---|---|---|---|---|
| S-1 | codex | critical | critical | open / needs_human (fix-required) | Artefakt düzeyinde kontrolör ölçümüyle doğrulandı; canlı durum ölçülmedi |
| S-2 | claude + codex | high + high | high | open / fix-required | both-agree; mekanizma ölçüldü (argv · `env=` yok · izin listesi) |
| S-3 | claude + codex | high + medium | **high** | open / fix-required | premis doğrulaması sonrası temkinli taraf; zincir ayağı (hidepid yok + kısıtsız alt süreç) ölçüldü |
| S-4 | claude | high | **low** | **rejected** (bloklayan ayak) + documented_residual | rotasyon 2026-09-06'da YAPILDI, eski token ölü ölçüldü (401) — premis çürüdü; kalan: ölü token geçmişte |
| S-5 | claude | low | low | accepted_risk (`policy_accepted`) | doğrulandı; şekil kapısı, kaçış üretmiyor |
| S-6 | claude | medium | medium | **open** (evidence gap) | mekanizma doğrulandı, istismar doğrulanmadı → D1(d) kapısı |
| S-7 | sınıf kapısı (düzeltme turu) | critical | critical | **open** / needs_human | tarayıcı çağırıyor → başlık kapatamaz; imzalı jeton tasarım kararı |
| S-8 | kontrolör ölçümü | high | high | **fixed** (2026-09-12) | temsil maskelendi; kalan risk oturum kaydı, rotasyon kararı kullanıcıda |
| — | codex | medium (DSN argv) | — | merged-into S-3 | aynı kök neden |

Ham bulgu sayısı: Claude 5 · Codex 3 → sentez sonrası 6 ayrı kalem (biri birleştirildi).
Hakemler-arası çelişki: yok (yalnız S-3'te severity ayrışması — yukarıda uzlaştırıldı).
Push-back ile kapatılan: 0.

## Deploy/Finish Gate

- **security-risk: BLOCKED** — S-1/S-2/S-3/S-8 kod tarafı kapandı, S-4'ün bloklayan ayağı
  premis-çürütmesiyle düştü; ama **S-7 (critical) AÇIK** ve S-1'in canlı ayağı (n8n credential +
  ortam değişkeni) henüz kurulmadı. Override yok.
- **dual-review: complete** — iki hakem de koştu.
- **coverage: full-diff** (coverage_gap yok).
- **evidence-gap kararı bekliyor:** S-6.

**Task 18 (ön-pilot dağıtım) Step 0(d) SAĞLANMADI:** kapı "critical/high açık bulgu varsa dağıtım
BAŞLAMAZ" diyor. Step 0'ın diğer üç ayağı bu oturumda ölçüldü ve geçti:
tam takım `4379 passed` · Katman-1 sweep + pin testleri `156 passed` (tek bayt fark yok).

## Prosedürel kapanış

Tanımlı pas bütçesi tamamlandı (1 attempt; `total_invocations=1`, `consecutive_degraded=0`);
adlandırılmış güvenlik kategorileri (6 grup) iki hakem tarafından da tarandı.
Kapsanan alanlar: boru hattı modülleri, CLI, router diff'i, üç migration + rollback, dört n8n
workflow'u, frontend diff'i. Kapsanmayan/denenmeyen: `docs/**` ve `tests/**` (görev tanımı gereği),
`brief_doctor.py`'nin 3855 satırlık ayrıştırıcı mantığının satır satır semantik denetimi (desen
taraması yapıldı), canlı n8n durumu, canlı enjeksiyon koşumu, `standard_conforming_strings` ölçümü.
Residual'lar: S-5 (`accepted_risk`), S-6 (evidence gap, karar bekliyor).
**Exhaustiveness iddiası yok.**

## Ham kanıt — işaretçiler (bu makinede, bu kökten)

- Codex ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-12-secreview-feat-sektor-bilgi-paketi-plan2-1.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-12-secreview-feat-sektor-bilgi-paketi-plan2-1.claude.md` (secret değerleri maskeli)
