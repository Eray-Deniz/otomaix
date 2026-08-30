---
task: sektor-bilgi-paketi-plan2
written: 2026-08-30
---

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-08-30) — bu anlatı yürütme öncesine değil, **Task 1 bitişine**
> aittir; güncel durum TASK.md + yürütme defteri + git defterinden okunur, çelişkide onlar esastır.

# Resume From

**Sıradaki adım: Task 2.** Yürütme devam ediyor, komut:
`/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** seçilir.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Her görevin commit aralığı, her hakem bulgusu, her kontrolör kararı ve gerekçesi orada.
Bağlam kaybolursa **defter + `git log`** esastır, anlatı değil.

**Yürütme durumu (TASK.md "Execution State"):** kip alt-ajanlı · başlangıç çapası `a806e29` ·
defter penceresi `a806e29` · `cp_count: 0` (checkpoint henüz koşmadı) ·
Codex log `~/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Push EDİLMEDİ** (ölçüldü 2026-08-30):
yürütme commit'leri yereldedir. `main` = `origin/main` = `d5d72e1`.

**Task 2 dispatch'inde ZORUNLU olarak taşınacaklar** (Task 1'de bunlar işe yaradı):
1. Arayüz eki **bağlayıcıdır**, çelişkide EK geçerlidir; Task 2'yi bağlayan hükümler planın
   Task 2 başlığındaki "Arayüz eki bağlar" satırında yazılı — uygulayıcı onları okumadan
   koda başlamaz.
2. Test komutu **sanal ortam aktifleştirilerek** koşar (aşağıda Verification).
3. Taban **667**; bu sayı düşmeyecek.
4. Task 1'den devredilen üç Minor bulgu (TASK.md Open Problems ilk maddesi) Task 2'nin işidir.
5. Test önce yazılır, **kırmızı düştüğü gözle görülür**, kırmızı çıktı rapora yazılır.
6. Uygulayıcı **kendi alt-ajanını çağırmaz**; review kontrolörden gelir.

**Task 2 dış depoda çalışır** (`/root/otomaix-sosyal-medya-arastirmasi/`) ve bitiminde monorepo'ya
döner — göreli yollar oradan çözülmez, bu planın kendi kısıtı.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-08-30):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **667 passed in 105.52s.** (Yürütme öncesi taban 660; Task 1 yedi test ekledi, regresyon yok.)
  Bu ölçümü kontrolör uygulayıcıdan bağımsız olarak kendisi koştu.
- Task 1 kırmızı turu: `ModuleNotFoundError: No module named 'app.services.sector_pipeline'`
  — modülün yokluğu yakalandı, testin kendi yazım hatası değil.
- Ortam ölçümü: `python` PATH'te **YOK**; `.venv` requirements sürümlerini birebir taşıyor
  (pytest 9.1.1 · pytest-asyncio 1.4.0 · asyncpg 0.29.0 · fastapi 0.115.0).
- Veritabanı: `127.0.0.1:5433` erişilebilir, `social.sector_packages` okundu (0 satır).
- Dış sözleşme deposu: temiz, `master`, HEAD `b356033`, üç sözleşme dosyası yerinde.
- En yüksek mevcut migration **034** (plan 035/036 yazacak).
- Mekanik öz-denetim (kontrolörün kendi betiği, ajan sayılarından bağımsız):
  **50 hüküm→görev çifti, 50'si görev satırında, 0 eksik**; genel liste 17 hüküm diyor, 17 bulundu.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Task 2–20 hiç yazılmadı.** Plandaki test adlarının çoğu henüz var olmayan dosyalara ait.
- **Hiç checkpoint review'ı koşmadı** (`cp_count: 0`) — Task 1 riskli sınıflamaya girmedi.
- `git` ikilisi olmayan ortamda ve `GIT_DIR`/`GIT_WORK_TREE` ezildiğinde pin davranışı
  **ölçülmedi** (hakem ortam bulamadı).
