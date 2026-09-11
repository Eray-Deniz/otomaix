# Review (dual): dış sözleşmenin kod uyarlaması (`080aa7f`) — 2026-09-11

Review aralığı: `b1ef708..080aa7f` (tek commit)
- BASE_REF: `b1ef708` | BASE_SHA: `b1ef708` | HEAD_SHA: `080aa7f` | REVIEW_BASE_SHA (merge-base): `b1ef708`

Reviewers: fresh Claude subagent (general-purpose) + Codex `adversarial-review`
dual-review: **true** (claude_status: ran; codex_status: ran — rc=0, 45 komut koşumu, kararla kapandı)
Review workspace: pinli worktree @ `080aa7f` (temiz)
Main tree at review: clean (0 uncommitted dosya)

**Gereksinim bağlamı — sapma BEYAN EDİLİR.** Tam metin prompt'a GÖMÜLEMEDİ (tek argüman 131.072 bayt
sınırı). İki hakem de AYNI pinli committed dosyaları okudu:
- Dış sözleşme (bu değişikliğin ASIL otoritesi), worktree'ye context-only kopyalandı ve
  `shared/contracts/research-contracts.pin.json` (`12beec1`) ile **sha256 byte-eşit** doğrulandı:
  `_SABLON.md` · `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`
- `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (§9.4 K-126, §11.2 K-03) — committed
- `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md` — committed (diff bunu da değiştiriyor)
- `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — committed (kanonik girdi)

**Güvenlik yüzeyi:** `security_surface_touched: true` (K-126 bir YETKİLENDİRME kapısıdır ve bu turda
KAPALI'dan AÇIK'a geçti) → güvenlik-checklist eki konmadı, `/security-review-claude-codex` zorunlu kalır.

**Kontrolörün kendi ölçümü.** Aşağıdaki her `[both-agree]` bulgu, hakemlerin iddiası olarak DEĞİL,
kontrolörün kendi taze koşumuyla doğrulanmış olarak kaydedilir (İlke: ölçülmemiş mekanizma iddiası
aktarılmaz). Doğrulama komutları bulguların yanındadır.

---

## Critical

### F1 — Tür↔kategori çatışması TÜM KOŞUYU BLOKLUYOR `[both-agree]`

`engine.py::_kategori_cakismasi` `sinif="tur-kategori-catismasi"` taşıyan bir NOT satırı üretiyor;
`identity.py:92` `NOT_SINIFLARI` İKİ değerle kapalı (`reddedilen-aday` · `eslesmeyen-ozel-gun`) ve
`identity.py:528` kapalı küme dışını reddediyor. `decide()` motorun kendi ürettiği günlüğü doğrulamadan
geçirdiği için şema hatası **bloklanmış sonuca** dönüşüyor.

**KONTROLÖR ÖLÇÜMÜ (taze):** girdi `paket_turu='ticari-firsat'`, `kategori='national'` →
`run_checks` notu ÜRETİLİYOR (`tur-kategori-catismasi`), ama `decide()` → `sonuc='blocked'`,
`sebep='uygulanan-cift-butunluk-kapisini-gecmiyor'`.

Bu, K-03'ün kendi hükmünün **tam tersi**: kural "paket türü üstündür, çatışma kayda geçer, blok DEĞİL"
diyor. Kodun docstring'i, arayüz eki R-H8 satırı ve commit mesajının 6. kalemi üçü de "blok değildir"
diyor; **ölçüm üçünü de yalanlıyor.**

**Neden test yakalamadı:** testler yalnız `run_checks()` çağırıyor, son montaj yolunu (`decide()`)
hiç geçmiyor. Emsal AYNI dosyada duruyordu (`test_notes_pass_the_decision_log_schema`,
`eslesmeyen-ozel-gun` notu için tam bu kapıyı koşuyor) ve yeni not sınıfına uygulanmamış.

