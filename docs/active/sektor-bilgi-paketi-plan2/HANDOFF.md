---
task: sektor-bilgi-paketi-plan2
written: 2026-08-30
---

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-08-30) — bu anlatı **Task 3'ün ortasına** aittir; güncel
> durum TASK.md + yürütme defteri + git defterinden okunur, çelişkide onlar esastır.

# Resume From

**İlk iş: Task 3 düzeltme turu 2'nin kapsamlı yeniden incelemesi. KOŞMADI.**
Task 4'e geçmeden önce bu kapatılır. Kod indi (`a34d3f6`), testler yeşil, ama düzeltmenin
kendisi hiçbir hakem görmedi — ve bu oturumda tam olarak bu sınıf bir kez daha kendini
gösterdi: düzeltme turu 1'in yeniden incelemesi, düzeltmenin *kendi* içinde yeni bir Important
buldu. Yani "düzeltme küçüktü, incelemeyi atlayalım" burada ölçülmüş biçimde yanlış.

Yeniden inceleme kapsamı: `411c767..a34d3f6`. Doğrulanacak iki kalem:
1. **F4** — yanlış K-56 gerekçesi hem `sector_package_lifecycle.py` belgesinden hem
   `task-3-report.md`'nin iki F1 bölümünden silindi mi, ve yerine yazılan maliyet ölçüme
   uyuyor mu. Uygulayıcı, ne kontrolörün ne hakemin saydığı bir kalem daha bulduğunu
   bildiriyor: migration 033'ün kendi doğrulama bloğu kısıtın tanımını **birebir** bekliyor,
   dolayısıyla genişletme o beklentiyi de günceller. Uygulayıcı bunun bir yarısını
   "okudum, ölçmedim" diye dürüstçe etiketlemiş — **o etiket doğrulanmalı, kabul edilmemeli.**
2. **Minor** — uyarı günlükleme sırası geri alındı mı ve neden öyle olduğu yazıldı mı.
   Uygulayıcı bu değişiklik için gerçek bir kırmızı üretilemeyeceğini söylüyor (uyarı yolunu
   sabitleyen test yok) ve sahte kanıt üretmeyi reddetmiş — doğru davranış, ama demek ki o yol
   test edilmiyor.

Sonra **Task 4** (sözleşme v2 — denetçi yeniden-doğrulama envanteri + sentez kimlik taşıması).

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** seçilir.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Her görevin commit aralığı, her hakem bulgusu, her kontrolör kararı ve gerekçesi orada.
Sonundaki **SHA eşlem tablosu** önemlidir: defterin eski kayıtları eski commit numaralarını
anıyor, çünkü onları silmek o commit'lerin var olduğu gerçeğini silerdi.
Bağlam kaybolursa **defter + `git log`** esastır, anlatı değil.

**Yürütme durumu (TASK.md "Execution State"):** kip alt-ajanlı · başlangıç çapası `a806e29` ·
defter penceresi `a806e29` · `cp_count: 1` · `last_checkpoint_ref: 72f5744`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, origin'in 17 commit önünde. **Push EDİLMEDİ** —
uzak dal hâlâ `a806e29`'da. **Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`:
`master`, HEAD `d901eb4`, temiz, uzak deposu yok.

**Yedek etiket `backup/pre-footer-fix-20260830`** commit etiketi yeniden yazımının geri dönüş
yoludur. Silinme koşulu TASK.md'de yazılı.

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar** (hepsi bu oturumda işe yaradı):
1. Arayüz eki **bağlayıcıdır**. Uygulayıcı brief'e, ekin ilgili hükümleri **harfiyen
   kopyalanmış** olarak gider — plan metni tek başına yetmez, "eki oku" demek de yetmez.
