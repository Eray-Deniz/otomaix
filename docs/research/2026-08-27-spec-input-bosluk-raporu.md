---
title: Spec-input → Spec eksik-aktarma boşluk raporu (Plan 2 hazırlığı)
status: done
date: 2026-08-27
kaynak: docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md
hedef: docs/specs/2026-08-21-sektor-bilgi-paketi.md
tetik: Plan 1 yürütülürken K-02'nin eksik aktarıldığı görüldü (Eray, 2026-08-27); tek vaka
  düzeltilmiş ama yayılımı hiç ölçülmemişti (İlke 6).
---

# Spec-input → Spec eksik-aktarma boşluk raporu

## Yöntem

İki geçiş, çünkü iki ayrı kayıp türü var:

1. **Kimlik geçişi** — girdideki karar kartlarının hangileri spec'e hiç geçmemiş.
   Mekanik; dosyanın tamamını kapsar.
2. **Kart geçişi** — spec'te geçen kararların kartındaki öneri / sahip / çözüm yolu /
   bağlı kararlar bilgisinin eksilip eksilmediği. K-02 sınıfı budur. Yalnız Plan 2
   bölümleri (spec §8 hat · §9 motor · §13 işletim · §15 pilot) taranır.

**Kapsam dışı (dürüst etiket):** Plan 1 bölümlerinin kart geçişi yapılmadı. Gerekçe:
Plan 1 yürütüldü ve canlıda; oradaki bir eksik plan yazımını bloklamıyor. Kimlik geçişi
Plan 1 alanını da kapsıyor. **Yeniden açılma koşulu:** Plan 1 alanında bir kusur çıkarsa
o bölümlerin kart geçişi koşulur.

## Doğrulanan zemin

- Repodaki girdi kopyası araştırma deposundaki asılla **bayt-özdeş**
  (`tail -n +7 <kopya> | sha256sum` = `efe2170…b50b4d`, koşuldu 2026-08-27).
  Tek fark başa eklenen 6 satırlık salt-okunur notu.
- §17'den ayıklanan kart sayısı **162/162** — belgenin kendi alt bölüm sayılarına karşı
  doğrulandı (39+36+51+36). İlk ayıklama 156 vermişti; harf ekli kimlikler
  (`K-01a` · `K-04a-d` · `K-01b`) desene uymadığı için kaçmıştı, desen düzeltildi.

## 1. Geçiş — kimlik: 162 karttan 32'si spec'e hiç geçmemiş

`K-04b/c/d` ilk sayımda eksik görünüyordu; spec `K-04a–d` aralık yazımı kullanıyor,
kapsanıyorlar. Gerçek eksik **32**.

### A. Plan 2'nin göbeğinde — kalıp kimliği ailesi ve motor geçişi (5)

Spec, kalıcı kalıp kimliğini (K-84) **politika motorunun ön koşulu** sayıyor. O ailenin
dört üyesi spec'e hiç geçmemiş; motorun temeli bu yüzden spec'te yarım.

| ID | Soru | Sahip (girdiye göre) | Girdinin blok sınıfı |
|---|---|---|---|
| K-85 | İki kalıbın semantik olarak aynı sayılma ölçütü tanımlanacak mı? | Teknik (mekanizma) + **ürün** (kalite/risk) | Koşullu — motor Faz 1'de olduğu için gerekli |
| K-153 | Eş anlamlı/yeniden yazılmış kalıplar hangi yöntemle eşleştirilecek? (deterministik / hakemli) | Teknik (mekanizma) + **ürün** (operasyon yükü) | Koşullu — K-85 kapanınca gerekli. Hakemli dal kalıp başına insan kararı doğurur |
| K-86 | Kalıp kimliği hangi değişiklik seviyesine kadar korunur? (`guncelle` ↔ `cikar+ekle`) | Teknik | Koşullu — K-84'te sabit kimlik seçilirse doğar |
| K-154 | `guncelle` ↔ `cikar+ekle` ayrımı karar izinde nasıl temsil edilir? | Teknik | Koşullu — K-84'e bağlı. Kaynak kendi içinde çelişiyor |
| K-134 | Motor işletime alınırken eski doğrudan operatör-onay akışı ne olacak? (paralel / kaldır) | **Ürün** | Koşullu — motor Faz 1'de olduğu için gerekli; geçiş planının parçası |

