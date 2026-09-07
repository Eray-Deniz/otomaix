---
task: sektor-bilgi-paketi-plan2
written: 2026-09-07
---

# Resume From

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-09-07 09:05) — bu anlatı yürütme öncesine aittir; güncel durum TASK.md "Notes For Claude" + git defterinden okunur, çelişkide onlar esastır.

**Sıradaki iş Task 7 — `brief-doctor` mekanik girdi kapısı** (plan satır 938).

Bu oturum yeni bir plan görevi indirmedi. Eray'ın talebi üzerine **bilinçle park edilmiş dört
kalem** kapatıldı ve **checkpoint 5** koşuldu. Ayrıntı TASK.md "Current Status"ta; burada
tekrarlanmaz.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** → Adım 7 (Task 7 dispatch).

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
**Bu dosya git'e girmiyor** — kaybolursa git defteri ve commit mesajları esastır.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **Bu kez İLERLETİLDİ ve gerekçesi var:** checkpoint 5 iki tur sürdü ve tur 2 **`approve`**
> döndü. Önceki üç oturumun aksine sayaç fail-safe bırakılmadı; sıradaki checkpoint'in tabanı
> artık `2b468e8d`. Checkpoint 3 ve 4'ün `approve` almamış aralıkları bu turun tabanına dâhildi,
> yani **artık incelendi** — o borç kapandı.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit **`2b468e8d`** (bu devir commit'i onun
üstüne biner). **Push EDİLMEDİ.**
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: bu oturum ona DOKUNMADI.
**Yedek etiket `backup/pre-footer-fix-20260830`** duruyor; silinme koşulu TASK.md'de.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **Ek metni kodla uyumsuz, İKİ yerde** (değişmedi): R12(a2)(d) amende edildi ve aktör
   kapısının tanım yeri ekin gösterdiği modül değil.
2. **Ekin kendi içinde çelişkisi** (değişmedi): ayak (d) düzyazısı `BEFORE UPDATE OR DELETE`,
   bağlayıcı SQL bloğu `BEFORE UPDATE`. Evi Task 8.
3. **YENİ — `036`'nın onay mührü yüklemi değişti.** Artık dolu → BOŞ geçişi de reddediliyor.
   Yeniden mühürleme (dolu → dolu) BİLEREK açık; ekin AÇIK-1 ayak (d) hükmü bu davranışı
   anlatmıyor, hakem de bunu not etti. Task 8'e giderken ek metniyle karşılaştırılmalı.
4. **YENİ — kimlik kapıları artık dosyaların BAŞINDA.** Yeni bir migration yazılırken kapı,
   dosyanın ilk üst düzey DDL'inden ÖNCE konmalı; yapısal test bunu zorluyor ve kapısız dosya
   eklendiği an kırmızı düşüyor.
5. **Substrat kapsam kaybı** (değişmedi): Codex kum havuzu `api_key=<ifade>` desenli üretim
   dosyalarını dışlıyor. **Bu turda ek bir kayıp ölçüldü:** kapanış-doğrulama turunda hakem
   `CURRENT.md` ve `HANDOFF.md`'yi de göremedi (tur 1'de görebilmişti) ve yazılabilir geçici
   dizin olmadığı için hedefli pytest'i de başlatamadı. **Rapora dürüstçe yazıldı: hakem her
   şeyi görmedi.**

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar (sayılar taze)

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 1499**; bu sayı düşmeyecek. (1452 → 1493 → 1499, üçü de kontrolörün kendi koşumu.)
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ;
   `.py` ve `.json` GİRER.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, `Co-Authored-By` / `Claude-Session` **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter.**
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz** — orası kontrolörün.
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır ve mutasyona
    **boş-küme kontrol kolu** eklenir.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
13. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
14. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testlerin ayrıştırıcılarını bayatlatabilir.
15. **YENİ (bu oturumun dersi) — "hepsi birbirine eşit" bir kimlik iddiası DEĞİLDİR.** Bu
    oturumda iki kez yakalandı: credential kapısı önce yalnız iç tutarlılık ölçüyordu, sonra
    yalnız VAR OLAN atıfları inceliyordu. Kimlik kapısı ya kanonik değerle TAM eşleşmeli ya da
    kümeyi ÜRETEN yapıdan (düğüm · dosya) türemeli — mevcut örneklerden değil.