2. Test komutu **sanal ortam aktifleştirilerek** koşar (aşağıda Verification).
3. **Taban 744**; bu sayı düşmeyecek.
4. **`Exec-Kind` sınıflandırıcıya karşı seçilir, uzantıya karşı DEĞİL.** Bu oturumda bir
   history rewrite'a mal oldu. Beyaz liste altı değerlidir: `code` (hem test hem impl) ·
   `red-only` (yalnız test) · `green-only` (yalnız impl) · `docs-only` (hiç çalıştırılabilir
   yol yok) · `migration` (kapısız) · `merge`. **`shared/contracts/*.json` çalıştırılabilir
   sayılır** — davranış belirleyen veri. Yazmadan önce commit'in gerçek path kümesine bak.
5. Test önce yazılır, **kırmızı düştüğü gözle görülür**, kırmızı çıktı rapora yazılır.
6. Uygulayıcı **kendi alt-ajanını çağırmaz**; review kontrolörden gelir.
7. **Codex çağrılarına tam 40 karakterlik SHA verilir.** Kısa SHA substrat kurulumunda
   `rc=2` üretir — Codex hiç çağrılmaz, tur boşa gider (bu oturumda bir kez oldu).

**Devir pointer'ları — hangi görev neyi devralıyor:** TASK.md'nin "Task 3'ün doğurduğu evler"
bölümü. Task 6 · Task 9 · Task 11 · Task 12 · Task 13 · Task 15 · Task 18 dispatch'lerinde
ilgili maddeler taşınır. Task 4 ayrıca Task 2'den üç sözleşme kalemi devralır.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-08-30, kontrolörün kendi koşumları — hiçbiri
uygulayıcının sözüne dayanmıyor):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **744 passed in 106.65s** (yeniden yazım sonrası tekrar koşuldu).
  Oturum içi seyir: 667 → 672 (Task 2) → 692 (checkpoint düzeltmesi) → 737 (Task 3) → 744.
- `ec_ledger_view <çapa> <kök> - --post-window` → **rc=0**, her satır temiz.
  (Düzeltmeden önce rc=2, iki MECH-FAIL.)
- `git diff backup/pre-footer-fix-20260830 HEAD` → **0 satır**; iki aralıkta da 6 commit.
  Yeniden yazımın içeriği değiştirmediğinin kanıtı.
- Pin manifesti bayt bayt: `commit` = dış depo HEAD `d901eb4`, üç sha256 = diskteki dosyalar.
  Canlı `verify_pin` → boş liste.
- Checkpoint high bulgusunun üç senaryosu düzeltme öncesi/sonrası koşuldu: öncesinde üçü de
  geçiyordu, sonrasında üçü de gerekçeli hata veriyor.
- `git branch -r --contains 77dd268` → boş; `origin/feat/...` = `a806e29`. Yeniden yazılan
  geçmiş hiçbir uzak dalda yoktu.
- Codex: checkpoint 1 `needs-attention` (1 high + 2 medium) → düzeltme → kapanış turu
  `approve` (1 medium kabul edilmiş risk).

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Task 3 düzeltme turu 2'nin yeniden incelemesi KOŞMADI.** Bu oturumun tek açık döngüsü.
- **Task 4–20 hiç yazılmadı.**
- **Sözleşme metinlerinin ÇALIŞMA ZAMANI tüketimi hiç ölçülmedi.** Sweep'in "var" yargıları
  metin varlığını ölçer, davranışı değil; ilk kuru koşumda (Task 11/19) görülür.
- Uyarı günlükleme yolu hiçbir testle sabitlenmemiş (yukarıda).
- `git` ikilisi olmayan ortamda ve git ortam değişkenleri ezildiğinde pin davranışı
  ölçülmedi — evi Task 18 Step 8b.
- Migration 033'ün doğrulama bloğunun **üst-küme** durumunda ne yapacağı ölçülmedi; uygulayıcı
  "okudum, ölçmedim" diye etiketledi.
- Canlıya hiçbir şey dağıtılmadı, hiçbir migration uygulanmadı, pilot koşulmadı.

# Risks

- **Bu oturumun en pahalı dersi: etiket uzantıya göre seçilmez.** İki yanlış `Exec-Kind` final
  kapısını bloklayan iki MECH-FAIL üretti; birini kontrolör kendisi onaylamıştı. Ödemesi altı
  commit'lik bir yeniden yazım oldu — **on yedi görev sonra fark edilseydi ödenemezdi.**
  Defter kapısı artık her checkpoint'te koşulmalı, sadece finalde değil.
