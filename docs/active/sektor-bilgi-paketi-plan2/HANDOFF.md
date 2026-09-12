---
task: sektor-bilgi-paketi-plan2
written: 2026-09-12
---

# Resume From

**Sıradaki iş: Task 19 Step 5 — üç araştırma koşusu, ELLE. İş Eray'da, yürütücüde değil.**

Eray'ın yapacağı (spec §8.1'in yazdığı hâliyle):
1. `/root/otomaix-sosyal-medya-arastirmasi/kuyumculuk.md` dosyasının TAMAMINI üç derin
   araştırma aracına AYRI AYRI ver — üçüne de AYNI metin.
2. Çıktıları `KAYNAK-1.md` · `KAYNAK-2.md` · `KAYNAK-3.md` olarak kaydet
   (**kör adlandırma dosya adından itibaren** — spec §8.1).
3. Her kaynak için damga bilgisi: **model + sürüm + tarih** (K-80 ZORUNLU; komut tarih
   üretmez). Araç kimliği KAYDEDİLİR (K-138 kapalı) ve yalnız operatör/yönetici okur
   (K-139 kapalı); denetçiye yapısal olarak kapalıdır (K-137).

Çıktılar gelince yürütücü devam eder: `tur-ac` (sektör kimliği
`7353a672-148f-4add-8920-619f05e839c7`, `--kosu-turu ilk`) → `brief-doctor` (kaynak başına,
damgayla) → `denetim` → `sentez`. **`motor` BURADA KOŞMAZ** — Step 7'de operatörün
YALNIZ-SENTEZ yargısı önce kaydedilir (K-134 çatalı; körlük kalibrasyonun ön koşulu).

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → beklenen `4412 passed`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Yürütme durumu:** kip `inline` ·
başlangıç çapası `a806e29` · defter penceresi `a806e29`.
**Dış sözleşme deposu:** `/root/otomaix-sosyal-medya-arastirmasi`, HEAD `abb1850`
(uzak sunucusu YOK — yalnız yerel), pin bu commit'e güncel.

# Bu oturum ne yaptı — tek cümle

Task 19'un ilk dört adımını indirdi (dört operatör kararı · canlıda test markası + alt sektör
satırı · R-35'in ölçülebilen iki ayağı) ve pahalı elle adıma girmeden ÖNCE brief'te iki kusur
buldu: brief temel paketi ATLA diyordu ve K-04b'yi yansıtmıyordu.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları:**

- Tam takım `.venv/bin/python -m pytest tests/ -q`:
  - oturum başı tabanı → **4412 passed / 318.42s / exit 0**
  - pin bump sonrası → **4412 passed / 322.21s / exit 0** (regresyon yok)
- `tests/test_contract_pin.py` → **32 passed**.
- Gerçek iki depoya karşı **`require_pin` sessiz dönüş = GEÇTİ** (canlı kapı, test değil).
- R-35 bariyer testleri (beş hedef test, ayrı ayrı adlandırılmış) → **5 passed / 0.55s**.
- `sector_sweep.py` önce/sonra: `brands_total 3` · `root_anchored 3` · `sub_sector_rows 0→1` ·
  `remapped 0` · `removed 0` · `added 0` · `differences 0` · **rc=0**.
- Canlı veritabanı kimliği ÖLÇÜLDÜ (varsayılmadı): `127.0.0.1:5433/otomaix` üzerinde canlı iki
  marka + 2026-09-12 dağıtımının dört Plan 2 tablosu.
- Takvimde `Black Friday` satırı ÖLÇÜLDÜ: 2026-11-27, `category=commercial`.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **R-35'in ÜÇÜNCÜ ayağı (paket İÇERİĞİ) ölçülmedi ve bugün ÖLÇÜLEMEZ** — paket içeriği yok.
  Evi: Step 9'dan sonra, Step 10 aktivasyonundan ÖNCE. "R-35 doğrulandı" DENMEZ.
- **Bu oturumun commit'leri bağımsız hakem GÖRMEDİ.** İkisi de docs + pin (`abb1850`,
  `2f9157a`); yürütülebilir kod değişmedi. Önceki oturumun KOD/ŞEMA commit'lerinin hakem
  görmemesi ayrı ve daha ağır bir kalemdir — Open Problems'ta duruyor, kapanmadı.
