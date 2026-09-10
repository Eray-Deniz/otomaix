---
title: Denetçinin denetim tablosu TİPLİ okunsun (çoğunluk sınıfı düz yazıdan çıkarılmasın)
status: done
started: 2026-09-10
finished: 2026-09-10
last-touched: 2026-09-10
blocked-by: null
source_task: docs/active/sektor-bilgi-paketi-plan2/TASK.md
---

# Goal

Denetçinin **denetim tablosunu** tipli veriye çevirmek ve motorun yapısal çoğunluk kapısını o
tipli veriden beslemek. Bugün motor, denetçinin bir SÜTUNDA söylediği şeyi sentezin serbest
metninden yeniden çıkarmaya çalışıyor.

**Bu, `brief-sozlesmesi-kaynak-bolumu-makine-okunur` görevinin KARDEŞİDİR** — aynı sınıf, bir
katman aşağıda. Orada araştırma sözleşmesinin çıktı biçimi yapısal hâle getirilmişti; burada
sözleşme ZATEN yapısal, eksik olan bizim tipli okuyucumuz.

# Ölçülen durum (2026-09-09, Task 12 checkpoint 9 zinciri)

**Sözleşmeler yapıyı ZATEN istiyor:**

- `hakem-denetci-gorevi.md` ÇIKTI SÖZLEŞMESİ (1): denetim tablosu MARKDOWN TABLO, sekiz sütun —
  `no | alan | iddia-özeti | kaynaklar (1,2,3 hangileri) | sınıf | bayraklar | öneri | gerekçe`.
  Yani *"bu iddiayı hangi kaynaklar destekliyor"* ve `3-3`/`2-3`/`tekil`/`çelişki` sınıfı
  denetçinin KENDİ sütunlarında.
- `hakem-sentez-gorevi.md` ADIM 4: `"kanit": <standart format: "D1#<satır no>" / "D2#<satır no>"
  / "KAYNAK-N" / URL>`.

**Bizim tarafımızda eksik olan:** `auditors.validate_report` yalnız İKİ tabloyu tipli okuyor —
yeniden doğrulama envanteri (`_ENVANTER_BASLIK_HUCRELERI`) ve URL örneklemi
(`_URL_BASLIK_HUCRELERI`). Sekiz sütunlu denetim tablosu hiç ayrıştırılmıyor; `bolumler`
içinde serbest metin olarak kalıyor. Bu yüzden `engine._yeni_oge_cogunlugu` çoğunluğu
sentezin `kanit` düz yazısından saymak zorunda.

**Bunun bedeli ÖLÇÜLDÜ:** Task 12'nin kontrol noktasında aynı eksen DÖRT hakem turunda dört
ayrı sızıntı verdi (metnin herhangi bir yerinde desen → bileşen içinde sarmalanmış etiket →
komşu bileşene taşan düzyazı → gevşek URL kolu). Dördü de kapatıldı ve kapı bugün fail-closed;
ama kapının okuduğu şey hâlâ düz yazıdır.

# Kapanış yönü

1. Denetim tablosu tipli satırlara çevrilir (`no` satır kimliğidir; `kaynaklar` ve `sınıf`
   sütunları kapalı değer kümeleriyle doğrulanır).
2. `AuditReport` bu satırları taşır; motorun çoğunluk kapısı `kanit` metnini SAYMAYI bırakır ve
   denetçinin sınıf/kaynak sütununu okur.
