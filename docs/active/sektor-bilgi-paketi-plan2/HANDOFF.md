---
task: sektor-bilgi-paketi-plan2
written: 2026-09-07
---

# Resume From

**Sıradaki iş Task 8 — koşu ve artefakt servisi** (plan satır 981).

Bu oturum **Task 7'yi indirdi ve checkpoint 6'yı kapattı.** Ayrıntı TASK.md "Task 7 + checkpoint
6" başlığında; burada tekrarlanmaz.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** → Task 8 dispatch.

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
**Bu dosya git'e girmiyor** — kaybolursa git defteri ve commit mesajları esastır.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **Bu kez BİLEREK İLERLETİLMEDİ.** Checkpoint 6 üç tur sürdü ve hakem `approve` VERMEDİ; kapanış
> Eray'ın risk kabulüyle alınan bir **override**'dır. §8.6 mutasyon protokolü yalnız
> Clean/Accepted-risk dallarında koşar, bu koşum onlardan biri değil. Sonuç fail-safe: sonraki
> checkpoint'in tabanı `2b468e8d` KALIR ve Task 7'nin yedi commit'ini kendiliğinden kapsar.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit **`73451c9`** (bu devir commit'i onun
üstüne biner). **Push EDİLMEDİ.**
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: bu oturum ona DOKUNMADI (pin
doğrulandı, sıfır sapma).
**Yedek etiket `backup/pre-footer-fix-20260830`** duruyor; silinme koşulu TASK.md'de.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **Ek metni kodla uyumsuz, İKİ yerde** (değişmedi): R12(a2)(d) amende edildi ve aktör
   kapısının tanım yeri ekin gösterdiği modül değil.
2. **Ekin kendi içinde çelişkisi** (değişmedi): ayak (d) düzyazısı `BEFORE UPDATE OR DELETE`,
   bağlayıcı SQL bloğu `BEFORE UPDATE`. Evi Task 8 — **yani sıradaki görev.**
3. **Onay mührü yüklemi** (değişmedi): dolu → BOŞ geçişi reddediliyor, yeniden mühürleme
   (dolu → dolu) BİLEREK açık. Task 8'e giderken ek metniyle karşılaştırılmalı.
4. **Kimlik kapıları migration dosyalarının BAŞINDA** (değişmedi): yeni migration yazılırken
   kapı ilk üst düzey DDL'den ÖNCE konmalı; yapısal test bunu zorluyor.
