# Handoff

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi TAMAMLANDI, durum `waiting-review`
- Last updated: 2026-08-26 (on dokuzuncu oturum — review zincirinin 3. adımı: güvenlik review'ı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Review raporu: `docs/reviews/2026-08-26-feat-sektor-bilgi-paketi.md`
- Kapanış raporu (Plan 1): `docs/active/sektor-bilgi-paketi/PLAN1-KAPANIS.md`
- Codex ham log'ları (bu makinede, bu kökten):
  - review attempt-1: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-review-feat-sektor-bilgi-paketi-1.md`
  - review closure: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-review-feat-sektor-bilgi-paketi-2.md`
  - basitleştirme: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-simplify-feat-sektor-bilgi-paketi-1.md`
  - yürütme: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Resume From

**Sıradaki iş: ÜÇ YÜKSEK GÜVENLİK BULGUSUNUN DÜZELTİLMESİ** (plan-yürütme komutuyla; Eray kararı
2026-08-26). Zincirin 3. adımı (`/security-review-claude-codex`) KOŞTU — ayrıntı bu belgenin sonundaki
"Güvenlik review'ı koştu" bölümünde; bulgular `TASK.md` `# Open Problems`'ta. Kapı BLOKE, açık kapı VAR.
Zincirin 2. adımı (`/review-claude-codex`) daha önce bitmişti; yedi yüksek bulgusu düzeltilip commit edildi.

**Devralınan "ilk iş" borcu KAPANDI:** yürütmenin final turunda bağımsız hakem görmeden inen
taşıyıcı-sözleşme fix'i (`17840c6`) bu review'da denetlendi — iki hakem de 032/033/034'ün
doğrulama bloklarını okudu ve oradan H1 çıktı.

Zincirin kalanı: üç high fix → attempt-2 kapanış turu (aynı pinli sözleşme) → `/finish-branch-claude-codex`.

**Tetiği DOLDU (ama sıra fix'lerden sonra):** `sector-packages-mandatory-split` (`CURRENT.md`) —
1804 satırlık dosyanın zorunlu bölmesi. Tetik "review zinciri bittikten sonra"ydı; güvenlik review'ı
koştu. Ama önce üç high fix + kapanış turu gelir — 490 satırlık taşımayı fix'lerin önüne koymak
kapanış hakemine asıl işi değil taşımayı okuturdu (aynı gerekçe 2026-08-26'da bir kez verildi).

**Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Verification (bu oturum)

**Koşan komutlar / taze çıktı (hepsi son commit'te, `1e12af9`):**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **580 passed** (105s)
  (oturum başı taban 577'ydi; +3 bu turda yazılan regresyon testleri)
- `cd apps/social/backend && .venv/bin/python -m pytest tests/prompt_regression/ -q` → **121 passed**
  (bayt-değişmezlik kapısı; donmuş fixture'lar DEĞİŞMEDİ)
- `cd apps/social/frontend && npx tsc --noEmit` → **rc=0**
- `ec_footer_parse <sha> /root/otomaix` yedi düzeltme commit'i + rapor commit'inde → **rc=0**

**Pozitif kontroller — her yüksek bulgu KENDİ ölçümüyle kapatıldı, hiçbiri okumaya bırakılmadı:**
- **H1:** gerçek `pgvector/pgvector:pg16` (16.15) konteyneri. Düzeltme ÖNCESİ dosyalar
  `column k.conenforced does not exist` ile düşüyor; SONRASI 001→034 tamamı geçiyor, beş tablo
  oluşuyor. Zayıflatma kontrolü: PG18'de gerçekten `NOT ENFORCED` bir FK yaratıldı — jsonb yolu
  da doğrudan okuma da `false` diyor, maskeleme yok. Hakem ayrıca PG16'da `NOT VALID` FK ile
  pozitif kontrol koştu (`rc=3`, doğru etiketle reddetti).
- **H2 / N1 / N3:** üç mutasyon kontrolü. Savepoint kaldırılınca `InFailedSQLTransactionError`;
  sarmalayıcı koşulsuz yapılınca koşullu-açılma testi düşüyor; `_notify_admin` savepoint'i
  kaldırılınca ikinci test düşüyor. Her mutasyondan sonra dosya geri yüklendi.
- **H3 / N-H3:** koşucunun BEŞ dalı stub'lı `docker` ile ölçüldü — dolu→rc=1, boş→rc=0 (34 dosya),
  kaçış→rc=0, sonda hatası→rc=1, sonda çöpü→rc=1. Son iki dal düzeltme öncesi GEÇİYORDU.
  `003`'ün idempotent olmadığı canlı DB'de ölçüldü (`42P07`).
- **H4 / N-H4:** premisler ölçüldü — önyüzde `beforeunload`/`visibilitychange` sıfır sonuç;
  sayfa marka değişiminde remount olmuyor (`currentBrand?.id` effect'i + `switchBrand` state).

**Hakemler:** attempt-1 ve closure'ın ikisi de **dual** (claude_status: ran, codex_status: ran).
`total_invocations=2`, `consecutive_degraded=0`. Degradasyon YOK, override kullanılmadı.

**DENENMEYEN / kapsanmayan (bu oturum):**
- **Önyüzde otomatik test YOK.** İki önyüz düzeltmesi (H4, N-H4) okuma + `tsc` + lint ile
  doğrulandı, KOŞAN bir testle değil. Çapraz-marka dizisi regresyon olarak çalıştırılamıyor.
  Bu, `brand-settings-save-integrity`'nin ilan edilmiş ön koşuludur.
- **Gerçek `docker compose` ile uçtan uca yerel kurulum** (`setup.sh`) denenmedi.
- **Spec'in 7-17. bölümleri** hiçbir hakem tarafından okunmadı (Claude hakemi kapsama beyanında
  açıkça yazdı). Kapsam boşluğudur.
- **`rollback/032_down.sql`** (265 satır) hiçbir turda satır satır okunmadı.
- **`onboarding/page.tsx`** (107 satır ekleme) okunmadı.
- **034'ün DDL'i** servis koduyla karşılaştırılmadı (attempt-1'de yalnız grep'lendi).
- **n8n workflow'unun Code düğümlerinin JS gövdeleri** okunmadı.
- Testlerin ~15.000 satırının çoğu iki hakemde de satır satır okunmadı.
- Canlıya hiçbir migration uygulanmadı; canlı veritabanına karşı sweep koşulmadı.
- Devralınan tüm manuel doğrulamalar (arayüz · canlı n8n + Telegram · gerçek uçtan uca üretim ·
  gerçek model çağrıları) hâlâ Plan 2 sonrasındaki tek tura ertelenmiş durumda.

## Risks

**Bu oturumun ürünü — açık kalemler:**
- **[`accepted_risk`, ama BU PARTİNİN ürünü — TASK.md Open Problems'ta]** `resolve_sector`
  istisnası yakalanmıyor (500 yerine 503 olmalıydı) + ölü geri-düşüş dalı · `schema_version`
  hiç okunmuyor · K-04 talimatı üç metne ayrışmış. Üçü de devralınan borç DEĞİL.
- **[Kapsam sınırı, DÜZELTİLMEDİ]** Önyüz düzeltmeleri koşan testle doğrulanmadı. Ev:
  `brand-settings-save-integrity` (`CURRENT.md`), ön koşulu önyüz test altyapısı.
- **[KAPANIŞTA KARAR GEREKTİRİR — evi `/finish-branch-claude-codex`]** Bağımsız review'ın
  BEŞ kapsama boşluğu var ve hiçbiri "denetlendi" sayılamaz: spec'in 7-17. bölümleri ·
  `rollback/032_down.sql` (265 satır) · `onboarding/page.tsx` (107 satır) · 034'ün DDL'inin
  servis koduyla uyumu · n8n workflow'unun Code düğümlerinin JS gövdeleri. Güvenlik review'ı
  bunların bir kısmına DEĞECEK ama merceği güvenliktir, spec-uyumu değil. Dal birleştirmeye
  giderken bu, "kabul ediyorum" ya da "ek tur" diye AÇIKÇA kararlaştırılmalı — sessizce
  kapanmamalı. Dürüst etiket: denetlenmedi, evi kapanış adımı.
- **[Ders — kayda değer]** Bu turda düzeltilen yedi yüksek bulgunun ÜÇÜ, ilk dört düzeltmenin
  kendi yan etkisiydi ve hiçbiri mekanik doğrulamayla değil, bağımsız kapanış turuyla yakalandı.
  Bir sınıfı kapatan düzeltme yeni sınıf açabilir; kapanış turu atlanamaz.

**Devralınan, DEĞİŞMEYEN kalemler:**
- **[Manuel adım — Plan 2 sonrası tek tur]** Migration'ların canlıya uygulanması ·
  `N8N_ADMIN_EVENT_SECRET` + Telegram env'leri · n8n workflow importu ve TEK teslim smoke'u ·
  `.env.example`'a satır eklenmesi (sır-dosyası kapısı agent'ı engelliyor) · Task 15'in UI
  doğrulaması.
- **[TETİK BEKLİYOR — güvenlik review'ından sonra, dal kapanışından önce]**
  `sector-packages-mandatory-split` (`CURRENT.md`).
- **[Eray tetikledi]** Süpürücü ↔ geç webhook terminallik çelişkisi. Ev: `CURRENT.md`.
  Review bunu bağımsız olarak yeniden buldu (kütüphane yoklaması sınırsız — iki hakem de).
- **[TETİKLİ]** `sector_packages.sector_id` değişmez değil. Ev: `CURRENT.md`.
- **[MÜŞTERİ yüzeyi]** Marka ayarları otomatik kaydetmesinin devralınmış kayıp yolları (sıra
  bozulması · iki sekme · başarısız yazımın taslağı yok etmesi). Ev: `CURRENT.md` →
  `brand-settings-save-integrity`. Tetik: canlıya müşteri alınmadan ÖNCE.
- **[Kod tabanı geneli]** Senkron sağlayıcı çağrısı gerçekten kesilemiyor. Ev: `CURRENT.md`.
- **[Araç]** Kirli ağaçta Codex denetim ortamı kurulamıyor (`codex-substrate-dirty-secret-excluded-file`)
  ve `run_codex_scan` önkoşul kapısı yok (`codex-scan-substrate-preflight-guard`). İkisi de
  `CURRENT.md`'de; bu oturumda TEMİZ ağaçta çalışıldığı için ikisi de doğmadı.
- **[Plan 2 teslim kalemi]** Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli ·
  `recovered` modu + geri-dönüş mesajı (F23 kapanışı).
- **[Residual]** 033 ve 034 için geri alma script'i YOK (plan istemedi).
- **[Etiketler — evi `/finish-branch-claude-codex`]** `backup/pre-footer-fix` ·
  `backup/pre-t3-kind-fix` · `backup/pre-t15b-footer-fix` · `backup/pre-t16-kind-fix`
  merge/PR kararından sonra silinir.
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı silinemez.
- `accepted_risk` (test altyapısı): **eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür**
  (bu oturumda GÖZLENDİ — kapanış hakemi kendi pytest'ini koşarken 20 test çöktü, tekrar koşumda
  geçti) · migration keşfi tekrarlı numarayı reddetmiyor (belgeli) · `db` fixture geri sarma
  testi yok · `sector_research_artifacts` TRUNCATE regresyonu yok.

## Notes For Claude/Codex

- **Güvenlik review'ı için hazır zemin:** bu review'ın güvenlik-yüzeyi sınıflaması `true` çıktı
  (ölçüldü: 50 sır/hmac, 468 authz/sahiplik, 6 migration, 1 kabuk script'i eşleşmesi), yani
  `/security-review-claude-codex` ATLANMAZ ve bu review güvenlik-checklist eki KOYMADI.
- **Codex bağımsızlığı:** attempt-1'de Codex kendi inisiyatifiyle `docs/active/CURRENT.md` ve
  `TASK.md`'yi okudu. Orkestratör vermedi. Güvenlik review'ında aynı şey olursa bulguların
  bilinen-sorun listesinden etkilenmiş olabileceği not edilmeli.
- **Sözleşme sapması (beyan, raporda da var):** gereksinim metninin iki hakemin prompt'una
  GÖMÜLMESİ bu boyutta imkânsız — tek argüman sınırı 131.072 bayt (ölçüldü), gömülü prompt
  180.619 bayttı. İkisi de aynı pinli worktree'deki aynı donmuş dosyayı okudu, hash doğrulandı.
  Güvenlik review'ında aynı sınır çıkacaktır.
- **Codex 480s'de kesiliyor** (attempt-1'de `rc=124`). Asılma değil, uzun koşum — log'da komutlar
  kesilme anına kadar `exit 0` veriyordu. 1200s dış timeout + prompt'a "keşfi genişletmeye devam
  edip kesilme, okumayı bitir ve çıktıyı ver" bütçe talimatıyla tamamlandı. Aynı deseni bekle.

### Güvenlik review'ı koştu (2026-08-26, zincirin 3. adımı) — sıradaki iş DÜZELTME

- **Sonuç: 3 high + 5 medium/low; kritik yok. Kapı BLOKE** (`security-risk`), `dual-review` tamam,
  kapsam boşluğu yok. Rapor: `docs/security-reviews/2026-08-26-feat-sektor-bilgi-paketi.md`
  (commit `e792ae9`). Üç high `# Open Problems`'a işlendi — **sıradaki executor'ın girdisi budur.**
- **Eray kararı (2026-08-26): ÜÇÜ DE düzeltilecek**, plan-yürütme komutuyla (ara hakem kontrolleriyle).
  Devralınan/bu-dalın-ürünü ayrımı raporda duruyor ama düzeltme kapsamı üçünü de içeriyor.
- **Ledger (attempt-1, pinli):** `review_target_id`
  `security-review:feat-sektor-bilgi-paketi:5a9d5d4220d0a58db84dc23f274199491d91216b` ·
  `ledger_locator` `task:sektor-bilgi-paketi` · `pinned_contract_hash`
  `0f9a7629fc2fa17dd8fbd212492902ce7f1b495b2ac681cf07f6d72ac7b93fbe` ·
  `completed_evaluations=1` · `total_invocations=1` · `consecutive_degraded=0`.
- **Fix'ler indikten SONRA attempt-2 kapanış turu ZORUNLU** (aynı pinli sözleşmeyle, dar kapsam:
  dokunulan dosyalar + doğrudan çağıranları + komşu testler + etkilenen config). O tur koşmadan
  `/finish-branch-claude-codex` ilerlemez; koşulmazsa kapanış raporu "fix re-review görmedi" satırı taşır.
- **Politika dışı NOT (rapor gömmedi, buraya da geçiyor):** paket içeriğinin ham metni hata kaydına
  → n8n → Telegram'a taşınıyor (`sector_packages.py:263/272/280` → `:656` → n8n `Detay:`). Politika
  low'u `accepted_risk` sayıyor AMA bu, dalın kendi yazdığı sözleşmeyi (`033_package_events.sql:14`)
  delen kendi gerilemesidir ve fix'i tek satır: ham metin yerine sınıf taşı. Düzeltme turuna dahil edilmeli.
- **Codex bağımsızlığı — kirlenme (ölçüldü):** Codex her iki çağrıda da orkestratör vermeden
  `docs/active/CURRENT.md` + `TASK.md` okudu. Bu yüzden "kesilemeyen senkron sağlayıcı çağrısı"
  bulgusu bağımsız keşif SAYILMAZ — o madde zaten `CURRENT.md`'de park edilmişti.
- **Codex bütçesi:** 480s'de yine `rc=124` (28 alt-komut, hepsi `exit 0` — asılma değil). 1200s'lik
  ikinci çağrı byte-identical prompt'la `rc=0` verdi. Sentetik liveness-probe koşulmadı; gerekçe
  raporda ve `$CODEX_LOG`'da. **Aynı deseni bekle: ilk turda 480s yetmiyor.**
- **Ham kanıt (bu makinede, bu kökten):**
  - Codex: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-secreview-feat-sektor-bilgi-paketi-1.md`
  - Claude alt-hakem: aynı dizinde `...-1.claude.md`
- **Temizlik borcu:** `docs/reviews/.ledger-index/` bu turda oluştu ve **untracked**. Commit kapısı
  yalnız rapor dosyasını eklemeye izin verdiği için tracked edilmedi. Kapanışta karar: izlensin mi
  (oturumlar arası ledger kalıcılığı için gerekli) yoksa yok sayılsın mı.
