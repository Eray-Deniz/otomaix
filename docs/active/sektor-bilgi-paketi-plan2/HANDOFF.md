---
task: sektor-bilgi-paketi-plan2
written: 2026-08-30
---

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-08-30) — bu anlatı **checkpoint 1 kapanışına** aittir;
> güncel durum TASK.md + yürütme defteri + git defterinden okunur, çelişkide onlar esastır.

# Resume From

**Sıradaki adım: Task 3** (kalıp kimliği + karar günlüğü şeması, K-84 ailesi). Komut:
`/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** seçilir.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Her görevin commit aralığı, her hakem bulgusu, her kontrolör kararı ve gerekçesi orada.
Bağlam kaybolursa **defter + `git log`** esastır, anlatı değil.

**Yürütme durumu (TASK.md "Execution State"):** kip alt-ajanlı · başlangıç çapası `a806e29` ·
defter penceresi `a806e29` · `cp_count: 1` · `last_checkpoint_ref: 72f5744`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Push EDİLMEDİ** — yürütme commit'leri yereldedir.
**Dış sözleşme deposu da yereldedir:** `/root/otomaix-sosyal-medya-arastirmasi`, `master`,
HEAD `d901eb4`, temiz, uzak deposu yok.

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar** (üçü de bu oturumda işe yaradı):
1. Arayüz eki **bağlayıcıdır**, çelişkide EK geçerlidir; görevi bağlayan hükümler planın o
   görev başlığındaki "Arayüz eki bağlar" satırında yazılı. Uygulayıcı brief'e **ekin ilgili
   hükümleri harfiyen kopyalanmış** olarak gider — plan metni tek başına yetmez.
2. Test komutu **sanal ortam aktifleştirilerek** koşar (aşağıda Verification).
3. **Taban 692**; bu sayı düşmeyecek.
4. Commit footer'ı **yalnız monorepo** commit'lerine biner; dış depo commit'i düz Conventional
   Commits alır. `Exec-Kind` yazılmadan ÖNCE commit'in gerçek path kümesine BAKILIR.
5. Test önce yazılır, **kırmızı düştüğü gözle görülür**, kırmızı çıktı rapora yazılır.
6. Uygulayıcı **kendi alt-ajanını çağırmaz**; review kontrolörden gelir.

**Task 4'e taşınacak devir:** Task 2'nin Task 4'e bağladığı üç sözleşme kalemi (TASK.md Open
Problems). Task 4 aynı dosyalara dokunuyor ve sürümlerini zaten artırıyor.

**Task 8'e taşınacak devir:** `tests/test_contract_pin.py` dış depo yolunu sabit yazıyor
(depoda tek geçtiği yer). Task 8 `run_folder` ile aynı yola ihtiyaç duyacak — ortak sabit
oraya ait, burada icat edilmedi.

**Task 11'e taşınacak devir:** K-113'ün **kod ayağının** Plan 2'de evi yok (ölçüldü: Task 11'in
invariant listesi yalnız iki-havuz şeklinden söz ediyor, planda `hareket` için iki geçiş var
ikisi de şema, `short_video.py:295-308` hâlâ paket girdisi olmadan kendi sabit listesinden
çekiyor). Ev Task 11 dispatch'inde verilir.

**Task 18 Step 8b'ye taşınacak devir:** git ortam değişkeni (`GIT_DIR`/`GIT_WORK_TREE`)
ezilmesi ekseninin **iki örneği birden** — üretim tarafı (`contracts.py::_head_commit`) ve
test tarafı (`test_external_repo_gitignores_run_folder`). Tek süpürme ikisini birlikte kapatır.

**Operasyonel not (ölçüldü):** `run_codex_scan`'e **tam 40 karakterlik SHA** verilir. Kısa SHA
substrat kurulumunda `fatal: couldn't find remote ref` ile `rc=2` üretir — Codex hiç çağrılmaz.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-08-30, kontrolörün kendi koşumları — uygulayıcının
sözü değil):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **692 passed in 106.18s.** (Oturum başı 667 → Task 2 ile 672 → checkpoint düzeltmesiyle
  692. Hiçbir mevcut test zayıflatılmadı; bu ayrıca kontrol edildi.)
- Pin manifesti bayt bayt doğrulandı: `commit` = dış depo HEAD `d901eb4`, üç sha256 = diskteki
  dosyaların gerçek hash'leri. Canlı `verify_pin` → boş liste (temiz).
- Checkpoint high bulgusunun **üç senaryosu da** düzeltme öncesi ve sonrası koşuldu:
  öncesinde üçü de `[]` (geçiyor) döndürüyordu, sonrasında üçü de gerekçeli hata fırlatıyor.
- `ec_classify_diff` → RISKY · `ec_should_checkpoint 1 0 9` → RUN_RISK (kapı ölçüldü, seçilmedi).
- Codex checkpoint 1: `verdict: needs-attention` (1 high + 2 medium) → düzeltme →
  kapanış turu `verdict: approve` (1 medium kaldı, kabul edilmiş risk).

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Task 3–20 hiç yazılmadı.** Plandaki test adlarının çoğu henüz var olmayan dosyalara ait.
- **Sözleşme metinlerinin ÇALIŞMA ZAMANI tüketimi hiç ölçülmedi.** Sweep'in "var" yargıları
  metin varlığını ölçer, davranışı değil — sözleşmelerin gerçekten dediğini yaptırıp
  yaptırmadığı ilk kuru koşumda (Task 11/19) görülür.
