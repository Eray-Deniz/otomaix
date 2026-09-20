---
task: sektor-bilgi-paketi-plan2
written: 2026-09-20
---

# Resume From

**SIRADAKİ İŞ, TEK CÜMLE: kusur 4 için Eray'ın spec-sırası kararını al, sonra yeni pilot
koşusunu aç.** Başka ön koşul kalmadı.

**Eray'ın önünde duran TEK karar:** Katman-1'i motordan önce koşturmak için **spec §13.3'ün
bağlayıcı sırasını ikiye ayırmak** — Katman-1 önce, Katman-2 draft'tan sonra. Gerekçe ve ölçüm
`TASK.md` → `# Open Problems` 4. maddede; **kod değişikliği gerekmiyor**, spec §13.3 + plan
Task 19 Step 8/9 birlikte düzenlenecek. **Eray onaylamadan spec'e DOKUNMA.**

**Kusur 1, 2, 3 ve ölü koşu kusuru KAPANDI.** Yeni koşunun üç ön koşulundan ikisi ödendi;
kalan tek ön koşul kusur 4'tür ve o bir spec kararıdır.

**Bu oturumun üç dersi — hepsi ölçümle, üçü de tekrar edecek desen:**
- **Kaydın teşhisine güvenme, mekanizmayı aç.** Kaydın teşhisi bu oturumda ÜÇ kez yanlış çıktı:
  kusur 3 sözleşme değişikliği istemiyordu · kusur 4'ün önerdiği düzeltme spec'le çelişiyor ·
  ölü koşunun "geri açma yolu yok" ayağı kusur değil tasarım (K-82).
- **Kendi düzeltmenin kapsamını ölç ve daralt.** Kusur 3'te iki kez, ölü koşuda iki kez kapsamım
  fazla genişti ve **her seferinde testler/hakemler yakaladı, ben değil.** Refleks: kapı koyduğun
  yerin komşu katmanında ZATEN bir kapı var mı diye bak (`load_verified_run` örneği).
- **Aynı eksen üçüncü kez açılıyorsa varyantı yamamayı bırak.** Bayrak kapısı üç turda üç varyant
  verdi; kapanış ancak üretilmiş matrisle (tam çarpım, çift yönlü, elle yazılmış oracle) geldi.

# Verification

**ALTI commit atıldı, push YAPILMADI.** `1611d1f` (kusur 3) · `9b87c95`+`81d5ed6` (attempt-1
düzeltmeleri + kayıt) · `4b776fa`+`4865a45` (kapanış turu + kayıt) · `c0d073a` (attempt-3 raporu) ·
`2bf3d71` (ölü koşu kapısı). Footer'ların hepsi `rc=0`.

| Ne | Taze çıktı |
|---|---|
| Tam takım (SON, ölü koşu kapısından sonra) | **4640 passed / 0 failed**, 336,03 s |
| Test sayısı | 4618 → 4619 → 4625 → 4635 → **4640** (her adımda aritmetik tuttu) |
| Motor sürümü | 2.17.0 → **2.20.0** (ölü koşu turunda DOKUNULMADI — hat seviyesi kapı) |
| Sözleşme (dış depo) | **2.6, DOKUNULMADI** |
| Review | ÜÇ tur: attempt-1 dual · attempt-2 dual · attempt-3 Codex-only → **approve** |
| Mutasyon | bayrak turunda 7/7 · ölü koşu turunda 4/4 yakalandı |

**Ölü koşu kapısının mutasyonları:** kapı dispatch'ten kaldırıldı → 2 test kırmızı · `sentez`
sınıflandırmadan çıkarıldı → bütünlük testi kırmızı · aşağı akış adımı yanlışlıkla kapıya alındı →
bütünlük testi kırmızı · `mark_incomplete` terminal koruması kaldırıldı → doğru test kırmızı.
(Son mutasyonun ilk denemesi SQL'i bozduğu için kirliydi; temizleyip tekrarladım — mutasyon da
prob gibi kirlenebiliyor.)

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**
- **`yazim` · `katman1/2` · `onay` · `aktive-et` ayakları HÂLÂ hiç koşmadı.**
- **Bayrak kapısının `koru` kolu** aktif paketi OLAN sektörde denenmedi (pilotun aktif paketi yok).
- **Bayrak başına kuralın ANLAM ayağı mekanik DEĞİLDİR**; `bayrak_kaydi` onun yerine geçmez.
- **`bayrak_kaydi` yalnız `ekle` yolunda** ve altı kapıyı geçen kararlar için doğar — tetikleyici
  sınıfın bir ALT KÜMESİNİ kapsar (kodda etiketli).
- **`eski-kaynak` çoğunluk kuralı hiçbir yerde uygulanmıyor** (bu koşudaki parası sıfır ölçüldü).
- **Modelin EK-M'yi doğru kullanacağı ölçülmedi** — evi yeni koşu.
- **`/security-review-claude-codex` bu dalda HİÇ koşmadı** ve kusur 3 review'ında
  `security_surface_touched` **uncertain → true** (fail-closed) işaretlendi, yani ZORUNLU.
- Bu oturumda **DB'ye hiçbir şey yazılmadı**; `record_result` çağrılmadı.

**TUZAK — sonraki oturum bunu bilmeli:** arka planda test koşan bir iş (alt-hakem) varken tam
takımı koşturma. Üç koşum 39-58 hata verdi (`FATAL: database "otomaix_test_scratch" does not
exist`); sebep kod değil, aynı yerel PostgreSQL'in scratch veritabanını iki koşumun birlikte
kurup düşürmesi. Hakem bitince temiz koşum geldi. Çıktı birebir gerilemeye benziyor.

