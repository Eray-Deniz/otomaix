---
task: sektor-bilgi-paketi-plan2
written: 2026-09-20
---

# Resume From

**Kusur 3 kapandı; İKİ review turu (attempt-1 + kapanış) koştu. AÇIK BİR CHECKPOINT VAR (aşağıda).
SIRADAKİ İŞ: kusur 4 (sıra kusuru) + ölü koşu kusuru — ikisi de yeni pilot koşusunun ÖNÜNDE.**

**CHECKPOINT KAPANDI.** Kapanış turu, H2 düzeltmemin FAIL-OPEN açtığını buldu (reddedilen
`guncelle` bayraklı aktif değeri geri yüklüyor ve paket aktive olabiliyordu). Sınıfı kapattım,
üretilmiş matrisle kanıtladım; sonra Eray kararıyla **üçüncü tur (yalnız Codex)** koştu ve
**approve / materyal bulgu YOK** geldi. **Dürüst sınır:** teyit tek hakemden
(`dual-review: false`). ÜÇ review turu koştu, unresolved critical/high YOK.

**Eray kararı (2026-09-19, hâlâ geçerli): tören YOK.** Spec seansı açılmaz, plan yazılmaz;
düzeltme doğrudan başlar. Review gerekirse düzeltme SIRASINDA çağrılır — kusur 3'te böyle
yapıldı ve karşılığını verdi (iki high, dört medium, dört low; hepsi o turda düzeltildi).

Okunacak yer: **`TASK.md` → `# Open Problems`**. Sıradaki iki kalem: 4. madde (sıra kusuru) ve
onun altındaki ölü-koşu kalemi. Ölçüm dosyası `K134-MOTOR-KARSILASTIRMA.md` artık İKİ ölçümü ve
uzlaştırmasını taşıyor — sayı karşılaştırırken **motor sürümünü birlikte oku** (2.15.0 fotoğrafı
ile 2.17.0 ölçümü farklı sayı verir, ikisi de doğrudur).

**Kusur 3'ten çıkan üç ders (hepsi bu oturumda ölçümle):**
- **Kaydın teşhisine güvenme, mekanizmayı aç.** Kayıt "sözleşme değişikliği gerekir + yapısal
  alan aç" diyordu. Ölçüm ikisini de çürüttü: iki kapı da sözleşmenin yasaklamadığı yüzeyleri
  tarıyordu, yasaklanan yüzeyi (paket metni) hiçbiri taramıyordu.
- **Devralan katmanın kapsamını ÖLÇ.** "Bunu yazım kapısı yapar" demek üzereydim; 60 hücreye tek
  tek bayrak koyunca 43'ünü geçirdiği çıktı. Devir sahte olurdu.
- **Kendi düzeltmenin yan etkisini ölç — hakem benden önce buldu.** Yüzeyi taşımak yeni bir sınıf
  açtı (ölü satırın yolu, sıra kayması yüzünden yaşayan yolla çakışıyor) ve bunu ben değil
  bağımsız hakem yakaladı. Ders: kolun testini yazmadığım yerde kusur çıktı.

# Verification

**Bu oturumda ÜRETİM KODU DEĞİŞTİ.** BEŞ commit atıldı: `1611d1f` (kusur 3) · `9b87c95` +
`81d5ed6` (attempt-1 düzeltmeleri + kayıt) · `4b776fa` + `4865a45` (kapanış turu düzeltmeleri +
kayıt). **Push YAPILMADI.** Attempt-3 raporu bu dosyadan sonra commit edilir.

| Ne | Taze çıktı |
|---|---|
| Tam takım (kusur 3 ilk hâli) | 4619 passed / 0 failed, 335,51 s |
| Tam takım (review düzeltmelerinden SONRA) | 4625 passed / 0 failed, 337,31 s |
| Tam takım (kapanış turu düzeltmelerinden SONRA, SON) | **4635 passed / 0 failed**, 334,21 s |
| Test sayısı | 4618 → 4619 → 4625 → **4635** (+1, +6, +10; aritmetik tutuyor) |
| Motor sürümü | 2.17.0 → 2.18.0 → 2.19.0 → **2.20.0** |
| Sözleşme | **2.6, DOKUNULMADI** — kusur 3 sözleşme değişikliği gerektirmedi |
| Review turu | ÜÇ tur: attempt-1 dual · attempt-2 dual · attempt-3 Codex-only; beş hakem koşumu |
| Kapanış | attempt-3 **approve, materyal bulgu yok** (tek hakem → `dual-review: false`) |
| Kapanış kanıtı | ÜRETİLMİŞ matris (8 vaka, çift yönlü, 2 mutasyon) + bağımsız hakem teyidi |

