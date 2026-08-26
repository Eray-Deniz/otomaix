# Handoff

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi TAMAMLANDI, durum `waiting-review`
- Last updated: 2026-08-26 (on yedinci oturum — review zincirinin 1. adımı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Kapanış raporu: `docs/active/sektor-bilgi-paketi/PLAN1-KAPANIS.md`
- Codex ham log'ları (bu makinede, bu kökten):
  - yürütme: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`
  - basitleştirme: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-simplify-feat-sektor-bilgi-paketi-1.md`

## Resume From

**Sıradaki iş: `/review-claude-codex`.** Zincirin 1. adımı (`/simplify-claude-codex`) bitti ve
commit edildi (`6407f89`); çalışma ağacı TEMİZ.

**Review'in İLK işi hâlâ aynı:** yürütmenin final turunda düzeltilen taşıyıcı-sözleşme fix'i
(`17840c6`) bağımsız hakem görmeden indi. Bu, basitleştirme turunda ele ALINMADI — o tur yalnız
tekrar/ölü kod/adlandırma baktı, davranış bakmadı.

Zincirin kalanı: `/review-claude-codex` → `/security-review-claude-codex` →
`/finish-branch-claude-codex`.

**Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Verification (bu oturum)

**Koşan komutlar / taze çıktı (hepsi commit'ten ÖNCE, HEAD'de):**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **577 passed**
  (oturum başındaki taban ile aynı — basitleştirme test sayısını değiştirmedi, değiştirmemeliydi)
- `cd apps/social/backend && .venv/bin/python -m pytest tests/prompt_regression/ -q` → **121 passed**
  (bayt-değişmezlik kapısı; donmuş fixture'lar DEĞİŞMEDİ)
- `cd apps/social/frontend && npx tsc --noEmit` → **rc=0**
- Commit SONRASI defter kapısı: `ec_footer_parse HEAD` → rc=0;
  `ec_ledger_view <merge-base> . - --post-window` → **rc=0**, stderr temiz, yeni satır
  `T16-simplify | code` olarak doğru sınıflandı

**Pozitif kontrol niteliğinde ölçümler (iddiaların gerçekten ölçüldüğünü gösterenler):**
- Devralınan borç listesi ÖLÇÜLDÜ ve yanlış çıktı: `BrandOut` importu `main`'de birebir aynı
  (`git show main:...` ile), yani devralınan borç; "kullanılmayan pytest importları" test
  dosyalarında ve biri gerçekten kullanılıyor.
- Codex'in eklediği dört adayın dördü de kod okunarak ayrı ayrı doğrulandı — hiçbiri körlemesine
  uygulanmadı. Biri (`filter_channel_dependent` dönüş tipi) çağrı yerine bakılarak teyit edildi:
  iki çağırandan biri düz metin geçiyor.
- Ad değişikliğinin bir kaynak-yokluk kapısını (`assert "scene_pool" not in source`) bozup
  bozmadığı ölçüldü: kapının denetlediği fonksiyon o adı hiç taşımıyor, ve yeni ad eski adı alt
  dize olarak içerdiği için kapı hâlâ ateşlenir.
- Hakemin verdiği iki doğrulama komutu da koşuldu (dosya satır sayısı + üç test dosyası;
  ve geçersiz atfın kalmadığını gösteren arama).

**Codex:**
- Ön-tarama: koştu (Standard mod).
- Final adversarial review: **`verdict: approve`**, kritik/yüksek bulgu YOK.
  - F1 (orta) → `accepted_risk`: ertelenen dosya bölmesinin adlandırılmış evi yoktu.
    **Bu oturumda kapatıldı** — `CURRENT.md`'ye gerçek madde açıldı.
  - F2 (düşük) → **DÜZELTİLDİ**, park edilmedi. Kendi ad değişikliğimin ürünüydü ve politika
    düşüğü advisory saysa da o izin ÖNCEDEN VAR OLAN borç içindir.

**DENENMEYEN / kapsanmayan (bu oturum):**
- **Önyüzde otomatik test YOK** (0 test dosyası, ölçüldü). Frontend'deki 4 düzeltme yalnız tip
  denetimiyle doğrulandı. Hepsi mekanikti (sabit çıkarma, gereksiz karşılaştırma silme, tip
  daraltma) — zamanlama/eşzamanlılık koduna DOKUNULMADI, bu bilinçliydi (Task 15b dersi).
- **Hakem, değişen 10 dosyanın 3'ünü dosya sisteminden okuyamadı.** Değişiklikleri prompt'a
  gömülerek denetlendi; **çevrelerindeki değişmemiş kod denetlenmedi.**
- Bu oturumda hiçbir migration canlıya uygulanmadı; canlı veritabanına karşı sweep koşulmadı
  (kod değişikliği veri yolunu etkilemiyor).
- Devralınan tüm manuel doğrulamalar (arayüz · canlı n8n + Telegram · gerçek uçtan uca üretim ·
  gerçek model çağrıları) hâlâ Plan 2 sonrasındaki tek tura ertelenmiş durumda.

## Risks

**Bu oturumun ürünü — açık kalemler:**
- **[Kapsam sınırı, DÜZELTİLMEDİ]** Üç dosyanın çevre kodu bağımsız hakem görmedi. Ev:
  `/review-claude-codex` — o komut TEMİZ ağaçta koşacağı için taban-tabanlı denetim kullanır ve
  bu kısıt orada DOĞMAZ. Tetik: zincirin kendisi.
- **[ÇÖZÜLMEDİ + evi açıldı]** 1785 satırlık dosyanın zorunlu bölmesi. Ayrım noktası ÖLÇÜLDÜ
  (yaşam döngüsü bölümü, tek yönlü bağımlılık; üstteki hiçbir şey o adlara atıf yapmıyor).
  Ev: `CURRENT.md` → `sector-packages-mandatory-split`. Tetik: review zinciri bittikten sonra.
- **[ÇÖZÜLMEDİ, bilinçle]** İki modüldeki prompt bloğu tekrarı duruyor (Eray kararı).
  Yeniden açılma koşulu: iki yüzeyden biri değişip diğeri kalırsa, ya da bayt kapısının
  koruması gevşerse.

**Devralınan, DEĞİŞMEYEN kalemler (basitleştirme bunlara dokunmadı):**
- **[Bu partinin değil, yürütmenin ürünü — DENETLENMEMİŞ]** Taşıyıcı-sözleşme düzeltmesi
  (`17840c6`) bağımsız hakem görmeden indi. Ev: `/review-claude-codex`, İLK iş.
- **[Manuel adım — Plan 2 sonrası tek tur]** Migration'ların canlıya uygulanması ·
  `N8N_ADMIN_EVENT_SECRET` + Telegram env'leri · n8n workflow importu ve TEK teslim smoke'u ·
  `.env.example`'a satır eklenmesi (sır-dosyası kapısı agent'ı engelliyor) · Task 15'in UI
  doğrulaması.
- **[Eray tetikledi]** Süpürücü ↔ geç webhook terminallik çelişkisi. Ev: `CURRENT.md`.
- **[TETİKLİ]** `sector_packages.sector_id` değişmez değil. Ev: `CURRENT.md`.
- **[MÜŞTERİ yüzeyi]** Marka ayarları otomatik kaydetmesinin dört kayıp yolu. Ev: `CURRENT.md` →
  `brand-settings-save-integrity`. Tetik: canlıya müşteri alınmadan ÖNCE. Önyüz test altyapısı
  ÖN KOŞUL.
- **[Kod tabanı geneli]** Senkron sağlayıcı çağrısı gerçekten kesilemiyor. Ev: `CURRENT.md` →
  `sync-provider-calls-not-cancellable`.
- **[Yeni — bu oturumda ölçüldü]** İçerik kütüphanesinde yoklama döngüsünün sonu yok: kalıcı
  başarısız bir satır sekme açık kaldıkça her 3 saniyede bir sorulmaya devam eder. Bu bir
  **davranış** bulgusudur, basitleştirme adayı değil — bilerek düzeltilmedi. Ev:
  `/review-claude-codex`. Kökü zaten adlandırılmış: süpürücü ↔ geç webhook çelişkisi.
- **[Yeni — bu oturumda ölçüldü]** Aynı partide veritabanı bağlantısını uzun ağ çağrısı boyunca
  tutma konusunda İKİ ZIT karar var: bir uç bağlantıyı bilerek bırakıyor ve gerekçesini yazıyor,
  iki uç bilerek tutuyor. Davranış bulgusu. Ev: `/review-claude-codex`; kökü
  `sync-provider-calls-not-cancellable`.
- **[accepted_risk, checkpoint 12]** Kütüphane yoklaması terminal başarısız satırları sınırsız yokluyor.
- **[Plan 2 teslim kalemi]** Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli ·
  `recovered` modu + geri-dönüş mesajı (F23 kapanışı).
- **[Residual]** 033 ve 034 için geri alma script'i YOK (plan istemedi).
- **[Etiketler — evi `/finish-branch-claude-codex`]** `backup/pre-footer-fix` ·
  `backup/pre-t3-kind-fix` · `backup/pre-t15b-footer-fix` · `backup/pre-t16-kind-fix`
  merge/PR kararından sonra silinir.
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı silinemez.
- `accepted_risk` (test altyapısı): **eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür** ·
  migration keşfi tekrarlı numarayı reddetmiyor (belgeli) · `db` fixture geri sarma testi yok ·
  `sector_research_artifacts` TRUNCATE regresyonu yok.
- **[Eray risk kabulü]** On-prem PG16 ↔ 032'nin PG18 kolonu: çözülmedi + park edildi.
- **F17 (Eray):** damga = edited-lineage atfı. **Yeniden açtırma.**

**Temizlik borcu — DÜZELTME (devralınan liste yanlıştı):** eski HANDOFF "iki dosyada kullanılmayan
`pytest` importu · `brands.py`'de kullanılmayan `BrandOut`" diyordu ve bunları bu partinin borcu
sayıyordu. ÖLÇÜLDÜ: `BrandOut` importu `main`'de de aynı (devralınan borç, kapsam dışı bırakıldı);
`pytest` importları test dosyalarında (kapsam dışı) ve biri gerçekten kullanılıyor. Aynı ölçümde
`avatar.py`'de kullanılmayan bir import daha bulundu — o da devralınan.

## Notes For Claude

- `next: /review-claude-codex → /security-review-claude-codex → /finish-branch-claude-codex`
- `simplify_completed: 2026-08-26` · `simplify_commit: 6407f89` · `simplify_verdict: approve`
- `branch_pushed: <push kapısında karara bağlanır>`
- **ARAÇ TUZAĞI (bu oturumda ölçüldü, bir sonraki komutta da vurabilir):** sır taraması bir dosyayı
  dışladıysa ve o dosyada KAYDEDİLMEMİŞ değişiklik varsa çalışma-ağacı denetim ortamı **hiç
  kurulmaz** (rc=2, Codex çağrılmaz, stderr'de yalnız `No such file or directory` görünür).
  Tetikleyen desen `api_key=<ifade>` — model çağıran her dosya. **Temiz ağaçta sorun YOK**, çünkü
  taban-tabanlı denetim commit'lerden okur. Ayrıntı ve çözüm: memory
  `feedback_substrate_dirty_secret_excluded_file`.
- **Codex 480s'de timeout verirse** önce 120s canlılık yoklaması, sağlamsa `CSS_CALL_TIMEOUT=1200s`
  ile BİR tekrar. Bu oturumda tam olarak bu gerekti ve işe yaradı.
- **Bu dalda ETİKETSİZ COMMIT ATMA.** Defter penceresi merge-base'ten başlıyor, yani her commit
  pencere içinde; footer'sız commit `ec_ledger_view --post-window`'u **rc=4** ile düşürür (ölçüldü).
  Gramer: `Exec-Task` = `T<N>` veya `T<N>-<sonek>`; `Exec-Kind` ∈
  code|docs-only|migration|red-only|green-only|merge; `code` kindi HEM test HEM üretim dosyası
  gerektirir; `Exec-Plan` tarihli kanonik plan yolu olmalı ve aktif planla AYNI.
- **Hakem önerisini körlemesine uygulama.** Bu oturumda dört öneriden dördü de doğru çıktı ama
  dördü de ÖNCE ölçüldü; biri kaynak-metin üzerinden çalışan bir kapıya çok yakındı.
- **Kendi düzeltmenin yan etkisini ÖLÇ.** Bu oturumda iki kez kendi düzeltmem kusur doğurdu:
  biri anında tip denetiminde yakalandı (eksik import), biri hakem tarafından bulundu (yorumda
  geçersiz atıf). İkincisi düşük seviyeydi ama park EDİLMEDİ — kendi ürünüm olduğu için.
- **Tip denetleyicisi uyarılarını otomatik kendine mal etme.** Bu oturumda birçok uyarı "yeni"
  diye göründü ama `HEAD`'deki satırlarla birebir aynıydı; ayrımı `git show HEAD:<yol>` ile
  yapmak gerekti.
- **Mutasyonu geri alırken `git checkout <dosya>` KULLANMA** — yedek kopyadan geri yaz.
