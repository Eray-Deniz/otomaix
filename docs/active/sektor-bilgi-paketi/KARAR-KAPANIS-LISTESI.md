# Sektör Bilgi Paketi — Ürün Kararları Kapanış Listesi

> Hazırlayan: Claude, 2026-08-23. Kaynak: sentez Bölüm 17'nin "spec öncesi kullanıcı
> kararı" sınıfı (43 karar; K-20 aynı gün kanıtla kapandı → 42 açık).
> **Kullanım:** Eray listeye bir kez bakar; "itiraz etmediklerimi öneriye göre kapat"
> diyebilir. İtiraz edilenler tek tek konuşulur. Her öneri tek cümle gerekçeli;
> teknik ayrıntı spec'te, burada sade dil.
> **Durum sütunu:** boş = Eray kararı bekliyor.
> **2026-08-23 KAPANIŞ:** Tur tamamlandı — 45/45 karar Eray'la TEK TEK kapatıldı
> (toplu "itiraz etmediklerimi kapat" mekanizması kullanılmadı). ⚠️ işaretli 3 satır
> öneriden farklı kapandı. Kanonik kayıt: TASK.md Decisions Log + spec K-ID satırları.

## A. Paketin geri çekilmesi ve geçmiş kayıtlar

| K-ID | Soru (sade) | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-38 | Yeni sürüm koymadan paket geri çekilebilsin mi? | **Evet** | Acil durumun en ucuz kolu; ilk pakette geri alınacak eski sürüm olmadığından tek çıkış yolu bu. | ✅ öneri kabul (2026-08-23) |
| K-39 | Geçmiş postlar geriye dönük değiştirilebilsin mi? | **Hayır** | Post kaydı üretim anının kanıtı; değiştirilebilirse hangi paketin ne ürettiği güvenilir izlenemez. | ✅ öneri kabul (2026-08-23) |
| K-40 | "Değerli bilgi sessizce kaybolmaz" sözü bağlayıcı garanti mi, hedef mi? | **Hedef** | Garanti demek her turda kanıt yükü ve kabul kriteri demek; Faz 1'de bu yükü almadan aynı korumalar zaten kurulu. | ✅ öneri kabul — hedef (2026-08-23) |

## B. Bayat atama (paketi arşivlenmiş sektöre bağlı marka)

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-43 | Atama kaydı korunsun mu, silinsin mi? | **Korunsun** | Silmek veri kaybı; paket geri gelirse marka kendiliğinden tekrar çalışır. | ✅ öneri kabul (2026-08-23) |
| K-44 | Bayat durum sistemde işaretlensin mi? | **Evet (log/işaret)** | Ucuz ve teşhisi kolaylaştırır; zaten "atanmış ama paketsiz" log'u zorunlu. | ✅ öneri kabul (2026-08-23) |
| K-45 | Kullanıcıya bildirilsin mi? | **Faz 1'de hayır** | 2 marka varken bildirim arayüzü işi gereksiz; marka ayarları ekranı zaten güncel durumu gösterir. Yeniden açılma: marka sayısı artınca. | ⚠️ öneriden FARKLI kapandı: ÇİFT YÖNLÜ bildirim — yönetici + müşteri (bakım mesajı devre-dışı/geri-dönüş çifti) (2026-08-23) |

