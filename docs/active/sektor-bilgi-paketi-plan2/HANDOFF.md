---
task: sektor-bilgi-paketi-plan2
written: 2026-09-21
---

# Resume From

**SIRADAKİ İŞ, TEK CÜMLE: Grup 3 kodu ve iki sözleşme COMMIT EDİLDİ (dış depo `34a34db`, pin ona
bağlı); sırada `/review-claude-codex` (ayrıştırıcı + motor + sentez değişti — zorunlu), sonra Eray
üç araştırmayı yeni brief'le alır → tek tur.** Push EDİLMEDİ. Kalem listesi ve ilk turda ölçülecekler
TASK.md Open Problems ilk maddede; kararlar Decisions Log "Grup 3 — kod tarafı".

**Bugün ne oldu:** Altı kalem indi. Brief-doctor 9 sütun + `[C: …]` kapsama + `kaynak-bulunamadı`;
EK-M kanıt kaydı basıyor; sentez `validate` etiket sızıntısını reddediyor; motor kanıt kapısı
(mutabakat=varlık · çelişki → açık soru · alan sınıfına göre destek kümesi · hepsi `yok` →
içerikte bekletme, riskte açık soru); iki sözleşme düzenlendi; pin geçici; 47 yeni test.
**Ardından Eray Codex'i dışarıdan koşturdu: 5 bulgu (2 yüksek, 3 orta), 5'i de kapatıldı** —
(1) URL'siz satırın destek beyanı kanıt sayılmaz (`_etkin_destek`); (2) sentez talimatı
"aday yapma, not düş"ü içerikle sınırladı, risk maddesi `ekle` ile motora gider (EK-M başlığı +
sözleşme ADIM 1); (3) boş `[C: ]` etiketi bozuk sayılır; (4) `KAYNAKTA YOK` de URL eşitliği ister
("aynı iddia, aynı URL"); (5) sızıntı kapısı kaçışlı yazımı (`\[uyarlama\]`) da yakalar.
Her biri önce bellekte yeniden üretildi, sonra düzeltildi; 8 regresyon testi eklendi.

**Dosya durumu:**
- Dış depo: iki sözleşme `34a34db` ile commit'lendi (yalnız o iki dosya seçildi). **Çalışma
  ağacında Eray'ın 44 silinmiş dosyası (SWEEP-* · TASLAK-* · kök `kuyumculuk.md`) hâlâ
  commit'lenmemiş duruyor — bana ait değil, dokunulmadı; Eray karar verir.**
- Pin: `commit=34a34db` + üç dosyanın hash'i; pin testi yeşil (191 passed, paketleme dâhil).
- Monorepo: kod + testler + pin + TASK/HANDOFF TEK commit'te (bu oturumun son işlemi).

# Verification

| Ne | Taze çıktı |
|---|---|
| Tam takım, Codex düzeltmeleri SONRASI (`pytest -q`, 401 s) | **4704 passed / 0 failed** |
| Tam takım, ilk koşum (Codex öncesi) | 4693 passed / 1 failed — kırık test aynı oturumda düzeltildi (`_kap` çağrı yeri 8→9) |
| Codex karşı örnekleri (bulgu 1 · 3 · 5) | düzeltmeden ÖNCE bellekte yeniden üretildi: `notlu-gecti`+`destek=öneri`/URL boş · `[C: ]` → `gecti` 0 not · kaçışlı etiket → `[]` |
| Mutasyon (dosya yedeğiyle geri alındı, 7 kol) | kanıt kapısı 6/6 · çelişki 2/2 · sızıntı 4/4 · EK-M 1/1 · geri bağlantı 5/5 · kaynaksız muafiyet 3/3 · `destek=yok` hücre 5/5 — **hepsi yakalandı** |
| Gerçek eski raporlar (Kaynak-1 · Kaynak-3) yeni kapıdan | **0 iddia**, "ESKİ sözleşme sürümünün başlık satırı" kap notu (ölçüldü; satır koluna ulaşmıyor) |
| Prompt regresyonu (paketli/paketsiz byte-exact, `tests/prompt_regression/`) | tam takımın içinde koştu, yeşil — üretim kodu DOKUNULMADI |

**DENENMEYEN / DOĞRULANMAYAN:**
- Yeni şablonla hiçbir gerçek rapor alınmadı; LLM'lerin 9 sütunu, `[C: …]`'yi, `kaynak-bulunamadı`yı
  doğru yazması ÖLÇÜLMEDİ. Fixture sentetik.