**Gerçekçi vaka:** kuyumculukta `Sevgililer Günü` (sistem `commercial`) `kutlama` etiketlenirse ya da
`Ramazan Bayramı` (`religious`) `ticari-firsat` etiketlenirse ilk gerçek koşu düşer; operatör
yanıltıcı bir bütünlük-kapısı sebebi görür ve K-28 gereği `blocked` hiçbir uçtan aktive edilemez.

---

## High

### F2 — Çoğunluk SAYISI hâlâ alan düzeyinde toplanıyor `[both-agree]`

İddia bağı "hangi iddia yetkilendiriyor"u bağlıyor; **sayım** ise `cozulen`in TAMAMI üstünden kaynak
birleştiriyor (`engine.py:1085-1090`). `kaynak_iddia` beyanı ile bu toplam arasında hiçbir bağ yok.

**KONTROLÖR ÖLÇÜMÜ (taze):** `kanit="D1#2"` + `kaynak_iddia="K1#2"` (tek kaynaklı iddia) →
`['cogunluk-yok']`. Aynı iddia, atfa AYNI ALANDAN alakasız bir satır eklenerek
(`kanit="D1#2, D1#1"`) → **karar UYGULANDI**.

Yani tek kaynaklı bir iddiadan türetildiği BEYAN EDİLEN kalıp, komşu satırdan iki-kaynaklık çoğunluk
devralıyor ve bu turda açılan K-126 istisnası (resmîlik + canlı URL) **tamamen atlanıyor**.
Kapatıldığı iddia edilen sınıf — *"aynı alandaki herhangi bir denetçi satırı yetkilendirir"* —
sayım ayağında aynen yaşıyor.

### F3 — Görev B dönem bağı MEŞRU araştırma çıktısını reddediyor `[both-agree]`

`engine.py::_iddia_alani_bagli_mi` araştırmanın DÖNEM ADINI `normalize_special_day_key` ile
`oge_yolu` slug'ına eşliyor. İki ad uzayı FARKLI: `_SABLON.md` Bölüm B/C dönem adını brief'in
ADAY TAKVİM yazımıyla ister (günlük dil: `29 Ekim`), `oge_yolu` ise SİSTEM adının slug'ıdır
(`cumhuriyet-bayrami`). Sentez sözleşmesi bu ayrımı kendisi söylüyor.

**KONTROLÖR ÖLÇÜMÜ (taze):** `normalize_special_day_key('29 Ekim')` → `'29-ekim'`;
`'23 Nisan'` → `'23-nisan'`; `'19 Mayıs'` → `'19-mayis'`; `'30 Ağustos'` → `'30-agustos'`;
`'10 Kasım'` → `'10-kasim'`; `'8 Mart Dünya Kadınlar Günü'` → `'8-mart-dunya-kadinlar-gunu'`.
Sistem takvimi (`social.public_holidays`, 22 satır) karşılıklarını `Cumhuriyet Bayramı` ·
`Ulusal Egemenlik ve Çocuk Bayramı` · `Atatürk'ü Anma, Gençlik ve Spor Bayramı` · `Zafer Bayramı` ·
`Dünya Kadınlar Günü` yazıyor. **Alt-hakem ölçümü:** brief'in 15 aday adından yalnız 4'ü sistem
slug'ına düşüyor; karşılığı OLDUĞU HÂLDE düşmeyen 8 dönem var (`Ramazan Bayramı` ve `Kurban Bayramı`
dahil — sistem onları `...-1-gun` diye yazıyor).

**Fixture maskeledi:** pozitif test `Sevgililer Günü` kullanıyor — çakışan dört addan biri. İki adın
AYRIŞTIĞI tek bir test yok. Commit bunu "ölçülmüş incelik" diye anlatıyor; ölçüm tam da ayrışan
tarafı atlamış.

### F4 — K-126'nın ikinci ayağı İDDİA değil KAYNAK düzeyinde ölçülüyor `[both-agree]`

