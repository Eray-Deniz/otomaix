---
title: Denetçinin denetim tablosu TİPLİ okunsun (çoğunluk sınıfı düz yazıdan çıkarılmasın)
status: proposed
started: null
finished: null
last-touched: 2026-09-09
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

# Decisions Log

- **2026-09-09 — görev AÇILDI (Eray onayı).** Task 12'nin dört turluk kapanış zinciri sırasında
  kök sebep ölçüldü ve kod tarafında olduğu görüldü; kontrolörün ilk çerçevesi ("kalıcı çözüm
  sözleşmede") ÖLÇÜMLE DÜZELTİLDİ — sözleşme zaten yapısal.
- **2026-09-09 — kapsam sınırı:** bu görev motorun bugünkü fail-closed kapısını KALDIRMAZ; kapı
  tipli veri gelene kadar olduğu gibi kalır.

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