16. **YENİ — canlıya hiçbir n8n dosyası körlemesine yüklenmez.** Depo ile canlı İKİ YÖNDE birden
    sapıyor (ölçüldü). Yükleme öncesi düğüm bazında karşılaştır, farkların hepsinin kastedilen
    düzeltme olduğunu doğrula, yalnız `nodes`+`connections` gönder, sonra tek tek ölç.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07, hepsi kontrolörün KENDİ koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **1499 passed in 543.13s**, exit 0, temiz ağaçta, HEAD `2b468e8d`'de.
  Seyir: 1452 (giriş) → 1493 (borç kapanışı) → 1499 (checkpoint 5 düzeltmeleri). Hiç düşmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- `bash ~/.claude/tools/command-blocks-maint.sh verify` → **PASS**.
- **Codex çağrısı: 2** (checkpoint 5 tur 1 `base-review` + tur 2 kapanış-doğrulama, ikisi de
  `rc=0`). Ham çıktı
  `/root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.
- **H2 ampirik kanıtı:** geri alınan bir transaction'da temizle → hedefi değiştir → yeniden
  mühürle zinciri koşuldu; `target_version` 3 → 99 oldu ve satır yine mühürlü göründü. Kontrol
  kolu (doğrudan hedef değişimi) aynı koşumda REDDEDİLDİ. Düzeltmeden sonra zincir ilk adımda
  duruyor.
- **Mutasyon probları:** kimlik kapısı 4 dosyada (kapı sökülünce zarar düşüyor) · credential
  kapısı iki yönde (blok silme · kimlik değiştirme) · webhook köken kapısı (CRM-3 reminder).
- **Canlı n8n ölçümleri:** yükleme sonrası yedi workflow'da çıplak token 0 · credential bağlı ·
  yedisi aktif. CRM-4/CRM-5 günlük turları 3·4·5·6 Eylül'de `success`. Pasifleştirme sonrası
  CRM-1/2/3 `active=False` ve `POST /webhook/crm/*` → **404**.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** — hiçbir koşum Telegram
  düğümüne ulaşmadı (CRM'de gerçek müşteri verisi yok). "Bildirimler artık gidiyor" İDDİA
  EDİLMİYOR; yalnız "ölü token artık hiçbir workflow'da yok".
- **CRM-3'ün webhook yolu düzeltmesi çalıştırılarak doğrulanmadı** — topolojiden türetildi;
  workflow hiç koşmamış ve şu an pasif.
- **F5 düzeltmesi `approve`'dan SONRA yapıldı** — hakem onu görmedi. Yalnız bir testi
  güçlendiriyor, üretim davranışına dokunmuyor.
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı. Pasifleştirme bir shutdown'dır.
- PG 18.3 dışında sürüm denenmedi; gerçek çok-oturumlu eşzamanlılık denenmedi.
- Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı.
- **Dal push EDİLMEDİ.**
- Task 7–20 hiç yazılmadı.

# Risks

- **YENİ, EN YÜKSEK — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
  CRM yeniden aktive edilmeden önce header auth + parametreli sorgu + backend başlığı ZORUNLU;
  aktive etmek ucu geri açar. CURRENT.md'de tetikli madde.
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.** Hakem bunu
  medium olarak gösterdi; gerekçesiyle REDDEDİLDİ: yürütme protokolünün kendi defter grameri
  `red-only`/`green-only` türlerini tanımlar, defter kapısı rc=0 ve önerilen çözüm (geçmişi
  squash) denetim izini silerdi.
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ.** Onaylı koşum yolu her dosyayı
  `--single-transaction` ile sardığı için bugün zararsız; kimlik kapıları dosya başına taşınınca
  maruziyet daraldı ama sınıf kapanmadı.
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (ölçüldü, kapatılamaz).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **Codex maliyeti:** bu oturumda 2 çağrı. Final için ≥3 tur rezerve kuralı yerinde.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Bu oturumun en önemli dersi: "kapattım" demeden önce kapatmanın KENDİSİNİ ölç.** Üç kez
  kendi işimin eksiğini kendi ölçümüm ya da hakem yakaladı — CRM-1/CRM-2'yi gereksiz yere
  değiştirmiştim (geri alındı), reminder'ın üçüncü atfını atlamıştım, credential kapısı iki
  ayrı biçimde fail-open'dı. Üçü de "yaptım" dedikten SONRA çıktı.
- **Hakem raporunu doğrulanmamış iddia say.** Bu turda altı bulgunun altısı da kontrolör
  tarafından yeniden ölçüldü; biri (H1) ölçüm sonucu ÖNCEDEN VAR olan bir yüzey çıktı ve
  ciddiyeti hakemin gösterdiğinden farklı yerde durdu (partinin ürünü değil ama canlıda
  gerçekti); biri (M3) reddedildi.
- **Ölçüm probunun kendisini de sorgula.** H2 probu ilk koşumda `ON_ERROR_STOP` yüzünden kontrol
  kolunda duruyordu ve "zincir kapalı" gibi görünüyordu; prob düzeltilince gerçek çıktı.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
