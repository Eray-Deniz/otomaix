---
task: brief-sozlesmesi-kaynak-bolumu-makine-okunur
written: 2026-09-07
---

# Resume From

**Bu görev henüz BAŞLAMADI** (`status: proposed`). Hiçbir dosyaya dokunulmadı.

**Başlama yuvası: Plan 2'nin Task 8'i bittikten SONRA, Task 9'a girmeden ÖNCE.** Gerekçe ve iki
son tarih TASK.md'de.

**Giriş kapısı tasarımdır, yürütme değil.** İki ürün kararı (tablo tekrarı ↔ rapor uzunluğu;
katı biçim ↔ oturmayan bulgunun düşürülmemesi) karara bağlanmadan sözleşme metni yazılamaz —
ikisi de TASK.md Open Problems'ta. Bu yüzden doğal başlangıç `/spec-claude-codex` değil, **kısa
bir karar turu**: iki gerilim Eray'a somut senaryolarla sorulur, sonra metin yazılır.

**Neden dosya değil karar önce:** sözleşme dış depoda ve parmak iziyle kilitli. Metni yazıp sonra
karar değiştirmek yeniden kilitleme + doğrulama turu demek.

# Verification

**Bu görev için henüz hiçbir doğrulama koşulmadı.**

Görevi doğuran ölçümler (2026-09-07, Plan 2 checkpoint 6 oturumunda, kontrolörün kendi koşumları):
- Kapı serbest düzyazıyı geçiriyor: `- Düz yazı, devamı https://example.com/kaynak` → `gecti`,
  0 not. Üç hakem turunda sertleştirme yakınsamadı.
- Şu anki sözleşme biçiminde üretilmiş gerçek çıktı YOK: dış depodaki dosyalar 2026-07-11 tarihli,
  sözleşmenin yürürlükteki sürümü 2026-08-30; beşinde de kaynak bölümü eski biçimde.
- Sözleşme pini temiz: doğrulayıcı sıfır sapma verdi, yani değişikliğe temiz bir tabandan girilir.

**Bu görev kapanırken doğrulanması ZORUNLU olanlar:**
- Pin yenilendi ve fail-closed doğrulayıcı yeni sürüme bağlandı (mevcut pin testiyle).
- Girdi kapısının kaynak bölümü ailesi olumlu yapısal sözleşmeye çevrildi.
- **Task 7'de konulan "makineyle doğrulanmadı" kapsam beyanı KALDIRILDI** — kalırsa bayat beyan
  olur ve denetçiyi yanıltır.
- Denetçi görev metninin kaynak bölümüne atfı yeni biçimle hizalı.
- Girdi kapısının tam test kümesi düşmedi.

# Risks

- **SON TARİH KAÇIRILIRSA maliyet ikiye katlanır.** Task 19 Step 5 üç araştırmayı tek seferde
  yeniden üretir; sözleşme ondan sonra değişirse araştırmalar ikinci kez ürettirilmek zorunda.
- **Task 9/10'dan sonra yapılırsa denetçi koduna geri dönmek gerekir.**
- **Katı biçim yanlış-pozitif üretebilir.** Bugün girdi kapısında hiçbir kontrol eleme yapmıyor,
  yani maliyet gürültü — ama gürültü de denetçinin işini bozar. Kapsam sınırı beyan edilmeli.
- **Dış depo ve monorepo iki ayrı depodur;** sözleşme değişikliği ikisinde birden commit ister ve
  arada pin sapması penceresi doğar. Sıra: önce sözleşme, sonra pin, sonra kod.

# Notes For Claude/Codex

- **Sözleşme metnini yürütücü alt-ajan YAZMAZ.** İki ürün kararı önce Eray'a gider.
- **Spec değil, spec-input kanoniktir** — kaynak bölümünün kontrol tanımı orada (§7.3 tablosu).
- Bu görevin doğduğu yer: Plan 2 Task 7 / checkpoint 6, `[checkpoint-override turn 3]` etiketli
  Open Problems kalemi. Oradaki kalem bu görev kapanınca kapatılmalı — **iki yerde birden
  yaşamasın.**