3. `D1#<no>` / `D2#<no>` atıfları artık gerçekten ÇÖZÜLEBİLİR olur (bugün çözülemiyor — Task 11
   HANDOFF'unun açık kalemi).

**Dokunduğu yerler (ölçüldü):** `auditors.py` (Task 9'un indirdiği `AuditReport`/`validate_report`),
arayüz eki R5/R6 (tip alan listeleri), `engine._yeni_oge_cogunlugu` (Task 12). Yani küçük bir
tasarım turu ister — bu yüzden adım değil GÖREV.

# Yuva ve son tarih

**YUVA: Task 13'ten SONRA, Task 16'dan ÖNCE.** Task 16 motorun çağırıcısını kuruyor; tipli alan
ondan sonra gelirse o bağlantılar yeniden yazılır.

**SERT SON TARİH: Task 19 (kuyumculuk pilotunun resmî turu).** Sözleşme/çıktı tarafı pilottan
sonra değişirse araştırmalar ikinci kez ürettirilir — kardeş görevin gerekçesiyle aynı.

# Current Status

**BİTTİ (2026-09-10).** Üç kapanış maddesinin üçü de indi; iki bağımsız hakem turu koştu ve
bulguları işlendi.

**Commit'ler:** `31a4656` (dış sözleşme deposu, iki dosya + damga) · `7f27646` (tipli okuma +
koşu bağı) · `2c429b9` (hakem turu 1 — beş bulgu) · `4408dbe` (kapanış turu — kaynak tabanı +
tipli bayrak) · `9a603be` (Eray itirazı — bayrak katlaması + bayat belge).

**Ölçüm:** tam takım 3931 passed / 297,25 s / exit 0 (taban 3876 → +55 test). Yirmi altı yeni
kapının YİRMİ ALTISI ayrı ayrı mutasyonla kanıtlandı.

**Hakem turları:** Tur 1 → 5 bulgu (2 yüksek, 3 orta), beşi de kontrolörün KENDİ probuyla
doğrulandı ve beşi de kapatıldı. Kapanış turu → F3/F4/F5 CLOSED, F1/F2 INCOMPLETE + 3 yeni
bulgu (1 yüksek, 1 orta, 1 düşük).

**Kapanmayanlar — dürüst liste:**

- **Yüksek bulgunun kalan ayağı (atıf ADAYA bağlanmalı) ÇÖZÜLMEDİ.** Sözleşme revizyonu ister;
  yama değildir. **Evi: `docs/active/denetci-atif-aday-kimligi/` (proposed, sert son tarih
  Task 19).** Aynı eksen üç turda üç varyant verdi; yamamayı bırakma kararı bilinçlidir.
- ~~Düşük (kontrolörün ürünü): bayat docstring~~ — **KAPANDI (2026-09-10).** Eray'a "karar
  senin" diye taşınmıştı; taşınmamalıydı — kontrolörün kendi ürettiği yanlış belgeydi ve üç
  satırdı. Düzeltildi.
- ~~Düşük (önceden var olan): bayrak yazım katlaması~~ — **KAPANDI (2026-09-10).** `_katla`
  noktasız `ı`'yı katlamıyordu; sözleşmenin kendi yazımı `[marka-adı]`, `[kanal-bağımlı]`,
  `[kaynak-bağımlı]` hiçbir bayrak kontrolünde TANINMIYORDU — `[marka-adı]` gerçek marka adının
  pakete girmesini engelleyen bayraktır, yani boş bir kusur değildi. Bu da Eray'a karar diye
  taşınmıştı; taşınmamalıydı. Sınıf tek örnekle değil SÖZLEŞMEDEN ÜRETİLEN kümeyle kapatıldı
  (sekiz yazımın sekizi) + negatif kontrol kolu. Etki alanı ölçüldü (İlke 6): `_katla`'nın dört
  tüketicisinde de yön TEMKİNLİ — hiçbir kolda kapı gevşemiyor.
- **Uçtan uca koşum YOK.** Motor gerçek denetçi çıktısıyla hiç çağrılmadı; ilk gerçek ölçüm
  Task 19.

# Decisions Log

- **2026-09-09 — görev AÇILDI (Eray onayı).** Task 12'nin dört turluk kapanış zinciri sırasında
  kök sebep ölçüldü ve kod tarafında olduğu görüldü; kontrolörün ilk çerçevesi ("kalıcı çözüm
  sözleşmede") ÖLÇÜMLE DÜZELTİLDİ — sözleşme zaten yapısal.
- **2026-09-09 — kapsam sınırı:** bu görev motorun bugünkü fail-closed kapısını KALDIRMAZ; kapı
  tipli veri gelene kadar olduğu gibi kalır.
- **2026-09-10 — Eray kararı (1):** `ekle` kararında hakem satırına atıf ZORUNLU; çoğunluk artık
  hiçbir yerde düz yazıdan sayılmaz. Bedeli sentez sözleşmesinde küçük bir değişikliktir ve o
  pencere Task 19'a kadar açıktır.
- **2026-09-10 — Eray kararı (2):** hakemin `çelişki` dediği satıra dayanan ekleme OTOMATİK
  GİRMEZ; açık soru olarak operatöre çıkar.
- **2026-09-10 — Eray kararı (3):** `EngineInputs`'un koşu bağı AYNI turda kapatıldı (ayrı
  göreve taşınmadı). Motorun girdi alan kümesi AÇILMADI.
- **2026-09-10 — Eray talimatı (severity):** hakem bulgularından yalnız critical/high
  düzeltilir; orta/düşük raporlanır. Bu talimat, HANDOFF'taki "gerileme kontrolörün kendi
  ürünüyse `accepted_risk` yoktur" istisnasının ÜSTÜNE gelir — çelişkide severity yönetir.
  Tur 1'in üç orta bulgusu talimat gelmeden önce düzeltilmişti; geri alınmadı.
- **2026-09-10 — kontrolörün inisiyatifi (beyan):** denetim tablosunun ve envanter tablosunun
  BİREBİR başlık satırı dayatması Eray'ın kararı DEĞİLDİ; ayrıştırıcı başlığı tahmin etmek
  zorunda kalmasın diye eklendi ve aynı boşluk envanter tablosunda da vardı.

# Open Problems

- ~~`EngineInputs` paket/koşu bağı taşımıyor~~ — **KAPANDI (2026-09-10, Eray kararı: aynı turda
  kapat).** Bağ, motorun girdi alan kümesi AÇILMADAN kuruldu: kimlik `build_packet`'te mekanik
  rapor kümesinden TÜRETİLİR (`brief_doctor.kaynak_seti_sha`), `PacketRef` → denetçi çifti
  üzerinden TAŞINIR, `EngineInputs` yapımında KARŞILAŞTIRILIR. Ayrışma `ValueError`.
  Kimlik sıraya duyarlıdır ve üç eksende ayrışır (ad · içerik · eleme); dördü de üretilmiş
  matrisle ölçüldü. **Kapsam sınırı (dürüst etiket):** kimlik `run_id` TAŞIMAZ — motorun alan
  kümesinde karşılaştırılacak ikinci bir `run_id` taşıyıcısı yok. Kanıtlanan: "motora verilen
  mekanik kapı, denetçi paketini kuran kapıdır". AYNI kaynaklarla koşulmuş iki ayrı koşuyu
  ayırmaz. Ayrıntı: arayüz eki, "KOŞU BAĞI" bloğu.
