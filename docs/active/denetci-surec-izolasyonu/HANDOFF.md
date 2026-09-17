---
task: denetci-surec-izolasyonu
written: 2026-09-17
---

# Resume From

**Sıradaki iş: T5 — sahne dizininin yol kapısından geçtiğini ve kanonik pakete
DOKUNMADIĞINI teste bağlamak.** Faz 1 ve T4 indi; ayrıntı ve doğrulama `TASK.md`'de.

T5'in iki ayağı var:

1. **Yol kapısı.** Sahne dizini de takma ad / symlink / beklenmedik kök barındırmamalı.
   Bugün sahne `mkdtemp` ile açılıyor, yani yol güvenli görünüyor — ama bu ÖLÇÜLMEDİ,
   varsayım. Kanonik paket için `kok_yolunu_kapila` ve `PacketRef._rol_yollarini_kapila`
   aynı işi yapıyor; sahne için karşılığı yok.
2. **Kanonik pakete dokunulmuyor.** Alt süreç sahneye dosya yazsa/silsin bile kanonik
   rol dizininin ağaç parmağı DEĞİŞMEMELİ. Ölçüm için hazır yardımcı var:
   `_rol_agaci_parmagi`. Sahte araç sahneye dosya yazsın, sonra kanonik ağacın parmağı
   koşum öncesi/sonrası karşılaştırılsın.

**Paket kökü YERİNDE kalır** — `ARASTIRMA_DEPOSU_KOKU` değişmez, mevcut üç-kök testleri
aynen geçerli.

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest -q` → beklenen **4547 passed**.
⚠️ **Tek koşum.** İki pytest oturumu aynı anda koşarsa ortak test şablon veritabanını
birbirinden çekerler ve sahte hatalar üretirler.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, HEAD `1fa0c10`. Çalışma ağacı TEMİZ.

# Verification

**Bu oturumda KOŞAN komutlar ve çıktıları:**

| Ne | Komut | Sonuç |
|---|---|---|
| Tam takım (T4 öncesi) | `pytest -q` | 4538 passed / 332,14 s |
| Tam takım (T4 sonrası) | `pytest -q` | **4547 passed / 331,41 s** |
| Kutu tripwire'ı | `pytest tests/test_auditor_process_isolation.py -q` | 3 passed |
| T1 — sudo | `sudo -l -U codex` | "not allowed to run sudo" |
| T1 — gruplar | `id codex` | `1001(codex),100(users)` |
| T3 — kutulu ağ | kutulu kullanıcıda `codex exec` + `network_access=true` | canlı başlık `11:09:28 GMT`, sistem saati `11:09:33` → 5 sn; `id -un` → `codex` |
| T4 — mutasyon | altı mutasyon, her biri ayrı koşum | altısı da kırmızı döndü (dökümü `TASK.md` T4) |

**DENENMEYEN senaryolar — yeşil sayılmaz:**

- **Sahne GERÇEK denetçi araçlarıyla hiç koşmadı.** Dokuz testin hepsi zararsız bir Python
  alt süreciyle ölçüldü. `claude -p` ve `codex exec` sahnede koşarken kendi yapılandırmasını
  bulamayabilir — `HOME` hâlâ `/root`'u gösteriyor ve kutulu kullanıcı oraya giremez.
  **Evi: T8** (ortam beyaz listesi araç başına ayrışsın). Bu, T4'ün eksiği değil, T8'in işi —
  ama T4'ün yeşili "gerçek araç sahnede koşar" DEMEZ.
- **Ayrıcalık düşürme (T7) inmedi.** Alt süreç bugün hâlâ root koşuyor. Sahne kuruldu ve
  devredildi, ama kutu HENÜZ yürürlükte değil.
- **T3b'nin ağ-AÇIK varyantı bugün tekrar ölçülmedi** — kapanış turunda prob harness
  sınıflandırıcısına takıldı. Ayrıntı ve evi `TASK.md` Open Problems'da.
- **Zincirin `denetim` · `sentez` · `motor` ayakları hâlâ HİÇ koşmadı** (Plan 2'nin kendi
  durumu; bu görev onun önündeki engeli kaldırıyor).

# Risks

- **`SIGKILL` sahneyi geride bırakır.** Silme `finally`'de; süreç 9 sinyaliyle ölürse
  `finally` koşmaz ve `/tmp/denetci-sahne-*` diskte kalır. İçinde paketin kopyası vardır ve
  kutulu kullanıcıya aittir — yani o kullanıcı adına koşan bir sonraki süreç okuyabilir.
  **Bilinçli DÜŞÜRÜLDÜ, evi yok:** bakım işi kurmak için sebep zayıf (süreçleri biz
  öldürmüyoruz, servis henüz dağıtılmadı). **Yeniden açma koşulu:** diskte kalmış bir sahne
  görülürse, ya da servis kapsayıcıda koşmaya başlayıp `kill -9` rutin hâle gelirse.
- **Sahne `/tmp` altında.** Paket büyükse `/tmp`'nin doluluğu koşumu düşürebilir; boyut
  ÖLÇÜLMEDİ. **Yeniden açma koşulu:** gerçek bir tur disk hatasıyla düşerse.
- **`/home/codex/.ssh/authorized_keys`** duruyor (1 anahtar) — kutulu kullanıcıya SSH ile
  girilebilir. Bu görevin kapsamı dışında bırakıldı, `TASK.md` "Dokunulmayanlar".

# Notes For Claude

- **Sahne runner'ın içinde yaşıyor**, orkestrasyonda değil. Sahte runner kullanan testler
  sahneyi GÖRMEZ; sahne davranışı yalnız gerçek alt süreçle ölçülür. Yeni sahne iddiası
  eklerken bunu unutma — sahte runner'la yazılan bir sahne testi hiçbir şey ölçmez.
- **Ölçüm çocuğun gözünden yapılır.** Mevcut dokuz test, alt sürecin kendi bastığı değerlere
  bakıyor (nerede durduğu, ne okuyabildiği, klasörün sahibi/izni). Ebeveynin niyetini ölçen
  bir test bu dosyada yeri olmayan bir testtir.
- **Sahiplik ölçmek erişim ölçmek DEĞİLDİR.** Bu oturumda tam olarak bu hata yapıldı: sahne
  doğru kişiye aitti ama üstündeki geçici kök root'ta kalmıştı — sahiplik testi yeşil, dizin
  erişilemez. Kapanışı `sudo -u` ile zincirin tamamını deneyen test sağlıyor.
- **Mutasyon kanıtı YENİ kapıya yazılır.** Değişmemiş yardımcıları yeniden mutasyona sokma.

# Notes For Codex

Bu oturumda Codex hakem turu KOŞMADI. T15 review'ı Faz 3-4 bittikten sonra planlı.