**Alt-hakem tam takımı bağımsız koşturdu:** 4619 passed / 332,44 s (düzeltmelerden önceki hâl) —
benim o anki sayımı doğruladı.

**Mutasyonla ölçülen kapılar — YEDİ mutasyon, yedisi de yakalandı; hepsi yedekten geri alındı ve
`cmp` ile bayt-eşit doğrulandı:**
- Ölü satır süzgeci kaldırıldı → çakışma testi kırmızı.
- Kanal muafiyeti yine koşulsuz yapıldı → CTA-dışı testi kırmızı.
- Tipli bayrak kaydı kaldırıldı → iki test kırmızı.
- `decide` sınıf düşürmesi kaldırıldı → reddedilen-ekleme testi kırmızı.
- Yargı yine ret kümesine bağlandı (FAIL-OPEN geri) → matrisin tam o vakası kırmızı.
- Düşürme tümden kaldırıldı (her bayrak bloklar) → matrisin TERS yöndeki vakası kırmızı.
- `channel_flag_scope_path`'in `/cta` kolu silindi → özel gün CTA testi kırmızı.
  **Dürüst etiket:** bu son mutasyon ilk denemede SAĞ KALDI, çünkü testimin süzgeci
  `"bayrak" in detay` idi ve kanal mesajı "bayrağı" yazıyor (ğ≠k) — süzgeç onu hiç görmüyordu.
  Yapısal ölçüte (`b.kontrol == "bayrak_tuketimi"`) çevrildikten SONRA yakalandı.