## C. Roller ve işletim ritmi

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-54 | Yönetici rolü ikiye bölünsün mü (koşan ↔ ürün sahibi)? | **Bölünmesin** | Solo işletim; iki rol de sensin. Bölünme ölçek gelince yeniden açılır. | ✅ öneri kabul (2026-08-23) |
| K-69 | Aktivasyon öncesi 20 maddelik hazırlık listesi imza kapısı olsun mu? | **Evet — otomatik ön-kontrol + tek onay** | Maddelerin çoğunu komut ailesi kendisi kontrol edip işaretler; sana yalnız özet + tek onay düşer. Sorumlusu: sen (operatör). | ✅ öneri kabul (2026-08-23; K-70 sorumlusu=operatör dahil) |
| K-26 | Tur periyodu tek mi, sektör başına mı? | **Alan sektör başına, Faz 1'de tek değer** | Pilotta tek sektör varken tek periyot yeter; alanı sektör-başına kurmak ileride bedava esneklik. | ✅ öneri kabul + GENİŞLEME: vade bildirimi eklendi (2026-08-23) |
| K-149 | Periyot değeri 3 ay mı, 6 ay mı? | **6 ayla başla** | Mevzuat acili için zaten tur-dışı kol var; 3 aylık elle tur yükü ölçülmeden fazla iddialı. İlk tur süresi ölçülünce revize edilir. | ✅ öneri kabul — 6 ay (2026-08-23) |
| K-71 | Açık sorular kapanmadan aktivasyon yapılabilsin mi? | **Yapılabilsin** | Açık soruları onay ekranında görürsün; bloklamak K-30 kararının (beklemeden ilerle) ruhuna aykırı. | ⚠️ öneriden FARKLI kapandı: BLOKLAR (2026-08-23) |
| K-72 | Yöneticinin reddi otomatik düzeltme turu başlatsın mı? | **Hayır — elle** | Reddin sebebi değişir; otomatik tur yanlış işi tetikleyebilir. İstersen yeni koşuyu sen tetiklersin. | ✅ öneri kabul (2026-08-23) |
| K-73 | Acil (tur dışı) güncellemede tam araştırma turu zorunlu mu? | **Hayır** | Mevzuat düzeltmesi için üç araçlı tam tur aşırı; şart: doğrulanmış kaynak kanıtı + iki denetçinin yalnız o değişiklik üzerinde hızlı doğrulaması. Onay kapısı zaten kalkmıyor. | ✅ öneri kabul (2026-08-23) |
| K-56 | Eşik aşımında otomatik alarm katmanı kurulsun mu? | **Faz 1'de hayır** | Eşikler ölçülmeden alarm kurulamaz (uydurma eşik yasak); log+metrik var. Yeniden açılma: pilot ölçümleri sonrası. | ⚠️ öneriden FARKLI kapandı: OLAY-BAZLI anında uyarı Faz 1'de kurulur (eşik yok, paketsiz-düşüş anında bildirim) (2026-08-23) |

## D. Denetim orkestrasyonu (komut ailesi kurulurken)

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-77 | Denetimi başlatan kimlik/yetki modeli? | **Yeni model kurulmaz — lokal tek kullanıcı** | Her şey senin makinende, mevcut CLI kimlikleriyle koşuyor; ayrı yetki sistemi Faz 1'de gereksiz yük. | ✅ öneri kabul (2026-08-23) |
| K-79 | İki denetçinin izolasyonu ve aynı girdiyi alması teknik garanti olsun mu? | **Evet (hafif)** | Komut ailesi aynı dosya setini iki ayrı oturuma verir — zaten çalışma biçimimiz; garanti bedava denecek kadar ucuz. | ✅ öneri kabul (2026-08-23) |
| K-80 | Tekrar-üretilebilirlik damgası (model/sürüm/tarih/girdi özeti) zorunlu olsun mu? | **Evet** | Artefakt satırına birkaç alan; "bu sonuç nereden çıktı" sorusunu kalıcı cevaplar. | ✅ öneri kabul (2026-08-23) |
| K-81 | Denetçi çıktısının otomatik biçim kontrolü kurulsun mu? | **Evet** | brief-doctor emsali; deterministik ve ucuz. | ✅ öneri kabul (2026-08-23) |
| K-150 | Tek geçerli raporla sentez engellensin mi? | **Evet** | İki bağımsız denetçi mimarinin özü; tek raporla koşmak kör denetimin değerini düşürür. | ✅ öneri kabul (2026-08-23) |
| K-82 | Zaman aşımı / yarım kalan koşuda ne olur? | **Koşu "tamamlanmadı" işaretlenir; yeniden koşum yeni deneme kimliği alır** | Dosya ezilmez, iz kaybolmaz; basit ve yeterli. | ✅ öneri kabul (2026-08-23; K-83 yeniden-koşum kimliği dahil) |
| K-105 | Aktivasyon ara-penceresi için özel okuyucu testi zorunlu olsun mu? | **Hayır** | Pencere zaten emniyetli (paketsiz yola düşer) ve loglanıyor; ayrı test isteğe bağlı plan kalemi. | ✅ öneri kabul (2026-08-23) |