### B. Pilot içerik kararları — veritabanına yazmadan önce kapanmalı (2)

Bunlar spec'in `K-04a–d` diye saydığı dört operatör kararının kardeşleri; spec'e geçmemişler.

| ID | Soru | Not |
|---|---|---|
| K-146 | Takvime 24 Kasım Öğretmenler Günü eklensin mi? | Sabit gün, `anma` bağı yok |
| K-147 | Okula dönüş dönemi takvime eklensin mi? | **Şema etkisi var:** eklenecekse takvim kaydı gün değil DÖNEM taşımalı |

### C. Teknik — plan kendisi bağlayabilir (4)

Girdi bunları "spec içinde teknik olarak çözülür" sınıfına koymuş; spec çözmemiş.

| ID | Soru | Bugünkü durum |
|---|---|---|
| K-111 | Paket JSON doğrulayıcı şemasının kesin biçimi | Plan 1 `validate_package_content`'i yazdı — fiilen çözüldü, karar olarak kayda geçmedi |
| K-114 | Aday alt sektör kümesini hangi sorgu yetkili üretir | Plan 1 tek uç açtı (`sub-sector-candidates`) — fiilen A seçildi, kayıtsız |
| K-112 | Takvim erişilemezse özel gün bloğu nasıl davranır | ÇÖZÜLMEDİ. Girdi "önce bugünkü davranış taze doğrulanır" diyor |
| K-117 | Web sitesi olmayan marka için öneri hangi uçtan çağrılır | ÇÖZÜLMEDİ |

### D. Rol ve sahiplik kararları (12)

K-55 (teknik sahip kim) · K-57 (alarmı kim izler) · K-58 (olayda kim bilgilendirilir) ·
K-59 (inceleme bulgusu kabul yetkisi) · K-60 (teknik doğruluk operatöre geçilsin mi) ·
K-61…K-68 (sekiz risk satırının sahipliği: tür↔kategori çatışması · motorun kararsız
bıraktıkları · girdi kayması · içerik aynıyken yeni sürüm · politika↔onay arası sürüm
değişimi · müşteri tercihinin sektöre karışması · uzun bağlamlı sentezin kaçırması ·
kişisel veri doğrulaması).

Spec `K-54 = bölünmez` (solo işletim, tek yönetici rolü) kararını taşıyor; bu on ikisinin
çoğu fiilen Eray'a düşüyor. Ama kartlar açıkça *"K-54'e indirgenemez"* diyor — sahiplik
ayrı bir sorudur. Tek toplu kararla kapatılabilirler.

### E. Kapsam dışı ilan edilmiş ama karar olarak kapatılmamış (8)

K-46 (toplu marka atama eşiği) · K-48 · K-49 · K-50 (üç bakım borcu) · K-51 (kök rehber
yolu tam kapsam sonrası kaldırılsın mı) · K-53 · K-148 (ölçeklenebilirlik artefaktı
kanonik sayılsın mı / içeriği denetlensin mi).

Spec §2.2 bakım borçlarını *"bu işte dokunulmaz"* diye kaydetmiş — yani **içerik olarak**
kapsanmışlar, **karar olarak** kapatılmamışlar. Düşük risk.

### F. Kapalı karar, spec'e hiç taşınmamış (1)

| ID | Durum |
|---|---|
| K-145 | ✅ **KAPANDI — B** (2026-08-17, kullanıcı kararı): kural hatasında **vaka bazında** geri alma. Etkisi kanıtlananlar geri alınır; etki alanı güvenilir ayrılamıyorsa kuralın uygulandığı tümü geri alınır. Ölçütler tanımsız ve uydurulmamış. **Spec'e hiç geçmemiş** — Plan 2/3'ün geri alma davranışını doğrudan ilgilendirir |