**Gerçek koşuda (`kosu-222706dc…`) ölçülen davranış, yeni motorla:** bayrak kaynaklı açık soru
**8 → 1**. Kalan 1, daraltma kararının ÖNGÖRÜLEN faturası: `gorsel_kodlar` kaleminin
`[kanal-bağımlı: fiziksel_magaza]` etiketi, filtrenin koşmadığı bir yüzeyde. Ayrıca 3
`bayrak_kaydi` (bloklamıyor) ve 1 `regresyon_kapisi` (kusur 4). Koşu hâlâ `blocked` — ama
**kusur 3 yüzünden değil**: tükenmiş koşunun EK-M öncesi atıf numaraları (14 uygulanmayan
karar), sentezin kendi açık soruları ve kusur 4'ün regresyon kapısı yüzünden.

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**
- **Yeni kapının `koru` kolu hiç koşmadı** — pilot sektörün aktif paketi yok. Aktif pakette duran
  eski bir bayrak bundan sonra açık soru üretir; bu dal ölçülmedi (TASK'ta evi var).
- **Bayrak başına kuralın ANLAM ayağı mekanik DEĞİLDİR** (ör. "kopya şüphesi soyutlanarak
  giderildi mi"). `bayrak_kaydi` onun yerine geçmez, operatör denetimine dayanaktır.
- **`eski-kaynak` çoğunluk kuralı hiçbir yerde uygulanmıyor** — bu koşudaki parası sıfır ölçüldü,
  koşullu düşürüldü.
- **Modelin EK-M'yi doğru kullanacağı hâlâ ÖLÇÜLMEDİ** (kusur 1'in davranış ayağı; evi yeni koşu).
- **`yazim` · `katman1/2` · `onay` · `aktive-et` ayakları HÂLÂ hiç koşmadı.**
- Bu oturumda **DB'ye hiçbir şey yazılmadı**; koşu satırlarına dokunulmadı, `record_result`
  çağrılmadı.

**TAM TAKIM SAPMASI ÖLÇÜLDÜ — sonraki oturum için tuzak.** Düzeltme turu sırasında üç ayrı tam
koşum 39-58 hata verdi (`FATAL: database "otomaix_test_scratch" does not exist`). Sebep kod DEĞİL:
alt-hakem aynı yerel PostgreSQL'in scratch veritabanını kurup düşürüyordu. Hakem bitince temiz
koşum geldi (4635/0). **Arka planda test koşan bir iş varken tam takımı koşturma** — çıktı birebir
gerilemeye benziyor.

**PROB ÜÇ KEZ KİRLENDİ, üçü de düzeltildi.** (1) Yazım kapısı kapsamını ölçen ilk prob taban
içeriği şema-geçersiz kurmuştu → her mutasyon alakasız sebeple reddediliyordu; taban gerçek
adaya taşındı. (2) Reddedilen-öğe probu `final_candidate`e bakıyordu; blocked sonuçta o alan boş
→ iki kol da "YOK" diyerek kendi hatasını doğruluyordu; ölçüm `_nihai_icerik`e taşındı.
(3) Önceki oturumdan devreden ders: prob motorun yüklemini kopyalamaz, ÇAĞIRIR.
Sonraki oturum: **probu yazınca önce taban varyantının canlı sonucu birebir ürettiğini doğrula.**

# Risks

- **Kusur 4 ve ölü koşu kusuru kapanmadan yeni koşu açılmamalı.** Kusur 4 düzeltilmezse aynı
  `regresyon_kapisi` bulgusu yeni koşuda TEKRAR çıkar (bu oturumda gerçek koşuda görüldü). Ölü
  koşu kusuru düşen bir adımın koşuyu sessizce öldürmesine ve sonraki adımların habersiz
  çalışmasına izin veriyor — ~1900 saniyelik iki model turu yanabilir.
- **Yeni koşu pahalı ve körlük tabanını geri getirmez:** `denetim` 956 sn + `sentez` 941 sn + para.
- **Daraltma kararının bilinçli maliyeti:** CTA dışı yüzeyde kanal etiketi taşıyan bir kalem
  aktivasyonu DURDURUR (`onaylanabilir` açık soru varken False). Operatör (= Eray) taslağı
  `duzeltme-yaz` yolundan düzeltmeli. Gerçek koşuda faturası 1 kalem ölçüldü.
- **SPK kararı bilinçli risk kabulüdür** (önceki oturumlardan): paket doğrulanmamış bir hukuki
  iddia taşıyacak; gerekçe `K134-KOR-YARGI.md`'de.
- **Operatör eklemeleri** (yerel görsel kodlar · Ramazan/Kurban · yılbaşı · 23 Nisan/29 Ekim)
  mekanik kaynak bağı OLMAYAN kalemlerdir; paketin "her kalem bir kaynağa bağlıdır" garantisini
  zayıflatırlar.
- **Sentez klasörü doluysa tur koşmaz** (`mkdir` `exist_ok` kullanmıyor). Düşen denemeler
  `DUSMUS-<tarih>-<sebep>-<koşu>` adıyla duruyor; silme YOK.

# Notes For Claude

- **Eray ham kanıt istiyor, özet değil** (hâlâ geçerli). Karar sorusunun ALTINA somut senaryo
  yaz: ne gelir, sistem ne yapar, o ne görür. Bu oturumda "daralt vs bırak" kararı ancak gerçek
  `render_package_block` çıktısı basıldıktan sonra anlaşıldı.
- **"Operatör" = Eray** (spec K-70: *"işaretleme sorumlusu operatördür — solo işletimde Eray"*).
  Ona "operatör görür" demek "sen göreceksin" demektir; rolü adıyla anlat.
- **Açık soru varken aktivasyon YOK** — `onaylanabilir` koşulu açık soru listesinin boş olmasını
  ister. "Operatör bilerek kabul edip geçer" diye bir yol YOKTUR (bu oturumda yanlış söyledim,
  koda bakıp düzelttim).
- **Model turundan ÖNCE offline replay yap** (hâlâ geçerli).
- **CEVAP BEKLEYEN SORU — Eray'a soruldu, yanıt gelmedi.** Araştırma deposunda
  (`otomaix-sosyal-medya-arastirmasi`) **42 dosya silinmiş ama commit edilmemiş** duruyor
  (SWEEP-*, TASLAK-*, `kuyumculuk.md`). Bu oturumda DOKUNULMADI ve o depoya commit atılmadı
  (kusur 3 sözleşme değişikliği gerektirmedi). **Koşul:** yanıt gelmeden bu dosyalara
  dokunulmaz; o depoda commit atılacaksa yalnız hedef dosya adlandırılarak atılır.
- **Alt-hakem `superpowers:code-reviewer` olarak çözülemedi** (bu kurulumun agent listesinde yok)
  → `general-purpose` + aynı persona kullanıldı. Ayrıca `model` alanını GEÇME: hook
  `model='opus'`u reddediyor, config-default miras alınır.

# Notes For Codex

Codex bu oturumda **bir kez** koştu (`adversarial-review`, review turu). Ham çıktı:
`/root/.claude/logs/otomaix--ffc87809/2026-09-20-review-feat-sektor-bilgi-paketi-plan2-1.md`.
Kota o çağrıda primary %5 / secondary %13 okudu ama okuma **stale**'di; sonraki uzun turdan önce
kotayı TAZE ölç.

**`/security-review-claude-codex` bu dalda HÂLÂ koşmadı.** Kusur 3 review'ında
`security_surface_touched` **uncertain → true** (fail-closed) işaretlendi: değişiklik paketin
aktivasyon kapısının anlamına dokunuyor. Yani güvenlik-checklist eki konmadı ve güvenlik turu
zorunlu kalıyor. Zincirin yeri Task 19 sonrasıdır.

**Kusur 3'ün düzeltme turu için kapanış-doğrulama (attempt-2) review'ı HENÜZ KOŞMADI** —
çalışma ağacı temizlendikten (commit) sonra koşulmalı; aynı pinli sözleşmeyle, bounded impact
envelope üzerinde.
