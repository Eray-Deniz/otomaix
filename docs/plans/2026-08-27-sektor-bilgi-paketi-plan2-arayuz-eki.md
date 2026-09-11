---
title: Sektör Bilgi Paketi — Plan 2/2 Arayüz Eki (BAĞLAYICI)
status: binding-addendum
date: 2026-08-30
revised: 2026-09-08
revisions: 6
binds_plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
source_spec: docs/specs/2026-08-21-sektor-bilgi-paketi.md
canonical_input: docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md
preflight_scan: .superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/preflight-scan.md
rulings: 14
---

# Plan 2 — Arayüz Eki: 14 hükmün sözleşme metni

## Bu belge neden var

Plan 2'nin 20 görevi tek tek uygulanır ve **her biri kendi brief'ine karşı** gözden geçirilir.
Bunun kaçınılmaz kör noktası şudur: **iki görevin birbirinden bağımsız olarak FARKLI icat
edeceği bir sözleşme, görev-başına review'a görünmez.** Task 8 `record_result`'ı yazarken
kendi brief'ine uyar, Task 13 `EngineResult`'ı yazarken kendi brief'ine uyar; ikisi
buluşmadığında hiçbir görev review'ı "burada bir uyuşmazlık var" diyemez — çünkü uyuşmazlık
görevlerin *arasındadır*, içinde değil.

Bu ek tam olarak o **paylaşılan sözleşmeleri** — imzalar, tip tanımları, kapalı değer
kümeleri, test sahipliği — **önden** sabitler; böylece iki görev ayrışamaz.

**BAĞLAYICIDIR: bu belge ile plan gövdesi çeliştiğinde BU BELGE GEÇERLİDİR.** Her hüküm,
geçersiz kıldığı plan satırlarını adıyla sayar. Ek hiçbir yeni kapsam açmaz; yalnız
kontrolörün 2026-08-30'da verdiği 14 hükmü test edilebilir sözleşme metnine çevirir.

**Kaynak hiyerarşisi:** spec girdisi (`docs/research/2026-08-21-...-spec-input.md`) spec'e
ÜSTÜNDÜR; çeliştikleri yerde girdi satırı alıntılanır ve o kazanır.

**Okuma kuralı (İlke 8):** bu belgenin gövdesi teknik seviyedir — doğrulaması Eray onayı
değil, review zinciri + adı konmuş testlerdir.

**Alıntı kuralı (fix turu 1, 2026-08-30).** Bu ekteki HER `plan <satır>` · `<dosya>:<satır>` ·
`spec-input satır <n>` alıntısı fix turu 1'de **tek tek yeniden ölçüldü** ve plan gövdesinin
**bu turdaki** hâline göre güncellendi (plan gövdesine bu turda görev-başına "Arayüz eki
bağlar" satırları eklendiği için tüm satır numaraları kaydı). Satır çapası kırılgan olan
yerlerde çapa **sembole · test adına · başlığa** çevrildi (ör.
`sector_package_lifecycle.py::_require_evidence`, `Task 6 Produces → sector_package_runs`).
**Plan gövdesi bir daha düzenlenirse bu numaralar yeniden kayar** — bu bilinen ve kabul
edilen bir sınırdır; kayma riski taşımayan çapa sembol adıdır, satır numarası değildir.

## Revizyon kaydı — 2026-09-08 (Task 8 dispatch'inden ÖNCE)

> **R-E ve R-F dispatch'ten SONRA eklendi** (checkpoint kapanış-doğrulama turları,
> bağımsız hakem bulguları). Başlıktaki "dispatch'inden ÖNCE" yalnız R-A…R-D için doğrudur.

Ek 2026-08-30'da kapandı; aradan Task 3 · 4 · 5 · 6 · 7 geçti ve **kod dört yerde ekin
metnini geride bıraktı.** Task 8'in brief'i bu hükümleri HARFİYEN kopyaladığı için, yürütücü
uyuşmazlığı kendi başına yorumlasaydı ekin bağlayıcılığı fiilen kalkardı. Dördü de ölçülerek
kapatıldı; **hiçbiri yeni kapsam açmaz.**

| # | ne değişti | yön |
|---|---|---|
| **R-A** | Hüküm (a)'nın **ad kümesi**: "kullanılan TEK ad `identity.canonical_sha`" → `identity`nin ÜRETİLMİŞ public yüzeyi | metin koda uyarlandı |
| **R-B** | Ayak (d) düzyazısı ile bağlayıcı SQL bloğunun **çelişkisi**: SQL bağlar (`BEFORE UPDATE`); yanlış emsal ve yanlış satır alıntısı düzeltildi | metin SQL'e ve 036'ya uyarlandı |
| **R-C** | **Onay mührünün yüklemi** yazılı DEĞİLDİ: dolu → BOŞ geçişinin reddedildiği (036'da uygulanmış) kural metne alındı | metin koda uyarlandı |
| **R-D** | Aktör kapısının **tanım yeri**: `sector_package_lifecycle._require_actor` bir yeniden-dışavurumdur; tanım `package_events.require_actor` | metin koda uyarlandı |
| **R-E** | A4'ün **dördüncü koşulu** yaşam döngüsü modülünde koşabilir hâle getirildi: beklenen kanonik imza yalnız-anahtar bir parametreyle ÇAĞIRANDAN gelir; import kenarı AÇILMAZ | hüküm korundu, yol değişti |
| **R-F** | Kanıt yükünün **ŞEKİL kapısı**: `acik_sorular` YALNIZ `list`/`tuple` (boş olanlar dâhil), jsonb tasdikleri YALNIZ `Mapping`/`None`; kalan her şey `EvidenceMintRefused` — ekin ÖRNEK kodu `len(...)`'i şekil doğrulamadan çağırıyordu | hüküm DARALTILDI (fail-closed) |

**R-E (2026-09-08) — hakem bulgusunun kapanışı.** Task 8'in ilk yazımı A4 kapısının dördüncü
koşulunu (tasdikteki imzanın kanonik madde kümesi imzasına birebir eşitliği) *"AÇIK-3 import
yasağı yüzünden burada koşamaz"* diyerek DÜŞÜRMÜŞTÜ ve gerekçeyi *"aktivasyon kapısı onu
ayrıca reddeder"* diye yazmıştı — **o kapı Task 15'e ait ve henüz YOK.** Bağımsız hakem bunu
**yüksek** olarak buldu; kontrolör ölçerek doğruladı: `activate_package` ilgili booleanlara
olduğu gibi güveniyor, jeton tüketimi yok. **Kapanış import kenarını AÇMADAN yapıldı** —
beklenen imza `activation_evidence_payload`'a yalnız-anahtar, varsayılansız bir parametre
olarak girer ve tek çağıran (`runs.mint_evidence_token`) kanonik sabiti geçer; kaynağın
kapalılığı düzyazıyla değil, çağrı yerindeki ifadeyi okuyan bir AST kapısıyla ölçülür.
Aynı turda ikinci bir açık daha kapandı: onay anlık görüntüsü YOKKEN "açık soru sayısı 0"
yazılıyordu; artık jeton basımı REDDEDİLİR.

**R-F (2026-09-08) — hakem bulgusunun kapanışı, checkpoint fix turu 2.** R-E eksik anlık
görüntüyü ve eksik anahtarı kapattı ama değerin **ŞEKLİNİ** doğrulamadan `len(...)` çağırmayı
sürdürdü. Kontrolör ölçtü: `{"acik_sorular": ""}` · `{}` · `set()` · `()` şekillerinin
DÖRDÜ de `open_questions_count=0` üretiyordu — sıfır, K-71 kapısını GEÇİREN tek değerdir;
skaler şekiller (`int`/`bool`/`None`/`float`) ise alan-DIŞI bir `TypeError` fırlatıyordu, o da
bir alan reddi DEĞİLDİR. **Ek bu noktada kodun ÖNÜNDE değil, ARKASINDA kaldı:** bağlayıcı örnek
kod tam olarak korumasız `len(...)`'i yazıyor — İKİ yerde: `writeback.activate_from_snapshot`
örneğinde ve `activation_evidence_payload`'ın anahtar listesinde. (Çapa SEMBOL adıdır, satır
numarası DEĞİL — bu belgenin kendi kuralı; ikisine de yerinde R-F işaretçisi kondu.) Sapma
DARALTMA yönündedir ve meşrudur; hüküm olarak işlenir:

* `acik_sorular` için KABUL kümesi KAPALI ve NOMİNALDİR: `list` ve `tuple`, **boş olanlar
  dâhil** — `[]` ve `()` MEŞRUDUR ("açık soru yok" demektir) ve pozitif kontrolleri vardır.
  `tuple` de zorunludur çünkü `VerifiedRun.__post_init__` yükü `identity.donmus`'tan geçirir ve
  `donmus` kuralı (2) `list|tuple → tuple` yazar: DONMUŞ yolda değer `tuple`, HAM yolda `list`
  gelir. Kalan HER şey `EvidenceMintRefused`.
* Aynı şekil disiplini **eşleme alanlarına** da uygulanır: `approval_snapshot` ·
  `katman1_attestation` · `readiness_attestation` YALNIZ `Mapping` (tasdiklerde ayrıca `None`,
  ki kapıyı KAPATIR). Gerekçe ölçüldü: `"x" in "xy"` alt dize, `"x" in {"x"}` küme üyeliğidir —
  ikisi de `in` kapısını geçer, ardından gelen `[...]` alan-dışı `TypeError` fırlatır.
* **`Sized`/`Iterable`/`len()` var-mı tabanlı GEVŞEK kontrol YASAKTIR** — `str` ve `dict` o
  kontrolü geçer, açık aynen kalırdı. Negatif kontrolü test matrisindedir.
* Süpürme aynı turda koştu: aynı okuma `rollback_evidence_payload`'ın
  `hedef_kosu.katman1_attestation` dalında da vardı, o da kapatıldı.

**R-F'nin erişilebilirlik sınırı — dürüst etiket.** `approval_snapshot` kolonu 036'da şekilsiz
`JSONB`'dir (yalnız değişmezlik tetikleyicisi var, CHECK yok) ve **bugün ÜRETİM YAZICISI
YOKTUR** — yazıcı Task 14'ün kalemidir. Yani sınıf bugün canlıda tetiklenemez; kapatılma
sebebi, Task 14 yazıcısının bu şekli üretmesi hâlinde kanıtın SESSİZCE genişlemesidir. Tehdit
modeli: girdi araştırma çıktısıdır — ÖZENSİZ/BAYAT olabilir, SALDIRGAN değildir.

**R-A'nın ölçümü (2026-09-08).** `sector_package_lifecycle.py` `identity` modülünden İKİ ad
kullanıyor — `validate_decision_log` ve `check_unit_integrity` — ve `canonical_sha`'yı HİÇ
ÇAĞIRMIYOR; 645 satırda tek bir hash hesabı yok. Yani hüküm yalnız "fazla ad var" diye değil,
**dayandığı varsayım yüzünden de** kodla uyumsuzdu. Sebep meşrudur: Task 3'ün şema kapısı
`insert_draft` içinde koşar ve kuralın İKİNCİ BİR KOPYASI yazılamaz. Bu yüzden daraltılan ad
sayısı değil, **kenarın kendisidir** (tek import, yaprak hedef, başka modül yok).

**Bu revizyonun kendi sınırı — dürüst etiket.** Dördü de **bağımsız hakem GÖRMEDİ**; Task 8
dispatch'i öncesi kontrolör kararıyla yazıldılar. Evleri var: final incelemenin tabanı
`a806e29` olduğu için bu commit de oraya kendiliğinden girer.

---

## Revizyon kaydı — 2026-09-11 (Task 18 dispatch'inden ÖNCE)

Ek en son 2026-09-08'de revize edildi; aradan Task 8 · 10 · 11 · 13 · 14 · 16 · 17 geçti.
**Kod YEDİ yerde ekin metnini geride bıraktı.** İkisi hakem turlarında, **BEŞİ bu turun
tarama koşumunda** bulundu.

**Neden tarama, neden spot değil (İlke 6 — blast radius).** Bilinen sapmalar dört AYRI
hakem turunda TESADÜFEN çıkmıştı. Onları üreten süreç ("kod ekin önüne geçer, ek
güncellenmez") **süreç-İÇKİNDİR**: ekin beyan ettiği BÜTÜN yüzeyler aynı risk altındadır.
Bu sınıfta spot kontrol final karar üretemez, o yüzden ekin ```python bloklarında beyan
ettiği **65 yüzeyin (32 blok) HEPSİ** koddaki karşılığıyla imza ve alan kümesi düzeyinde
karşılaştırıldı.

**Taramanın ölçülmüş sınırı — DÜRÜST ETİKET, liste TAM DEĞİLDİR.** Kapsanan: kod
bloklarında beyan edilen 65 yüzey. **Kapsanmayan:** ekin **düz yazıda** beyan ettiği
yüzeyler. `readiness.evaluate` tam olarak böyle bir yüzeydir ve taramayla DEĞİL, hakem
turuyla bulunmuştu. Düz yazı kolu için güvenilir bir üretilmiş kontrol yazılamadı (serbest
metinden imza çıkarmak yanlış-pozitif ile kaçırma arasında salınıyor); o kol için
**sapma olmadığı İDDİA EDİLMEZ**.

| # | ne değişti | yön | nasıl bulundu |
|---|---|---|---|
| **R-G1** | `BulguIzi` ÜÇ alanlıydı; kodda DÖRT (`kontrol`) | metin koda uyarlandı | hakem turu (Task 14) |
| **R-G2** | `ChecklistItem` ÜÇ alanlıydı; kodda DÖRT (`baslik`) | metin koda uyarlandı | **bu turun taraması** |
| **R-G3** | `check_snapshot_agreement` tek mühür parametresi taşıyordu; kodda İKİ (`expected_kaynak_sha`) | metin koda uyarlandı | **bu turun taraması** |
| **R-G4** | `verify_pin` iki parametreliydi; kodda üçüncü bir anahtar-kelime parametresi var (`snapshots`) | metin koda uyarlandı | **bu turun taraması** |
| **R-G5** | `_consume_provenance` `(table, evidence, keys)` alıyordu; kodda `(evidence, *, hedef)` | metin koda uyarlandı | **bu turun taraması** |
| **R-G6** | `readiness.evaluate(db)` koşu kimliği almıyordu; kodda alıyor | metin koda uyarlandı | hakem turu (Task 17) |
| **R-G7** | AÇIK-2 kararı "A — `geri-al` KALIR" diyordu; komut KALDIRILDI | **KARAR DEĞİŞTİ** (Eray, 2026-09-11) | yürütme ölçümü |
| **R-G8** | `policy_report` kolonuna yazılan **kalıcı yük şekli** ekte SAHİPSİZDİ (`as_payload`/`from_payload` hiç geçmiyordu) | eksik sözleşme eklendi | `BulguIzi` kaydının ikinci ayağı |
| **R-G9** | Hazırlık onayı dayandığı kanıt kümesine BAĞLI DEĞİLDİ (checkpoint 14 · F1, yüksek) | **YENİ HÜKÜM** — kapı eklendi (Eray kararı, 2026-09-11) | hakem turu, iki turda aynı eksen |

**R-G8 taramanın ürünü DEĞİLDİR** — tarama yalnız ekte ADI GEÇEN yüzeyleri kodla
karşılaştırır, ekte HİÇ GEÇMEYEN bir yüzeyi göremez. Bu kalem `BulguIzi` açık sorununun
ikinci ayağından geldi ve **aynı sınıfın taramayla kapatılamayan kolunu gösterir**: eksik
beyan, yanlış beyandan farklı bir kusurdur.

**R-G1…R-G6 ve R-G8 yeni kapsam AÇMAZ** — altısı da kodun ZATEN yaptığını ekin metnine yazar; kapı
kümesi hiçbirinde büyümez (R-G3 ve R-G4 bunu açıkça söyler: taşıma/ölçüm biçimi değişir,
kapı sayısı değişmez).

**R-G7 bir metin uyarlaması DEĞİLDİR — bağlayıcı bir kararın tersine dönmesidir.** Tam
gerekçesi ve yeniden açılma koşulu AÇIK-2 bölümünün başındaki blokta yazılıdır.

**R-G9 de metin uyarlaması değildir — YENİ bir bağlayıcı kapıdır.** Onay, gördüğü kanıt
kümesinin parmak izini tasdike YAZAR; aktivasyon aynı izi yeniden hesaplar ve ayrışma varsa
paket AKTİVE EDİLMEZ. Eray'a sorulan şey mekanizma değil risk tercihiydi (İlke 8): reddedilen
iki seçenek *"uyar ama devam et"* ve *"bugünkü hâli Task 20'ye taşı"*dır.

**R-G9'un ÖLÇÜLMÜŞ sınırı — kapanan ve KAPANMAYAN yarı.** Açık sorunun tarif ettiği arıza
(*"onaydan SONRA DÜŞEN bir satır"*) canlı ölçümle **ulaşılamaz** çıktı: ham artefakt tablosu
veritabanı düzeyinde salt-eklemedir (`sector_research_artifacts_append_only`, `BEFORE DELETE
OR UPDATE`). Erişilebilir yönler EKLEME ve koşu satırının sekiz prob-kolonunun
GÜNCELLENMESİDİR — parmak izi ikisini de kapsar. **Kapanmayan yarı:** `attest_readiness` prob
SONUÇLARINI hâlâ görmez, çağıranın madde kümesi iddiasını yazar; probları yazıcıya koymak
`runs` → `readiness` bağımlılığı demek olurdu ve R9 yasaklar. Gerçek kapı `hazirlik-onayla`
komutundadır ve **üretimde başka çağıran olmadığı artık tekrar koşulabilir bir testle
pinlenmiştir** (`test_attest_readiness_URETIM_cagirani_YALNIZ_cli_onay_yoludur`); ikinci bir
üretim çağıranı eklenirse test kırılır. Bu bir kapanış DEĞİL, adı konmuş ve ölçülen bir
sınırdır.

**Bu revizyonun kendi sınırı — dürüst etiket.** Yedisini de **bağımsız hakem GÖRMEDİ**;
kontrolör ölçümüyle yazıldılar. **Evleri var:** dış araştırma sözleşmesi turunun sonundaki
hakem turu ve dal kapanışındaki final inceleme (tabanı `a806e29`, bu commit oraya
kendiliğinden girer).

**Sınıfın kendisi KAPANMADI — yalnız bugünkü örnekleri kapandı.** Ek ile kodun sessizce
ıraksaması bir SÜREÇ kusurudur; bu revizyon onu üreten süreci değiştirmez. Kalıcı kapanış,
ekin beyan ettiği yüzeyleri koda karşı ölçen ÜRETİLMİŞ bir kapıdır (bugünkü tarama elle
koşuldu ve düz yazı kolunu kapsamıyor). **Bu, kontrolörün önerisidir, ölçülmüş bir çözüm
DEĞİLDİR** — kapının yanlış-pozitif maliyeti ölçülmedi ve düz yazı kolu için yazılabilir
olduğu GÖSTERİLMEDİ.

---

## Revizyon kaydı — 2026-09-11/b (dış sözleşmenin KOD uyarlaması)

Aynı gün ikinci revizyon. Öncekinden farkı YÖNÜDÜR: o revizyon **ekin metnini koda**
uyarlıyordu (kod ilerlemiş, ek geride kalmıştı); bu revizyon **kodun sözleşmeye** uyarlanmasını
kaydeder. Dış araştırma sözleşmesi `12beec1` ile üç noktada değişti ve kod o gün uyarlanmamıştı;
ağaç bilerek KIRMIZI bırakılmıştı (iki sapma alarmı) — yarım uyarlama, kırmızı alarmdan daha
kötü bir sessiz ara durum üretirdi.

| # | ne değişti | yön | kapı büyüyor mu |
|---|---|---|---|
| **R-H1** | Bölüm C tablosu `no` sütunu kazandı; `C_TABLOSU_SUTUNLARI` YEDİ üyeli | sözleşme koda uyarlandı | **EVET** — `no` biçimi ve tablo boyu DİZİSİ (tekrarsız, boşluksuz) |
| **R-H2** | `DoctorReport` `iddialar: tuple[CIddia, ...]` taşır; `run` onu belgeden ÜRETİR | YENİ taşıyıcı | EVET — yapıcı kimlik değişmezlerini zorlar |
| **R-H3** | Denetim tablosu DOKUZ sütun (`kaynak-iddialari`); `AuditRow` aynı adlı alanı taşır | sözleşme koda uyarlandı | **EVET** — biçim + `kaynaklar` ile ÇİFT YÖNLÜ tutarlılık |
| **R-H4** | KAYNAK PROFİLİ düz yazıdan TABLOYA döndü; `AuditReport.kaynak_profili` | sözleşme koda uyarlandı | **EVET** — `resmi` kapalı kümesi, numara tekrarsızlığı, dolu not |
| **R-H5** | Motor atfı ALAN düzeyinden İDDİA düzeyine taşıdı; bağ İKİ UÇLU | YENİ kapı | **EVET** — üç yeni uygulanmama sebebi |
| **R-H6** | K-126 tek-kaynak istisnası AÇILDI (iki ayağı da artık ölçülüyor) | kapı DAVRANIŞI değişti | EVET — istisna artık İŞLER |
| **R-H7** | `kaynak_seti_sha` mührü `iddialar`ı da kapsar | mühür GENİŞLEDİ | EVET |
| **R-H8** | `EngineInputs` `takvim_kategorileri` alanını kazandı; K-03'ün tür↔kategori ayağı ÇALIŞIR | **R5 ALAN KÜMESİ REVİZYONU** | EVET — çatışma karar günlüğüne NOT olarak yazılır (blok DEĞİL) |

**R-H5 ve R-H6 metin uyarlaması DEĞİLDİR — motorun davranışını değiştirirler.**

* **R-H5** aynı eksenin ÜÇ hakem turunda ürettiği üç varyantı kapatır: yetkilendirme bağı
  ALAN düzeyindeydi, yani `kanca_kaliplari` hakkındaki HERHANGİ bir denetçi satırı o listeye
  giren HERHANGİ bir kalıbı yetkilendirebiliyordu. Varyant yamamak bırakıldı; üç beyan da
  (araştırma · denetçi · sentez) aynı üst kaynağa — iddia NUMARASINA — çivilendi. Bağ iki
  uçlu aranır çünkü tek uçlu bir bağ KENDİNİ ONAYLAR: sentez beyanını da denetçi beyanını da
  aynı model yazar, üçüncü taraf (mekanik ayrıştırıcı) olmadan zincir kapanmaz.
* **R-H6** bir AND koşulunun kapalı kalan yarısını açar. İstisna bugüne kadar KAPALIYDI ve
  bu bilinçliydi: resmîlik yargısı serbest düzyazıya gömülüydü, motor onu göremiyordu. Kök
  çözüm yine KODA değil SÖZLEŞMEYE yapıldı — motor hâlâ hiçbir şey ÇIKARSAMAZ, okur.

**R5 alan kümesi (`EngineInputs`) DEĞİŞMEDİ — ve bu ölçüldü.** İddia evreni yeni bir alandan
değil, `mekanik_eleme.raporlar`dan türetilir; kaynak numarası KONUMDAN gelir ve bu
`_kabul_edilen_etiketler`in kuralının AYNISIDIR. K-126'nın resmîlik ayağı da yeni alan
istemez: yargı `denetci_envanterleri` içindeki raporların kendi profil tablosunda taşınır.

**Görev B bağının ölçülmüş inceliği.** Bölüm C'nin `alan/dönem` hücresi bir dönem için DÖNEM
ADIDIR (araştırmanın kendi yazımı: `Sevgililer Günü`), karar satırı ise `ozel_gun` taşır ve
dönemi `oge_yolu`nun slug'ında saklar. Bağ bu yüzden O DÖNEME kurulur, `ozel_gun` alanına
DEĞİL — alana kurulsaydı kapatılan sınıf bir basamak aşağıda aynen sürerdi (herhangi bir dönem
iddiası herhangi bir özel günü yetkilendirirdi). Normalizasyon kuralı kopyalanmaz:
`normalize_special_day_key` tek kaynaktır.

**R-H8 — K-03 kategori ayağı: neden TAM EŞLEME yazılmadı.** Sistem takvimi `religious` ·
`national` · `commercial` yazıyor (yerel veritabanında sayıldı: 9 · 8 · 5; ölçüm komutu
`SELECT category, count(*) FROM social.public_holidays GROUP BY 1`), paket tür etiketi ise
`kutlama` · `anma` · `ticari-firsat` · `karma`. İki sözlük arasındaki TAM karşılık ne spec'te
ne spec girdisinde yazılıdır ve UYDURULMADI — uydurulan bir eşleme ölçülmemiş bir kuralı
kapıya çevirirdi (İlke 9(3)).

Kural (*"ikisi çeliştiğinde paket kazanır, çatışma kayda geçer"*) yalnız iki sözlüğün GERÇEKTEN
paylaştığı eksende uygulanır: **ticari mi, değil mi.** `religious`/`national` ayrımının paket
sözlüğünde karşılığı YOKTUR, dolayısıyla orada çelişecek bir şey de yoktur. Karşılaştırma ÇİFT
YÖNLÜDÜR (kural yön seçmez): sistem `commercial` ↔ paket `kutlama`/`anma` da, sistem
`religious`/`national` ↔ paket `ticari-firsat` da çatışmadır. `karma` iki ekseni birden taşıdığı
için hiçbir kategoriyle çelişmez. Kategorisi BİLİNMEYEN gün hakkında hiçbir şey iddia edilmez
(etiketsiz gün davranışı K-15(a) kapsamında AÇIKTIR ve normatifleştirilmez).

**Üstünlük yönü değişmedi — bu bir BLOK DEĞİLDİR.** Motor içeriği değiştirmez; çatışmayı karar
günlüğüne `tur-kategori-catismasi` sınıfıyla NOT olarak yazar. Ölçüm iki ayaklıdır ve testte
ikisi birden aranır: not ÜRETİLİR **ve** uygulanmama listesi BOŞ kalır.

**İlk öneri KURALDAN DARDI ve Eray düzeltti (2026-09-11).** Kontrolör "yalnız riskli yönü
kaydet" önermişti (sistem dinî/ulusal ↔ paket ticari); kural *"ikisi çeliştiğinde"* der, "riskli
yön çeliştiğinde" demez. Risk filtresini kuralın üstüne koymak, kuralın kendisini daraltmaktı.

**Bu revizyonun kendi sınırı.** Yedi kalemin hiçbirini bağımsız hakem GÖRMEDİ. **Ev:** dış
araştırma sözleşmesi turunun sonundaki tek hakem turu (Eray'ın "hafif yol" kararı) ve dal
kapanışındaki final inceleme.

---

## R1 — Koşu klasörleri pinlenen dış depoya ASLA commit edilmez

**Kusur (plan satırları):** `runs.run_folder(run_id) -> <arastirma-deposu>/kosu/<run_id>/`
(plan 1011) her koşunun artefaktını, pin kapısının **commit sha**'sını karşılaştırdığı depoya
(plan 423-426) yazar; Task 18 Step 4 o depoyu sabit bir commit'e getirir (plan 2007), Task 19
klasörü orada yaratır (plan 2034). "Monorepo'ya düzenlenebilir ikinci kopya ALINMAZ"
kısıtı (plan 76-78) ile birlikte okununca plan, klasörün commit edilip edilmeyeceğini
hiç söylemez.

**Ölçüm (2026-08-30, `verify_pin`'in plan metni, plan 423-426):** kapı kümesi TAM OLARAK
dörttür — dosya yok · hash uyuşmuyor · commit uyuşmuyor · depo dizini yok. Çalışma ağacının
temizliği **kontrol edilmez** ve doğrulama açıkça salt-okunurdur (plan 426). Yani izlenmeyen
koşu klasörü yazmak pini DÜŞÜRMEZ; onu **commit etmek** düşürür (HEAD kayar → commit
uyuşmazlığı → fail-closed).

**Kural (kontrolör):** koşu klasörü kanonun koyduğu yerde KALIR — spec girdisi satır 2318:
*"Yeniden üretimde sorun ortadan kalkar — **brief kopyası koşu klasörüne yazılır** (**K-17**,
Bölüm 7.2)."* Bu satır kanoniktir ve spec'in sessizliğini yener. `kosu/` dış deponun
`.gitignore`'una **Task 2'de** eklenir (o görev zaten orada commit atıyor), ve `verify_pin`
açık bir **NEGATİF invariant** kazanır.

**Bağlayıcı sözleşme:**

```python
# apps/social/backend/app/services/sector_pipeline/contracts.py  (Task 1)
def verify_pin(
    pin: ContractPin,
    repo_root: Path,
    *,
    snapshots: Mapping[str, bytes | None] | None = None,   # R-G4 (2026-09-11)
) -> list[str]: ...
```

`verify_pin` invariantları — pozitif küme DEĞİŞMEZ (dört kapı, plan 423-426), üstüne
**negatif invariant** eklenir:

- **Kirli çalışma ağacı TEK BAŞINA pini DÜŞÜRMEZ.** Manifestte adı geçmeyen hiçbir dosya
  veya dizin — izlenmeyen `kosu/<run_id>/` klasörleri dâhil — uyuşmazlık üretmez.
- Kapı yalnız şunlara bakar: (a) pinlenen ÜÇ dosyanın (`_SABLON.md` ·
  `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`) sha256'sı, (b) dış deponun HEAD
  commit sha'sı, (c) depo dizininin varlığı.
- `verify_pin` `git status`/`git diff` çağırmaz ve dış depoda hiçbir şey değiştirmez.
- **`snapshots` KAPI EKLEMEZ (R-G4, 2026-09-11)** — kapı kümesi TAM OLARAK dört kalır;
  yalnız kapının HANGİ BAYTLARI ölçtüğünü değiştirir. Çağıran bir sözleşme dosyasını
  zaten okuduysa o anlık görüntüyü verir ve hash kapısı diskten İKİNCİ bir okuma
  yapmadan aynı baytları ölçer. Gerekçe ölçülmüş: doğrulanan bayt ile kullanılan bayt
  iki AYRI okumadan gelirse aradaki pencerede dosya değişebilir ve pinlenmemiş içerik
  doğrulanmış sayılırdı. Anlık görüntü `None` ise dosya okunamamıştır — ikinci kapı düşer.
- Pinlenen üç dosyanın baytı değişirse kapı zaten (a) ile düşer; bu **kirlilik değil içerik
  drift'idir** ve iki hâl karıştırılmaz.

Dış depo `.gitignore` kalemi (Task 2, `/root/otomaix-sosyal-medya-arastirmasi/.gitignore`):

```
kosu/
```

**Etkilenen görev · geçersiz kılınan satırlar:** Task 1 (invariant listesi plan 422-426
üzerine EKLENİR) · Task 2 (Files listesine `.gitignore` eklenir; plan 450-455) ·
Task 8 `run_folder` yeri DEĞİŞMEZ (plan 1011 geçerli kalır) · Task 18 Step 4 / Task 19
belirsizliği (plan 2007 · 2034) bu hükümle kapanır.

**Kanıt testi · sahibi:**
- `test_verify_passes_with_dirty_external_worktree` — sahte depoda pinlenen üç dosya
  eşleşiyor, yanında izlenmeyen `kosu/<run_id>/x.md` var → `verify_pin` **boş liste** döner.
  **Sahip: Task 1**, `tests/test_contract_pin.py`.
- `test_external_repo_gitignores_run_folder` — gerçek dış deponun `.gitignore`'u `kosu/`
  satırını taşır. **Sahip: Task 2**, `tests/test_contract_pin.py` (Step 5'te eklenir).

---

## R2 — Her NOT NULL kolonun ve her kapı kolonunun ADI KONMUŞ bir üreticisi olur

**Kusur (plan satırları):** (a) `kosu_turu text NOT NULL` (plan 793) ama
`open_run(db, *, sector_id, run_id, parent_run_id=None)` (plan 986) böyle bir parametre
taşımıyor; (b) `durum='tamamlandi'`, `load_verified_run`'ın **1. kapısıdır** (plan 341) ama
onu yazan bir üretici yok; (c) `engine_version` · `engine_config_sha` · `content_sha` ·
`decision_log_sha` · `policy_report` · `engine_diff` koşu satırına yalnız isimsiz
`**report_fields` üzerinden ulaşıyor (plan 1001-1002). Bu, planın `barrier_report` için
zaten uyguladığı düzeltmenin (plan 1003-1007) kardeşlerine **süpürülmemiş** hâlidir.
(d) `engine_version`/`engine_config_sha` `load_verified_run`'ın 3. ve 4. kapısı ve
`affected_packages`'ın kapalı dörtlüsünün yarısı (plan 341-344 · 1024-1029) olmasına rağmen
`EngineResult`'ta YOK (plan 1469-1471) ve `engine_config_sha`'yı (K-97) hesaplayan yer
adlandırılmamış. **(e) Fix turu 1 bulgusu (yüksek, KABUL):** `record_result` HER sonuçta
`policy_report` istiyor (Task 6 Produces → `sector_package_runs.policy_report jsonb`, K-95),
oysa `EngineResult` yalnız `kararsizlar` taşıyor (plan 1469-1471) ve `policy_report`'u ÜRETEN
bir **tip ya da fonksiyon hiçbir görevde adlandırılmamış**. Bu, R2'nin kapatmak için var
olduğu **isimsiz-üretici** sınıfının ta kendisidir: Task 16'nın motor çağırıcısı serbest bir
sözlük İCAT etmek zorunda kalırdı ve iki görev ayrışırdı.

**Kural (kontrolör):** `open_run` zorunlu `kosu_turu` parametresi kazanır (kapalı küme).
`record_result` **yazdığı HER alanı adı konmuş, tipi kapalı bir kaynaktan** alır ve
`**report_fields` SİLİNİR: motor türevi alanların TAMAMI tek bir `EngineResult`
parametresinden gelir, serbest sözlük hiçbir yerde kalmaz. `durum='tamamlandi'`'yi yazan
`record_result`'tır — açıkça yazılır. `engine_version` + `engine_config_sha`
`EngineResult`'a eklenir; hesaplandıkları yer adlandırılır. **`policy_report` KAPALI bir
tip kazanır (`PolicyReport`), tek üreticisi `decide`'dır ve `record_result` onu
`EngineResult`'tan OKUR — ayrı bir parametre olarak KABUL ETMEZ.** `kararsizlar`
`EngineResult`'tan ÇIKAR; tek yeri `policy_report.kararsizlar`'dır (iki kaynak yasağı).

**Bağlayıcı sözleşme:**

```python
# runs.py  (Task 8)
KOSU_TURLERI: tuple[str, ...] = ("ilk", "periyodik", "duzeltme")     # KAPALI
DURUMLAR:    tuple[str, ...] = ("calisiyor", "tamamlandi", "tamamlanmadi")  # KAPALI
# SONUCLAR burada TANIMLANMAZ: motor sözleşmesine aittir ve `engine_contract.py`'de
# (yine Task 8) durur — aşağıya bakınız. `runs.py` onu import eder, ikinci kopya YOKTUR.

async def open_run(
    db,
    *,
    sector_id: UUID,
    run_id: str,
    kosu_turu: str,                 # KOSU_TURLERI içinden; varsayılan YOK
    parent_run_id: str | None = None,
) -> UUID: ...
```

- `open_run` satırı `durum='calisiyor'`, `sonuc=NULL` ile açar.
- `kosu_turu` ∈ {`ilk`, `periyodik`, `duzeltme`} — küme KAPALIDIR. `open_run`
  **`duzeltme` değerini KENDİ reddeder** (`ValueError`): o değer `duzeltilen_run_id`
  gerektirir (036 CHECK, plan 847-848) ve onu yalnız `open_correction_run` yazar.
- `parent_run_id` DOLU ise (yeniden koşum, K-83) satır ana koşudan **`kosu_turu` ·
  `duzeltilen_run_id` · `package_id` üçlüsünü DEVRALIR** (plan 855-857 devralma hükmü);
  açıkça verilen `kosu_turu` ana koşununkinden farklıysa çağrı REDDEDİLİR.

```python
# runs.py  (Task 8)
async def record_result(
    db,
    *,
    run_id: str,
    result: EngineResult,            # KAPALI tip: TANIMI Task 8 (`engine_contract.py`),
                                     # ÜRETİMİ Task 13 (`decide`) — TEK motor-türevi girdi
) -> None: ...
```

- **`**report_fields` YOKTUR.** Fonksiyonun imzasında hiçbir `*args`/`**kwargs` bulunmaz.
- **Serbest sözlük parametresi de YOKTUR.** İlk yazım on iki alanı tek tek sayıyordu; o
  biçim `policy_report: dict` gibi **tipi olmayan** bir alanı imzada meşrulaştırıyordu —
  yani isimsiz-üretici deliği parametre adı kazanmış hâlde duruyordu. Bağlanan hüküm:
  koşu satırına yazılan HER motor-türevi kolon, `EngineResult`'ın **adı konmuş ve kapalı**
  bir alanından okunur. Alanın sessizce düşmesi artık imza sorunu değil, **alan-kümesi
  testi** sorunudur ve o test aşağıda adıyla sabittir.
- **Eşleme BİREBİRDİR (on bir alan → on bir kolon):** `sonuc` · `sebep` · `engine_version` ·
  `engine_config_sha` · `policy_report` · `barrier_report` · `engine_diff` ·
  `final_candidate` · `final_decision_log` · `content_sha` · `decision_log_sha`.
  `EngineResult`'ta bulunup koşu satırına yazılmayan alan YOKTUR; koşu satırında bulunup
  `EngineResult`'tan gelmeyen motor-türevi kolon da YOKTUR.
- **`record_result` aynı ifadede `durum='tamamlandi'` yazar.** `load_verified_run`'ın
  1. kapısını (plan 341) sağlanabilir kılan tek üretici budur.
- `result.sonuc == 'activation_eligible'` iken `final_candidate` · `final_decision_log` ·
  `content_sha` · `decision_log_sha` DÖRDÜ de dolu olmak ZORUNDADIR; biri eksikse yazım
  REDDEDİLİR (plan 1009-1010 F19 hükmü). Diğer iki sonuçta bu dördü `None` olabilir;
  `engine_version` · `engine_config_sha` · `policy_report` · `barrier_report` üç sonuçta da
  ZORUNLUDUR — `policy_report` en kötü hâlde **boş demetli** bir `PolicyReport`'tur,
  `None` DEĞİL.
- `kararsizlar` için ayrı kolon YOKTUR: plan 1486-1487 gereği "koşu raporuna girer" —
  yani `policy_report.kararsizlar` içinde taşınır.

```python
# runs.py  (Task 8) — load_verified_run'ın döndürdüğü tip
@dataclass(frozen=True)
class VerifiedRun:
    id: UUID
    run_id: str
    parent_run_id: str | None
    sector_id: UUID
    package_id: UUID | None
    kosu_turu: str
    duzeltilen_run_id: UUID | None
    durum: str
    sonuc: str
    sebep: str | None
    engine_version: str
    engine_config_sha: str
    content_sha: str
    decision_log_sha: str
    final_candidate: Mapping             # A1: `identity.donmus` ile SALT-OKUNUR
    final_decision_log: tuple[Mapping, ...]   # A1: DEMET (eski `list[dict]`)
    policy_report: Mapping       # PolicyReport'un jsonb'den okunmuş hâli — SALT-OKUNUR
    barrier_report: Mapping
    engine_diff: Mapping
    approval_snapshot: Mapping | None
    approval_karar: str | None
    snapshot_sha: str | None
    katman1_attestation: Mapping | None
    katman2_attestation: Mapping | None
    readiness_attestation: Mapping | None

    def __post_init__(self) -> None:
        """A1 (fix turu 2): jsonb'den okunan DOKUZ yükün hepsi `identity.donmus`'tan
        geçirilir. Gerekçe ölçülü: aktivasyon kapısı bu yüklerin İÇİNDEN okur
        (`readiness_attestation["onaylandi"]` · `katman1_attestation["sonuc"]`) ve
        `content_sha`/`decision_log_sha` `final_candidate`/`final_decision_log`'un
        kimliğidir. Donmuş sarmalayıcının içinde değiştirilebilir bir sözlük taşımak,
        kilitli satırdan okunmuş kanıtın YAPIMDAN SONRA çevrilmesine izin verirdi."""
        for _alan in (
            "final_candidate", "final_decision_log", "policy_report", "barrier_report",
            "engine_diff", "approval_snapshot", "katman1_attestation",
            "katman2_attestation", "readiness_attestation",
        ):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
```

`VerifiedRun` yalnız YEDİ kapının tamamı geçtiğinde üretilir (plan 341-344); bu yüzden
`engine_version` · `engine_config_sha` · `content_sha` · `decision_log_sha` ·
`final_candidate` · `final_decision_log` alanları `| None` DEĞİLDİR — kapıdan geçmiş bir
satırda dolu olmaları garantidir.

**Tipler NEREDE doğar — R9'un mekanik sonucu.** `record_result` (Task 8) artık
`EngineResult`'ı TÜKETİYOR; oysa `decide` Task 13'te doğar ve **R9 bir görevin sonraki
görevde doğan yüzeyi tüketmesini YASAKLAR.** Bu yüzden motor sözleşmesinin **veri tipleri**
(mantığı değil) Task 8'de doğan ayrı bir sözleşme modülüne alınır:

```python
# apps/social/backend/app/services/sector_pipeline/engine_contract.py   (Task 8 CREATE)
# YALNIZ kapalı değer kümeleri ve dataclass tanımları. Fonksiyon YOK, DB YOK, import
# yönü tek yönlüdür: engine.py buradan okur, burası engine.py'yi GÖRMEZ.

SONUCLAR: tuple[str, ...] = ("activation_eligible", "no_change", "blocked")   # KAPALI
BULGU_SINIFLARI: tuple[str, ...] = (
    "kapsam_ihlali", "mevzuat_uyusmazligi", "mevzuat_dogrulanamadi",
    "regresyon_kapisi", "ikinci_aktif", "acik_soru",
)   # KAPALI — altı değer (R7)
```

```python
# engine_contract.py  (Task 8) — tip tanımları
ENGINE_VERSION: str = "..."          # engine.py'de (Task 13); sözleşme değişince artar

def config_sha(config: PolicyConfig) -> str:      # policy_config.py (Task 13) — K-97 üreticisi
    """PolicyConfig'in kanonik hash'i. identity.canonical_sha'yı ÇAĞIRIR (K-92),
    ikinci bir hash kuralı yazmaz."""

UYGULANMAMA_SEBEPLERI: tuple[str, ...] = (
    "kanit-yok",        # spec girdisi satır 1189: kanıt yoksa karar uygulanmaz
    "mutabakat-yok",    # K-125: iki denetçi uyuşmuyor
    "referans-yok",     # 2026-09-10: sentez sözleşmesi 2.1 — `ekle` en az bir D# referansı ister
                        # VE atıfların HEPSİ çözülmeli (kısmi çözüm fail-closed)
    "referans-uyusmuyor",  # 2026-09-10: atıf BAŞKA bir alanın satırını gösteriyor
    "oneri-olumsuz",    # 2026-09-10: denetçi o satırda `alma`/`açık-soru` önermiş
    "celiski",          # 2026-09-10: referansın satırı `çelişki` sınıfında; sayı yetse de girmez
    "cogunluk-yok",     # yeni öğe 2-3 yapısal çoğunluk kuralı
)   # KAPALI — YEDİ değer; kaynağı Task 12'nin bağlayıcı kontrol kümesidir (plan 1376-1381)
    # ve spec girdisi satır 1189; UYDURULMUŞ değer YOKTUR.
    # SIRA ÖNCELİKTİR (`engine._reddedilenler`): `referans-yok` · `referans-uyusmuyor` ·
    # `oneri-olumsuz` · `celiski`,
    # `cogunluk-yok`'tan ÖNCE gelir — ikisinde de sayı ya hiç okunamamıştır ya da
    # okunması anlamsızdır; "çoğunluk yok" demek okunmuş bir sayı ima ederdi.

@dataclass(frozen=True)
class KararsizMadde:
    """K-23=B — motorun karar veremediği birim. Aktivasyonu BLOKLAMAZ (plan 1486-1487)."""
    unit_id: str
    sebep: str                       # serbest metin; kapalı küme DEĞİL (dürüst etiket)

@dataclass(frozen=True)
class BulguIzi:
    """run_checks'in ürettiği bulgunun kalıcı izi."""
    sinif: str                       # BULGU_SINIFLARI içinden — KAPALI KÜME (R7, altı değer)
    unit_id: str | None              # birime bağlanamayan bulguda None
                                     # (ör. `regresyon_kapisi`, `ikinci_aktif`)
    detay: str                       # bulguyu doğuran ölçümün tek cümlelik ifadesi
    kontrol: str = ""                # R-G1 (2026-09-11): bulguyu ÜRETEN kontrolün adı
                                     # (`EngineCheck.ad`). TEK yazıcısı `run_checks`'tir;
                                     # kontrol GÖVDESİNİN yazdığı bir değer REDDEDİLİR
                                     # (uydurma atıf = sessiz sınıf kayması). Varsayılan
                                     # BOŞTUR çünkü değeri gövde değil TOPLAYICI yazar.
                                     # Gerekçe ölçülmüş: `sinif` riskli sınıfları ayırt
                                     # ETMEZ — `acik_soru` sınıfını BEŞ ayrı kontrol
                                     # üretir ve onay yüzeyi (Task 14, K-42) sıralamayı
                                     # sınıf ADIYLA kurar. Alternatifi `detay` metnini
                                     # eşleştirmekti: referans bütünlüğü olmayan bağ (İlke 1).

@dataclass(frozen=True)
class UygulanmayanKarar:
    """Aday karar KANITSIZ/MUTABAKATSIZ olduğu için uygulanmadı, kalıp KORUNDU."""
    unit_id: str
    karar: str                       # identity'nin karar türü enum'undan (Task 3;
                                     # plan teknik karar 5: BEŞ değerli, KAPALI)
    sebep: str                       # UYGULANMAMA_SEBEPLERI içinden — KAPALI

@dataclass(frozen=True)
class PolicyReport:
    """K-95 politika raporu — koşu satırının `policy_report` kolonuna yazılan KAPALI tip.

    **TEK ÜRETİCİSİ `engine.decide`'dır.** Başka hiçbir modül bu sınıfı KURMAZ; serbest
    sözlükten üretilen bir politika raporu yolu YOKTUR (R2'nin isimsiz-üretici yasağı).
    Dört alanın dördü de ZORUNLUDUR; boş rapor `PolicyReport((), (), (), ())` biçiminde
    **boş demetlerle** ifade edilir, `None` ile DEĞİL.
    """
    kararsizlar: tuple[KararsizMadde, ...]
    bulgular: tuple[BulguIzi, ...]
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...]
    acik_soru_kimlikleri: tuple[str, ...]   # R7: `acik_soru` bulgusunu doğuran birimler;
                                            # sayaç DEĞİL, iz — K-71 kapısı R8'in yolunda

    # ── R-G8 (2026-09-11): KALICI YÜK ŞEKLİ — ekte SAHİPSİZDİ, artık burada.
    # `policy_report` kolonu `jsonb`'dir ve dataclass demetleri kendiliğinden
    # serileşmez. Çeviri BURADA doğar ki `record_result` kendi çevirisini
    # YAZMASIN — iki çeviri iki biçim demektir.
    def as_payload(self) -> dict[str, Any]: ...
    #   {"kararsizlar":            [{"unit_id", "sebep"}],
    #    "bulgular":               [{"sinif", "unit_id", "detay", "kontrol"}],   # R-G1
    #    "uygulanmayan_kararlar":  [{"unit_id", "karar", "sebep"}],
    #    "acik_soru_kimlikleri":   [str]}
    #
    # `from_payload` ÜRETİM YOLU DEĞİL, OKUYUCUDUR (H2 korunur): yalnız
    # `as_payload`'ın ürettiği biçimi kabul eder ve her öğeyi kendi
    # dataclass'ına kurarak kapalı kümeleri YENİDEN uygular. Gerekçesi hakem
    # turu 2'nin yüksek bulgusudur: ham sözlüğü okuyan tüketiciler (hazırlık
    # listesi, Task 17) alan VARLIĞINI şekil kanıtı sanıyordu ve
    # `{"kararsizlar": 1, "bulgular": [{}], ...}` biçimindeki bir yük "motor
    # kontrolleri tamam + bulgu yok" diye okunabiliyordu. Tüketicinin kendi
    # doğrulama listesini yazması İKİNCİ BİR SÖZLEŞME olurdu.
    @classmethod
    def from_payload(cls, payload: Any) -> "PolicyReport": ...

    _OGE_TIPLERI = {                        # KAPALI eşleme — dört alan, beşincisi YOK
        "kararsizlar": KararsizMadde,
        "bulgular": BulguIzi,
        "uygulanmayan_kararlar": UygulanmayanKarar,
        "acik_soru_kimlikleri": str,
    }

    def __post_init__(self) -> None:
        """A3 (fix turu 3, orta, KABUL) — DEMET ANOTASYONU ZORLAMA DEĞİLDİR.

        Fix turu 2'nin süpürme tablosu bu sınıfı *"temiz — dört alan da DEMET"* diye
        işaretlemişti. **Ölçüldü ve bu YANLIŞTI:** `tuple[...]` bir ANOTASYONDUR; çağıran
        `PolicyReport(kararsizlar=[…], …)` yazarsa alan bir LİSTE olur, donmuşluk onu
        engellemez ve çağıranla takma ad PAYLAŞILIR — R6(e)'nin `ValidatedReport`'ta
        kapattığı sınıfın ta kendisi. Alan `record_result` üzerinden koşu satırına
        yazıldığı için içeriği KİMLİK taşır.

        **`identity.donmus` BURADA KULLANILAMAZ — ölçülmüş tuzak.** `donmus`'un dönüşüm
        kümesi KAPALIDIR (R6(e), BEŞ kural) ve `KararsizMadde` · `BulguIzi` ·
        `UygulanmayanKarar` o kümenin DIŞINDADIR: donmuş dataclass ne `Mapping`, ne dizi,
        ne küme, ne de değişmez skaler listesinin üyesidir → kural (5) gereği `TypeError`.
        Onları `donmus`'a vermek, alanı dondurmak yerine YAPIMI DÜŞÜRÜRDÜ. Bu yüzden
        kural burada `tuple(...)` KOPYASI + ÖĞE TİPİ kontrolüdür; öğeler zaten kendi
        `frozen=True` sınıflarıdır ve `str` değişmezdir, dolayısıyla derinlik gerekmez.
        (`acik_soru_kimlikleri` `str` öğe taşır ve `donmus`'un kapalı skaler listesinde
        VARDIR; buna rağmen dört alanın hepsine AYNI kural uygulanır — iki alanı iki
        kuralla dondurmak, tam olarak ekin yasakladığı ikinci-kural sınıfıdır.)
        """
        for _alan, _tip in PolicyReport._OGE_TIPLERI.items():
            _deger = tuple(getattr(self, _alan))          # KOPYA — takma ad kapanır
            for _oge in _deger:
                if type(_oge) is not _tip:
                    raise TypeError(
                        f"PolicyReport.{_alan} yalnız {_tip.__name__} taşır "
                        f"({type(_oge).__name__} verildi) — benzeyen nesne kabul edilmez"
                    )
            object.__setattr__(self, _alan, _deger)