## E. İçerik ve öncelik politikası

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-118 | Kullanıcının somut isteği ↔ markanın ses profili çatışırsa? | **Kullanıcı isteği kazanır** (yasak kelimeler hariç) | Ürün felsefesi: kullanıcı ne istediyse o; ses profili yumuşak yönlendirme, sert kısıt değil. | ✅ öneri kabul (2026-08-23) |
| K-119 | Anma günü satış yasağı, kullanıcı satış istese bile geçerli mi? | **Evet — tek istisna bu** | 10 Kasım'da indirim postu markayı yakar; kültürel uygunluk ürünün değer vaadinin parçası. | ✅ öneri kabul (2026-08-23) |
| K-120 | "Anma günü için içerik önerilmez" seçeneği ile "en az 2 çağrı kalıbı" kuralı çelişiyor — çözüm? | **Boş alanın özel temsili** ("içerik-önerilmez" değeri; kapı bunu eksik saymaz) | En az revizyonla iki kuralı da yaşatır; brief sözleşmesinin sonraki sürümüne girer. | ✅ öneri kabul (2026-08-23) |
| K-121 | Paket şişince önce ne kırpılır? | **Önerilen yeni sıra: mevzuat/güvenlik en üstte korunur** | Mevzuat bilgisi kırpılarak yer açılması kabul edilemez; sıra öncelik hiyerarşisiyle tutarlı. | ✅ öneri kabul (2026-08-23) |
| K-122 | Churn koruması ("yeni ama zayıf öğe, sırf yeni diye doğrulanmışı atamaz") benimsensin mi? | **Evet** | Bilgi kaybı güvencesinin doğal tamamlayıcısı; bedava. | ✅ öneri kabul (2026-08-23) |
| K-123 | "Güçlü kaynak" tanımlansın mı? | **Evet** — resmî/birincil kaynak + güncellik çekirdeği | Tanımsız kalırsa "muhtemel uydurma" ayrımı denetçi keyfine kalır; tam metin sözleşme revizyonunda (teknik). | ✅ öneri kabul (2026-08-23) |
| K-124 | Çıkarma için kanıt yeterlilik eşiği? | **En az bir doğrulanmış kaynaklı kanıt satırı; mevzuat/güvenlikte iki denetçi uyumu** | Minimal ve mekanik; kanıtsız çıkarma zaten yasak, bu sadece "kanıt nedir"i netler. | ✅ öneri kabul (2026-08-23) |
| K-126 | Tek resmî kaynak istisnasının kesin sözleşmesi? | **Tanımlansın:** resmî kaynak + en az bir denetçinin URL doğrulaması | İstisna kapısı belirsiz kalırsa ya hiç kullanılamaz ya kötüye açılır. | ✅ öneri kabul (2026-08-23) |
| K-127 | Koşu en az kaç kaynakla devam edebilir? | **2** | Tek kaynakla mutabakat sinyali üretilemiyor; 1'e düşerse koşu durur, kararı sen verirsin. | ✅ öneri kabul — 2 (2026-08-23) |
| K-129 | "Mevzuat/güvenlik sayılır → turu bloklar" alan listesi sabitlensin mi? | **Evet:** yasaklar-ve-hassasiyetler alanı + mevzuat/tarih/sayı içeren tüm iddialar | Liste sabit olmazsa neyin turu durduracağı her koşuda yorum işi olur. | ✅ öneri kabul (2026-08-23) |