- **Kontrolör de ölçmeden kabul edebiliyor.** Uygulayıcının "K-56 bildirim bağı var" iddiasını
  ölçmeden kendi kararına yazdı; yeniden inceleme yakaladı, ölçüldü, yanlıştı. Aynı oturumda
  üç alt-ajana "ölçmeden kabul etme" diye dayatılmıştı. **İddia bir düzeltme raporundan
  geliyorsa da ölçülür.** Ayrıca hakemin düzeltmesi de yarı yanlıştı — iki tarafı da ölçmek
  gerekti.
- **KABUL EDİLMİŞ RİSK (checkpoint 1):** `test_external_repo_gitignores_run_folder` git ortam
  değişkenleriyle sahte bir depoya yönlendirilebilir. Üretim pin yolu etkilenmiyor; saldırı
  tam pinlenen commit'te bir sahte depo + zehirli ortam ister. Evi Task 18 Step 8b.
- **KABUL EDİLMİŞ RİSK (uygulayıcının bildirdiği kalıntı):** dış deponun içinde dışarıyı
  gösteren sembolik bağ ele alınmıyor; kapatmak ekin R14 hükmünün yasakladığı beşinci kapıyı
  gerektirir. Modül belgesinde dürüst etiketiyle duruyor. **"Ele alındı" DEĞİL.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`). Arayüz eki 8 çelişki
  + 12 boşluğu kapattı ama **Plan 1 alanındaki kart geçişi hâlâ taranmadı** — Plan 1 yüzeyinde
  kusur çıkarsa ilk bakılacak yer.
- **"Bildirilen örneği değil sınıfı kapat" bu oturumda İKİ kez kendini ödedi.** Task 2'de atıf
  sweep'inin ikinci tablosunda 25 atıfın 25'i yanlıştı, hakem yalnız 5'ini bildirmişti.
- **Küçük düzeltmenin kendi kusuru olabiliyor.** Task 3'ün düzeltme turu 1, kapattığı bulgunun
  *kendi sınıfından* yeni bir Important açtı. Düzeltme sonrası yeniden inceleme atlanamaz.
- **Codex maliyeti:** bu oturumda 3 çağrı (checkpoint · substrat hatasıyla hiç kurulamayan ·
  kapanış turu). Uzun turlar **arka planda** koşulur — ön planda kabuk 10 dakikada keser.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı
  ([[feedback_claude_runs_reviewer_rounds]]). Maliyet tek satır bilgilendirmedir.
- **Kontrolör düzeltme YAPMAZ.** Tek istisna `docs/active/` — orası kontrolörün kendi yüzeyi.
- **Minor bulgular döngüye girmez** — ama bu oturumda beş Minor bilinçle turun içine alındı
  ve her seferinde gerekçe deftere yazıldı: aynı dosyaya dokunuyorlardı ve pin zaten yeniden
  hesaplanıyordu, yani kapatmak bir tur yerine sıfır tur maliyetindeydi.
- **Spec değil, spec-input kanoniktir.** Bu oturumda yine fark yarattı: uygulayıcı `EK-K`'yı
  üç dosyalık dar bir aramaya dayanarak "kanonda yok" ilan etti, yanıldı, kendi düzeltti
  ([[feedback_dont_declare_absence_from_one_check]]).
- **Uygulayıcı raporunu doğrulanmamış iddia say** — ama iyi uygulayıcı kendi kusurunu da
  bildirir: bu oturumda biri testlerinin boş taslağa karşı *hiçbir şey kanıtlamadan* geçtiğini
  fark edip implementasyondan önce sertleştirdi, biri kapatamadığı kalıntıyı dürüst etiketle
  belgeye yazdı, biri kontrolörün yanlış test tahminine testi uydurmayı reddetti. Üçü de doğru
  davranış — raporu şüpheyle okumak, uygulayıcıyı düşman saymak demek değil.
- Diskte bekleyen düzeltme YOK; her iki çalışma ağacı da temiz.
