---
task: sektor-bilgi-paketi-plan2
written: 2026-09-12
---

# Resume From

**Sıradaki iş: Task 19 (kuyumculuk pilotu) — TAZE OTURUMDA başlar (Eray kararı).**

İlk iş **Step 1: dört operatör kararını kapatmak** (K-04a–d). Dördü de "pakete ne girecek"
kararıdır, birbirinden bağımsızdır ve tasarım bunları bilinçle Eray'a bırakmıştır. Öneriler
`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` satır 2470-2473'te:
- **K-04a** gümüş pakete girsin mi? → öneri: **girsin**
- **K-04b** kasım indirim dönemi girsin mi? → öneri: **girmesin** (sistemde `Black Friday` adıyla)
- **K-04c** kampanya-aciliyet istisnası tanımlansın mı? → öneri: **tanımlanmasın**
- **K-04d** kaynaksız kültürel sahne eklentileri Faz 1'e mi? → öneri: **Faz 2**

Dördü de `Bloklamaz` etiketli ama **paket taslağı yazılmadan ÖNCE** kapanmalı.
**Karar turu kuralı:** her `AskUserQuestion` TEK karar taşır, altına sade dille senaryo özeti.

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → beklenen `4412 passed`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, **push EDİLDİ** (`08607f8`'e kadar; `8daad2f` bu
oturumun son commit'i ve HENÜZ push edilmedi — ölç: `git rev-list --left-right --count
origin/feat/sektor-bilgi-paketi-plan2...HEAD`).
**Yürütme durumu:** kip `inline` · başlangıç çapası `a806e29` · defter penceresi `a806e29`.

**Dış sözleşme deposu:** `/root/otomaix-sosyal-medya-arastirmasi`, HEAD `c3f0d30`,
pin bu commit'e güncel (`shared/contracts/research-contracts.pin.json`).

**Bu oturumun commit'leri (7):** `12d1743` artefakt türü + sınıf kapısı · `be538ed` F6 ·
`ac0b896` runbook · `ab91495` pin bump · `6d671f6` canlı dağıtım kaydı · `08607f8` M-1 kararı ·
`8daad2f` servis dağıtımı kararı.

**Defter kapısı (`ec_mechanical_sweep`) rc=1 — BU COMMIT'LERDEN DEĞİL.** T18/T19/T20 henüz
düz kimlikli (`Exec-Task: T<N>`) bir commit almadı; tamamlanan görevlerin hepsi (T1..T17) almış.
HEAD~1'de de aynı çıktı ölçüldü. Kapı, görevler bitince kendiliğinden yeşile döner.

# Bu oturum ne yaptı — tek cümle

Task 18'in canlıya dokunmayan bütün kalemlerini kapattı (artefakt türü + kusur sınıfı · F6 ·
brief yeniden türetme · runbook), ardından Eray onayıyla canlıya **şemayı** dağıttı (prova →
geri dönüş noktası → 035/036) ve dağıtımın üç ayağını ölçülmüş gerekçelerle tarihli evlere bağladı.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları:**

- Tam takım `.venv/bin/python -m pytest tests/ -q`:
  - oturum başı tabanı → **4404 passed / 321.43s**
  - `12d1743` sonrası → **4411 passed / 320.20s**
  - `be538ed` sonrası → **4412 passed / 318.44s**
  - `ab91495` sonrası → **4412 passed / 320.03s**
  - `6d671f6` sonrası → **4412 passed / 316.20s** (hepsi 0 failed)
- Migration dosyaları (`test_migration_036` + `032` + `032_rollback` + `object_identity`) →
  **583 passed**. Sözleşme pin'i `test_contract_pin.py` → **32 passed**.
- **Mutasyon 8/8:** artefakt türü ayağında 6 (CLI türü · yazıcı değişmezi · 036 genişletmesi ·
  geri alma daraltması · Python sabiti ıraksaması · eşleşme tablosu eksilmesi), F6 ayağında 2
  (dağılım kapısı susturuldu · kaynak başına sabit 3→2).
- **Canlı prova (klonda):** 6 koşum, 6'sı rc=0; üç tablo VAR→YOK→VAR; `public_holidays.end_date`
  1→0→1.
- **Canlı uygulama:** `035` rc=0 · `036` rc=0. Geri dönüş noktası
  `/root/otomaix-deploy-backups/canli-035-036-oncesi-20260912-145056.dump` (188 KB, 0600,
  `pg_restore -l` ile 242 nesne okunabilir). Canlı doğrulama: beş tablo VAR · `end_date` VAR ·
  üç tetikleyici kurulu · artefakt tür kümesi DÖRT değerli.
- **Canlı CLI:** `--help` rc=0 · `durum --run-id <yok>` → `koşu yok: …` (bağlantının kanıtı) ·
  `sector_sweep --dry-run` → `differences: 0`.
- **Canlı pin:** `require_pin` sessiz dönüş = geçti. **`git` ortamı:** `git version 2.43.0`,
  `GIT_DIR`/`GIT_WORK_TREE` set DEĞİL.
- **Yetki ölçümü (M-2):** API kimliği `otomaix`, `rolsuper=True`, tabloların sahibi; negatif
  yazma denemesi üç tabloda da KABUL EDİLDİ.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Bu oturumun hiçbir commit'i bağımsız hakem GÖRMEDİ.** Ne `/review-claude-codex` ne
  `/security-review-claude-codex` bu dört kod/şema commit'i üzerinde koşuldu. Şema canlıya
  hakem görmeden indi — bilinçli, Eray onaylı, ama **doğrulanmamış**.
- **Backend SERVİSİ dağıtılmadı** → Task 18 Step 5 · 6 · 7 KOŞULMADI.
- **Yetki KALDIRMA ayağı yapılmadı** (M-1 kararla ertelendi).
- Uçtan uca CLI koşumu YOK; yeni sözleşme biçiminde gerçek araştırma çıktısı YOK (ilk ölçüm Task 19).
- `ruff` / `pyright` ortamda YOK.
- 22 tabloluk API yazma kümesi **üst sınırdır** (ithal kapanışından türetildi; "modül yükleniyor"
  ile "fonksiyon çağrılıyor" ayrı şeyler). 4 kanıt tablosunun okuma/yazma ayrımı ise fonksiyon
  düzeyinde ölçüldü.

# Risks

- **Canlı şema ileride, kod geride.** Veritabanında Plan 2 tabloları var; canlı API onları
  tanımayan eski imajı koşuyor. **Bu tasarım gereği güvenlidir** (yeni tablolara eski kod
  dokunmaz) ama unutulursa "neden çalışmıyor" karmaşası üretir.
- **S-7 (critical, `accepted_risk`)** — Telegram onay/ret uçları kimliksiz; Eray kararıyla açık
  risk kabulü, iki workflow canlıda AKTİF. Yeniden açılma koşulu: gerçek müşteri kullanımı.
- **S-6 (medium, kanıt boşluğu)** — takvim workflow'u SQL'i string birleştirmeyle kuruyor;
  **Task 18 Step 7 (n8n import) o dosyayı import ediyor** → karar o adımdan önce gerekli.
- **M-1 (yüksek)** — uygulama veritabanına KÖK kimlikle bağlanıyor; kanıt katmanının güvencesi
  şu an yalnız Python'da. Ev: depo/anahtar temizliği turu.
- **`repo-public-exposed-live-credentials`** — depo public, anahtarlar ilk commit'ten beri açıkta.
  Ev: Plan 2 yürütmesi biter bitmez, ilk iş.
- **İstemci/sunucu sürüm farkı** — sunucu PostgreSQL 18.3, host araçları 16.15; `pg_dump`
  reddediyor. Döküm/klon konteyner araçlarıyla yapılır. Host'a 18 istemcisi kurulmadı.
- Önceki oturumlardan devralınan kabul edilmiş riskler aynen (N1/1 · çok günlü bayramlar ·
  normalize edicinin `î` düşürmesi · attest_readiness prob sonuçlarını görmez · kilit sözleşmesi ·
  `recovered` bakım penceresi · commit geçmişi tek-commit TDD modeline uymuyor · plan hakem
  görmeden onaylandı · kapanış turu tek-hakem kaldı).

# Notes For Claude/Codex

**Sonraki oturumun girdisi:** Task 19 Step 1 (dört karar) → Step 2 (test markası) → Step 3
(alt sektör satırı) → Step 4 (kişisel veri doğrulaması) → Step 5 (K-18 yeniden üretim).
**Step 11'den ÖNCE Coolify deploy'u** yapılır (Task 18'in 5-6-7'si orada kapanır).

**Bu oturumda öğrenilenler:**
1. **Kusur sınıfını kapatmak varyantı yamamaktan ucuz.** Artefakt türü kusuru tekil değildi;
   aynı süreç yedi kapalı küme üretmişti ve yalnız biri korumalıydı. Tek sınıf kapısı + kapsama
   kapısı ikisini de kapattı ve yazıldığı anda bir kalem daha buldu.
2. **Metin okuyan kapı bir sonraki migration'a kördür.** İki kapı 032'nin satır içi CHECK
   METNİNİ regex'liyordu; 036'nın genişletmesi ölçüme hiç girmiyordu. Kaynak kataloğa taşındı.
3. **Fixture kusuru taşıyorsa kapı yazınca ortaya çıkar.** F6'nın dağılım kuralını üç test
   yardımcısı ihlal ediyordu — kapı eklenince 41 test kırmızıya döndü ve kusuru gösterdi.
4. **`git checkout` mutasyonu geri almaz, DOSYAYI geri alır.** Mutasyon testinden dönerken o
   dosyadaki tüm yeni testler silindi. Mutasyon geri alması DOSYA YEDEĞİYLE yapılır.
5. **İstemci sürümü sessiz bloker olabilir.** İlk prova düştü çünkü `pg_dump` 16, sunucu 18.
   Hata "sürüm" demiyordu; zincir "döküm boş → restore boş → migration tabansız" diye ilerledi.
6. **Dar ölçüm ile geniş ölçüm ayrı sorulara cevap verir.** "API bu tablolara yazıyor mu"
   sorusu router'ların DOĞRUDAN referansıyla ve geçişli ithal kapanışıyla FARKLI çıktı; doğru
   ölçüm fonksiyon düzeyindeydi. Kaba kapanış modülün YÜKLENDİĞİNİ gösterir, ÇAĞRILDIĞINI değil.
7. **Dağıtım hedefi varsayılmaz, ölçülür.** Coolify `main` dalını izliyor; "deploy et" demek
   Plan 2 kodunu dağıtmazdı.

**Codex çağrısı kurarken:** COMPANION + PROMPT çağıran kabukta; prompt dosyası SETUP fence
sonrası Write ile; uzun turlar arka planda 1200 s; çağrı sonrası `rc` + koşum sayısı + son cümle
üçünü kontrol et. Aynı oturumda ikinci uzun turdan önce kotayı TAZE ölç.
