# Review (dual): sektör bilgi paketi Plan 1 runtime çekirdeği — 2026-08-26

Review aralığı: `REVIEW_BASE_SHA..HEAD_SHA`
- BASE_REF: `main` | BASE_SHA: `5a9d5d4` | HEAD_SHA (attempt-1): `3e943c9` | REVIEW_BASE_SHA (merge-base): `5a9d5d4`
- Kapsam: 103 commit, 80 dosya, +22.615 / −325. Üretim kodu ~7.074 satır (30 dosya), testler ~15.000 satır.
- Closure (attempt-2) aralığı: `3e943c9..bf9e080` (4 commit, 8 dosya, +264/−93)
- Düzeltmeler sonrası HEAD: `6e6830a`

Reviewers: fresh Claude subagent (`general-purpose`, code-reviewer personası) + Codex `adversarial-review`
dual-review: **true** (claude_status: ran; codex_status: ran) — attempt-1 ve attempt-2'nin ikisinde de
review_confidence: full
Review workspace: pinned worktree @ HEAD_SHA (clean); closure için ikinci pinned worktree @ `bf9e080`
Main tree at review: clean (0 uncommitted dosya)

Requirement context (snapshot):
- `docs/specs/2026-08-21-sektor-bilgi-paketi.md` — committed, sha256 `c7061faf…`
- `docs/plans/2026-08-23-sektor-bilgi-paketi.md` — committed, sha256 `13c3cccd…`

**Sözleşme sapması (beyan).** Komut, gereksinim metninin TAM METNİNİ iki hakemin prompt'una da
gömmeyi ister. Bu boyutta **fiziksel olarak imkânsız**: tek komut argümanı 131.072 baytla sınırlı
(ölçüldü — 131.000 geçiyor, 131.072 `Argument list too long`), gömülü prompt 180.619 bayt. Yerine
her iki hakem de aynı pinli worktree'deki AYNI donmuş dosyayı okudu; hash'ler ana depo ile worktree
arasında birebir doğrulandı. Bu, gömmeye göre daha güçlüdür — aradan orkestratörün kopyalaması
çıkar, kopyalama kayması riski sıfırlanır.

**Bağımsızlık notu.** Codex, attempt-1'de kendi inisiyatifiyle `docs/active/CURRENT.md` ve
`TASK.md`'yi okudu. Orkestratör vermedi (komut vermeyi yasaklar), ama Codex depoda görüp açtı.
Bulguları o bilinen-sorun listesinden etkilenmiş olabilir; dürüst etiket budur.

---

## Critical

Yok.

## High — dördü de KAPANDI

### H1 — On-prem/yerel dağıtım 032'de kesin duruyordu `[both-agree]`
Doğrulama blokları `pg_constraint.conenforced`'ı doğrudan okuyordu (14 kod sitesi). O kolon
PostgreSQL 18'de geldi; yerel paket `pgvector/pgvector:pg16` imajına pinli. Referans **ayrıştırma
anında** düşüyordu, yani taze kurulum 032'ye varır varmaz duruyordu.

**Ölçüm (iki yönlü, gerçek konteyner):** düzeltme öncesi dosyalar taze PG16 (16.15) üzerinde
`column k.conenforced does not exist` ile düşüyor; düzeltilmiş hâlde 001→034'ün tamamı uygulanıyor
ve beş yeni tablo oluşuyor. PG18 (18.3) zincirinde de tamamı geçiyor.

**Zayıflatma YOK.** Bayrak satırdan jsonb olarak anahtar adıyla okunuyor
(`COALESCE(to_jsonb(k)->>'conenforced','true')`). PG18'de gerçekten `NOT ENFORCED` bir FK ile
ölçüldü: jsonb yolu da doğrudan okuma da `false` diyor. `'true'` geri düşüşü yalnız anahtar
yokken (PG<18) devreye girer ve orada doğrudur — `NOT ENFORCED` kavramı PG18'de geldi.
Claude hakemi ayrıca PG16'da `NOT VALID` bir FK ile **pozitif kontrol** koştu: blok `rc=3` ile
doğru etiketle reddetti, yani PG16'da boş geçmiyor.

**Önceki durum:** `TASK.md` bunu 2026-08-24 tarihli açık bir Eray risk kabulü olarak taşıyordu
(yeniden açılma koşulu: "on-prem paketi gerçekten kurulacaksa"). İki hakem de bunu bilmeden
bağımsız buldu; kullanıcı kapatmayı seçti. Commit `a2d19a7`.