`engine.py::_tek_kaynak_istisnasi` yalnız `kontrol.kaynak == etiket and erisildi and icerik_uyumlu`
arıyor. Sözleşme *"en az bir denetçi O URL'yi canlı açıp"* diyor — o iddianın URL'si. Kod, o kaynağın
örneklemdeki HERHANGİ BİR doğrulanmış URL'sini yeterli sayıyor: üç örneklem satırından biri
`DOĞRULANDI` ise o kaynağın pakete giren HER tekil iddiası istisnadan yararlanıyor.

**Mekanik engel (ölçüldü):** `UrlCheck` iddia numarası TAŞIMIYOR — üstelik sözleşmenin URL tablosu
`iddia | kaynak | sonuç | not` sütunlu olduğu hâlde `auditors.py::_url_orneklemi` `iddia` hücresini
`UrlCheck.url` alanına yazıyor (bu, bu commit'ten ÖNCE de böyle). Bağ bugünkü sözleşmeyle mekanik
olarak kurulamaz. Modül docstring'i "K-126 istisnasının iki ayağı da ölçülür" derken bu daralmayı
BEYAN ETMİYOR.

### F5 — "Çekişmeli yargı istisnayı açmaz" garantisi atlanabilir `[both-agree]` *(severity: medium→high uzlaştırıldı)*

`_tek_kaynak_istisnasi` yargıları iki raporun profil satırlarından topluyor ve "yazan herkes evet
demiş olmalı" diyor; ama **hiçbir katman profilin HER kaynağı kapsadığını ölçmüyor** —
`auditors.py::_kaynak_profili` bunu açıkça kapsam-dışı beyan ediyor (R6) ve motor da ölçmüyor.

**Alt-hakem ölçümü (taze):** D1 kaynak-1 için `resmi=evet`, D2 kaynak-1 için satır HİÇ YAZMAMIŞ →
`_tek_kaynak_istisnasi(..., {"KAYNAK-1"}) is True`. Bir denetçinin şüphesi, **satırı yazmamasıyla**
susturulabiliyor — docstring'in kapattığını söylediği şeyin ta kendisi.

Severity uzlaştırma: alt-hakem `medium`, Codex bunu F4 ile birlikte `high` verdi. En yüksek alınır
(`high`) — fail-open yönü ve K-126'nın bu turda açılmış olması nedeniyle.

---

## Medium

### F6 — Bağlayıcı arayüz eki KENDİ İÇİNDE çelişiyor `[both-agree]`

R-H8 satırı "**R5 ALAN KÜMESİ REVİZYONU**" diyor; ama `EngineInputs` imza bloğunda
`takvim_kategorileri` YOK (dosyada tek geçtiği yer R-H8 satırı) ve `__post_init__` dondurma listesi
de alanı saymıyor — oysa kod onu donduruyor. Üstelik aynı belge düz bir cümleyle
*"R5 alan kümesi (`EngineInputs`) DEĞİŞMEDİ — ve bu ölçüldü"* diyor. **İki ifade aynı commit içinde
çelişiyor**; hangisinin bağlayıcı olduğu okunamıyor.

### F7 — `karma` muafiyeti kuralın fiat'la daraltılması `[both-agree]`

`karma` "kutlama + ÖLÇÜLÜ TİCARİ" demek, yani `national`/`religious` bir günde ticari bileşen TAŞIR —
tam da K-03'ün kendi örneğiyle (national ↔ ticari) aynı eksende. Muafiyet docstring'de
gerekçelendirilmiş ama **ne spec'te ne spec-input'ta yazılı**. Commit "TAM eşleme UYDURULMADI"
ilkesini savunurken burada bir muafiyet uydurmuş oluyor. Yön: **daraltma** (çatışma daha az bildirilir).

---

## Low

### F8 — `_c_no_dizisi_ihlalleri` aynı arızayı İKİ kez bildiriyor `[single-source: claude]`

Fonksiyon "aynı arıza iki kez sayılmaz" diyor; ama biçimi bozuk hücre `numaralar`dan düştüğü için N
küçülüyor ve boşluk kuralı sahte bir "eksik" üretiyor. **Ölçüldü:** `no` hücreleri `1,2,3a,4` →
`"eksik numara: [3]"`. 3 eksik değil, BOZUK. İkisi de `SEVIYE_NOT`, elemeyi etkilemiyor — raporu
kirletiyor.

### F9 — Mührün gerekçesi olduğundan güçlü yazılmış `[single-source: claude]`

`kaynak_seti_sha` docstring'i "iddia kümesi değişmiş bir rapor mühürden SESSİZCE geçerdi" diyor;
oysa `iddialar` `run`'da kaynak METNİNDEN saf olarak türer ve metnin kimliği `icerik_ozeti` (aynı
mühürde) ile zaten kapalı. **Davranışsal kusur YOK** — iki hakem de eksen 5'i temiz buldu ve mührün
iki tarafının aynı değeri ürettiğini ayrı ayrı doğruladı; yalnız gerekçe abartılı.

