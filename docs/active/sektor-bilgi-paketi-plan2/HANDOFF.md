---
task: sektor-bilgi-paketi-plan2
written: 2026-09-14
---

# Resume From

> ✅ **2026-09-18 — ENGEL KALKTI.** `denetci-surec-izolasyonu` görevi bitti (15/15) ve K-14
> canlı ölçüldü: **iki denetçi için de `erisim-var`, `tur_baslayabilir=True`** (claude 9,9 s ·
> codex 22,8 s). Aşağıdaki `denetim` komutu artık koşturulabilir.
>
> ⚠️ **Ama önce bir KARAR var.** O görevin dual review'ından üç bulgu açık (F1 critical + F5/F6
> high): ağa çıkabilen ajan, okuyabildiği her şeyi gönderebilir — en ağırı, kutulu codex'in
> Eray'ın OpenAI oturum jetonunu okuyabilmesi. Parasız yapısal kapanışı yok; kontrolörün önerisi
> "koşullu kabul edilmiş risk" (koşul: pakete üçüncü taraf ham içerik girdiği gün yeniden açılır),
> Eray onaylamadı. Ayrıntı: `docs/active/denetci-surec-izolasyonu/TASK.md` "Review bulguları".
> **Tur teknik olarak koşabilir; kararı vermeden koşturmak riski sessizce kabul etmek olur.**

**Sıradaki iş: Task 19 Step 6'nın `denetim` ayağı — iki kör denetçiyi koştur. İş YÜRÜTÜCÜDE,
Eray'da DEĞİL.**

