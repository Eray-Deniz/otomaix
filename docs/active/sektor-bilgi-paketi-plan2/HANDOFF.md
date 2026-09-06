---
task: sektor-bilgi-paketi-plan2
written: 2026-09-06
---

# Resume From

**Task 5 KAPANDI. Sıradaki iş Task 6.**

Task 6 = migration 036 (koşu kaydı · politika raporu · onay anlık görüntüsü · atama geçmişi)
ve `033_down.sql` / `034_down.sql` geri alma dosyaları. Devralınan iki yükümlülüğü var,
ikisi de TASK.md'de yazılı: (a) **F1 eşli yükümlülük** — `draft_created` olay türünü açar,
çağrıyı Task 15 ekler, yarım iniş görünür olsun diye eşli yazıldı; (b) **`033_down.sql` YOK**
(ölçüldü: `rollback/` yalnız `032_down.sql` ve `035_down.sql` taşıyor).

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
**Bu dosya git'e girmiyor** — kaybolursa git defteri ve commit mesajları esastır.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 2`** · **`last_checkpoint_ref: a6e053f`**.

> **İkisi de BİLEREK ilerletilmedi.** Checkpoint 3 koştu (iki Codex turu) ama `approve`
> almadan kapatıldı, yani §8.6 mutasyon protokolünün Clean/Accepted-risk dalına hiç
> girilmedi. Sonuç fail-safe: sonraki checkpoint'in tabanı `a6e053f` kalır ve **hakem
> görmemiş tur 5/6 commit'lerini kendiliğinden kapsar.** Bunu "unutulmuş" sanıp elle
> ilerletme.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, HEAD **`412a895`**. **Push EDİLMEDİ.**
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: `master`, HEAD
`6d5d90db9537b516413d31f091b4d475526bcb73`, temiz. Bu oturum ona dokunmadı.

**Yedek etiket `backup/pre-footer-fix-20260830`** duruyor; silinme koşulu TASK.md'de.

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar** (sayılar taze):
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 963**; bu sayı düşmeyecek. (921 → 936 → 939 → 943 → 947 → 950 → 961 → 963.)
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ —
   SQL-only commit `migration` alır.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, `Co-Authored-By` / `Claude-Session` **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter.**
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz.
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris de **mutasyonla** sınanır.
11. **YENİ (bu oturumun dersi):** kapanışı *sayarak* değil *yapıyla* kur. Tur 5'te üç kusur
    kapatıldı ama ikisi eksik süpürüldü ve tur 6'da geri geldi; tur 6 aynı şeyleri yüklemi
    katalogdan türeterek ve kalıcı işi tek deyime alarak kapattı — o hücreler artık DOĞAMIYOR.