### F10 — `_iddia_alani_bagli_mi` iki ayakta iki normalizasyon kuralı `[single-source: claude]`

İlk ayakta `karar_alani` `alan_karsilastirma_anahtari`'den geçiyor, ikinci ayakta
`karar_alani != "ozel_gun"` diye HAM karşılaştırılıyor. Aynı girdi iki kuralla okunuyor; "tek kural"
iddiasıyla çelişiyor.

---

## Disposition Ledger (her ham bulgu — sessiz drop YOK)

| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| C1 | claude | critical | critical | kept (F1) | kontrolör taze koşumla doğruladı |
| X4 | codex | high | critical | merged-into F1 | aynı kök neden; en yüksek severity alındı |
| C2 | claude | high | high | kept (F2) | kontrolör probu doğruladı |
| X1 | codex | high | high | merged-into F2 | aynı kök neden |
| C3 | claude | high | high | kept (F3) | kontrolör normalizasyon ölçümüyle doğruladı |
| X3 | codex | high | high | merged-into F3 | aynı kök neden |
| C4 | claude | high | high | kept (F4) | kontrolör `_url_orneklemi` alan eşlemesini okudu |
| X2 | codex | high | high | merged-into F4 + F5 | Codex iki ayağı tek bulguda topladı; sentezde AYRILDI (ayrı kök nedenler, ayrı fix) |
| C5 | claude | medium | high | kept (F5) | severity YÜKSELTİLDİ (indirme değil → gate gerekmez) |
| C6 | claude | medium | medium | kept (F6) | kontrolör grep ile doğruladı |
| X6 | codex | medium | medium | merged-into F6 | aynı kök neden |
| C7 | claude | medium | medium | kept (F7) | — |
| X5 | codex | medium | medium | merged-into F7 | aynı kök neden |
| C8 | claude | low | low | kept (F8) | — |
| C9 | claude | low | low | kept (F9) | davranışsal kusur yok; belge düzeltmesi |
| C10 | claude | low | low | kept (F10) | — |

**Severity indirme (`severity_downgrade`) YAPILMADI** — hiçbir raw critical/high medium/low'a
indirilmedi. Tek severity hareketi C5'in medium→high YÜKSELTİLMESİ (gate gerektirmez).

## Hakemler-arası çelişki

**Yok.** Yedi eksende iki hakem bağımsız olarak aynı kusurları buldu. Üç low yalnız alt-hakemden
geldi (`single-source: claude`) ve üçü de belge/rapor-kalitesi düzeyinde — Codex onları bulgu
saymadı, çürütmedi.

**Ortak-mod kontrolü:** hiçbir bulgu kontrolörün hakem bağlamına yazdığı bir rol-iddiasına iz
sürmüyor; beş dikkat ekseni NÖTR betimlendi ("şunu sorgula"), rol atfedilmedi. `[both-agree]`
sinyali bu turda GEÇERLİ.

## Temiz bulunan alanlar (iki hakem de)

- **Denetçi katmanı** (`auditors.py`): `kaynak_iddialari_coz` tek ayrıştırıcı ve biçim kapalı;
  `kaynak-iddialari ↔ kaynaklar` eşitliği gerçekten ÇİFT YÖNLÜ (eksik ve fazla kolları ayrı test
  edilmiş); `KaynakProfili` satır-içi tutarlılığı eksiksiz; başlıklar pinli sözleşmeden OKUNUYOR.
