---
task: sektor-bilgi-paketi-plan2
written: 2026-08-31
---

> ⚠️ YÜRÜTME AÇIK — bu anlatı **checkpoint 2'nin düzeltme turu 2 indikten sonra, o turun
> yeniden inceleme turundan ÖNCE** yazıldı. Güncel durum TASK.md + yürütme defteri + git
> defterinden okunur; çelişkide onlar esastır.

# Resume From

**Task 4 İNDİ. Checkpoint 2'nin yeniden inceleme turu KOŞTU (3 bulgu onaylandı) ve
düzeltme turu 2 İNDİ. Checkpoint 2 HÂLÂ AÇIK — düzeltme turu 2 bağımsız yargı görmedi.**

Sıra: düzeltme turu 2'nin kapanış-doğrulama turu → (temiz çıkarsa) Task 5.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** seçilir.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Her görevin commit aralığı, her hakem bulgusu, her kontrolör kararı ve gerekçesi orada.
Bağlam kaybolursa **defter + `git log`** esastır, anlatı değil.

**Yürütme durumu (TASK.md "Execution State"):** kip alt-ajanlı · başlangıç çapası `a806e29` ·
defter penceresi `a806e29` · `cp_count: 1` · `last_checkpoint_ref: 72f5744`.
**`cp_count` ve `last_checkpoint_ref` checkpoint 2 KAPANDIĞINDA ilerler** — henüz ilerlemedi,
çünkü tur bitmedi. Bu ikisi yalnız mutasyon protokolüyle değişir.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Push EDİLMEDİ** — uzak dal hâlâ `a806e29`'da.
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: `master`, HEAD
**`6d5d90db9537b516413d31f091b4d475526bcb73`** (Task 4'ün sözleşme v2'si), temiz, uzak deposu
yok. Pin manifesti bu commit'e ve iki dosyanın yeni sha256'sına bakıyor.

**Yedek etiket `backup/pre-footer-fix-20260830`** commit etiketi yeniden yazımının geri dönüş
yoludur. Silinme koşulu TASK.md'de yazılı (dal merge edilince VEYA final inceleme temiz geçince).

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar:**
1. Arayüz eki **bağlayıcıdır**. Uygulayıcı brief'e, ekin ilgili hükümleri **harfiyen
   kopyalanmış** olarak gider — plan metni tek başına yetmez, "eki oku" demek de yetmez.
2. Test komutu **sanal ortam aktifleştirilerek** koşar (aşağıda Verification).
3. **Taban 914**; bu sayı düşmeyecek. (745'ti; düzeltme turu 1'de 13, düzeltme turu 2'de
   156 test eklendi.)
4. **`Exec-Kind` sınıflandırıcıya karşı seçilir, uzantıya karşı DEĞİL.** Beyaz liste altı
   değerli: `code` · `red-only` · `green-only` · `docs-only` · `migration` · `merge`.
   `shared/contracts/*.json` çalıştırılabilir sayılır.
5. **`Exec-*` bloğu mesajın SON PARAGRAFI olmalı**, ve `Co-Authored-By` / `Claude-Session`
   satırları **aynı paragrafın içinde** durmalı — araya boş satır girerse defter kapısı
   `rc=4` verir.
6. **Her commit'ten SONRA defter kapısı koşulur** — finalde değil.
7. Test önce yazılır, **kırmızı düştüğü gözle görülür**, kırmızı çıktı rapora yazılır.
8. Uygulayıcı **kendi alt-ajanını çağırmaz**; review kontrolörden gelir.
9. **Codex çağrılarına tam 40 karakterlik SHA verilir.** Kısa SHA substrat kurulumunda `rc=2`
   üretir — Codex hiç çağrılmaz, tur boşa gider.
10. **Dış depo değişikliği hakeme prompt'a GÖMÜLEREK gider.** Codex sandbox'ı
    `/root/otomaix-sosyal-medya-arastirmasi`'ya erişemez; sözleşme dosyalarına dokunan her
    turda diff prompt'un sonuna veri olarak eklenir ve kapsam beyanında adı geçer.

**Devir pointer'ları — hangi görev neyi devralıyor:** TASK.md'nin "Task 3'ün doğurduğu evler"
bölümü. Task 6 · Task 9 · Task 11 · Task 12 · Task 13 · Task 15 · Task 18 dispatch'lerinde
ilgili maddeler taşınır.
**Task 9 ayrıca ekin M1 hükmünü devralır:** beş çıktı bölümü anahtarı pinlenmiş denetçi
sözleşmesinden **ÖLÇÜLEREK** doldurulur, uydurulmaz; iki kapı testi Task 9'un malıdır.
**Task 5 · Task 19 Eray kararı bekliyor** (takvim satırlarının yılı/kategorisi/kanonik adı;
dört operatör kararı) — Task 5 dispatch'inden ÖNCE sorulur.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-08-31, hepsi kontrolörün kendi koşumları —
hiçbiri uygulayıcının ya da hakemin sözüne dayanmıyor):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **914 passed in 109.92s**. Oturum seyri: 745 (giriş) → 745 (Task 4) → 758 (düzeltme 1)
  → 914 (düzeltme 2).
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**. `T4` satırı
  `green-only` (yalnız pin manifesti), `T4-fix1` satırı `code` (hem test hem uygulama).