- Arayüz ekinin kalan medium/low sınıfı (annotation ≠ çalışma zamanı zorlaması; kimlik
  karşılaştırmasında hoşgörülü normalleştirme) **dördüncü turla kovalanmadı** — kabul edildi.
- Canlıya hiçbir şey dağıtılmadı, hiçbir migration uygulanmadı, pilot koşulmadı.

# Risks

- **Plan, hakem görmeden onaylanmıştı** (risk kabulüyle, `approved-by-iteration-limit`). Yürütme
  öncesi ön-tarama bunun bedelini ölçtü: 8 çelişki · 12 boşluk. Arayüz eki bunları kapattı ama
  **Plan 1 alanındaki kart geçişi hâlâ taranmadı** — Plan 1 yüzeyinde kusur çıkarsa ilk bakılacak yer.
- **Tekrarlayan kusur sınıfı — bu oturumda ÜÇ kez tekrarladı:** bir hüküm yazılıp onu tüketen
  yerler süpürülmüyor. Deftere süreç kuralı olarak yazıldı: *bir karar, süpürülene kadar
  uygulanmış sayılmaz*; aynı düzenlemede çelişen her kod bloğu, genel liste ve kararın adını
  andığı her görev satırı güncellenir. **Yeni oturum bu kuralı devralmalı.**
- **Kanıt doktrini kod düzeyinde HENÜZ zorlanmıyor.** Arayüz eki jetonu savunma katmanı olarak
  tanımlar; gerçek sınır bir veritabanı yetki sınırıdır ve ancak canlı ölçümle kurulur.
  Evi: Task 15 Step 6 + Task 18 Step 7 (üç tabloyu ve jeton kolonlarını kapsayacak şekilde
  genişletildi). Bugün **açık**, tarihi belli.
- **Hakem bulgusunu ölçmeden kabul etme.** Bu oturumda Codex'in iki bulgusu (pytest sürümleri,
  veritabanı erişimi) **yanlış çıktı** — sanitize edilmiş kopyada koştuğu için `.venv` ve `.env`
  göremiyor. Ölçmeden düzeltmeye başlansaydı ortam boşuna kurcalanacaktı.
- **Codex maliyeti:** bu oturumda 4 çağrı (1 ön-değerlendirme + 3 arayüz eki turu). Kota
  başlangıçta tazeydi. Uzun turlar **arka planda** koşulmalı — ön planda kabuk 10 dakikada keser
  ve tur boşa gider (bu oturumda bir kez oldu).

# Notes For Claude/Codex

- **Hakem turunu kim koşar? ÖNCE SOR.** 2026-08-30 oturumunda Eray "eskisi gibi sen koşabilirsin"
  dedi ve bunun **o oturuma özgü** olduğunu belirtti; kalıcı hafızaya yazılmadı. Yeni oturumda
  teyit al.
- **Kontrolör düzeltme YAPMAZ.** Bulgular uygulayıcıya gider; kontrolör düzeltirse review atlanır
  ve kontrolörün bağlamı kirlenir.
- **Minor bulgular döngüye girmez** — deftere yazılır ve adı konmuş bir sonraki göreve bağlanır.
  Park etmek yasak; ev ya vardır ya bulgu düşürülür.
- **Spec değil, spec-input kanoniktir.** Bu oturumda da fark yarattı (koşu klasörü / K-17 ve
  "kanıt yoksa karar uygulanmaz" hükmü).
- **Süpürme sayıları ölçüldü, hatırlanmadı:** ek atıflarının %12'si kaymıştı (222'nin 26'sı);
  dondurulmuş tiplerin 18'inden 8'i kusurluydu — hakem yalnız 2 bildirmişti. **Bildirilen
  örneği değil sınıfı kapat.**
- Diskte bekleyen düzeltme YOK; her şey commit'li, çalışma ağacı temiz.