- **Mühür (eksen 5)**: iki taraf aynı değeri üretiyor, kalıcılaştırılmış eski mühürle karşılaştırma
  yok → **kırılan meşru koşum yok**. (Yalnız F9 gerekçe abartısı.)
- **`brief_doctor` Bölüm C testleri**: matris kavramdan türetilmiş, indeksler addan türüyor, her kapı
  ayrı söküldüğünde komşusu ayakta kalıyor. Alt-hakem "bu turda gördüğüm en sağlam test bloğu" dedi.
- **Performans**: bariz regresyon yok; yeni işler tur başına sabit-küçük tablolar üstünde.
- **İlke 9 uyumu**: `TICARI_SISTEM_KATEGORISI` docstring'indeki sayım (`religious` 9 · `national` 8 ·
  `commercial` 5) alt-hakem tarafından yerel DB'de TAZE koşumla doğrulandı — birebir tutuyor.
- **Sözleşme pini**: `contract-snapshot/` üç dosyası pin ile sha256 byte-eşit.

## Sonuç

- Kapatılan (push-back): 0 (push-back turu henüz koşulmadı)
- Açık: **10** — 1 critical, 4 high, 2 medium, 3 low
- Hakemler-arası çelişki: yok
- **fix-required (C/H): F1 · F2 · F3 · F4 · F5**
- **medium/low:** politika gereği `accepted_risk` OLURDU — **ama F6·F7·F8·F9·F10'un hepsi bu
  commit'in KENDİ ürünüdür.** "Gerileme kontrolörün kendi ürünüyse düzeltilir" istisnası uygulanır;
  hiçbiri `accepted_risk` yazılmaz.

**Chain-advance: HARD-BLOCK.** Unresolved critical/high var → `/security-review-claude-codex`'a
geçilmez. Önce düzeltme + re-review.

**F3 ve F4 kod-içi tam kapanmaz** — ikisi de DIŞ SÖZLEŞME düzeyinde eksik kimlik taşıyor
(dönem için kanonik sistem anahtarı; URL örneklemi için iddia numarası). Kapanışları sözleşme
revizyonu + pin yenilemesi ister. Bu, kullanıcı kararıdır.

## Ham kanıt — işaretçiler (bu makinede, bu kökten)

- Codex ham çıktısı:
  `/root/.claude/logs/otomaix--ffc87809/2026-09-11-review-feat-sektor-bilgi-paketi-plan2-1.md`
- Claude alt-hakem ham çıktısı:
  `/root/.claude/logs/otomaix--ffc87809/2026-09-11-review-feat-sektor-bilgi-paketi-plan2-1.claude.md`

**Dürüst etiket:** işaretçiler MUTLAK yoldur; ham kanıt proje klonuyla TAŞINMAZ (K4 kabul edilen risk).

## Ölçülmeyen / kapsanmayan

- **Komple takım (4323 test) bu review'da KOŞULMADI.** Alt-hakem yalnız diff'in dokunduğu yedi modülü
  koştu (`2076 passed, 140 errors`); 140 hatanın hepsi worktree'de `.env` olmamasından
  (`DATABASE_URL boş`) — ortam kısıtı, kod kusuru değil. Commit'in `4323 passed / 317 s` iddiası bu
  turda DOĞRULANMADI (kontrolörün ana ağaçtaki kendi koşumundan gelir).
- Uçtan uca CLI koşumu yapılmadı.
- Aşağı akış tüketicilerinin (`readiness` · `approval` · `runs`) `kategori_cakismalari` ölçümünü nasıl
  gösterdiğine bakılmadı — F1 koşuyu o noktaya ulaşmadan kesiyor.
- `ruff`/`pyright` bu ortamda YOK, koşulmadı.
- Tam gereksinim metni prompt'a gömülemedi (argüman boyut sınırı); iki hakem de aynı pinli committed
  dosyaları okudu — sapma yukarıda beyan edildi.