- **Pin doğruluğu ölçüldü:** manifest üç dosyanın disk `sha256sum` çıktısıyla birebir; dış
  depo HEAD == pinlenen commit.
- **Modül çıkarımının SADAKATİ ölçüldü, iddia edilmedi:** kaynak modülden kaybolan 27 üst
  düzey adın **27'si** yaprakta bayt-aynı; kaynakta kalan 35 adın **hiçbiri** değişmemiş
  (AST + kaynak-parça karşılaştırması). Kaybolan 8 ad özel; depo taraması hiçbirinin eski
  modül üzerinden anılmadığını gösterdi.
- **Hash kayması YENİDEN ölçüldü (düzeltme turu 2):** 19 farklı eski-biçim girdi (düz sözlük ·
  dize · NFC dize · liste · tamsayı · büyük tamsayı `10**309`/`10**400`/`-10**309`/`2**1024` ·
  float · bool · `None` · iç içe yapı · boş kapsayıcılar) → **0 digest kayması**. İstisna TİPİ
  sözleşmesi ayrıca üretilmiş listeden sınandı: 9 ret sınıfı × 4 kapsayıcı = 36 yol, **36'sı da
  `TypeError`**, 0 ihlal.
  **Düzeltme turu 1'in "10 girdi → 0 kayma" ölçümü YETERSİZDİ:** örneklem hiç büyük tamsayı
  taşımıyordu ve tam da o sınıf kaymıştı (`10**309` `OverflowError` veriyordu).
- **Yapısal kapının AYIRT EDİCİLİĞİ ÜRETİLMİŞ MATRİSLE ölçüldü (düzeltme turu 2):** import
  sözdiziminin 44 hücrelik çarpımı (mutlak + göreceli seviye 1/2/3 × düz `import` /
  `from … import` / çok adlı × takma adlı-adsız × modül üstü-fonksiyon gövdesi) BELLEK İÇİ
  kaynak metnine enjekte edildi; hücrelerin **44'ü de** yasaklı kenarı görüyor. Çözülemeyen
  göreceli seviye (4 · 5) fail-closed düşüyor.
  **Düzeltme turu 1'in ayırt edicilik ölçümü YETERSİZDİ:** ELLE SEÇİLMİŞ TEK bir mutlak
  import'a bakıyordu ve yanlış güven veriyordu — göreceli (`from .. import sector_packages`)
  ve dolaylı (`from app.services import sector_pipeline`) biçimler kapıdan sessizce geçiyordu
  (ölçüldü: **3 passed**). Yeni çözümleyicide beş mutasyonun **beşi de** kapıyı düşürüyor,
  mutasyonsuz kod ise hâlâ ONAYLANIYOR. Enjeksiyon bellek içidir — gerçek dosyaya
  DOKUNULMADI, `git status` temiz.