- **K-129 rakam kuralı:** rakam içeren her içerik maddesi risk sınıfına düşer ve `öneri`/`uygulama`
  desteğiyle AÇIK SORU açar. Canlıda kaç maddeyi vuracağı ÖLÇÜLMEDİ; ilk turda açık soru sayısı
  artarsa kök burasıdır (K-129'un kabul edilmiş yanlış-pozitif riski, kanıt kapısına genişledi).
- `/review-claude-codex` KOŞMADI (kirli ağaca karşı güvenilmez; önce commit). Codex'in dış
  incelemesi Codex ayağını karşılar ama Claude alt-hakemi koşmadı; Codex'in beş düzeltmesi de
  bağımsız hakem GÖRMEDİ (yalnız kendi regresyon testleri + tam takım).
- `/security-review-claude-codex` dalda hâlâ borç.
- Grup 3'ün süresi ölçülmedi (oturum başı damgası alınmadı).

**TUZAKLAR:**
- Pin'i dış commit'ten ÖNCE bump etme; dış commit'e Eray'ın silinmiş 44 dosyasını KATMA.
- `VARSAYILAN_DESTEK = "veri"` (test fixture'ı): iki alan sınıfında da sayılır — mevcut motor
  testleri kanıt kapısına takılmasın diye seçildi; kapının kendisi ayrı testlerde ölçülüyor.
- Sentez `validate` artık `destek=`/`yer=` düz metnini de reddeder; bir paket metni meşru olarak
  "yer =" içeriyorsa kapı yanlış-pozitif verir (kabul edilmiş, sözleşmeye yazıldı).
- Koşu `kosu-7705437…` hâlâ `calisiyor`; eski Kaynak-1..6 yeni hatta girdi olamaz (0 iddia,
  sentez boş dizinle başlamaz).

# Risks

- Yeni şablon + 9 sütun + geri bağlantı LLM'e yapısal yük; ilk turda brief-doctor notu artabilir
  (not elemez, ama sentez girdisi kirlenir).
- Kanıt kapısı içerikte `öneri`yi kabul ediyor (Eray onaylı Grup 2); tarihsiz ajans blogu
  "öneri" sayılırsa zayıf kaynaklı kalıp mutabakatla girer.
- Denetçi sözleşmesi YENİ SÜTUN almadı — çelişki kuralı URL örneklem tablosundan okunuyor.
  Denetçi örneklemi kaynak başına 3 satırla sınırlı: örneklenmeyen iddiada `KAYNAKTA YOK`
  düşürmesi hiç işlemez, beyan olduğu gibi geçer (tasarımın "örnekleme alınmayan iddia
  doğrulanmış SAYILMAZ" cümlesi K-126'ya bağlı; kanıt kapısı beyanı örneklemsiz KABUL eder).

# Notes For Claude

- **2026-09-22 review turu (dual) koştu:** 2 high (H1 etiket/tekrar yüzeyi · H2 eski rapor oy verir),
  3 medium, 4 low; ikisi de orkestratör probuyla doğrulandı. Eray kararı: H1+H2(+M1) fix →
  `/review-claude-codex` kapanış → üç araştırma. Ayrıntı TASK Open Problems ilk madde + rapor.
  Codex ilk çağrıda 480 s'de düştü, 1200 s tekrar 701 s'de bitti — bu aralıkta Codex turu 480 s'ye SIĞMAZ.
- Eray'ın bugünkü talimatı "Grup 3'e başla" idi; seçenek sunulmadı, dosyadakiler yapıldı.
  Kararı sorulacak tek şey: dış depo + monorepo commit onayı (çalışma kuralı) ve Grup 3'ün evi.
- İlke 9: buradaki sayılar bu oturumun koşumlarıdır; sonraki oturum tam takımı yeniden koşar.
- Aile kümesi dokuza çıkarılmadı (K-89); geri bağlantı `url-bicimi` altında ikinci `Check`.
- `_essiz_donem_sayisi` desteksiz dönemi saymaz; aynı ad hem dolu hem desteksiz yazılmışsa dolu
  görünüm sayılır (tekrar ayrı ölçülür).

# Notes For Codex

Codex'i Eray dışarıdan koşturdu (2026-09-21 akşam, kirli ağaç üstünde, bellekte karşı
örneklerle): 5 bulgu → 5 düzeltme (yukarıda). Codex'in kendi doğrulama sınırı: seçili beş test
dosyasında 18 DB kurulum hatası (davranış doğrulanmadı), tam takımı ve mutasyonları yeniden
koşmadı, K-129 rakam kuralını tasarım tercihi sayıp bulgu yapmadı. Kalan dikkat listesi bir
sonraki `/review-claude-codex` için: (1) `_kanit_kapisi` alan sınıfı (`_mevzuat_mi` rakam kolu),
(2) `_kontrol_geri_baglanti` yüzey kümesi ↔ sözleşme, (3) sızıntı regex'inin yanlış-pozitif
yüzeyi (`yer=`/`destek=` düz metin), (4) EK-M satır boyutu (98 iddia × ~40 bayt), (5) Codex
düzeltmelerinin kendisi (bağımsız hakem görmedi).