- `git` ikilisi olmayan ortamda ve `GIT_DIR`/`GIT_WORK_TREE` ezildiğinde pin davranışı
  **hâlâ ölçülmedi** — evi Task 18 Step 8b (yukarıda).
- Canlıya hiçbir şey dağıtılmadı, hiçbir migration uygulanmadı, pilot koşulmadı.

# Risks

- **KABUL EDİLMİŞ RİSK (checkpoint 1, policy_accepted):** `test_external_repo_gitignores_run_folder`
  `git -C` kullanıyor ama `GIT_DIR`/`GIT_WORK_TREE` bunu eziyor — o değişkenlerle işaret edilen
  bir sahte depo testi geçirebilir. Codex bunu doğrudan üretti. Üretim pin yolu etkilenmiyor ve
  saldırı tam olarak pinlenen commit'te bir sahte depo + zehirli ortam ister. Evi Task 18 Step 8b.
- **KABUL EDİLMİŞ RİSK (uygulayıcının kendi bildirdiği kalıntı):** dış deponun İÇİNDE dışarıyı
  gösteren bir sembolik bağ hâlâ ele alınmıyor; kapatmak `verify_pin`'e `resolve()` içerilik
  kontrolü eklemeyi gerektirir — ekin R14 hükmünün yasakladığı beşinci kapı. Modül belgesinde
  "çözülmedi + park edildi" etiketiyle, yeniden açılma koşuluyla duruyor. **"Ele alındı" DEĞİL.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`). Arayüz eki 8 çelişki +
  12 boşluğu kapattı ama **Plan 1 alanındaki kart geçişi hâlâ taranmadı** — Plan 1 yüzeyinde
  kusur çıkarsa ilk bakılacak yer.
- **Tekrarlayan kusur sınıfı — bu oturumda da doğrulandı:** bir hüküm yazılıp onu tüketen yerler
  süpürülmüyor. Task 2'de ölçüldü: atıf sweep'inin ikinci tablosunda **25 atıfın 25'i** yanlıştı,
  hakem bunların yalnız 5'ini bildirmişti; kalan 20'si düzeltmenin kendi metin değişikliklerinden
  kaymıştı. **Bildirilen örneği değil sınıfı kapat** — bu oturumda iki kez kendini ödedi.
- **Hakem bulgusunu ölçmeden kabul etme.** Bu oturumda üç kez fark yarattı: (a) Codex'in high
  bulgusu kod okumasına dayanıyordu ve ölçünce **doğru** çıktı; (b) hakemin ~6.000 karakter
  tavanı uyarısı ölçünce **yanlış** çıktı (sapan taraf spec metniydi, sözleşme değil);
  (c) kontrolörün kendi test tahmini yanlıştı ve uygulayıcı testi ona uydurmayı reddetti — haklıydı.
- **Codex maliyeti:** bu oturumda 3 çağrı (1 checkpoint + 1 substrat-hatası ile hiç çağrılmayan
  + 1 kapanış turu). Toplam yürütme boyunca 7. Uzun turlar **arka planda** koşulmalı — ön planda
  kabuk 10 dakikada keser.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı
  ([[feedback_claude_runs_reviewer_rounds]]). Checkpoint, final, bağımsız hakem: hepsi doğrudan
  koşulur. Maliyet tek satır bilgilendirmedir, izin sorusu değil.
- **Kontrolör düzeltme YAPMAZ.** Bulgular uygulayıcıya gider. Tek istisna `docs/active/` —
  o kontrolörün kendi yüzeyidir (checkpoint 1'de Codex haklı olarak bayat TASK/HANDOFF'u yakaladı).
- **Minor bulgular döngüye girmez** — deftere yazılır ve adı konmuş bir sonraki göreve bağlanır.
  Bu oturumda beş Minor bilinçli olarak turun içine alındı; gerekçe her seferinde deftere yazıldı
  (aynı dosyaya dokunuyorlardı ve manifest zaten yeniden pinleniyordu).
- **Spec değil, spec-input kanoniktir.** Task 2'de yine fark yarattı: uygulayıcı `EK-K`'yı üç
  dosyalık dar bir aramaya dayanarak "kanonda yok" ilan etti, yanıldı, kendi düzeltti. Dar arama
  refleksi bu depoda tekrarlayan bir kusurdur ([[feedback_dont_declare_absence_from_one_check]]).
- **Uygulayıcı raporunu doğrulanmamış iddia say.** Bu oturumda her sayı bağımsız olarak yeniden
  koşuldu ve hepsi tuttu — ama tutması, koşmamanın gerekçesi değildir.
- Diskte bekleyen düzeltme YOK; her şey commit'li, iki çalışma ağacı da temiz.