**Devir pointer'ları — Task 5'in doğurduğu evler:**
- **Task 6:** `035_down.sql`'in `\set ON_ERROR_STOP on` ayarını çağıran psql oturumuna
  sızdırması (`032_down.sql`'den devralındı). Task 6 sıradaki geri alma dosyalarını yazan
  görev — konvansiyon orada benimsenir ya da kapsanır.
- **Task 18:** (a) `get_holidays` yıl başına 24 saat önbellekliyor, yazımda geçersizleştirme
  yok → dağıtım sonrası önyüz bir güne kadar `end_date`siz yanıt alabilir. (b) Step 9 runbook'u
  geri alma sırasını yazarken **operatör adımını** içermek zorunda (TASK.md Open Problems).
- Önceki oturumdan devam: Task 9 · 11 · 12 · 13 · 15 · 18 pointer'ları TASK.md "Task 3'ün
  doğurduğu evler" bölümünde.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-06, hepsi kontrolörün KENDİ koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **963 passed in 272.97s** (final commit'li, temiz ağaçta). Seyir: 950 (giriş) → 961
  (tur 5) → 963 (tur 6). Hiç düşmedi.
- `ec_should_checkpoint 1 2 9` → **`RUN_RISK`** (taze; 15 commit'in 11'i RISKY/UNKNOWN).
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, altı yeni commit'in
  hepsinden sonra.
- **Codex çağrısı: 2** (checkpoint 3 tur 1 + tur 2), ikisi de `rc=0`, ham çıktı
  `/root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.
- **Kontrolörün kendi probları** (hepsi POZİTİF KONTROL kollu; kontrol yeşil olmadan yargı
  verilmedi), `/tmp/.../scratchpad/` altında: `probe_h2_constraint.py` · `probe_h1_h3.py` ·
  `probe_r2.py`. Beş bulgunun **beşi de** önce kusurlu, fix'ten sonra kapalı ölçüldü.
- **FDW ölçümü:** `pg_available_extensions` → `file_fdw`, `postgres_fdw` **kurulabilir**;
  `pg_foreign_server` → 0; PG 18.3. Eski "bu kurulumda yaratılamıyor" iddiası bununla çürüdü.
- **Otomatik geri alma taraması:** depo genelinde `035_down`/`rollback/` çağıran betik,
  uygulama yolu veya n8n işi **YOK** (ölçüldü) — geri alma yalnız elle koşulur.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Tur 6 (son düzeltme) bağımsız hakem GÖRMEDİ.** Üçüncü tur Eray kararıyla açılmadı.
  Kapsanma yolu adlandırılmış (final inceleme tabanı `a806e29`), ama bugün alınmış bir
  `approve` YOK.
- **Checkpoint 3'ün son verdict'i `needs-attention`** (tur 2). Sonraki tur koşulmadığı için
  bu verdict yürürlükte kaldı.
- PG 18.3 dışında sürüm denenmedi; **gerçek çok-oturumlu eşzamanlılık denenmedi** (kilit
  davranışı yalnız koddan okundu, süre ölçülmedi).
- Canlıya hiçbir şey dağıtılmadı, **035 hiçbir gerçek ortama uygulanmadı**, pilot koşulmadı.
- **Dal push EDİLMEDİ.**
- Task 6–20 hiç yazılmadı.

# Risks

- **KABUL EDİLMİŞ RİSK — tur 6 hakem görmedi** (yukarıda). "Ele alındı" DEĞİL.
- **EVSİZ PARK (İlke 7, uydurma ev VERİLMEDİ) — atomiklik sınıfı depo GENELİ.** 035 artık
  her çağrı biçiminde atomik, ama bu **tek başına atomik olan tek migration dosyası**.
  Diğerlerinin hepsi çok deyimli (ölçüldü: 032'de 24 üst düzey DDL) ve çıplak elle
  `psql -f` altında yarım kalabilir. **Bugün zararsız çünkü onaylı koşum yolu
  (`run-migrations.sh`) her dosyayı `--single-transaction` ile sarıyor** — ölçüldü, satır 206.
  Kapatmak runner/politika işidir, tek dosyanın işi değil; Task 5'e sıkıştırmak yanlış olurdu.
  **Yeniden açılma koşulu:** onaylı koşum yolu sarmalayıcısız hâle gelirse VEYA elle uygulama
  bir olayda kök sebep çıkarsa. **Dürüst etiket: çözülmedi + park edildi, EVİ YOK.**
- **KABUL EDİLMİŞ RİSK — sabit seed id'lerinin yan etkisi.** Bir seed satırının tarihi elle
  kaydırılırsa ikinci koşumda birincil anahtar çakışır. Ölçüldü: **fail-closed** (`rc=3`,
  hiçbir şey uygulanmadı). Ayrıca "manifestte olup tabloda olmayan alan" yolu da ölçüldü ve
  fail-closed (`rc=3`). İkisi de SQL'in kendi yorumunda yazılı.
- **KABUL EDİLMİŞ RİSK — kilit süresi.** Çıplak `psql` altında ACCESS EXCLUSIVE kilidi artık
  blok sonuna kadar tutuluyor (eskiden `ALTER` sonrası bırakılıyordu). Yapısal sonuç koddan
  okundu; **süre olarak ÖLÇÜLMEDİ.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`); Plan 1 alanındaki
  kart geçişi hâlâ taranmadı.
- **Codex maliyeti:** bu oturumda 2 çağrı. Final için ≥3 tur rezerve kuralı yerinde.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **SÜREÇ AĞIRLIĞI ≈ RİSK AĞIRLIĞI — bu oturumun en pahalı dersi.** Otonom fix döngüsü
  kuralca onay istemiyor, ben de tur 1 → fix → tur 2 → fix diye zincirledim ve Eray haklı
  olarak "saatlerdir bitiremedin" dedi. **Turlar gerçek kusur buldu** (beşi de ölçüldü, ikisi
  sessiz veri kaybıydı) — yani zincir boş değildi. Hata **maliyeti görünür kılmamaktı**:
  ilk tur bittiğinde "bu uzayacak, devam edeyim mi" diye SORMALIYDIM. Tek başına ilk düzeltme
  turu 69 dakika sürdü. **Bundan sonra: çok turlu zincire girmeden önce maliyeti tek satırla
  bildir, sonra devam et.**
- **Kontrolör düzeltme YAPMAZ.** Bu oturumda istisna kullanılmadı.
- **Kendi ürettiğin gerilemeyi park etme.** Bu oturumda iki medium (`F4` ölçülmemiş "ölçüldü"
  iddiaları · `F5` mutasyon altında yeşil kalan kapanış testleri) politika gereği advisory'ydi
  ama **bu yürütmenin kendi ürünüydü**, o yüzden döngüye alındı ve kapatıldı.
- **Uygulayıcı raporunu doğrulanmamış iddia say** — ama iki uygulayıcı da iyiydi: kontrolörün
  toplam **beş** önerisini ölçümle reddettiler ve her seferinde haklı çıktılar; biri kendi
  ölçüm aracının yalan söylediğini fark edip düzeltti (mutasyon "yeşil" görünüyordu çünkü
  sınıflandırıcı pytest `error`ünü `failed` saymıyordu).
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