- **Beş çıktı bölümü ölçüldü:** `grep -cE '^[0-9]\) ' hakem-denetci-gorevi.md` → **5**.
- **Kapalı bayrak kümesi ölçüldü:** 8 üye; `muhtemel-uydurma` içinde YOK.
- **Ölü SHA taraması:** squash edilen commit ve amend öncesi dış SHA hiçbir yerde anılmıyor.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Düzeltme turu 2 bağımsız yargı GÖRMEDİ.** Checkpoint 2'nin yeniden inceleme turu koştu
  (düzeltme turu 1'i yargıladı, 3 bulgu onaylandı); düzeltme turu 2 o bulguları kapatıyor ama
  kendisi henüz incelenmedi. Tur AÇIK.
- **Sözleşme metninin bir hakem oturumu tarafından fiilen beş bölümlü ve tamlık kurallı çıktı
  ürettireceği doğrulanmadı** — bu ancak gerçek bir denetçi koşumuyla ölçülür.
- **Task 8'in ileride yazılacak modülünün temiz import edeceği doğrulanmadı**; yalnız kanonik
  hash'in ekin bağladığı BİÇİMİ kabul ettiği ölçüldü. Modül henüz yok.
- **Task 5–20 hiç yazılmadı.**
- **Sözleşme metinlerinin ÇALIŞMA ZAMANI tüketimi hiç ölçülmedi.** Metin varlığı ölçüldü,
  davranış değil; ilk kuru koşumda (Task 11/19) görülür.
- `git` ikilisi olmayan ortamda ve git ortam değişkenleri ezildiğinde pin davranışı
  ölçülmedi — evi Task 18 Step 8b.
- Canlıya hiçbir şey dağıtılmadı, hiçbir migration uygulanmadı, pilot koşulmadı.
- **Dal push EDİLMEDİ.**

# Risks

- **KAPANMAMIŞ AYAK (düzeltme turu 1, dürüst etiket):** ekin bağımlılık hükmünün "kullanılan
  TEK ad" ayağı kapanmadı — yaşam döngüsü kimlik modülünden iki adı daha kullanıyor. İmport
  biçimi hükme çevrildi, ad kümesi AÇIK. **Kapanması ek belgesinin revizyonunu ister ve o
  tasarım katmanının işidir** — yürütücü ek metnini yeniden yazmaz. "Ele alındı" DEĞİL.
- **KABUL EDİLMİŞ RİSK (checkpoint 2, low):** `a34d3f6`'nın `green-only` etiketi tarihsel
  olarak yanlış — o commit sıra değişikliğini testsiz indirdi, ayırt edici test bir sonraki
  commit'te (`ad95846`) geldi. HEAD kapsanıyor, ama bu aralık için "her commit'te TDD"
  iddiası yapılamaz. **Düzeltilmiyor:** geçmiş değişmez ve ikinci bir commit yeniden yazımı
  (ilki altı commit'e mal olmuştu) düzelttiğinden büyük bedel çıkarır.
- **Aynı sınıf Task 3'te üç tur üst üste tekrarladı:** düzeltme metninin KENDİ içinde
  ölçülmemiş atıf. Task 4'ün uygulayıcısı bu turda kendi atıflarını denetledi ve iki tanesini
  ilk yazımda yanlış bulup düzeltti — sınıf hâlâ canlı, her turda atıf matrisi koşulmalı.
- **Kontrolör de ölçmeden kabul edebiliyor.** Bu oturumda hakemin beş bulgusunun her biri
  ayrı ayrı ölçüldü; biri (bağımlılık sınırı) hakemin verdiğinden **yüksek** çıktı, biri
  (aktör kaybı) ölçülen erişilemezlik yüzünden "şimdi düzelt"ten çıkarıldı. İkisi de
  ölçümle, hakemin sözüyle değil.
- **KABUL EDİLMİŞ RİSK (arayüz eki, tur 3 sonrası):** "annotation çalışma zamanı zorlaması
  değildir" sınıfının kalıntısı ve kimlik karşılaştırmalarındaki hoşgörülü normalleştirme.
- **KABUL EDİLMİŞ RİSK (checkpoint 1):** `test_external_repo_gitignores_run_folder` git ortam
  değişkenleriyle sahte bir depoya yönlendirilebilir. Üretim pin yolu etkilenmiyor.
  Evi Task 18 Step 8b.
- **KABUL EDİLMİŞ RİSK:** dış deponun içinde dışarıyı gösteren sembolik bağ ele alınmıyor;
  kapatmak ekin R14 hükmünün yasakladığı beşinci kapıyı gerektirir. **"Ele alındı" DEĞİL.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`). Arayüz eki 8 çelişki
  + 12 boşluğu kapattı ama **Plan 1 alanındaki kart geçişi hâlâ taranmadı**.
- **Codex maliyeti:** bu oturumda checkpoint 2 için **2** Codex çağrısı yapıldı (ilk tur +
  yeniden inceleme turu); düzeltme turu 2'nin yeniden incelemesi üçüncüsü olacak. Final için
  **≥3 tur rezerve** kalmalı.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Kontrolör düzeltme YAPMAZ.** Tek istisna `docs/active/` — orası kontrolörün kendi yüzeyi.
  Bu oturumda hakemin bir high'ı (bayat aktif katman) tam olarak o yüzeydeydi ve kontrolör
  kendisi kapattı.
- **Hakemin severity'si bağlayıcı değildir, ölçüm bağlayıcıdır.** Bir medium bu turda high'a
  yükseldi (kendi ürettiğimiz gerileme + bağlayıcı hüküm ihlali), bir high ölçülen
  erişilemezlik yüzünden evine geri kondu.
- **Kendi ürettiğin medium'u park etme.** Politikanın medium-advisory izni ÖNCEDEN VAR OLAN
  borç içindir; gerileme bu yürütmenin ürünüyse düzeltilir.
- **Spec değil, spec-input kanoniktir.**
- **Uygulayıcı raporunu doğrulanmamış iddia say** — ama iyi uygulayıcı kendi kusurunu bildirir:
  bu turdaki uygulayıcı kapatamadığı ayağı gizlemedi, üç yerde etiketledi ve bağlayıcı ek
  metnini kendi başına yeniden yazmaya kalkmadı.
- **Modül taşımasında sadakat İDDİA EDİLMEZ, ÖLÇÜLÜR.** Bu turda 27 adın 27'si bayt-aynı
  çıktı; ölçmeden "sadece taşıdım" demek kabul edilmez.
- Diskte bekleyen düzeltme YOK; her iki çalışma ağacı da temiz.
