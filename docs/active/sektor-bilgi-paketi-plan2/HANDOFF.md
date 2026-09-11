---
task: sektor-bilgi-paketi-plan2
written: 2026-09-11
---

# Resume From

**Sıradaki iş: Task 18 (ön-pilot dağıtım).** Dış sözleşme turu BİTTİ: dış depo `d9dc289`,
pin `2739797`, kod uyarlaması `4cf6aa3`, hakem turu (dual) üç yüksek → düzeltme `171c1e5` →
kapanış turu (**Claude-only**) üçünü KAPANDI ölçtü → iki düşük `90aee2c`. Canlıya girme kararı
hâlâ Eray'da.

**Eray kararı (oturum kapanışı):** YALNIZ bu düzeltme partisi için tekrar review yok — **genel kural
DEĞİL**, sonraki oturumlarda düzeltme → tekrar review düzeni aynen sürer. Kapanış tek-hakem kaldı
(`dual-review: false`); `/security-review-claude-codex` başlatılırken chain-advance gate'i explicit
dual-review override soracak — karar o anda. Codex kapanış tekrarı İPTAL (aktif katman kaydı
TASK.md `# Open Problems` ilk kalem).

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → beklenen `4379 passed`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Push durumu buraya YAZILMAZ, ölç:
`git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD` (oturum sonunda
origin'in ÖNÜNDE, push edilmedi — Eray onayı olmadan push yok).
**Yürütme durumu:** kip `inline` · başlangıç çapası `a806e29` · defter penceresi `a806e29`.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi` @ `d9dc289`; pin monorepo'da
`2739797`. Üç dosyanın sha256'sı pinle byte-eşit (iki hakem turunda ayrı ayrı doğrulandı).
`kuyumculuk.md` (pilot brief kopyası) 2026-08-17 tarihli ve şablonun ESKİ hâli — pilotta şablondan
yeniden türetilmeli (Task 19 girdisi; pin'de DEĞİL).

**Review defteri:** locator `task:sektor-bilgi-paketi-plan2`, hedef
`code-review:feat-sektor-bilgi-paketi-plan2:10f22da…`, pinli sözleşme `a76100bd…`. Authoritative
state TASK.md `# Review Ledger` (bu oturumda KURULDU — önceki oturumun "kurulmalı" borcu kapandı).

## Bu oturum ne yaptı — tek cümle

Üç sözleşme borcu tek dış-depo revizyonunda kapatıldı, pin ilerletildi, kod üç kimliği tüketecek
şekilde uyarlandı; dual hakem turunun üç yüksek bulgusu düzeltilip Claude-only kapanış turuyla
kapalı ölçüldü, iki düşük de kapatıldı.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (kontrolörün kendi koşumları):**

- Tam takım `.venv/bin/python -m pytest tests/ -q`:
  - `2739797` (pin) → **4334 passed, 1 failed** (Bölüm B sütun alarmı — beklenen kırmızı), 315 s
  - `4cf6aa3` (kod uyarlaması) → **4370 passed**, 318 s
  - `171c1e5` (düzeltme) → **4379 passed**, 315 s (alt-hakem kendi kopyasında da 4379 ölçtü)
  - `90aee2c` (iki düşük) → üç takım 1753 passed; tam takım: aşağıdaki satır
  - `90aee2c` tam takım → **4379 passed in 313.83s (0:05:13)**
- **Mutasyon:** kod uyarlaması 12 kapı → 12/12 kırıldı · düzeltme partisi 5 kapı → ilk 4/5, sağ kalan
  ("iki taraf da boş URL") gerçek boşluktu, test güçlendirildi → 5/5 · iki düşük 2/2. Alt-hakem
  bağımsız 4 mutasyon: 4/4.
- **Pin testleri** (`test_contract_pin.py`) 32 passed; pin geçici hash'le ölçüldü: 1829 passed / 1 alarm.
- **Canlı yerel DB:** `social.public_holidays` 22 satır + anahtarları (şablon tablosunun kaynağı);
  `social.sector_package_runs` tablosu yerelde YOK (03x migration'lar uygulanmamış) → sema-1
  dondurulmuş görüntü yerelde imkânsız.
- **Hakem turları:** attempt-1 dual (Claude 67 araç / 1010 s; Codex rc=0 / 52 komut) → 3 high both-agree,
  üçü kontrolör ölçümüyle doğrulandı · kapanış Claude-only (63 araç / 1104 s): F1-F3 kapandı, 2 low.
- **Defter kapısı** her commit'ten sonra `rc=0` (6 commit: pin · kod · review · fix1 · fix2 · kapanış docs).

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Codex kapanış hakemi KOŞMADI** (ilk çağrı kesik `exit=1` → kanıt değil; tekrar "usage limit").
  Eray kararıyla bu parti için tekrar edilmedi (tek seferlik); `dual-review: false` etiketi bu
  kapanışa özgü.
- **`90aee2c` bağımsız hakem GÖRMEDİ** (test-ağırlıklı + tek yüklem değişikliği).
- **Uçtan uca CLI koşumu YAPILMADI**; yeni sözleşme biçiminde gerçek araştırma çıktısı YOK (ilk ölçüm Task 19).
- **Üretim DB'sinde sema-1 dondurulmuş görüntü yokluğu bu kökten ölçülemedi** (koşu tablosu canlıda
  da dağıtılmadı — HANDOFF'un önceki iddiası; fail-closed: olursa `RC_REFUSED`).
- **`ruff`/`pyright` ortamda YOK.** CRM webhook onarımı YAPILMADI. Task 18-20 yazılmadı.

# Risks

- **Dual-review eksik kapanış** — üç yüksek yalnız Claude hakemiyle "kapandı" ölçüldü; Codex'in kesik
  ilk çıktısı iki şüphe bırakmıştı (URL kırpma toleransı · özette gerekçe metni); ikisi de kontrolör
  tarafından ölçüldü ve kabul edildi (kırpma gerçek yolda fark yaratmaz; özet üç kimlik alanını basar).
- **N1/1 — aday-dışı gün ad↔anahtar bağı ölçülemiyor** (accepted_risk, koşullu; yeniden açılma:
  pilot aday-dışı bir gün seçerse). İkinci kapı: tür↔kategori çatışması notu artık onay yüzeyinde.
- **F6 — kaynak başına 3 URL satırı dağılımı ölçülmüyor** (önceden var olan; ev Task 18 listesi).
- **Çok günlü bayramlar** (Ramazan 4, Kurban 5 sistem satırı): mevcut kural paket girdisi başına bir
  anahtar ister — sözleşmede ilk kez AÇIKÇA yazıldı; paket şişmesi pilotta ölçülür. Dönem düzeyinde tek
  anahtar çalışma zamanı (K-01b) değişikliğidir; ev: pilot ölçümü sonrası spec K-01b takibi.
- **Normalize edici "Millî"nin î'sini düşürüyor** (`demokrasi-ve-mill-birlik-gunu`); tablo bu hâliyle
  yazıldı; düzeltmesi sektör slug kuralına dokunur (kapsam dışı, kayıtlı).
- **035 migration dağıtılana kadar** şablondaki üç dönem (10 Kasım · 24 Kasım · okula dönüş)
  "sistemde yok" gibi davranır — şablonda yazılı; Task 18 dağıtım sırası.
- **K-03 notu operatör yüzeyinde ama CLI çıktısı uçtan uca koşulmadı** (yalnız render testi + CLI testi).
- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI**
  (CURRENT.md tetikli kalem).
- Önceki oturumlardan devralınan kabul edilmiş riskler aynen (attest_readiness prob sonuçlarını görmez ·
  kilit sözleşmesi kaynaktaki kilitleri modeller · `recovered` bakım penceresi · migration 036 yerinde ·
  commit geçmişi tek-commit TDD modeline uymuyor · plan hakem görmeden onaylandı).

# Notes For Claude/Codex

**Sonraki oturumun girdisi:** Task 18 (ön-pilot dağıtım) — TASK.md'deki liste: migration dağıtım
sırası (035/036 + n8n takvim işi) · mekanik kapı raporu artefakt türü · köken jetonu (M-1/M-2) · F6 ·
`kuyumculuk.md`'nin şablondan yeniden türetilmesi. Canlıya girme kararı Eray'da.

**Sözleşme turunda öğrenilenler (bu oturum):**
1. **Tek sözleşme turu iyi çalıştı** — üç borç bir revizyonda, pencere (araştırma üretilmemiş) hâlâ açık.
2. **Denetçi paketinde EK-J yok** — 2.2 denetçiden görmediği bir listeye uymasını istiyordu; anahtarın
   kaynağı artık araştırmanın Bölüm B sütunu. Sözleşme yazarken "hangi ek hangi hakeme gidiyor" ölç.
3. **Sözleşme değişikliğinin üçte biri alarm taşıyordu** — URL başlığı ve not sınıfı için pinli
   sözleşmeye karşı test yoktu; eklendi. Yeni sözleşme yüzeyi eklerken alarm testini aynı commit'e koy.
4. **Kesik Codex kararı kanıt değildir** — `exit=1` + 28 komut + yarım cümle; retry kotaya takıldı.
   Kota kapısı "stale" derken uzun tur planlıyorsan önce taze ölç.
5. **Mutasyon kolu iki gerçek boşluk yakaladı** (boş==boş URL; aday-dışı çoklu anahtar) — kapı
   eklerken sınır vakalarını (boş/çift/karma) mutasyonla ayrıca sına.

**Codex çağrısı kurarken:** COMPANION + PROMPT çağıran kabukta; prompt dosyası SETUP fence sonrası
Write ile; uzun turlar arka planda 1200 s; çağrı sonrası `rc` + koşum sayısı + son cümle üçünü kontrol et.