Bu, Eray'ın uyardığı sürüklenmenin en saf hâli: karar verilmiş, gerekçesi yazılmış, spec'e
taşınmamış.

## 2. Geçiş — kart karşılaştırması

*(devam ediyor)*

## 2. Geçiş — kart karşılaştırması

Üç eksende tarandı. Her eksen ayrı bir kayıp türünü yakalar.

### Eksen 1 — düşen öneri

Girdideki 162 karttan **18'i açık ve somut bir öneri taşıyor**. Ham tarama 17'sinin
spec'e geçmediğini söyledi; **on sekizi de tek tek doğrulandı ve gerçek sayı 3 çıktı.**
Kalan 14'ünde spec öneriyi ya kelimesiz ama özüyle taşımış (ör. K-04a–d'nin dördünün
önerisi §15.2'de aynen duruyor) ya da karar sonradan kapanmış.

| ID | Kartın önerisi | Spec'teki hâli | Durum |
|---|---|---|---|
| K-02 | **A** — paket `video_kodlar`'ından sektöre özgü hareket havuzu; gerekçe: paketsizde prompt değişmez ve ek model çağrısı doğmaz | Yalnız "hareket dili (K-02)" — açık karar olarak listelenmiş | **DÜŞTÜ** (bilinen vaka; Eray 2026-08-24'te kapattı) |
| K-23 | **B + rapor** — kararsızda mevcut kalıbı koru, rapora yaz. Gerekçe: (A) ölçekte insana iş geri yükler, (C) tek maddede turu bloklar | Üç yerde geçiyor, üçünde de yalnız "K-23 açık" | **DÜŞTÜ** |
| K-25 | **A** — aktör alanı eklensin; maliyet yok denecek kadar az, olmadan kötü sürümün kaynağı (motor kuralı mı sentez mi) teşhis edilemez | "Aktör alanı … **K-25**" — açık olarak listelenmiş | **DÜŞTÜ** |
| K-12 | **A — ama önce ölçülmeli**; iki çelişen boyut hedefi var | Çelişki taşınmış ("iki uzlaştırılmamış tahmin"), tercih taşınmamış | **KISMİ** — kapı olmadığı için etkisi düşük |

### Eksen 2 — "spec içinde teknik olarak çözülür" denip çözülmeyenler

K-02'nin asıl sürüklenme ekseni budur: kart kararı **teknik** sayıp spec'in çözmesini
bekler, spec ise açık ürün kararı gibi bırakır.

Bu sınıfta **37 açık kart** var:

- **21'ini spec çözmüş** ✅
- **4'ü spec'e hiç ulaşmamış** — K-111 · K-112 · K-114 · K-117 (1. geçişte de çıktılar)
- **12'sini spec açık bırakmış.** Bunlardan K-115/K-116 spec'te açıkça "plan işidir"
  denip Plan 1'e devredilmiş ve Plan 1 onları bağlamış; K-110'u Plan 1 bilinçle
  bekletmiş. **Geriye 9 gerçek boşluk kalıyor:**

| ID | Soru |
|---|---|
| K-09 | Aynı koşunun iki kez yüklenmesi engellenecek mi? |
| K-74 | Sentezin on açık soru sınırı aşılırsa ne olacak? |
| K-75 | Denetçinin beş öneri sınırı aşılırsa ne olacak? |
| K-87 | Pakete hiç girmeyen aday karar izinde nasıl temsil edilecek? |
| K-88 | Mekanik elemenin hangi bulgusu *eleme*, hangisi *not* üretecek? |
| K-107 | Kısmi sürümde değişmeyen alanlar karar günlüğünde nasıl temsil edilecek? |
| K-108 | Eşleşmeyen özel gün notu karar günlüğünde nasıl temsil edilecek? |
| **K-151** | **Kalıcı kalıp kimliğinin biçimi sözleşmede sabitlenecek mi?** |
| **K-152** | **Kalıcı kalıp kimliğinin üretim yöntemi tanımlanacak mı?** |

Son ikisi kritik: spec kalıp kimliği sözleşmesini **politika motorunun ön koşulu**
sayıyor. Yani motorun ön koşulu, spec'in kendi sınıflandırmasına göre spec içinde
teknik olarak çözülmesi gerekirken çözülmeden kalmış.