Aktif koşu **`kosu-a4d4b59607384a30b072cd0395d0f750`** (`calisiyor`). Kapı üç kaynağa koştu,
artefaktlar yazıldı; kaynaklar koşu klasöründe (`denetim` oradan okur, DB'den okumaz).

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest -q` → beklenen **`4547 passed`** (2026-09-17'de ölçüldü; bu satır `4509` diyordu ve üç oturum boyunca bayatlamıştı).
⚠️ **Tek koşum.** İki pytest oturumu aynı anda koşarsa ortak test şablon veritabanını
birbirinden çekerler ve 42 sahte hata üretirler (bu oturumda ölçüldü).

**Denetim komutunun biçimi:**
```
cd apps/social/backend && set -a; . .env; set +a
.venv/bin/python scripts/sector_pipeline_cli.py --database-url-env DATABASE_URL denetim \
  --run-id kosu-a4d4b59607384a30b072cd0395d0f750 --sektor-slug kuyumculuk \
  --zaman-asimi-sn <SAYI> --arac-surumu bilinmiyor --tarih <YYYY-MM-DD>
```
`--zaman-asimi-sn` VARSAYILANSIZDIR (bilinçli: ölçülmemiş saniye sabitlenmiyor) — değer
seçilip GEREKÇESİ kayda geçirilir. Denetçiler alt süreçtir (`claude -p` ve `codex exec`,
ikisi de kurulu: 2.1.270 / 0.151.0) ve UZUN sürer → **arka planda koştur.**

**`denetim` SONRASI sıra:** `sentez` → **[K-134 çatalı: operatörün YALNIZ-SENTEZ yargısı
KAYDEDİLİR]** → `motor`. **Motor, Eray'ın kör yargısı kaydedilmeden KOŞMAZ** — körlük
kalibrasyonun ön koşuludur.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Kip** `inline` · başlangıç çapası `a806e29` ·
defter penceresi `a806e29`. **Dış sözleşme deposu:** `/root/otomaix-sosyal-medya-arastirmasi`,
HEAD `abb1850`, pin GÜNCEL.

⚠️ **Dış depoda COMMIT ATMA.** HEAD değişirse pin bayatlar ve CLI'ın her alt komutu
fail-closed durur. Kaynak dosyaları bilerek izlenmiyor; kirli ağaç pini DÜŞÜRMEZ.

# Bu oturum ne yaptı — tek cümle

Eray üç araştırmayı üretti; kapı onlara koşarken kapının KENDİ dört kusuru ölçüldü ve
kapatıldı (üretilmiş matris + fail-closed kollarıyla), kapı üç kaynağa taze koşturuldu.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları:**

- Tam takım `pytest tests/ -q`: oturum başı **4412 passed** → kapanışta **4509 passed /
  0 failed / 326,50 s** (+97 yeni test). Ara koşumlarda 4467 ve 4478 de ölçüldü.
- `tests/test_brief_doctor.py` tek başına → **1579 passed**.
- `tests/test_migration_036.py` tek başına → **491 passed**.
- Süs matrisi YAZILDIĞINDA **47 kırmızı / 1 yeşil** (yalnız süssüz hücre) — tautoloji
  olmadığı ölçüldü; düzeltmeden sonra 48/48.
- Eski kod ↔ yeni kod karşılaştırması (commit `3aca9a6` sürümü ayrı modül olarak yüklendi):
  ChatGPT 17 → **1** · Claude 50 → **45** · Gemini 34 → **119**. ChatGPT ve Claude'un
  bulguları ilk (markdown) düzeltmede **bit bit aynı** kaldı — gizli yan etki YOK.
- Canlı veritabanı ÖLÇÜLDÜ: `kuyumculuk` alt sektörü VAR (`7353a672-148f-4add-8920-619f05e839c7`,
  ebeveyn `e-ticaret-perakende`, TEK alt sektör satırı) · üç marka · `sector_packages` 0 satır.
- Koşu durumu ÖLÇÜLDÜ: üç koşu satırı; ikisi `tamamlanmadi` (gerekçeli), biri `calisiyor`.
- Kaçış/vurgu düzeltmeleri KONTROLLÜ DENEYLE doğrulandı (aynı içerik, iki yazım).

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **`denetim` · `sentez` · `motor` HİÇ KOŞMADI.** Zincirin bu ayakları bugüne kadar bir kez
  bile uçtan uca çalışmadı; ilk gerçek koşumları resmî tur olacak.
- **Bu oturumun KOD commit'leri bağımsız hakem GÖRMEDİ** ve henüz COMMIT EDİLMEDİ (573 satır,
  2 dosya). Önceki oturumun görülmemiş kod commit'leri zaten açık kalemdi; bu oturum onu
  BÜYÜTTÜ. Evi aşağıda.
- **R-35'in üçüncü ayağı (paket İÇERİĞİ) ölçülemez** — paket içeriği yok. Evi: Step 9 sonrası,
  Step 10 aktivasyonundan ÖNCE.
- **Backend SERVİSİ dağıtılmadı** (Task 18 Step 5·6·7). Evi: Task 19 Step 11'den ÖNCE.
- Test markası arayüzde GÖRÜLMEDİ.
- `ec_mechanical_sweep` bu oturumda KOŞULMADI.
- `ruff` / `pyright` ortamda YOK (düzenleyici uyarıları ayrı kalem — aşağıda).

# Risks

- **Zincirin ilk gerçek koşumu resmî tur olacak.** Prova önerildi, Eray gerek görmedi
  (kararı kayıtta). Bir şey tutmazsa resmî turda görülecek.
- **Kaynakların bulgu dengesi eşit değil:** Gemini 119 not / 3 çeşit (101'i `*` madde
  alışkanlığı), Claude 45 / 2 çeşit (42'si `hayir`→`hayır`), ChatGPT 1 / 1 çeşit. Denetçiler
  bu tabloyu görecek; mutabakat sinyali buna göre okunmalı.
- **Canlıda kurgu marka var** (`Deniz Kuyumculuk (TEST)`). Yeniden açılma anı: Task 20 kapanışı.
- **S-7 (critical, `accepted_risk`)** — Telegram uçları kimliksiz, iki workflow canlıda aktif.
- **S-6 (medium, kanıt boşluğu)** — takvim workflow'u SQL'i string birleştirmeyle kuruyor.
- **M-1 (yüksek)** — uygulama veritabanına KÖK kimlikle bağlanıyor.
- **`repo-public-exposed-live-credentials`** — depo public, anahtarlar açıkta.
- **İstemci/sunucu sürüm farkı** — sunucu PostgreSQL 18.3, host araçları 16.15.

# Notes For Claude/Codex

**Bu oturumda öğrenilenler:**

1. **Varyantı değil SINIFI kapat — ve deseni KAVRAMDAN türet.** İlk teklifim elle bulunan üç
   eksene yamaydı. Eray *"eski kaynak dosyalarında da var mı"* diye sorunca iki eksen daha
   çıktı (harf durumu, kaçışlı nokta) ve yaklaşım değişti: tek sadeleştirme kuralı + üretilmiş
   matris. Sonra aynı sınıfın DEĞER karşılaştırmasında iki sızıntısı daha bulundu.
2. **Prob ölçümü kirletir — beklenmedik sonuçta ÖNCE probu sorgula.** Kapı sonuçlarını iki kez
   yanlış okudum: çıkarma desenim mesajın içindeki tırnakta kesiliyordu ("ChatGPT 3, Claude 1"
   dedim; gerçek 17 ve 50'ydi). Ayrıca 42 test hatasını koda yazacaktım; iki takımı aynı anda
   koşturduğum için test veritabanı çakışmıştı.
3. **Kararı kullanıcıya taşıma — al, gerekçelendir, veto bırak.** H1 başlığı kararını Eray'a
   sordum; sözleşme sessizdi ama karar bana aitti. Eray itiraz etti: *"yapacağın işe başlatma"*.
4. **Önceki turun gerekçeli kararını sessizce ezme.** `_MADDE_RE` genişletmesi tur 11'in testle
   kilitlenmiş kararıyla çelişiyordu. İkisini de koruyan yol bulundu (say + not düş).
5. **Kendi düzeltmenin yan etkisini ölç.** Pinli sayı 102 → 107; kaynağı izlendi ve sessizce
   bump edilmedi.

**Codex çağrısı kurarken:** COMPANION + PROMPT çağıran kabukta; uzun turlar arka planda 1200 s;
çağrı sonrası `rc` + koşum sayısı + son cümle üçünü kontrol et; aynı oturumda ikinci uzun
turdan önce kotayı TAZE ölç.

# Evsiz kalan yok — kapanış sweep'i

- **Bu oturumun kod değişikliği (573 satır, 2 dosya) COMMIT EDİLMEDİ.** Ev: **oturum kapanışı,
  Eray onayıyla** — `/commit`. Onay alınmazsa dal kirli kalır ve sonraki oturum bunu devralır.
- **Bu oturumun kodu bağımsız hakem GÖRMEDİ.** Ev: mevcut YÜKSEK kalemle BİRLEŞİR
  (`7068a0b..HEAD` aralığı) — **Task 19 Step 11'den ÖNCE, servis dağıtımıyla aynı turda**
  `/review-claude-codex` + `/security-review-claude-codex`.
- **`pyright` tip uyarıları (8 adet, `list[str]` ↔ `list[str | _Mesaj]`).** Dokunduğum satırlar
  DEĞİL; ilk düzenlememden ÖNCE de vardı. Projenin kapısında pyright YOK.
  **Dürüst etiket: ÇÖZÜLMEDİ, DÜŞÜRÜLDÜ.** Yeniden açılma koşulu: pyright kalite zincirine
  eklenirse.
- **Gemini'nin 101 `*` maddesi ve Claude'un 42 `hayir` yazımı** borç DEĞİL — denetçilere giden
  kalite sinyalidir; kapı bildiriyor, karar sentez/denetim turunun.