5. **YENİ — Task 7 ve Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** (ölçüldü: 20
   görevin 18'inde var). Task 7'de sorun ÇIKARMADI çünkü ekin iki tüketici sözleşmesi (satır 656
   ve 689) yine de bağlıyordu ve dispatch'e harfiyen taşındı. **Task 11'e gelindiğinde aynı
   kontrol elle yapılmalı** — eksik satır, ekin o görevi bağlamadığı anlamına GELMEZ.
6. **YENİ — Task 8/9/12, girdi kapısının ürettiği tipleri tüketecek.** Bugün depoda o tiplere
   modül ve kendi testi dışında **hiçbir atıf yok** (kontrolör taradı). Task 8 ilk tüketiciyi
   ekleyecekse, TASK.md Open Problems'taki iki tetikli kalem (uydurma özet · başlık taklidi)
   yeniden değerlendirilmeli.
7. **Substrat kapsam kaybı** (değişmedi): Codex kum havuzu `api_key=<ifade>` desenli üretim
   dosyalarını dışlıyor; aktif katman dosyaları ve bağlayıcı ek de dışlanıyor. Hakem bu turda
   onları HEAD git nesnelerinden okuduğunu açıkça yazdı ve tam test kümesini kum havuzunda
   yeniden koşamadığını bildirdi — **kontrolörün 1793 sonucu bağımsız olarak doğrulanmadı.**

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar (sayılar taze)

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 1793**; bu sayı düşmeyecek. (1499 → 1552 → 1644 → 1758 → 1793, beşi de kontrolörün
   kendi koşumu.)
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
14. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testlerin ayrıştırıcılarını bayatlatabilir. Bu
    oturumda ölçüldü: bir testin yeşilliği tam da kapatılan fail-open'a dayanıyordu. **Her
    düzeltme turunda eski test dosyasını yeni modüle karşı koştur.**
15. "hepsi birbirine eşit" bir kimlik iddiası DEĞİLDİR. Kimlik kapısı ya kanonik değerle TAM
    eşleşmeli ya da kümeyi ÜRETEN yapıdan türemeli.
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez; düğüm bazında karşılaştır.
17. **YENİ — hakem/kontrolör önerisi ADAYDIR, cevap değil.** Bu görevde ölçümde yanlış çıkan
    öneri sayısı **beşe** ulaştı; ikisi bu oturumda. Uygulayıcı ölçüp reddetmekle yükümlü.
18. **YENİ — kendi probunu da sorgula.** Bu oturumda kontrolörün bir probu bulguyu ÜRETEMEDİ ve
    "kapanmış" gibi göründü; prob zayıftı, güçlendirilince bulgu birebir çıktı.
19. **YENİ — üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.** Sınıfı adlandır,
    üretilmiş matrisle kapat; kapanmıyorsa çerçeve teşhisiyle Eray'a git.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07, hepsi kontrolörün KENDİ koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **1793 passed in 546.52s**, exit 0, temiz ağaçta, HEAD `73451c9`'da.
  Seyir: 1499 (giriş) → 1552 (Task 7) → 1644 (düzeltme 1) → 1758 (düzeltme 2) → 1793
  (düzeltme 3). Hiç düşmedi, hiç test silinmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- `bash ~/.claude/tools/command-blocks-maint.sh verify` → **PASS** (oturum başında).
- `ec_classify_diff` (Task 7 commit'i) → **RISKY**; `ec_should_checkpoint 1 3 9` → **RUN_RISK**.
- **Sözleşme pini:** `verify_pin` → **sıfır sapma**; pinli sözleşme diskteki dosyayla bayt-aynı.
- **Codex çağrısı: 3** (checkpoint 6 tur 1 `base-review` + tur 2 ve 3 kapanış-doğrulama, üçü de
  `rc=0`). Ham çıktı + kapanış denetim kaydı
  `/root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.
- **Kontrolörün kendi bulgu doğrulaması:** checkpoint 6'nın beş bulgusunun ve her turdaki
  yeniden açılmanın HEPSİ kontrolörün kendi probuyla ölçüldü. Kapanış probları da aynen tekrar
  koşuldu (özetsiz rapor · gizlenme · takma ad · iç içe tekrar · beyan · sıra davranışı).
- **Yanlış-pozitif regresyon ölçümü:** dış depodaki beş gerçek araştırma çıktısında not sayıları
  öncesi/sonrası **birebir aynı** (25/25/24/20/29). Eski modül ayrı yüklenip karşılaştırıldı.
- **Çağıran taraması:** girdi kapısının tiplerine modül ve kendi testi dışında depoda **atıf yok**.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Bölüm C'nin üçlü yapısı makineyle DOĞRULANMIYOR** — ilan edildi, onarılmadı (Open Problems).
- **Sözleşmeye uyan bir araştırma çıktısında yanlış-pozitif oranı ÖLÇÜLMEDİ** — dış depodaki beş
  dosya sözleşmenin şimdiki biçiminden eski (2026-07-11 vs sözleşme 2026-08-30) ve beşinde de
  Bölüm B tablosuz. Gerekçe-tablosu başlık eşiğinin gerçek çıktıdaki kapsama oranı ölçülemedi.
- **Kontrolörün 1793 sonucu bağımsız hakem tarafından yeniden üretilmedi** — Codex kum havuzunda
  dışlanan üretim dosyaları toplama hatası veriyor; hakem bunu raporunda kendisi yazdı.
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- PG 18.3 dışında sürüm denenmedi; gerçek çok-oturumlu eşzamanlılık denenmedi.
- Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı.
- **Dal push EDİLMEDİ.**
- Task 8–20 hiç yazılmadı.

# Risks

- **YENİ — checkpoint 6 `approve` ALMADI.** Kapanış Eray'ın risk kabulüyle alınan bir
  **override**'dır (3 tur, son tur `needs-attention`). Kabul edilen üç kalem TASK.md Open
  Problems'ta `[checkpoint-override turn 3]` etiketiyle duruyor. `cp_count` bilerek
  ilerletilmedi; sonraki checkpoint Task 7'yi kendiliğinden yeniden kapsar.
- **YENİ, TARİHLİ — sözleşmenin kaynak bölümü makine-okunur değil.** Ev:
  `brief-sozlesmesi-kaynak-bolumu-makine-okunur` (CURRENT.md). **SON TARİH Task 19 Step 5** —
  o adımdan sonra yapılırsa üç araştırma ikinci kez üretilmek zorunda kalır.
- **EN YÜKSEK — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI** (değişmedi).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor** (değişmedi;
  hakem bu oturumda bu itirazı TEKRAR ETMEDİ).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **Codex maliyeti:** bu oturumda 3 çağrı. Final için ≥3 tur rezerve kuralı yerinde (checkpoint
  bütçesi 5, kullanılan 3).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Bu oturumun en önemli dersi: üç tur aynı ekseni getiriyorsa sorun kapıda değil, ÇERÇEVEDE.**
  İlk iki tur bulunan örnekleri yamaladı ve her seferinde yeni örnek çıktı. Üçüncü turda sınıf
  adlandırıldı ve üretilmiş matrisle kapatıldı; kapanamayan tek kalem dürüstçe ilan edilip kök
  çözüme (sözleşme revizyonu) tarihli bir ev verildi.
- **"Doğrulanmadı" demek çözmek değildir — devretmektir, ve devrin nereye gittiğini ÖLÇ.**
  Bu oturumda ölçüldü: denetçi sözleşmesi kaynak başına 3 iddia örnekleyip bağlantıyı gerçekten
  açıyor (makinenin yapamayacağı daha güçlü kontrol), ama bütünlük sorusunu cevaplamıyor.
  Kaybedilen kısım açıkça yazıldı, "çözüldü" DENMEDİ.
- **Hakem raporunu doğrulanmamış iddia say.** Bu turda beş bulgunun beşi de yeniden ölçüldü.
- **Kendi probunu da sorgula** — bir kez zayıf prob "kapanmış" izlenimi verdi.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma** — bu oturumda İlke-8 kapısı bir soruyu reddetti ve haklıydı.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
