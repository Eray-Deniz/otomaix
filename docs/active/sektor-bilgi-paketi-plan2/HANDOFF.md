---
task: sektor-bilgi-paketi-plan2
written: 2026-09-06
---

# Resume From

**Checkpoint 4 koştu ve kapandı. Sıradaki iş Task 7 — `brief-doctor` mekanik girdi kapısı**
(plan satır 938).

Task 6 bitti, checkpoint kapısı ödendi ve karşılığını verdi: iki Codex turu **üç gerçek kusur**
buldu, ikisi high, biri daha önce kapatılmış bir sınıfın açık kalmış varyantı. Ayrıntı TASK.md
"Current Status"ta; burada tekrarlanmaz.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** → Adım 7 (Task 7 dispatch).

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
**Bu dosya git'e girmiyor** — kaybolursa git defteri ve commit mesajları esastır.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 2`** · **`last_checkpoint_ref: a6e053f`**.

> **İkisi de ÜÇÜNCÜ kez BİLEREK ilerletilmedi.** Checkpoint 4 koştu ama `approve` almadan
> kapandı (Eray kararı: oturum süresi), yani §8.6 mutasyon protokolüne yine girilmedi. Sonuç
> fail-safe: sıradaki checkpoint'in tabanı `a6e053f` kalır ve **Task 5'in tur 5/6'sını, Task 6'nın
> tamamını VE checkpoint 4'ün yedi düzeltme commit'ini** kendiliğinden kapsar. "Unutulmuş" sanıp
> elle ilerletme.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son kod commit'i **`5d42db5`**; HEAD bu devir
commit'inin kendisidir (`docs-only`). **Push EDİLMEDİ.**
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: `master`, HEAD
`6d5d90db9537b516413d31f091b4d475526bcb73`, temiz. Bu oturum ona dokunmadı.
**Yedek etiket `backup/pre-footer-fix-20260830`** duruyor; silinme koşulu TASK.md'de.

## Sıradaki checkpoint dispatch'inde ÖNDEN bildirilecekler

1. **F7 düzeltmesi (`9a65c0e`·`4b1e354`·`5d42db5`) hakem görmedi** — kapsam bu tabanda zaten var,
   ama hakem bunu bilerek baksın.
2. **Kapatılan sınıfın kalan beş dosyası** — DDL nesne kimliği (`001`·`023`·`026`·`032`·
   `rollback/032_down`). Bilinçli kapsam dışı; CURRENT.md'de tetikli madde.
3. **Ek metni kodla uyumsuz, İKİ yerde:** R12(a2)(d) amende edildi (TASK.md Decisions Log) ve
   aktör kapısının tanım yeri ekin gösterdiği modül değil (aynı yerde, ölçülmüş döngü gerekçesi).
4. **Ekin kendi içinde çelişkisi** — ayak (d) düzyazısı `BEFORE UPDATE OR DELETE` diyor, bağlayıcı
   SQL bloğu `BEFORE UPDATE`. Onaylı plan satırı SİLİNEBİLİR; evi Task 8.
5. **Substrat kapsam kaybı** — Codex kum havuzu `api_key=<ifade>` desenli üretim dosyalarını sır
   sanıp dışlıyor (bilinen yanlış pozitif). Bu turda hakem AYRICA ek/HANDOFF/CURRENT dosyalarını
   da göremediğini yazdı ve `.venv` olmadığı için testleri koşamadı. **Rapora dürüstçe yazılmalı:
   hakem her şeyi görmedi.**

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar (sayılar taze)

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 1452**; bu sayı düşmeyecek. (1181 → 1436 → 1452, üçü de kontrolörün kendi koşumu.)
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ —
   SQL-only commit `migration` alır; `.py` ve `.json` GİRER.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, `Co-Authored-By` / `Claude-Session` **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter.**
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz** — orası kontrolörün.
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır ve mutasyona
    **boş-küme kontrol kolu** eklenir. *Bu oturumda karşılığını verdi:* F7 düzeltmesi F1 ve F3'ün
    ayrıştırıcılarını bayatlattı ve iddiaları hâlâ doğruyken **kontrol kolları ateşledi**.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
13. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
    Sıraya koy — arıza biçimi çökme değil, inandırıcı bir kırmızıdır.
14. **YENİ (bu oturumun dersi):** bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testlerin
    ayrıştırıcılarını bayatlatabilir. Yapı taşındıysa okuyucuyu da kavramdan yeniden türet;
    "testler yeşil" yetmez, kontrol kolunun hâlâ ateşlediğini ölç.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-06, hepsi kontrolörün KENDİ koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **1452 passed in 453.65s**, exit 0, temiz ağaçta, izole (başka pytest oturumu yokken),
  HEAD `5d42db5`'te. Seyir: 1181 (giriş) → 1436 (düzeltme turu 1) → 1452 (düzeltme turu 2).
  Hiç düşmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, iki kez (her düzeltme
  turundan sonra), sıfır kırmızı satır.