### H2 — Yutulan olay hatası çağıranın transaction'ını öldürüyordu `[single-source: claude — claude-confirmed]`
`log_package_event` altyapı hatasını yutup `None` döner ve sözleşmesi "çağıranın akışı ASLA
düşmez"dir. Transaction içinde bu **yanlıştı**: PostgreSQL başarısız ifadede transaction'ı abort
eder ve sonraki her komutu reddeder; asyncpg kendiliğinden savepoint açmaz. `resolve_persist_stamp`
post yazımıyla aynı transaction'dadır (K-07), dolayısıyla düşen bir olay yazımı post INSERT'ünü de
düşürüyor ve kullanıcı 500 alıyordu. Koruma, tam da yazıldığı senaryoda (033 uygulanmamış) tersine
çalışıyordu.

Hakem bunu "çıkarımdır, ölçemedim" diye işaretledi. **Orkestratör canlı veritabanında ölçtü:**
yutmadan sonraki INSERT `InFailedSQLTransactionError` veriyor; iç transaction'lı varyant kurtarıyor.

**Mevcut test bu hatayı yakalayamazdı** — sahte bir bağlantı nesnesiyle, transaction olmadan
koşuyordu. Yerine gerçek bağlantı + gerçek transaction + erişilemez kılınmış olay tablosuyla koşan
bir regresyon yazıldı. Mutasyon kontrolü: savepoint kaldırılınca test `InFailedSQLTransactionError`
ile düşüyor. Commit `88c1260`; kendi yan etkisinin düzeltmesi `1a6486a` (aşağıda N1).

### H3 — Migration koşucusu ikinci kez koşamıyordu, README "tekrar çalıştır" diyordu `[single-source: claude — claude-confirmed]`
Bu dal koşucuyu fail-fast yaptı (`set -euo pipefail` + `ON_ERROR_STOP=1`) ama uygulanmış-migration
defteri yok; her koşum 001'den başlıyor. `003` kısıtı koşulsuz ekliyor. **Ölçüldü:** ikinci koşumda
`42P07 ... already exists`. Fail-fast öncesinde aynı hatalar basılıyor ama psql 0 dönüyordu — yani
koşucu yeniden-koşulabilir GÖRÜNÜYORDU; görünüş yanlıştı, davranış değil.

README'nin 114. satırı (güncelleme adımı) ve 144. satırı (sorun giderme) operatöre tam bu komutu
söylüyordu. Koşucuya dolu-veritabanı kapısı eklendi, README gerçeğe uyduruldu.
Commit `035be40`; fail-open düzeltmesi `e4d59d2` (aşağıda N-H3).

