# Handoff

## Context

- Task: sektor-bilgi-paketi — Plan 1 yürütmesi TAMAMLANDI, durum `waiting-review`
- Last updated: 2026-08-26 (on dokuzuncu oturum — review zincirinin 3. adımı: güvenlik review'ı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**; `main`'in ~118 commit önünde)
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

**Zincirin 3. adımı (`/security-review-claude-codex`) BİTTİ. Güvenlik kapısı TEMİZ:
çözülmemiş kritik/yüksek bulgu YOK, dual-review üç turda da tam, kapsam boşluğu yok.**

Sıradaki iki iş, bu sırayla:

1. **`sector-packages-mandatory-split`** (`CURRENT.md`) — `sector_packages.py` 1804 satır, zorunlu
   bölme eşiğinin üstünde. **Tetiği DOLDU** (tetik "review zinciri bittikten sonra, dal kapanışından
   önce"ydi). Ayrım noktası daha önce ÖLÇÜLDÜ: yaşam döngüsü bölümü (`LifecycleError`'dan
   `deactivate_package`'a, ~490 satır) tek yönlü bağımlı. Gövdenin kalanı çift yönlü bağlı; onu
   bölmek üçüncü bir "ortak ilkeller" modülü ister, yani yapı değil dağılma olur. Üretimde dosya
   dışı çağıran YOK; üç test dosyası yaşam döngüsü adlarını içe aktarıyor.
2. **`/finish-branch-claude-codex`** — dört seçenek (merge / PR / tut / sil).

**Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Verification (bu oturum)

**Koşan komutlar / taze çıktı (son commit `00bd771`):**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **657 passed** (103s)
  (oturum başı taban 580; fark bu oturumda yazılan güvenlik regresyonları)
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

## Risks

**Bu oturumun ürünü:**
- **[`accepted_risk`, düşük]** Kısa video 2. aşama ürün kapısı testsiz (yukarıda). Ev: dal kapanışı.
- **[`accepted_risk`, düşük, DEVRALINAN]** Site analizi ucunda hız sınırı yok.
- **[Ders — kayda değer]** Güvenlik review'ının üç turundan ikisi benim kendi düzeltmelerimin
  eksiklerini buldu; biri de benim ürettiğim geçersiz bir bulguyu temizlemeye gitti. İki kök neden
  de aşağıda Notes'ta kayıtlı.

**Devralınan, DEĞİŞMEYEN kalemler:**
- **[Manuel adım — Plan 2 sonrası tek tur]** Migration'ların canlıya uygulanması ·
  `N8N_ADMIN_EVENT_SECRET` + Telegram env'leri · n8n workflow importu ve TEK teslim smoke'u ·
  `.env.example`'a satır eklenmesi (sır-dosyası kapısı agent'ı engelliyor) · Task 15'in UI doğrulaması.
- **[TETİĞİ DOLDU — sıradaki iş]** `sector-packages-mandatory-split` (`CURRENT.md`).
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