- `ec_should_checkpoint 1 2 9` → **RUN_RISK** (taze; `ec_ceiling 20` → 9, `cp_count` → 2).
- `ec_classify_diff` taban `a6e053f`'ten HEAD'e: Task 6'nın altı commit'i RISKY.
- `bash ~/.claude/tools/command-blocks-maint.sh verify` → **PASS**.
- **Codex çağrısı: 2** (checkpoint tur 1 + tur 2 kapanış-doğrulama, ikisi de `base-review`,
  `rc=0`). Ham çıktı `/root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.
- **Kontrolörün kendi doğrulama probları** (hakemin sözüne dayanılmadı): ek satır 2658-2675 ↔
  036 manifest `<yok>` (F1) · `bool(actor)` kapısı + `package_events.actor` kolonunda CHECK/NOT
  NULL yokluğu + kapının tabanda da var olduğu (F2) · kilit sırası ↔ tetikleyici yazım yönü (F3) ·
  aynı dosyadaki üç "beş alan" cümlesinin hangisinin şimdiki zaman olduğu (F4) · kısıtlar için
  KAPI 2/KAPI 3'ün varlığı ↔ fonksiyon/tetikleyici için yokluğu (F7) · KAPI 4'ün kalıcı DDL'den
  ÖNCE olduğu (satır 277 < 348) ve down aynasının ilk `DROP`tan önce olduğu (245 < 313).

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **F7 düzeltmesi bağımsız hakem görmedi** (üçüncü tur Eray kararıyla açılmadı).
- **Uygulayıcının kendi ölçemedikleri** (dört kalem, TASK.md Open Problems'da tek tek yazılı):
  temiz-şemaya-yabancı-nesne hücresi · geri alma dosyasındaki özet-tabanlı fonksiyon kimliği ·
  farklı imzalı aşırı yükleme · başka tablodaki aynı adlı yabancı tetikleyici.
- **DDL nesne kimliği sınıfı beş dosyada AÇIK** (bilinçli kapsam kararı).
- PG 18.3 dışında sürüm denenmedi; **gerçek çok-oturumlu eşzamanlılık denenmedi** — F3'ün
  kapanışı YAPISALdır, canlı deadlock ölçümü değildir.
- Canlıya hiçbir şey dağıtılmadı; **035 ve 036 yalnız tek kullanımlık test veritabanlarına**
  uygulandı, pilot koşulmadı.
- **Düzeltilmiş iki n8n workflow'u canlıya import EDİLMEDİ** — CRM + takvim bildirimleri şu an
  sessiz (operatör işlemi, CURRENT.md'de yazılı).
- **Dal push EDİLMEDİ.**
- Task 7–20 hiç yazılmadı.

# Risks

- **KABUL EDİLMİŞ RİSK — checkpoint 4 `approve` almadan kapandı.** "Ele alındı" DEĞİL; kapısı
  adlandırıldı (sıradaki checkpoint tabanı kapsıyor).
- **EVSİZ DEĞİL AMA TARİHSİZ — yapısal bulgunun B yarısı** (düzyazı sayı yüzeyi + politika
  kararı). Evi dal-sonu triage listesi; o ev bir KARAR noktası, düzeltme değil.
- **EVSİZ PARK (Task 5'ten devralındı) — atomiklik sınıfı depo GENELİ.** Onaylı koşum yolu her
  dosyayı `--single-transaction` ile sardığı için bugün zararsız.
- **YENİ, TETİKLİ — DDL nesne kimliği sınıfı beş dosyada açık** (CURRENT.md'de madde).
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (ölçüldü, kapatılamaz).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **Codex maliyeti:** bu oturumda 2 çağrı. Final için ≥3 tur rezerve kuralı yerinde.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Bu oturum verimliydi ve bunu kayda geçir:** iki Codex turu, dört + bir bulgu, hepsi gerçek;
  ikisi denetim izini yalanlanabilir kılan sınıftaydı (onaylı planın değiştirilebilmesi, kimliksiz
  onay kaydı) ve biri projenin KENDİ standardının açık kalmış varyantıydı.
- **Uygulayıcı iyiydi:** kendi düzeltmesinin iki testi bayatlattığını KENDİ buldu, sebebini
  ayrıştırıcıya kadar izledi ve kavramdan yeniden türetti; kirlenmiş bir ölçümü kendi bildirdi
  ("iki pytest oturumu aynı tek kullanımlık veritabanlarını paylaşıyordu"); ölçemediği dört kalemi
  "doğrulanmadı" diye AYRI başlık altında listeledi.
- **Kontrolör düzeltme YAPMAZ.** Bu oturumda istisna kullanılmadı.
- **Uygulayıcı raporunu doğrulanmamış iddia say — hakem raporunu da.** Bu oturumda BEŞ bulgunun
  beşi de kontrolör tarafından yeniden ölçüldü; biri (F4) hakemin gösterdiğinden DAR çıktı.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor; alanı
  boş bırakmak opus-5 tabanını miras alır.
- **Spec değil, spec-input kanoniktir.**
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