- **Uçtan uca CLI koşumu YOK; yeni sözleşme biçiminde gerçek araştırma çıktısı YOK** (Step 5).
- **Backend SERVİSİ hâlâ dağıtılmadı** — Task 18 Step 5·6·7 açık; Step 11'den ÖNCE koşulur.
- Test markası arayüzde GÖRÜLMEDİ (marka listesi önbelleği 300 s; kod okundu, ekran değil).
- `ec_mechanical_sweep` bu oturumda KOŞULMADI. T19 artık düz kimlikli commit aldı
  (`2f9157a`, `Exec-Task: T19`); T20 almadı — kapı yine rc=1 verir, görevler bitince yeşile döner.
- `ruff` / `pyright` ortamda YOK.

# Risks

- **Canlı şema ileride, kod geride** — veritabanında Plan 2 tabloları var, canlı API onları
  tanımayan eski imajı koşuyor. Tasarım gereği güvenli; unutulursa "neden çalışmıyor" üretir.
- **Canlıda kurgu marka var.** `Deniz Kuyumculuk (TEST)` prod verisidir ve Eray'ın marka
  listesinde görünür. Pilot bitince akıbeti kararlaştırılmalı — şu an evi YOK, dürüst etiket:
  **çözülmedi, park edildi**; yeniden açılma anı Task 20 kapanışıdır.
- **S-7 (critical, `accepted_risk`)** — Telegram onay/ret uçları kimliksiz; iki workflow canlıda
  AKTİF. Yeniden açılma koşulu: gerçek müşteri kullanımı.
- **S-6 (medium, kanıt boşluğu)** — takvim workflow'u SQL'i string birleştirmeyle kuruyor;
  n8n import adımı (Task 18 Step 7) o dosyayı import ediyor → karar o adımdan ÖNCE gerekli.
- **M-1 (yüksek)** — uygulama veritabanına KÖK kimlikle bağlanıyor. Ev: depo/anahtar temizliği turu.
- **`repo-public-exposed-live-credentials`** — depo public, anahtarlar ilk commit'ten beri açıkta.
  Ev: Plan 2 yürütmesi biter bitmez, ilk iş.
- **İstemci/sunucu sürüm farkı** — sunucu PostgreSQL 18.3, host araçları 16.15; döküm/klon
  konteyner araçlarıyla yapılır.
- Önceki oturumlardan devralınan kabul edilmiş riskler aynen.

# Notes For Claude/Codex

**Bu oturumda öğrenilenler:**

1. **Pilot içerik detayını mimari karara çevirme.** K-04a bir konumlandırma tradeoff'u gibi
   sunuldu; kuyumculuk yalnız ÖRNEK sektör ve karar zaten dondurulmuş brief'te kapalıydı.
   Eray itiraz etti. Karar sorusundan ÖNCE sözleşme ölçülür.
2. **Spec-input bayat olabilir; spec daha yeni kararı taşır.** K-138/K-139 spec-input'ta
   `[AÇIK]`, spec §3.3'te **2026-08-23'te KAPALI**. Yürütücü spec-input'a bakıp spec'e
   bakmadan "açık karar" dedi ve Eray'a kendi tercihini önerdi — iki kat hata. Kayıt: TASK.md.
3. **Pahalı elle adımdan ÖNCE girdiyi oku.** Brief'in iki kusuru ancak dosya açılınca çıktı;
   üç aracı o hâliyle koşturmak turu çöpe atardı.
4. **Alt sektör satırı açmak ölçülür, varsayılmaz.** `sector_sweep` önce/sonra ikilisi tam
   eşleme listesi karşılaştırıyor; "kök bağlı kaldı" tek başına yeterli değil.

**Codex çağrısı kurarken:** COMPANION + PROMPT çağıran kabukta; prompt dosyası SETUP fence
sonrası Write ile; uzun turlar arka planda 1200 s; çağrı sonrası `rc` + koşum sayısı + son
cümle üçünü kontrol et. Aynı oturumda ikinci uzun turdan önce kotayı TAZE ölç.