### Eksen 3 — karar sahibi ayrımı (Plan 2 için doğrudan kullanılabilir çıktı)

Spec'in Plan 2 bölümlerinde (§8 hat · §9 motor · §13 işletim · §15 pilot)
**50 karar hâlâ açık.** Girdideki `Karar sahibi` sütununa göre ikiye ayrılıyorlar.
Bu ayrım İlke 8'in gereği: teknik olanları Eray'a onaylatmak sahte-checkpoint üretir.

#### Eray'a gidecek — ürün/yönetici kararı (21)

| ID | Soru |
|---|---|
| K-11(a) | Kör değerlendirme örnekleminin boyutu |
| K-11(b) | Katman-2 için geçme eşiği konulacak mı? |
| K-12 | Tier 2 belirteç bütçesi paket bloğu ile Marka DNA blokları için birlikte mi yönetilecek? |
| K-13 | Faz 1'de eşzamanlı işletilecek aktif paket tavanı |
| K-14 | Koşu öncesi ön kontrol kurulacak mı? — denetçi-2 ortamının web erişimi her turdan önce sınanacak mı |
| K-17 | Araştırma çıktıları hangi teslim yapısına yazılacak? |
| K-23 | Motorun karar veremediği maddeler ne olacak? |
| K-32 | Katman-1 düzeneğinin bütün yüzeylerde yeşil olması genişleme kapısı mı? |
| K-33 | İlk turun operasyon süresinin ölçülmüş olması genişleme kapısı mı? |
| K-34 | K-01b'nin kapanmış olması genişleme kapısı mı? |
| K-35 | K-02'nin kapanmış olması genişleme kapısı mı? |
| K-36 | Atama akışının gerçek kullanıcıyla en az bir kez denenmiş olması genişleme kapısı mı? |
| K-37 | Kalibrasyon kanıtı ölçeğe geçişin koşulu olacak mı? |
| K-41 | Özet farkta "eşik-üstü çıkarılanlar" için eşik konulacak mı? |
| K-42 | Sinyal odaklı özet kontrolü benimsenecek mi? |
| K-84 | Kalıp kimliği sürümler arası nasıl korunacak? |
| K-125 | Motor katmanında `guncelle` ve `cikar` için iki denetçi mutabakatı kapısı benimsenecek mi? |
| K-130 | Değişim büyüklüğü bariyeri benimsenecek mi? |
| K-131 | Ekleme oranı bariyeri benimsenecek mi? |
| K-132 | Kararsızlık oranı bariyeri benimsenecek mi? — motorun kararsız bıraktığı madde oranı eşiği aşarsa tur durur |
| K-133 | Kuru mod zorunlu olacak mı? — motorun kararlarını uygulamadan önce yalnız raporlaması |

#### Planın kendi bağlayabileceği — teknik sahip (29)

Bunlardan 5'i Plan 1'de adı geçmiş (K-07, K-08(a), K-08(b), K-94, K-103); 24'ü hiç ele alınmamış.