**PROB/MUTASYON KİRLENMESİ bu oturumda DÖRT kez oldu.** (1) yazım kapısı probunun tabanı
şema-geçersizdi → her mutasyon alakasız sebeple reddediliyordu. (2) reddedilen-öğe probu
`final_candidate`e bakıyordu; blocked sonuçta o alan boş → prob kendi hatasını doğruluyordu.
(3) kimlik haritası yol-anahtarlı olduğu için çakışma probu iki satıra aynı kimliği veriyordu.
(4) SQL'i bozan mutasyon davranış yerine sözdizimi ölçtü. **Refleks: probu/mutasyonu yazınca önce
taban varyantının beklenen sonucu birebir ürettiğini doğrula.**

# Risks

- **Yeni koşu pahalı:** `denetim` 956 sn + `sentez` 941 sn + model parası. Körlük tabanı
  (K-134 kalibrasyonu) geri GELMEZ.
- **Kusur 4 çözülmeden yeni koşu açılırsa** aynı `regresyon_kapisi` bulgusu tekrar çıkar ve
  değişiklik varsa aktivasyonu engeller.
- **Daraltma kararının bilinçli maliyeti:** CTA dışı yüzeyde kanal etiketi taşıyan bir kalem
  aktivasyonu DURDURUR. Operatör (= Eray) taslağı `duzeltme-yaz` yolundan düzeltir. Gerçek koşuda
  faturası 1 kalem ölçüldü (`gorsel_kodlar`).
- **Ölü koşu kapısının operatöre yansıması:** bir koşu ölmüşse o koşuda hiçbir adım tekrar
  denenemez — `tur-ac` ile yeni tur açılır (K-82). Bugün de fiilen böyleydi; fark, artık ilk
  adımda NET bir ret alınması.
- **SPK kararı bilinçli risk kabulüdür:** paket doğrulanmamış bir hukuki iddia taşıyacak; gerekçe
  `K134-KOR-YARGI.md`'de.
- **Operatör eklemeleri** (yerel görsel kodlar · Ramazan/Kurban · yılbaşı · 23 Nisan/29 Ekim)
  mekanik kaynak bağı OLMAYAN kalemlerdir.
- **Sentez klasörü doluysa tur koşmaz** (`mkdir` `exist_ok` kullanmıyor); düşen denemeler
  `DUSMUS-…` adıyla duruyor, silme YOK.

# Notes For Claude

- **Eray ham kanıt istiyor, özet değil.** Karar sorusunun ALTINA somut senaryo yaz: ne gelir,
  sistem ne yapar, o ne görür. "Daralt vs bırak" kararı ancak gerçek `render_package_block`
  çıktısı basıldıktan sonra anlaşıldı.
- **"Operatör" = Eray** (spec K-70). "Operatör görür" demek "sen göreceksin" demektir.
- **Açık soru varken aktivasyon YOK** — `onaylanabilir` açık soru listesinin boş olmasını ister.
  "Bilerek kabul edip geç" diye bir yol YOKTUR (bu oturumda yanlış söyledim, koda bakıp düzelttim).
- **Model turundan ÖNCE offline replay yap.**
- **Alt-hakem:** `superpowers:code-reviewer` bu kurulumda YOK → `general-purpose` + aynı persona.
  `model` alanını GEÇME; hook `model='opus'`u reddediyor, config-default miras alınır.
- **Kota okuması bu oturumda hep stale geldi** (primary %5 / secondary %13) ve tazelenmedi —
  sonraki uzun turdan önce yine taze ölçmeyi dene, ama stale okumayı "taze" diye raporlama.
- **CEVAP BEKLEYEN SORU — iki oturumdur yanıt gelmedi.** Araştırma deposunda
  (`otomaix-sosyal-medya-arastirmasi`) **42 dosya silinmiş ama commit edilmemiş** duruyor
  (SWEEP-*, TASLAK-*, `kuyumculuk.md`). Bu oturumda DOKUNULMADI. **Koşul:** yanıt gelmeden
  dokunulmaz; commit atılacaksa yalnız hedef dosya adlandırılarak atılır.

# Notes For Codex

Codex bu oturumda **üç kez** koştu (attempt-1 · attempt-2 · attempt-3 kapanış). Ham çıktılar:
`/root/.claude/logs/otomaix--ffc87809/2026-09-20-review-feat-sektor-bilgi-paketi-plan2-{1,2,3}.md`
(alt-hakem raporu `-1.claude.md`; sentez `docs/reviews/2026-09-20-feat-sektor-bilgi-paketi-plan2.md`).

**En değerli katkısı ölçüldü:** attempt-2'de benim düzeltmemin açtığı FAIL-OPEN'ı buldu
(reddedilen `guncelle` bayraklı aktif değeri geri yüklüyordu). Alt-hakem ise matrisimin kör
noktasını buldu (süzgeç "bayrak" arıyordu, mesaj "bayrağı" yazıyor). **İkisi farklı sınıf
yakalıyor** — tek hakeme düşmek bilinçli bir daraltmadır, eşdeğer değil.

**Zincirin sonraki adımı:** `/security-review-claude-codex` — bu dalda hiç koşmadı,
`security_surface_touched: true` (fail-closed) olduğu için zorunlu. Yeri Task 19 sonrasıdır.
Çalışma ağacı review'dan önce TEMİZ olmalı.