### H4 — Yeni alt-sektör ve kanal onayları kaybolabiliyordu `[single-source: codex — claude-confirmed]`
1,5 saniyelik gecikmeli otomatik kaydetme **devralınmıştır** (main'de de var), ama bu dal
`sub_sector_id`'yi ve kanal anahtarlarını o yola ekledi. **Ölçüldü:** tüm önyüzde
sayfadan-çıkışta-gönder koruması yok (`beforeunload`/`visibilitychange` sıfır sonuç) ve arka uçtaki
koşullu yazım kapısı uykuda (hiçbir çağıran sürüm göndermiyor). Kullanıcı alt sektörü seçip 1,5
saniye dolmadan çıkarsa istek hiç gitmiyordu. Marka ayarları **müşteri yüzeyidir**.

Ayrık onaylar artık doğrudan gönderiliyor; bekleyen gecikmeli yazım iptal ediliyor ama kaybolmuyor
(tam anlık görüntü gönderilir — erken boşaltma). Gönderim gövdesi tek yere alındı.
Commit `bf9e080`; çapraz-marka gerilemesinin düzeltmesi `6e6830a` (aşağıda N-H4).

---

## Closure turunda çıkan YENİ bulgular — hepsi düzeltmelerin KENDİ ürünü

Bunlar devralınan borç DEĞİL, bu turun ürünüdür; `accepted_risk` sınıfına park edilmediler.

### N1 — `high` — Yönetici bildiriminin hızlı gönderim yolu %100 öldü `[single-source: claude — claude-confirmed]`
H2 için eklenen savepoint koşulsuz açılıyordu. Transaction **dışında** `db.transaction()` savepoint
değil GERÇEK transaction açar; o sırada `is_in_transaction()` `True` döner ve
`notifications._maybe_trigger_fast_dispatch` tam o kapıyı taşır. **Ölçüldü (18.3):** dışarıda
`db.transaction()` içinde `is_in_transaction()` `True`. `ADMIN_NOTIFIED_EVENTS` üreten tüm üretim
çağrı yerleri transaction dışında, yani kayıp bu yüzeyin tamamındaydı.

Teslim garantisi bozulmadı (onu kurtarma yolu üstlenir); kaybolan, tasarlanmış gecikme kısaltmasıdır.
`high` olmasının sebebi büyüklük değil, **sessiz, tam kapsamlı ve hiçbir testin görmediği kendi
açtığımız gerileme** olması. Düzeltme: savepoint yalnız çağıranın transaction'ı varken açılır.
Commit `1a6486a`.

### N2 — `medium` — Komşu test boşa düşmüştü `[single-source: claude — claude-confirmed]`
`test_event_write_failure_does_not_block_caller`'ın sahte bağlantısında `transaction()` yok;
sarmalayıcı `AttributeError` atıyor ve o yutuluyordu — testin enjekte ettiği `RuntimeError` hiç
çalışmıyordu. Test yeşil kalıyor ama iddiası yanlıştı. N1 düzeltmesi bunu **kendiliğinden** kapattı
(sahte nesnede `is_in_transaction` yok → savepoint açılmaz). Ölçüldü: log artık `tablo yok` taşıyor.

### N3 — `medium` (`evidence_gap`) — Üç savepoint'in ikisi hiçbir testle bağlı değildi `[single-source: claude — claude-confirmed]`
Hakem mutasyonla ölçtü: iki savepoint tek tek devre dışı bırakıldığında paket yeşil kalıyordu.
İki yeni kapı eklendi — koşullu-açılma invariantı (kaydeden sahte bağlantıyla; gerçek `db` fixture'ı
zaten transaction içinde koştuğu için "dışarıda" dalı onunla gözlemlenemez) ve `_notify_admin`
savepoint'i (gerçek yoldan, outbox tablosu erişilemez kılınarak). **Mutasyon kontrolü:** sarmalayıcı
koşulsuz yapılırsa birinci test, `_notify_admin` savepoint'i kaldırılırsa ikinci test
`InFailedSQLTransactionError` ile düşüyor.

### N-H3 — `high` — Kurulum kapısının sondası fail-OPEN'dı `[both-agree]`
Kapı `$( ... || echo 0 )` biçimindeydi: psql'in her başarısızlığı "0 tablo = boş veritabanı, devam
et"e dönüşüyordu. **Ölçüldü:** sondayı düşüren bir shim ile kapı sessizce geçiyor ve 34 migration
gönderiliyor; sayısal olmayan çıktı da aynı yoldan geçiyor. Kapı, korumak için var olduğu duruma
karşı fail-open'dı. Sonda hatası ve sayısal olmayan çıktı artık ölümcül. **Beş dal ölçüldü:**
dolu → rc=1, boş → rc=0 (34 dosya), kaçış → rc=0, sonda hatası → rc=1, sonda çöpü → rc=1.
Commit `e4d59d2`.

### N-H4 — `high` — Ayrık onay, BAŞKA markanın bekleyen düzenlemesini düşürüyordu `[single-source: codex — claude-confirmed]`
`commitBrandNow`/`commitKitNow` hangi zamanlayıcı bekliyorsa koşulsuz iptal ediyordu. **Ölçüldü:**
sayfa marka değişiminde remount OLMUYOR (`currentBrand?.id`'ye bağlı effect yerinde tazeliyor,
`switchBrand` yalnız state değiştiriyor), yani zamanlayıcı referansı markalar arası yaşıyor.
B'de bir onay, A'nın bekleyen düzenlemesini düşürebiliyordu — düzeltmenin açtığı kayıp.

Bekleyen yazımlar artık marka kimliği taşıyor; yalnız aynı markanınki birleştiriliyor. Başka
markanınki dokunulmadan bırakılıyor (kendi anlık görüntüsünü taşır, zamanında gider). Bu, aynı
tehlikeyi devralınmış gecikme yolunda da kapatır.

**İkinci dereceden bir kusur, düzeltmeyi yeniden okurken bulundu:** zamanlayıcı geri çağrıları
ateşlenirken referansı sıfırlıyordu; A'nın zamanlayıcısı B'ninkinden sonra ateşlenirse B'nin kaydını
siliyor, sonraki bir B onayı bekleyen yazımı iptal edemiyor ve eski anlık görüntü yenisini ezebiliyordu.
Geri çağrılar artık referansa dokunmuyor. Commit `6e6830a`.

### N4 — `low` — `commit*Now` state'i doğrudan okuyor
Kardeşleri fonksiyonel updater kullanıyor. Hakem **ulaşılabilirliğini ölçemediğini** açıkça
etiketledi (React 18 ayrık olayları senkron flush ediyor; önyüzde test altyapısı yok). Teorik.
`accepted_risk`.

### N5 — `low` — Aynı kayıp sınıfı, dalın DOKUNMADIĞI ayrık kontrollerde duruyor
`logo_overlay`, logo konumu, tonalite, sektör, tanıtım videosu konumu — hepsi dal öncesi.
Devralınmış borç; evi `brand-settings-save-integrity`. `accepted_risk`.

---

## Medium (attempt-1) — `accepted_risk`, fix edilmedi

| # | Bulgu | Kaynak | Not |
|---|---|---|---|
| M1 | İçerik kütüphanesi yoklaması `failed` satırlarda sınırsız — sayfa açık kaldıkça 3 sn'de bir. Codex ekliyor: başarısız carousel satırları geç-webhook yolundan zaten kurtulamaz, yani yoklama saf israf | `[both-agree]` | Bu partinin ürünü (clearInterval kaldırıldı + `failed` eklendi). Kökü `stale-sweeper-vs-late-webhook-terminality` |
| M2 | `schema_version` kolonu hiçbir yerde okunmuyor; bir şema artışı tüm eski paketleri sessizce devre dışı bırakır | `[single-source: claude]` | Spec §3.4'ün kod karşılığı yok |
| M3 | `resolve_sector` artık istisna fırlatıyor, hiçbir çağıran yakalamıyor → taksonomi bozukken marka oluşturma 500; `brands.py:122`'de ölü geri-düşüş dalı | `[single-source: claude]` | **Bu partinin ürünü** (dönüş sözleşmesi `tuple \| None` → `tuple` değişti, çağıranlar tam güncellenmedi). Ölçüldü: `main.py`'de handler yok |
| M4 | K-04 kullanım talimatı üç farklı metne ayrışmış; `_enrich_with_scene`'de hiç yok | `[single-source: claude]` | Spec §4.5 "her enjeksiyon bloğunun başına" diyor |

## Low (attempt-1) — `accepted_risk`

Madde numarası 6→8 atlıyor (`caption_generator.py`) · `generation_stamps` temizlik politikası yok ·
`insert_draft` tek bozuk tatil adında tamamen düşüyor · jsonb codec ortak fixture'da değil, yedi
modülde tekrar · `local-deployment/migrations/` altında 11 ölü kopya · `_lock_sector` gereğinden
geniş kilit alıyor (`FOR UPDATE` yerine `FOR NO KEY UPDATE` yeterdi).

---

## Disposition Ledger

| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| H1 | claude+codex | high | high | **fixed** (`a2d19a7`) | İki yönlü PG16/PG18 ölçümü + pozitif kontrol |
| H2 | claude | high | high | **fixed** (`88c1260`, `1a6486a`) | Canlı DB ölçümü + mutasyon kontrolü |
| H3 | claude | high | high | **fixed** (`035be40`, `e4d59d2`) | Beş dal ölçüldü |
| H4 | codex | high | high | **fixed** (`bf9e080`, `6e6830a`) | Yapısal; önyüz testi YOK (dürüst sınır) |
| N1 | claude | high | high | **fixed** (`1a6486a`) | Kendi yan etkimiz; ölçüldü |
| N-H3 | claude+codex | high | high | **fixed** (`e4d59d2`) | Kendi yan etkimiz; ölçüldü |
| N-H4 | codex | high | high | **fixed** (`6e6830a`) | Kendi yan etkimiz; premis ölçüldü |
| N2 | claude | medium | medium | **fixed** (`1a6486a`) | Kendi yan etkimiz — park EDİLMEDİ |
| N3 | claude | medium | medium | **fixed** (`1a6486a`) | İki yeni kapı + mutasyon kontrolü |
| M1 | claude+codex | medium | medium | accepted_risk | Politika: medium fix edilmez |
| M2 | claude | medium | medium | accepted_risk | — |
| M3 | claude | medium | medium | accepted_risk | Bu partinin ürünü — görünür etiketlendi |
| M4 | claude | medium | medium | accepted_risk | — |
| N4 | claude | low | low | accepted_risk | Ulaşılabilirlik ÖLÇÜLMEDİ (etiketli) |
| N5 | claude | low | low | accepted_risk | Devralınmış; evi var |
| L1-L6 | claude | low | low | accepted_risk | — |
| EG1 | claude | evidence_gap | — | **closed** | "Hiçbir test koşamadım" → orkestratör koştu: 580 + 121 |
| EG2 | claude | evidence_gap | — | **closed** | "PG16 ölçemedim" → gerçek PG16 konteynerinde ölçüldü |
| EG3 | claude | evidence_gap | — | **closed** | "Transaction zehirlenmesi çıkarımdır" → canlı DB'de ölçüldü |

Hakemler-arası çelişki: **yok**. Örtüşmeyen bulgular kapsama boşluklarından kaynaklandı, karşıt
yargıdan değil — Codex'in H4'ü Claude'un okumadığı bölümdeydi; Claude'un N1'i Codex'in bakmadığı
çağrı zinciriydi.

Push-back (kapatılan): **0** — kullanıcı hiçbir bulguya itiraz etmedi.

---

## Prosedürel kapanış

Tanımlı pas bütçesi tamamlandı (2 attempt: tam dual review + odaklı closure; `total_invocations=2`,
`consecutive_degraded=0`). Adlandırılmış closure kontrolleri çalıştı.

**Kapsanan alanlar:** üretim kodu (30 dosya) · migration'lar 011/032/033/034 + rollback · dağıtım
koşucusu ve belgeleri · outbox/eventing · yaşam döngüsü · üç önyüz sayfası · dört düzeltmenin etki
zarfı (dokunulmamış çağıranlar, config, ortak invariantlar dahil).

**Denetlenmeyen / kapsanmayan alanlar:**
- **Önyüzün çalışan davranışı.** Depoda önyüz otomatik test altyapısı YOK. H4 ve N-H4 kararları
  statik okuma + `tsc` + lint kapısına dayanıyor, koşan bir teste değil. Bu, dalın kendi belgelediği
  boşluktur ve `brand-settings-save-integrity`'nin ön koşuludur.
- **Gerçek `docker compose` ile uçtan uca yerel dağıtım** (`setup.sh`). Kapı iddiaları runner
  sözleşme testleri (21/21) + boş PG16/PG18 zincir koşumları + shim'li dal ölçümleriyle dayanıyor.
- **Spec'in 7-17. bölümleri** attempt-1'de Claude hakemi tarafından okunmadı (Plan 1 kapsamının
  çoğu 3-6'da olduğu için öncelik oraya verildi). Kapsam boşluğudur.
- **`rollback/032_down.sql`** (265 satır) hiçbir turda satır satır okunmadı.
- **`onboarding/page.tsx`** (107 satır ekleme) attempt-1'de okunmadı.
- **034'ün DDL'i** servis koduyla karşılaştırılmadı (attempt-1'de yalnız grep'lendi).
- **n8n workflow'unun Code düğümlerinin JavaScript gövdeleri** okunmadı.
- Testlerin ~15.000 satırının çoğu iki hakemde de satır satır okunmadı.
- Canlıya hiçbir migration uygulanmadı.

**Residual'lar:** M1-M4 + L1-L6 + N4 + N5 (`accepted_risk`); yukarıdaki denetlenmeyen alanlar.

**Taze koşum (HEAD `6e6830a`):**
- `pytest tests/ -q` → **580 passed** (105s)
- `pytest tests/prompt_regression/ -q` → **121 passed** (bayt değişmezlik kapısı)
- `npx tsc --noEmit` → **rc=0**
- `ec_footer_parse` yedi düzeltme commit'inde → **rc=0**

**Exhaustiveness iddiası YOK.**

`Unresolved critical/high:` **yok** — yedi high bulgunun yedisi de düzeltildi ve her biri kendi
ölçümüyle kapatıldı.

---

## Ham kanıt — işaretçiler (bu makinede, bu kökten)

- Codex attempt-1: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-review-feat-sektor-bilgi-paketi-1.md`
- Codex closure (attempt-2): `/root/.claude/logs/otomaix--ffc87809/2026-08-26-review-feat-sektor-bilgi-paketi-2.md`
