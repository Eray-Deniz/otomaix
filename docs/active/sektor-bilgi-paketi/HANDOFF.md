# Handoff

## Context
- Task: sektor-bilgi-paketi — **Plan 1 yürütmesi TAMAMLANDI**, `waiting-review`
- Last updated: 2026-08-25 (on altıncı oturum — Task 16 kapanışı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Kapanış raporu: `docs/active/sektor-bilgi-paketi/PLAN1-KAPANIS.md`
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Plan 1'in 16 görevinin 16'sı yazıldı.** Açık kapı YOK.
- Yürütme kapandı: `status: waiting-review`. Sıradaki zincir `/simplify-claude-codex` →
  `/review-claude-codex` → `/security-review-claude-codex`.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Verification (bu oturum)

**Kapanış alanları (kanonik):**
- `full_test_suite: PASS` (577 + 121)
- `mechanical_ledger_sweep: PASS` (rc=0)
- `pre_execution_codex_review: ran`
- `checkpoint_codex_reviews: ran 17` (sonuncusu 4 turda `approve`)
- `final_codex_execution_review: override`
- `final_codex_execution_review_reason: null`
- `checkpoint_execution_review_status: ok`
- `final_unresolved_high_severity_override: true`
- `unresolved_critical_high: none` — tur 4'ün yüksek bulgusu DÜZELTİLDİ; override'ın konusu
  bulgunun kendisi değil, **düzeltmenin bağımsız hakemce doğrulanmamış olmasıdır.**
  Denetim satırı: `2026-08-25 — FINAL OVERRIDE: dört final turu koşuldu, hiçbiri approve ile
  bitmedi; tur 4'ün yüksek bulgusu (032 taşıyıcı sözleşmesi) düzeltildi ve kendi pozitif
  kontrolleriyle ölçüldü, ancak review bütçesi dolduğu için yeniden denetlenmedi.
  accepted findings: [none unresolved; unverified fix: 032 carrier contract]`

**Koşan komutlar / taze çıktı (hepsi HEAD'de):**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **577 passed**
  (oturum başında 538; +39 bu oturumun ürünü).
- `cd apps/social/backend && .venv/bin/python -m pytest tests/prompt_regression/ -q` → **121 passed**
  (byte-exact freeze kapısı; donmuş fixture'lar bayt DEĞİŞMEDİ).
- Marka → kök sektör sweep'i, CANLI veritabanına karşı, hedef parmak izine bağlı
  fail-closed komutla → `differences: 0`, rc=0. Komut ve parmak izi kapanış raporu §0'da.
- `ec_mechanical_sweep` (defter bütünlüğü) → **rc=0**; türetilmiş defter görünümü 100 commit,
  T1–T16 tamamı etiketli.
- `command-blocks-maint.sh verify` → **PASS**.

**Pozitif kontroller (kapıların gerçekten ölçtüğünü kanıtlayanlar — hepsi taze):**
- Arayüz sözleşme testi: **10 mutasyon**, hepsi ilgili testi düşürdü (tek havuz · takvim
  denetimi kapalı · byte-exact no-op · `insert_draft`'ın `active` yazması · kolon adı ·
  birincil anahtar · varsayılan · yabancı anahtar · tetikleyici bağlanması · UNLOGGED tablo).
- Migration garanti blokları: **tuzak testleri** — yanlış tip · PK'sız · UNLOGGED · RLS açık ·
  fazladan `CHECK (false)` · fazladan UNIQUE · yazımı reddeden tetikleyici · aynı adda yanlış
  kolonlu/benzersiz/başka tablodaki indeks · yabancı anahtarı düşürülmüş taşıyıcı kolon.
- **Kapıların kendisi ölçüldü:** yeni girdiler bloklardan çıkarılınca aynı tuzaklar GEÇİYOR —
  yani testler yeni kapıları ölçüyor, öncekileri değil.
- Atomiklik: bayraksız koşumda kalıntı KALIYOR, `--single-transaction` ile KALMIYOR (ikisi de
  ölçüldü; test her iki yönü de bağlıyor).
- Sweep komutu: doğru parmak izi rc=0 · ihlal + doğru parmak izi rc=1 · temiz + yanlış parmak
  izi rc=1.

**Codex:**
- Checkpoint 17 (Task 16): **4 tur** → `approve`.
- Final execution review: **4 tur**. Turların hepsi gerçek, ulaşılabilir kusur buldu:
  migration'ların atomik olmaması · 032/033'ün imza denetlememesi · izin listesinin fazladan
  nesneyi görmemesi · dizin symlink'i · 011'in geçersiz indeks kalıntısı · indeks kimliğinin
  ada bağlı olması · taşıyıcı sözleşmenin denetlenmemesi. **İkisi, bir önceki turun
  düzeltmesinden doğdu** (F4→F5 ve tur 2→tur 3).
- **KAPANIŞIN DÜRÜST DURUMU:** hiçbir tur `approve` ile bitmedi. Tur 4'ün yüksek bulgusu
  düzeltildi ama **o düzeltme bağımsız hakem tarafından DENETLENMEDİ** — kendi pozitif
  kontrolleriyle ölçüldü. Kullanıcı bir ek tur onayladı ve o tur koşuldu; bütçe doldu.

**DENENMEYEN / kapsanmayan:**
- **TÜM MANUEL DOĞRULAMALAR PLAN 2 SONRASINA ERTELENDİ (Eray kararı, 2026-08-25).**
  Kapsam: Task 15'in arayüz doğrulaması · canlı n8n importu ve gerçek Telegram teslimi ·
  gerçek arayüzde uçtan uca üretim · öneri uçlarının GERÇEK model çağrısıyla koşulması.
  Ev: **Plan 2 bitiminde koşulacak tek doğrulama turu.**
- Canlıya hiçbir migration uygulanmadı (032 · 033 · 034). Uygulama komutu kapanış raporu
  "MANUEL ADIMLAR" §1'de; **runner KULLANILMAZ** (defter tutmaz, 003'te takılır).
- Gerçek bir sektör paketi hiç yazılmadı.
- Kota kapısı davranışsal ölçülmedi (Redis ister; ev kuralı Redis yokken fail-open).
- `IS JSON OBJECT` · `conenforced` · PG17+ `NOT NULL` kısıt satırları yalnız PostgreSQL 18.3'te
  ölçüldü; PG16 davranışı BELGEYE dayanıyor. Manifestler bu farkı bilerek dışlıyor.

## Risks

**Bilinçli tasarım kararları (bulgu SAYILMAZ):**
- Alt sektör YAZIM kapısı aktif paket şartı ARAMAZ (K-43: paketi arşivlenen markanın ataması
  korunur). Aday kümesi neyin ÖNERİLECEĞİNİ belirler, neyin saklanabileceğini değil.
- Öneri ucunun kota kapısı Redis yokken fail-open'dır — ev kuralının belgeli kararı.
- `record_admin_event` aynı anahtarla gelen FARKLI olayı yutar; "ilk yazım kazanır" bilinçlidir.
- Çözümleyici hiçbir hatada üretimi bloklamaz; eksik alan ile açık NULL bugün ayırt edilmez.
- Tekrarlı migration numarası REDDEDİLMEZ — eşit numarada dosya adına düşmek belgeli davranış.
- Sunucudaki koşullu yazım kapısı ve 5 testi depoda UYKUDA (hiçbir çağıran sürüm göndermiyor).

**Açık kalemler — hepsinin evi VAR:**
- **[Bu oturumun ürünü, DENETLENMEMİŞ]** Tur 4'ün taşıyıcı-sözleşme düzeltmesi (`33f7779` →
  yeniden yazımdan sonra `17840c6`) bağımsız hakem görmeden indi. Ev: `/review-claude-codex`
  zinciri — kapanış sonrası ilk adım. Tetik: zincirin kendisi.
- **[Manuel adım — Plan 2 sonrası tek tur]** Migration'ların canlıya uygulanması ·
  `N8N_ADMIN_EVENT_SECRET` + Telegram env'lerinin kurulması · n8n workflow importu ve TEK
  teslim smoke'u · `.env.example`'a satır eklenmesi (sır-dosyası kapısı agent'ı engelliyor) ·
  Task 15'in UI doğrulaması.
- **[Eray tetikledi]** Süpürücü ↔ geç webhook terminallik çelişkisi. Ev: `CURRENT.md`.
  Tetik: sektör bilgi paketi işi TAMAMEN bittikten sonra.
- **[TETİKLİ]** `sector_packages.sector_id` değişmez değil. Ev: `CURRENT.md`.
- **[MÜŞTERİ yüzeyi]** Marka ayarları otomatik kaydetmesinin dört kayıp yolu. Ev: `CURRENT.md` →
  `brand-settings-save-integrity`. **Tetik: canlıya müşteri alınmadan ÖNCE.** Önyüz test
  altyapısı ÖN KOŞUL.
- **[Kod tabanı geneli]** Senkron sağlayıcı çağrısı gerçekten kesilemiyor. Ev: `CURRENT.md` →
  `sync-provider-calls-not-cancellable`.
- **[accepted_risk, checkpoint 12]** Kütüphane yoklaması terminal başarısız satırları sınırsız yokluyor.
- **[doğrulama boşluğu — evi: kuyumculuk pilotu]** Uçtan uca gerçek akış ölçümü.
- **[Plan 2 teslim kalemi]** Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli ·
  `recovered` modu + geri-dönüş mesajı (F23 kapanışı).
- **[Residual]** 033 ve 034 için geri alma script'i YOK (plan istemedi).
- **[Temizlik borçları — evi `/simplify-claude-codex`]** İki dosyada kullanılmayan `pytest`
  importu · `brands.py`'de kullanılmayan `BrandOut`.
- **[Etiketler — evi `/finish-branch-claude-codex`]** `backup/pre-footer-fix` ·
  `backup/pre-t3-kind-fix` · `backup/pre-t15b-footer-fix` · `backup/pre-t16-kind-fix`
  merge/PR kararından sonra silinir.

**Devralınan, değişmeyen kalemler:**
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı silinemez.
- Belgeli sınırlar (testle pinli, borç DEĞİL): ayraçsız kanal işareti yakalanmaz · tam genişlikli
  ayraçlı etiket tanınır ama basımdan çıkarılamaz.
- `accepted_risk` (test altyapısı): **eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür** ·
  migration keşfi tekrarlı numarayı reddetmiyor (belgeli) · `db` fixture geri sarma testi yok ·
  `sector_research_artifacts` TRUNCATE regresyonu yok.
- **[Eray risk kabulü]** On-prem PG16 ↔ 032'nin PG18 kolonu: çözülmedi + park edildi.
- **F17 (Eray):** damga = edited-lineage atfı. **Yeniden açtırma.**

## Notes For Claude

- `next: /simplify-claude-codex → /review-claude-codex → /security-review-claude-codex`
- `execute_completed: 2026-08-25`
- `branch_pushed: <push kapısında karara bağlanır>`
- **İLK İŞ:** tur 4'ün düzeltmesi denetlenmedi — review zinciri onunla başlasın.
- **ÖLÇEMEDİĞİN YERE ELLE EŞZAMANLILIK KODU YAZMA.** (Task 15b dersi; önyüzde otomatik test
  altyapısı yok, "okundu + derlendi" araya-girme hatalarını tanım gereği yakalamaz.)
- **Kendi düzeltmenin yan etkisini ÖLÇ.** Bu oturumda iki kez kendi düzeltmem yeni kusur
  doğurdu ve ikisini de hakem buldu: sweep komutunun çıkış kodunu yutması, indeks kimliğinin
  ada bağlı kalması. Düzeltmeyi yazınca "bu neyi bozar" diye AYRICA ölç.
- **Hakem önerisini körlemesine uygulama.** Tekrarlı-numara guard'ı belgeli bir davranışı
  kırıyordu; mevcut bir test onu yakaladı. Öneriyi önce deponun kendi sözleşmesine karşı oku.
- **`.sql` dosyası defter sınıflandırmasında "kod" DEĞİLDİR** → migration commit'i
  `Exec-Kind: migration` alır. Bu oturumda iki commit `code` etiketiyle indi ve mekanik kapıyı
  düşürdü; mesaj-yeniden-yazımıyla düzeltildi (`backup/pre-t16-kind-fix`).
- **Taban ref'i daima TAM SHA ver.** Kısaltılmış SHA substrat kurulumunda rc=2 ile düşer.
- **ARAÇ TUZAĞI:** `run_codex_scan` `$COMPANION` ve `$PROMPT`'u KULLANIR ama TANIMLAMAZ;
  çağıran kurar. Kurulmazsa `node ""` koşar — arka planda sessizce boş, ön planda asılı.
  stderr'de `[codex]` işareti YOKSA çağrı kurulmamıştır.
- **Codex 480s'de timeout verirse** önce 120s canlılık yoklaması, sağlamsa `CSS_CALL_TIMEOUT=1200s`
  ile BİR tekrar.
- **Mutasyonu geri alırken `git checkout <dosya>` KULLANMA** — yedek kopyadan geri yaz.