@dataclass(frozen=True)
class EngineResult:
    sonuc: str                       # SONUCLAR — KAPALI
    sebep: str | None
    final_candidate: Mapping | None            # A1: `identity.donmus` — SALT-OKUNUR
    final_decision_log: tuple[Mapping, ...] | None   # A1: DEMET (eski `list[dict]`)
    engine_diff: Mapping                       # A1
    policy_report: PolicyReport      # YENİ — K-95'in adı konmuş üreticisi;
                                     # `kararsizlar` alanı BURAYA taşındı
    barrier_report: Mapping                    # A1
    content_sha: str | None
    decision_log_sha: str | None
    engine_version: str              # YENİ — load_verified_run kapı 3'ün kaynağı
    engine_config_sha: str           # YENİ — kapı 4'ün kaynağı; config_sha() üretir

    def __post_init__(self) -> None:
        """A1 (fix turu 2): DÖRT yük alanı `identity.donmus`'tan geçirilir.
        `content_sha` `final_candidate`'in, `decision_log_sha` `final_decision_log`'un
        KİMLİĞİDİR; yapımdan sonra yükü değiştirmek, hash'i satıra yazılmış ama içeriği
        başka olan bir sonuç nesnesi üretirdi (`record_result` onu olduğu gibi basar)."""
        for _alan in ("final_candidate", "final_decision_log", "engine_diff", "barrier_report"):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
        # A3 (fix turu 3): `policy_report` bu döngüye GİRMEZ ve girmesi HATA olurdu —
        # `donmus`'un kapalı dönüşüm kümesi donmuş dataclass'ı REDDEDER (kural 5,
        # `TypeError`). `PolicyReport` kendi `__post_init__`'inde zaten kopyalanmış ve
        # öğe tipleri sınanmıştır; ikinci bir dondurma YAZILMAZ.
        if type(self.policy_report) is not PolicyReport:
            raise TypeError("policy_report PolicyReport olmalı — serbest sözlük KABUL EDİLMEZ")