## F. Güvenlik, gizlilik, saklama

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-135 | "Yazma yetkisi yalnız operatör + koşu yüzeyinde" kural olsun mu? | **Evet** | Zaten fiilî durum; kurala çevirmek bedava, ileride çok kullanıcıda sınır hazır olur. | ✅ öneri kabul (2026-08-23) |
| K-10 | Prompt-injection'a özel ek savunma kurulsun mu? | **Faz 1'de hayır (bilinçli risk kabulü)** | İçerik zaten iki kör denetçiden ve senin onayından geçiyor; özel tarama katmanı ayrı bir iş. Yeniden açılma: paket sayısı/kaynak çeşitliliği artınca. Risk kaydında açık kalır. | ✅ öneri kabul (2026-08-23) |
| K-136 | Orkestrasyon günlüklerinde sır tutulmaması kuralı? | **Evet** | Mevcut global sır hijyeniyle aynı çizgi; maliyeti yok. | ✅ öneri kabul (2026-08-23) |
| K-137 | Araç-eşlemesinin denetçi bağlamına sızmaması teknik garanti olsun mu? | **Evet (yapısal)** | Komut ailesi denetçiye eşleme bilgisini hiç vermez — ayrı mekanizma değil, tasarım kuralı. | ✅ öneri kabul (2026-08-23) |
| K-16 | Paket içeriği arayüzden kimlere okunur? | **İç kullanım + yönetici; müşteriye kapalı** | Müşteri paketi zaten üretim çıktısı üzerinden yaşıyor; içeriği açmanın ürün gerekçesi yok. | ✅ öneri kabul (2026-08-23) |
| K-138 | Araç ↔ ham rapor eşlemesi kalıcı kaydedilsin mi? | **Evet** | Kanıt zinciri tamamlanır; körlük kaydın kendisiyle değil erişimiyle korunur. | ✅ öneri kabul (2026-08-23) |
| K-139 | Ham katman + eşlemeyi kim okuyabilir? | **Yalnız operatör/yönetici** | Denetçi bağlamına girmez (körlük); müşteriye zaten kapalı. | ✅ öneri kabul (2026-08-23) |
| K-140/141 | Ham katman ve paket sürümleri ne kadar saklanır? | **Süresiz** | Veri küçük, arşiv güvencesi geri getirmeye dayanıyor; süre koymak salt-ekleme kararını yeniden açardı. Yeniden değerlendirme: hacim/KVKK sinyali. | ✅ öneri kabul — süresiz (2026-08-23) |
| K-142 | Aktive edilmemiş taslaklara ayrı saklama kuralı? | **Hayır — onlar da kalıcı** | Ayrı kural ayrı mekanizma demek; basitlik kazanır. (Süre sorusu K-143 böylece hiç doğmaz.) | ✅ öneri kabul (2026-08-23) |
| K-144 | "Faz 1'de ayrı hukuk onayı gerekmez" değerlendirmesi benimsensin mi? | **Evet (risk kabulü)** | Yalnız kamuya açık yayımlanmış kaynaklardan derleme; hukuk eşiği gerektiren iki iş (ürünleştirme, platform kazıma) zaten kapsam dışı. | ✅ öneri kabul (2026-08-23) |

## G. Pilot (Codex bulgusuyla listeye eklendi — spec'te açık bırakıldı)

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-29 | Pilot nasıl koşulur: A) kontrollü test markası / B) mevcut kayıtlı markalar? | **A — test markası** | Taze ölçüm: iki kayıtlı marka da kuyumcu değil (Otomaix + MyGoodShoes) — B seçeneği kuyumculuk pilotu için anlamlı çıktı üretmez. | ✅ öneri kabul — A (2026-08-23) |
| K-31 | Pilota takvim süresi tanımlansın mı? | **Hayır — ön koşul modeli** | Süre değeri hiçbir belgede yok; uydurma süre koymak yerine genişleme ön koşullara bağlanır (K-32…K-37 kapı kararları ayrıca gelecek). | ✅ öneri kabul — ön koşul modeli (2026-08-23) |

## H. Arayüz

| K-ID | Soru | Öneri | Gerekçe | Durum |
|---|---|---|---|---|
| K-19 | Alt sektör teyit bileşeni hangi ekranda? | **Onboarding + marka ayarları, mevcut sektör seçiminin yanında** | İki ekran da sektör listesini zaten çekiyor; yeni yüzey açılmaz. | ✅ öneri kabul (2026-08-23) |

---

**Kapanış yöntemi:** Eray'ın onayladığı satırlar TASK.md Decisions Log'a tarih +
"öneri kabul" kaydıyla geçer; itiraz edilen satırlar ayrı konuşulur. Kapanan
kararların sentez deposu Bölüm 17 / Ek B'ye işlenmesi ayrı bir sweep işidir
(kardeş-site süpürme kuralı) ve bu listede değil, kapanış commit'inde planlanır.
