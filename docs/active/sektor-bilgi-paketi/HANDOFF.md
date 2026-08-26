# Handoff

## Context

- Task: sektor-bilgi-paketi — Plan 1 yürütmesi TAMAMLANDI, durum `waiting-review`
- Last updated: 2026-08-26 (on dokuzuncu oturum — review zincirinin 3. adımı: güvenlik review'ı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` @ `d8a6d5d` — **PUSH EDİLDİ**, upstream `origin/feat/sektor-bilgi-paketi`
- **PR: https://github.com/Eray-Deniz/otomaix/pull/2** (açık, `feat/sektor-bilgi-paketi` → `main`)
  PR gövdesi hakemi doğrudan incelenmemiş iki koda yönlendiriyor (`39f283d`, `3561231`).
- Kod review raporu: `docs/reviews/2026-08-26-feat-sektor-bilgi-paketi.md`
- Güvenlik review raporu: `docs/security-reviews/2026-08-26-feat-sektor-bilgi-paketi.md`
  (**başındaki düzeltme banner'ını ÖNCE oku** — bir bulgu geçersiz çıktı)
- Kapanış raporu (Plan 1): `docs/active/sektor-bilgi-paketi/PLAN1-KAPANIS.md`
- Ham hakem log'ları (bu makinede, bu kökten) — `/root/.claude/logs/otomaix--ffc87809/`:
  - güvenlik: `2026-08-26-secreview-feat-sektor-bilgi-paketi-{1,2,3}.md` (Codex)
    ve `-{1,2,3}.claude.md` (Claude alt-hakem)
  - kod review: `2026-08-26-review-feat-sektor-bilgi-paketi-{1,2}.md`
  - yürütme: `2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Resume From

### ✅ Migration'lar canlıda (2026-08-26)

032 · 033 · 034 uygulandı, üçü de `rc=0`, dosya başına tek transaction.
Yedek (uygulama ÖNCESİ, okunabilirliği doğrulandı):
`/root/otomaix-db-backups/otomaix-pre-032-20260826-185643.dump`

**Uygulama sonrası ölçüm (iddia değil, koşum):**
- Yeni nesneler: `sector_packages` · `package_events` · `admin_events` ·
  `sector_research_artifacts` · `generation_stamps`
- Mevcut veri: 2 marka · 81 post · 12 sektör — **değişmedi**; `brands.sub_sector_id` 2/2 NULL,
  `posts.package_id` 81/81 NULL (geri doldurma YOK)
- Beş tetikleyicinin hepsi kurulu; `uq_sector_packages_single_active` kısmi unique indeksi yerinde
- **Negatif kontroller (hepsi ROLLBACK'li, canlı veri değişmedi):** markaya kök sektör ataması
  REDDEDİLDİ · mevcut sektörün ebeveyn değişimi REDDEDİLDİ · ham artefaktta UPDATE REDDEDİLDİ ·
  DELETE REDDEDİLDİ
- **Pozitif kontrol:** canlıda koşan eski backend'in (`3e1617e`) yazımları hâlâ geçiyor —
  marka güncelleme · paketsiz post ekleme
- Artefakt tablosu kontrollerden sonra 0 satır (sızıntı yok)

**Canlıda hâlâ alt sektör YOK** (12 sektörün hepsi kök) — şema hazır, bağlanacak veri Plan 2'nin işi.

### ⚠️ Canlıya elle koşulacak adımlar (izin katmanı agent'ı reddetti — Eray koşar)

Sıra bağlayıcıdır. 1 ve 2 bugün koşulabilir; 3 ve 4 dal deploy edilmeden ANLAMSIZDIR
(`/internal/admin-events/dispatch-pending` ucu canlıda YOK — canlıda `3e1617e` koşuyor, ölçüldü).

**1. ~~Migration'lar~~ — ✅ UYGULANDI (2026-08-26 18:56).** Komut kayıt için duruyor:
```
for f in 032_sector_packages 033_package_events 034_admin_events; do
  docker exec -i wlg6ned4e72aty3pqhnxs0hg psql -U otomaix -d otomaix \
    -v ON_ERROR_STOP=1 --single-transaction -q \
    < /root/otomaix/shared/db/migrations/$f.sql && echo "$f OK"
done
```

**2. n8n credential'ı** (sır üretildi: `/root/otomaix-admin-event-secret.txt`, chmod 600):
```
S=$(cut -d= -f2 /root/otomaix-admin-event-secret.txt)
printf '[{"id":"otomaixAdminEvtKey","name":"Otomaix Admin Event Key","type":"httpHeaderAuth","data":{"name":"X-Admin-Event-Key","value":"%s"}}]' "$S" > /tmp/cred.json
docker cp /tmp/cred.json n8n-py684zd3w0ktf75a1vg0d5hk:/tmp/cred.json && rm /tmp/cred.json
docker exec n8n-py684zd3w0ktf75a1vg0d5hk n8n import:credentials --input=/tmp/cred.json
docker exec n8n-py684zd3w0ktf75a1vg0d5hk rm -f /tmp/cred.json
```

**3. Backend env** (Coolify → backend servisi): `N8N_ADMIN_EVENT_SECRET` = aynı değer.
Boşken sistem hiç gönderim yapmaz (bilinçli fail-closed), yani bu adım atlanırsa kanal sessizdir.

**4. Workflow importu** — dal deploy EDİLDİKTEN sonra, pasif import + elle tek teslim smoke'u:
```
docker cp /root/otomaix/shared/n8n-workflows/sector-package-admin-events.json \
  n8n-py684zd3w0ktf75a1vg0d5hk:/tmp/wf.json
docker exec n8n-py684zd3w0ktf75a1vg0d5hk n8n import:workflow --input=/tmp/wf.json
docker exec n8n-py684zd3w0ktf75a1vg0d5hk rm -f /tmp/wf.json
```

**Canlı ölçümü (2026-08-26):** 2 marka · 81 post · 12 sektör — **hepsi kök, alt sektör YOK**.
Yani migration atılsa bile paket sistemi bugün bağlanacak bir şey bulamaz; taksonomi Plan 2'nin işi.


**Zincirin 3. adımı (`/security-review-claude-codex`) BİTTİ. Güvenlik kapısı TEMİZ:
çözülmemiş kritik/yüksek bulgu YOK, dual-review üç turda da tam, kapsam boşluğu yok.**

Sıradaki iş:

1. ~~`sector-packages-mandatory-split`~~ — **BU OTURUMDA YAPILDI** (`39f283d`): yaşam döngüsü
   `app/services/sector_package_lifecycle.py`'ye taşındı (1804 → 1310 + 524 satır); taşınan gövde
   bayt-aynı, kapsülleme testi mutasyonla pozitif kontrol edildi.
2. **`/finish-branch-claude-codex`** — dört seçenek (merge / PR / tut / sil).

**Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Verification

> **Bu bölüm iki oturumu birlikte taşır.** Aşağıdaki ilk blok on dokuzuncu oturuma (güvenlik
> zinciri) aittir ve kendi commit'ine pinlidir; yirminci oturumun ölçümleri ayrı blokta.

### Yirminci oturum (kapanış) — son commit `0733cb0`

- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **659 passed** (106s)
  (fark: n8n workflow'unun iki regresyonu)
- Mutasyon pozitif kontrolleri: kapsülleme testi (ham geçiş public takma ad) · `$env` yasağı ·
  yer tutucu credential yasağı — üçü de mutasyonda KIRMIZI, geri yüklemede YEŞİL
- Modül bölmesi bayt karşılaştırmalı: taşınan gövde ile `git show HEAD:<eski yol>` arasındaki tek
  fark kasıtlı başlık satırı; kalan dosyada tek fark kasıtlı yönlendirme notu
- Canlı veritabanı prova koşumu: 032/033/034 canlı verinin kopyasında rc=0 + idempotent;
  eski backend'in yazımları etkilenmedi; kapılar iki yönde doğrulandı
- `ec_footer_parse` dört yeni commit'te → rc=0

### On dokuzuncu oturum (güvenlik zinciri) — o günün son commit'i `00bd771`

- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **657 passed** (103s)
  (oturum başı taban 580; fark o oturumda yazılan güvenlik regresyonları)
- `ec_footer_parse <sha> /root/otomaix` rapor commit'inde → **rc=0**
- Canlı internet sondası (SSRF kapısı, düzeltme öncesi ve sonrası): `example.com` · `otomaix.com` ·
  `github.com` (yönlendirme zinciri) çekiliyor; bulut kimlik adresi · geri döngü · `localhost` ·
  özel ağ · IPv6 geri döngü · IPv4-mapped · taşıyıcı-NAT · izinsiz port · `file:` şeması ·
  kimlik bilgili URL reddediliyor
- **Üretilmiş matris** (elle seçilmiş örnek DEĞİL): kodlama × boyut × parça biçimi = 75 kombinasyon;
  "aktarılan ham bayt, sınırı en fazla bir parça aşar" sözleşmesi hepsinde tutuyor; sıkıştırılmış
  varyantların hepsi SIFIR bayt okunarak reddediliyor; yavaş damlatma tam tavanda kesiliyor
- **Gerçek parça boyutu ölçümü:** canlı `github.com` çekiminde en büyük tek parça 16.384 bayt —
  parça boyutunu sunucu değil aktarım tamponu belirliyor. Kodun docstring'indeki kapsam-sınırı
  cümlesinin dayanağı budur, varsayım değil.

**Mutasyon kontrolleri — her düzeltme kendi ölçümüyle kapatıldı, hiçbiri okumaya bırakılmadı:**
marka filtresi · fail-closed sayım · ürün sahipliği kapısı · uç 404 kapısı · adres bayrak listesi ·
pozitif `is_global` koşulu · akıtarak okuma · yönlendirme gövdesi · IP sabitleme · port allowlist'i.
Her mutasyondan sonra dosya geri yüklendi ve taze koşum yapıldı.

**DENENMEYEN / kapsanmayan (bu oturum):**
- Kısa videonun 2. aşamasındaki ürün kapısı **testle bağlanmadı**: kota kontrolünün arkasında
  duruyor, varsayılan planlı hesapla kapıya ulaşılamıyor (ÖLÇÜLDÜ: 404 yerine 402). Güvenlik
  sorunu değil (kota da reddediyor) ama koruma yok. Bağlamak plan fixture'ı ister.
- `/ai/analyze-website` hız sınırı taşımıyor (kardeş uçlarda var). Devralınan; düzeltilmedi.
- Sarmalanmış-adres açma katmanının ayırt edici testi YOK (bugünkü Python'da hiçbir sonucu
  değiştirmiyor; docstring bunu açıkça söylüyor).
- Önyüzde otomatik test altyapısı YOK (devralınan, değişmedi).
- Spec'in 7-17. bölümleri hiçbir hakem tarafından okunmadı (kod review'ının kapsama boşluğu).
- Canlıya hiçbir migration uygulanmadı; canlı veritabanına karşı sweep koşulmadı.
- Devralınan manuel doğrulamalar (arayüz · canlı n8n + Telegram · gerçek uçtan uca üretim ·
  gerçek model çağrıları) hâlâ Plan 2 sonrasındaki tek tura ertelenmiş.

## Closure Audit (2026-08-26, `/finish-branch-claude-codex`)

Codex closure-readiness audit'i `a11390d..0733cb0` aralığında koştu (pinli worktree).
**Sonuç: 2 closure-blocker + 2 closure-warning.** Log:
`/root/.claude/logs/otomaix--ffc87809/2026-08-26-finish-branch-sektor-bilgi-paketi-1.md`

- **[BLOCKER — PR review'ının kapatması gereken]** Zincir raporları kapanış aralığını
  KAPSAMIYOR. Kod review'ı `bf9e080`'de, güvenlik review'ı `b15ab6e`'de duruyor; ikisi de
  `0733cb0` değil. **Güvenlik kapanış turundan sonra 10 commit var ve İKİSİ KOD:**
  `39f283d` (yaşam döngüsü modül bölmesi) ve `3561231` (n8n workflow credential bağlaması).
  **Hiçbir hakem bu ikisini görmedi.** Taban tarafında da audit aralığı daha geniş: rapor tabanı
  `5a9d5d4`, audit tabanı `a11390d` — aradaki iki commit docs-only (plan onayı).
- **[BLOCKER — KAPANDI]** 130 commit yalnız yerel depodaydı, upstream yoktu. PR yolu bunu kapattı.
- **[WARNING]** Open Problems tümüyle kapalı DEĞİL: üç `accepted_risk` (bu partinin ürünü olan
  `resolve_sector` dönüş sözleşmesi · okunmayan `schema_version` · K-04 talimat ayrışması) ve
  bir tetikli açık kalem duruyor. **Özellikle `resolve_sector`:** politika orta bulguyu
  fix-required saymadığı için park edildi ama bu devralınan borç değil, bu dalın ürünü.
- **[WARNING — KAPANDI]** `docs/reviews/.ledger-index/` izlenmeye alındı (25 baytlık locator;
  oturumlar arası defter sürekliliğinin tek dayanağı, yok sayılırsa mekanizma amacını kaybeder).

**Codex bağımsızlığı — dürüst sınır:** ikinci blocker ve ikinci warning zaten bu dosyada
yazılıydı ve Codex onu okudu; bağımsız keşif SAYILMAZ. Birinci blocker'ın ölçümünü de ben
verdim, Codex teyit etti. **Gerçekten yeni olan tek bulgu birinci warning'dir** (Open Problems'ın
kapalı olmadığını ben kaçırmıştım).

## Risks

**Bu oturumun ürünü:**
- **[`accepted_risk`, düşük]** Kısa video 2. aşama ürün kapısı testsiz (yukarıda). Ev: dal kapanışı.
- **[`accepted_risk`, düşük, DEVRALINAN]** Site analizi ucunda hız sınırı yok.
- **[Ders — kayda değer]** Güvenlik review'ının üç turundan ikisi benim kendi düzeltmelerimin
  eksiklerini buldu; biri de benim ürettiğim geçersiz bir bulguyu temizlemeye gitti. İki kök neden
  de aşağıda Notes'ta kayıtlı.

**Devralınan, DEĞİŞMEYEN kalemler:**
- **[Manuel adım — komutlar yukarıda "Resume From"da]** Migration'ların canlıya uygulanması ·
  `N8N_ADMIN_EVENT_SECRET` (sır üretildi) · n8n credential + workflow importu ve TEK teslim smoke'u ·
  **Telegram env'i ARTIK GEREKMİYOR** — workflow mevcut credential'a bağlandı (`3561231`) ·
  `.env.example`'a satır eklenmesi (sır-dosyası kapısı agent'ı engelliyor) · Task 15'in UI doğrulaması.
- ~~`sector-packages-mandatory-split`~~ — KAPANDI (`39f283d`); `CURRENT.md`'den çıkarıldı.
- **[Eray tetikledi]** Süpürücü ↔ geç webhook terminallik çelişkisi. Ev: `CURRENT.md`.
- **[TETİKLİ]** `sector_packages.sector_id` değişmez değil. Ev: `CURRENT.md`.
- **[MÜŞTERİ yüzeyi]** Marka ayarları otomatik kaydetmesinin devralınmış kayıp yolları. Ev:
  `CURRENT.md` → `brand-settings-save-integrity`. Tetik: canlıya müşteri alınmadan ÖNCE.
- **[Kod tabanı geneli]** Senkron sağlayıcı çağrısı gerçekten kesilemiyor. Ev: `CURRENT.md`.
- **[Araç]** Kirli ağaçta Codex denetim ortamı kurulamıyor + `run_codex_scan` önkoşul kapısı yok.
  İkisi de `CURRENT.md`'de; bu oturumda TEMİZ ağaçta çalışıldığı için ikisi de doğmadı.
- **[Plan 2 teslim kalemi]** Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli ·
  `recovered` modu + geri-dönüş mesajı (F23 kapanışı).
- **[Residual]** 033 ve 034 için geri alma script'i YOK (plan istemedi).
- **[Etiketler — evi `/finish-branch-claude-codex`]** `backup/pre-footer-fix` ·
  `backup/pre-t3-kind-fix` · `backup/pre-t15b-footer-fix` · `backup/pre-t16-kind-fix`
  merge/PR kararından sonra silinir.
- **[Temizlik borcu — evi dal kapanışı]** `docs/reviews/.ledger-index/` bu oturumda oluştu ve
  **untracked**. Güvenlik review komutunun commit kapısı yalnız rapor dosyasını eklemeye izin
  verdiği için tracked edilmedi. Karar: izlensin mi (oturumlar arası ledger kalıcılığı için
  gerekli) yoksa yok sayılsın mı.
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı silinemez.
- `accepted_risk` (test altyapısı): eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür ·
  migration keşfi tekrarlı numarayı reddetmiyor · `db` fixture geri sarma testi yok ·
  `sector_research_artifacts` TRUNCATE regresyonu yok.

## Notes For Claude/Codex

- **Güvenlik zinciri özeti:** üç tur, her turda iki bağımsız hakem (fresh Claude subagent + Codex),
  hiçbirinde degradasyon yok. Düzeltilen iki gerçek sınıf: kullanıcı URL'ini çeken yüzeylerde SSRF
  (+ sıkıştırma bombası + yavaş damlatma), ve doküman/ürün erişiminde kiracı kapsamı. Üçüncü
  "bulgu" geçersiz çıktı ve geri alındı.
- **⚠️ BİR SONRAKİ REVIEW İÇİN — bu oturumun en pahalı dersi:** hakemlere verilen ORTAK BAĞLAM
  metnine doğrulanmamış rol/kural iddiası **YAZMA** ("X gizlidir", "Y fail-closed'dur"). Bu
  oturumda yazdım; iki hakem de iddiayı sorgulamak yerine kodu ona karşı doğruladı, olmayan bir
  yüksek bulgu üretildi, iki tur + bir geri alma harcandı. **İki hakemin uyuşması, iddia
  orkestratörden geldiyse bağımsız teyit DEĞİLDİR.** Komutun kendi kuralı ("ortak-mod bias
  guard'ı") bunu zaten yazıyor. Kalıcı not: memory `feedback_no_role_claims_in_reviewer_context`.
- **⚠️ İKİNCİ DERS:** aynı eksende iki tur üst üste bulgu geldiyse varyantı yamama, SINIFI kapat.
  Bayt sınırı üç turda üç kez düzeltildi (sonuç kesiliyordu → indirme kesilmiyordu → sıkıştırma
  açılıyordu). İlk seferde "kaynak sınırı" sorusunun tüm eksenleri (bayt · sıkıştırma · süre ·
  eşzamanlılık) sorulsaydı tek turda biterdi. Kapanış artık üretilmiş matrisle kanıtlanıyor.
- **Paket gizliliği — kalıcı olgu:** paket metni müşteriden gizli DEĞİLDİR (üretimi besler,
  müşteri çıkan post'u onaylar). Gizli olan ham araştırma katmanı (K-139) ve yönetici işlemleridir.
  K-16'nın "API'den okunabilirlik" hükmü, müşteriye paket listeleyen bir UÇ olup olmadığını karara
  bağlar. Memory: `project_sector_package_confidentiality`.
- **Codex bağımsızlığı — kirlenme (ölçüldü):** Codex her çağrıda orkestratör vermeden
  `docs/active/CURRENT.md` + `TASK.md` okuyor. Bilinen-sorun listesinde zaten duran bir maddeyi
  bulursa bu bağımsız keşif sayılmaz; raporda beyan edilmeli.
- **Codex bütçesi:** ilk çağrıda `timeout 480s` yetmiyor (`rc=124`). Asılma değil, uzun koşum —
  log'da alt komutlar kesilme anına kadar `exit 0` veriyor. 1200s ile ikinci çağrı tamamlanıyor.
  Prompt'a "keşfi genişletmeye devam edip kesilme, okumayı bitir ve çıktıyı ver" bütçe talimatı koy.
- **Hakem prompt'u boyut sınırı:** tek argüman 131.072 bayt. Büyük spec'i gömemezsin; iki hakem de
  aynı pinli worktree'deki aynı donmuş dosyayı okusun ve sapma raporda beyan edilsin.
- **Ledger (güvenlik review'ı, pinli):** `review_target_id`
  `security-review:feat-sektor-bilgi-paketi:5a9d5d4220d0a58db84dc23f274199491d91216b` ·
  `ledger_locator` `task:sektor-bilgi-paketi` · `pinned_contract_hash`
  `0f9a7629fc2fa17dd8fbd212492902ce7f1b495b2ac681cf07f6d72ac7b93fbe` ·
  `completed_evaluations=3` · `total_invocations=3` · `consecutive_degraded=0`.