| ID | Soru | Plan 1'de |
|---|---|---|
| K-07 | Üretim sürüm damgası nerede tutulacak? | geçti |
| K-08(a) | Araştırma artefaktındaki sektör ilişkisi hangi modelle kurulacak? | geçti |
| K-08(b) | `brands.sub_sector_id`'nin yalnız alt sektör satırlarını kabul etmesi nerede zorlanacak? | geçti |
| K-24 | Motorun eşik ve limit değerleri ne zaman belirlenecek? — değişim oranı, alan bazlı sınırlar, ekleme oranı tava | — |
| K-25 | Karar satırına aktör alanı eklenecek mi? — kararı motor mu insan mı verdi | — |
| K-74 | Sentezin on açık soru sınırı aşılırsa ne olacak? | — |
| K-75 | Denetçinin beş öneri sınırı aşılırsa ne olacak? | — |
| K-76 | Denetim hangi bağlantı yöntemiyle başlatılacak? | — |
| K-78 | İki denetim paralel mi sıralı mı yürütülecek? | — |
| K-83 | Yeniden koşumda hangi deneme veya artefakt kimliği üretilecek? | — |
| K-87 | Pakete hiç girmeyen aday, karar izinde nasıl temsil edilecek? | — |
| K-88 | Biçimsel-mekanik elemenin hangi bulgusu *eleme*, hangisi *not* üretecek? | — |
| K-89 | Mekanik kapının kontrol kümesi sözleşmede sabitlenecek mi? | — |
| K-90 | `tur durduruldu` öğesi `bloklandı` ile birleştirilecek mi? | — |
| K-91 | İlk paket koşusunda `değişiklik yok` sonucu geçersiz sayılacak mı? | — |
| K-92 | Sıra ve biçim farklarının yanlış değişiklik sayılmasını önleyecek canonical üretim kuralı tanımlanacak mı? | — |
| K-93 | `değişiklik yok` ve `bloklandı` koşuları paket satırı oluşturmadan nerede kayıtlanacak ve nasıl sorgulanacak? | — |
| K-94 | Motorun değerlendirdiği base sürüm ile onay anındaki aktif sürüm farklıysa sonuç geçersiz sayılacak mı? | geçti |
| K-95 | Politika sonucu ve koşu kaydı nerede tutulacak? | — |
| K-96 | Motor sentez kararını değiştirdiğinde özgün sentez, nihai aday ve gerekçeli fark ayrı mı saklanacak? | — |
| K-97 | Motorun sürümü ve yapılandırması her koşuya damgalanacak mı? | — |
| K-98 | Yöneticiye gösterilen anlık görüntü değiştirilemez olacak mı? | — |
| K-99 | Son onay veya ret olayı kimlik ve zaman damgasıyla kaydedilecek mi? | — |
| K-100 | Denetçi sözleşmesine eklenecek yeniden doğrulama envanterinin adı ve şeması tanımlanacak mı? | — |
| K-103 | Aktivasyon ve geri alma yetkisi teknik olarak nasıl zorlanacak? | geçti |
| K-107 | Kısmi sürümde değişmeyen alanlar karar günlüğünde nasıl temsil edilecek? | — |
| K-108 | Eşleşmeyen özel gün notu karar günlüğünde nasıl temsil edilecek? | — |
| K-151 | Kalıcı kalıp kimliğinin biçimi sözleşmede sabitlenecek mi? | — |
| K-152 | Kalıcı kalıp kimliğinin üretim yöntemi tanımlanacak mı? | — |


## Dedektör dürüstlüğü

Kapanış tespiti mekanik yapıldı ve **pozitif kontrolden geçirildi**: elle doğrulanmış
35 kapalı + 23 açık kimlikten oluşan kontrol kümesinde **0 yanlış pozitif**, 3 yanlış
negatif (K-69 · K-70 · K-144 — bu üçünde kapanış işareti kimlikten ÖNCE yazılmış).
Üçü elle doğrulanmış istisna olarak eklendi. İlk sürümler hem yanlış pozitif hem
yanlış negatif üretiyordu (K-23 komşu cümledeki `K-149 — KAPANDI` ifadesine takılıyor,
K-69 ise kapalıyken açık sayılıyordu); cümle sınırına saygılı sürümle düzeltildi.

## Kapsam sınırı (dürüst etiket)

- Plan 1 bölümlerinin (spec §1-7, §10-12, §14, §16-17) **kart geçişi yapılmadı**.
  Kimlik geçişi onları da kapsıyor — K-112 ve K-117 oradan çıktı.
  **Yeniden açılma koşulu:** Plan 1 alanında bir kusur çıkarsa o bölümlerin kart geçişi koşulur.
- Girdinin §17 dışındaki gövde metniyle (§7 · §14 · §15 · §16 prose'u) spec arasındaki
  **karar-dışı içerik** karşılaştırması yapılmadı — bu tarama karar kartları eksenlidir.
  **Yeniden açılma koşulu:** Plan 2 yazımında bir sözleşme ayrıntısının spec'te
  bulunmadığı fark edilirse.