```

- **`kararsizlar: list[dict]` alanı `EngineResult`'tan SİLİNDİ** (plan 1471 geçersiz).
  İki kaynak olsaydı hangisinin koşu satırına yazıldığı görev-başına review'a görünmezdi —
  R2'nin kapattığı sınıfın ta kendisi. Tek yer: `result.policy_report.kararsizlar`.
- `decide` her üç sonuçta da `engine_version=ENGINE_VERSION` ve
  `engine_config_sha=config_sha(config)` damgalar (K-97, plan 150-152) **ve her üç sonuçta
  da bir `PolicyReport` üretir** — `blocked`/`no_change` koşuları dahil (K-93).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — plan 986 (`open_run` imzası)
ve plan 1001-1002 (`record_result` imzası) GEÇERSİZ, yerine yukarıdakiler. Task 8'in Files
listesine **`Create: apps/social/backend/app/services/sector_pipeline/engine_contract.py`**
EKLENİR (plan 979-981) ve Produces listesine `SONUCLAR` · `BULGU_SINIFLARI` ·
`UYGULANMAMA_SEBEPLERI` · `KararsizMadde` · `BulguIzi` · `UygulanmayanKarar` ·
`PolicyReport` · `EngineResult` girer. Consumes satırı (plan 984) DEĞİŞMEZ — Task 8
sonraki hiçbir görevden yüzey tüketmez (R9 korunur). **Task 12** — `BULGU_SINIFLARI` artık
Task 12'de TANIMLANMAZ, `engine_contract`'tan **import edilir** ve Task 12 onun
**değerlerini üretir**; R7'nin Produces satırı bu biçimde okunur. **Task 13** — plan
1469-1471 (`EngineResult` alan listesi) `policy_report` ile genişler, `kararsizlar` ÇIKAR;
`decide` · `config_sha` · `ENGINE_VERSION` Task 13'ün Produces listesinde kalır ve
`PolicyReport`/`EngineResult` **tek üreticisi** Task 13'tür — tanım Task 8'de, **üretim**
Task 13'te (R5'in amacı tipin adının konması, R9'unki ileri-tüketimin yasaklanması;
tanım/üretim ayrımı ikisini birden karşılar).

**Kanıt testi · sahibi:**
- `test_open_run_requires_kosu_turu` · `test_kosu_turu_value_set_is_closed` ·
  `test_open_run_rejects_duzeltme_type` · `test_retry_inherits_type_target_and_package`
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_record_result_sets_durum_tamamlandi` ·
  `test_record_result_persists_every_engine_result_field` (on bir alanın on biri de satırda
  okunur — R2'nin sessiz-düşme kapısı) ·
  `test_record_result_signature_has_no_var_keyword_arguments` (yapısal: `inspect.signature`
  ile `VAR_KEYWORD` YOK) ·
  `test_record_result_takes_no_free_form_dict_parameter` (yapısal: `db` · `run_id` ·
  `result` DIŞINDA parametre YOK) ·
  `test_record_result_rejects_eligible_result_missing_f19_fields`
  — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_engine_result_carries_version_and_config_sha` ·
  `test_engine_result_field_set_is_closed` (alan adları yukarıdaki on birle **birebir**;
  fazlası da eksiği de RED — `kararsizlar` alanının VAR OLMAMASI da bu testin konusudur) ·
  `test_config_sha_changes_when_config_changes` ·
  `test_config_sha_uses_identity_canonical_rule` — **Sahip: Task 13**,
  `tests/test_policy_engine_outcome.py`.
- **`PolicyReport`'un kapısı (H2'nin ispatı):**
  `test_policy_report_field_set_is_closed` (dört alan adı birebir; fazlası da eksiği de RED)
  · `test_policy_report_constructed_only_in_engine_module` (yapısal depo-geneli tarama:
  `PolicyReport(` çağrısı YALNIZ `engine.py`'de; tanım dosyası ve `tests/` dizini açıkça
  muaftır, muafiyet testin içinde yazılıdır) ·
  `test_decide_returns_policy_report_for_every_outcome` (üç sonucun üçünde de dolu tip) ·
  `test_bulgu_izi_class_values_are_closed` (`BULGU_SINIFLARI` dışında `sinif` RED) ·
  `test_uygulanmama_sebepleri_are_closed` — **Sahip: Task 13**,
  `tests/test_policy_engine_outcome.py`.

---

## R3 — Onay olayı paket kimliğini TAŞIR

**Kusur (plan satırları):** planın kendi teknik kararı 14(c) (plan 178-181) şunu bağlıyor:
olaylar yaşam döngüsü kapsam sınıfındadır ve `033 F21` gereği `sector_id` + `package_id` +
`actor` ister, *"bu yüzden `record_decision` koşu kimliğinin yanında paket kimliğini de
taşır"*. Ölçüldü (`package_events.py::log_package_event`, yaşam döngüsü dalı, satır 221-223): yaşam döngüsü olayı `sector_id`,
`package_id` ve `actor` yoksa `PackageEventContractError` ile düşer. Buna rağmen plan
1555 satırındaki imza paket kimliği taşımıyor — yani `approval`/`rejection` olayı **yazılamadan
patlardı**.

**Kural (kontrolör):** eklenir; kaynağı **kilitli doğrulanmış koşudur.**

**Bağlayıcı sözleşme:**

```python
# approval.py  (Task 14)
KARARLAR: tuple[str, ...] = ("onay", "ret")          # KAPALI

async def record_decision(
    db,
    *,
    run_id: str,
    karar: str,                # KARARLAR içinden
    actor: str,
    seconds: int,              # K-42(b) — eşik YOK, yalnız kayıt
    snapshot_sha: str,         # F18 — karar dondurulmuş görüntünün hash'ine bağlanır
) -> None: ...
```

- Olay **`package_id` TAŞIR** ve o değer **çağırandan ALINMAZ**: `record_decision` ilk iş
  olarak `runs.load_verified_run(db, run_id=run_id, for_update=True)` çağırır ve
  `package_id` ile `sector_id`'yi **`VerifiedRun`'dan** okur. Çağıranın verdiği bir paket
  kimliği koşununkiyle çelişebilirdi; TEK KAPI doktrini (plan 345-347) ve F18 bunu yasaklar.
  Bu yüzden imzaya **çağıran-taraflı `package_id` parametresi EKLENMEZ** — hükmün istediği
  "olayın paket kimliğini taşıması"dır, çağırandan alması değil.
- Olay çağrısı: `log_package_event(db, event_type=("approval" if karar == "onay" else
  "rejection"), sector_id=run.sector_id, package_id=run.package_id, actor=actor, detail=...)`.
- `run.package_id` boşsa (taslak henüz yazılmamışsa) onay REDDEDİLİR — onay yüzeyi yalnız
  `activation_eligible` koşuda çalıştığı için taslak her zaman vardır (plan 180-181).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 14** — plan 1555-1559 imzası bu
metinle değiştirilir (parametre kümesi aynı kalır, gövde sözleşmesi bağlanır).

**Kanıt testi · sahibi:**
- `test_approval_event_carries_package_id_from_locked_run` ·
  `test_rejection_event_carries_package_id_from_locked_run` ·
  `test_record_decision_refuses_run_without_package_link` ·
  `test_record_decision_takes_no_caller_supplied_package_id` (yapısal: imzada
  `package_id`/`sector_id` parametresi YOK) — **Sahip: Task 14**,
  `tests/test_approval_surface.py`.

---

## R4 — Test, konusunu ÜRETEN görevde durur

**Kusur (plan satırları):** Task 6 (migration 036) Step 1 test listesi (plan 880-912) üç
tane **servis davranışı** testi taşıyor — konusu Task 8/Task 15 kodudur — ama Task 6 Step 5
(plan 923-924) onlardan PASS bekliyor. O kod o noktada YOKTUR.

**Kural (kontrolör):** bu üç test, konusunu kuran göreve taşınır. Task 6 yalnız
**migration'ın kendi** testlerini tutar: kolonlar · kısıtlar · CHECK'ler · geri alma.

**Bağlayıcı sözleşme — taşınan testler:**

| Test | Plan satırı | Konusu | YENİ sahip · dosya |
|---|---|---|---|
| `test_second_write_for_same_run_returns_existing_draft` | 906 | `writeback.write_draft_from_run` idempotency'si | **Task 15**, `tests/test_pipeline_writeback.py` — Task 15'in mevcut `test_replay_returns_existing_draft_without_new_version` (plan 1704) testiyle **AYNI iddiadır**; ikinci bir ad yazılmaz, Task 6'dan SİLİNİR ve Task 15'in mevcut adı kanonik sahiptir |
| `test_concurrent_write_for_same_run_yields_one_draft` | 907 | aynı yolun yarış hâli | **Task 15** — mevcut `test_concurrent_writes_yield_single_draft` (plan 1705) ile aynı iddia; Task 6'dan SİLİNİR |
| `test_retry_of_correction_inherits_target_and_type` | 905 | `runs.open_run(parent_run_id=…)` devralması (R2) | **Task 8**, `tests/test_pipeline_runs.py` — R2'nin `test_retry_inherits_type_target_and_package` testiyle birleşir |

Task 6'da **KALAN** kardeşleri (şema seviyesi, migration'ın kendi konusu, taşınmaz):
`test_package_id_is_not_unique` · `test_correction_run_may_share_package_id_with_parent` ·
`test_kosu_turu_and_duzeltilen_run_id_check_consistent` ·
`test_retry_of_correction_may_carry_both_links` (plan 901-904) — bunlar CHECK/kardinalite
testleridir, servis davranışı değil.

**Ek düzeltme (Row-D D5, aynı sınıf):** `test_content_written_without_decision_log_rejected`
(plan 892) şemada bulunmayan bir `content` kolonuna iddia ediyor; 036'nın kolonları
`final_candidate` / `final_decision_log`'dur (plan 780-781). Test adı ve iddiası
**`test_final_candidate_written_without_decision_log_rejected`** olarak düzeltilir.
Sahip DEĞİŞMEZ (Task 6).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 6** — plan 905 · 906 · 907
listeden ÇIKAR, plan 892 yeniden adlandırılır; Step 5 (plan 923-924) beklentisi böylece
karşılanabilir hâle gelir. **Task 8** ve **Task 15** — listeleri R2/R4 ile eşlenir.

---

## R5 — İmzada kullanılan her tip, onu ilk üreten görevde TANIMLANIR

**Kusur (plan satırları):** `EngineInputs` (plan 1373 · 1469), `AuditReport` (plan 1221),
`PacketRef` (plan 1167 · 1220) imzalarda kullanılıyor, hiçbir görevde tanımlanmıyor.
Sonuç: Karar Kapıları K-52'nin *"motor girdileri §9.1 ile sınırlıdır; DNA okuma yolu
açılmaz"* hükmünün (plan 97) **denetlenebileceği bir artefakt yok.**

**Kural (kontrolör):** üçü de tam alan listesiyle tanımlanır. `EngineInputs` Task 12'nin
malıdır ve en az şunları taşır: sentez aday kümesi · doğrulanmış denetçi envanteri · aktif
paket birim eşlemesi · bariyer paydası · K-91 ilk-koşu bayrağı · takvim anahtarları.
`PacketRef` ve `AuditReport` Task 9'un malıdır.

**Bağlayıcı sözleşme — Task 9 tipleri:**

```python
# auditors.py  (Task 9)
STATU_DEGERLERI: tuple[str, ...] = (
    "supported", "not_observed", "needs_update", "contradicted", "risk_unverified",
)   # KAPALI — beş değer (K-100, spec-input satır 1025-1029)

DENETCI_ROLLERI: tuple[str, ...] = ("denetci-1", "denetci-2")   # KAPALI (rol adı; ARAÇ adı DEĞİL — K-137)

BOLUM_ANAHTARLARI: tuple[str, ...]   # BEŞ anahtar; değerleri Task 4'ün pinlenmiş
                                     # sözleşme v2 metninden ÖLÇÜLEREK doldurulur, burada UYDURULMAZ (İlke 9)
                                     # Doldurma kuralı ve sıra kapısı: aşağıdaki "M1" bloğu

@dataclass(frozen=True)
class InventoryRow:              # K-100 — dört alan; spec-input satır 1031 kanoniktir:
    unit_id: str                 # "karar birimi anahtarı, denetçi statüsü, kanıt referansı
    statu: str                   #  ve tek cümle gerekçe"
    kanit: str
    gerekce: str

@dataclass(frozen=True)
class UrlCheck:
    url: str
    kaynak: str
    erisildi: bool
    icerik_uyumlu: bool          # K-126'nın "canlı URL doğrulaması" ayağı
    not_metni: str

ONERI_DEGERLERI: tuple[str, ...] = ("al", "uyarla", "alma", "açık-soru")
                                 # KAPALI — dört değer; pinli sözleşmenin ADIM 2 `ÖNERİ:` satırından ÖLÇÜLÜR

SINIF_TEKIL = "tekil"            # `sınıf` sütununun İKİ ADLI değeri; geri kalanı ORAN yazımıdır (`n-m`).
SINIF_CELISKI = "çelişki"        # Sözlük KAPALI DEĞİLDİR: eleme sonrası oran kalan kaynak sayısına
                                 # uyarlanır (2-2, 1-2), yani geçerli oran kümesi KOŞUYA göre değişir.

RESMI_DEGERLERI: tuple[str, ...] = ("evet", "hayır")
                                 # KAPALI — KAYNAK PROFİLİ `resmi` sütunu (2026-09-11, dış depo `12beec1`).
                                 # K-123'ün resmîlik yargısı ARTIK TİPLİ taşınır; K-126 istisnasının
                                 # BİRİNCİ ayağı motorda buradan okunur.

@dataclass(frozen=True, order=True)
class KaynakIddiasi:             # `K<kaynak>#<iddia>` — bir ARAŞTIRMA İDDİASININ kimliği
    kaynak: int                  # 1..AZAMI_KAYNAK
    iddia: int                   # araştırma raporunun Bölüm C `no` sütunu (≥1)

    @property
    def etiket(self) -> str: ...                 # "K1#3"

def kaynak_iddialari_coz(ham: str) -> tuple[KaynakIddiasi, ...] | None: ...
                                 # TEK ayrıştırıcı, İKİ çağıran: denetçinin `kaynak-iddialari`
                                 # sütunu ve sentezin `kaynak_iddia` alanı. Biçim KAPALI:
                                 # virgülle ayrılmış, ARTAN, tekrarsız. Bozuk girdi → None
                                 # (fail-closed). SIRA kuralı da burada yaşar, çağıranda DEĞİL:
                                 # iki uç farklı biçimleri kabul ederse BAĞ sessizce gevşer.

@dataclass(frozen=True)
class KaynakProfili:             # ÇIKTI SÖZLEŞMESİ (3) — KAYNAK PROFİLİ satırı
    kaynak: int                  # kaynak numarası; rapor içinde TEKRARSIZ (kimlik)
    resmi: bool                  # RESMI_DEGERLERI'nden ÇÖZÜLÜR
    not_metni: str               # 2-3 cümle; BOŞ olamaz

@dataclass(frozen=True)
class AuditRow:                  # ÇIKTI SÖZLEŞMESİ (1) — DENETİM TABLOSU satırı, DOKUZ sütun
    no: int                      # SATIR KİMLİĞİ; artan. Sentezin `D1#<no>` referansı BUNA çözülür
    alan: str
    iddia_ozeti: str
    kaynak_iddialari: frozenset[KaynakIddiasi]
                                 # 2026-09-11: satırın DAYANDIĞI araştırma iddiaları. Geçen kaynak
                                 # numaralarının kümesi `kaynaklar` ile ÇİFT YÖNLÜ EŞİTTİR — tek
                                 # yönlü bir kapı ("⊆") üç kaynakta gördüğünü söyleyen bir satırın
                                 # tek iddia göstermesine izin verirdi ve o satır motorda hâlâ ÜÇ
                                 # kaynaklık çoğunluk sayardı.
    kaynaklar: frozenset[int]    # kaynak NUMARALARI (1..AZAMI_KAYNAK) — yapısal çoğunluğun TEK girdisi
    sinif: str                   # `n-m` oranı · SINIF_TEKIL · SINIF_CELISKI; `kaynaklar` ile TUTARLI
    bayraklar: str
    oneri: str                   # ONERI_DEGERLERI içinden — KAPALI
    gerekce: str

@dataclass(frozen=True)
class AuditReport:
    denetci: str                             # DENETCI_ROLLERI içinden
    ham_metin: str
    bolumler: Mapping[str, str]              # anahtar kümesi = BOLUM_ANAHTARLARI (beş, kapalı)
                                             # A1: SALT-OKUNUR — anahtar kümesi bir KAPIDIR
    denetim_tablosu: tuple[AuditRow, ...]    # 2026-09-10: TİPLİ okunur; varsayılanı YOKTUR
    kaynak_profili: tuple[KaynakProfili, ...]
                                             # 2026-09-11: TİPLİ okunur; varsayılanı YOKTUR.
                                             # KAPSAM SINIRI (R6): bu imza koşunun YETKİLİ kaynak
                                             # sayısını GÖRMEZ, yani "her kaynak kapsandı mı"
                                             # sorusu burada CEVAPLANMAZ — yalnız satırların iç
                                             # tutarlılığı ölçülür.
    yeniden_dogrulama: tuple[InventoryRow, ...]
    url_orneklem: tuple[UrlCheck, ...]
    unit_snapshot_sha: str                   # raporun karşı raporladığı görüntünün hash'i (K-79/K-100)

    def __post_init__(self) -> None:
        # A1 (fix turu 2): `bolumler` `identity.donmus`'tan geçer. Beş anahtarlı kapalı
        # küme `validate_report`'un kapısıdır; yapımdan sonra anahtar eklemek/silmek o
        # kapıyı geçmiş bir raporu kapıdan geçmemiş hâle çevirirdi.
        object.__setattr__(self, "bolumler", identity.donmus(self.bolumler))
        # A3 (fix turu 3, orta, KABUL): iki dizi alanı DA kopyalanır ve öğe tipleri
        # sınanır. Fix turu 2 bunları yalnız `tuple[...]` ANOTASYONUNA bırakmıştı;
        # anotasyon çalışma zamanında hiçbir şey yapmaz — çağıran liste verirse takma ad
        # paylaşılır ve `validate_report`'un "her `unit_id` tam bir kez" kapısından geçmiş
        # bir envanter yapımdan SONRA değiştirilebilirdi. `identity.donmus` burada da
        # KULLANILAMAZ: `InventoryRow`/`UrlCheck` donmuş dataclass'tır ve `donmus`'un
        # KAPALI dönüşüm kümesinin dışındadır (kural 5 → `TypeError`).
        for _alan, _tip in (
            ("denetim_tablosu", AuditRow),
            ("kaynak_profili", KaynakProfili),           # 2026-09-11
            ("yeniden_dogrulama", InventoryRow),
            ("url_orneklem", UrlCheck),
        ):
            _deger = tuple(getattr(self, _alan))          # KOPYA — takma ad kapanır
            for _oge in _deger:
                if type(_oge) is not _tip:
                    raise TypeError(
                        f"AuditReport.{_alan} yalnız {_tip.__name__} taşır "
                        f"({type(_oge).__name__} verildi) — benzeyen nesne kabul edilmez"
                    )
            object.__setattr__(self, _alan, _deger)

@dataclass(frozen=True)
class PacketRef:
    run_id: str
    yetkili_kaynak_sayisi: int              # koşuya giren kaynak sayısı (tur kapılarının yetkili değeri)
    kaynak_seti_sha: str                    # 2026-09-10: `brief_doctor.kaynak_seti_sha(doctor_reports)`
                                            # — mekanik kapı rapor kümesinin SIRA-DUYARLI kimliği
    sector_id: UUID
    kok: Path                                # paket kök dizini
    kopyalar: Mapping[str, Path]             # anahtarlar = DENETCI_ROLLERI (iki, kapalı)
    kopya_shalari: Mapping[str, str]         # aynı anahtarlar; K-79: iki değer EŞİT olmak ZORUNDA
    unit_snapshot: Mapping[str, Mapping]     # identity.decision_units çıktısı (Task 3)
    unit_snapshot_sha: str                   # identity.canonical_sha(unit_snapshot)

    def __post_init__(self) -> None:
        # A1 (fix turu 2): ÜÇ eşleme de `identity.donmus`'tan geçer. `kopya_shalari`
        # K-79'un eşitlik invariantını, `unit_snapshot` ise `unit_snapshot_sha`'nın
        # KİMLİĞİNİ taşır; ikisi de yapımdan sonra değiştirilebilir olamaz.
        for _alan in ("kopyalar", "kopya_shalari", "unit_snapshot"):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
```

**KOŞU BAĞI (2026-09-10) — motorun girdi alan kümesi AÇILMADAN kurulur.**

Açık kalemdi: `EngineInputs` kendisine verilen `mekanik_eleme`'nin BU koşuya ait olduğunu
göremiyordu. Motorun kabul ettiği kör kaynak etiketi (`KAYNAK-1/2/3`) doğrudan
`mekanik_eleme.raporlar`'ın SIRASINDAN türer; başka bir koşunun kapısı verilirse aynı etiket
başka bir kaynağı gösterir ve yapısal çoğunluk sessizce yanlış kaynaklara dayanır.

Çözüm R5'in kapalı alan kümesini KORUR — `EngineInputs`'a alan EKLENMEZ. Kimlik zincirle taşınır:

```
build_packet(doctor_reports)  →  PacketRef.kaynak_seti_sha        (TÜRETİLİR, çağırandan alınmaz)
      → check_snapshot_agreement(expected_kaynak_sha=…)           (TAŞIR — kapı değil, mühür)
            → ValidatedAuditPair.kaynak_seti_sha
                  → EngineInputs.__post_init__                    (KARŞILAŞTIRIR — kapı BURADA)
```

`EngineInputs` yapımda `brief_doctor.kaynak_seti_sha(mekanik_eleme.raporlar)` hesaplar ve çiftin
mührüyle karşılaştırır; ayrışırsa `ValueError`. Emsal F1 ile aynıdır (`unit_snapshot_sha` ↔
`aktif_birimler`): karşılaştırma İKİ MEVCUT alan arasında yapılır, çağıranın beyanına DEĞİL.

Kimlik ÜÇ alandan türer ve üçü de bir sebeple girer: `icerik_ozeti` (kaynağın metni) ·
`kaynak_adi` (kimliği) · `sonuc` (elenme durumu — kabul edilen etiket kümesi elemeye bağlıdır).
Sıraya duyarlıdır.

**Kapsam sınırı (dürüst etiket).** Kimlik koşunun `run_id`'sini TAŞIMAZ ve taşıyamaz: motorun
girdi alan kümesi kapalıdır ve orada karşılaştırılacak ikinci bir `run_id` taşıyıcısı yoktur.
Kanıtlanan tam olarak şudur: *"motora verilen mekanik kapı, denetçi paketini kuran kapının ta
kendisidir."* AYNI kaynaklarla koşulmuş iki ayrı koşuyu birbirinden AYIRMAZ.

**ATIF ADAYA BAĞLIDIR (2026-09-10, hakem turu 1 — YÜKSEK).**

Motor bir `ekle` kararının kanıtını çözerken denetçi satırının YALNIZ `kaynaklar` ve `sinif`
sütunlarını okuyordu. Ölçüldü: `kanca_kaliplari` eklemesi `cta_kaliplari` hakkındaki bir satırı
gösterip yapısal çoğunluk kapısını GEÇEBİLİYORDU — olağan bir sentez sapmasıdır ve denetçinin
açıkça reddettiği bir kalıbı pakete sokar. Testin kendi fixture'ı da tam bu eşleşmeyi taşıyordu
ve hatayı MASKELİYORDU.

İki ayak bağlandı:

1. **Alan bağı** — denetçi satırının `alan`'ı kararın `alan`'ıyla eşleşmeli. Bağ TAM EŞİTLİK ya
   da `<alan>/` ÖNEKİDİR (Görev B satırı `ozel_gun/{dönem}/{başlık}` yazar, karar satırı yalnız
   `ozel_gun`); serbest alt dizge DEĞİL — `ozel_gun` öneki `ozel_gunler`'i KAPSAMAZ. Düşerse
   `referans-uyusmuyor`.
2. **Öneri bağı** — satırın `oneri`'si `EKLEMEYE_IZIN_VEREN_ONERILER` içinde olmalı. `alma` ve
   `açık-soru` kalıbı pakete SOKMAZ; karar AÇIK SORU olarak operatöre çıkar (`oneri-olumsuz`).

Ayrıca **kısmen çözülemeyen atıf listesi** kapatıldı (orta): `D1#1, D2#999` gibi bir alanda
geçerli satır TEK BAŞINA yetkilendiriyor, hatalı satır numarası provenanstan sessizce
kayboluyordu. Atıflardan biri bile çözülmüyorsa alan yapısal kanıt TAŞIMAZ.

**M1 — beş bölüm anahtarı ŞİMDİ bağlanmaz; bağımlılık bağlanır (fix turu 1, KISMEN RED).**
Fix turu 1'de bağımsız hakem *"beş bölüm anahtarını şimdi sabitle"* dedi. **REDDEDİLDİ.**
Gerekçe ölçülü: o anahtarlar **Task 4'ün henüz YAZILMAMIŞ** sözleşme v2 metninden ölçülür
(plan 643-644: *"dört bölüm → beş bölüm (yeniden doğrulama eklendi). Biçim kapısı (Task 9)
bu beşi arar."*); bugün burada beş ad yazmak, planın kendine bağladığı **ölçülmemiş-değer
yasağını** (İlke 9, plan 68-70) çiğnemek olurdu — yazılan adlar sonra sözleşmeye
UYDURULURDU, tersi değil. **Bu satır bilerek boştur; ileride okuyan biri "yardımcı olmak
için" değer İCAT ETMEZ.**

Boşluğun yerine **bağlayıcı ve test edilebilir** olan şudur:

1. **Sıra kapısı:** **Task 9, Task 4 tamamlanmadan BAŞLAYAMAZ.** Ölçüt mekaniktir: Task 4
   Step 5 (`chore: repin research contracts at v2`, plan 667) atılmış ve
   `shared/contracts/research-contracts.pin.json` v2 hash'lerini taşıyor olmalıdır. Task 9
   ilk iş olarak `contracts.require_pin` çağırır; pin v2 değilse görev DURUR (fail-closed).
2. **Doldurma kuralı:** `BOLUM_ANAHTARLARI`, pinlenmiş `hakem-denetci-gorevi.md`'nin **çıktı
   bölümü başlıkları ÖLÇÜLEREK** doldurulur — sıra ve sayı dosyadaki hâliyle aynıdır.
   Ölçüm komutu ve taze çıktısı Task 9'un adım notuna yazılır (İlke 9).
3. **Kapı testi:** `test_bolum_anahtarlari_match_pinned_contract_headings` — pin
   manifestinden dosya yolunu ve sha256'sını okur, dosyayı **hash doğrulayarak** açar,
   çıktı bölümü başlıklarını çıkarır ve `BOLUM_ANAHTARLARI` ile **birebir** (sıra dâhil)
   karşılaştırır. Sözleşme değişip anahtarlar güncellenmezse test DÜŞER; anahtarlar
   uydurulup sözleşmede karşılığı yoksa da DÜŞER. **Sahip: Task 9**,
   `tests/test_auditor_packaging.py`.
4. `test_bolum_anahtarlari_has_five_entries` — beş sayısı sözleşmenin kendi hükmüdür
   (plan 643-644), ölçülmemiş bir tahmin değildir. **Sahip: Task 9.**

**Etkilenen görev (M1):** **Task 4** — Step 5'in pin yenilemesi artık Task 9'un **açık ön
koşuludur**; Task 4'ün Interfaces "Produces" satırı bunu belirtir. **Task 9** — Consumes
satırına (plan 1165) *"Task 4 sözleşme v2 **pinlenmiş** hâli"* yazılır ve yukarıdaki iki
test eklenir.

`build_packet` imzası, anlık görüntüyü pakete **taşıyacak** biçimde bağlanır (R6(b)'nin
erişilebilirlik ayağı):

```python
def build_packet(
    *,
    brief: str,
    sources: list[str],
    doctor_reports: list[DoctorReport],
    active_package: dict | None,
    unit_snapshot: dict[str, dict],          # YENİ — Task 3 identity.decision_units
    run_id: str,
    sector_id: UUID,
    dest: Path,
) -> PacketRef: ...
```

**Bağlayıcı sözleşme — Task 12 tipleri:**

```python
# engine.py  (Task 12)
@dataclass(frozen=True)
class GateResults:
    katman1_passed: bool          # regresyon kapısı (spec §9.1: "prompt regresyonu zorunlu kapıdır")
    tek_aktif_ihlali: bool        # tek-aktif ön kontrolü

@dataclass(frozen=True)
class EngineInputs:
    """Motor girdileri — ALAN KÜMESİ KAPALIDIR (K-52, plan 97; spec §9.1).
    Marka DNA'sı için alan YOKTUR ve eklenmesi sözleşme revizyonu ister."""
    sentez: SynthesisResult                              # §9.1: sentez aday paketi + karar günlüğü
    aktif_paket: Mapping | None                          # §9.1: aktif paket (ilk koşuda None) — A1
    aktif_schema_version: int | None                     # §9.1: şema sürümü
    aktif_birimler: Mapping[str, Mapping]                # identity.decision_units (Task 3) — karar kapsamı kontrolü
                                                          # A1: SALT-OKUNUR — `mevcut_birim_sayisi` onun UZUNLUĞUDUR
    mevcut_birim_sayisi: int                             # bariyer paydası (K-130); ilk koşuda 0
    ilk_kosu: bool                                       # K-91
    son_turlarin_cikarmalari: tuple[Mapping, ...]        # §9.1: son turların çıkarma kararları (K-122) — A1: DEMET
    denetci_envanterleri: ValidatedAuditPair              # §9.1: iki denetçi tablosu + URL örneklemi.
                                                          # TİP ZORUNLUDUR: ham `AuditReport` KABUL EDİLMEZ
                                                          # (R6'nın H3 düzeltmesi; K-150: tam iki rapor)
    mekanik_eleme: RoundGate                             # §9.1: mekanik eleme sonucu (Task 7)
                                                          # 2026-09-11: `raporlar[i].iddialar` motorun
                                                          # İDDİA EVRENİDİR (`brief_doctor.CIddia`)
    takvim_anahtarlari: frozenset[str]                   # §9.1: sistem özel gün listesi (normalize anahtarlar)
    otomatik_kapilar: GateResults                        # §9.1: otomatik kapı sonuçları
```

- **`PolicyConfig` `EngineInputs`'a GİRMEZ** — `decide(inputs, config)` onu ayrı alır
  (plan 1469); tek kanonik yer korunur.
- **2026-09-11 — alan kümesi DEĞİŞMEDİ; iddia bağı YENİ ALAN İSTEMEDİ (ölçüldü).** Sentezin
  `kaynak_iddia` beyanı iki uçtan doğrulanır ve iki ucun da taşıyıcısı ZATEN buradadır:
  araştırma ucu `mekanik_eleme.raporlar[i].iddialar` (kaynak numarası KONUMDAN türer — bu
  `_kabul_edilen_etiketler`in kuralının AYNISIDIR, ikinci bir numaralandırma kuralı
  yazılmaz), denetçi ucu `denetci_envanterleri` içindeki satırların `kaynak_iddialari`
  sütunu. Aynı şey K-126'nın resmîlik ayağı için de geçerlidir (`kaynak_profili`).
  İlk tasarımda bu alanların `EngineInputs`'a EKLENECEĞİ sanılmıştı; taşıyıcıların
  zaten var olduğu ölçülünce R5 revizyonuna gerek kalmadı.
- `mevcut_birim_sayisi == len(aktif_birimler)` invariantı yapımda zorlanır. **A1
  (fix turu 2; KODA fix turu 3'te indi — A3):** bu invariantın anlamlı kalabilmesi için
  `aktif_paket` · `aktif_birimler` · `son_turlarin_cikarmalari` (ve `takvim_anahtarlari`)
  `__post_init__`'te `identity.donmus`'tan
  geçirilir (`object.__setattr__`), invariant kontrolü ondan SONRA koşar — aksi hâlde
  yapımdan sonra `aktif_birimler`'e bir birim eklemek, bariyer paydasını sessizce
  bozardı ve motor kendi kontrol ettiği sayıya güvenemezdi.
- **`denetci_envanterleri` tipi YAPIMDA zorlanır** (Plan 1'in `_require_evidence`
  doktrininin motor ayağı — ördek tiplemesi kabul edilmez):

```python
    def __post_init__(self) -> None:
        # A3 (fix turu 3, orta, KABUL) — NORMALİZASYON ARTIK KODDA.
        # Fix turu 2 bu üç koleksiyonun `identity.donmus`'tan geçtiğini yalnız PROSE'da
        # söylüyordu; blok hiç normalize etmiyor, doğrudan `len()` okuyordu. Anotasyon
        # çalışma zamanı zorlaması DEĞİLDİR: çağıran değiştirilebilir bir `dict` verirse
        # takma ad paylaşılır ve `mevcut_birim_sayisi == len(aktif_birimler)` invariantı
        # yapımdan SONRA sessizce bozulurdu. Sıra bağlayıcıdır: ÖNCE dondur, SONRA kontrol.
        for _alan in ("aktif_paket", "aktif_birimler", "son_turlarin_cikarmalari"):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
        # `takvim_anahtarlari` ZATEN değişmezdir (`frozenset`), ama çağıran `set` verebilir;
        # `donmus` onu da `frozenset`'e çevirir — aynı TEK kural, ikinci kural YOK.
        object.__setattr__(self, "takvim_anahtarlari",
                           identity.donmus(self.takvim_anahtarlari))
        if type(self.denetci_envanterleri) is not ValidatedAuditPair:
            raise TypeError(
                "denetci_envanterleri ValidatedAuditPair olmalı "
                f"({type(self.denetci_envanterleri).__name__} verildi) — ham denetçi "
                "raporu motora GİRMEZ; doğrulayıcı ve tur-seviyesi mutabakat atlanamaz"
            )
        if self.mevcut_birim_sayisi != len(self.aktif_birimler):
            raise ValueError("mevcut_birim_sayisi aktif_birimler ile tutarsız")
```

  İki `AuditReport`'tan oluşan bir demet, aynı alan adlarını taşısa bile REDDEDİLİR:
  `ValidatedAuditPair`'ı **yalnız** tur seviyesindeki mutabakat fonksiyonu üretir (R6),
  dolayısıyla motora ulaşan her envanter hem doğrulayıcıdan hem mutabakat kapısından
  geçmiştir. **Bu, planın *"girdi yalnız Task 9'un doğrulanmış envanteridir"* hükmünün
  (plan 1389-1390) tipe dönüşmüş hâlidir** — prose değil, kapı.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 9** — Produces listesine
`PacketRef` · `AuditReport` · `InventoryRow` · `UrlCheck` · `STATU_DEGERLERI` ·
`BOLUM_ANAHTARLARI` EKLENİR; `build_packet` imzası (plan 1167) yukarıdakiyle değişir.
**Task 4** — pin yenilemesi Task 9'un ön koşulu olarak beyan edilir (M1).
**Task 12** — Produces listesine `EngineInputs` · `GateResults` EKLENİR (plan 1372-1374);
`EngineInputs` **Task 10'un `ValidatedAuditPair` tipini TÜKETİR** (Task 10 < Task 12,
R9 korunur).
**Task 13** — `decide(inputs: EngineInputs, …)` (plan 1469) artık tanımlı bir tipe işaret
eder.

**Kanıt testi · sahibi:**
- `test_engine_inputs_field_set_is_closed` — `EngineInputs` alan adları yukarıdaki listeyle
  **birebir** eşleşir; fazlası da eksiği de RED. **K-52'nin denetlenebilir karşılığı budur**
  (preflight C12'yi kapatır). **Sahip: Task 12**, `tests/test_policy_engine_checks.py`.
- `test_engine_inputs_has_no_brand_dna_field` (K-52 negatif kontrol) — **Sahip: Task 12**.
- **H3'ün negatif kapıları:** `test_engine_inputs_refuses_bare_audit_report_tuple`
  (iki ham `AuditReport`'tan oluşan demet → `TypeError`; planın `test_engine_consumes_only_validated_inventory`
  testi, plan 1424, artık bu tipe karşı okunur) ·
  `test_engine_inputs_refuses_lookalike_pair` (aynı alan adlarını taşıyan sahte nesne → RED) ·
  `test_engine_inputs_accepts_only_validated_pair` (pozitif kontrol) — **Sahip: Task 12**,
  `tests/test_policy_engine_checks.py`.
- `test_packet_ref_carries_unit_snapshot_and_equal_copy_hashes` (K-79) ·
  `test_audit_report_inventory_rows_have_four_fields` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`.

---

## R6 — Veriyi kapılayan doğrulayıcı AYRIŞTIRILMIŞ NESNEYİ geri verir; çapraz denetçi karşılaştırması TUR seviyesindedir

**Kusur (plan satırları):** (a) `validate_report(...) -> list[str]` (plan 1170) yalnız hata
metni döner, oysa motorun girdisi *"Task 9'un **doğrulanmış** envanteridir"* (plan 1389-1390)
— ayrıştırılmış envanteri **hiçbir görev üretmiyor**; (b) `validate_report`'un ZORUNLU
`unit_snapshot` girdisinin (plan 1182-1185) adlandırılmış bir üreticisi yok ve Task 9'un
Consumes satırı (plan 1165) Task 3'ü hiç saymıyor; (c) TEK rapor alan bir doğrulayıcıdan
*"iki denetçi AYNI anlık görüntüye karşı raporlamış"* olduğunu kanıtlaması isteniyor
(plan 1185) ve testi (`test_inventory_rejects_divergent_snapshot_hash`, plan 1200) Task 9'a
dosyalanmış. **(d) Fix turu 1 bulgusu (yüksek, KABUL):** ilk yazımın `ValidatedReport`'u
`ValidatedReport(rapor=None, errors=[])` biçiminde KURULABİLİYORDU — `gecerli` özelliği o
nesnede `True` döner ve **raporsuz bir "geçerli" envanter** doğardı; ayrıca
`EngineInputs.denetci_envanterleri` ham `AuditReport` kabul ettiği için çağıran hem
doğrulayıcıyı hem tur seviyesindeki mutabakat kapısını **atlayabiliyordu**. Yani motorun
*"yalnız doğrulanmış envanter"* şartının hiçbir tipte veya kapıda karşılığı YOKTU — prose
olarak yazılıydı, kod olarak değil.

**Kural (kontrolör):** (a) `validate_report` **ayrıştırılmış envanter nesnesi + hata listesi**
döner — tip tanımlanır; (b) anlık görüntünün üreticisi adlandırılır: `identity.decision_units`
(Task 3) ve Task 9'un Consumes satırı Task 3'ü BEYAN EDER; (c) çapraz denetçi
snapshot-hash mutabakatı **iki raporu birden gören TUR seviyesi** bir fonksiyona taşınır
(Task 10) ve testi onunla birlikte gider; (d) **`ValidatedReport` tutarsız kurulamaz** ve
motorun kabul ettiği envanter, yalnız tur seviyesinde üretilen **kapalı bir çift tipidir**
(`ValidatedAuditPair`) — ham rapor motora ULAŞAMAZ.

**Bağlayıcı sözleşme:**

```python
# auditors.py  (Task 9)
@dataclass(frozen=True)
class ValidatedReport:
    rapor: AuditReport | None       # errors BOŞ DEĞİLSE None (geçersiz rapor nesneye dönüşmez)
    errors: tuple[str, ...]         # A1: DEMET — donmuş sarmalayıcı DEĞİŞTİRİLEBİLİR liste TAŞIMAZ

    def __post_init__(self) -> None:
        """İKİ HÂL VARDIR, üçüncüsü YOKTUR — yapımda zorlanır.

        (rapor dolu, errors boş)  = geçerli
        (rapor None, errors dolu) = geçersiz

        Diğer iki kombinasyon YAPIM HATASIDIR: `ValidatedReport(None, ())` `gecerli`
        özelliğini `True` döndürüp **raporsuz bir geçerli envanter** üretirdi;
        `ValidatedReport(rapor, ("...",))` ise hatalı bir raporu geçerli gibi taşırdı.

        **A1 (fix turu 2):** `errors` tutarlılık kontrolünden ÖNCE **normalize edilir** —
        çağıran liste verse de alan bir DEMET olur ve çağıranın nesnesiyle takma ad
        PAYLAŞMAZ. Normalizasyon önce koşmazsa kontrol, kendisinin kopyalamadığı ve
        yapımdan SONRA boşaltılabilen bir koleksiyona bakmış olurdu.
        """
        object.__setattr__(self, "errors", tuple(self.errors))
        if (self.rapor is None) != bool(self.errors):
            raise ValueError(
                "ValidatedReport tutarsız: `rapor is None` ile `errors` doluluğu AYNI "
                f"olmak ZORUNDA (rapor={'None' if self.rapor is None else 'dolu'}, "
                f"errors={len(self.errors)}) — yarım doğrulama sonucu yazılmaz"
            )

    @property
    def gecerli(self) -> bool:
        """A1: İKİ koşul BİRDEN — rapor VAR **ve** hata YOK. Yalnız `not self.errors`
        demek, yapımdan sonra hataları boşaltılmış raporsuz bir nesneyi `True`
        gösterirdi; kusurun ta kendisi buydu. Demet + iki koşul birlikte kapatır."""
        return self.rapor is not None and not self.errors

def validate_report(
    text: str,
    *,
    unit_snapshot: dict[str, dict],     # identity.decision_units (Task 3) — TEK üretici
    denetci: str,                       # DENETCI_ROLLERI içinden
) -> ValidatedReport: ...
```

`validate_report`'un zorladıkları (plan 1178-1186 aynen geçerli, tek fark dönüş tipi):
beş bölüm · her envanter satırı dört alanlı · `statu` ∈ `STATU_DEGERLERI` · `unit_snapshot`
içindeki HER `unit_id` **tam bir kez** · tanınmayan kimlik YOK · tekrar YOK. **Çapraz
denetçi karşılaştırması BURADA YAPILMAZ** — tek rapor görür.

```python
# auditors.py  (Task 10) — TUR seviyesi
@dataclass(frozen=True)
class ValidatedAuditPair:
    """Motorun kabul ettiği TEK envanter tipi (K-150: tam iki denetçi).

    **TEK ÜRETİCİSİ `check_snapshot_agreement`'tır.** Sınıf başka hiçbir modülde
    KURULMAZ; kurulsaydı doğrulayıcıyı ve mutabakat kapısını atlayan ikinci bir yol
    doğardı — R6'nın kapattığı sınıfın ta kendisi.
    """
    birinci: AuditReport           # DENETCI_ROLLERI[0] ("denetci-1") raporu
    ikinci: AuditReport            # DENETCI_ROLLERI[1] ("denetci-2") raporu
    unit_snapshot_sha: str         # ikisinin de üzerinde mutabık kaldığı görüntü hash'i
    kaynak_seti_sha: str           # 2026-09-10 KOŞU BAĞI: paketten TAŞINAN kaynak kümesi kimliği;
                                   # burada kapı DEĞİL mühürdür — karşılaştırma EngineInputs'ta

@dataclass(frozen=True)
class SnapshotAgreement:
    cift: ValidatedAuditPair | None
    errors: tuple[str, ...]         # A1: DEMET — `ValidatedReport` ile AYNI kural

    def __post_init__(self) -> None:
        # ValidatedReport ile AYNI iki-hâl kuralı — üçüncü hâl yapım hatasıdır.
        # A1 (fix turu 2): normalizasyon kontrolden ÖNCE; takma ad da PAYLAŞILMAZ.
        object.__setattr__(self, "errors", tuple(self.errors))
        if (self.cift is None) != bool(self.errors):
            raise ValueError("SnapshotAgreement tutarsız: cift ile errors birlikte karar verir")

    @property
    def gecerli(self) -> bool:
        # A1: İKİ koşul BİRDEN — çift VAR ve hata YOK.
        return self.cift is not None and not self.errors

def check_snapshot_agreement(
    validated: tuple[ValidatedReport, ValidatedReport],
    *,
    expected_snapshot_sha: str,        # PacketRef.unit_snapshot_sha
    expected_kaynak_sha: str,          # R-G3 (2026-09-11): PacketRef.kaynak_seti_sha
) -> SnapshotAgreement:
    """Girdi HAM rapor DEĞİL, `validate_report`'un dönüşüdür. DÖRT koşul birden aranır:

    (1) iki `ValidatedReport`'un İKİSİ de `gecerli` — biri değilse `cift=None` ve
        hataları `errors`'a birleştirilir (K-150 fail-closed);
    (2) iki raporun `denetci` alanları `DENETCI_ROLLERI`nin ikisini de TAM BİR KEZ kapsar
        (aynı rolden iki rapor REDDEDİLİR);
    (3) her raporun `unit_snapshot_sha`'sı `expected_snapshot_sha`'ya EŞİT;
    (4) iki raporun `unit_snapshot_sha`'ları birbirine EŞİT (K-79/K-100).

    **`expected_kaynak_sha` KAPI DEĞİLDİR, TAŞIMADIR (R-G3, 2026-09-11).** Kapı kümesi
    DÖRT koşulda kalır — beşinci koşul EKLENMEZ. Tek rapor gören bu imzada
    karşılaştırılacak ikinci bir kaynak-kümesi taşıyıcısı yoktur; değer pakete
    mühürlenir ve karşılaştırma BİR KATMAN SONRA, `EngineInputs` yapımında yapılır
    (motora verilen mekanik kapının bu paketi kuran kapı olduğu ORADA ölçülür).

    Dördü de geçerse `ValidatedAuditPair` üretilir — BAŞKA ÜRETİCİ YOKTUR. Bir koşul
    düşerse `cift` `None`'dır ve tur GEÇERSİZDİR.
    """
```

`run_audit_round` (plan 1220) imzası DEĞİŞMEZ: anlık görüntü ve hash'i `packet`'in içinden
gelir (R5'teki `PacketRef`). Uyuşmazlıkta `AuditRound(gecerli=False, sebep=...)` döner →
K-150 gereği sentez BAŞLAMAZ (plan 1253-1255).

Motorun girdisi (plan 1389-1390 karşılığı): `EngineInputs.denetci_envanterleri`
**tipi gereği** yalnız `check_snapshot_agreement`'ın ürettiği `ValidatedAuditPair` olabilir
(R5'teki `__post_init__` kapısı); ham metin de ham `AuditReport` da motora ULAŞMAZ.
Zincir tek yönlü ve atlanamazdır:

`validate_report` → `ValidatedReport` → `check_snapshot_agreement` → `ValidatedAuditPair`
→ `EngineInputs` → `run_checks`/`decide`

Ara halkanın atlanabildiği hiçbir imza YOKTUR.

### R6(e) — A1: DONMUŞ SARMALAYICININ İÇİNDEKİ DEĞİŞTİRİLEBİLİR KOLEKSİYON (fix turu 2, yüksek, KABUL)

**Kusur (kapanış-doğrulama turu, ölçüldü).** `ValidatedReport` `frozen=True`'dur ama
`errors` alanı bir **liste**dir; donmuşluk yalnız *alanın yeniden atanmasını* engeller,
listenin İÇİNİ değil. Yasak hâl yapımdan SONRA geri kuruluyordu:

```python
v = ValidatedReport(None, ["x"])   # __post_init__ geçer: rapor None, errors dolu
v.errors.clear()                   # donmuşluk buna KARIŞMAZ
# şimdi: rapor None · errors boş · eski `gecerli` özelliği True  → RAPORSUZ GEÇERLİ ENVANTER
```

`SnapshotAgreement` aynı kusuru taşıyordu (`cift=None`, `errors` boşaltılır → `gecerli`
`True`). İlk yazımın kapıları **yalnız kurucuyu** sınıyordu; kurucu-sonrası mutasyonu
hiçbir test görmüyordu.

**Kural (kontrolör) — SINIF düzeyinde, iki örnek düzeyinde DEĞİL.** Bir donmuş
dataclass'ın **geçerlilik ya da kimlik taşıyan** her koleksiyon alanı DEĞİŞTİRİLEMEZ
olur ve `__post_init__`'te **normalize/kopyalanır** (takma ad da kapanır); geçerlilik
özelliği tek koşula değil, **taşıdığı iki koşulun ikisine birden** bakar
(`rapor is not None and not self.errors`).

**Tek normalizasyon kuralı — ikinci bir kural YAZILMAZ (Task 3 CREATE'e EKLENİR):**

```python
# apps/social/backend/app/services/sector_pipeline/identity.py   (Task 3)
from types import MappingProxyType

def donmus(value: Any) -> Any:
    """Donmuş dataclass alanlarının TEK normalizasyon kuralı: derin, SALT-OKUNUR kopya.

    Kopya olduğu için çağıranın nesnesiyle takma ad PAYLAŞMAZ; salt-okunur olduğu için
    yapımdan sonra içi değiştirilemez. Dönüşüm KÜMESİ KAPALIDIR — BEŞ kural, altıncısı
    YOKTUR:

      (1) `Mapping`           → `MappingProxyType`(anahtarları sıralı YENİ `dict`;
                                her değer özyinelemeli `donmus`)
      (2) `list` | `tuple`    → `tuple`(her öğe özyinelemeli `donmus`)
      (3) `set` | `frozenset` → `frozenset`(her öğe özyinelemeli `donmus`)
      (4) değişmez skaler     → OLDUĞU GİBİ döner; KAPALI liste:
                                `None` · `bool` · `int` · `float` · `str` · `bytes` ·
                                `Decimal` · `UUID` · `Path` · `datetime` · `date`
      (5) bu dördünün DIŞINDA her şey → `TypeError` (fail-closed; sessiz geçiş YOK)

    `donmus(donmus(x))` ile `donmus(x)` AYNI değeri verir (idempotent) — iki kez
    çağrılması bir hata değildir.
    """
```

**SÜPÜRME — ekin TANIMLADIĞI ON SEKİZ donmuş dataclass'ın tamamı tek tek okundu
(2026-08-30).** Ölçüt: *donmuş sarmalayıcı, içeriği geçerlilik ya da kimlik taşıyan
değiştirilebilir bir `list`/`dict` tutuyor mu?*

| # | Donmuş dataclass (modül · görev) | Değiştirilebilir koleksiyon | Verdikt |
|---|---|---|---|
| 1 | `VerifiedRun` (`runs.py` · Task 8) | dokuz jsonb yükü | **KUSURLU → DÜZELTİLDİ** — aktivasyon kapısı `readiness_attestation["onaylandi"]` ve `katman1_attestation["sonuc"]` içinden okur; `content_sha`/`decision_log_sha` yükün kimliğidir |
| 2 | `KararsizMadde` (`engine_contract.py` · Task 8) | yok (iki `str`) | temiz |
| 3 | `BulguIzi` (`engine_contract.py` · Task 8) | yok | temiz |
| 4 | `UygulanmayanKarar` (`engine_contract.py` · Task 8) | yok | temiz |
| 5 | `PolicyReport` (`engine_contract.py` · Task 8) | dört alanın DÖRDÜ de (yalnız ANOTASYON demetti) | **KUSURLU → DÜZELTİLDİ (fix turu 3, A3)** — fix turu 2 bunu "temiz" saymıştı; ölçüldü ki `tuple[...]` anotasyonu çalışma zamanında hiçbir şey yapmaz, liste geçirilirse takma ad korunur. Kopya + öğe tipi kontrolü eklendi (`donmus` KULLANILAMAZ — kapalı küme donmuş dataclass'ı reddeder) |
| 6 | `EngineResult` (`engine_contract.py` · Task 8) | `final_candidate` · `final_decision_log` · `engine_diff` · `barrier_report` | **KUSURLU → DÜZELTİLDİ** — ilk ikisi `content_sha`/`decision_log_sha`'nın konusudur |
| 7 | `InventoryRow` (`auditors.py` · Task 9) | yok (dört `str`) | temiz |
| 8 | `UrlCheck` (`auditors.py` · Task 9) | yok | temiz |
| 9 | `AuditReport` (`auditors.py` · Task 9) | `bolumler` **+ `yeniden_dogrulama` · `url_orneklem`** | **KUSURLU → DÜZELTİLDİ (ikinci ayak fix turu 3, A3)** — `bolumler` `BOLUM_ANAHTARLARI` kapısıdır; iki dizi alanı fix turu 2'de yalnız anotasyonla korunuyordu, şimdi kopyalanıyor ve öğe tipleri sınanıyor |
| 10 | `PacketRef` (`auditors.py` · Task 9) | `kopyalar` · `kopya_shalari` · `unit_snapshot` | **KUSURLU → DÜZELTİLDİ** — K-79 eşitlik invariantı + `unit_snapshot_sha` kimliği |
| 11 | `GateResults` (`engine.py` · Task 12) | yok (iki `bool`) | temiz |
| 12 | `EngineInputs` (`engine.py` · Task 12) | `aktif_paket` · `aktif_birimler` · `son_turlarin_cikarmalari` (+ `takvim_anahtarlari`) | **KUSURLU → DÜZELTİLDİ (kodda ancak fix turu 3'te, A3)** — `mevcut_birim_sayisi == len(aktif_birimler)` invariantı; fix turu 2 normalizasyonu yalnız PROSE'da söylüyordu, `__post_init__` bloğu `len()`'i doğrudan okuyordu |
| 13 | `ValidatedReport` (`auditors.py` · Task 9) | `errors` | **KUSURLU → DÜZELTİLDİ** — hükmün ana vakası |
| 14 | `ValidatedAuditPair` (`auditors.py` · Task 10) | yok — iki `AuditReport` + `str`; #9 düzeltilince derinlemesine donmuş | temiz (türev) |
| 15 | `SnapshotAgreement` (`auditors.py` · Task 10) | `errors` | **KUSURLU → DÜZELTİLDİ** — ikinci ana vaka |
| 16 | `ActivationGateEvidence` (`sector_package_lifecycle.py` · Task 15) | yok — altı skaler + iki jeton alanı | temiz |
| 17 | `RollbackGateEvidence` (`sector_package_lifecycle.py` · Task 15) | yok | temiz |
| 18 | `ChecklistItem` (`readiness_items.py` · Task 8) | yok | temiz |

**Sonuç (fix turu 3'te GÜNCELLENDİ): on sekizin SEKİZİ kusurlu, sekizi de düzeltildi.**
Fix turu 2 yediyi sayıyordu; fix turu 3'te `PolicyReport` (#5) yanlış "temiz"likten
çıkarıldı ve #9 ile #12'nin düzeltmeleri **prose'dan koda** indirildi. Ölçüt fix turu
3'te KESKİNLEŞTİ: *anotasyon değil, `__post_init__` bloğunun KENDİSİ kopyalıyor ve
öğe tipini sınıyor mu?* Düzeltme her birinin KENDİ tanım bloğunda yazılıdır (yukarıda ve
R2 · R5); burada tekrarlanmaz — çift kayıt yasağı (R14) tip tanımları için de geçerlidir.

**`identity.donmus`'un KAPALI kümesi — hangi alan hangi kuralla dondurulur (A3, fix turu 3).**
`donmus` yalnız `Mapping` · dizi · küme · değişmez skaler alır; **donmuş dataclass öğesi
kuralın DIŞINDADIR ve `TypeError` ile düşer** (R6(e), kural 5). Bu yüzden iki ayrı ve
BİRBİRİNİ DIŞLAYAN uygulama vardır, üçüncüsü YOKTUR:
- Öğeleri `Mapping`/dizi/skaler olan alan → `identity.donmus(...)` (ör. `VerifiedRun`'ın
  dokuz yükü, `EngineResult`'ın dört yükü, `EngineInputs`'ın dört koleksiyonu,
  `AuditReport.bolumler`, `PacketRef`'in üç eşlemesi).
- Öğeleri **donmuş dataclass** olan alan → `tuple(...)` KOPYASI + `type(öge) is <Sınıf>`
  kontrolü (`PolicyReport`'un dört alanı, `AuditReport.yeniden_dogrulama` ve
  `.url_orneklem`). `donmus`'a verilmez.
Hangi alanın hangi kola düştüğü tanım bloğunda yazılıdır; ikinci bir normalizasyon kuralı
YAZILMAZ.

**Etkilenen görev (A1):** **Task 3** — `identity.donmus` Produces listesine EKLENİR
(`identity.py`, plan 508-524 aralığındaki Produces listesi). **Task 8** — `VerifiedRun` ve
`EngineResult` tanımlarına `__post_init__` kapısı EKLENİR (ikisi de Task 8'de doğar).
**Task 9** — `ValidatedReport` · `AuditReport` · `PacketRef`. **Task 10** —
`SnapshotAgreement`. **Task 12** — `EngineInputs`. **Task 13** — `EngineResult`'ın
salt-okunurluk testinin sahibi (üretici görev, R4).

**Kanıt testi · sahibi (A1) — hepsi kurucu-SONRASI mutasyonu ve takma adı hedefler:**
- `test_donmus_returns_read_only_mapping` (`donmus({"a": 1})["a"] = 2` → `TypeError`) ·
  `test_donmus_freezes_nested_values` (iç içe sözlük/liste de salt-okunur) ·
  `test_donmus_does_not_alias_caller_object` (çağıranın sözlüğü sonradan değişince dönen
  değer DEĞİŞMEZ) · `test_donmus_rejects_unknown_type` (kapalı kümenin dışı → `TypeError`,
  fail-closed) · `test_donmus_is_idempotent` (pozitif kontrol) — **Sahip: Task 3**,
  `tests/test_unit_identity.py`.
- `test_validated_report_errors_are_a_tuple_and_cannot_be_cleared`
  (`ValidatedReport(None, ["x"]).errors.clear()` → `AttributeError`; hükmün ana ispatı) ·
  `test_validated_report_does_not_alias_caller_error_list` (çağıranın listesi sonradan
  boşaltılınca nesne DEĞİŞMEZ) ·
  `test_validated_report_gecerli_is_false_without_a_report` (`gecerli` İKİ koşula bakar) ·
  `test_audit_report_sections_are_read_only` ·
  `test_packet_ref_mappings_are_read_only_and_unaliased` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`.
- `test_snapshot_agreement_errors_are_a_tuple_and_cannot_be_cleared` ·
  `test_snapshot_agreement_gecerli_is_false_without_a_pair` — **Sahip: Task 10**,
  `tests/test_auditor_orchestration.py`.
- `test_verified_run_payload_fields_are_read_only` (dokuz alanın dokuzu da; birine yazma
  denemesi `TypeError`) — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_engine_result_payload_fields_are_read_only` — **Sahip: Task 13**,
  `tests/test_policy_engine_outcome.py` (üreticisi Task 13'tür — R4).
- `test_engine_inputs_collections_are_read_only` ·
  `test_engine_inputs_unit_count_cannot_drift_after_construction` (yapımdan sonra
  `aktif_birimler`'e birim eklenemez) — **Sahip: Task 12**,
  `tests/test_policy_engine_checks.py`.

**A3'ün EKSİK KALAN testleri (fix turu 3) — normalizasyon PROSE'da vardı, KODDA yoktu:**
- `test_engine_inputs_normalises_before_the_count_check` (çağıran `aktif_birimler`'i
  değiştirilebilir bir `dict` olarak verir; yapımdan sonra ona birim eklemek
  `mevcut_birim_sayisi` invariantını BOZMAZ — dondurma kontrolden ÖNCE koştuğunun ispatı) ·
  `test_engine_inputs_does_not_alias_caller_collections` (üç koleksiyonun üçü de) ·
  `test_engine_inputs_accepts_a_plain_set_for_takvim_anahtarlari` (pozitif kontrol:
  `set` → `frozenset`) — **Sahip: Task 12**, `tests/test_policy_engine_checks.py`.
- `test_policy_report_sequences_are_tuples_when_lists_are_passed` ·
  `test_policy_report_does_not_alias_caller_lists` (çağıranın listesi sonradan
  boşaltılınca rapor DEĞİŞMEZ) ·
  `test_policy_report_rejects_foreign_element_type` (`bulgular=(<KararsizMadde>,)` →
  `TypeError`; alan-başına öğe tipi zorlanır) ·
  `test_policy_report_rejects_lookalike_element` (aynı alan adlarını taşıyan sahte nesne
  → RED) — **Sahip: Task 13**, `tests/test_policy_engine_outcome.py` (üretici görev, R4).
- `test_audit_report_sequences_are_tuples_and_unaliased` ·
  `test_audit_report_rejects_foreign_row_type` (`yeniden_dogrulama=(<UrlCheck>,)` →
  `TypeError`) — **Sahip: Task 9**, `tests/test_auditor_packaging.py`.
- **Tuzağın kendi kapısı:** `test_donmus_rejects_a_frozen_dataclass_element`
  (`identity.donmus((KararsizMadde("u", "s"),))` → `TypeError`) — donmuş dataclass öğeli
  alanların NEDEN `donmus`'a verilmediğinin ölçülmüş ispatı. **Sahip: Task 3**,
  `tests/test_unit_identity.py`.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 9** — plan 1170-1171 (dönüş tipi
`list[str]`) GEÇERSİZ; plan 1165 satırındaki Consumes satırı **`Task 3 identity.decision_units +
identity.canonical_sha`** ile genişler; plan 1200 satırındaki
`test_inventory_rejects_divergent_snapshot_hash` Task 9'dan ÇIKAR. **Task 10** — Produces
listesine `check_snapshot_agreement` · `ValidatedAuditPair` · `SnapshotAgreement` EKLENİR
(plan 1218-1221). **Task 12** — `EngineInputs` bu tipi tüketir (R5).

**Kanıt testi · sahibi:**
- `test_validate_report_returns_parsed_inventory_on_success` (pozitif kontrol) ·
  `test_invalid_report_yields_none_object_with_errors` — **Sahip: Task 9**,
  `tests/test_auditor_packaging.py`. (Mevcut K-100 testleri plan 1197-1201 aynen kalır,
  yalnız dönüş tipine göre okunur.)
- `test_inventory_rejects_divergent_snapshot_hash` — **YENİ sahip: Task 10**,
  `tests/test_auditor_orchestration.py`.
- `test_round_rejects_report_snapshot_differing_from_packet` — **Sahip: Task 10**.
- **H3'ün negatif kapıları — `ValidatedReport` (Sahip: Task 9,
  `tests/test_auditor_packaging.py`):**
  `test_validated_report_rejects_none_report_with_empty_errors`
  (`ValidatedReport(None, [])` → `ValueError`; bu, hükmün ana ispatıdır) ·
  `test_validated_report_rejects_report_carrying_errors`
  (`ValidatedReport(<rapor>, ["x"])` → `ValueError`) ·
  `test_valid_report_object_reports_gecerli_true` (pozitif kontrol).
- **H3'ün negatif kapıları — çift (Sahip: Task 10,
  `tests/test_auditor_orchestration.py`):**
  `test_snapshot_mismatch_yields_no_pair` (hash uyuşmazlığı → `cift is None`) ·
  `test_invalid_report_yields_no_pair` (bir rapor geçersizse çift ÜRETİLMEZ) ·
  `test_same_role_twice_yields_no_pair` (iki rapor da `denetci-1` → RED) ·
  `test_validated_pair_constructed_only_in_check_snapshot_agreement` (yapısal depo-geneli
  tarama: `ValidatedAuditPair(` çağrısı YALNIZ `auditors.py::check_snapshot_agreement`
  gövdesinde; tanım satırı ve `tests/` dizini açıkça muaftır) ·
  `test_agreement_yields_pair_when_all_four_conditions_hold` (pozitif kontrol).

---

## R7 — Yalnız-bulgu üreten fonksiyona UYGULAMA iddiası test edilemez; her bulgu sınıfının bir tüketicisi olur

**Kusur (plan satırları):** Task 12 `run_checks`'i **saf bulgu üreticisi** olarak bağlıyor
ve bunun kapısı olarak `test_run_checks_never_returns_a_run_outcome` testini koyuyor
(plan 1373 · 1378 · 1417); aynı Step 1 listesinde ise **uygulama/uygulanmama** iddia eden
testler duruyor (plan 1420 · 1421 · 1428 · 1430 · 1431). İkisi aynı anda doğru olamaz.
Ayrıca `acik_soru` bulgusu (plan 1429, `test_readd_conflict_emits_acik_soru_finding`)
Task 13'ün dönüşüm listesinde (plan 1522-1528) **hiçbir tüketiciye** sahip değil.

**Kanonik dayanak (spec girdisi, satır 1189 kontrol tablosu — spec'e ÜSTÜNDÜR):**
*"`guncelle` ve `cikar` kararları denetçi satırı veya doğrulanmış URL referansı taşımalı;
**kanıt yoksa karar uygulanmaz, kalıp korunur**"*. "Uygulanmaz/korunur" bir **uygulama**
semantiğidir; uygulamayı yapan `decide`'dır, `run_checks` değil.

**Kural (kontrolör):** uygulama/uygulanmama testleri Task 13'e taşınır; `acik_soru`
bulgusuna `decide`'da açık bir tüketici verilir ve K-71 gereği açık soru aktivasyonu
BLOKLAR — sonuç `blocked`'tır.

**Bağlayıcı sözleşme:**

```python
# engine_contract.py  (Task 8'de TANIMLI — R2'nin H2 düzeltmesi) — BULGU sınıfları, KAPALI
BULGU_SINIFLARI: tuple[str, ...] = (
    "kapsam_ihlali",
    "mevzuat_uyusmazligi",
    "mevzuat_dogrulanamadi",
    "regresyon_kapisi",
    "ikinci_aktif",
    "acik_soru",
)
# Task 12 bu kümeyi IMPORT eder ve DEĞERLERİNİ üretir; Task 13 `BulguIzi.sinif` alanında
# ve dönüşüm tablosunda tüketir. Tanımın Task 8'de olmasının sebebi R2/H2'de yazılıdır:
# `PolicyReport` Task 8'in `record_result`'ında imza tipidir ve R9 ileri-tüketimi yasaklar.
```

`decide`'ın (Task 13) dönüşüm tablosu — **altı sınıfın altısı da tüketilir**:

| Bulgu | `decide` sonucu | Koşul |
|---|---|---|
| `kapsam_ihlali` | `blocked` | her zaman (plan 1522) |
| `mevzuat_uyusmazligi` | `blocked` | her zaman — K-125 benimsendi (plan 1523) |
| `mevzuat_dogrulanamadi` | `blocked` | YALNIZ `config.block_on_legislation is True`; varsayılan `False` (plan 1524-1525) |
| `regresyon_kapisi` | `activation_eligible` OLAMAZ | plan 1526 |
| `ikinci_aktif` | `blocked` | plan 1527 |
| **`acik_soru`** | **`blocked`, `sebep="acik-soru-var"`** | **YENİ** — bulgu VARSA ya da `inputs.sentez.acik_sorular` boş DEĞİLSE. K-71 gereği açık soru aktivasyonu bloklar (plan 103 · 1488-1489) |

Sınır (plan 1486-1487 aynen geçerli): K-23=B kararsızları **bloklamaz** — `kararsizlar`
listesine girer, `policy_report`'a yazılır. Açık soru yolu ondan AYRIDIR.

**Taşınan testler (Task 12 → Task 13, `tests/test_policy_engine_outcome.py`):**

| Test | Plan satırı | Neden taşınıyor |
|---|---|---|
| `test_guncelle_without_evidence_is_not_applied` | 1420 | "uygulanmaz" = uygulama semantiği |
| `test_cikar_without_two_auditor_agreement_keeps_pattern` | 1421 | "korunur" = uygulama semantiği (preflight listesinde adı geçmiyor, sınıfı aynı) |
| `test_flag_consumption_applied` | 1428 | "applied" |
| `test_new_item_needs_two_of_three` | 1428 | aday öğenin pakete GİRİP girmediği |
| `test_category_conflict_package_type_wins` | 1430 | hangi değerin nihai adaya yazıldığı |
| `test_unmatched_holiday_key_not_written` | 1431 | "not_written" |

Task 12'de KALAN: `test_readd_conflict_emits_acik_soru_finding` (plan 1429) — konusu
bulgunun ÜRETİLMESİDİR. Task 13'e YENİ eklenen tüketici testi:
`test_acik_soru_finding_becomes_blocked` + `test_synthesis_open_questions_become_blocked`
(iki kaynak da aynı sonuca çıkar).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 12** — plan 1420 · 1421 · 1428 ·
1430 · 1431 listeden ÇIKAR; `BULGU_SINIFLARI` Task 12'nin Produces satırında **tanım olarak
DEĞİL, tüketim olarak** görünür (tanımı `engine_contract.py`'de, Task 8 — bkz. R2/H2).
**Task 13** — plan 1522-1528 dönüşüm listesi `acik_soru` satırıyla genişler; `acik_soru`
bulgusunun izi `PolicyReport.acik_soru_kimlikleri`'ne yazılır (R2).

**Kanıt testi · sahibi:** yukarıdaki tabloların tamamı; `test_acik_soru_finding_becomes_blocked`
ve `test_finding_classes_all_have_a_consumer` (yapısal: `BULGU_SINIFLARI`'nın her değeri
`decide`'ın dönüşüm tablosunda geçer) — **Sahip: Task 13**,
`tests/test_policy_engine_outcome.py`.

---

## R8 — Kanıt veritabanından OKUNUR, çağırandan alınmaz. İKİNCİ bir kurucu yoktur

**Kusur (plan satırları):** (a) Task 14 `Consumes: Task 13 EngineResult` (plan 1545) diyor,
oysa gövdesi her şeyi `load_verified_run`'dan **basıyor** (plan 1547-1552) ve planın kendi
doktrini kanıtın çağırandan alınmasını yasaklıyor (plan 319-325); Consumes ayrıca gerçekten
kullandığı yüzeyi (`runs.load_verified_run`) hiç saymıyor. (b) `approval.to_activation_evidence(
snapshot: dict) -> ActivationGateEvidence` (plan 1560-1563) **çağıranın verdiği bir sözlükten**
kanıt üreten İKİNCİ bir kurucudur — planın "TEK KAPI LİSTESİ" bölümünün (plan 334-359)
*"yolu yok"* dediği deliği tam olarak yeniden açar. Ölçüldü
(`sector_package_lifecycle.py::_require_evidence`, satır 133-144): `_require_evidence` yalnız SINIFI doğrular, kanıtın
KÖKENİNİ değil — yani uydurulmuş bir sözlükten kurulan kanıt kapıdan geçerdi.

**(c) Fix turu 1 bulgusu — EN ÖNEMLİSİ (yüksek, KABUL).** İlk yazımın R8'i yalnız bir
**kolaylık kurucusunu** sildi; kapının kendisine dokunmadı. **Ölçüldü (2026-08-30):**

- `ActivationGateEvidence` ve `RollbackGateEvidence` **public, `frozen=True` dataclass**'tır
  (`sector_package_lifecycle.py`, satır 83-113 ve 116-130); herkes literal değerlerle
  kurabilir.
- `_require_evidence` (aynı dosya, satır 133-144) **YALNIZ** `type(evidence) is expected`
  kontrolü yapar — kanıtın KÖKENİNE bakmaz.
- Plan 1'in kendi testleri bunu **yapıyor ve geçişleri tamamlıyor**:
  `tests/test_package_lifecycle.py::_activation_evidence` (satır 134-142) ve
  `::_rollback_evidence` (satır 145-148) kanıtı literalden kurar;
  `test_first_activation_single_step` (satır 268) · `test_rollback_restores_previous_version`
  (satır 420) o kanıtla **başarıyla** geçiş yapar.
- İlk yazımın kapısı **yapısal grep**'ti; grep `tests/` dizinini ve tanım dosyasını AÇIKÇA
  muaf tutar, ayrıca takma ad (`E = ActivationGateEvidence`) ve dinamik kurulumu
  (`globals()[...]`, `dataclasses.replace`) GÖREMEZ.

Sonuç: planın çekirdek doktrini — *"kanıt veritabanından okunur, çağırandan alınmaz"* —
**yazılıydı ama ZORLANMIYORDU.**

**Kural (kontrolör):** `to_activation_evidence` TAMAMEN SİLİNİR. Tek kurulum yeri
aktivasyon yolunun içidir ve kilitli doğrulanmış koşudan kurulur. Task 14'ün Consumes satırı
düzeltilir. **Ve kapı grep'ten ALINIP kabul fonksiyonunun İÇİNE konur:** her iki kanıt
sınıfı, yalnız veritabanı destekli bir fabrikanın üretebileceği **tek kullanımlık bir köken
jetonu** taşır; `activate_package` ve `rollback_package` bu jetonu **kendi işlemleri
içinde, kilitli satıra karşı** doğrular ve **harcar**. Yapısal tarama KALIR ama artık tek
kapı değildir — yardımcı bir hijyen kontrolüdür.

**Bağlayıcı sözleşme:**

```python
# approval.py  (Task 14)
# approval.to_activation_evidence  →  SİLİNDİ. Modülde ActivationGateEvidence KURULMAZ,
# import bile edilmez.
```

```python
# writeback.py  (Task 15) — TEK kurulum yeri
async def activate_from_snapshot(db, *, run_id: str, actor: str) -> None:
    """`ActivationGateEvidence` YALNIZ burada kurulur; alanlarının HEPSİ kilitli
    `VerifiedRun`'dan ve kilitli taslak satırından okunur:

        activation_eligible = (run.sonuc == "activation_eligible")
        # ŞEKİL KAPISI ZORUNLU (revizyon R-F, 2026-09-08) — aşağıdaki satır korumasızdır:
        # değer önce `list`/`tuple` olarak sınanır, değilse `EvidenceMintRefused`.
        open_questions_count = len(run.approval_snapshot["acik_sorular"])
        katman1_passed       = run.katman1_attestation["sonuc"] == "PASS"
        # A4 (fix turu 3, düzeltme) — ÖNCEKİ YAZIM `….strip() == KANONİK` yazıyordu;
        # ölçüldü ki bu, `" <kanonik> "` gibi boşluk-sarmalı bir değeri GEÇİRİR — oysa
        # bağlayıcı metin "BİREBİR EŞİT" diyor. Kural: alan BİR KEZ okunur, tipi
        # `type(...) is str` ile sınanır, boş-olmama ayrı bir kapıdır ve KARŞILAŞTIRMA
        # NORMALİZASYONSUZDUR (`strip`/`lower`/`casefold` YOK).
        _att = run.readiness_attestation
        _sha = _att["madde_kumesi_sha"] if (
            _att is not None and "madde_kumesi_sha" in _att) else None
        checklist_approved   = (
            _att is not None
            and _att["onaylandi"] is True          # anahtar yoksa KeyError — sessiz False YOK
            and type(_sha) is str                  # `bool`/alt sınıf/`None` RED
            and _sha.strip() != ""                 # boş ya da yalnız-boşluk RED (boşluk kapısı)
            and _sha == readiness_items.MADDE_KUMESI_SHA   # NORMALİZASYONSUZ — yedek yol YOK
            # R-G9 (F1) — BEŞİNCİ koşul: tasdik dayandığı kanıt kümesinin izini
            # TAŞIMALI ve iz, aktivasyon anında TAZE ölçülene BİREBİR eşit olmalı.
            # Alan yoksa kapı DÜŞER; parmak izsiz eski tasdik için yedek yol YOKTUR.
            and type(_att.get("kanit_parmakizi")) is str
            and _att["kanit_parmakizi"].strip() != ""
            and _att["kanit_parmakizi"] == beklenen_kanit_parmakizi
        )
        expected_active_version / expected_no_active  = K-94 taban durumu (plan 1685-1687)

    Hiçbir alan parametreden gelmez; fonksiyonun imzasında `evidence`, `snapshot`
    ya da herhangi bir `dict` parametresi YOKTUR."""
```

### R8(c) — KÖKEN JETONU: kapı grep'te değil, kabul fonksiyonunun içinde

**Dürüst sınır önce (İlke 3 · İlke 9).** Python'da **kriptografik anlamda taklit edilemez**
bir jeton, aynı süreçte koşan koda karşı KURULAMAZ: aynı süreçteki kod fabrikayı çağırabilir,
`dataclasses.replace` kullanabilir, `object.__setattr__` ile donmuş alanı yazabilir ya da
jetonu doğrudan veritabanından okuyabilir. Bunu iddia ETMİYORUZ. **Ulaşılabilir en güçlü
garanti** ve **adı konmuş sınırı** şudur:

> **Garanti — ve ne OLMADIĞI (A2, fix turu 2, KABUL).** Jeton bir **DERİNLEMESİNE SAVUNMA
> katmanıdır**; doktrini KAPATMAZ ve kapattığı bu ekte İDDİA EDİLMEZ.
>
> **Yaptığı:** bir kanıt nesnesi kapıdan ancak, o kanıtın **alan değerleri** üzerinde
> hesaplanmış bir parmak izi ile birlikte, ilgili **kilitli veritabanı satırında** basılmış
> ve **henüz harcanmamış** bir jeton varsa geçer. Yani hiçbir kanıt, **veritabanına gidip
> gelmeden** ve **o gidiş gelişte kilitli satıra yazmadan** kabul edilemez. Literal
> değerlerle kurulmuş bir kanıt — Plan 1'in bugünkü testlerinin kurduğu türden — **her iki
> geçişte de REDDEDİLİR.**
>
> **Yapamadığı — ve YAPAMAYACAĞI:** aynı **veritabanı kimliğiyle** (principal) koşan kod
> kendi jetonunu **basabilir**. `mint_evidence_token` da tam olarak o kimlikle koşar; onun
> koddan bir üstünlüğü YOKTUR. Dolayısıyla jeton *"kanıt uydurulamaz"* DEMEZ; *"kanıt,
> kilitli bir satıra yazan bir veritabanı turu OLMADAN kullanılamaz"* der. Bu iki cümle
> AYNI ŞEY DEĞİLDİR; burada yalnız ikincisi iddia edilmektedir.
>
> **Gerçek sınır nerededir:** bir **VERİTABANI YETKİ SINIRI** — jeton kolonlarına UPDATE
> edebilen rol ile uygulama kodunun koştuğu rolün AYRI olması. Böyle bir sınır ancak
> **canlı rollerin ÖLÇÜLMESİYLE** kurulabilir ve bu ekte **TASARLANMAZ**: ölçüm yapılmadan
> `SECURITY DEFINER` rutin, kolon düzeyi `GRANT` ya da yeni bir rol modeli YAZILMAZ —
> hangisinin gerektiği ölçümün ÇIKTISIDIR, girdisi değil.

**KALAN RİSK — kendi sözcükleriyle; K-103'ün bugünkü konusu DEĞİL (A2, fix turu 2).**

Önceki yazım bu kalanı *"planın K-103 etkin yetki ölçümünün (Task 15 Step 6) konusudur"*
diye dosyalamıştı. **Ölçüldü (2026-08-30, plan gövdesi Task 15 Step 6) ve bu dosyalama
YANLIŞ çıktı:** o ölçümün (b) ayağı `has_table_privilege(<rol>,'social.sector_packages',…)`
yazar — yani etkin yetkiyi **YALNIZ `social.sector_packages`** üzerinde ölçer.
`social.sector_package_runs` ve `social.package_rollback_plans` ölçüm metninde HİÇ geçmez;
jeton kolonları da geçmez. Kalan risk, bugünkü K-103'ün kapsamadığı bir yerde duruyordu.

**Kalanın dürüst ifadesi:** *"`social.sector_package_runs` ve
`social.package_rollback_plans` tablolarının jeton kolonlarına UPDATE edebilen her kod,
kendi kanıtı için jeton basabilir. Bu bir tip ya da kod-yapısı sorunu DEĞİL, bir veritabanı
yetki sorunudur. **ÖLÇÜLMEDİ** — dolayısıyla bugün kapalı mı açık mı olduğu BİLİNMİYOR."*

**Evi (TARİHLİ, evsiz-park DEĞİL):** planın **Task 15 Step 6** etkin-yetki ölçümü bu turda
**ÜÇ tabloyu** (`sector_packages` · `sector_package_runs` · `package_rollback_plans`) ve
**jeton kolonlarını** kapsayacak biçimde GENİŞLETİLDİ; planın **Task 18 Step 7** kaldırma +
negatif-deneme adımı aynı üç tabloya genişletildi. Sınırın kurulup kurulmadığı o ölçümün
çıktısıyla belli olur; o güne kadar burada **"kapatıldı" DENMEZ.**

**Şema ayağı (Task 6, migration 036).** İki tablo da aynı DÖRT kolonu kazanır:

```sql
-- social.sector_package_runs  VE  social.package_rollback_plans
kanit_jetonu             text        NULL,   -- 64 hex karakter; harcanınca NULL'lanır
kanit_jetonu_parmakizi   text        NULL,   -- kanıt alanlarının kanonik sha256'sı
kanit_jetonu_basildi_at  timestamptz NULL,
kanit_jetonu_harcandi_at timestamptz NULL,
CONSTRAINT <tablo>_kanit_jetonu_butun
  CHECK (kanit_jetonu IS NULL
         OR (kanit_jetonu_parmakizi IS NOT NULL AND kanit_jetonu_basildi_at IS NOT NULL))
```

Jeton **türü kolonu YOKTUR**: jetonun türünü taşıdığı TABLO belirler
(`sector_package_runs` → aktivasyon, `package_rollback_plans` → geri alma). İkinci bir
enum açmak, R2'nin kapattığı isimsiz-değer sınıfını geri getirirdi.

**Tip ayağı — Plan 1 arayüzünde BEYAN EDİLEN değişiklik (Task 8 + Task 15; görev
bölünmesi hemen aşağıda).** Bu değişiklik planın
*"Bu planın Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER"* bölümüne, `expected_no_active` ve
`_update_draft_row` kalemlerinin YANINA yazılır — gizli bir arayüz kırılması bırakılmaz.

**GÖREV BÖLÜNMESİ — AÇIK-3'ün gövdeye SÜPÜRÜLMÜŞ hâli (fix turu 3).** Bu tek dosya İKİ
görev arasında bölünür ve bölünme AÇIK-3'ün kararının aynısıdır:

- **Task 8 MODIFY** — DÖRT yardımcı + yerel görünüm tipi + **jeton ALANLARI ve onların
  şekil kapıları**: `activation_evidence_payload` · `rollback_evidence_payload` ·
  `_evidence_fingerprint` · `_evidence_fingerprint_from_payload` · `KilitliKosuGorunumu` ·
  `_require_kosu_gorunumu` · `_require_token` · `_require_kapsam_sha` ·
  `EvidenceMintRefused` · iki kanıt sınıfının köken alanları
  (`ActivationGateEvidence.run_id` · `.provenance_token`; `RollbackGateEvidence.incident_id`
  · `.package_id` · `.onay_kapsam_sha` · `.provenance_token`) ve YALNIZ o alanların
  `__post_init__` kapıları.
- **Task 15 MODIFY** — `EvidenceProvenanceInvalid` · `_consume_provenance` · iki geçiş
  fonksiyonunun jeton doğrulaması · `_update_draft_row` · `ActivationGateEvidence.
  expected_no_active` (planın zaten beyan ettiği alan) ve onun `_require_flag` kapısı.

**Alan düzeyinde bölünmenin sebebi R9'dur (fix turu 3'te ölçüldü ve düzeltildi).**
`runs.build_rollback_evidence` (**Task 8**) `RollbackGateEvidence(**payload,
provenance_token=token)` KURAR ve `runs.mint_evidence_token` (**Task 8**)
`EvidenceMintRefused` FIRLATIR. Fix turu 2 hem alanları hem istisnayı Task 15'e
yazıyordu; Task 8 < Task 15 olduğu için bu, **R9'un yasakladığı ileri-tüketimdi** —
Task 8 kendi sırasında tamamlanamazdı. Alanlar ve istisna Task 8'e, kapı gövdeleri ve
tüketim Task 15'e ait olunca her görev kendi sırasında kapanır. `expected_no_active`
Task 15'te KALIR: onu yalnız Task 15'in `activate_from_snapshot`'ı üretir.

**Fix turu 2'nin yazımı İKİ YÜK yardımcısını (`activation_evidence_payload` ·
`rollback_evidence_payload`) `runs.py`'de TANIMLIYOR ve `build_activation_evidence`'ı
`runs.activation_evidence_payload` çağırır diye yazıyordu** (aşağıdaki üretici bloğu) —
AÇIK-3 kararı verildi ama gövdeye işlenmedi. Fix turu 3'te dört yardımcının TANIMI da,
TÜM çağrıları da buraya taşındı; `runs.py`'de yardımcıların NE TANIMI NE İKİNCİ
KOPYASI kalır (yalnız import + çağrı).

```python
# apps/social/backend/app/services/sector_package_lifecycle.py
#   Task 8 MODIFY  → KilitliKosuGorunumu · _require_kosu_gorunumu ·
#                    activation_evidence_payload · rollback_evidence_payload ·
#                    _evidence_fingerprint · _evidence_fingerprint_from_payload ·
#                    _require_token · _require_kapsam_sha · EvidenceMintRefused ·
#                    iki kanıt sınıfının KÖKEN ALANLARI + o alanların kapıları
#   Task 15 MODIFY → EvidenceProvenanceInvalid · _consume_provenance ·
#                    expected_no_active + kapısı · geçiş fonksiyonlarının doğrulaması
# Her tanımın başında hangi görevin yazdığı ayrıca işaretlidir.
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

# ---------------------------------------------------------------- Task 8 MODIFY

class KilitliKosuGorunumu(Protocol):
    """`runs.VerifiedRun`'ın bu modülün GÖRDÜĞÜ yüzeyi — YEREL tip, KAPALI alan kümesi.

    **Neden var (AÇIK-3'ün ölçülmüş teknik kusuru, fix turu 3, KABUL).** AÇIK-3 kararı
    harfiyen uygulanınca `activation_evidence_payload(run: VerifiedRun)` bu modülü
    `runs.py`'ye bağımlı kılardı; oysa `runs.py` ZATEN bu modülden `_require_actor`'ı
    alıyor (AÇIK-1 ayak (b)) — yani **döngüsel import**. Karar doğru, uygulaması bu tiple
    yapılır: yardımcılar `VerifiedRun`'ı IMPORT ETMEZ, yalnız bu protokole yazılır.
    `VerifiedRun` protokolü **yapısal olarak** karşılar; nominal bir bağ KURULMAZ ve
    `runs.py` bu tipi import etmek ZORUNDA DEĞİLDİR.

    Alan kümesi KAPALIDIR — SEKİZ alan, dokuzuncusu YOKTUR (hepsi `VerifiedRun`'da
    aynı adla ve aynı tiple vardır):
    """
    run_id: str
    sector_id: UUID
    package_id: UUID | None
    durum: str
    sonuc: str
    approval_snapshot: Mapping[str, Any] | None
    katman1_attestation: Mapping[str, Any] | None
    readiness_attestation: Mapping[str, Any] | None


_KOSU_GORUNUM_ALANLARI: tuple[str, ...] = (
    "run_id", "sector_id", "package_id", "durum", "sonuc",
    "approval_snapshot", "katman1_attestation", "readiness_attestation",
)   # KAPALI — SEKİZ ad; `KilitliKosuGorunumu` ile BİREBİR


def _require_kosu_gorunumu(value: Any, label: str) -> None:
    """Ördek tiplemesi kabul edilmez ama nominal bağ da kurulamaz (döngüsel import).
    Aradaki tek dürüst kapı: SEKİZ alanın SEKİZİ de VAR mı? Biri eksikse `TypeError`
    (fail-closed) — sessizce `None` üretilmez."""
    eksik = [ad for ad in _KOSU_GORUNUM_ALANLARI if not hasattr(value, ad)]
    if eksik:
        raise TypeError(
            f"{label} kilitli koşu görünümü değil — eksik alanlar: {sorted(eksik)}"
        )


def activation_evidence_payload(
    kosu: KilitliKosuGorunumu,
    aktif_paket_satiri: Mapping[str, Any] | None,
    *,
    beklenen_madde_kumesi_sha: str,        # R-E (2026-09-08) — A4'ün 4. koşulu
) -> Mapping[str, Any]:
    """`ActivationGateEvidence`'ın jeton DIŞI alanlarını KİLİTLİ satırlardan TÜRETİR.

    İki girdinin İKİSİ de aynı işlemde `FOR UPDATE` ile kilitlenmiş satırlardır:
    `kosu` doğrulanmış koşu satırı, `aktif_paket_satiri` o sektörün o an AKTİF paket
    satırı (aktif paket yoksa `None` — K-94 ilk aktivasyon hâli). Çağıranın serbestçe
    ürettiği hiçbir değer GİRMEZ; ikinci parametre bir "çağıran girdisi" değil, mint
    fonksiyonunun kendi kilitli okumasıdır (aşağıda).

    Anahtar kümesi KAPALI ve TAM — YEDİ anahtar, sekizincisi YOKTUR:
      `activation_eligible: bool` = `kosu.sonuc == "activation_eligible"`
      `open_questions_count: int` = `len(kosu.approval_snapshot["acik_sorular"])`
                                    (ÖNCE şekil kapısı — revizyon R-F)
      `katman1_passed: bool`      = `kosu.katman1_attestation["sonuc"] == "PASS"`
      `checklist_approved: bool`  = R8 gövdesindeki DÖRT koşullu A4 kapısı (aynen)
      `expected_active_version: int | None` = `aktif_paket_satiri["version"]`
                                             (aktif satır `None` ise `None`)
      `expected_no_active: bool`  = `aktif_paket_satiri is None`
      `run_id: str`               = `kosu.run_id`
    İlk iş `_require_kosu_gorunumu(kosu, "kosu")`; sonra türetme.

    **TEK türetici:** hem `runs.mint_evidence_token` hem `writeback.build_activation_evidence`
    BUNU çağırır. İki yerde iki türetme yazılsaydı, basılan parmak izi ile kurulan kanıtın
    parmak izi sessizce ayrışabilirdi.
    """


def rollback_evidence_payload(
    plan_satiri: Mapping[str, Any],
    hedef_kosu: KilitliKosuGorunumu,
) -> Mapping[str, Any]:
    """`RollbackGateEvidence`'ın jeton DIŞI alanlarını KİLİTLİ plan satırından ve hedef
    sürümü üreten KİLİTLİ koşudan TÜRETİR.

    Anahtar kümesi KAPALI ve TAM — **BEŞ anahtar** (A1(c), fix turu 3: `onay_kapsam_sha`
    EKLENDİ; eski küme DÖRT idi):
      `manager_approved: bool` · `katman1_passed: bool` · `incident_id: str` ·
      `package_id: UUID` · `onay_kapsam_sha: str`
    Değerlerin hepsi `plan_satiri`nin ve `hedef_kosu`nun alanlarından okunur; türetme
    kuralı R11'in `build_rollback_evidence` gövdesinde yazılıdır. İlk iş
    `_require_kosu_gorunumu(hedef_kosu, "hedef_kosu")`. **TEK türetici** kuralı
    yukarıdakinin aynısıdır.
    """


def _evidence_fingerprint(evidence: Any) -> str:
    """Kanıtın kanonik parmak izi: SINIF ADI + (alan adı, değer) çiftleri, alan adına
    göre ARTAN sırada, `provenance_token` HARİÇ; `identity.canonical_sha` (Task 3, K-92)
    kuralıyla hash'lenir. İkinci bir hash kuralı YAZILMAZ."""


def _evidence_fingerprint_from_payload(cls: type, payload: Mapping[str, Any]) -> str:
    """`_evidence_fingerprint`'in NESNESİZ ikizi — aynı kanonik diziyi üretir.

    Tanım gereği: `_evidence_fingerprint(e)` ≡
    `_evidence_fingerprint_from_payload(type(e), <e'nin `provenance_token` DIŞINDAKİ tüm
    alanları>)`. İki fonksiyon TEK kuralı paylaşır; ikinci bir hash kuralı YAZILMAZ.
    `payload` anahtar kümesi sınıfın jeton-dışı alan kümesiyle **birebir** olmalıdır;
    eksik ya da fazla anahtar `ValueError`'dır (fail-closed). `RollbackGateEvidence` için
    bu küme BEŞ anahtardır (A1(c)) — `onay_kapsam_sha` parmak izine GİRER."""


# `identity.canonical_sha` bağımlılığı — DÜRÜST ETİKET, gizlenmiş kenar YOK.
# Bu iki yardımcı `sector_pipeline/identity.py`'nin `canonical_sha`'sını çağırır; yani
# `sector_package_lifecycle` (Plan 1) → `sector_pipeline` (Plan 2) yönünde BİR import
# kenarı vardır. AÇIK-3'ün gerekçesi "yönü hiç açma"ydı; ölçüldü ki bu kenar AÇIK-3
# kararıyla DEĞİL, fix turu 2'nin `_evidence_fingerprint` yazımıyla ZATEN açılmıştı —
# hüküm "ikinci bir hash kuralı YAZILMAZ" olduğu için `hashlib`'e inmek de yol değildir.
# Bağlanan sınır: kenar TEKTİR ve YAPRAK bir modüle gider.
#   (a) İzin verilen TEK import BİÇİMİ: `from app.services.sector_pipeline import identity`
#       — MODÜL importudur; addan import (`from ...sector_pipeline.identity import X`) YASAK.
#       **AD KÜMESİ REVİZE EDİLDİ 2026-09-08 — revizyon R-A (aşağıdaki revizyon kaydı).**
#       Ad kümesi TEK ada sabitlenmez ve ELLE SAYILMAZ: `identity`nin ALTÇİZGİSİZ (public)
#       yüzeyidir ve o yüzeyi ÜRETEN yapıdan türer (kapı `dir(identity)`den üretilmiş
#       listeyle kurulur, elle seçilmiş örnekle DEĞİL). Bağlayan invaryant AD SAYISI değil
#       KENARIN kendisidir: kenar TEKTİR, hedefi YAPRAKTIR (ayak (b)), ve `sector_pipeline`
#       altından başka hiçbir modüle uzanmaz (ayak (c)).
#   (b) `identity.py` hiçbir Plan 1 modülünü ve hiçbir DB yüzeyini IMPORT ETMEZ
#       (Task 3'ün kendi sözleşmesi: "YALNIZ kimlik + hash"), dolayısıyla DÖNGÜ YOKTUR.
#   (c) `sector_package_lifecycle` `sector_pipeline` altından BAŞKA hiçbir modülü
#       (`runs` · `writeback` · `engine*` · `auditors` · `readiness*` · `contracts`)
#       IMPORT ETMEZ. Kapısı yapısal testtir (aşağıda, Sahip: Task 8).


class EvidenceMintRefused(RuntimeError):        # Task 8 MODIFY — `mint_evidence_token`
    """Jeton BASILAMADI — satır yok ya da jeton basmaya uygun durumda değil.
    R9: `runs.mint_evidence_token` (Task 8) bunu fırlatır, bu yüzden Task 8'de doğar."""


def _require_token(value: Any, label: str) -> None:        # Task 8 MODIFY
    """Jeton 64 karakterlik küçük harf hex `str` olmalı — boş/whitespace/`None` RED."""
    if (type(value) is not str or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value)):
        raise TypeError(f"{label} 64 karakterlik hex jeton olmalı — köken kanıtı uydurulamaz")


def _require_kapsam_sha(value: Any, label: str) -> None:    # Task 8 MODIFY
    """A4 süpürmesi #6 · A1(c): kapsam parmak izi de 64 karakterlik küçük harf hex `str`.
    `_require_token` ile AYNI şekil kuralıdır, ayrı bir mesajla — ikinci bir NORMALİZASYON
    kuralı DEĞİLDİR; hiçbir yerde `strip()`/`lower()` uygulanmaz."""
    if (type(value) is not str or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value)):
        raise TypeError(f"{label} 64 karakterlik hex sha olmalı — kapsam mührü uydurulamaz")


@dataclass(frozen=True)
class ActivationGateEvidence:
    activation_eligible: bool                         # Plan 1 — mevcut
    open_questions_count: int                         # Plan 1 — mevcut
    katman1_passed: bool                              # Plan 1 — mevcut
    checklist_approved: bool                          # Plan 1 — mevcut
    expected_active_version: int | None = None        # Plan 1 — mevcut
    expected_no_active: bool = False                  # Task 15 (planın zaten beyan ettiği alan)
    run_id: str = field(kw_only=True)                 # Task 8 — jetonun basıldığı koşu
    provenance_token: str = field(kw_only=True)       # Task 8 — 64 hex, TEK KULLANIMLIK

    def __post_init__(self) -> None:
        ...                                           # mevcut dört `_require_*` kapısı AYNEN
        _require_flag(self.expected_no_active, "expected_no_active")   # Task 15
        # Task 8 · A4 süpürmesi #4 (fix turu 3): `isinstance` → `type(...) is not str`;
        # `str` alt sınıfı da RED. Boşluk kapısı AYRI kalır, karşılaştırma değil.
        if type(self.run_id) is not str or self.run_id.strip() == "":
            raise ValueError("run_id zorunlu — kökensiz kanıt kurulamaz")
        _require_token(self.provenance_token, "provenance_token")      # Task 8


@dataclass(frozen=True)
class RollbackGateEvidence:
    manager_approved: bool                            # Plan 1 — mevcut
    katman1_passed: bool                              # Plan 1 — mevcut
    incident_id: str = field(kw_only=True)            # Task 8 — jetonun basıldığı olay
    package_id: UUID = field(kw_only=True)            # Task 8 — geri alınan paket
    onay_kapsam_sha: str = field(kw_only=True)        # Task 8 (A1(c)) — onaylanan ÜYELİĞİN
                                                      # parmak izi; parmak izine GİRER
    provenance_token: str = field(kw_only=True)       # Task 8 — 64 hex, TEK KULLANIMLIK

    def __post_init__(self) -> None:                  # tamamı Task 8
        _require_flag(self.manager_approved, "manager_approved")
        _require_flag(self.katman1_passed, "katman1_passed")
        # A4 süpürmesi #5 (fix turu 3): `isinstance` → `type(...) is not str`.
        if type(self.incident_id) is not str or self.incident_id.strip() == "":
            raise ValueError("incident_id zorunlu")
        if type(self.package_id) is not UUID:
            raise TypeError("package_id UUID olmalı")
        _require_kapsam_sha(self.onay_kapsam_sha, "onay_kapsam_sha")   # A4 #6
        _require_token(self.provenance_token, "provenance_token")


# --------------------------------------------------------------- Task 15 MODIFY

class EvidenceProvenanceInvalid(GateNotSatisfied):
    """Kanıtın köken jetonu kilitli satırda YOK, eşleşmiyor ya da ZATEN harcanmış.
    YALNIZ `_consume_provenance` fırlatır; o da Task 15'in kalemidir."""
```

`field(kw_only=True)` seçilmesinin sebebi ölçülmüştür: yeni alanlar **varsayılansız**
olmalı, ama `expected_active_version` zaten varsayılanlı olduğu için konumsal sırada
öncelerine konamazlar. Ölçüldü — depoda kanıt sınıflarını kuran **her** çağrı anahtar
argüman kullanıyor (`tests/test_package_lifecycle.py` satır 134-148 · 704-726;
`tests/test_plan2_interface_contract.py` satır 476 · 496 · 519 · 539), yani konumsal
kurulumun kalkması mevcut hiçbir çağrıyı kırmaz.

**Üretici ayağı (jeton basımı).**

**Yardımcıların TANIMI BURADA DEĞİLDİR (AÇIK-3, gövdeye süpürüldü — fix turu 3).**
`activation_evidence_payload` · `rollback_evidence_payload` · `_evidence_fingerprint` ·
`_evidence_fingerprint_from_payload` **`sector_package_lifecycle.py`'de, Task 8 MODIFY
kaleminde** tanımlıdır (yukarıdaki blok). `runs.py` onları **yalnız çağırır**; bu dosyada
NE TANIMLARI NE İKİNCİ BİR KOPYALARI bulunur. Fix turu 2'nin metni tanımları burada
tutuyordu ve AÇIK-3 kararıyla çelişiyordu — bu tur o çelişkiyi kapatır.

```python
# runs.py  (Task 8) — yardımcıları ÇAĞIRIR, TANIMLAMAZ (AÇIK-3)
from app.services.sector_package_lifecycle import (
    ActivationGateEvidence,
    RollbackGateEvidence,
    activation_evidence_payload,
    rollback_evidence_payload,
    _evidence_fingerprint_from_payload,
)
# `runs.py` ZATEN bu modülden `_require_actor`'ı alıyor (AÇIK-1 ayak (b)); yön
# değişmez, yalnız alınan ad sayısı artar. Ters yönde import YOKTUR:
# `sector_package_lifecycle` `runs`'ı IMPORT ETMEZ — yardımcılar `runs.VerifiedRun`'a
# değil, orada tanımlı `KilitliKosuGorunumu` protokolüne yazılmıştır.

async def mint_evidence_token(
    db,
    *,
    table: str,                 # "sector_package_runs" | "package_rollback_plans" — KAPALI
    run_id: str | None,         # aktivasyon yolunda dolu, geri alma yolunda None
    incident_id: str | None,    # geri alma yolunda dolu, aktivasyon yolunda None
    package_id: UUID | None,    # geri alma yolunda dolu, aktivasyon yolunda None
) -> str:
    """Kilitli satıra 64 hex'lik YENİ bir jeton + parmak izi basar ve jetonu döner.

    **`fingerprint` PARAMETRE DEĞİLDİR (A2(d), fix turu 2, KABUL).** Önceki imza parmak
    izini ÇAĞIRANDAN alıyordu; çağıran ona istediği değeri verebildiği için jeton, kilitli
    satırla ilgisi olmayan bir kanıta basılabilirdi — R8'in *"kanıt çağırandan alınmaz"*
    doktrininin, kapatmak için var olduğu yolda yeniden açılmış hâli. **Parmak izi artık
    BURADA, KİLİTLİ SATIRDAN TÜRETİLİR:**

        # aktivasyon yolu (table == "sector_package_runs"):
        kosu        = <bu işlemde ZATEN kilitli koşu satırı, tekrar okunur>
        aktif       = <o sektörün AKTİF paket satırı, aynı işlemde FOR UPDATE; yoksa None>
        payload     = activation_evidence_payload(
                          kosu, aktif,
                          beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA)
        fingerprint = _evidence_fingerprint_from_payload(ActivationGateEvidence, payload)

        # geri alma yolu (table == "package_rollback_plans"):
        plan_satiri = <bu işlemde ZATEN kilitli plan satırı, tekrar okunur>
        hedef_kosu  = <plan satırının target_version'ını üreten KİLİTLİ koşu>
        payload     = rollback_evidence_payload(plan_satiri, hedef_kosu)
        fingerprint = _evidence_fingerprint_from_payload(RollbackGateEvidence, payload)

    Her iki yolda da yardımcılar `sector_package_lifecycle`'dan gelir (AÇIK-3); `runs.py`
    kendi türetmesini ya da kendi parmak izi hesabını YAZMAZ.

    Satır ÇAĞIRAN tarafından ZATEN kilitlenmiş olmalıdır (`FOR UPDATE`); fonksiyon kendi
    SATIR kilidini ALMAZ — kilit · basım · tüketim aynı işlemde kalsın diye. Geri alma
    yolunda **olay danışma kilidi (A1(b)) ZATEN TUTULUYOR olmalıdır**; fonksiyon
    `_lock_incident`'ı yeniden çağırır (yeniden-girişli) ve kilidi TUTMADAN basım
    YAPILMAZ. Basılamazsa (satır yok · koşu `durum != 'tamamlandi'` · plan satırı
    `durum != 'bekliyor'`) `EvidenceMintRefused` fırlatır; **boş dönüş YOKTUR.**
    """
```

```python
# writeback.py  (Task 15) — aktivasyon fabrikası
async def build_activation_evidence(db, *, run_id: str) -> ActivationGateEvidence:
    """`activate_from_snapshot`'ın İÇİNDEN, onun işleminde çağrılır. Sırayla:

      1. `run = await runs.load_verified_run(db, run_id=run_id, for_update=True)`
      2. `aktif = <o sektörün AKTİF paket satırı, aynı işlemde FOR UPDATE; yoksa None>`
      3. `payload = sector_package_lifecycle.activation_evidence_payload(run, aktif,
         beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA)` — dört
         boolean/sayaç + K-94 taban durumu + `run_id`; **TEK türetici** (A2(d)).
         **Yardımcı `runs.py`'de DEĞİL, `sector_package_lifecycle.py`'dedir (AÇIK-3,
         fix turu 3'te gövdeye süpürüldü);** `runs.activation_evidence_payload` adı
         ARTIK YOKTUR.
      4. `token = await runs.mint_evidence_token(db, table="sector_package_runs",
             run_id=run_id, incident_id=None, package_id=None)`
         — parmak izini **fonksiyonun kendisi** kilitli satırlardan türetir; buradan
         `fingerprint` GEÇİLMEZ
      5. `return ActivationGateEvidence(**payload, provenance_token=token)`

    İmzasında `evidence`, `snapshot` ya da herhangi bir `dict` parametresi YOKTUR.
    """
```

Geri alma fabrikası R11'in `runs.build_rollback_evidence`'ıdır; oraya **aynı 3-4-5 adımı**
eklenir (`table="package_rollback_plans"`, `incident_id`/`package_id` dolu, `run_id=None`).

**Tüketici ayağı — kapı BURADA (Plan 1'in kabul fonksiyonlarının İÇİ).**

```python
# sector_package_lifecycle.py  (Task 15 MODIFY)
async def _consume_provenance(db, evidence: Any, *, hedef: Mapping[str, Any]) -> None:
    # R-G5 (2026-09-11) — imza DEĞİŞTİ: `table` + `keys` yerine `hedef`. Gerekçe fix
    # turu 1'in yüksek hakem bulgusudur: jeton, kanıtın KENDİ alanlarına karşı
    # doğrulanırsa meşru basılmış bir jeton BAŞKA bir taslağa ya da onaylanmamış bir
    # hedefe karşı harcanabiliyordu. `hedef` artık ÇAĞIRANIN geçiş hedefidir ve jetonun
    # basıldığı satırla EŞLEŞMEK ZORUNDADIR. Kolon adları kapalı `_JETON_KOSULU`
    # tablosundan gelir — çağıran yalnız DEĞER verir, bilinmeyen bir kolon adı SQL'e
    # hiç ulaşmaz (eski imzanın `table`/`keys` çiftinin kapattığı şey de buydu).
    """Kilitli satırdaki jetonu ATOMİK olarak tüketir — okuma ile yazma AYRILMAZ,
    dolayısıyla iki eşzamanlı geçişten yalnız biri kazanır.

    **M1 (fix turu 2, orta, KABUL) — `RETURNING id` KALDIRILDI.** Ölçüldü (bu ekin ve
    planın kendi bağlayıcı şema metni): `social.sector_package_runs` `id uuid PK` taşır
    (plan Task 6 Produces satırı), ama `social.package_rollback_plans` **`id` kolonu
    TAŞIMAZ** — kimliği bileşiktir: `UNIQUE (incident_id, package_id)` (plan Task 6
    Produces satırı). Genel `RETURNING id` harfiyen uygulanınca HER geri alma jetonu
    tüketimi *"column \"id\" does not exist"* ile düşerdi. **Salt bu sorguyu memnun
    etmek için kimlik kolonu EKLENMEZ** — bileşik anahtar bilinçli bir tasarımdır.

    Yerine, İKİ tabloda da GERÇEKTEN var olan bir kolon döndürülür: jetonun harcanma
    zamanı. O kolon R8(c)'nin dört jeton kolonundan biridir ve iki tabloya da eklenir;
    `UPDATE` onu `now()` yaptığı için dönüş DAİMA doludur — `None` yalnız "hiçbir satır
    eşleşmedi" demektir, tam da kapının aradığı sinyal.
    """
    consumed = await db.fetchval(
        f"UPDATE social.{table} "
        "   SET kanit_jetonu = NULL, kanit_jetonu_harcandi_at = now() "
        " WHERE " + " AND ".join(f"{k} = ${i + 1}" for i, k in enumerate(keys)) +
        f"   AND kanit_jetonu = ${len(keys) + 1} "
        f"   AND kanit_jetonu_parmakizi = ${len(keys) + 2} "
        "   AND kanit_jetonu_harcandi_at IS NULL "
        " RETURNING kanit_jetonu_harcandi_at",     # M1: iki tabloda da VAR; `id` yalnız birinde
        *keys.values(), evidence.provenance_token, _evidence_fingerprint(evidence),
    )
    if consumed is None:
        raise EvidenceProvenanceInvalid(
            "kanıt kökeni doğrulanamadı: jeton yok, eşleşmiyor, kanıt alanları jetonun "
            "basıldığı andakinden farklı, ya da jeton ZATEN harcanmış — literal kurulmuş "
            "kanıt kabul edilmez"
        )
```

`activate_package` — mevcut gövdesi DEĞİŞMEZ, tek ekleme yapılır (tam imza):

```python
async def activate_package(
    db, *, package_id: UUID, evidence: ActivationGateEvidence, actor: str,
) -> None:
    _require_evidence(evidence, ActivationGateEvidence)     # AYNEN (sınıf kapısı)
    owner = _require_actor(actor)
    ...                                                     # mevcut dört alan kontrolü AYNEN
    async with db.transaction():
        sector_id, target = await _lock_and_load(db, package_id)
        ...                                                 # durum + expected_* kontrolleri AYNEN
        await _consume_provenance(                          # YENİ — geçişten hemen ÖNCE
            db, table="sector_package_runs", evidence=evidence,
            keys={"run_id": evidence.run_id, "package_id": package_id},
        )
        await _apply_status_transition(...)                 # AYNEN
```

`rollback_package` — aynı desen, anahtarlar farklı:

```python
async def rollback_package(
    db, *, sector_id: UUID, to_version: int, evidence: RollbackGateEvidence, actor: str,
) -> None:
    _require_evidence(evidence, RollbackGateEvidence)       # AYNEN
    owner = _require_actor(actor)
    ...                                                     # mevcut iki alan kontrolü AYNEN
    async with db.transaction():
        ...                                                 # hedef ve `current` çözümü AYNEN
        if evidence.package_id != current["id"]:            # YENİ — jeton HEDEFE bağlıdır
            raise EvidenceProvenanceInvalid(
                "kanıt başka bir paket için basılmış — olay/paket bağı tutmuyor"
            )
        await _consume_provenance(                          # YENİ
            db, table="package_rollback_plans", evidence=evidence,
            keys={"incident_id": evidence.incident_id, "package_id": evidence.package_id},
        )
        await _apply_status_transition(...)                 # AYNEN
```

**Kapının NE YAPMADIĞI (kapsam sınırı, dürüst etiket).** Jeton **fabrikanın koştuğunu**
kanıtlar; **yedi kapıyı YENİDEN KONTROL ETMEZ.** `load_verified_run`'ın yedi kapısı
tek yerde kalır ve burada TEKRARLANMAZ — ikinci bir kapı listesi yazmak, planın
"TEK KAPI LİSTESİ" bölümünün yasakladığı şeydir.

**Anahtar şekli tablo başına GERÇEKTİR (M1).** `keys` sözlüğü her tablonun kendi kimlik
şekline bağlanır ve iki tabloda da var olan kolonlardan kurulur:
`sector_package_runs` → `{"run_id": …, "package_id": …}` (`run_id` `UNIQUE`, `package_id`
hedef bağı); `package_rollback_plans` → `{"incident_id": …, "package_id": …}` — tablonun
`UNIQUE (incident_id, package_id)` kimliğinin ta kendisi. Genel bir kimlik kolonu
varsayan hiçbir ifade KULLANILMAZ.

**Jeton tek kullanımlıktır ve HEDEFE bağlıdır.** `package_id`/`incident_id` anahtarları
`WHERE` yan tümcesinde olduğu için A koşusu için basılmış bir jeton B paketini aktive
edemez; `kanit_jetonu_harcandi_at IS NULL` koşulu tekrar oynatmayı kapatır.

**Güncellenmesi ZORUNLU Plan 1 testleri — sahip: Task 15.** Plan zaten bu iki dosyayı
Task 15'in *"DAVRANIŞ DEĞİŞİKLİĞİ — Plan 1 testleri"* kaleminde sayıyor ve Step 5b'de
koşuyor; kapsam o kalemin altında genişler:

| Dosya · yer | Ne değişir |
|---|---|
| `tests/test_package_lifecycle.py::_activation_evidence` (satır 134-142) | Fabrikaya dönüşür: `pkg_db` + gerçek koşu satırı alır, `mint_evidence_token` ile jeton basar, kanıtı onunla kurar |
| `tests/test_package_lifecycle.py::_rollback_evidence` (satır 145-148) | Aynısı, `package_rollback_plans` satırı üzerinden |
| `tests/test_package_lifecycle.py` — geçişi BAŞARIYLA tamamlayan her test (`test_first_activation_single_step` 268 · `test_activate_archives_previous_then_activates` 284 · `test_activate_accepts_matching_base_version` 349 · `test_rollback_restores_previous_version` 420 · `test_rollback_allowed_while_candidate_activation_gates_fail` 475 · `test_concurrent_activation_of_same_draft_single_winner` 813 · `test_concurrent_activation_of_different_drafts_is_serializable` 952) | İki fabrikadan geçtikleri için imza değişikliğini **kendiliğinden** devralır; ek düzenleme YALNIZ jeton kurulumu gerektiren yerlerdedir |
| `tests/test_package_lifecycle.py::test_activation_evidence_rejects_loose_values` (704) · `::test_rollback_evidence_rejects_loose_values` (721) | Parametre listesine jeton vakaları eklenir (boş · kısa · büyük harf hex · `None`) |
| `tests/test_package_lifecycle.py::test_rollback_evidence_is_not_the_activation_evidence` (461) | **Ölçüldü: kırılmaz.** Testin `activation_only` kümesi dört adı sayıyor; `provenance_token` iki sınıfta da bulunduğu için kesişim boş kalır |
| `tests/test_plan2_interface_contract.py` satır 476 · 496 · 519 · 539 | Dört kanıt kurulumu jetonlu fabrikadan geçer |

**Kanıt testi · sahibi (R8(c)):**
- **Ana ispat — literal kanıt her İKİ geçişte de reddedilir:**
  `test_activation_refuses_literal_constructed_evidence` (gerçek `run_id`, uydurma
  `provenance_token="0"*64` → `EvidenceProvenanceInvalid`; paket `draft` KALIR ve
  `package_events`'e satır YAZILMAZ) ·
  `test_rollback_refuses_literal_constructed_evidence` (aynısı `rollback_package` için;
  aktif sürüm DEĞİŞMEZ) — **Sahip: Task 15**, `tests/test_package_lifecycle.py`.
- `test_activation_token_is_single_use` (aynı kanıtla ikinci aktivasyon RED) ·
  `test_rollback_token_is_single_use` ·
  `test_activation_token_is_bound_to_its_package` (A koşusunun jetonu B paketini aktive
  edemez) · `test_rollback_token_is_bound_to_its_incident_and_package` ·
  `test_tampered_evidence_field_breaks_fingerprint` (jeton gerçek, ama
  `checklist_approved` `False`→`True` çevrilmiş → RED) — **Sahip: Task 15**.
- Pozitif kontroller: `test_activation_succeeds_with_minted_evidence` ·
  `test_rollback_succeeds_with_minted_evidence` — **Sahip: Task 15**.
- **A2(d) — parmak izi ÇAĞIRANDAN alınmaz (fix turu 2):**
  `test_mint_evidence_token_takes_no_fingerprint_parameter` (yapısal: `inspect.signature`'da
  `fingerprint` YOK — hükmün ana ispatı) ·
  `test_minted_fingerprint_matches_evidence_built_by_the_factory` (basılan parmak izi,
  fabrikanın kurduğu kanıtın `_evidence_fingerprint`'iyle BİREBİR; pozitif kontrol) ·
  `test_minted_fingerprint_tracks_the_locked_row_not_the_caller` (satır alanı değişince
  parmak izi değişir; çağıranın elinde parmak izini etkileyecek hiçbir girdi yoktur) ·
  `test_evidence_payload_key_set_is_closed` (aktivasyonda YEDİ, geri almada **BEŞ**
  anahtar — A1(c) `onay_kapsam_sha`'yı ekledi; fazlası da eksiği de RED) — **Sahip: Task 8**,
  `tests/test_pipeline_runs.py`.
- **AÇIK-3'ün gövdeye süpürüldüğünün kapıları (fix turu 3) — Sahip: Task 8,
  `tests/test_pipeline_runs.py`:**
  `test_runs_module_defines_no_evidence_payload_or_fingerprint_helper` (yapısal: `runs.py`
  kaynağında `def activation_evidence_payload` · `def rollback_evidence_payload` ·
  `def _evidence_fingerprint` · `def _evidence_fingerprint_from_payload` **YOK**; dördü de
  `sector_package_lifecycle`'dan import edilir — AÇIK-3'ün ana ispatı) ·
  `test_lifecycle_imports_no_pipeline_module_other_than_identity` (yapısal:
  `sector_package_lifecycle.py` `app.services.sector_pipeline` altından YALNIZ `identity`
  import eder; `runs` · `writeback` · `engine*` · `auditors` · `readiness*` · `contracts`
  adları GEÇMEZ — döngüsel import yasağının kapısı) ·
  `test_payload_helpers_do_not_import_verified_run` (yapısal: yardımcılar
  `runs.VerifiedRun`'a değil `KilitliKosuGorunumu`'ne yazılmıştır) ·
  `test_kosu_gorunumu_field_set_is_closed` (SEKİZ ad birebir; `VerifiedRun` protokolü
  KARŞILAR — pozitif kontrol) ·
  `test_payload_helper_refuses_object_missing_a_view_field` (bir alanı eksik sahte nesne →
  `TypeError`, fail-closed).
- `test_evidence_token_minted_only_inside_the_two_factories` (yapısal depo-geneli tarama:
  `mint_evidence_token(` çağrısı YALNIZ `writeback.build_activation_evidence` ve
  `runs.build_rollback_evidence` gövdelerinde; `tests/` muaf) — **Sahip: Task 15**,
  `tests/test_write_surface_authorization.py`.
- Şema kapıları: `test_evidence_token_columns_present_and_nullable` (iki tabloda da dört
  kolon) · `test_evidence_token_check_requires_fingerprint_and_mint_time` (jeton dolu ama
  parmak izi/basım zamanı boş → CHECK RED) — **Sahip: Task 6**,
  `tests/test_migration_036.py`.
- **M1 — anahtar şekli (fix turu 2):**
  `test_rollback_token_consumption_succeeds_on_composite_key_table` (gerçek şemaya karşı
  koşar: `package_rollback_plans`'te jeton tüketimi başarılı — `id` kolonu olmadığı hâlde;
  hükmün ana ispatı) ·
  `test_consume_provenance_returns_spend_timestamp_not_row_id` (yapısal: `_consume_provenance`
  sorgu metni `RETURNING id` İÇERMEZ) — **Sahip: Task 15**,
  `tests/test_package_lifecycle.py`.

Task 14'ün düzeltilmiş Consumes satırı:

> `Consumes: Task 8 runs.load_verified_run (+ VerifiedRun); Task 6 sector_package_runs;
> package_events.log_package_event.` — `Task 13 EngineResult` **ÇIKARILDI**: Task 14 motor
> sonucunu nesne olarak DEĞİL, koşu satırından okur.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 14** — plan 1545 (Consumes) ve plan
1560-1563 (`to_activation_evidence`) GEÇERSİZ. **Task 15** — plan 1669-1684 aralığındaki F18
zinciri aynen geçerli, üstüne "tek kurulum yeri" hükmü EKLENİR; Files listesindeki
`Modify: sector_package_lifecycle.py` kalemi (plan 1619-1620) **`_consume_provenance` +
`EvidenceProvenanceInvalid` + iki geçiş fonksiyonunun jeton doğrulaması** ile genişler.
**Bu listede OLMAYANLAR (hepsi Task 8'in kalemidir, R9 + AÇIK-3):** dört parmak izi/yük
yardımcısı · `KilitliKosuGorunumu` · `_require_kosu_gorunumu` · `_require_token` ·
`_require_kapsam_sha` · `EvidenceMintRefused` · iki kanıt sınıfının köken alanları.
Produces listesine `writeback.build_activation_evidence` EKLENİR.
**Task 6** — 036 şemasına iki tabloya birden DÖRT jeton kolonu + bir CHECK eklenir.
**Task 8** — Produces listesine `mint_evidence_token` + `EvidenceMintRefused` EKLENİR
(ikisi de Task 8'de doğar; `EvidenceMintRefused`'un TANIM YERİ `sector_package_lifecycle.py`
ama YAZAN GÖREV Task 8'dir — R9: onu `runs.mint_evidence_token` fırlatır ve Task 8 <
Task 15). Task 8 Files listesine
`Modify: apps/social/backend/app/services/sector_package_lifecycle.py` EKLENİR; Produces
listesine **DÖRT yardımcı + `KilitliKosuGorunumu` + `_require_kosu_gorunumu` +
`_require_token` + `_require_kapsam_sha` + iki kanıt sınıfının KÖKEN ALANLARI** girer
(AÇIK-3 + R8(c)'nin alan düzeyi bölünmesi, fix turu 3).
**Plan gövdesi** — *"Bu planın Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER"* bölümüne köken
jetonu kalemi `expected_no_active`'in yanına yazılmıştır (bu fix turunda uygulandı).

**Kanıt testi · sahibi:**
- `test_no_module_constructs_activation_evidence_outside_writeback` — depo geneli yapısal
  tarama: `ActivationGateEvidence(` çağrısı YALNIZ `writeback.py`'de bulunur; tanım dosyası
  (`sector_package_lifecycle.py`) ve `tests/` dizini **açıkça muaftır** (muafiyet testin
  içinde yazılıdır). **Sahip: Task 15**, `tests/test_write_surface_authorization.py`.
- `test_approval_module_exposes_no_evidence_constructor` — `approval` modülünde
  `to_activation_evidence` adı YOK ve `ActivationGateEvidence` import EDİLMİYOR.
  **Sahip: Task 14**, `tests/test_approval_surface.py`.

---

## R9 — Bir görev, SONRAKİ görevde doğan yüzeyi tüketemez

**Kusur (plan satırları):** Task 15'in aktivasyonu `readiness_attestation`'ı doğruluyor
(plan 1677 · 1728), ama o alanın tek üreticisi `readiness.attest` **Task 17'de** doğuyor
(plan 1898-1900). Task 15'in pozitif kontrolü
`test_activation_succeeds_with_full_attestation_chain` (plan 1731) bu yüzden **yazıcısız**:
Task 15 kendi sırasında tamamlanamaz. Bu, planın `hazirlik-onayla` komutu için zaten
kapattığını söylediği sınıfın (plan 1894-1897) süpürülmemiş kardeşidir.

**Kural (kontrolör):** **YAZICI Task 15'in kapsamına taşınır.** Task 17 yirmi maddelik
listenin değerlendirmesini ve CLI alt komutunu TUTAR.

**Kusur (fix turu 1, yüksek, KABUL) — R9'un KENDİ açtığı delik.** İlk yazımın imzası
`attest_readiness(..., onaylandi: bool, kapi_maddeleri, sinyal_maddeleri, actor)` biçimindeydi:
**onay boolean'ını ve madde demetlerini doğrudan ÇAĞIRANDAN alıyordu.** Yani herhangi bir iç
çağıran `onaylandi=True, kapi_maddeleri=()` yazıp K-69 kapısını atlayabilirdi — ekin her yerde
yasakladığı **uydurulmuş boolean**'ın ta kendisi, üstelik F18'in kapatmak için var olduğu yolda.

**Kural (kontrolör):** **YAZICI Task 15'in kapsamına taşınır** ve **`onaylandi` PARAMETRE
OLMAKTAN ÇIKAR — YAZICI onu TÜRETİR.** Türetmenin dayandığı kanonik madde kümesi, yazıcıdan
ÖNCE var olan paylaşılan bir modüle alınır. Task 17 yirmi maddelik listenin
**değerlendirmesini** ve CLI alt komutunu TUTAR (R9'un sıra düzeltmesi AYNEN geçerlidir).

**Bağlayıcı sözleşme — kanonik madde kümesi (Task 8 CREATE):**

```python
# apps/social/backend/app/services/sector_pipeline/readiness_items.py   (Task 8 CREATE)
# YALNIZ kimlik + sınıflandırma. Değerlendirme mantığı YOK (o Task 17'nindir), DB YOK.

MADDE_SINIFLARI: tuple[str, ...] = ("kapi", "sinyal")   # KAPALI — iki değer

@dataclass(frozen=True)
class ChecklistItem:
    madde_id: str        # kanonik madde kimliği
    sinif: str           # MADDE_SINIFLARI içinden — KAPALI
    otomatik: bool       # otomatik ön-kontrolle ölçülebiliyor mu (Task 17 tüketir)
    baslik: str          # R-G2 (2026-09-11): maddenin insan-okunur etiketi.
                         # `MADDE_KUMESI_SHA`ya GİRMEZ — başlık bir insan etiketidir ve
                         # bir yazım düzeltmesi eski tasdikleri geçersizleştirmemelidir.
                         # Kimlik · sınıf · ölçülebilirlik kapının ANLAMINI değiştirir,
                         # onlar hash'e girer.

MADDELER: tuple[ChecklistItem, ...]
# YİRMİ madde. Kimlikler ve sınıflar spec §13.4'ün YİRMİ maddesinden ÖLÇÜLEREK
# doldurulur — burada UYDURULMAZ (İlke 9, M1 ile aynı disiplin). Küme KAPALIDIR.
# Bağlayıcı olan iki şey ölçüm gerektirmez ve şimdiden yazılıdır:
#   (a) madde sayısı YİRMİ'dir (plan 1891: "spec §13.4'ün 20 maddesi");
#   (b) 15. madde ("kör değerlendirmede sektörel ayrışma gözlendi") `sinif="sinyal"`dir
#       ve tamamlanma kapısına GİRMEZ (plan 1919-1921 · 1924-1925).

KANIT_KOLONLARI: frozenset[str]
# R-G9 (F1, 2026-09-11) — hazırlık PROBLARININ koşu satırından okuduğu kolonların
# KAPALI kümesi. Burada yaşar çünkü kolon ADLARIDIR: kimlik, değerlendirme mantığı
# değil; modülün "yalnız kimlik + sınıflandırma, DB YOK" sözleşmesini bozmaz.
# Küme ELLE SEÇİLMEZ — `readiness.py` AST ile ayrıştırılıp her `kanit.kosu["..."]`
# okuması toplanır ve kümeye BİREBİR eşitlik aranır (kapının pozitif kontrolü de
# vardır: hiç okuma bulunmazsa test DÜŞER). Yeni bir prob yeni bir kolon okursa
# test KIRILIR; kolon parmak izinin dışında sessizce kalamaz.

KAPI_MADDELERI:   frozenset[str]   # {i.madde_id for i in MADDELER if i.sinif == "kapi"}
SINYAL_MADDELERI: frozenset[str]   # {i.madde_id for i in MADDELER if i.sinif == "sinyal"}

MADDE_KUMESI_SHA: str = identity.canonical_sha(MADDELER)
# A4 (fix turu 2): kanonik madde kümesinin BUGÜNKÜ parmak izi — modül yüklenirken BİR KEZ
# hesaplanır. Hem `attest_readiness` bunu yazar, hem `activate_from_snapshot` buna karşı
# karşılaştırır; iki yerde iki hesap YAZILMAZ. Madde eklenince/çıkınca/sınıfı değişince
# değer değişir ve eski tasdikler kendiliğinden GEÇERSİZLEŞİR.
```

**Bağlayıcı sözleşme — DÜZELTİLMİŞ yazıcı (tam imza):**

```python
# runs.py  (Task 8 — TEK doğum görevi) — attest_katman1/attest_katman2'nin kardeşi
# Task 15 bu yüzeyi yalnız TÜKETİR; ikinci bir yazıcı ya da ikinci bir tanım YOKTUR.
# (Fix turu 3: başlık önce "Task 15 MODIFY eder" diyordu ve R9 bölümünün gövdesiyle
#  çelişiyordu — gövde Task 15'i tüketici sayıyor. Doğum görevi TEKTİR: Task 8.)
class ReadinessAttestationRefused(ValueError):
    """Onay TÜRETİLEMEDİ — verilen kapı kümesi kanonik kümeyle örtüşmüyor. Kayıt YAZILMAZ."""


async def attest_readiness(
    db,
    *,
    run_id: str,
    kapi_maddeleri: tuple[str, ...],      # operatörün işaretlediği `kapi` madde kimlikleri
    sinyal_maddeleri: tuple[str, ...],    # `sinyal` sınıfındakiler — tamamlanma kapısına GİRMEZ
    actor: str,
) -> None:
    """F18: operatörün TEK onayını koşu satırının `readiness_attestation` alanına kalıcı
    yazar (kim · ne zaman · hangi maddeler · **hangi kanıta dayanarak**).

    **R-G9 (F1, Eray kararı 2026-09-11) — yük `kanit_parmakizi` TAŞIR.** Değer
    PARAMETRE DEĞİLDİR; yazıcı onu `kanit_parmakizi(db, run_id=...)` ile
    veritabanından TÜRETİR (R8: kanıt çağırandan alınmaz). Aktivasyon aynı izi
    yeniden hesaplar ve ayrışma varsa paketi AKTİVE ETMEZ.

```python
# runs.py  (Task 8) — TEK türetici
async def kanit_parmakizi(db, *, run_id: str) -> str: ...
#   kanıt kümesi = (a) koşunun ham artefakt satırları (kind · source · brief_ref)
#                + (b) koşu satırının `readiness_items.KANIT_KOLONLARI` kolonları
#   `readiness.kanit_parmakizi` (Task 17) BUNA VEKİLDİR, kendi hesabını yazmaz.
#   `content_md` hash'e GİRMEZ: tablo salt-eklemedir (032 tetikleyicisi), var olan
#   satırın içeriği DEĞİŞEMEZ; değişebilen tek şey küme ÜYELİĞİdir.
```


    **`onaylandi` PARAMETRE DEĞİLDİR — burada TÜRETİLİR:**

        onaylandi = (set(kapi_maddeleri) == readiness_items.KAPI_MADDELERI)

    ve aşağıdaki BEŞ koşuldan biri düşerse kayıt hiç YAZILMAZ
    (`ReadinessAttestationRefused`; sessiz `onaylandi=False` kaydı da ÜRETİLMEZ):

      (1) `kapi_maddeleri` BOŞ;
      (2) `KAPI_MADDELERI`nin bir üyesi `kapi_maddeleri`'nde YOK          → eksik madde;
      (3) `kapi_maddeleri`'nde `MADDELER`de bulunmayan bir kimlik var     → tanınmayan madde;
      (4) `kapi_maddeleri`'nde sınıfı `sinyal` olan bir kimlik var, ya da
          `sinyal_maddeleri`'nde sınıfı `kapi` olan bir kimlik var        → yanlış sınıf;
      (5) iki demetten birinde TEKRAR EDEN kimlik var (küme boyu ≠ demet boyu).

    `actor` Plan 1'in KANONİK aktör kapısından geçer:
    `sector_package_lifecycle._require_actor` (**TANIM YERİ DÜZELTİLDİ 2026-09-08, revizyon
    R-D:** bu ad yaşam döngüsü modülünde bir YENİDEN-DIŞAVURUMDUR; tanım
    `app/services/package_events.py` `require_actor`tadır — ölçüldü, satır 258-280: `str`
    değilse ya da `strip()` sonrası boşsa `ValueError`, aksi hâlde kırpılmış kimlik).
    İkinci bir aktör kuralı YAZILMAZ.

    Yazılan kayıt:
        {"onaylandi": True, "actor": <doğrulanmış>, "at": <now>,
         "kapi_maddeleri": [...], "sinyal_maddeleri": [...],
         "madde_kumesi_sha": readiness_items.MADDE_KUMESI_SHA}
    """
```

- **Kayıt YALNIZ onay hâlinde doğar; `onaylandi` yazılan her kayıtta `True`'dur** — dürüst
  etiket: onaylanmamış hâlin kaydı YOKTUR, çünkü aktivasyon "kayıt yok" hâlini zaten RED
  sayar. Alan yine de yazılır, çünkü aktivasyonun okuduğu sözleşme odur.
- **`madde_kumesi_sha` BİR KAPIDIR, damga değil (A4, fix turu 2, yüksek, KABUL).**
  Önceki yazımda bu alan **yazılıyor ama HİÇBİR YERDE OKUNMUYORDU**:
  `activate_from_snapshot` yalnız `readiness_attestation["onaylandi"] is True` arıyordu.
  Sonuç ölçülebilir bir delikti — kontrol listesine zorunlu bir madde eklendiğinde ya da
  bir madde `sinyal`den `kapi`ya çevrildiğinde, ESKİ listeye verilmiş `True` tasdikler
  **yeni listenin altında kullanılmaya devam ederdi**. Hiçbir kapının okumadığı hash
  süstür. **Bağlanan hüküm:** `activate_from_snapshot`
  `readiness_attestation["madde_kumesi_sha"]` alanının
  (a) VAR ve boş-olmayan bir `str` olmasını, (b) `readiness_items.MADDE_KUMESI_SHA`'ya
  **BİREBİR EŞİT** olmasını arar. **GERİYE UYUM YOLU YOKTUR:** alanı olmayan, boş olan ya
  da eski liste sürümüne ait tasdik **REDDEDİLİR** — "eski kayıtlarda alan yoksa kontrolü
  atla" biçiminde bir yedek yol YAZILMAZ (fail-closed). Eski tasdiğin tek çıkışı yeni
  listeye karşı **yeniden onaydır** (`hazirlik-onayla` tekrar koşar).
- Parametreler **ilkel tiplerdir**, `ReadinessReport` DEĞİL: `ReadinessReport` Task 17'de
  doğar ve Task 15'in ona bağımlı olması bağımlılığı yine ters çevirirdi. `readiness_items`
  ise Task 8'de doğduğu için ileri-bağımlılık YOKTUR (R9'un kendi kuralı).
- `activate_from_snapshot` (Task 15) **BEŞ** koşulu birden arar — dördü A4'ün (fix turu
  3'te KESKİNLEŞTİRİLDİ), beşincisi R-G9'un (F1, 2026-09-11: tasdikteki `kanit_parmakizi`
  aktivasyon anındaki TAZE izle BİREBİR eşit olmalı; alan yoksa kapı düşer): (1) `onaylandi is True`; (2) `madde_kumesi_sha` anahtarı VAR ve
  değeri `type(...) is str`; (3) `strip()` sonrası BOŞ DEĞİL; (4) değerin KENDİSİ —
  kırpılmamış, küçültülmemiş hâliyle — `readiness_items.MADDE_KUMESI_SHA`'ya EŞİT.
  **Karşılaştırma NORMALİZASYONSUZDUR:** `strip()` yalnız (3)'ün boşluk kapısında,
  karşılaştırılan değerin ÜZERİNDE DEĞİL, ayrı bir kapı olarak kullanılır. Fix turu 2'nin
  yazımı `….strip() == KANONİK` diyordu ve ölçüldü ki `" <kanonik> "` biçiminde
  boşluk-sarmalı bir değer o kapıdan GEÇİYORDU — "BİREBİR EŞİT" metni ile kodun kendisi
  çelişiyordu. Herhangi bir koşul düşerse — tasdik eksik, `onaylandi` `False`,
  `madde_kumesi_sha` yok/boş/yanlış tipte/boşluk-sarmalı ya da farklı — aktivasyon
  REDDEDİLİR.

**A4 SÜPÜRMESİ — bu ekin GETİRDİĞİ her sha/jeton karşılaştırması tek tek okundu
(fix turu 3, DOKUZ nokta).** Ölçüt: *karşılaştırılan değer, karşılaştırmadan önce
normalize ediliyor mu (`strip`/`lower`/`casefold`/varsayılan düşüşü)?*

| # | Nokta | Bulgu · yapılan |
|---|---|---|
| 1 | `activate_from_snapshot` → `madde_kumesi_sha` | **KUSURLU → DÜZELTİLDİ** (yukarıdaki dört koşul; hükmün ana vakası) |
| 2 | `_consume_provenance` SQL: `kanit_jetonu = $n` · `kanit_jetonu_parmakizi = $n` | temiz — SQL `=` metin eşitliği; `btrim`/`lower` YOK ve EKLENMEZ |
| 3 | `_require_token` (64 küçük-harf hex) | temiz — `type(value) is not str` + uzunluk + karakter kümesi; normalizasyon YOK |
| 4 | `ActivationGateEvidence.__post_init__` → `run_id` | **GEVŞEKTİ → SIKILDI:** `isinstance(..., str)` yerine `type(...) is not str` (alt sınıf da RED); boşluk kapısı ayrı kalır |
| 5 | `RollbackGateEvidence.__post_init__` → `incident_id` | **GEVŞEKTİ → SIKILDI:** aynı düzeltme |
| 6 | `RollbackGateEvidence.__post_init__` → `onay_kapsam_sha` (A1(c), YENİ) | `_require_kapsam_sha` — `type(...) is str` + 64 küçük-harf hex; normalizasyon YOK |
| 7 | `build_rollback_evidence` → satırdaki `onay_kapsam_sha` ile bugünkü `incident_scope_sha` | **PROSE'DU → BAĞLANDI:** `type(...) is str` + boş-olmama + NORMALİZASYONSUZ `==` |
| 8 | `approve_incident_rollback` idempotans karşılaştırması (`onay_kapsam_sha` EŞİTSE dokunma) | **PROSE'DU → BAĞLANDI:** aynı kural; `strip()`'li karşılaştırma bayat mührü taze sanardı |
| 9 | `check_snapshot_agreement` (3) ve (4) — `unit_snapshot_sha` eşitlikleri | **PROSE'DU → BAĞLANDI:** `type(...) is str` + NORMALİZASYONSUZ `==` (K-79/K-100) |

**Sonuç: dokuz noktanın BİRİ kusurluydu (#1), İKİSİ gevşek tip kapısı taşıyordu (#4 · #5),
ÜÇÜ yalnız prose'du ve bağlandı (#7 · #8 · #9), BİRİ bu turda doğdu ve doğarken bağlandı
(#6), İKİSİ zaten temizdi (#2 · #3).** Yeni bir normalizasyon kuralı hiçbir noktaya
EKLENMEDİ.

**Kanıt testi · sahibi (A4 süpürmesi):**
- `test_activation_refused_when_madde_kumesi_sha_is_whitespace_padded`
  (`" " + MADDE_KUMESI_SHA + " "` → aktivasyon RED; #1'in ana ispatı) — **Sahip: Task 15**,
  `tests/test_pipeline_writeback.py`.
- `test_evidence_run_id_rejects_str_subclass` · `test_evidence_incident_id_rejects_str_subclass`
  (#4 · #5) — **Sahip: Task 8**, `tests/test_pipeline_runs.py` (alanları ve kapılarını
  yazan görev Task 8'dir — R9 bölünmesi + R4).
- `test_rollback_evidence_rejects_non_hex_scope_sha` (#6) — **Sahip: Task 8**,
  `tests/test_pipeline_runs.py`.
- `test_build_rollback_evidence_refuses_whitespace_padded_scope_sha` (#7) ·
  `test_approve_incident_treats_whitespace_padded_scope_sha_as_stale` (#8) — **Sahip: Task 8**,
  `tests/test_pipeline_runs.py`.
- `test_snapshot_agreement_rejects_whitespace_padded_snapshot_sha` (#9) — **Sahip: Task 10**,
  `tests/test_auditor_orchestration.py`.

**KALAN yüzeyler (Task 17, değişmez):** `readiness.CHECKLIST: tuple[Item, ...]` (plan 1891) ·
`readiness.evaluate(db, *, run_id) -> ReadinessReport` (plan 1892; **imza R-G6 ile
düzeltildi, 2026-09-11** — koşu kimliği olmadan ön-kontrolün okuyacağı artefakt YOKTUR:
yirmi maddenin otomatik ölçülen HEPSİ koşu satırını ya da o koşunun ham artefaktlarını
okur) · `kapi`/`sinyal` sınıflandırması
(plan 1909-1914 · 1920-1925) · CLI alt komutu **`hazirlik-onayla`** (plan 1893-1897) — komut
`readiness.evaluate`'i çağırır, operatörün TEK onayını alır ve **`runs.attest_readiness`**'e
yazdırır. **Tek fark (H5):** `readiness.CHECKLIST` ikinci bir liste DEĞİLDİR — kimlik ve
sınıf bilgisini `readiness_items.MADDELER`'den **kurar**; Task 17 üstüne yalnız
değerlendirme (`otomatik ön-kontrol` sonucu, `elle` etiketi) ekler. Çift kayıt YASAK.

**SİLİNEN yüzey:** `readiness.attest(db, *, run_id, report, actor)` (plan 1898-1900) —
YOKTUR; yerine `runs.attest_readiness` geçer.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — Files listesine
`Create: apps/social/backend/app/services/sector_pipeline/readiness_items.py` EKLENİR
(plan 979-981); Produces listesine `MADDELER` · `MADDE_SINIFLARI` · `KAPI_MADDELERI` ·
`SINYAL_MADDELERI` · **`MADDE_KUMESI_SHA`** (A4) · `ChecklistItem` · `attest_readiness` ·
`ReadinessAttestationRefused` girer. **Task 15** — Consumes satırına `Task 8 runs.attest_readiness` EKLENİR (plan 1618-1629);
Task 15 yazıcıyı **yalnız tüketir**. **Files listesine `Modify: runs.py` EKLENMEZ**
(fix turu 3 düzeltmesi: önceki metin hem "Modify" diyor hem "tüketir" diyordu; tüketen
görev dosyayı değiştirmez — yazıcının TEK doğum görevi Task 8'dir).
**Task 17** — plan 1898-1900 GEÇERSİZ; Produces listesinden çıkar, Step 3b'nin komut testi
aynen kalır ama tasdik yazıcısı olarak `runs.attest_readiness` çağrılır; `readiness.py`
`readiness_items`'ı IMPORT eder.

**Kanıt testi · sahibi:**
- **H5'in negatif kapıları — `onaylandi` uydurulamaz (Sahip: Task 8,
  `tests/test_pipeline_runs.py`):**
  `test_attest_readiness_takes_no_onaylandi_parameter` (yapısal: `inspect.signature`'da
  `onaylandi` YOK — hükmün ana ispatı) ·
  `test_attest_readiness_refuses_empty_gate_set` (boş küme) ·
  `test_attest_readiness_refuses_missing_gate_item` (eksik madde) ·
  `test_attest_readiness_refuses_unknown_item` (tanınmayan kimlik) ·
  `test_attest_readiness_refuses_signal_item_in_gate_set` (yanlış sınıf) ·
  `test_attest_readiness_refuses_gate_item_in_signal_set` (yanlış sınıf, ayna vaka) ·
  `test_attest_readiness_refuses_duplicate_item` (tekrar) ·
  `test_attest_readiness_refuses_blank_actor` (Plan 1 aktör kapısı) ·
  **pozitif kontrol:** `test_attest_readiness_persists_actor_time_and_items` — tam kapı
  kümesiyle çağrılınca kayıt DOĞAR, `onaylandi is True` ve `madde_kumesi_sha` yazılıdır.
  (Bu ad plan 1937 satırındaki `test_attest_persists_actor_and_time`'ın yerine geçer;
  **R9'un ilk yazımı bu testi Task 15'e vermişti — H5 ile yazıcının doğduğu göreve,
  Task 8'e taşınır.** R9'un SIRA düzeltmesi değişmez: yazıcı hâlâ Task 15'ten ÖNCEDİR ve
  Task 17 hâlâ değerlendirme + CLI'yi tutar.)
- **Madde kümesinin kapıları (Sahip: Task 8, `tests/test_pipeline_runs.py`):**
  `test_checklist_item_set_has_twenty_items` · `test_item_classes_are_closed`
  (`MADDE_SINIFLARI` dışında `sinif` RED) ·
  `test_gate_and_signal_sets_partition_the_item_set` (kesişim boş, birleşim tam) ·
  `test_item_ids_are_unique` ·
  `test_katman2_signal_item_is_not_a_gate_item` (15. madde `sinyal`, plan 1919-1921).
- `test_activation_succeeds_with_full_attestation_chain` (plan 1731) artık yazıcısı olan bir
  pozitif kontroldür — **Sahip: Task 15** (değişmedi).
- **A4'ün kapıları — hash'i OKUYAN gate (fix turu 2), Sahip: Task 15,
  `tests/test_pipeline_writeback.py`:**
  **`test_activation_refused_when_madde_kumesi_sha_missing_or_blank`** (tasdikte alan yok
  ya da `""`/`"   "` → aktivasyon RED; geriye-uyum yedeği OLMADIĞININ ispatı) ·
  **`test_activation_refused_when_madde_kumesi_sha_differs_from_current`** (tasdik eski
  liste sürümüne verilmiş; `MADDELER`'e bir `kapi` maddesi eklenmiş → aktivasyon RED) ·
  **`test_activation_succeeds_when_madde_kumesi_sha_matches_current`** (pozitif kontrol —
  kapının her şeyi reddetmediğinin ispatı).
- `test_madde_kumesi_sha_changes_when_item_set_changes` (madde eklenince/çıkınca ve bir
  maddenin `sinif`'i değişince değer DEĞİŞİR) · `test_madde_kumesi_sha_uses_identity_canonical_rule`
  (ikinci hash kuralı yok) — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_hazirlik_onayla_writes_attestation` (plan 1943) — **Sahip: Task 17** (değişmedi;
  yalnız çağırdığı yüzeyin adı `runs.attest_readiness` olur).
- `test_checklist_is_built_from_readiness_items` (çift kayıt yasağı: `readiness.CHECKLIST`
  kimlikleri `readiness_items.MADDELER` ile birebir) · `test_checklist_has_twenty_items`
  (plan 1929'daki mevcut test, artık `readiness_items` üzerinden okur) — **Sahip: Task 17**,
  `tests/test_readiness_checklist.py`.

---

## R10 — Operatörün koşmak zorunda olduğu her adımın CLI girişi olur

**Kusur (plan satırları):** kanonik sıra ve Task 19 Step 9 (plan 2071) **yazım kapısını**
koşmayı şart koşuyor, ama Task 16'nın alt komut listesinde (plan 1781-1797) taslak yazımını
ya da K-106 yerinde güncellemeyi çağıran hiçbir komut yok. `writeback.write_draft_from_run`
ve `update_draft_from_run` (plan 1635-1636) operatör tarafından ERİŞİLEMEZ.

**Kural (kontrolör):** eksik alt komutlar eklenir.

**Bağlayıcı sözleşme — Task 16 alt komut listesine EKLENEN:**

| Alt komut | Çağırdığı servis yüzeyi | Not |
|---|---|---|
| `yazim` | `writeback.write_draft_from_run(db, run_id=…, actor=…) -> UUID` | Yazım kapısı; düzeltme koşusunu REDDEDER (plan 1658-1660) |
| `duzeltme-yaz` | `writeback.update_draft_from_run(db, run_id=…, actor=…) -> None` | K-106 yerinde güncelleme; soyağacı ZORUNLU (plan 1660-1662) |
| `deaktive-et` | `sector_package_lifecycle.deactivate_package(db, package_id=…, actor=…)` | R11 — `hedefsiz` satırın TEK çıkışı (K-38) |

Üçü de Task 16'nın genel invariantına tabidir: resmî koşu başlatan her alt komut ilk iş
olarak `contracts.require_pin` çağırır (plan 1803-1804); argparse · açık `--database-url` ·
deterministik çıktı · anlamlı çıkış kodu (plan 1799-1800).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 16** — plan 1781-1797 aralığındaki liste üç
komutla genişler. **Task 19** — Step 9 (plan 2071) artık adı konmuş bir komuta işaret eder.

**Kanıt testi · sahibi:**
- `test_yazim_subcommand_calls_write_draft_from_run` ·
  `test_yazim_subcommand_refuses_correction_run` ·
  `test_duzeltme_yaz_subcommand_calls_update_draft_from_run` ·
  `test_deaktive_et_subcommand_calls_deactivate_package` ·
  `test_every_run_subcommand_requires_pin` (plan 1828 — yeni üç komut da kapsam içindedir)
  — **Sahip: Task 16**, `tests/test_pipeline_cli.py`.

---

## R11 — Geri alma kanıtının üreticisi olur; beyan edilen çıkışın komutu olur

**Kusur (plan satırları):** (a) `rollback_package(db, *, sector_id, to_version, evidence:
RollbackGateEvidence, actor)` (plan 272) iki boolean isteyen bir kanıt sınıfı taşıyor —
ölçüldü (`sector_package_lifecycle.py::RollbackGateEvidence`, satır 116-130): `RollbackGateEvidence(manager_approved: bool,
katman1_passed: bool)`, ikisi de `bool` olmak ZORUNDA ve `_require_evidence` yalnız SINIFI
doğruluyor. `execute_rollback_plan` (plan 1074-1079) ve CLI `olay-geri-al` (plan 1791-1796)
bu iki boolean'ı **uydurmak** zorunda kalırdı — F18'in aktivasyon yolunda kapattığı deliğin
kardeş yolda süpürülmemiş hâli. (b) `hedefsiz` satırın plan metninde yazılı TEK çıkışı
deaktivasyondur (plan 1072-1073) ama CLI listesinde (plan 1781-1797) deaktivasyon komutu
YOK.

**Kural (kontrolör):** geri alma kanıtını **veritabanından** kuran bir üretici adlandırılır —
kilitli koşu + kayıtlı yönetici onayı; çağıran-taraflı boolean ASLA. Deaktivasyon alt komutu
eklenir (R10'daki `deaktive-et`).

**Bağlayıcı sözleşme:**

```python
# runs.py  (Task 8)
class RollbackEvidenceUnavailable(RuntimeError):
    """Kanıt DB'den KURULAMADI — geri alma satırı `hata` olarak kapanır.
    Uydurulmuş boolean ile geçiş YOLU YOKTUR."""

async def build_rollback_evidence(
    db,
    *,
    incident_id: str,
    package_id: UUID,
) -> RollbackGateEvidence:
    """İki boolean'ı da OKUR, hiçbirini kabul etmez; jetonu da BURADA basar.

    **İLK İŞ: `await _lock_incident(db, incident_id)`** (A1(b), yol #3) — plan satırı
    `FOR UPDATE` ile okunmadan, `onay_*` alanları ve bugünkü kapsam hesaplanmadan ÖNCE.
    Kilit yeniden-giriş serbesttir; çağıran (yürütücü) onu zaten almış olsa bile bu çağrı
    KOŞULSUZ alır. Çağıran, plan satırını `FOR UPDATE` ile ZATEN kilitlemiş olmalıdır;
    satır kilidi olay kilidinin YERİNE GEÇMEZ — yeni satır eklenmesini yalnız olay kilidi
    serileştirir.

    manager_approved — bu olay kimliği için kayıtlı yönetici onayı VAR MI (AÇIK-1'in
        ÜÇ koşulu: `onay_actor` · `onaylandi_at` · `onay_kapsam_sha` dolu VE kapsam
        parmak izi bugünkü satır kümesiyle EŞLEŞİYOR).
        **Kapsam karşılaştırması NORMALİZASYONSUZDUR (A4 süpürmesi #7):** satırdaki
        `onay_kapsam_sha` `type(...) is str` olmalı, `strip()` sonrası boş olmamalı ve
        `incident_scope_sha(<olayın BUGÜNKÜ TÜM satırları>)` ile **ham hâliyle** EŞİT
        olmalıdır; `strip()`/`lower()` UYGULANMAZ.
        Herhangi biri düşerse → RollbackEvidenceUnavailable.

    katman1_passed — plan satırının HEDEF sürümünü (`target_version`) üreten koşunun
        `katman1_attestation["sonuc"] == "PASS"` kaydı. Hedef paketin `run_id` bağı yoksa,
        koşu satırı yoksa, `durum != 'tamamlandi'` ise ya da tasdik yoksa
        → RollbackEvidenceUnavailable (F18: tasdik kanıttır, boolean değil).

    Köken jetonu (R8(c)) — iki boolean türetildikten SONRA (A2(d) ile GÜNCELLENDİ:
    parmak izi ARTIK BURADAN GEÇİLMEZ, `mint_evidence_token` onu kilitli plan satırından
    kendisi türetir; **yardımcı `sector_package_lifecycle`'dan gelir — AÇIK-3**):
        payload = sector_package_lifecycle.rollback_evidence_payload(
                      <kilitli plan satırı>, <hedef koşu>)
        # payload BEŞ anahtar taşır (A1(c)): manager_approved · katman1_passed ·
        # incident_id · package_id · onay_kapsam_sha
        token = await mint_evidence_token(db, table="package_rollback_plans",
                    run_id=None, incident_id=incident_id, package_id=package_id)
        return RollbackGateEvidence(**payload, provenance_token=token)
    `onay_kapsam_sha` kanıtın alanı olduğu için `_evidence_fingerprint`'e GİRER; bayat
    kapsamla basılmış bir jeton harcanamaz (A1(c), ikinci savunma).
    Basım başarısızsa `EvidenceMintRefused` → çağıran onu `RollbackEvidenceUnavailable`
    gibi ele alır ve plan satırını `durum='hata'` ile kapatır.
    """
```

- `execute_rollback_plan` (plan 1074-1079) her paket için **kendi işlemini açar, İLK
  ifade olarak `await _lock_incident(db, incident_id)` çağırır** (A1(b), yol #4) ve o
  işlemi kanıt kurulumu ile jeton harcamasının İKİSİNİ de kapsayacak biçimde açık tutar:
  ÖNCE `build_rollback_evidence`, SONRA aynı işlemde
  `sector_package_lifecycle.rollback_package`. İkisi ayrı işlemlere bölünürse kilit
  "doğrula → harca" aralığını kapatmaz ve A1(b)'nin kapattığı yarış geri açılır.
  `RollbackEvidenceUnavailable` yakalanır ve o plan satırı **`durum='hata'`**
  (036'nın mevcut kapalı kümesinden — plan 797) + `reason` ile kapanır. **Yeni durum değeri
  ÜRETİLMEZ**; `hedefsiz` bu vaka için KULLANILMAZ (`hedefsiz` yalnız güvenli sürüm yokluğu
  demektir, plan 1072).
- `hedefsiz` satırların tek çıkışı `deaktive-et` alt komutudur (R10 tablosu); `olay-geri-al`
  onları ayrı başlıkta raporlar (plan 1792-1794) ve **kendiliğinden deaktive ETMEZ** —
  deaktivasyon operatörün ayrı kararıdır (K-38).

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — Produces listesine
`build_rollback_evidence` + `RollbackEvidenceUnavailable` EKLENİR (plan 1074-1079 civarı);
`execute_rollback_plan`'ın gövde sözleşmesi bağlanır (A1(b): olay kilidi + tek işlem).
**Task 6** — `build_rollback_evidence`'ın OKUDUĞU kolonlar (`onay_*` üçlüsü ve jeton
dörtlüsü) 036'da doğar; R11'in kanıt üreticisi o şema olmadan yazılamaz, bu yüzden Task 6
bu hükme bağlıdır (fix turu 3'te açıkça yazıldı — Task 6'nın bağlayıcı satırında R11
zaten vardı, karşılığı burada yoktu). **Task 16** — `deaktive-et` eklenir
(plan 1781-1797).

**DÜZELTME (fix turu 1):** ilk yazımın *"Plan 1 arayüzü DEĞİŞMEZ; `RollbackGateEvidence`
alan kümesine dokunulmaz"* cümlesi **ARTIK GEÇERSİZDİR.** R8(c) her iki kanıt sınıfına da
köken jetonu alanları ekliyor; `RollbackGateEvidence` `incident_id` · `package_id` ·
`provenance_token` kazanır (ölçülen bugünkü hâli:
`sector_package_lifecycle.py::RollbackGateEvidence`, satır 116-130 — yalnız iki `bool`).
Bu değişiklik planın *"Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER"* bölümünde **beyan
edilmiştir**; sessiz bir arayüz kırılması bırakılmaz.

**Kanıt testi · sahibi:**
- `test_build_rollback_evidence_reads_manager_approval_from_db` ·
  `test_build_rollback_evidence_reads_katman1_from_target_run_attestation` ·
  `test_build_rollback_evidence_refuses_when_target_run_unprovable` ·
  `test_executor_marks_row_hata_when_evidence_unavailable` ·
  `test_executor_never_constructs_evidence_from_literals` (yapısal: `runs.py` içinde
  `RollbackGateEvidence(` çağrısı YALNIZ `build_rollback_evidence` gövdesinde) ·
  `test_build_rollback_evidence_mints_a_single_use_token` (R8(c) ayağı: dönen kanıtın
  `provenance_token`'ı plan satırındaki `kanit_jetonu` ile aynı ve `kanit_jetonu_harcandi_at`
  hâlâ NULL) — **Sahip: Task 8**, `tests/test_pipeline_runs.py`.
- `test_deaktive_et_subcommand_calls_deactivate_package` ·
  `test_olay_geri_al_does_not_auto_deactivate_hedefsiz` — **Sahip: Task 16**,
  `tests/test_pipeline_cli.py`.

---

## R12 — Beyan edilen her dosya değişikliğinin onu YAPAN bir adımı olur

Üç ayrı vaka; her biri için karar ayrı verilir.

### R12(a) — Task 20: beyan DÜZELTİLİR · Task 6: SAHİPLİK VERİLİR

**Kusur:** Task 20 Files satırı `test_plan2_interface_contract.py` için *"(genişletilir)"*
diyor (plan 2094) ama Step 1-7'nin (plan 2096-2120) hiçbiri onu genişletmiyor.

**Karar: BEYAN DÜZELTİLİR** (kapanış görevine adım eklenmez). Dosyanın Plan 2 satırlarının
sahibi Task 3 (plan 503 · 603-605), **Task 6 (aşağıda)** ve Task 15'tir
(plan 1624 · 1742-1745); Task 20 onu yalnız **koşar** (Step 1'in tam suite'i içinde).
Kapanış görevine yeni sözleşme satırı yazdırmak kapsam eklemek olurdu.

Düzeltilmiş Files satırı:

> `- Test: apps/social/backend/tests/test_plan2_interface_contract.py` **(yalnız koşulur —
> satırlarının sahibi Task 3, Task 6 ve Task 15)**

**Geçersiz kılınan satır:** plan 2094.

#### R12(a2) — 032 MANİFESTİ: sahibi TASK 6'dır (fix turu 1, yüksek, KABUL)

**Kusur (R12(a)'nın ilk yazımının açtığı boşluk):** ilk yazım Task 20'nin sahipliğini
kaldırdı ama **hiçbir göreve vermedi.** Oysa Task 6 (migration 036) bu Python dosyasını
**kırıyor.**

**Ölçüm (2026-08-30, taze okuma):**
- `apps/social/backend/tests/test_plan2_interface_contract.py` satır 110'da
  `EXPECTED_032_MANIFEST` tanımlı; `"sector_research_artifacts"` → `"indexes"` anahtarı
  **TAM İKİ** kayıt taşıyor (satır 131-140): `sector_research_artifacts_pkey` ve
  `idx_sector_research_artifacts_slug_run`.
- `test_migration_032_relation_manifest_is_closed` (satır 350-371) kümeleri
  `observed[facet] == expected[facet]` ile **KAPALI** karşılaştırır: *"habersiz eklenmesi
  de bu testi düşürür"* (satır 355).
- 036, aynı tabloya K-09 için `UNIQUE (run_id, source, kind)` ekliyor (plan 804) → **üçüncü
  indeks** doğar → **bu Python testi DÜŞER.**
- Planın Task 6 Files satırı yalnız **SQL** dosyalarını sürüm-farkında yapıyor
  (plan 756-757); **032 SQL doğrulayıcısını sürüm-farkında yapmak bu Python manifestini
  DÜZELTMEZ** — ayrı iki artefakttır.

**Karar: TASK 6'YA SAHİPLİK VERİLİR.** Task 6 Files listesine EKLENİR:

> `- Modify: apps/social/backend/tests/test_plan2_interface_contract.py`
>   **(`EXPECTED_032_MANIFEST` indeks beklentisi sürüm-farkında yapılır — 036'nın kırdığı
>   dosyayı 036'yı yazan görev onarır)**

**İndeks adı sözleşmeyle SABİTLENİR** (katalogdan tahmin edilmez): 036'daki kısıt
`CONSTRAINT sector_research_artifacts_run_source_kind_key UNIQUE (run_id, source, kind)`
adıyla yazılır; PostgreSQL aynı adla indeks üretir.

**Task 6'ya EKLENEN adım:**

> - [ ] **Step 4c:** `tests/test_plan2_interface_contract.py`'ın 032 manifestini
>   **SÜRÜM-FARKINDA** yap. Bağlanan davranış:
>   (a) `EXPECTED_032_MANIFEST[...]["indexes"]` **iki kayıtla KALIR** — 032 tek başına
>       uygulandığında beklenen küme budur ve değişmez;
>   (b) `test_migration_032_relation_manifest_is_closed` `indexes` yüzeyini karşılaştırırken
>       **yalnız adı geçen** `sector_research_artifacts_run_source_kind_key` indeksini
>       **ek olarak kabul eder** (036 uygulanmışsa);
>   (c) **başka HERHANGİ bir fazla indeks hâlâ REDDEDİLİR** — kapalılık vaadi zayıflamaz,
>       muafiyet **tek ada** yazılır, "036 sonrası her şey serbest" DEĞİL;
>   (d) diğer dört yüzey (`columns` · `constraints` · `triggers` · `relation`) **hiç
>       gevşemez.**
>   Koş: `cd apps/social/backend && python -m pytest tests/test_plan2_interface_contract.py -v`
>   — Beklenen: PASS.

**Kanıt testi · sahibi (hepsi Task 6,
`apps/social/backend/tests/test_plan2_interface_contract.py`):**
- `test_032_manifest_alone_expects_exactly_two_artifact_indexes` — 036 uygulanmadan beklenti
  hâlâ iki kayıttır (davranışın geri uyumu).
- `test_032_manifest_accepts_named_k09_index_after_036` — 036 sonrası
  `sector_research_artifacts_run_source_kind_key` kabul edilir (pozitif kontrol).
- `test_032_manifest_still_rejects_unnamed_extra_index` — muafiyet listesinde OLMAYAN
  fazladan bir indeks eklenince test hâlâ DÜŞER (kapalılığın ispatı; Task 6 Step 2'nin
  `test_unnamed_extra_index_still_rejected` testinin Python manifest karşılığı).
- Task 6 Step 6 (plan 925-927) zaten `test_plan2_interface_contract.py`'ı adıyla sayarak
  koşuyor — bu adım o beklentiyi karşılanabilir hâle getirir.

### R12(b) — Task 5: ADIM EKLENİR

**Kusur:** Task 5 `shared/n8n-workflows/turkey-calendar-update.json`'ı değiştiriyor
(plan 679) ama bu workflow mevcut sözleşme testlerinden HİÇ geçmiyor; Task 16 Step 7b
(plan 1859-1865) aynı üçlüyü **yalnız yeni hata-bildirimi workflow'u** için ekliyor.
Ölçüldü (`tests/test_notifications.py:818 · 838 · 855`): `test_workflow_reads_no_process_env` ·
`test_workflow_carries_a_stable_id` · `test_workflow_credentials_are_bound` üçü de
`_admin_workflow()` üzerinde koşuyor — takvim workflow'u kapsam DIŞI.

**Karar: TASK 5'E ADIM EKLENİR.**

> - [ ] **Step 4b:** Değiştirilmiş takvim workflow'unu mevcut sözleşme testlerine SOK —
>   `tests/test_notifications.py`'a aynı üçlü: `test_calendar_workflow_carries_stable_id` ·
>   `test_calendar_workflow_reads_no_process_env` ·
>   `test_calendar_workflow_credentials_are_bound`. Koş:
>   `cd apps/social/backend && python -m pytest tests/test_notifications.py -v`
>   — Beklenen: PASS. Gerekçe ölçülü: canlı kurulumda `$env` kapalı ve import sabit kimlik
>   istiyor ([[decisions/2026-08-26-n8n-credential-over-env]]).

**Etkilenen görev:** Task 5 — Files listesine
`Modify: apps/social/backend/tests/test_notifications.py` EKLENİR (plan 676-680).
**Kanıt testi · sahibi:** üç test, **Task 5**.

### R12(c) — Task 2: `_SABLON.md` beyanı DOĞRUDUR, kalemin İNİŞ YERİ yazılır

**Kusur:** Task 2 `_SABLON.md`'yi Modify diye sayıyor (plan 453) ama altı düzeltmenin ve
yedi sweep kaleminin hiçbiri oraya indiğini SÖYLEMİYOR (plan 461-479).

**Ölçüm (2026-08-30, dış depo):** `_SABLON.md:49-51` · `hakem-sentez-gorevi.md:78` ·
`hakem-denetci-gorevi.md:74` — üçü de serbest `[kanal-bağımlı: X]` etiketini taşıyor.
Yani 6. düzeltme kalemi (kanal anahtar uzayının dört değerle KAPATILMASI, plan 469-472)
**üç dosyaya birden** iner ve `_SABLON.md` beyanı DOĞRUDUR.

**Karar: BEYAN KORUNUR, kalem 6 iniş yerlerini AÇIKÇA yazar.** Düzeltilmiş kalem metni:

> 6. **Kanal anahtar uzayı dört değerle KAPATILIR** — `whatsapp_hatti` · `fiziksel_magaza` ·
>    `randevu_sistemi` · `eticaret_sitesi`. **İniş yerleri (ölçüldü 2026-08-30):**
>    `_SABLON.md:49-51` · `hakem-sentez-gorevi.md:78` · `hakem-denetci-gorevi.md:74` —
>    üçünde de serbest `X` yer alıyor. Kod tarafı Plan 1'de
>    `sector_packages.py::CHANNEL_KEYS` olarak zaten kapalı; sözleşme ona hizalanır.

**Geçersiz kılınan satırlar:** plan 469-472. **Kanıt:** Task 2 Step 1/Step 3 sweep raporunun
6. kalemi artık üç dosya + satır işaretiyle ölçülür (test değil, ölçülmüş rapor kalemi —
dürüst etiket).

---

## R13 — Ölçüm adımının sonucu ÖNCEDEN KARARLAŞTIRILMIŞ olamaz

**Kusur (plan satırları):** Task 5 Step 1 (plan 721-723) K-112 için *"Bulguya göre Task
12'nin özel gün kontrolü hizalanır. Ölçmeden bağlama"* diyor; oysa Task 12 aynı davranışı
ZATEN bağlıyor (plan 242 · 1356-1366): üretim yolunda sessiz düşüş + zorunlu maskeli log,
yazım kapısında tipli hata ile fail-closed.

**Kural (kontrolör):** **BAĞLAMA KALIR** — spec türevidir, ölçüm türevi değildir. Task 5'in
adımı dürüst şekilde yeniden adlandırılır: bugünkü davranışı, hata-enjeksiyon testinin karşı
koşacağı **regresyon TABANI** olarak kaydeder.

**Bağlayıcı sözleşme — Task 5 Step 1'in YENİ metni (plan 721-723 yerine):**

> - [ ] **Step 1:** **BUGÜNKÜ DAVRANIŞI KAYDET (K-112 regresyon tabanı — bağlama DEĞİL):**
>   takvim erişilemezken (a) özel gün enjeksiyon yolunun ve (b)
>   `sector_package_lifecycle.insert_draft`'ın bugün ne yaptığını fixture ile ölç; sonucu
>   `docs/research/2026-08-27-k112-takvim-erisilemezlik-taban.md`'ye yaz — komut + taze çıktı
>   ile (İlke 9). **Bu adım hiçbir davranışı BAĞLAMAZ ve Task 12'nin bağladığı davranışı
>   değiştirmez** (plan 230-242 · 1356-1366: bağlama spec §11/§3.4 türevidir). Ölçümün tek
>   işlevi, Task 12'nin hata-enjeksiyon testlerinin karşı koşacağı tabanı vermektir. Ölçülen
>   davranış bağlanan davranıştan farklı çıkarsa bu bir REGRESYON DEĞİL, planın istediği
>   değişikliktir ve taban notunda öyle etiketlenir.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 5** — plan 721-723 GEÇERSİZ.
**Task 12** — plan 1356-1366 ve plan 1433-1435 satırlarındaki üç K-112 testi AYNEN geçerli; bağlama
onlarındır.

**Kanıt testi · sahibi:** yeni test yok. Kapıyı kanıtlayan testler Task 12'nindir:
`test_calendar_unavailable_yields_empty_special_day_context_and_logs` ·
`test_calendar_unavailable_fails_draft_write_closed` ·
`test_calendar_unavailable_log_is_masked` (plan 1433-1435). Task 5'in çıktısı ölçülmüş bir
taban notudur, kapı değildir.

---

## R14 — Pin'in negatif invariantının sözleşme testi

Bu hüküm **R1'e katlanır** ve burada bir kez daha yazılmaz: negatif invariantın metni
(*"kirli çalışma ağacı tek başına pini düşürmez"*), onu kanıtlayan test
(`test_verify_passes_with_dirty_external_worktree`, **Sahip: Task 1**) ve commit yolunu
kapatan kalem (`kosu/` → dış depo `.gitignore`,
`test_external_repo_gitignores_run_folder`, **Sahip: Task 2**) R1'de tam metinle bağlanmıştır.

Tek ek hüküm — **çift kayıt yasağı:** aynı invariant için ikinci bir test yazılmaz ve
`verify_pin`'in kapı kümesi (plan 423-426, DÖRT kapı) **genişletilmez**; negatif invariant
bir kapı değil, kapı kümesinin **kapalılığının** ifadesidir.

**Etkilenen görev · geçersiz kılınan satırlar (fix turu 3'te AÇIKÇA YAZILDI):** **Task 1** —
`verify_pin`'in negatif invariantı ve `test_verify_passes_with_dirty_external_worktree`
sahipliği. **Task 2** — `kosu/` `.gitignore` kalemi ve
`test_external_repo_gitignores_run_folder` sahipliği. Metin R1'de durur; bu satır yalnız
**hangi görevlerin bağlandığını** adıyla sayar, çünkü iki görevin de bağlayıcı satırında
R14 yazılıdır ve karşılığının ekte adı konmuş olması gerekir (süpürme kuralı 2).

---

## AÇIK-1 KAPANDI — kontrolör kararı, 2026-08-30

**Karar: B seçeneği, olay düzeyinde onay.** `social.package_rollback_plans` ÜÇ kolon kazanır:

```sql
onay_actor      text        NULL,   -- onayı veren yönetici kimliği
onaylandi_at    timestamptz NULL,   -- onay zamanı
onay_kapsam_sha text        NULL,   -- onaylanan satır KÜMESİNİN kanonik parmak izi

CONSTRAINT package_rollback_plans_onay_butun
  CHECK (num_nonnulls(onay_actor, onaylandi_at, onay_kapsam_sha) IN (0, 3)),
  -- üçü BİRLİKTE dolar, BİRLİKTE boşalır

CONSTRAINT package_rollback_plans_onay_actor_dolu
  CHECK (onay_actor IS NULL OR btrim(onay_actor) <> '')
  -- boş/yalnız-boşluk kimlik onay SAYILMAZ
```

**Neden üç kolon ve iki CHECK — fix turu 1 bulgusu (yüksek, KABUL).** İlk yazımın tek
CHECK'i `(onay_actor IS NULL) = (onaylandi_at IS NULL)` idi ve **ölçüldü ki
`onay_actor = ''` değerini KABUL EDER**: iki kolon da NULL olmaz, kısıt geçer, ve
`build_rollback_evidence` **boş kimlikli bir onay** için `manager_approved=True` üretirdi —
R11'in yasakladığı uydurulmuş boolean'ın veri katmanından gelen hâli. İkinci kusur: onay
**onayladığı satırlara BAĞLI DEĞİLDİ** — onaydan sonra bir satırın `target_version`'ı
değişse bile satır "yönetici onaylı" görünmeye devam ederdi.

**Ayak (b) — servis katmanında fail-closed aktör doğrulaması, Plan 1'in KENDİ kapısıyla.**
**Ölçüldü (TAZE, 2026-09-08 — revizyon R-D; eski metin İKİ şeyi birden yanlış
gösteriyordu).** Kapının TANIMI `app/services/package_events.py` `require_actor`tadır
(satır 258-280); `sector_package_lifecycle` onu `_require_actor` adıyla ALIR (satır 37) ve
kuralın SAHİBİ yaşam döngüsüdür. Tanımın yaprak modülde durmasının sebebi ölçülmüş bir
DÖNGÜdür: `log_package_event` dalı da aynı kapıyı kullanır ve ters yönde bir import
`ImportError` ile düşer. Eski metin tanımı yaşam döngüsü modülünde ve satır 147-150'de
gösteriyordu; **davranış ve aşağıdaki import biçimi DEĞİŞMEDİ** —
`isinstance(actor, str)` değilse ya da
`actor.strip()` boşsa `ValueError("actor zorunlu — sahipsiz yaşam döngüsü işlemi yazılmaz")`
fırlatır, aksi hâlde **kırpılmış** kimliği döner. `runs.approve_incident_rollback` ve
`runs.attest_readiness` (R9) **bu kapıyı kullanır**; `runs.py` onu açıkça alır:

```python
from app.services.sector_package_lifecycle import _require_actor as require_actor
```

Ad modül-özeldir; buna rağmen **ikinci bir aktör kuralı yazmak yerine özel bir adı yeniden
kullanmak** bilinçli tercihtir — iki kapı iki davranış demektir ve ekin kapattığı sınıf tam
olarak budur. Kolona yazılan değer `require_actor`'ın döndürdüğü **kırpılmış** kimliktir,
dolayısıyla `btrim(onay_actor) <> ''` CHECK'i servis yolunda hiç tetiklenmez; CHECK, servis
dışı bir yazımın (elle SQL, gelecekteki ikinci çağıran) son savunmasıdır.

**Ayak (c) — onay, olayın KANONİK satır kümesine MÜHÜRLENİR.**

```python
# runs.py  (Task 8)
class IncidentMembershipLocked(RuntimeError):
    """Olayın ÜYELİĞİ artık değiştirilemez — yürütme BAŞLAMIŞ durumda. Satır YAZILMAZ."""


def incident_scope_sha(rows: Sequence[Mapping]) -> str:
    """Olayın DEĞİŞMEZ ÜYELİĞİNİN parmak izi — yürütme durumunun DEĞİL.

    **A3 (fix turu 2, yüksek, KABUL) — girdi kümesi DEĞİŞTİ.** Önceki yazım girdiyi
    *"o `incident_id`'ye ait `durum='bekliyor'` satırlar"* diye tanımlıyordu. Ölçüldü ki
    bu, N satırlı bir olayın TAMAMLANMASINI imkânsız kılar: yürütücü paket-paket koşar ve
    her tamamlanan satırı `bekliyor`dan ÇIKARIR; ilk başarılı geri almadan sonra yeniden
    hesaplanan kapsam zorunlu olarak KÜÇÜLÜR ve ikinci satırın onayı reddedilir.
    Kurtarma da çelişkiliydi: metin *"kapsam kayarsa yeni onay gerekir"* diyordu, ama
    `approve_incident_rollback` zaten damgalı satırı yeniden damgalamayı REDDEDİYORDU.

    **Girdi (BAĞLAYICI): o `incident_id`'ye ait TÜM plan satırları — `durum`'dan
    BAĞIMSIZ** (`bekliyor` · `tamamlandi` · `hata` · `hedefsiz` hepsi dâhil). Her satırdan
    yalnız **kimlik ve hedef** alanları alınır:
    `(package_id, observed_active_version, target_version, evidence_class)`.
    **`durum` ve `reason` hash'e GİRMEZ** — onlar yürütme durumudur, üyelik değil.
    032 desenli değişmezlik tetikleyicisi (aşağıda, ayak (d)) bu DÖRT alana `incident_id`'yi
    de ekleyerek BEŞ alanı kilitler; `incident_id` hash'e ayrıca girmez çünkü hash'lenen
    küme zaten TEK bir olaya aittir. Yani kilitlenen küme, hash'lenen kümenin üstünde
    yalnız kümeyi TANIMLAYAN alanı taşır.
    Satırlar `package_id` metnine göre ARTAN sıralanır ve `identity.canonical_sha`
    (Task 3, K-92) ile hash'lenir. İkinci bir hash kuralı YAZILMAZ.
    """
```

**A1(a) — ÜYELİK DEĞİŞİKLİĞİNİN ADI KONMUŞ SÖZLEŞMESİ (fix turu 3, yüksek, KABUL).**

```python
# runs.py  (Task 8)
async def amend_rollback_plan(
    db,
    *,
    incident_id: str,          # DEĞİŞTİRİLECEK olayın kimliği — `build_rollback_plan`'ın döndürdüğü değer
    affected: AffectedSet,     # olayın YENİ TAM üyeliği (delta DEĞİL — mutlak küme)
    actor: str,                # `require_actor` (Plan 1 kanonik kapısı) ile doğrulanır
) -> tuple[int, int]:
    """MEVCUT bir olayın üyeliğini YENİDEN YAZAR; olay AÇMAZ. `(eklenen, silinen)` döner.

    **`build_rollback_plan`'dan FARKI — iki fonksiyon karıştırılamaz:**
      | | `build_rollback_plan` | `amend_rollback_plan` |
      |---|---|---|
      | olay kimliği | ÜRETİR (döner) | PARAMETRE olarak ALIR |
      | mevcut satırlar | yoktur | okunur, karşılaştırılır |
      | dönüş | `str` (yeni olay kimliği) | `tuple[int, int]` (eklenen, silinen) |
      | pencere kapısı | uygulanmaz (olay yeni) | ZORUNLU (`IncidentMembershipLocked`) |

    Adımlar — SIRA BAĞLAYICIDIR ve hepsi TEK işlemdedir:

      1. `owner = require_actor(actor)`  — boş/`str` olmayan kimlik → `ValueError`,
         hiçbir satır yazılmaz.
      2. `await _lock_incident(db, incident_id)`  — **olay danışma kilidi; HERHANGİ bir
         `durum` ya da kapsam OKUMASINDAN ÖNCE** (A1(b)). Kilitsiz okunan pencere kararı
         yarışa açıktır.
      3. Olayın TÜM satırları `FOR UPDATE` ile okunur.
      4. **Pencere kapısı:** en az bir satır `durum ∈ ('tamamlandi', 'hata')` ise
         `IncidentMembershipLocked` — **hiçbir satır yazılmaz** (fail-closed).
      5. `affected`'tan hedef satır kümesi kurulur (hedef sürüm seçimi
         `build_rollback_plan`'ın GÜVENLİ HEDEF kuralının aynısıdır; ikinci bir kural
         YAZILMAZ). Kümede olup satırı olmayanlar EKLENİR; satırı olup kümede olmayanlar
         SİLİNİR. Hem eklenen hem silinen satırlar yalnız `durum='bekliyor'` ya da
         `durum='hedefsiz'` olabilir; başka durumdaki satır adım 4'te zaten yakalanmıştır.
      6. **Mühürlere DOKUNULMAZ.** `amend_rollback_plan` `onay_*` kolonlarını YAZMAZ;
         üyelik değişince kalan damgalar kendiliğinden BAYATLAR (`onay_kapsam_sha` artık
         yeni üyeliğin sha'sına eşit değildir) ve olay yürütülemez hâle gelir. Yeniden
         mühürleme operatörün ayrı ve GÖRÜNÜR adımıdır: `olay-onayla` (madde 3).
      7. Eklenen/silinen satır sayısı 0/0 ise fonksiyon yine de başarıyla döner
         (`(0, 0)`); çağıran bunu "değişiklik yok" diye raporlar, hata SAYMAZ.
    """
```

**A1(b) — TEK OLAY KİLİDİ: dördü de AYNI kilidi, AYNI noktada alır (fix turu 3, yüksek, KABUL).**

**Kusur (ölçüldü, fix turu 2 metni):** üyelik değişimi, onay/yeniden mühürleme, kanıt
kurulumu ve yürütme için **paylaşılan tek bir kilit adı yoktu**; her yol yalnız kendi
satırlarını `FOR UPDATE` ediyordu. Bu, satır-yerel kilitlerin kapatamadığı bir aralık
bırakır: yürütücü olayın BUGÜNKÜ kapsamını doğrulayıp kanıt basarken, planlayıcı aynı
olaya **başka bir satır** ekleyebilir (yeni satır kimsenin kilidinde değildir). Kanıt zaten
basılmıştır ve — fix turu 2'de `onay_kapsam_sha` parmak izine GİRMEDİĞİ için — bayat
kapsamla basılmış o kanıt hâlâ HARCANABİLİRDİ. **Sıralı testler bu aralığı göremez.**

```python
# runs.py  (Task 8)
_OLAY_KILIT_ONEKI: str = "sektor_paketi.olay:"     # KAPALI — tek önek, ikincisi YOKTUR

async def _lock_incident(db, incident_id: str) -> None:
    """Olay kapsamlı, İŞLEM ÖMÜRLÜ danışma kilidi. TEK kilit adı budur.

        await db.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended($1, 0))",
            _OLAY_KILIT_ONEKI + incident_id,
        )

    - **İşlem ömürlüdür:** `COMMIT`/`ROLLBACK` ile kendiliğinden bırakılır; elle
      `unlock` YOKTUR ve yazılmaz.
    - **Yeniden giriş serbesttir:** aynı işlem içinde ikinci kez çağrılması anında
      döner. Bu yüzden aşağıdaki DÖRT yol da kilidi KOŞULSUZ alır — "acaba çağıran
      almış mıydı" diye sorulmaz (o soru sessiz atlamanın kapısıdır).
    - **İkinci bir kilit adı YAZILMAZ:** satır düzeyi `FOR UPDATE` kilitleri AYNEN kalır,
      ama üyelik/kapsam kararlarının serileştirilmesi YALNIZ bu kilidin işidir.
    """
```

**Kilidi ALAN DÖRT yol — her biri için "nerede" ayrı ayrı yazılıdır:**

| # | Yol (modül · görev) | Kilidi ALDIĞI NOKTA |
|---|---|---|
| 1 | `runs.amend_rollback_plan` (Task 8) | Adım 2 — `require_actor`'dan hemen SONRA, olayın satırları ve `durum`'ları OKUNMADAN ÖNCE |
| 2 | `runs.approve_incident_rollback` (Task 8) | İşlemin İLK ifadesi (`require_actor`'dan sonra), `durum='bekliyor'` satırlar ve `incident_scope_sha` girdisi OKUNMADAN ÖNCE |
| 3 | `runs.build_rollback_evidence` (Task 8) | Gövdesinin İLK ifadesi — plan satırı `FOR UPDATE` ile okunmadan, `onay_*` alanları ve bugünkü kapsam hesaplanmadan ÖNCE (`mint_evidence_token` de içeride yeniden çağırır; yeniden-girişli) |
| 4 | `runs.execute_rollback_plan` (Task 8) | Her paket için açtığı işlemin İLK ifadesi — o paketin plan satırı okunmadan ÖNCE; kilit `build_rollback_evidence` **ve** `sector_package_lifecycle.rollback_package` çağrılarının İKİSİNİ de kapsayacak biçimde işlem sonuna kadar TUTULUR |

**Kapsama BAĞLAYICI kuralı (4. satırın gerçek anlamı):** kanıt kurulumu ile jeton
harcaması **AYNI bağlantıda ve AYNI dış işlemde** koşar. `rollback_package`'ın kendi
`async with db.transaction()` bloğu bu dış işlemin İÇİNDE bir savepoint'tir; ayrı bir
işlem AÇMAZ. Bu, kilidin "doğrula → harca" aralığının tamamını kapsamasının tek yoludur ve
bu ekte **bağlayıcı olan budur** — iç içe işlem bloğunun savepoint'e karşılık gelmesi
sürücü davranışıdır, kapının kendisi değil. Tek paketlik yol **ayrı bir komut DEĞİLDİR** (R-G7,
2026-09-11 — AÇIK-2'nin kararı DEĞİŞTİ): tek satırlık bir olay açılır ve `olay-geri-al`
aynı sarmalayıcıyı kullanır — kilidi alır, kanıtı kurar, harcar, commit eder.

**A1(c) — KEMER VE ASKI: `onay_kapsam_sha` parmak izine BAĞLANIR (fix turu 3, yüksek, KABUL).**
Kilit doğru kurulursa (b) tek başına yeterlidir. Buna rağmen `RollbackGateEvidence`
**`onay_kapsam_sha` alanını taşır** ve o alan `_evidence_fingerprint`'e GİRER
(geri alma yükü DÖRT değil **BEŞ** anahtar — R8(c) bloğu). **Bunun açıkça
ikinci-savunma olduğunu beyan ediyoruz:** kilit uçtan uca tutulmazsa — ileride bir
çağıran onu almayı unutursa, ya da yürütme yolu bölünürse — bayat kapsamla basılmış bir
jeton `_consume_provenance`'ın `kanit_jetonu_parmakizi = $n` koşulunda DÜŞER, çünkü satırdaki
parmak izi eski kapsam sha'sıyla, kanıttaki yeni kapsam sha'sıyla hesaplanmıştır.
**İddia edilmeyen:** bu, kilidin yerini TUTMAZ; yarışın kendisini engellemez, yalnız
yarışın ÇIKTISININ harcanmasını engeller.

- **Damgalanan küme ile KAPSAM kümesi AYRIDIR (A3'ün özü).** `approve_incident_rollback`
  damgayı yalnız `durum='bekliyor'` satırlara yazar (tamamlanmış/hatalı/hedefsiz iş geriye
  dönük onaylanmaz), ama yazdığı **değeri** olayın **TÜM** satırları üzerinde hesaplar.
  Damgalanan HER satıra AYNI değer yazılır.
- `build_rollback_evidence` kilitli plan satırını okuduğunda değeri olayın **BUGÜNKÜ TAM**
  satır kümesi üzerinde **yeniden hesaplar**; satırdaki `onay_kapsam_sha` ile eşleşmiyorsa
  `RollbackEvidenceUnavailable` fırlatır. Bir satırın tamamlanması bu değeri DEĞİŞTİRMEZ
  (satır kümeden çıkmaz, yalnız `durum`'u değişir ve `durum` hash'e girmez), dolayısıyla
  N satırlı olay uçtan uca tamamlanabilir. Değeri değiştiren tek şey **üyeliğin kendisidir**:
  satır eklenmesi, satır silinmesi ya da kimlik/hedef alanlarının değişmesi.

**Üyelik NE ZAMAN değişebilir — ve değişince onaya NE olur (A3, atomik kural).**

1. **Pencere:** üyelik YALNIZ **yürütme başlamadan önce** değişebilir. Ölçüt mekaniktir:
   *yürütme başlamış sayılır ⇔ o olayın en az bir satırı `durum ∈ ('tamamlandi', 'hata')`.*
   (`hedefsiz` yürütme değil, plan yazımının çıktısıdır — pencereyi KAPATMAZ.)
2. **Değişikliğin yolu — `amend_rollback_plan` (A1(a), fix turu 3, yüksek, KABUL).**
   Fix turu 2 bu yolu `runs.build_rollback_plan`'a veriyordu. **Ölçüldü ve bu YANLIŞTI:**
   o fonksiyonun bağlayıcı imzası `build_rollback_plan(db, *, affected: AffectedSet,
   actor: str) -> str`'dir (plan 1064) — **YENİ bir olay MİNTLER ve olay kimliği
   PARAMETRE OLARAK ALMAZ.** Yani mevcut bir olayın üyeliğini büyütmenin/küçültmenin
   API'si HİÇ YOKTU; üyelik-büyümesi, bayat mühür ve yeniden mühürleme geçişleri
   **erişilemezdi** ve onlar için adı konmuş sekiz test hiçbir şeyi koşamazdı.
   Bağlanan hüküm: üyelik yalnız **`runs.amend_rollback_plan`** üzerinden değişir
   (`olay-plani --incident-id`). `build_rollback_plan` imzası ve anlamı DEĞİŞMEZ — o
   yalnız olay AÇAR. Pencere kapalıyken satır eklemek/çıkarmak
   `IncidentMembershipLocked` fırlatır ve **hiçbir satır yazılmaz** (fail-closed, tek
   işlem). Kimlik/hedef alanlarının değiştirilmesi onaylanmış satırlarda zaten veri
   katmanında reddedilir (ayak (d)).
3. **Onaya ne olur — MÜHÜR YENİLENİR (reseal), ve nasıl olduğu tam olarak şudur:**
   üyelik değişince tüm damgalı satırların `onay_kapsam_sha`'sı BAYATLAR ve o olay
   yürütülemez hâle gelir. Operatör `olay-onayla`'yı TEKRAR çalıştırır;
   `approve_incident_rollback` bu kez **bayat damgalı satırları da YENİDEN damgalar**
   (`onay_actor` · `onaylandi_at` · `onay_kapsam_sha` üçü birden yeni değerlerle yazılır).
   Bu, önceki *"zaten damgalı satır TEKRAR damgalanmaz"* kuralının **daraltılmış** hâlidir:
   idempotans kapsam DEĞİŞMEDİĞİNDE korunur (aynı sha → ilk onay ve ilk onaylayan aynen
   kalır), kapsam DEĞİŞTİĞİNDE ise yeniden mühürleme ZORUNLUDUR. Yeniden mühürlemenin
   tetikleyiciyle çatışması YOKTUR: `onay_*` kolonları onaydan sonra da güncellenebilir
   (aşırı kilitleme yasağı, ayak (d)).
4. **Yürütme BAŞLADIKTAN sonra üyelik değişirse:** bu yol (2) gereği **REDDEDİLİR** —
   yazma hiç gerçekleşmez. Buna rağmen veri katmanına elle bir satır sokulursa,
   `build_rollback_evidence`'ın kapsam karşılaştırması bayat damgayı yakalar ve kalan
   satırlar `RollbackEvidenceUnavailable` ile durur (**fail-closed**); yarım yürütülmüş bir
   olay sessizce yeni üyelikle devam ETMEZ. Kurtarma yolu tektir ve elle-müdahale
   gerektirir; sistem kendiliğinden yeniden mühürlemez.

**Ayak (d) — onaylanmış satırın kimlik/hedef alanları DEĞİŞMEZ (tetikleyici).**

> **REVİZYON R-B (2026-09-08) — düzyazı ile bağlayıcı SQL bloğu ÇELİŞİYORDU; SQL BAĞLAR.**
> Eski düzyazı mekanizmayı *"032'nin `sector_research_artifacts_append_only` tetikleyicisinin
> aynısı"* diye tarif edip `BEFORE UPDATE OR DELETE` desenini gösteriyordu; hemen altındaki
> bağlayıcı SQL bloğu ise `BEFORE UPDATE` diyordu. **Taze ölçümler (2026-09-08):**
> **(1)** o desen `032_sector_packages.sql` **satır 187-188**'dedir — eski metnin gösterdiği
> 49-51 bir tetikleyici değil, fonksiyon GÖVDESİDİR; **(2)** 032 İKİ deseni birden taşır:
> salt-ekleme `BEFORE UPDATE OR DELETE` (187-188) ve alan-kilitleyen
> `sectors_reject_reparenting BEFORE UPDATE` (310-311); **(3)** hüküm ARTIK UYGULANMIŞTIR —
> `shared/db/migrations/036_package_runs.sql` tetikleyiciyi
> `BEFORE UPDATE ON social.package_rollback_plans` olarak kuruyor (kanonik manifest satır 122).
>
> **Karar: SQL bloğu bağlar — `BEFORE UPDATE`.** Salt-ekleme analojisi zaten YANLIŞTI: o desen
> HER `UPDATE`i reddeder, oysa burada `durum` · `reason` · `onay_*` · `kanit_jetonu_*`
> onaydan SONRA yazılabilir KALMAK ZORUNDADIR (yeniden mühürleme yolu). Doğru emsal
> `sectors_reject_reparenting`'tir. Düzeltilen düzyazıdır; SQL bloğu DEĞİŞMEDİ ve uygulanmış
> 036 ile hizalı kaldı.
>
> **AÇIK AYAK KAPANDI — Task 8 kararı, 2026-09-08 (commit `3b4beec`).** R-B bu ayağı
> *"çözülmedi, evi var (Task 8)"* diye bırakmıştı; Task 8 `amend_rollback_plan`'ı yazarken
> soruyu doğurdu ve **HARD DELETE**'i seçti. **Gerekçe ölçülmüştür:** `incident_scope_sha`
> üyelik parmak izini `durum`'u DIŞARIDA bırakarak kurar — yani durum tabanlı bir "çıkarma"
> satırı hash'in İÇİNDE bırakır, mühür TAZE görünmeye devam eder ve üyelik daralması her
> kapıda GÖRÜNMEZ olur. Yeni bir `durum` değeri hem şema değişikliği ister hem de bu körlüğü
> çözmez.
> **Bağlanan sınır iki ayakla karşılandı** (ikisi de aynı turda indi):
> **(a)** 036'nın tetikleyicisi `BEFORE DELETE OR UPDATE`e genişletildi ve gövdeye `TG_OP`
> ayrımlı bir DELETE kolu **EN BAŞA** kondu — `NEW` okuyan iki yüklem önce gelseydi HER
> silmeyi yanlışlıkla reddederdi. Kol, **yürütülmüş** işin izini korur: `durum IN
> ('tamamlandi','hata')` ya da jeton harcanmışsa silme REDDEDİLİR. `bekliyor` ve `hedefsiz`
> satırlar — onaylı olsalar bile — silinebilir; üyelik yürütme başlamadan önce değişebilir
> (A3 penceresi). **(b)** `amend_rollback_plan`, mühürlü ama yürütülmemiş bir satırı
> düşürdüğünde `sektor_paketi.olay_uyeligi_daraltildi` yönetici olayı yazar — mühür kaybı
> SESSİZ kalmaz.
> **Kanonik metin sırası `BEFORE DELETE OR UPDATE`'tir**, `BEFORE UPDATE OR DELETE` değil:
> ölçüldü ki PostgreSQL `pg_get_triggerdef` çıktısını o sırada normalize ediyor ve 036'nın
> tetikleyici manifesti metni birebir karşılaştırıyor.

```sql
CREATE FUNCTION social.reject_approved_rollback_plan_mutation() RETURNS trigger AS $$
BEGIN
  -- DELETE kolu EN BAŞTA: aşağıdaki iki yüklem `NEW` okur, DELETE'te `NEW` NULL'dur.
  IF TG_OP = 'DELETE' THEN
    IF OLD.durum IN ('tamamlandi', 'hata') OR OLD.kanit_jetonu_harcandi_at IS NOT NULL THEN
      RAISE EXCEPTION 'yurutulmus geri alma plani satiri SILINEMEZ';
    END IF;
    RETURN OLD;   -- bekliyor / hedefsiz satır silinebilir (A3 üyelik penceresi)
  END IF;

  IF OLD.onay_actor IS NOT NULL AND NEW.onay_actor IS NULL THEN
    RAISE EXCEPTION 'onaylanmış geri alma planının onay mührü SİLİNEMEZ';
  END IF;

  IF OLD.onay_actor IS NOT NULL AND (
       NEW.incident_id             IS DISTINCT FROM OLD.incident_id
    OR NEW.package_id              IS DISTINCT FROM OLD.package_id
    OR NEW.observed_active_version IS DISTINCT FROM OLD.observed_active_version
    OR NEW.target_version          IS DISTINCT FROM OLD.target_version
    OR NEW.evidence_class          IS DISTINCT FROM OLD.evidence_class
  ) THEN
    RAISE EXCEPTION 'onaylanmış geri alma planı satırının kimlik/hedef alanları değiştirilemez';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER package_rollback_plans_approved_immutable
  BEFORE DELETE OR UPDATE ON social.package_rollback_plans
  FOR EACH ROW EXECUTE FUNCTION social.reject_approved_rollback_plan_mutation();
```

**Aşırı kilitleme YOK:** `durum` · `reason` · `onay_*` · `kanit_jetonu_*` kolonları
onaydan SONRA da güncellenebilir — yürütücü onları yazar. Kilitlenen yalnız **neyin
onaylandığını tanımlayan beş alandır** — artı mührün kendisi (dolu → BOŞ; aşağıdaki R-C).
**Satırın SİLİNMESİ KISMEN kilitlidir** (R-B'nin kapanan ayağı, Task 8 kararı): yürütülmüş
satır (`durum IN ('tamamlandi','hata')` ya da jeton harcanmış) SİLİNEMEZ; `bekliyor` ve
`hedefsiz` satırlar onaylı olsalar bile silinebilir — üyelik yürütme başlamadan önce değişir.

**Onay mührünün yüklemi — AÇIKÇA BEYAN EDİLİR (revizyon R-C, 2026-09-08).** Üç onay kolonu
üzerinde ÜÇ geçiş vardır; üçünün de davranışı burada YAZILIDIR, okuyucu çıkarım YAPMAZ:

| geçiş | izin | nerede bağlanır |
|---|---|---|
| BOŞ → DOLU (ilk onay) | **ZORUNLU YOL** — üçü birlikte yazılır | `approve_incident_rollback`; `..._onay_butun` CHECK'i (0,3) |
| DOLU → DOLU (yeniden mühürleme) | **BİLEREK AÇIK** — kapsam değişince ZORUNLU | A3; tetikleyici `onay_*`'ı kilitlemez |
| DOLU → BOŞ (mühür silme) | **REDDEDİLİR** | tetikleyicinin BİRİNCİ kolu (yukarıdaki SQL; uygulanmış hâli `036_package_runs.sql` satır 190-199) |

**Üçüncü satırın gerekçesi ÖLÇÜLDÜ (2026-09-07, Task 6 yazımı sırasında) ve bu metin ondan
GERİDE kalmıştı — şimdi hizalandı.** Kilit `OLD.onay_actor IS NOT NULL` yüklemine dayanır;
onay üçlüsü birlikte NULL yapılabilseydi değişmezlik **İKİ ADIMDA** atlatılırdı
(mührü temizle → kimlik/hedef alanını değiştir → yeniden mühürle) ve `num_nonnulls ∈ {0,3}`
CHECK'i buna İZİN VERİRDİ. Ölçülen zincir `target_version`'ı 3'ten 99'a taşıyordu.
Kapanan yalnız **dolu → BOŞ** geçişidir; yeniden mühürleme açık kalır.
**Yanlışlıkla verilmiş onayın düzeltme yolu:** kapsam değiştiyse YENİDEN MÜHÜRLE (üçlü dolu
kalır); hedef değişecekse YENİ bir plan satırı yaz — mührü silmek yol DEĞİLDİR.

**Gerekçe — kanonik kayıt seçeneği C'yi zaten eliyor.** Spec girdisi satır 1409 geri alma
kararını *"yöneticiye/operatöre"* verir ve satır 1977 aktivasyon/geri alma olayının
kaydedilmesini **her katmanda ortak, açık-olmayan yükümlülük** sayar. "Komutu çalıştırmak
onaydır" bu yüzden yol değildir: kaydı olmayan onay, R11'in yasakladığı uydurulmuş
boolean'ın adı değişmiş hâlidir.

**Neden A değil B.** Outbox (`social.admin_events`) bir bildirim kuyruğudur; onay deposu
yapılırsa (a) yürütücü, zaten KİLİTLEDİĞİ plan satırının yanında ikinci bir tabloyu okumak
zorunda kalır — kanıt kurulumu artık tek satırdan atomik değildir; (b) kuyruk kaydının
yaşam döngüsü (tüketim, budama) onay kaydının yaşam döngüsünden farklıdır ve onayı bir
temizlik işi sessizce yok edebilir. Onay, onayladığı planın yanında durur.

**Maliyet ölçüldü ve SIFIRA yakın — ölçüm TARİHLİDİR (2026-08-30):** o gün Task 6 henüz
uygulanmamıştı (migration 036 yazılmamıştı; `shared/db/migrations/` en yüksek numara 034).
İki nullable kolon + bir CHECK o an ücretsizdi; karar Task 6'dan SONRA verilseydi migration
037 gerekirdi. **Bugün geçerli değildir:** `036_package_runs.sql` yazıldı (ölçüldü
2026-09-08) ve bu kolonları taşıyor — yani karar zamanında alınmış, bedel gerçekten
doğmamıştır. Buradan sonraki şema değişiklikleri 037 ister.

**Granülerlik — onay OLAY düzeyindedir, paket düzeyinde DEĞİL.** K-145 bir kural sürümünün
etkilediği TÜM paketleri geri alır; paket başına ayrı onay istemek tek operatörlü işletimde
(K-54 · K-77) taşınamaz bir yüktür ve K-153'ün operasyon-yükü kaygısını doğrudan büyütür.
Bu yüzden:

```python
# sector_pipeline_cli.py  (Task 16) — yeni alt komut + genişleyen alt komut
#   olay-onayla --incident-id <id> --actor <kimlik>
#   olay-plani  [--incident-id <id>] --actor <kimlik>      (A1(a), fix turu 3)
#       --incident-id YOK  → runs.build_rollback_plan  (olay AÇAR, kimliği basar)
#       --incident-id VAR  → runs.amend_rollback_plan  (üyeliği DEĞİŞTİRİR)
# runs.py  (Task 8)
async def approve_incident_rollback(db, *, incident_id: str, actor: str) -> int:
    """O olay kimliğine ait BEKLEYEN plan satırlarının TAMAMINI tek işlemde damgalar
    (`onay_actor`, `onaylandi_at`, `onay_kapsam_sha`); damgalanan satır sayısını döner.

    - **İLK İŞ: `await _lock_incident(db, incident_id)`** (A1(b), yol #2) — `require_actor`
      çağrısından hemen sonra, HİÇBİR `durum` ya da kapsam okumasından ÖNCE.
    - `actor` **Plan 1'in kanonik kapısından** geçer: `require_actor` (yani
      `sector_package_lifecycle._require_actor`; TANIM `package_events.require_actor`,
      satır 258-280 — revizyon R-D). Boş/whitespace/`str`
      olmayan kimlikte `ValueError` fırlar ve **HİÇBİR satır damgalanmaz** (fail-closed;
      kısmi damgalama YOK — tek işlem).
    - `durum='bekliyor'` OLMAYAN satırlar damgalanmaz (tamamlanmış/hatalı/hedefsiz iş
      geriye dönük onaylanamaz).
    - **`onay_kapsam_sha` = `incident_scope_sha(<olayın TÜM satırları>)`** — damgalanacak
      satırların değil, olayın **TAM üyeliğinin** parmak izi (A3). Damgalanan HER satıra
      AYNI değer yazılır.
    - **Damgalı satır iki hâlde iki farklı davranış görür (A3):** satırdaki
      `onay_kapsam_sha` bu koşumda hesaplanan değere **EŞİTSE** dokunulmaz — ilk onay ve
      ilk onaylayan korunur (idempotans). **FARKLIYSA** satır yeniden mühürlenir: üç onay
      kolonu birden yeni değerlerle yazılır. Bayat mühür sessizce BIRAKILMAZ.
      **Karşılaştırma NORMALİZASYONSUZDUR (A4 süpürmesi #8):** satırdaki değer
      `type(...) is str` değilse ya da `strip()` sonrası boşsa BAYAT sayılır ve satır
      yeniden mühürlenir; eşitlik `strip()`/`lower()` uygulanmadan, ham değerler
      üzerinde kurulur. `strip()`'li bir karşılaştırma boşluk-sarmalı bayat bir mührü
      TAZE sanardı.
    - Hiç satır damgalanmadıysa 0 döner; çağıran bunu hata olarak raporlar.
    """
```

Böylece operatör TEK komut çalıştırır, N satır damgalanır, ve yürütücünün satır-başına
okuması yerel ve atomik kalır.

**`build_rollback_evidence`'ın `manager_approved` ayağı bağlanır — ÜÇ koşul birden:**
kilitli plan satırının `onay_actor` · `onaylandi_at` · `onay_kapsam_sha` alanlarının
**ÜÇÜ de** dolu VE `onay_kapsam_sha`, olayın **bugünkü** kanonik satır kümesi üzerinde
yeniden hesaplanan değere **EŞİT** ise `True`; biri düşerse
`RollbackEvidenceUnavailable` (uydurma YOK). Alan `bool`'a çevrilirken herhangi bir
varsayılan/`.get` düşüşü KULLANILMAZ. Boş/whitespace kimlik veri katmanına zaten giremez
(`package_rollback_plans_onay_actor_dolu` CHECK'i), servis katmanına da giremez
(`require_actor`) — **iki katmanda birden fail-closed.**

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 6** — `package_rollback_plans`
şemasına ÜÇ onay kolonu + İKİ CHECK + BİR değişmezlik tetikleyicisi, ve (R8(c) gereği)
DÖRT jeton kolonu + BİR CHECK eklenir (plan 795-800 aralığını genişletir). **Task 8** —
`approve_incident_rollback` · `incident_scope_sha` · **`IncidentMembershipLocked`**
(A3, fix turu 2) · **`amend_rollback_plan`** · **`_lock_incident`** ·
**`_OLAY_KILIT_ONEKI`** (A1, fix turu 3) Produces listesine eklenir;
`build_rollback_evidence`'ın `manager_approved` kaynağı bu kolonlardır ve **üyelik
penceresini `amend_rollback_plan` zorlar — `build_rollback_plan` DEĞİL** (A1(a);
`build_rollback_plan`'ın imzası ve anlamı plan 1064'teki hâliyle DEĞİŞMEZ, o yalnız olay
AÇAR). **Task 16** — `olay-onayla` alt komutu eklenir (plan 1781-1797) ve **`olay-plani`
isteğe bağlı `--incident-id` parametresi kazanır:** verilmezse `build_rollback_plan`
(olay AÇ), verilirse `amend_rollback_plan` (üyelik DEĞİŞTİR) çağrılır; ikinci hâlde A3'ün
pencere kapısı uygulanır. İkinci bir alt komut adı AÇILMAZ — R10'un "her operatör adımının
CLI girişi olur" hükmü bu parametreyle karşılanır.
**Task 15** (A1(c), fix turu 3) — `RollbackGateEvidence` `onay_kapsam_sha` alanını kazanır
ve alan `_evidence_fingerprint`'e girer; sınıf Task 15'in Modify kaleminde yaşadığı için bu
hüküm Task 15'i de bağlar.

**Kanıt testi · sahibi:**
- **Şema kapıları — Sahip: Task 6, `tests/test_migration_036.py`:**
  `test_rollback_plan_approval_columns_exist_and_nullable` (ÜÇ kolon) ·
  `test_rollback_plan_approval_requires_all_three_or_none`
  (`num_nonnulls(...) IN (0,3)`; bir ya da iki kolon dolu → CHECK RED) ·
  **`test_rollback_plan_approval_rejects_blank_actor`** (`onay_actor=''` ve `'   '` →
  CHECK RED — H7'nin ana ispatı) ·
  `test_approved_plan_row_target_version_is_immutable` ·
  `test_approved_plan_row_identity_is_immutable` (`incident_id` · `package_id` ·
  `observed_active_version` · `evidence_class`) ·
  `test_approved_plan_row_status_and_reason_still_updatable` (aşırı kilitleme YOK —
  pozitif kontrol) ·
  `test_unapproved_plan_row_fields_still_editable` (tetikleyici yalnız onaylı satırı
  kilitler — pozitif kontrol).
- **Servis kapıları — Sahip: Task 8, `tests/test_pipeline_runs.py`:**
  `test_approve_incident_stamps_only_bekliyor_rows` ·
  `test_approve_incident_is_idempotent_and_keeps_first_approver_when_scope_unchanged`
  (A3: idempotans artık KAPSAM DEĞİŞMEDİĞİNDE geçerlidir; bu ad, fix turu 1'in
  `test_approve_incident_is_idempotent_and_keeps_first_approver` adının yerine geçer) ·
  `test_approve_incident_returns_zero_when_nothing_pending` ·
  **`test_approve_incident_refuses_blank_actor`** (`''` · `'   '` · `None` → `ValueError`,
  hiçbir satır damgalanmaz) ·
  `test_approve_incident_uses_plan1_actor_guard` (yapısal: `runs.py` `require_actor`
  DIŞINDA `strip()`-tabanlı ikinci bir aktör kontrolü içermez) ·
  `test_approve_incident_writes_same_scope_sha_to_every_stamped_row` ·
  `test_incident_scope_sha_uses_identity_canonical_rule` ·
  `test_build_rollback_evidence_refuses_when_plan_row_unapproved` (negatif kontrol) ·
  `test_build_rollback_evidence_true_only_when_all_three_approval_fields_set` ·
  **`test_build_rollback_evidence_refuses_when_incident_scope_grew`** (onaydan sonra
  olaya YENİ satır eklendi → RED) ·
  **`test_build_rollback_evidence_refuses_when_incident_scope_shrank`** (onaylı bir satır
  olayın üyeliğinden ÇIKARILDI/silindi → RED; A3: satırın `tamamlandi`'ya geçmesi
  küçülme SAYILMAZ) ·
  `test_build_rollback_evidence_accepts_unchanged_scope` (pozitif kontrol).
- **A3'ün uçtan uca kapıları — SEKİZİ DE A1(a)'ya göre YENİDEN YAZILDI (fix turu 3).**
  Fix turu 2'nin sekiz testi `build_rollback_plan` üzerinden üyelik değiştirmeye
  dayanıyordu; o fonksiyon olay kimliği ALMADIĞI için testlerin beşi (üyelik büyümesi ·
  bayat mühür · yeniden mühürleme · pencere kapısı · sınır vakası) hiçbir şeyi
  koşamıyordu. Hepsi `amend_rollback_plan` sözleşmesine bağlandı. **Sahip: Task 8,
  `tests/test_pipeline_runs.py`:**
  1. **`test_incident_scope_sha_ignores_durum`** — aynı üyelik, farklı `durum` değerleri
     → AYNI sha. (Kapsam tanımının ana ispatı; A1(a)'dan bağımsız, DEĞİŞMEDİ.)
  2. `test_incident_scope_sha_covers_rows_outside_bekliyor` — `tamamlandi` · `hata` ·
     `hedefsiz` satırlar da hash'e girer. (DEĞİŞMEDİ.)
  3. **`test_two_row_incident_completes_end_to_end`** — `build_rollback_plan` iki satırlı
     olay açar, `approve_incident_rollback` mühürler, `execute_rollback_plan` koşar;
     birinci satır `tamamlandi`'ya geçtikten SONRA ikincisinin kanıtı da KURULUR ve olay
     biter. **Yeni kapı:** ikinci satırın kanıtındaki `onay_kapsam_sha`, birincininkiyle
     AYNIdır (A1(c): tamamlanma kapsamı değiştirmez).
  4. **`test_partial_failure_then_retry_reuses_the_same_approval`** — birinci satır `hata`
     ile kapandı; aynı komut tekrar koşunca kalan satır AYNI onayla yürür, yeni onay
     İSTENMEZ. **Yeni kapı:** ikinci koşumda `approve_incident_rollback` HİÇ çağrılmaz
     (yapısal: yürütücü onay yüzeyini çağırmaz).
  5. **`test_membership_growth_before_execution_then_reapproval_completes`** —
     `amend_rollback_plan(incident_id=…, affected=<bir paket DAHA geniş küme>, actor=…)`
     `(1, 0)` döner; mevcut damgalar BAYATLAR ve `build_rollback_evidence`
     `RollbackEvidenceUnavailable` fırlatır; `approve_incident_rollback` tekrar koşunca
     TÜM bekleyen satırlar yeni sha ile YENİDEN MÜHÜRLENİR ve olay tamamlanır.
  6. `test_reapproval_restamps_stale_rows_and_leaves_fresh_rows_untouched` — `amend`
     sonrası yeniden onayda **bayat** satırların üç onay kolonu da yenilenir; aynı
     koşumda zaten taze olan (yeni eklenmiş, hiç mühürlenmemiş) satır ilk kez mühürlenir
     ve **iki kez mühürlenen satır YOKTUR**.
  7. **`test_membership_growth_after_execution_started_is_rejected`** — bir satır
     `tamamlandi`'ya geçtikten SONRA `amend_rollback_plan` → `IncidentMembershipLocked`;
     **hiçbir satır yazılmaz** (öncesi/sonrası satır sayısı ve sha AYNI).
     (Fix turu 2 bu testi `build_rollback_plan`'a dosyalamıştı — o çağrı yeni bir olay
     açardı ve pencere kapısına hiç uğramazdı.)
  8. `test_membership_lock_window_opens_only_on_tamamlandi_or_hata` — yalnız `hedefsiz`
     satır içeren olayda `amend_rollback_plan` BAŞARILI (pencere AÇIK); tek bir `hata`
     satırı eklenince aynı çağrı `IncidentMembershipLocked` (pencere KAPALI). Sınır vakası.
- **A1(a)'nın kendi kapıları (fix turu 3) — Sahip: Task 8, `tests/test_pipeline_runs.py`:**
  **`test_amend_rollback_plan_takes_incident_id_and_build_does_not`** (yapısal,
  `inspect.signature`: `amend_rollback_plan`'da `incident_id` VAR, `build_rollback_plan`'da
  YOK ve dönüş tipleri farklıdır — A1(a)'nın ana ispatı) ·
  `test_amend_rollback_plan_adds_and_removes_rows` (`(eklenen, silinen)` sayıları) ·
  `test_amend_rollback_plan_leaves_approval_columns_untouched` (madde 6: `onay_*`
  YAZILMAZ) · `test_amend_rollback_plan_is_a_no_op_for_unchanged_membership` (`(0, 0)`,
  hata DEĞİL) · `test_amend_rollback_plan_refuses_blank_actor`.
- **A1(b)'nin kapıları — KİLİT (fix turu 3), Sahip: Task 8,
  `tests/test_pipeline_runs.py`:**
  **`test_evidence_and_spend_are_serialised_by_the_incident_lock`** — **DETERMİNİSTİK
  ARALIK TESTİ, hükmün ana ispatı.** İki bağlantı kullanılır. Bağlantı A
  `execute_rollback_plan`'ın yolunu koşar ama **kapsam doğrulaması ile jeton harcaması
  ARASINDA bir `asyncio.Event` ile DURDURULUR** (duraklama noktası test kancasıyla
  enjekte edilir; uyku/zamanlama YOK — bu yüzden deterministiktir). Bağlantı B o sırada
  `amend_rollback_plan` ile olaya YENİ bir satır eklemeye çalışır. **Beklenen:** B, A'nın
  işlemi bitene kadar olay kilidinde BEKLER; A geçişini tamamlar; B sonra koşar ve
  (A'nın yürütmeyi başlatmış olması nedeniyle) `IncidentMembershipLocked` alır. Kilit
  kaldırılırsa test DÜŞER — yani test kilidin varlığını ölçer, prose'u değil. ·
  `test_incident_lock_is_reentrant_within_one_transaction` (aynı işlemde ikinci
  `_lock_incident` çağrısı anında döner — dört yolun koşulsuz almasının önkoşulu) ·
  `test_incident_lock_name_is_the_single_prefix` (yapısal: `runs.py` içinde
  `pg_advisory_xact_lock` yalnız `_lock_incident` gövdesinde geçer; ikinci bir kilit adı
  YOK) ·
  `test_evidence_construction_and_spend_share_one_transaction` (yapısal:
  `execute_rollback_plan` gövdesinde `build_rollback_evidence` ve `rollback_package`
  AYNI `async with db.transaction()` bloğunun içindedir).
- **A1(c)'nin kapıları — KEMER VE ASKI (fix turu 3), Sahip: Task 15,
  `tests/test_package_lifecycle.py`:**
  **`test_stale_scope_token_cannot_be_spent_even_without_the_lock`** — jeton eski kapsamla
  basılır, sonra üyelik değiştirilir ve kanıt yeni `onay_kapsam_sha` ile kurulur;
  `_consume_provenance` parmak izi uyuşmazlığından RED verir (kilit hiç alınmamış olsa
  bile). ·
  `test_rollback_evidence_payload_has_five_keys` (**Sahip: Task 8** — BEŞ anahtar; DÖRT
  anahtarlı eski küme RED).
- `test_olay_onayla_subcommand_stamps_incident` ·
  `test_olay_onayla_subcommand_refuses_blank_actor` ·
  **`test_olay_onayla_reseals_incident_after_membership_growth`** (A3) ·
  **`test_olay_plani_with_incident_id_calls_amend_not_build`** (A1(a): `--incident-id`
  verilince `amend_rollback_plan`, verilmeyince `build_rollback_plan` çağrılır) ·
  **`test_olay_plani_refuses_new_rows_after_execution_started`** (A3 — komut
  `IncidentMembershipLocked`'ı sıfırdan farklı çıkış koduyla raporlar) — **Sahip: Task 16**,
  `tests/test_pipeline_cli.py`.

---

## AÇIK — kontrolörün kararı gerekiyor

> **AÇIK-1 kapandı** (yukarıda; gövdesi kararın dayanağı olarak korunuyor).
> **AÇIK-2 fix turu 1'de açıldı, AYNI TURDA KAPANDI** (kontrolör kararı, 2026-08-30).
> **AÇIK-3 fix turu 2'de açıldı, AYNI TURDA KAPANDI** (kontrolör kararı, 2026-08-30).

## AÇIK-3 KAPANDI — kontrolör kararı, 2026-08-30

**Karar: B seçeneği — yardımcılar Task 8'de `sector_package_lifecycle.py`'ye yazılır.**
`_evidence_fingerprint` ve `_evidence_fingerprint_from_payload` (ve onların beslediği
`activation_evidence_payload` / `rollback_evidence_payload`) **Task 8'in MODIFY kalemidir**;
jeton kolonlarının tüketimi (`_consume_provenance`) ve aktivasyon/geri alma kapılarının
jeton doğrulaması Task 15'te kalır.

**Gerekçe — bağımlılık YÖNÜ, bu depoda tek yönlü kurulmuş bir sözleşmedir.**
Bugüne kadar Plan 2'nin her modülü Plan 1'den OKUR; hiçbir Plan 1 servisi Plan 2 paketine
bağımlı değildir. A seçeneği bu yönü ters çevirir: `sector_package_lifecycle.py` (Plan 1
servisi) `sector_pipeline/` (Plan 2 paketi) altından import etmeye başlar. Tek bir import
zararsız görünür, ama yön bir kez açıldıktan sonra ikinci ve üçüncü import'un gerekçesi
kendiliğinden hazır olur ve iki katman birbirine kilitlenir. Yönü korumak, kapatılması
kolay olmayan bir kapıyı hiç açmamaktır.

**B'nin maliyeti YENİ bir sınıf açmıyor — ölçüldü.** İtiraz "tek dosya iki görev arasında
bölünür"dü; oysa `sector_package_lifecycle.py` bu ekte **zaten** bölünmüş durumdadır:
Task 3 `insert_draft`'ın karar günlüğü parametresini, Task 15 jeton alanlarını ve kapı
doğrulamasını yazar. B üçüncü bir dilim ekler, ilk dilimi açmaz.

**Emsal zaten var:** `runs.py` (Task 8) o modülden `_require_actor`'ı hâlihazırda çağırıyor
(AÇIK-1 ayak (b)) — yani Task 8'in o dosyayla ilişkisi bu kararla doğmuyor, yalnız
okumadan yazmaya genişliyor.

**C reddedildi** — A2(d)'nin davranış hükmüyle (*"parmak izi kilitli satırdan türetilir,
çağırandan alınmaz"*) doğrudan çelişir. Bu hüküm bağlıdır ve geri alınmaz.

**Bağlanan hüküm:**

- **Task 8** Files listesine `apps/social/backend/app/services/sector_package_lifecycle.py`
  **Modify** olarak eklenir; o görevde YALNIZ dört yardımcı + onların yazıldığı yerel
  görünüm tipi yazılır (`activation_evidence_payload` · `rollback_evidence_payload` ·
  `_evidence_fingerprint` · `_evidence_fingerprint_from_payload` · `KilitliKosuGorunumu` ·
  `_require_kosu_gorunumu`). Jeton alanlarına, `_require_evidence`'a ve kapı gövdelerine
  Task 8'de DOKUNULMAZ.
- **DÖNGÜSEL IMPORT — kararın ÖLÇÜLMÜŞ teknik kusuru ve çözümü (fix turu 3, KABUL).**
  Karar harfiyen uygulanınca `activation_evidence_payload(run: VerifiedRun)` bu Plan 1
  modülünü `runs.py`'ye bağımlı kılıyordu; oysa `runs.py` ZATEN buradan `_require_actor`'ı
  alıyor (AÇIK-1 ayak (b)) — **döngü**. Karar GEÇERLİ KALIR; uygulaması şudur: yardımcılar
  `runs.VerifiedRun`'ı IMPORT ETMEZ, modülün KENDİ içinde tanımlı **`KilitliKosuGorunumu`**
  protokolüne yazılır (tam tanımı R8(c)'nin sözleşme bloğunda; SEKİZ alan, KAPALI).
  `VerifiedRun` protokolü yapısal olarak karşılar, nominal bağ KURULMAZ.
- **Yardımcıların imzaları AÇIK-3 nedeniyle tamamlandı (mekanik sonuç, yeni hüküm DEĞİL):**
  `activation_evidence_payload(kosu: KilitliKosuGorunumu, aktif_paket_satiri: Mapping[str, Any] | None)`
  — K-94 taban durumu (`expected_active_version` / `expected_no_active`) koşu satırından
  türetilemez, o sektörün AKTİF paket satırından okunur ve o satır aynı işlemde
  `FOR UPDATE` ile kilitlenir; ikinci parametre bir "çağıran girdisi" değil, kilitli
  okumadır. `rollback_evidence_payload(plan_satiri: Mapping[str, Any], hedef_kosu: KilitliKosuGorunumu)`
  — anahtar kümesi A1(c) ile BEŞ'e çıktı.
- **Task 15** aynı dosyada `_consume_provenance`'ı, `EvidenceProvenanceInvalid`'i,
  `expected_no_active`'i ve iki geçiş fonksiyonunun jeton doğrulamasını yazar — Task 8'in
  yazdığı yardımcıları ÇAĞIRIR, yeniden tanımlamaz.
  **Fix turu 3 düzeltmesi:** bu satır önce *"jeton alanlarını"* da Task 15'e veriyordu;
  R9 gereği köken ALANLARI (`run_id` · `provenance_token` · `incident_id` · `package_id` ·
  `onay_kapsam_sha`), şekil kapıları (`_require_token` · `_require_kapsam_sha`) ve
  `EvidenceMintRefused` **Task 8'e** taşındı — çünkü onları KURAN/FIRLATAN iki fonksiyon
  (`build_rollback_evidence` · `mint_evidence_token`) Task 8'dedir ve Task 8 < Task 15.
  Aşağıdaki seçenek tablosunun B satırındaki *"jeton alanları Task 15'te kalır"* ifadesi
  bu düzeltmeyle **DARALTILMIŞTIR**: Task 15'te kalan, alanlar değil **tüketim ve kapı
  gövdeleridir**.
- **Tek hash kuralı tek yerdedir:** parmak izi yalnız bu dört yardımcıdan üretilir;
  başka hiçbir modül kendi parmak izi hesabını yazmaz.

**Kanıt testi · sahibi:**
- `test_evidence_payload_derived_from_locked_row_fields_only` (yardımcılar çağırandan
  hiçbir değer almaz) · `test_fingerprint_is_stable_across_equal_payloads` ·
  `test_fingerprint_differs_on_any_field_change` — **Sahip: Task 8**,
  `tests/test_pipeline_runs.py`.
- `test_no_module_other_than_lifecycle_computes_evidence_fingerprint` (yapısal: depo
  genelinde parmak izi hesabı TEK yerde — `runs.py` ve `writeback.py` dâhil hiçbir modül
  kendi hesabını yazmaz) — **Sahip: Task 15**,
  `tests/test_write_surface_authorization.py`.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 8** — Files listesine Plan 1 modülü
eklenir, Produces listesine dört yardımcı eklenir. **Task 15** — yardımcıların yazımı
kapsamından ÇIKAR, çağrımı KALIR.

---

### AÇIK-3 (KAPANDI — kararı yukarıda): Parmak izi yardımcıları HANGİ görevde doğar? — A2(d)'nin mekanik yan etkisi

**Neden açık.** A2(d) `mint_evidence_token`'dan `fingerprint` parametresini kaldırdı; artık
parmak izini fonksiyonun KENDİSİ, kilitli satırdan türetir. Ama `mint_evidence_token`
**`runs.py`'dedir ve Task 8'de doğar**, oysa `_evidence_fingerprint` ve
`_evidence_fingerprint_from_payload` bu ekte **`sector_package_lifecycle.py`'ye Task 15
MODIFY kaleminde** yazılıyor. **R9 bir görevin SONRAKİ görevde doğan yüzeyi tüketmesini
YASAKLAR** — Task 8 < Task 15.

**Dürüst etiket — bu tam olarak YENİ bir kusur değildir:** ilerisi ölçüldü, gerileme de
ölçüldü. Aynı gerilim fix turu 1'in metninde de vardı (R11'in `build_rollback_evidence`'ı
`runs.py`'de, yani Task 8'de, `_evidence_fingerprint_from_payload`'ı çağırıyordu). A2(d) onu
**yok etmedi, yapısal hâle getirdi**: artık jeton basan HER yol bu yardımcıya muhtaç.
Kendi başıma kapatmıyorum, çünkü seçenekler görev sahipliğini ve Plan 1 arayüz yüzeyini
değiştiriyor.

| Seçenek | Nasıl | Maliyet / etki |
|---|---|---|
| **A — Yardımcılar Task 8'e taşınır** | `_evidence_fingerprint` · `_evidence_fingerprint_from_payload` `sector_pipeline/` altında Task 8'de doğan bir modüle (ör. `evidence_fingerprint.py`) konur; `sector_package_lifecycle.py` (Task 15) onu IMPORT eder | R9 tam olarak korunur; tek hash kuralı tek yerde kalır. Ama Plan 1 modülü Plan 2 modülüne bağımlı hâle gelir — bugüne kadar bağımlılık HEP ters yönde (Plan 2 → Plan 1) kuruldu |
| **B — Yardımcılar Task 8'de `sector_package_lifecycle.py`'ye yazılır** | Dosya Task 15'te değil, **Task 8'de** MODIFY edilir; jeton alanları ve `_consume_provenance` Task 15'te kalır | Bağımlılık yönü DEĞİŞMEZ (`runs.py` zaten `_require_actor`'ı oradan alıyor — AÇIK-1 ayak (b)). Ama tek dosya iki görev arasında bölünür ve Task 8'in Files listesi Plan 1 modülüne uzanır |
| **C — Her iki fabrika parmak izini KENDİ hesaplar, mint almaz** | A2(d) geri alınır | **REDDEDİLMESİ önerilir, yalnız tamlık için sayılıyor:** kontrolörün A2(d) hükmüyle doğrudan çelişir (parmak izi çağırandan alınamaz) |

**Bloklama etkisi:** karar **Task 8 uygulanmadan ÖNCE** gerekir. Karara kadar A2(d)'nin
DAVRANIŞ hükmü — *"parmak izi kilitli satırdan türetilir, çağırandan alınmaz"* — **bağlıdır
ve değişmez**; değişecek olan yalnız iki yardımcının hangi dosyada ve hangi görevde
doğduğudur.

## AÇIK-2 KAPANDI — kontrolör kararı, 2026-08-30

> # ⚠️ BU KARAR DEĞİŞTİ — R-G7, Eray kararı 2026-09-11
>
> **Yeni karar: `geri-al` alt komutu KALDIRILDI (aşağıdaki A seçeneği UYGULANMADI).**
> Aşağıdaki metin tarihsel kayıttır; **bağlayıcı olan bu bloktur.**
>
> **Neden A kapanmadı — ölçüldü (hakem turu 13 + kapanış turu, Task 16).** Komut olayın
> üyeliğini doğruladıktan SONRA, paket filtresi ALMAYAN olay-kapsamlı yürütücüyü
> çağırıyordu; doğrulama ile yürütmenin kilidi arasında bir pencere kalıyor ve o pencerede
> üyeliği değiştiren ikinci bir operatör, **adlandırılmayan bir paketin geri alınmasına**
> yol açabiliyordu. A1(b)'nin tek-kilit sarmalayıcısı bu yolu kapsamıyordu.
>
> **Pencereyi kapatmanın yolu** olay kilidini baştan sona tutan PAKET-HEDEFLİ bir
> yürütücüdür; o yüzey servis katmanındadır ve Task 16'nın beyan ettiği dosya kümesinin
> DIŞINDADIR. Yani seçim "kapat ya da kapsam aç" ikilemiydi.
>
> **Karar (Eray, 2026-09-11): komutu kapat, olay yolunu TEK yol yap.**
>
> **Yetenek KAYBOLMUYOR — kaybolan kısayoldur, kanıt zinciri değil.** Tek paketlik geri
> alma da `olay-plani` ile tek satırlık bir olay açılarak yapılır; `olay-onayla` ve
> `olay-geri-al` aynen koşar. **Tek satırlık olay AÇIK-2'nin kendi kararında zaten
> MEŞRUDUR** ("`olay-plani` bir paketle çağrılabilir"), yani bu karar yeni bir kavram
> ÜRETMEZ — yalnız ikinci giriş noktasını kaldırır.
>
> **`deaktive-et` yine ETKİLENMEZ** (K-38): kanıt zinciri istemez, tek komuttur, acil kol
> olarak kalır. A'nın kabul edilebilirliğinin sebebi buydu ve kaldırma kararından SONRA da
> geçerlidir — "aktif paketi hemen indir" hâlâ TEK komuttur.
>
> **Aşağıdaki kanıt testlerinden `geri-al`e ait ÜÇÜ DÜŞER**
> (`test_geri_al_requires_incident_id` · `test_geri_al_refuses_when_plan_row_unapproved` ·
> `test_geri_al_succeeds_on_approved_single_row_incident`); yerlerine komutun VAR OLMADIĞINI
> ölçen kapı geçer. `test_deaktive_et_needs_no_incident_and_no_evidence` AYNEN KALIR.
>
> **Sessiz geri ekleme YASAĞI:** komut yeniden eklenirse kapanmamış yarış da geri gelir.
> Yeniden açılma koşulu TEK: paket-hedefli, olay kilidini baştan sona tutan yürütücü
> yazılırsa.

**Karar: A seçeneği — `geri-al` olay kimliği İSTER.** Alt komut listede KALIR, ama imzası
`geri-al --incident-id <id> --package-id <id>` olur ve kanıtını R8(c) jetonundan, yani
`social.package_rollback_plans` satırından alır. Olay kimliği olmayan geri alma yolu YOKTUR.

**Gerekçe — B'nin maliyeti sanılandan büyük, A'nın maliyeti sanılandan küçük.**

*A'nın maliyeti küçük, çünkü acil kol ETKİLENMİYOR (ölçüldü — bu, kararı çeviren bulgudur).*
İlk değerlendirmemde "acil durumda üç komut koşturmak fazla" diye B'ye meylettim; bu YANLIŞTI.
K-38'in acil kolu `deaktive-et`'tir, kanıt zinciri İSTEMEZ ve bu kararla değişmez. Yani
"kötü aktif paketi hemen indir" hâlâ TEK komuttur. A'nın kapattığı tek şey *"önceki sürüme
kanıtsız dön"*dür — ve o acil bir hamle değil, sürüm seçimi içeren düşünülmüş bir hamledir.
Düşünülmüş hamlenin kanıt zincirinden geçmesi maliyet değil, kuralın kendisidir.

*B'nin maliyeti kalıcı ve büyüyen bir kirlilik.* Tek-paketlik sarmalayıcı olaylar `etki-analizi`
raporlarına gerçek K-145 olaylarıyla aynı uzayda düşer; "olay" terimi iki anlama gelir ve
zamanla hangi satırın gerçek bir kural-sürümü olayı olduğunu ayırmak için ikinci bir ayrım
kolonu gerekir. Bu, kaçınmaya çalıştığımız ikinci-kimlik-uzayı sınıfının aynısıdır (bkz.
teknik karar 23: `attempt` ikinci kimlik uzayı olduğu için KALDIRILMIŞTI).

*C reddedildi* çünkü tek-paketlik geri alma gerçek bir ihtiyaçtır (bir sektörün paketi kötü
çıkar, kural sürümü değil); komutu silmek o ihtiyacı `olay-plani` + `olay-geri-al` çiftine
zorlar ve hiçbir şey kazandırmaz — A zaten aynı zinciri, adı doğru komutla sunar.

**Bağlanan hüküm:**

- `geri-al` alt komutu KALIR; imzası `geri-al --incident-id <id> --package-id <id> --actor <kimlik>`.
- Tek-paketlik geri alma da bir olay planı satırı ister; onu `olay-plani` üretir.
  **Tek satırlık olay meşrudur** — `olay-plani` bir paketle çağrılabilir; sentetik/örtük
  olay ÜRETİLMEZ, operatör olayı açıkça açar.
- Onay adımı (`olay-onayla`) HER İKİ ölçekte de zorunludur — tek pakette de, N pakette de.
  Onay yolu tekildir; ikinci bir kapı listesi YOKTUR.
- **`deaktive-et` bu karardan ETKİLENMEZ** (K-38): kanıt zinciri istemez, tek komuttur,
  acil kol olarak kalır. Bu, A'nın kabul edilebilir olmasının SEBEBİDİR ve burada yazılıdır
  ki ileride "acil durumda üç komut" diye yanlış hatırlanmasın.

**Etkilenen görev · geçersiz kılınan satırlar:** **Task 16** — `geri-al` alt komutunun
imzası bağlanır (plan 1797 civarındaki listede adı KALIR, parametreleri EKLENİR).

**Kanıt testi · sahibi:**
- `test_geri_al_requires_incident_id` (olay kimliğisiz çağrı REDDEDİLİR) ·
  `test_geri_al_refuses_when_plan_row_unapproved` (negatif kontrol) ·
  `test_geri_al_succeeds_on_approved_single_row_incident` (pozitif kontrol) ·
  `test_deaktive_et_needs_no_incident_and_no_evidence` (acil kolun etkilenmediğinin kanıtı)
  — **Sahip: Task 16**, `tests/test_pipeline_cli.py`.

---

### AÇIK-2 (KAPANDI — kararı yukarıda): Olay planına bağlı OLMAYAN bir geri alma nasıl kanıt bulur?

**Neden açık — R8(c)'nin mekanik yan etkisi.** R8(c) `RollbackGateEvidence`'ın köken
jetonunu `social.package_rollback_plans` satırına bağlıyor; `rollback_package` jetonu
`(incident_id, package_id)` anahtarıyla tüketiyor. Bunun sonucu şudur: **plan satırı
OLMAYAN bir geri alma artık mümkün değildir.** Oysa Task 16'nın alt komut listesinde
(plan 1797) olay kimliğinden bağımsız bir **`geri-al`** komutu duruyor. İki ifade
çelişiyor ve seçim maliyet farkı taşıyor — kendi başıma kapatmıyorum.

| Seçenek | Nasıl | Maliyet / etki |
|---|---|---|
| **A — `geri-al` olay kimliği İSTER** | Operatör önce `olay-plani`, sonra `olay-onayla`, sonra `geri-al --incident-id`. Tek yol kalır, kanıt zinciri tekilleşir | Kanıt/onay/iz üçlüsü TEK yoldan geçer; acil durumda operatörün üç komut koşması gerekir. K-38 acil kolu (`deaktive-et`) zaten kanıtsızdır ve **etkilenmez** — yani "aktif sürümü hemen indirme" yolu kapanmaz, kapanan yalnız "önceki sürüme kanıtsız dönme"dir |
| **B — `geri-al` tek satırlık örtük olay planı yazar** | Komut kendi `incident_id`'sini üretir, tek satırlık plan yazar, onay adımını **yine ister** | Operatör tek komut koşar; ama "olay" kavramı iki anlama gelir (gerçek K-145 olayı ve tek-paketlik sarmalayıcı) ve `etki-analizi` raporları bu sentetik olaylarla kirlenir |
| **C — `geri-al` KALDIRILIR** | Tek geri alma yolu `olay-geri-al`'dır; `geri-al` alt komutu plan listesinden çıkar | En az yüzey; ama plan gövdesinde adı geçen bir komutu silmek Task 16'nın beyanını değiştirir ve tek-paketlik geri alma için ayrı bir kolaylık kalmaz |

**Bloklama etkisi:** karar **Task 16 uygulanmadan ÖNCE** gerekir. Karara kadar R8(c)'nin
tüketici sözleşmesi (jeton `(incident_id, package_id)` ile tüketilir) **bağlıdır ve
değişmez**; değişecek olan yalnız `geri-al` alt komutunun var olup olmadığı ve olay
kimliğini nereden aldığıdır. R11'in geri kalanı (katman1 ayağı, `hata` düşüşü,
`deaktive-et` çıkışı, kapsam mührü) karardan bağımsız olarak bağlıdır.

---

### AÇIK-1 (KAPANDI — kararı yukarıda): Olay geri alması için yönetici onayı NEREDE kayıtlanır?

**Neden açık:** R11 kanıt üreticisinin *"kayıtlı yönetici onayı"*ndan okumasını bağlıyor,
ama planın hiçbir yerinde bir olay-geri-alma onayını **kaydeden** yüzey yok: `olay-plani`
plan satırlarını yazar (plan 1789-1791), `olay-geri-al` yürütür (plan 1791-1796); arada
kayıtlı bir onay adımı yoktur. Üretici bir yerden okumak zorunda, ve o yerin seçimi maliyet
farkı taşıyor — kendi başıma kapatmıyorum.

| Seçenek | Nasıl | Maliyet / etki |
|---|---|---|
| **A — Outbox kaydı** | Yeni CLI alt komutu `olay-onayla` → `notifications.record_admin_event(kind="sektor_paketi.olay_geri_alma_onayi", idempotency_key=<incident_id>)`; üretici `social.admin_events`'ten okur | Migration DEĞİŞMEZ; mevcut idempotency sözleşmesi yeniden kullanılır. Ama outbox bir **bildirim kuyruğudur**, onay deposu olarak kullanılması amacının biraz dışıdır |
| **B — Plan satırında kolon** | `social.package_rollback_plans`'e `onay_actor text NULL` + `onaylandi_at timestamptz NULL`; `olay-onayla` onları yazar, üretici tek satırdan okur | Anlamsal olarak en temiz (onay, onayladığı planın yanında durur) ve tek-satır okuması atomik. Ama **Task 6'nın migration 036 şemasını değiştirir** (plan 795-800) ve Task 6'nın test listesine iki CHECK testi ekler |
| **C — Onay adımı YOK** | `execute_rollback_plan` yönetici onayını komutun kendisinin çalıştırılmasından sayar | R11'in *"çağıran-taraflı boolean ASLA"* hükmüyle ÇELİŞİR — kaydı olmayan onay, uydurulmuş boolean'ın adı değişmiş hâlidir. Bu yüzden burada yalnız tamlık için sayılıyor |

**Bloklama etkisi:** karar verilene kadar `build_rollback_evidence`'ın `manager_approved`
ayağı tek noktada (fonksiyonun içinde) okunur ve karar kapanınca **yalnız o nokta** değişir;
R11'in geri kalanı (katman1 ayağı, `hata` düşüşü, `deaktive-et` çıkışı) karardan bağımsız
olarak bağlıdır. Karar Task 8 uygulanmadan ÖNCE gerekir; B seçilirse Task 6'dan önce
gerekir.
