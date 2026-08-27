---
title: Sektör Bilgi Paketi — Plan 2/2 İşletim Hattı
status: plan-approved
date: 2026-08-27
source_spec: docs/specs/2026-08-21-sektor-bilgi-paketi.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: true
codex_plan_review_status: approved-by-iteration-limit
codex_plan_review_iterations: 7
codex_plan_review_log: docs/reviews/codex/2026-08-27-sektor-bilgi-paketi-plan2.md
---

# Sektör Bilgi Paketi — Plan 2/2: İşletim Hattı Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.
> **Skill chain override:** `finishing-a-development-branch` ve `using-git-worktrees`
> otomatik zincirleri KIRILIR — kapanış `/simplify-claude-codex` →
> `/review-claude-codex` → `/security-review-claude-codex` → `/finish-branch-claude-codex`
> sırasıyla yapılır.

**Goal:** Sektör bilgi paketini ÜRETEN ve AKTİVE EDEN işletim hattını kurmak — sözleşme
düzeltmelerinden kuyumculuk pilotunun aktivasyonuna kadar.

**Architecture:** Plan 1 runtime çekirdeğini (DB sözleşmesi + prompt tüketimi + yaşam
döngüsü servisleri) kurdu ve main'de. Bu plan onun üstüne ÜRETİM hattını koyar. Kanonik
sıra bağlayıcıdır: **sentez → motor → draft** — sentez çıktısı tek başına DB'ye yazamaz.
İş mantığı monorepo'da test edilebilir CLI olarak yaşar (`scripts/sector_sweep.py`
deseni: argparse · açık `--database-url` · deterministik çıktı · anlamlı çıkış kodu);
`~/.claude/commands/` yalnız ince çağırıcı adaptör taşır. Kaynak görev sözleşmeleri dış
araştırma deposunda KALIR; monorepo bir pin manifesti tutar ve uyuşmazlıkta resmî koşu
fail-closed durur.

**Tech Stack:** Python 3.12 + asyncpg + argparse CLI (mevcut backend), PostgreSQL
migration (`shared/db/migrations/035_*.sql`, `036_*.sql`), pytest (Plan 1'de kurulu),
n8n workflow JSON (`shared/n8n-workflows/`), Claude Code + Codex CLI (denetçi oturumları).

**Spec:** `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)

**Spec girdisi (KANONİK — çelişkide girdi esastır):**
`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`. Spec bir damıtmadır ve
162 karar kartından 32'sini hiç taşımamıştır (ölçüldü:
`docs/research/2026-08-27-spec-input-bosluk-raporu.md`). Bir sözleşme ayrıntısını spec'te
bulamazsan girdiye dön.

**Karar turu:** `docs/research/2026-08-27-plan2-karar-turu.md` — 13 kapalı Eray kararı.

---

## Global Constraints

- **Kanonik sıra:** `sentez → motor → draft`. Sentez çıktısı DB'ye `draft` YAZAMAZ;
  yalnız dosya + ham artefakt katmanına yazılır (spec §8.1, karar turu "Plan 2 kapsam").
- **Tek yazma yüzeyi (K-135):** `sector_packages` tablosuna yazım YALNIZ
  `sector_package_lifecycle.py` fonksiyonlarından yapılır. Doğrudan SQL `INSERT`/`UPDATE`
  bu planda YASAK (migration dosyaları hariç).
- **Ölçülmemiş sayı kapı yapılmaz (İlke 9):** bariyer eşikleri (K-130/131/132), açık soru
  sınırı (≤10, K-74), denetçi öneri sınırı (≤5, K-75), alan boyut hedefleri ve ~6.000
  karakter tavanı **kapı DEĞİLDİR**. Mekanizma kurulur, değer boş kalır, pilot kalibre eder.
- **Katman-1 kapısı:** enjeksiyon yüzeyine dokunan HER görevin sonunda
  `cd apps/social/backend && python -m pytest tests/prompt_regression/ -v` taze koşulur;
  tek bayt fark = RED.
- **Migration geri alma:** her yeni migration `shared/db/migrations/rollback/<n>_down.sql`
  ile birlikte iner. "git revert" DB için geri alma DEĞİLDİR.
- **Dış depo sınırı:** `_SABLON.md` · `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`
  kanonik olarak `/root/otomaix-sosyal-medya-arastirmasi/` deposundadır. Monorepo'ya
  düzenlenebilir ikinci kopya ALINMAZ — yalnız pin manifesti.
- **Sır hijyeni (K-136):** koşu günlüğü yazıcısı maskeleme süzgecinden geçer; sır hiçbir
  kopyaya girmez (hata mesajları dahil).
- **Körlük (K-137):** denetçiye giden pakette araç kimliği BULUNMAZ — dosya adı, talimat
  ve rapor gövdesi dahil. Anonimleştirme kod düzeyindedir, disiplin değil.
- **Çalışma dizini BAĞLAYICIDIR (review turu düzeltmesi).** Her adım kendi kabuğunda
  başlar — önceki adımın `cd`'si DEVRALINMAZ. Bu yüzden her test komutu kendi içinde
  `cd apps/social/backend && …` taşır; migration dosyaları ve `shared/` artefaktları
  repo kökünden adreslenir. **Dış depoda çalışan görevler** (Task 2 · Task 4) bunu
  başlıklarında açıkça yazar ve bitiminde monorepo'ya döner.
- **Commit dili:** Conventional Commits, İngilizce, ≤72 karakter. Push YOK.

---

## Karar Kapıları (açık K-ID'ler — bu planın davranışı)

| K-ID | Soru | Bu planın davranışı |
|---|---|---|
| K-128 | Mevzuat/güvenlik bloklaması kapısı benimsenecek mi? | **AÇIK — bu kapı KURULMAZ ve pasif doğar** (`policy_config.block_on_legislation=False`). **K-125 ile KARIŞTIRILMAZ — iki ayrı bloklama yolu vardır:** (a) **K-125 yolu (BENİMSENDİ, aktif):** `guncelle`/`cikar` için iki denetçi mutabakatı aranır; mevzuat/güvenlik alanında (K-129 sabit listesi) **uyuşmazlık** koşuyu bloklar. Bu Eray'ın 2026-08-27 kararıdır, K-128'e bağlı DEĞİLDİR. (b) **K-128 yolu (AÇIK, pasif):** denetçiler **uyuşuyor** olsa bile mevzuat/güvenlik öğesi doğrulanamıyorsa (`risk_unverified`) koşuyu bloklama kapısı. Kod yeteneği kurulur, yapılandırma bayrağı `False` doğar. Karar kapanınca tek satır açar. |
| K-52 | Marka DNA verisi motora girdi olacak mı? | **AÇIK — girmez.** Motor girdileri §9.1 ile sınırlıdır; DNA okuma yolu açılmaz. Karar "girsin" çıkarsa yeni girdi kalemidir, mevcut kontrolleri değiştirmez. |
| K-11(a/b), K-12, K-13 | Katman-2 örneklem/eşik, maliyet, aktif paket tavanı | **Kapı yapılmaz** (spec §1.3 isim isim sayıyor). Pilot ölçüm kalemleridir; Task 19 ölçümü koşar, değer üretmez. |
| K-32…K-37 | Genişleme kapıları | **Plan 2'yi etkilemez** — pilot sonrası genişleme turunun konusu. Bu planda hiçbir görev bunlara dokunmaz. |
| K-47 | Yılbaşı kategori tutarsızlığı | **Dokunulmaz** (spec §17.2 bakım borcu). Pakete miras kalır. |
| K-06 | Legacy `/posts/generate-short-video` | **Dokunulmaz.** Katman-1 fixture'ında bugünkü bozuk-boş davranışıyla donmuş (Plan 1 Task 7); K-06 yalnız beklenen değeri belirler. |
| K-10 | Prompt enjeksiyonu savunması | **KAPALI: Faz 1'de kurulmaz** (bilinçli risk kabulü). Risk kaydı R-09 açık kalır. Bu planın hiçbir görevi enjeksiyon savunması eklemez. |
| K-85, K-153 | Kalıp semantik eşleştirme ölçütü / yöntemi | **AÇIK — ve bu plan onları KAPATMAZ.** İlk yazımda "kimlik tasarımı bunları gereksiz kılar" denmişti; **bu iddia review turunda ÇÜRÜTÜLDÜ ve geri alındı** — döngüseldi: kimlik `guncelle` kararında korunuyor, ama *metni değişmiş bir kalıbın `guncelle` mi `cikar+ekle` mi olduğu* sorusunun kendisi K-85/K-153'tür. Rastgele kimlik o ölçütü tanımlamaz. **Bu planın yaptığı:** yürürlükteki sözleşmenin **iddia düzeyinde eşleştirme**sini (denetçi sözleşmesi ADIM 2 "eş anlamlı ifadeleri aynı iddia say"; sentez sözleşmesi ADIM 1-2) **mevcut yöntem olarak KABUL ETMEK** — yeni mekanizma kurmaz, seçim yapmaz. **Belirsiz sınıflandırma açık soruya düşer** ve K-71 gereği aktivasyonu bloklar. Kartların ürün ayakları (K-85 kalite/risk · K-153 operasyon yükü — hakemli dal kalıp başına insan kararı doğurur) **Eray'a açık kalır**; kapanmaları bu planın çıktısı DEĞİLDİR. |

---

## Plan'ın bağladığı teknik kararlar (İlke 8: Eray'a FYI — doğrulaması review zinciri)

Karar turu 30 teknik kalemi plana devretti. Bağlanan hükümler:

1. **K-151 kimlik biçimi · K-152 üretim:** `unit_id` = `ku-` + 12 hex karakter, ilk `ekle`
   anında **rastgele** üretilir. Metin özetinden TÜRETİLMEZ (girdi hükmü) — özet, kalıbın
   metni `guncelle` ile değişince kimliği kırardı.
2. **K-86 kimlik koruma seviyesi:** kimlik `guncelle` kararında KORUNUR, `cikar`+`ekle`
   ikilisinde YENİDİR. **Dürüst sınır (review turunda düzeltildi):** bu, kimliğin
   *taşınma kuralını* bağlar; *hangi değişikliğin `guncelle` sayılacağını* bağlamaz — o soru
   K-85/K-153'tür ve AÇIK kalır (bkz. Karar Kapıları). Bu plan yürürlükteki iddia-düzeyi
   eşleştirmeyi mevcut yöntem olarak kabul eder, yeni ölçüt tanımlamaz.
3. **K-154 temsil:** her karar satırı `unit_id` taşır; `cikar`+`ekle` çifti iki ayrı satırdır
   ve `ekle` satırı `yerine_gecer: <eski unit_id>` alanı taşır.
4. **K-25 aktör:** her karar satırı `aktor` ∈ {`sentez`, `motor`, `insan`} taşır.
5. **K-87/K-108 temsil:** `decision_log` satırları iki türlüdür — `tur: "karar"`
   (beş değerli enum KAPALI kalır) ve `tur: "not"` (`sinif`: `reddedilen-aday` ·
   `eslesmeyen-ozel-gun`). Enum'a altıncı değer EKLENMEZ.
5b. **K-107 temsil — DÜZELTİLDİ (review turu):** ilk yazım kısmi turda değişmeyen alanları
   `tur="not"` satırına bağlamıştı; bu **spec §3.5'e aykırıydı**: *"Yalnız-özel-gün turunda
   taşınan temel alanlar da birer `koru` satırıdır — sessiz taşıma yok."* Ayrıca motorun
   karar-kapsamı kontrolü her `unit_id` için bir SONUÇ arar; tek not satırı onu karşılamaz,
   yani kısmi turlar ya izlenebilirliğini kaybeder ya her seferinde bloklanırdı.
   **Bağlanan hüküm:** kısmi turda değişmeyen HER birim kendi `tur="karar"`, `karar="koru"`
   satırını alır; `kapsam: "kismi-tur-tasima"` o satırın **ek alanıdır**, satırın yerine
   geçmez.
6. **K-100 envanter şeması — DÜZELTİLDİ (review turu):** denetçi çıktısına
   `yeniden_dogrulama` bölümü — `[{unit_id, statu, kanit, gerekce}]`, `statu` beş değerle
   kapalı. **`gerekce` ilk yazımda düşmüştü;** kanonik girdi (spec-input satır 1031) dört alan
   istiyor: *"karar birimi anahtarı, denetçi statüsü, kanıt referansı ve tek cümle gerekçe."*
   Spec bu ayrıntıyı taşımamış — girdi kanoniktir.
   **Tamlık sözleşmesi (girdi hükmü):** denetçi *"aynı aktif paket anlık görüntüsündeki
   BÜTÜN karar birimlerini"* tarar. Dolayısıyla envanter **tam kapsam** kanıtıdır: her aktif
   `unit_id` her iki raporda **tam bir kez** görünür; eksik · tekrar · tanınmayan kimlik ·
   geçersiz statü · farklı anlık görüntü → rapor GEÇERSİZ (Task 9 kapısı). Motor yalnız
   doğrulanmış envanteri tüketir — aksi hâlde bir denetçinin eksiği "mutabakat" gibi görünürdü.
7. **K-106 yerinde güncelleme:** reddedilen `draft` **aynı sürüm numarasıyla yerinde**
   güncellenir; yeni sürüm yakılmaz. Tüm kapılar yeniden koşar (kısmi güncelleme kapı
   atlamaz).
8. **K-90:** `tur durduruldu` ayrı sonuç tipi DEĞİL — `blocked` + `sebep` alanı.
9. **K-91:** ilk paket koşusunda `no_change` GEÇERSİZDİR (fail-closed hata).
10. **K-92 canonical hash:** `sha256` — anahtarları sıralı, boşluksuz, NFC-normalize JSON
    üzerinden. Liste sırası içeriğin parçasıdır, normalize edilmez.
11. **K-93/K-95/K-96/K-97:** `no_change`/`blocked` koşuları dahil HER koşu
    `social.sector_package_runs` satırı üretir (paket satırı üretmeden). Motor sürümü +
    yapılandırma hash'i her satıra damgalanır. Özgün sentez (ham katman) · nihai aday ·
    gerekçeli fark ÜÇÜ AYRI saklanır.
12. **K-94 — DÜZELTİLDİ (review turu):** ilk yazım "`expected_active_version` her zaman
    dolu" diyordu; bu **ilk aktivasyonu İMKÂNSIZ kılıyordu.** Ölçüldü
    (`sector_package_lifecycle.py::ActivationGateEvidence.__post_init__`): alan `None` ise
    kontrol ATLANIR, dolu ise `< 1` REDDEDİLİR. İlk pakette gerçek aktif sürüm yoktur —
    yani hangi tam sayı yazılırsa yazılsın ya yapım hatası ya uyuşmazlık üretirdi.
    **Bağlanan hüküm:** kanıt sınıfı `expected_no_active: bool = False` alanı kazanır;
    `expected_active_version` dolu OLMASI veya `expected_no_active=True` olması —
    **tam olarak biri** zorunludur (ikisi birden veya hiçbiri → yapım hatası).
    `activate_package` iki hâli de karşılaştırır: `expected_no_active=True` iken sektörde
    aktif satır VARSA geçiş reddedilir. Böylece K-94 gerçekten zorunlu olur ve ilk
    aktivasyon da ifade edilebilir. Eski `None`-atlar davranışı KALKAR.
13. **K-98:** onay anlık görüntüsü YAZILDIKTAN SONRA değişmez — DB tetikleyicisi dolu
    snapshot üzerine `UPDATE`'i reddeder. Diğer kolonlar (karar, süre, zaman) güncellenebilir.
14. **K-99 — DÜZELTİLDİ (review turu):** ilk yazım olayı doğrudan
    `package_events.log_package_event`'e bağlıyordu; **ölçüldü** ki o küme KAPALI:
    `033_package_events.sql` `package_events_type_check` dokuz değer sayıyor
    (`mismatch_fallthrough` · `package_read_error` · `stale_assignment_fallback` ·
    `stamp_missing` · `stamp_invalid` · `stamp_stale_at_persist` · `activation` ·
    `rollback` · `deactivation`) — `approval`/`rejection` YOK, yani onay da ret de
    yazılamadan patlardı. Dahası 033 kendi doğrulama bloğunda CHECK metnini **birebir
    pinliyor** (satır 115 ve 184), yani genişletme o pini de ilgilendirir.
    **Bağlanan hüküm:** (a) migration 036 CHECK'i `approval` ve `rejection` ile genişletir
    ve geri alma script'i daraltır; (b) 033'ün pinlenmiş beklenti metni **sürüm-farkında**
    hâle getirilir — 033-tek-başına beklentisi geçerli kalır, 036 sonrası genişlemiş küme
    de kabul edilir; (c) olaylar yaşam döngüsü kapsam sınıfındadır (033 F21 notu:
    `sector_id` + `package_id` + `actor` ister), bu yüzden `record_decision` koşu kimliğinin
    yanında paket kimliğini de taşır. Onay yüzeyi yalnız `activation_eligible` koşuda
    çalıştığı için taslak her zaman vardır.
15. **K-103 yetki zorlaması — GÜÇLENDİRİLDİ (review turu):** iki katman —
    (a) **yapısal:** hiçbir HTTP router yaşam döngüsü yazıcılarını import ETMEZ **ve**
    depo genelinde (migration + yaşam döngüsü modülü dışında) `sector_packages` tablosuna
    doğrudan SQL yazımı YOKTUR — tarama import'la sınırlı kalmaz, ham SQL de tarar.
    (b) **etkin yetki:** `information_schema.role_table_grants` TEK BAŞINA yetersizdir —
    üyelikle miras, sahiplik, `PUBLIC` grant'ı ve superuser'ı göstermez, yani "zaten yetki
    yok" diye YANLIŞ ölçüm üretebilir. Ölçüm `has_table_privilege(<rol>, 'social.sector_packages',
    'INSERT'/'UPDATE'/'DELETE'/'TRUNCATE')` + rol üyeliği/sahiplik/superuser/PUBLIC
    incelemesiyle yapılır ve **negatif yazma denemesiyle** kapatılır (API kimliğiyle yazım
    gerçekten reddediliyor mu). Rol adı ölçülmeden migration'a yazılmaz (Task 15 Step 6).
16. **K-74/K-75 taşma:** taşan maddeler DÜŞÜRÜLMEZ, kesilmez — koşu raporunda
    `tasma: true` işaretlenir. Sayı kapı DEĞİLDİR (İlke 9).
17. **K-76 bağlantı · K-78 sıra:** denetçiler **yerel CLI alt süreci** olarak, **SIRALI**
    koşulur. Paralellik iki denetçide kazanç üretmez, ortak-durum riski üretir.
18. **K-14 ön kontrol:** HER turdan önce ZORUNLU ve mekanik — Denetçi-2'nin web erişimi
    sınanır; başarısızsa tur BAŞLAMAZ (fail-closed).
19. **K-79 izolasyon:** her denetçi ayrı çalışma dizininde, aynı bayt-özdeş girdi kopyasıyla
    koşar; kopyaların hash'i koşu kaydına yazılır.
20. **K-88 eleme/not eşlemesi:** eleme YALNIZ açıkça eleme sayılan kontrollerden doğar
    (bugün tek küme: K-127 kaynak tabanı < 2 → koşu durur). Tüm adet alt sınırları `not`
    üretir — varsayılan `notlu geçti`.
21. **K-89:** mekanik kapı kontrol kümesi kodda **dondurulmuş demet**tir; kontrol eklemek
    sözleşme revizyonu ister.
22. **K-09 — DÜZELTİLDİ (review turu):** benzersizlik `UNIQUE (run_id, source, kind)`'tir,
    AMA **ölçüldü** ki bu indeksi `sector_research_artifacts`'a eklemek Plan 1'in donmuş
    sözleşmesine dokunuyor: `032_sector_packages.sql` (satır 419-420) o tablonun indeks
    kümesini *"kapalı"* diye **tam metinle** pinliyor (iki indeks); fazladan indeks 032'nin
    kendi doğrulamasını düşürür — özellikle 036'dan SONRA 032 yeniden uygulanırsa.
    **Bağlanan hüküm:** 036 indeksi ekler **ve** 032'nin kapalı-küme beklentisi
    **sürüm-farkında** hâle getirilir: 032-tek-başına iki indeks bekler; adı geçen K-09
    indeksi VARSA kabul edilir, adı geçmeyen fazladan indeks hâlâ REDDEDİLİR (kapalılık
    vaadi zayıflamaz). **Geri düşüş yolu:** 032'ye hiç dokunmadan, benzersizliği tamamen
    036'nın sahip olduğu ayrı bir yükleme-idempotency tablosunda tutmak.
23. **K-17 / K-83 koşu kimliği — DÜZELTİLDİ (review turu):** ilk yazım koşuyu
    `(run_id, attempt)` ile anahtarlıyor, artefaktı yalnız `run_id` ile, klasörü de
    `run_id`'ye eşitliyordu — yani yeniden koşum ya eski artefaktlarla ÇAKIŞIR ya da klasör
    adı koşu satırının kimliğiyle eşleşmez. İki kimlik modellenmiş ama üreticiler arasında
    ilişkilendirilmemişti. **Bağlanan hüküm: `run_id` deneme başına KANONİK kimliktir** —
    tek anahtar, her yerde aynı: koşu satırı · artefakt · paket `run_id` bağı · klasör adı.
    Yeniden koşum **YENİ bir `run_id`** alır ve `parent_run_id` ile ilkine bağlanır.
    Ayrı `attempt` kolonu YOKTUR (ikinci kimlik uzayı kapatıldı).
24. **K-82 yürütme durumu — DÜZELTİLDİ (review turu):** ilk yazımda `mark_incomplete`'in
    yazacağı yer yoktu — `sonuc` motorun çıktısıdır, "yarım kaldı" onun değeri değildir.
    **Bağlanan hüküm:** koşu satırı `sonuc`'tan AYRI bir `durum` kolonu taşır:
    `calisiyor` · `tamamlandi` · `tamamlanmadi` (kapalı küme). `sonuc` yalnız
    `durum='tamamlandi'` iken doludur. Yarım koşuda dosya EZİLMEZ.
25. **K-24 ölçüm mekanizması:** motor her koşuda ham dağılımı (değişim sayıları/oranları)
    koşu kaydına yazar. **Değer üretmez** — kalibrasyon bu kayıtları okumaktır.
26. **K-112 takvim erişilemezliği — İKİ AYRI YOL, ikisi de bağlanır** (bağımsız hakem
    itirazı, 2026-08-27: ilk yazım yalnız ölçüm yapıyordu, hangi kod yolunun değişeceğini
    ve hata-enjeksiyon testini bağlamıyordu).
    **(a) Üretim yolu (kararın asıl konusu):** takvim okunamazsa özel gün bloğu **sessizce
    düşer + zorunlu log**; uydurma anahtar hiçbir koşulda üretilmez. Dikiş: özel gün
    eşleştirme/enjeksiyon yolu (`sector_packages.py::match_special_day` çağıranı).
    **(b) Yazım kapısı (ölçülmüş ikinci maruziyet):** `sector_package_lifecycle.py::insert_draft`
    takvim listesini doğrulayıcıya beslemek için okuyor ve **hata yakalanmıyor** — takvim
    erişilemezse taslak yazımı doğrudan kesilir. Bu yolda sessiz düşüş YANLIŞ olurdu
    (anahtar doğrulaması yapılamadan yazım, uydurma anahtarı içeri alırdı): doğru davranış
    **fail-closed durup açık hata vermektir** — ama bugün bu bilinçli bir karar değil,
    kazara. Plan onu bilinçli hâle getirir ve **hata enjeksiyonuyla test eder**.
    Bugünkü davranışın ölçümü Task 5 Step 1'de; bağlama Task 12'de.
27. **K-117 web sitesiz marka:** ayrı uç AÇILMAZ — mevcut öneri ucu boş aday kümesinde boş
    döner (Plan 1 Task 15 invariantı).
28. **K-111 / K-114:** fiilen Plan 1'de çözüldü (`validate_package_content` ·
    `sub-sector-candidates`); bu plan yalnız karar olarak kayda geçirir, kod değiştirmez.
29. **K-145 geri alma — ÜÇ KURAL, provenanstan ibaret DEĞİL** (bağımsız hakem itirazı,
    2026-08-27). İlk yazım kararı "koşu kaydı kural sürümünü taşır"a indirgemişti; kanonik
    kayıt fazlasını istiyor: *(a)* **etkisi kanıtlanan** paketler geri alınır · *(b)* **etki
    alanı güvenilir biçimde ayrılamıyorsa** kuralın uygulandığı **BÜTÜN** paketler etkilenmiş
    kabul edilir ve geri alınır · *(c)* **etkilenmediği kanıtlanan** paketler gereksiz yere
    geri alınmaz. **Belirsizlik güvenli tarafa düşer** — ayrım yapılamadığı anda davranış
    koşulsuz toplu geri almayla AYNIdır.
    **Ölçütler ("etkisi kanıtlanan" · "güvenilir ayrılabilen") hiçbir katmanda tanımlı değil
    ve uydurulmadı** — kanonik kayıt bunu *teknik kabul sözleşmesi* sayıp evini olay müdahale
    yordamına veriyor, kullanıcı kararına çevirmiyor. Bu plan o sözleşmeyi Task 13'te yazar.
    **Mekanizma sınırı, dürüst etiket:** birden çok paketi TEK işlemde geri alan mekanizma
    hiçbir katmanda tarif edilmemiştir; aksiyon **her etkilenen pakete ayrı ayrı** mevcut
    geri alma yordamının uygulanmasıdır. Yeni toplu mekanizma icat EDİLMEZ.
30. **K-72:** düzeltme turu otomatik BAŞLAMAZ; yönetici elle tetikler (komut ailesi ucu).

---

## Plan 1'den devralınan arayüzler (Consumes — imzalar Plan 1'in kanonik listesinde)

Kaynak: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` → "Plan 2'ye teslim edilen arayüzler".

- `app/services/sector_packages.py::normalize_special_day_key(name) -> str`
- `app/services/sector_packages.py::validate_package_content(content, *, banned_brand_names, holiday_keys) -> ValidationResult`
- `app/services/sector_package_lifecycle.py::insert_draft(db, *, sector_id, content, schema_version, run_id=None, actor) -> UUID`
- `app/services/sector_package_lifecycle.py::activate_package(db, *, package_id, evidence: ActivationGateEvidence, actor)`
- `app/services/sector_package_lifecycle.py::rollback_package(db, *, sector_id, to_version, evidence: RollbackGateEvidence, actor)`
- `app/services/sector_package_lifecycle.py::deactivate_package(db, *, package_id, actor)`
- `app/services/notifications.py::record_admin_event(db, *, kind, payload, idempotency_key) -> UUID`
- `app/services/package_events.py::log_package_event(...)`
- Katman-1 harness: `apps/social/backend/tests/prompt_regression/`
- Migration 032/033/034 şeması + `scripts/sector_sweep.py`

### Bu planın Plan 1 arayüzünde yaptığı DEĞİŞİKLİKLER (ölçülmüş boşluk)

**Ölçüldü (2026-08-27, `sector_package_lifecycle.py:307-365`):** `insert_draft` bugün
`decision_log` alanını **sabit** `[{"event": "draft_created", "actor": owner}]` olarak
yazıyor — sentez/motor karar günlüğünü kabul eden bir parametresi YOK. Plan 1'in kanonik
arayüz listesi de bu imzayı taşıyor. Karar günlüğü Plan 2'nin çekirdek ürünüdür, dolayısıyla
imza genişletilmek ZORUNDADIR:

- `insert_draft(..., decision_log: list[dict] | None = None)` — verilirse şema
  doğrulamasından geçer ve yazılır; verilmezse bugünkü tek satırlık davranış korunur
  (geriye uyum: Plan 1'in arayüz-sözleşme testi kırılmaz). **Task 3.**
- `ActivationGateEvidence` yeni alan: `expected_no_active: bool = False` (K-94 kapanışı —
  bkz. teknik karar 12). **Task 14/15.**
- `_update_draft_row(...)` — lifecycle modülünde **ÖZEL** karşılaştır-ve-güncelle ilkeli
  (K-106'nın ham mekaniği). **Public API DEĞİLDİR.** **Task 15.**

Bu değişiklikler `tests/test_plan2_interface_contract.py` dosyasına eklenir; Plan 1'in
mevcut satırları SİLİNMEZ.

### Köken ispatı — review turunun kapattığı iki atlatma yolu

**Ölçülmüş kusur (Codex adversarial review, 2026-08-27):** ilk yazımda kanonik sıra
`sentez → motor → draft` yalnız **isim ve tip düzeyinde** iddia ediliyordu. `writeback`
çağıranın verdiği bir `EngineResult` nesnesini kabul edip yalnız
`sonuc == "activation_eligible"` alanına bakıyordu — yani bir sentez adayı, motor hiç
koşmadan, elle kurulmuş bir sonuç nesnesine sarılıp yazdırılabilirdi ve planlanan yapısal
testler bunu GEÇİRİRDİ. Aynı kusurun ikinci yüzü `update_draft`'tı: public imzası
(`package_id, content, decision_log, actor`) koşu, motor sonucu, regresyon kanıtı, denetçi
envanteri ve dondurulmuş anlık görüntü taşımıyordu — yani reddedilmiş bir taslak, sentez
ve motor hiç koşmadan güncellenip sonra aktive edilebilirdi.

**Bağlanan hüküm — kanıt DB'den okunur, çağırandan alınmaz:**

- `writeback.write_draft_from_run(db, *, run_id, actor) -> UUID` — motor sonucunu
  **`sector_package_runs`'tan işlem içinde okur**; `durum='tamamlandi'` ·
  `sonuc='activation_eligible'` · motor sürümü ve yapılandırma hash'i dolu ·
  `content_sha` yazılacak `final_candidate` ile eşleşiyor — beşi de sağlanmazsa yazmaz.
  Çağırandan `EngineResult` nesnesi KABUL ETMEZ.
- `writeback.update_draft_from_run(db, *, run_id, actor) -> None` — K-106
  yerinde güncellemenin TEK public yolu; **aynı `load_verified_run`'dan** geçer (ayrı kapı
  listesi YOK), önceki onay anlık
  görüntüsünü geçersizler ve durum kontrolünü güncellemeyle **aynı işlemde** yapar
  (aktivasyonla yarışta tek kazanan).
- Yapısal test import iddiasıyla yetinmez: depo genelinde `sector_packages` tablosuna
  doğrudan SQL yazan kod arar (migration + lifecycle modülü hariç).

**TEK KAPI LİSTESİ — sınıfın kapanışı (review turu 3).** İlk iki turda aynı hatayı üç kez
yaptım: kapıyı bir yolda güçlendirip kardeş yolda eski listeyi bıraktım (yazım yolu yedi
kapıya çıktı, güncelleme yolu beşte kaldı; aktivasyon DB'den doğrularken onay hâlâ
çağırandan alınıyordu). Tek tek yamamak sınıfı kapatmaz — **iki ayrı kapı listesinin var
olamayacağı** bir yapı gerekir:

- `runs.load_verified_run(db, *, run_id, for_update=True) -> VerifiedRun` — koşu satırını
  **kilitli** okuyan ve YEDİ kapının tamamını uygulayan TEK doğrulayıcı: `durum='tamamlandi'` ·
  `sonuc='activation_eligible'` · `engine_version` dolu · `engine_config_sha` dolu ·
  `content_sha` = `final_candidate` hash'i · `final_decision_log` dolu ·
  `decision_log_sha` = o günlüğün hash'i. Kapılardan biri düşerse `RunNotVerified` fırlatır.
- **Yazım · güncelleme · onay · aktivasyon — DÖRDÜ DE bu fonksiyondan geçer.** Hiçbiri kendi
  kapı listesini taşımaz; ikinci bir liste yazmak mümkün değildir. Yapısal test bunu zorlar:
  `writeback` ve `approval` modülleri koşu satırını `load_verified_run` dışında OKUYAMAZ.
- **Anlık görüntü ÜRETİLİR, kabul EDİLMEZ:** `approval.build_and_freeze_from_run(db, *,
  run_id, actor)` snapshot'ı kilitli koşudan + bağlı taslaktan **basar** ve aynı işlemde
  dondurur. Çağıranın kurduğu bir snapshot'ı kabul eden yol YOKTUR — aksi hâlde bir
  snapshot üzerinden onay alıp başka bir koşuyu aktive etmek mümkündü.
- **Onay karara değil, HASH'e bağlanır:** `approval_karar` dondurulmuş snapshot'ın hash'ini
  taşır; onay sonrası koşu satırı değişirse aktivasyon eşleşmez ve REDDEDİLİR.
- **Bir koşu → bir taslak (idempotent):** `sector_package_runs.package_id` yazım işleminde
  doldurulur; koşu satırı KİLİTLİ okunduğu için tekrar çağrı yeni sürüm yakmaz, **mevcut
  taslağı döndürür**. Tekilliği sağlayan kilit + dolu kolondur, kısıt DEĞİLDİR:
  `package_id` **benzersiz değildir** — benzersiz olsaydı "bir taslak → bir koşu" zorlanırdı
  ve K-106 düzeltme turu imkânsız hâle gelirdi (düzeltme yeni bir koşudur ve AYNI taslağı
  güncellemek zorundadır).
  (Bağ neden `sector_packages` tarafında değil: **ölçüldü** — `032_sector_packages.sql`
  satır 421-422 o tablonun kısıt kümesini *"kapalı"* diye tam metinle pinliyor; oraya kısıt
  eklemek Plan 1'in donmuş sözleşmesini düşürürdü. Bağ bu yüzden 036'nın kendi tablosunda.)
- **Düzeltme soyağacı (K-72 + K-106 + K-83 birlikte çalışsın diye).** Üç karar tek başına
  tutarlı ama birleştiklerinde bir çelişki üretiyor: K-72 düzeltmeyi **yeni bir koşu** yapar,
  K-83 yeni koşuya **yeni `run_id`** verir, K-106 ise **aynı taslağın** yerinde güncellenmesini
  ister. Çözüm, düzeltme turunun hedefini kalıcı olarak taşımasıdır:
  `runs.open_correction_run(db, *, parent_run_id, actor) -> str` reddedilmiş ana koşuyu
  KİLİTLER (`approval_karar='ret'` değilse REDDEDER), `package_id`'sini KOPYALAR ve
  `duzeltilen_run_id` ile soyağacını kaydeder.
  **Aynı anda TEK açık düzeltme (tur 5 düzeltmesi):** hedef taslak için sonuçlanmamış bir
  düzeltme koşusu varsa yenisi AÇILMAZ. Aksi hâlde iki düzeltme aynı taslağı yazabilir ve
  biri diğerinin onayladığı baytları ezerdi. "Sonuçlanmış" = kararı var (`onay`/`ret`) ya da
  `durum='tamamlanmadi'`; yani reddedilen bir düzeltme zinciri sürdürmeyi engellemez.
  Bu, tek operatörlü işletimde (K-54 · K-77) yeterli koordinasyondur — sürüm jetonlu bir
  durum makinesi kurulmaz. Sonra: `write_draft_from_run` düzeltme
  koşusunu **reddeder** (ikinci sürüm yakılamaz), `update_draft_from_run` ise soyağacını
  **şart koşar**. Ana koşunun dondurulmuş görüntüsüne DOKUNULMAZ (K-98); düzeltme koşusu
  kendi taze görüntüsünü basar.

---

## Dosya yapısı (yeni modüller ve sorumlulukları)

| Dosya | Sorumluluk |
|---|---|
| `apps/social/backend/app/services/sector_pipeline/contracts.py` | Dış sözleşme pin manifesti okuma + fail-closed doğrulama |
| `apps/social/backend/app/services/sector_pipeline/identity.py` | `unit_id` üretimi + karar günlüğü satır şeması (K-84 ailesi) |
| `apps/social/backend/app/services/sector_pipeline/brief_doctor.py` | Mekanik girdi kapısı (LLM'siz) |
| `apps/social/backend/app/services/sector_pipeline/runs.py` | Koşu/artefakt servisi (K-09/K-17/K-82/K-83/K-93) |
| `apps/social/backend/app/services/sector_pipeline/auditors.py` | Anonimleştirme · biçim kapısı · ön kontrol · orkestrasyon |
| `apps/social/backend/app/services/sector_pipeline/synthesis.py` | Sentez koşumu + çıktı doğrulayıcı |
| `apps/social/backend/app/services/sector_pipeline/engine.py` | Politika motoru (saf fonksiyon) |
| `apps/social/backend/app/services/sector_pipeline/approval.py` | Onay yüzeyi sunumu + anlık görüntü + onay olayı |
| `apps/social/backend/scripts/sector_pipeline_cli.py` | Operatör CLI (tek giriş noktası, alt komutlar) |
| `shared/contracts/research-contracts.pin.json` | Dış depo commit'i + dosya hash'leri |
| `~/.claude/commands/sektor-paket.md` | İnce çağırıcı adaptör (iş mantığı YOK) |

Motor **saf fonksiyondur**: girdi sözlükleri alır, sonuç sözlüğü döner, DB'ye dokunmaz.
Bu ayrım motoru mutasyon testine açık tutar (Task 12-13'ün TDD'si buna dayanır).

---

### Task 1: Dış sözleşme pin altyapısı + fail-closed doğrulayıcı

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/__init__.py`
- Create: `apps/social/backend/app/services/sector_pipeline/contracts.py`
- Create: `shared/contracts/research-contracts.pin.json`
- Test: `apps/social/backend/tests/test_contract_pin.py`

**Interfaces:**
- Consumes: yok (bu planın ilk görevi).
- Produces:
  - `contracts.load_pin(pin_path: Path) -> ContractPin` — manifest okuyucu.
  - `contracts.verify_pin(pin: ContractPin, repo_root: Path) -> list[str]` — boş liste =
    geçti; dolu liste = uyuşmazlık sebepleri.
  - `contracts.require_pin(pin_path: Path, repo_root: Path) -> None` — uyuşmazlıkta
    `ContractDriftError` fırlatır. **Resmî koşuyu başlatan HER CLI alt komutu bunu çağırır.**

**Bağlayıcı invariantlar:**
- Manifest üç sözleşme dosyasının **sha256**'sını ve dış depo **commit sha**'sını taşır.
- Doğrulama **fail-closed**: dosya yok · hash uyuşmuyor · commit uyuşmuyor · depo dizini
  yok — dördü de RED. "Uyarıp devam" dalı YOKTUR.
- Doğrulama dış depoya YAZMAZ ve `git` durumunu değiştirmez (salt-okunur).

- [ ] **Step 1:** Testleri yaz — `tests/test_contract_pin.py`:
  `test_verify_passes_on_matching_hashes` (pozitif kontrol; kapının gerçekten geçebildiğini
  kanıtlar) · `test_verify_fails_on_content_drift` (tek bayt değişir → RED) ·
  `test_verify_fails_on_commit_drift` · `test_verify_fails_on_missing_file` ·
  `test_verify_fails_on_missing_repo` · `test_require_pin_raises_contract_drift_error`.
  Fixture: `tmp_path` altında sahte üç dosyalı depo (gerçek araştırma deposuna dokunulmaz).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_contract_pin.py -v`
  — Beklenen: FAIL (`sector_pipeline` modülü yok).
- [ ] **Step 3:** `contracts.py` + boş `research-contracts.pin.json` iskeletini yaz.
- [ ] **Step 4:** Koş: aynı komut — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add fail-closed research contract pin verifier`

---

### Task 2: Sözleşme düzeltmeleri — altı zorunlu kalem + kapanış yansıma sweep'i

Bu görev **dış depoda** (`/root/otomaix-sosyal-medya-arastirmasi/`) çalışır ve resmî turu
bloklayan drift'leri kapatır. Spec §8.7 beş kalem sayıyor; **altıncısı** Codex ön-analizinde
bulundu.

**Files:**
- Modify: `/root/otomaix-sosyal-medya-arastirmasi/hakem-sentez-gorevi.md`
- Modify: `/root/otomaix-sosyal-medya-arastirmasi/hakem-denetci-gorevi.md`
- Modify: `/root/otomaix-sosyal-medya-arastirmasi/_SABLON.md`
- Modify: `shared/contracts/research-contracts.pin.json` (düzeltmelerden SONRA pinlenir)
- Test: `apps/social/backend/tests/test_contract_pin.py` (gerçek pin doğrulaması eklenir)

**Interfaces:**
- Consumes: Task 1 `contracts.verify_pin`.
- Produces: pinlenmiş sözleşme sürümü — sonraki tüm görevlerin girdi tabanı.

**Altı zorunlu düzeltme (spec §8.7 + §12.2):**
1. Sentez sözleşmesine **K-03 yansıması** — tür etiketi üstündür; "açık soruya düşür" metni kalkar.
2. Sentez girdi listesine **kök sektör rehberi** eklenir (eklenene kadar resmî tur BLOKLU).
3. `[kopya-şüphesi]` bayrağının **tüketim satırı** eklenir.
4. Sentez sözleşmesinin **rol hükmü** motorlu modele revize edilir — sentez karar mercii
   değil **aday değişiklik seti üreticisidir** (K-22=A sonucu).
5. Denetçi sözleşmesindeki URL örneklem bölümünün sabit **"dokuz satır"** yazımı koşullu
   ölçüme düzeltilir (kaynak sayısı elenmeyle değişebilir).
6. **Kanal anahtar uzayı dört değerle KAPATILIR** — `whatsapp_hatti` · `fiziksel_magaza` ·
   `randevu_sistemi` · `eticaret_sitesi`. Serbest `X` değeri deterministik filtreyi
   imkânsız kılar (spec §12.2; kod tarafı Plan 1'de `sector_packages.py::CHANNEL_KEYS`
   olarak zaten kapalı — sözleşme ona hizalanır).

**Kapanış yansıma sweep'i (Codex ön-analizi — beş satırlık checklist YETMEZ):**
Şu kapanmış kararların sözleşme metnine yansıyıp yansımadığı **tek tek** denetlenir ve
eksikler aynı turda yazılır: K-120 (`içerik-önerilmez` resmî değeri) · K-121 (mevzuat
öncelikli altılı kırpma sırası) · K-122 (churn koruması) · K-123 ("güçlü kaynak" ölçütü) ·
K-124 (kanıt yeterliliği) · K-126 (tek-kaynak istisnası) · K-02/K-113 (`video_kodlar`
iki alt LİSTE: `hareket` · `sahne`).

- [ ] **Step 1:** Sweep raporunu yaz: yukarıdaki 6 + 7 = 13 kalemin her biri için
  "sözleşmede var / eksik / kısmi" ölçümü, dosya + satır işaretiyle.
  Çıktı: `docs/research/2026-08-27-sozlesme-yansima-sweep.md`.
- [ ] **Step 2:** Eksik çıkan her kalemi ilgili sözleşme dosyasına yaz (dış depoda).
- [ ] **Step 3:** Sweep'i **yeniden** koş — hedef: 13/13 "var". Kısmi kalan varsa dürüst
  etiketle raporda kalır, düşürülmez.
- [ ] **Step 4:** Dış depoda commit et: `docs(contracts): close six blocking drifts + reflection sweep`
- [ ] **Step 5:** `shared/contracts/research-contracts.pin.json`'ı yeni commit + hash'lerle
  doldur; `tests/test_contract_pin.py`'a `test_real_pin_verifies_clean` ekle.
- [ ] **Step 6:** **Monorepo'ya dön** ve koş:
  `cd /root/otomaix/apps/social/backend && python -m pytest tests/test_contract_pin.py -v`
  — Beklenen: PASS. (Bu görev dış depoda başlar; göreli yol oradan çözülmez.)
- [ ] **Step 7:** Commit: `chore: pin research contracts after blocking drift closure`

---

### Task 3: Kalıp kimliği + karar günlüğü şeması (K-84 ailesi)

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/identity.py`
- Modify: `apps/social/backend/app/services/sector_package_lifecycle.py` (`insert_draft`
  `decision_log` parametresi)
- Modify: `apps/social/backend/tests/test_plan2_interface_contract.py`
- Test: `apps/social/backend/tests/test_unit_identity.py`

**Interfaces:**
- Consumes: `sector_package_lifecycle.insert_draft`.
- Produces:
  - `identity.new_unit_id() -> str` — `ku-` + 12 hex, rastgele.
  - `identity.validate_decision_log(rows: list[dict]) -> list[str]` — hata listesi.
  - `identity.decision_units(content: dict, decision_log: list[dict]) -> dict[str, dict]` —
    aktif paketin karar birimlerini `unit_id` → birim eşlemesi olarak döner (motorun
    karar-kapsamı kontrolünün ve K-100 envanterinin girdisi).
  - `identity.check_unit_integrity(content: dict, decision_log: list[dict]) -> list[str]` —
    eşlemenin gerçekten kapsayıcı olduğunu doğrular (aşağıdaki invariant).
  - **`identity.canonical_sha(value) -> str`** — K-92'nin kanonik hash kuralı (sıralı
    anahtar · boşluksuz · NFC). **Burada doğar, Task 13'te DEĞİL** (bağımsız hakem
    itirazı: Task 3 onu Task 13'ten önce kullanmak zorundaydı). Task 13'ün
    `engine.canonical_content_sha`'sı bunu ÇAĞIRIR, kendi kuralını yazmaz.
  - **`identity.enumerate_content_units(content: dict) -> dict[str, dict]`** — içeriği
    kanonik **yol**larına ayırır: `<alan>[<sıra>]` · `video_kodlar/<havuz>[<sıra>]` ·
    `ozel_gun/<anahtar>/<yuva>` · düz metin alanları için `<alan>`. **Sıra ordinali
    zorunludur** — aynı listede birebir aynı metin iki kez geçebilir ve yalnız hash ile
    ayırt edilemez (çokluk sorunu).
  - `insert_draft(..., decision_log: list[dict] | None = None)` — genişletilmiş imza.

**Kimlik NEREDE yaşıyor — bağımsız hakem itirazının kapanışı (2026-08-27).**
İlk yazım kimlikleri `content`'ten okumayı öngörüyordu. **Ölçüldü ki bunun yeri yok:**
`sector_packages.py::_check_cta_items` CTA öğesinin anahtar kümesini `{kalip, tur, gerekce}`
ile **eşitlik** olarak doğruluyor, `_check_special_day_shapes` aynısını beş yuvayla yapıyor,
`_check_field_shapes` ise diğer liste öğelerini ve iki video havuzunu **düz metin** olmaya
zorluyor. Yani içeriğe `unit_id` eklemek doğrulayıcı tarafından REDDEDİLİR. Kimliği yalnız
karar günlüğüne yazmak da yetmezdi: kapsam kontrolü "aktif paketin HER birimi" der, birim
kümesi bir yerden türetilebilmelidir.

**Bağlanan çözüm — içerik şeması DEĞİŞMEZ, birim kümesi karar günlüğünden TÜRETİLİR:**
- Karar günlüğü satırı `unit_id` yanında **`oge_yolu`** ve **`oge_sha`** taşır:
  `oge_yolu` kimliğin ÇAPASI (kanonik yol, sıra ordinali dahil), `oge_sha` ise bütünlük
  kontrolü (o öğenin kanonik hash'i). **Yalnız hash yetmez** — aynı listede iki özdeş metin
  aynı hash'i taşır ve eşleme bire bir olmaz.
- **Yaşayan küme (`kirp` DÜZELTİLDİ — bağımsız hakem itirazı, ölçüldü):** yeni paketin
  karar birimleri `koru` + `guncelle` + `ekle` satırlarıdır. **`kirp` ve `cikar` birimi
  kümeden DÜŞÜRÜR.** İlk yazım `kirp`'i yaşayan saymıştı; kanonik kayıt bunu çürütüyor —
  *"kırpma **paketten çıkarır, kayıttan çıkarmaz**"* (spec-input satır 1160): kırpılan öğe
  aday pakete GİRMEZ, yalnız karar günlüğünde ve ham katmanda durur. Eski tanım her gerçek
  kırpmada zorunlu olarak hayalet birim üretirdi.
- **Karar kapsamı hangi küme üzerinde ölçülür:** kanonik kayıt (satır 1187) kapsamı
  **AKTİF paketin** her birimi için tam bir sonuç (`koru`/`guncelle`/`cikar`/`kirp`) diye
  tanımlar; `ekle` yeni birim doğurur. Motor kontrolü bu ayrımı kullanır.
- **Bütünlük invariantı (`check_unit_integrity`) — YOL üzerinden, bire bir:**
  `enumerate_content_units(content)` ile yaşayan satırların `oge_yolu` kümesi **birebir
  aynı** olmalı (fazlası hayalet birim, eksiği sahipsiz öğe) **ve** her satırın `oge_sha`'sı
  o yoldaki öğenin taze hash'iyle eşleşmeli. İki yönlü küme eşitliği + hash eşleşmesi;
  tek yönlü kontrol yetmez.
- **Neden sürüklenmiyor:** içerik ve karar günlüğü yalnız yaşam döngüsü modülünden ve
  **aynı işlemde** hash'leriyle birlikte yazılır (K-135 + F19). Dışarıdan içerik
  düzenleyen bir yol olmadığı için eşleme bayatlayamaz.
- **`schema_version` ARTIRILMAZ, Plan 1 doğrulayıcısına DOKUNULMAZ** — bu, ilk yazımın
  gerektireceği şema göçünü ve Plan 1 testlerinin kırılmasını gereksiz kılar.

**Bağlayıcı invariantlar (seam: `identity.py::validate_decision_log`):**
- `tur` ∈ {`karar`, `not`} — kapalı.
- `tur="karar"` satırı: `alan` · `oge_yolu` · `unit_id` · `oge_sha` · `karar` ∈ {`koru`,`guncelle`,`cikar`,`ekle`,`kirp`}
  (BEŞ değer, kapalı) · `gerekce` · `kanit` · `aktor` ∈ {`sentez`,`motor`,`insan`}
  · **`kural_kimligi` + `kural_surumu`** — `aktor="motor"` satırlarında ZORUNLU, diğerlerinde
  boş. **Bağımsız hakem itirazı:** kural provenansı yalnız `engine_diff`'e yazılıyordu ama
  K-145'in tüketicisi `final_decision_log`'da arıyordu — üretici ve tüketici FARKLI
  artefaktlara bakıyordu, yani sınıflandırma hiçbir zaman `kanitli` üretemezdi.
  Damga artık uygulanan karar satırının kendisinde; `engine_diff` reddedilenlerin izini
  taşımaya devam eder.
- `karar="cikar"` satırı **pozitif kanıt satırı olmadan GEÇERSİZDİR** (spec §3.5).
- `karar="ekle"` satırı `yerine_gecer` alanı taşıyabilir (K-154, `cikar`+`ekle` çifti).
- `tur="not"` satırı: `sinif` ∈ {`reddedilen-aday`,`eslesmeyen-ozel-gun`} — **İKİ değer,
  kapalı.** `kismi-tur-tasima` bir not sınıfı DEĞİLDİR (K-107 düzeltmesi): kısmi tur taşıması
  `tur="karar"`, `karar="koru"` satırında `kapsam="kismi-tur-tasima"` **ek alanı** olarak
  temsil edilir. Not olarak yazılmış `kismi-tur-tasima` REDDEDİLİR — geçseydi doğrulayıcıdan
  çıkar ama motorun birim-başına kapsam kontrolünü karşılamazdı (sessiz taşıma geri gelirdi).
  Beş değerli karar enum'una altıncı değer EKLENMEZ.
- Aynı `unit_id` bir karar günlüğünde **birden fazla `karar` satırı taşıyamaz**.
- `unit_id` biçimi ihlali → RED (kimlik metin özetinden türetilemez; biçim kapısı bunu zorlar).

- [ ] **Step 1:** Testleri yaz — `tests/test_unit_identity.py`:
  `test_new_unit_id_format_and_uniqueness` · `test_decision_log_accepts_valid_rows`
  (pozitif kontrol) · `test_rejects_sixth_enum_value` · `test_rejects_cikar_without_evidence` ·
  `test_rejects_duplicate_unit_id_decisions` · `test_rejects_unknown_actor` ·
  `test_note_row_classes_are_closed` (İKİ değer) ·
  `test_kismi_tur_tasima_as_note_rejected` (K-107 kapısı — eski biçim geçmemeli) ·
  `test_kismi_tur_tasima_as_koru_field_accepted` (pozitif kontrol) ·
  `test_decision_units_derived_from_living_log_rows` ·
  `test_cikar_row_drops_unit_from_set` ·
  `test_integrity_rejects_orphan_content_item` (sahipsiz öğe — kapsam kaçağı) ·
  `test_integrity_rejects_ghost_unit` (içerikte karşılığı olmayan birim) ·
  `test_kirp_row_is_not_a_living_unit` (kanonik kırpma hayalet üretmemeli) ·
  `test_duplicate_identical_text_gets_distinct_paths` (çokluk — iki özdeş metin) ·
  `test_two_special_days_with_identical_body_do_not_collide` ·
  `test_first_package_assigns_new_id_to_every_enumerated_unit` ·
  `test_integrity_rejects_stale_sha_on_correct_path` ·
  `test_motor_row_without_rule_id_rejected` (K-145 damgası) ·
  `test_motor_row_without_rule_version_rejected` ·
  `test_non_motor_row_carrying_rule_stamp_rejected` ·
  `test_integrity_passes_on_consistent_package` (pozitif kontrol) ·
  `test_content_schema_unchanged_plan1_validator_still_passes` (şema göçü YOK).
- [ ] **Step 2:** `tests/test_plan2_interface_contract.py`'a
  `test_insert_draft_accepts_decision_log` ve `test_insert_draft_without_decision_log_keeps_plan1_behavior`
  ekle (geriye uyum pozitif kontrolü).
- [ ] **Step 3:** Koş: `cd apps/social/backend && python -m pytest tests/test_unit_identity.py tests/test_plan2_interface_contract.py -v`
  — Beklenen: FAIL.
- [ ] **Step 4:** `identity.py`'ı yaz + `insert_draft`'a `decision_log` parametresini ekle
  (verilirse `validate_decision_log`'dan geçirilir, boş değilse yazılır; verilmezse Plan 1
  davranışı aynen).
- [ ] **Step 5:** Koş: aynı komut — Beklenen: PASS.
- [ ] **Step 6:** Koş: `cd apps/social/backend && python -m pytest tests/ -v` — Beklenen: Plan 1 testlerinde
  regresyon YOK (imza genişlemesi kimseyi kırmadı).
- [ ] **Step 7:** Commit: `feat: add persistent unit identity and decision log schema`

---

### Task 4: Sözleşme v2 — denetçi yeniden-doğrulama envanteri + sentez kimlik taşıması

**Files:**
- Modify: `/root/otomaix-sosyal-medya-arastirmasi/hakem-denetci-gorevi.md`
- Modify: `/root/otomaix-sosyal-medya-arastirmasi/hakem-sentez-gorevi.md`
- Modify: `shared/contracts/research-contracts.pin.json`
- Test: `apps/social/backend/tests/test_contract_pin.py`

**Interfaces:**
- Consumes: Task 3 `identity` şeması.
- Produces: sözleşme v2 — Task 9/10/11'in girdi tabanı.

**Sözleşme eklemeleri:**
- **Denetçi sözleşmesi (K-125 + K-100):** ADIM 3'ten sonra yeni bir adım — *aktif paketin
  yeniden doğrulanması*. Denetçi, kendisine verilen **aktif paket anlık görüntüsündeki HER**
  karar birimini tarar ve `yeniden_dogrulama: [{unit_id, statu, kanit, gerekce}]` üretir
  (**dört alan** — kanonik girdi satır 1031: *"karar birimi anahtarı, denetçi statüsü, kanıt
  referansı ve tek cümle gerekçe"*). `statu` beş değerle kapalı: `supported` ·
  `not_observed` · `needs_update` · `contradicted` · `risk_unverified`.
  Sözleşme açıkça yazar: **`not_observed` geçersizlik kanıtı DEĞİLDİR.**
  **Tamlık sözleşmede yazılır:** her birim **tam bir kez** raporlanır; atlanan birim raporu
  geçersiz kılar. (Bu, motorun mutabakat kapısının girdisidir — eksik envanter "uyum" gibi
  görünürdü.)
- **Denetçi çıktı sözleşmesi:** dört bölüm → **beş bölüm** (yeniden doğrulama eklendi).
  Biçim kapısı (Task 9) bu beşi arar.
- **Sentez sözleşmesi:** her karar satırı `unit_id` + **`oge_yolu`** + **`oge_sha`** +
  `aktor` taşır; `guncelle` kararında kimlik KORUNUR, `cikar`+`ekle` çiftinde `ekle` satırı
  `yerine_gecer` taşır. **Yol ve hash üretimi sözleşmenin işidir** (bağımsız hakem itirazı:
  ilk sürüm yalnız kimliği istiyordu, dolayısıyla doğrulayıcının aradığı alanları hiçbir
  üretici doldurmuyordu).
- **Sentez sözleşmesi:** `tur: "not"` satır türü ve İKİ `sinif` değeri tanımlanır
  (`reddedilen-aday` = K-87 · `eslesmeyen-ozel-gun` = K-108).
- **Sentez sözleşmesi — K-107 (kısmi tur):** yalnız-özel-gün / tek-alan turunda değişmeyen
  HER birim kendi `karar="koru"` satırını alır (spec §3.5: *"sessiz taşıma yok"*);
  `kapsam="kismi-tur-tasima"` o satırın ek alanıdır, satırın yerine geçmez.
- **Sentez sözleşmesi — yöntem hükmü (K-85/K-153 AÇIK):** metni değişmiş kalıbın `guncelle`
  mi `cikar+ekle` mi olduğu **yürürlükteki iddia-düzeyi eşleştirmeyle** belirlenir (ADIM 1-2).
  Sözleşme yeni bir benzerlik ölçütü TANIMLAMAZ; **ayırt edilemeyen vaka açık soruya düşer**
  ve K-71 gereği aktivasyonu bloklar. Ölçüt (K-85) ve yöntem seçimi (K-153) açık ürün
  kararlarıdır — bu sürüm onları kapatmaz, mevcut durumu yazılı hâle getirir.

- [ ] **Step 1:** Denetçi sözleşmesine yeniden doğrulama adımını + beşinci çıktı bölümünü yaz.
- [ ] **Step 2:** Sentez sözleşmesine kimlik taşıması + not satırı türünü yaz.
- [ ] **Step 3:** Dış depoda commit: `docs(contracts): add re-verification inventory and unit identity carriage`
- [ ] **Step 4:** **Monorepo'ya dön**, pin manifestini yenile ve koş:
  `cd /root/otomaix/apps/social/backend && python -m pytest tests/test_contract_pin.py -v`
  — Beklenen: PASS (yeni hash'lerle).
- [ ] **Step 5:** Commit: `chore: repin research contracts at v2`

---

### Task 5: Migration 035 — takvim dönem desteği + üç takvim kalemi (K-147/K-01a/K-146)

**Files:**
- Create: `shared/db/migrations/035_holiday_periods.sql`
- Create: `shared/db/migrations/rollback/035_down.sql`
- Modify: `apps/social/backend/app/routers/calendar.py` (`get_holidays` dönem alanını döner)
- Modify: `shared/n8n-workflows/turkey-calendar-update.json` (yıllık iş üç kategoriden fazlasını yazar)
- Test: `apps/social/backend/tests/test_migration_035.py`

**Interfaces:**
- Consumes: mevcut `social.public_holidays` (`id`·`year`·`date`·`name_tr`·`name_en`·`category`,
  `UNIQUE(year, date)` — ölçüldü, `001_initial_social.sql:113`).
- Produces: `social.public_holidays.end_date DATE NULL` — dolu ise kayıt bir DÖNEMdir
  (`date`..`end_date`), boş ise tek gündür.

**Bağlayıcı invariantlar:**
- `end_date IS NULL OR end_date >= date` — CHECK kısıtı.
- `UNIQUE(year, date)` KORUNUR (dönem başlangıcı hâlâ benzersiz anahtardır).
- `normalize_special_day_key` davranışı DEĞİŞMEZ — eşleşme ada dayanır, tarihe değil;
  dönem desteği paket eşleşmesini etkilemez, yalnız takvim beslemesini ve gün seçimini.
- Üç yeni satır: **10 Kasım** (`anma`) · **24 Kasım Öğretmenler Günü** · **okula dönüş**
  (dönem — bitiş tarihi dolu).
- **Seed değerleri UYDURULMAZ — operatör kararıdır (bağımsız hakem itirazı, 2026-08-27).**
  Ölçüldü: takvim kaydı yıl alanını ZORUNLU tutuyor ve `(yıl, tarih)` ikilisi benzersiz.
  Plan üç satırın **adını** veriyordu ama yıl · kategori · kanonik ad · "okula dönüş"ün
  başlangıç/bitiş tarihlerini vermiyordu; uygulayıcı bunları icat etmek zorunda kalırdı —
  ve kategori değeri tür↔kategori çatışması kuralını (§11.2) doğrudan etkiler.
  **Bağlanan hüküm:** bu beş değer Step 1b'de operatöre sorulur (K-04a–d ile aynı sınıf:
  DB'ye yazımdan önce kapanan içerik kararı), karar `docs/active/`'e işlenir, migration
  onları **sabit** yazar.
- **Yıllık işin tekrar koşumu — CANLI DAVRANIŞLA ÇELİŞMEZ (bağımsız hakem itirazı,
  ölçüldü).** İlk yazım "mevcut satırı ezme" diyordu; **ölçüm** canlı yıllık işin bugün
  `ON CONFLICT (year, date) DO UPDATE SET name_tr, name_en, category` kullandığını gösterdi —
  yani ad/kategori düzeltmelerini **bilinçli olarak** güncelliyor. Benim kuralım o
  düzeltmeleri sessizce durdururdu.
  **Bağlanan hüküm:** mevcut ezme davranışı **AYNEN KORUNUR** (takvim beslemesi kanonik
  kaynaktır, düzeltme hakkı onundur). Migration'ın eklediği üç satır da aynı yoldan geçer;
  değişen tek şey **dönem alanının korunmasıdır** — güncelleme dönem bilgisini SIFIRLAMAZ.
  Yani kural "ezme" değil, "ezerken dönemi düşürme"dir.
- **Geri alma anlamı bozmaz (review turu düzeltmesi):** ilk yazım "kolon gider, mevcut
  satırlar durur" diyordu — ama *"okula dönüş"* satırının ANLAMI `end_date`'e bağlıdır;
  kolon düşünce o satır **035 öncesinde var olmayan** bir hâle, "tek günlük okula dönüş"e
  dönüşürdü. `035_down.sql` migration'ın KENDİ eklediği üç satırı geri alır (önceden var
  olan satırlara dokunmaz) — sahiplik sınırı açık yazılır.
- **Üretici şemayla birlikte sürümlenir:** `turkey-calendar-update.json` dönem-farkında
  yazıma geçiyor; geri alma o workflow'un önceki sürümüne dönmeyi de kapsar, yoksa eski
  şemaya yeni üretici yazmaya çalışır. Dağıtım/geri alma sırası Task 18'de listelenir.

- [ ] **Step 1:** **ÖLÇ (K-112, açık kalem):** takvim erişilemezken özel gün bloğunun
  bugünkü davranışını fixture ile ölç ve `docs/research/`'e tek paragraf not düş. Bulguya
  göre Task 12'nin özel gün kontrolü hizalanır. Ölçmeden bağlama.
- [ ] **Step 1b:** **Operatör kararı — seed değerleri (DB'ye yazımdan ÖNCE):** üç satırın
  yılı · kategorisi · kanonik adı; "okula dönüş" döneminin başlangıç ve bitiş tarihi.
  Uydurulmaz; karar `docs/active/`'e işlenir ve migration'a sabit girer.
- [ ] **Step 2:** Testleri yaz — `tests/test_migration_035.py`:
  `test_end_date_column_exists_and_nullable` · `test_check_rejects_end_before_start` ·
  `test_period_row_roundtrip` · `test_three_new_rows_present_and_normalize`
  (üç yeni satırın `normalize_special_day_key` çıktısı benzersiz) ·
  `test_rollback_removes_migration_owned_seed_rows` ·
  `test_rollback_preserves_pre_existing_rows` ·
  `test_up_down_up_on_mixed_row_set` (önceden var olan + migration'ın eklediği satırlar bir arada) ·
  `test_annual_job_still_corrects_name_and_category` (mevcut ezme davranışı korunuyor) ·
  `test_annual_job_update_preserves_period_field` (dönem sıfırlanmıyor) ·
  `test_reseeding_is_conflict_free`.
- [ ] **Step 3:** Koş: `cd apps/social/backend && python -m pytest tests/test_migration_035.py -v` — Beklenen: FAIL.
- [ ] **Step 4:** `035_holiday_periods.sql` + `rollback/035_down.sql` yaz; `calendar.py::get_holidays`
  SELECT listesine `end_date` ekle; n8n takvim işine üç kalemi işle.
- [ ] **Step 5:** Koş: `cd apps/social/backend && python -m pytest tests/test_migration_035.py -v` — Beklenen: PASS.
- [ ] **Step 6:** Koş: `cd apps/social/backend && python -m pytest tests/prompt_regression/ -v` — Beklenen: tek bayt fark YOK.
- [ ] **Step 7:** Commit: `feat: add holiday period support and three calendar entries`

---

### Task 6: Migration 036 — koşu kaydı · politika raporu · onay anlık görüntüsü · atama geçmişi

**Working directory:** `apps/social/backend` (test komutları); migration dosyaları repo kökünden.

**Files:**
- Create: `shared/db/migrations/036_package_runs.sql`
- Create: `shared/db/migrations/rollback/036_down.sql`
- Create: `shared/db/migrations/rollback/033_down.sql`, `shared/db/migrations/rollback/034_down.sql`
- Modify: `shared/db/migrations/032_sector_packages.sql` (kapalı-indeks beklentisi sürüm-farkında)
- Modify: `shared/db/migrations/033_package_events.sql` (pinlenmiş CHECK beklentisi sürüm-farkında)
- **Modify: `apps/social/backend/app/services/package_events.py`** — **K-99 ÜRETİCİSİ.**
  **Ölçüldü:** `EVENT_TYPES = BRAND_SCOPED_EVENTS | LIFECYCLE_EVENTS` ve
  `LIFECYCLE_EVENTS = frozenset({"activation","rollback","deactivation"})`;
  `log_package_event` bilinmeyen türü SQL'e varmadan reddeder. Yani **yalnız DB CHECK'ini
  genişletmek onay/ret olayını yazılabilir yapmaz** — Python üreticisi de genişlemek zorunda.
- Test: `apps/social/backend/tests/test_migration_036.py`

**Interfaces:**
- Consumes: `social.sector_packages` · `social.sector_research_artifacts` (032) ·
  `social.package_events` (033) · `social.brands`.
- Produces:
  - `social.sector_package_runs` — `id uuid PK` · `run_id text NOT NULL UNIQUE` ·
    `parent_run_id text NULL` (yeniden koşum bağı, K-83) · `sector_id uuid FK` ·
    `durum text NOT NULL` (`calisiyor` · `tamamlandi` · `tamamlanmadi` — K-82) ·
    `sonuc text NULL` (`activation_eligible` · `no_change` · `blocked` — yalnız
    `durum='tamamlandi'` iken dolu) · `sebep text NULL` (K-90) · `engine_version text` ·
    `engine_config_sha text` (K-97) · `policy_report jsonb` (K-95) ·
    `barrier_report jsonb NULL` (**K-24** — motorun ham değişim sayı/oranları) ·
    **CHECK: `durum='tamamlandi'` ise `barrier_report` NULL OLAMAZ** — üç sonucun üçünde de
    (`activation_eligible`·`no_change`·`blocked`) zorunlu. Bağımsız hakem itirazı: kolon
    yalnız nullable'dı ve servis parametresi varsayılan `None`'dı, yani tamamlanmış bir koşu
    hiç metrik yazmadan kaydedilebilirdi; mevcut testler verilen değerin saklandığını
    kanıtlıyordu, EKSİK değerin reddedildiğini değil · `final_candidate jsonb`
    (K-96) · `final_decision_log jsonb` (**F19** — motorun uyguladığı KANONİK karar günlüğü) ·
    `decision_log_sha text` (**F19** — günlüğün bütünlük hash'i) ·
    `engine_diff jsonb` (K-96) · `content_sha text` (K-92) ·
    `approval_snapshot jsonb NULL` (K-98) · `approval_karar text NULL` (`onay`/`ret`) ·
    `approved_at timestamptz NULL` · `approval_seconds int NULL` (K-42) ·
    `katman1_attestation jsonb NULL` (**F18** — hangi Katman-1 koşumu, sonucu, ne zaman) ·
    `readiness_attestation jsonb NULL` (**F18** — K-69 listesinin operatör onayı, kim/ne zaman) ·
    `katman2_attestation jsonb NULL` (**koşuldu + sunuldu kanıtı** — sonucu KAPI DEĞİL;
    spec §10.2: *"koşulması ve sunulması ön koşul, sonucu kapı değil"*) ·
    `snapshot_sha text NULL` (**F18** — onayın bağlandığı dondurulmuş görüntünün hash'i) ·
    `package_id uuid NULL` FK → `sector_packages(id)` (**benzersiz DEĞİL** — bkz. düzeltme
    soyağacı) · `duzeltilen_run_id uuid NULL` (**K-106 düzeltme hedefi**) ·
    `kosu_turu text NOT NULL` (`ilk` · `periyodik` · `duzeltme` — kapalı) ·
    `created_at`.
  - `social.package_rollback_plans` (**K-145**) — `incident_id` · `package_id` ·
    `observed_active_version` · `target_version int NULL` · `evidence_class` · `reason` ·
    `durum` (`bekliyor`/`tamamlandi`/`hata`/**`hedefsiz`**) · `created_at`.
    `UNIQUE (incident_id, package_id)` — tekrar güvenliğinin veri karşılığı.
    **`hedefsiz`in AÇIK veri karşılığı (iki yönlü CHECK):** `durum='hedefsiz'` ⇔
    `target_version IS NULL`. Hedefsizlik KALICI bir kayıttır, çalışma zamanı sezgisi
    DEĞİL — tekrar koşumda korunur ve yeniden hedef aranmaz.
  - `social.brand_sub_sector_history` — `brand_id` · `sub_sector_id` · `assigned_at` ·
    `unassigned_at NULL` (K-45 maruziyet kanıtı) **+ satırı YAZAN tetikleyici**.
  - `UNIQUE (run_id, source, kind)` on `sector_research_artifacts` (K-09).
  - `package_events` olay kümesi `approval` ve `rejection` ile genişler (K-99).

**Bağlayıcı invariantlar:**
- **`run_id` deneme başına KANONİK ve BENZERSİZDİR** — koşu satırı, artefakt, klasör adı ve
  paket `run_id` bağı hep aynı değeri taşır. İkinci bir `attempt` kimlik uzayı YOKTUR;
  yeniden koşum yeni `run_id` + `parent_run_id` alır (review turu düzeltmesi — bkz.
  teknik karar 23).
- `durum` ve `sonuc` AYRI kolonlardır: `durum` yürütmenin hâli, `sonuc` motorun çıktısı.
  `durum != 'tamamlandi'` iken `sonuc` NULL olmak ZORUNDA (CHECK).
- `sonuc` üç değerle kapalı (K-90 birleştirmesi — dördüncü değer yok).
- **`approval_snapshot` değişmezdir (K-98):** tetikleyici `OLD.approval_snapshot IS NOT NULL`
  iken o kolonun DEĞİŞTİRİLMESİNİ reddeder; `approval_karar`/`approved_at`/`approval_seconds`
  güncellenebilir.
- **K-45 üretici ZORUNLU (review turu düzeltmesi):** geçmiş tablosunu **hiçbir şey yazmıyorsa**
  Task 16 onu maruziyet kanıtı olarak tüketemez. `brands.sub_sector_id` değişimini yakalayan
  bir **tetikleyici** aynı işlemde açık aralığı kapatır ve yenisini açar — atama yolu hangi
  koddan geçerse geçsin. Bilinmeyen geçmiş retroaktif "bakım tamamlandı" ÜRETMEZ
  (geri doldurma YOK; geçmişsiz marka bildirim almaz).
- **Donmuş sözleşmelere dokunuş — ölçülmüş ve bilinçli:** 032 (satır 419-420)
  `sector_research_artifacts` indeks kümesini, 033 (satır 115/184) `package_events` CHECK
  metnini **tam metinle** pinliyor. Her ikisi de **sürüm-farkında** hâle getirilir: eski
  beklenti (o migration tek başına uygulandığında) geçerli KALIR, 036 sonrası genişlemiş
  hâl de kabul edilir; **adı geçmeyen fazladan indeks / tanınmayan olay türü hâlâ REDDEDİLİR**
  — kapalılık vaadi zayıflamaz.
- 033/034 geri alma script'lerinin yokluğu **Plan 1'den devralınan gerçek boşluktur**
  (ölçüldü: `shared/db/migrations/rollback/` yalnız `032_down.sql` içeriyor) — bu görevde
  kapatılır, çünkü Plan 2'nin geri alma anlatısı onlara dayanıyor.
- **Bir koşu → bir taslak (idempotency, review turu 3; kardinalite turu 4'te düzeltildi).**
  `insert_draft` her çağrıda
  `MAX(version)+1` ayırıp yeni satır yazar; `sector_packages.run_id` ise 032'de nullable ve
  benzersiz DEĞİL. Yani cevabı kaybolmuş bir yazım tekrar denendiğinde ya da iki çağrı
  eşzamanlı geldiğinde **aynı koşudan birden çok taslak sürümü** doğardı ve aktivasyonun
  koşu→paket doğrulaması belirsizleşirdi. **Bağlanan hüküm:** `sector_package_runs.package_id`
  yazım işleminde doldurulur ve koşu satırı KİLİTLİ okunduğu için ikinci çağrı yeni sürüm
  yakmaz, mevcut taslağı döndürür.
  **Kolon BENZERSİZ DEĞİLDİR (tur 4 düzeltmesi).** İlk denemede `UNIQUE` koymuştum; ölçüldü
  ki bu istediğimin TERSİNİ zorluyor: bir koşu satırı zaten en fazla bir `package_id`
  taşıyabilir, dolayısıyla `UNIQUE` "bir koşu → bir taslak" değil **"bir taslak → bir koşu"**
  demek olur. Ve o kısıt K-106'yı **imkânsız** kılardı: düzeltme turu K-72 gereği yeni bir
  koşudur, K-83 gereği yeni bir `run_id` alır, ama K-106 gereği AYNI taslağı güncellemek
  zorundadır — hedef taslak ana koşu tarafından tutulduğu için kısıt ihlal olurdu.
  Tekilliği kısıt değil **kilit + dolu kolon** sağlar.
- **Düzeltme soyağacı ZORUNLU:** `duzeltilen_run_id` + `kosu_turu`. Tek CHECK:
  `kosu_turu='duzeltme'` ⇔ `duzeltilen_run_id` dolu.
  **Karşılıklı dışlama KALDIRILDI (tur 5 düzeltmesi).** İlk denemede `parent_run_id`
  (yeniden koşum) ile `duzeltilen_run_id` (düzeltme) aynı anda dolu olamaz demiştim; bu,
  **yarıda kalmış bir düzeltmenin kurtarılmasını imkânsız** kılıyordu: K-82 onu
  `tamamlanmadi` işaretler, K-83 yeniden koşuma yeni `run_id` verir — ama o yeniden koşum
  hem `parent_run_id` hem düzeltme soyağacı taşımak zorundadır, yoksa güncelleme yolu onu
  reddeder ya da yazma yolu ikinci bir sürüm yakar. İkisi **dik ilişkilerdir**, birlikte
  bulunabilirler. **Bağlanan hüküm:** bir düzeltme koşusunun yeniden koşumu ana koşusundan
  `kosu_turu` · `duzeltilen_run_id` · `package_id` üçünü **DEVRALIR**; hedef tutarlılığı
  (devralınan üçlü ana koşununkiyle aynı mı) servis katmanında zorlanır. Bağın `sector_packages` tarafında olmama sebebi ölçülmüştür (032 satır 421-422 o
  tablonun kısıt kümesini tam metinle pinliyor).
- **F19 — karar günlüğü de kökeninden okunur:** `write_draft_from_run` çağırandan nesne
  kabul etmediği için, `insert_draft`'a verilecek karar günlüğünün de DB'de duruyor olması
  ZORUNLUDUR. Aksi hâlde ya boş/Plan-1 yer tutucu günlük ya ham sentez günlüğü yazılırdı ve
  K-25 aktör ayrımı · K-84 kimlik izi · K-96 üçlü saklama · K-145 geri alma etki alanı
  aktif içerikten KOPARDI. `final_decision_log` + `decision_log_sha` bu yüzden içerikle
  **aynı işlemde** yazılır; ikisi ayrı yazılamaz.
- **F18 — kapı tasdikleri kanıttır, boolean değil.** Plan 1'in kanıt sınıfı `katman1_passed`
  ve `checklist_approved` alanlarını olduğu gibi KABUL EDER — yani onları kim ölçtü sorusunun
  cevabı Plan 2'de olmalı. `katman1_attestation` ve `readiness_attestation` o cevabı kalıcı
  kılar: hangi koşum, hangi sonuç, kim, ne zaman. Aktivasyon bu satırlardan okur; adaptörün
  boolean **uydurabileceği** yol kapanır.
- **F20 — 036 geri alması VERİ VARKEN fail-closed durur.** İlk yazım yalnız "şekil geri
  dönüyor mu" diye soruyordu; ama pilot bir `approval`/`rejection` olayı ürettikten sonra
  `package_events` CHECK'ini daraltmak mevcut satır yüzünden ZATEN başarısız olur, satırları
  silmek ise denetim izini yok eder. Aynısı koşu kayıtları ve atama geçmişi için geçerli.
  **Bağlanan hüküm:** `036_down.sql` başında atomik bir ön kontrol koşar — Plan 2 verisi
  (koşu satırı · onay/ret olayı · geçmiş aralığı) VARSA `rc≠0` ile DURUR ve hiçbir şeye
  dokunmaz. Pilot sonrası geri dönüş **şema geri alması değil, veri-koruyan ileri düzeltme
  migration'ıdır**; runbook ikisini ayrı başlıkta yazar (032'nin veri-varken fail-closed
  disiplininin 036'ya taşınması).

- [ ] **Step 1:** Testleri yaz — `tests/test_migration_036.py`:
  `test_runs_table_shape_and_closed_result_enum` · `test_run_id_unique_across_attempts` ·
  `test_parent_run_id_links_retry` · `test_sonuc_null_unless_completed` (CHECK) ·
  `test_approval_snapshot_update_rejected_when_set` (kapı) ·
  `test_approval_snapshot_first_write_allowed` (pozitif kontrol) ·
  `test_approval_decision_columns_still_updatable` (aşırı-kilitleme yok) ·
  `test_artifacts_unique_run_source_kind_rejects_duplicate_upload` (K-09) ·
  `test_package_events_accepts_approval_and_rejection` (K-99 pozitif kontrol) ·
  `test_package_events_still_rejects_unknown_type` (kapalılık korundu) ·
  `test_history_trigger_opens_and_closes_interval_on_assignment_change` (K-45 üretici) ·
  `test_history_trigger_fires_regardless_of_writing_code_path` ·
  **F19:** `test_final_decision_log_and_sha_written_atomically` ·
  `test_content_written_without_decision_log_rejected` ·
  **F18:** `test_attestation_columns_present_and_nullable` ·
  **K-24:** `test_barrier_report_column_present` ·
  **K-145:** `test_rollback_plan_unique_incident_package` ·
  `test_hedefsiz_requires_null_target_version` (CHECK, iki yönlü) ·
  `test_non_hedefsiz_requires_target_version` ·
  `test_snapshot_sha_column_present` ·
  **K-99 üretici:** `test_log_package_event_accepts_approval_and_rejection` (Python kapısı) ·
  `test_log_package_event_still_rejects_unknown_type` ·
  **idempotency + soyağacı:** `test_package_id_is_not_unique` (kardinalite kapısı) ·
  `test_correction_run_may_share_package_id_with_parent` (K-106 mümkün olmalı) ·
  `test_kosu_turu_and_duzeltilen_run_id_check_consistent` ·
  `test_retry_of_correction_may_carry_both_links` (NEW-2 — dışlama YOK) ·
  `test_retry_of_correction_inherits_target_and_type` ·
  `test_second_write_for_same_run_returns_existing_draft` ·
  `test_concurrent_write_for_same_run_yields_one_draft` ·
  **F20:** `test_036_down_refuses_when_run_rows_exist` ·
  `test_036_down_refuses_when_approval_events_exist` ·
  `test_036_down_refuses_when_history_intervals_exist` ·
  `test_036_down_leaves_everything_untouched_on_refusal` (bayt-bayt) ·
  `test_036_down_succeeds_on_empty_plan2_data` (pozitif kontrol).
- [ ] **Step 2:** Migration matrisi testlerini yaz (donmuş sözleşme uyumu):
  `test_clean_001_to_032_expectations_unchanged` · `test_full_001_to_036` ·
  `test_032_reapply_after_036_passes` · `test_033_reapply_after_036_passes` ·
  `test_036_down_then_032_and_033_reapply` ·
  `test_unnamed_extra_index_still_rejected` (kapalılık vaadinin pozitif kontrolü) ·
  `test_rollback_036_restores_prior_shape` · `test_rollback_033_and_034_restore_prior_shape`.
- [ ] **Step 3:** Koş: `cd apps/social/backend && python -m pytest tests/test_migration_036.py -v`
  — Beklenen: FAIL.
- [ ] **Step 4:** `036_package_runs.sql` + üç down script'i yaz; 032/033'ün pinlenmiş
  beklentilerini sürüm-farkında hâle getir.
- [ ] **Step 5:** Koş: `cd apps/social/backend && python -m pytest tests/test_migration_036.py -v`
  — Beklenen: PASS.
- [ ] **Step 6:** Koş: `cd apps/social/backend && python -m pytest tests/ -v` — Beklenen:
  regresyon YOK (özellikle `test_migration_032.py` · `test_migration_033.py` ·
  `test_plan2_interface_contract.py`).
- [ ] **Step 7:** Commit: `feat: add run/policy/approval tables and missing down scripts`

---

### Task 7: `brief-doctor` mekanik girdi kapısı

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/brief_doctor.py`
- Test: `apps/social/backend/tests/test_brief_doctor.py`

**Interfaces:**
- Consumes: Task 2 pinlenmiş `_SABLON.md` çıktı sözleşmesi.
- Produces:
  - `brief_doctor.CHECKS: tuple[Check, ...]` — **dondurulmuş demet** (K-89); kontrol
    eklemek sözleşme revizyonu ister.
  - `brief_doctor.run(source_text: str, *, source_name: str) -> DoctorReport` —
    `DoctorReport(sonuc, notlar, elemeler)`; `sonuc` ∈ {`gecti`,`notlu-gecti`,`elendi`}.
  - `brief_doctor.gate_round(reports: list[DoctorReport]) -> RoundGate` — K-127 kaynak
    tabanı kapısı.

**Bağlayıcı invariantlar (K-88 eşlemesi — seam: `brief_doctor.py::CHECKS`):**
- Her kontrol **açıkça** `eleme` veya `not` üretir. Varsayılan `not`tur.
- Bugün eleme üreten kontrol kümesi: **BOŞ.** Adet alt sınırları (cta ≥5 · kanca ≥3 ·
  görsel kod ≥20 · video kodu ≥10 · dönem ≥6; dönem başına kanca ≥2 · cta ≥2 ·
  gorsel_vurgu ≥5) ölçülmemiş sözleşme kurallarıdır → hepsi `not` (İlke 9 uyum hükmü,
  spec §8.3).
- "40+ kelime alıntı" → `not` (sözleşmenin tek açık eşlemesi).
- **Koşu kapısı (K-127=2):** geçerli kaynak sayısı 2'nin altına düşerse `gate_round`
  `dur=True` döner ve yöneticiye bildirilir. Bu kaynak-SAYISI kapısıdır, içerik eşiği değil.
- **K-120:** `içerik-önerilmez` resmî değeri doluluk kontrolünü "bilinçle boş" sayıp geçirir;
  diğer günlerde alt sınır denetimi aynen sürer.
- Beş bölümlü çıktı biçimi zorunlu; **fazladan bölüm** → `not` (biçim ihlali).

- [ ] **Step 1:** Testleri yaz — `tests/test_brief_doctor.py`:
  `test_clean_source_passes` (pozitif kontrol) · `test_count_shortfall_produces_note_not_elimination`
  (İlke 9 kapısı — bu test ölçülmemiş sayının kapıya dönmesini engeller) ·
  `test_icerik_onerilmez_passes_fill_check` · `test_long_quote_produces_note` ·
  `test_extra_section_produces_note` · `test_round_gate_stops_below_two_sources` ·
  `test_round_gate_allows_exactly_two_sources` (pozitif kontrol) ·
  `test_checks_tuple_is_frozen` (K-89 — demet değiştirilemez).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_brief_doctor.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `brief_doctor.py` yaz.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_brief_doctor.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add mechanical brief-doctor input gate`

---

### Task 8: Koşu ve artefakt servisi (K-09/K-17/K-80/K-82/K-83/K-93)

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/runs.py`
- Test: `apps/social/backend/tests/test_pipeline_runs.py`

**Interfaces:**
- Consumes: migration 036 tabloları; `contracts.require_pin`.
- Produces:
  - `runs.open_run(db, *, sector_id, run_id, parent_run_id=None) -> UUID`
  - `runs.record_artifact(db, *, run_id, sector_slug, kind, source, content_md, brief_ref=None) -> UUID`
  - `runs.mark_incomplete(db, *, run_id, asama, sebep) -> None` (K-82 — `durum='tamamlanmadi'`)
    **`asama` kapalı kümedir:** `brief-doctor` · `kaynak-tabani` · `denetim` · `sentez` ·
    `motor`. Parametre ZORUNLUDUR (bağımsız hakem itirazı: bildirim anahtarı "koşu + aşama"
    diye tanımlanmıştı ama imzada aşama yoktu — anahtar üretilemezdi).
    **+ YÖNETİCİ BİLDİRİMİ:** aynı işlemde `record_admin_event`
    ile `sektor_paketi.tur_arizasi` olayı yazar; `idempotency_key` = `run_id` + `asama`.
    n8n `errorWorkflow` yalnız **workflow'un kendi** arızasını yakalar — yerel CLI
    zaman aşımı, sıfırdan farklı çıkış ya da K-127 kaynak-tabanı duruşu ORAYA HİÇ ULAŞMAZ.
    Bu yol olmadan yarım tur yalnız veritabanında ve günlükte kalırdı.
    Olay yükü **maskeleme süzgecinden** geçer (K-136).
  - `runs.new_retry_run_id(db, *, parent_run_id) -> str` — YENİ bir `run_id` üretir ve
    `parent_run_id` ile ilkine bağlar (K-83). Sonek üreten `next_attempt` KALDIRILDI:
    ikinci bir kimlik uzayı açıyordu.
  - `runs.record_result(db, *, run_id, sonuc, barrier_report, sebep=None,
    final_candidate=None, final_decision_log=None, **report_fields) -> None`
    **`barrier_report` ZORUNLU** (varsayılanı YOK — K-24 kapısı).
    **K-24 eşlemesi AÇIK:** `engine.decide` çıktısındaki `barrier_report` buraya adı konmuş
    bir parametreyle geçer ve koşu satırına yazılır (bağımsız hakem itirazı: ilk yazımda
    yalnız genel `**report_fields`'e düşüyordu, yani hangi alanın nereye gittiği tanımsızdı
    ve kalıcılığı hiçbir test kanıtlamıyordu).
    — **`no_change`/`blocked` dahil HER koşu satır yazar** (K-93), paket satırı üretmeden.
    **F19:** `activation_eligible` sonuçta içerik ve karar günlüğü ile hash'leri
    **aynı işlemde** yazılır; biri eksikse yazım REDDEDİLİR (yarım köken kaydı yok).
  - `runs.run_folder(run_id: str) -> Path` — `<arastirma-deposu>/kosu/<run_id>/` (K-17).
  - **`runs.load_verified_run(db, *, run_id, for_update=True) -> VerifiedRun`** — koşu
    satırını kilitli okuyan ve YEDİ kapının tamamını uygulayan **TEK** doğrulayıcı
    (bkz. "TEK KAPI LİSTESİ"). Yazım · güncelleme · onay · aktivasyon dördü de bunu çağırır;
    kapılardan biri düşerse `RunNotVerified`.
  - **`runs.open_correction_run(db, *, parent_run_id, actor) -> str`** (**K-106/K-72**) —
    reddedilmiş ana koşuyu kilitler, `approval_karar='ret'` değilse REDDEDER, `package_id`'sini
    kopyalar, `kosu_turu='duzeltme'` + `duzeltilen_run_id` yazar ve YENİ bir `run_id` döndürür.
  - **`runs.mask_secrets(text: str) -> str`** ve maskeleme süzgeçli günlük yazıcısı
    (**K-136**) — bağımsız hakem itirazı (2026-08-27): karar yalnız evrensel kısıt olarak
    duruyordu, onu uygulayan dosya · arayüz · test YOKTU. Süzgeç **hata mesajlarını ve alt
    süreç stderr'ini de** kapsar (sızıntının en olası yeri orasıdır) ve günlüğe yazan HER
    yol ondan geçer.
  - **`runs.affected_packages(db, *, engine_version, engine_config_sha, kural_kimligi,
    kural_surumu) -> AffectedSet`** (**K-145**) — bir kural SÜRÜMÜNÜN etkilediği **aktif**
    paketleri döner; **sektör başına en fazla bir satır.** **Motorda DEĞİL burada**: motor saf kalır, bu fonksiyon koşu kayıtlarını okur.
    **Olay girdisi kapalı DÖRTLÜDÜR:** `engine_version` · `engine_config_sha` ·
    `kural_kimligi` · `kural_surumu`. Dördü de zorunludur — sürüm olmadan aynı kuralın iki
    sürümü ayrışmaz ve doğru sürümle üretilmiş paketler de geri alınırdı.
    **EVREN — AKTİF paketler üzerinden kurulur (iki kusur birden düzeltildi).**
    İlk yazım evreni *"motor damgasını taşıyan HER paket"* diye tanımlıyordu; iki ayrı şekilde
    kırıktı:
    *(a) Kendi kendiyle çelişiyordu:* evren "koşu satırı olan ve `package_id` dolu" paketlerle
    sınırlıydı, ama `ayrilamaz` sınıfı tam da *"koşu satırı yok"* ve *"`package_id` boş"*
    vakalarını sayıyordu. O vakalar evrene hiç giremediği için `ayrilamaz` asla dolmuyordu —
    yani **güvenli genişleme, var olduğu durumda hiç ateşlenmiyordu.**
    *(b) Paket durumunu sınırlamıyordu:* damgalı her paket (aktif · arşivlenmiş · taslak)
    evrene giriyordu. Oysa geri alma **mevcut aktif sürüm** üzerinde çalışır; aynı sektörün
    birden çok tarihî sürümü ayrı plan satırlarına dönüşür ve ilk geri almadan sonra
    kalanlar sürüm karşılaştırmasında düşerdi.

    **Bağlanan tanım:** aday küme = **aktif paketi olan HER sektörün o aktif paketi**
    (sektör başına tam bir satır; arşivlenmiş ve taslak sürümler evrene GİRMEZ — onlar hedef
    olabilir, konu olamaz). Her aday paket için köken, kendi `run_id` bağından okunur:

    · **`kanitli`** — köken okunabilir (koşu satırı var · `durum='tamamlandi'` · günlük
      okunabilir), koşu arızalı motor damgasını taşıyor **ve** uygulanmış motor kararlarından
      en az biri `kural_kimligi` + `kural_surumu` ikilisiyle damgalı (karar türü fark etmez).
    · **`kanitli_etkilenmemis`** — köken okunabilir **ve** ya koşu o motor damgasını hiç
      taşımıyor ya da o ikiliyle damgalı hiçbir uygulanmış motor kararı yok.
    · **`ayrilamaz`** — **köken okunamıyor:** paketin `run_id` bağı yok · koşu satırı yok ·
      `durum != 'tamamlandi'` · günlük okunamıyor. Bu vakalar artık evrenin İÇİNDE, çünkü
      evren kökene değil **aktif olmaya** dayanıyor. Etkilenmediği KANITLANAMADIĞI için
      güvenli tarafa düşer.

    **`ayrilamaz` boş DEĞİLSE küme ADAY KÜMENİN TAMAMINA genişler** — yani her sektörün aktif
    paketi. Kanonik kayıt bunu böyle bağlıyor: *"ayrım yapılamadığı anda davranış koşulsuz
    toplu geri almayla AYNIdır"* (spec-input satır 2895). Faz 1'de aday küme küçüktür.
  - **`runs.build_rollback_plan(db, *, affected: AffectedSet, actor) -> str`** — DEĞİŞMEZ
    bir geri alma planı yazar ve **olay kimliğini** döner. **Sektör başına TEK giriş** —
    aday küme aktif paketlerden kurulduğu için tarihî sürümler ayrı satır üretmez. Her giriş:
    `{package_id, observed_active_version, target_version, evidence_class, reason}`.
    **Hedef sürüm plan anında SABİTLENİR** (tekrar denemede yeniden hesaplanırsa ikinci kez
    geri alma riski doğar).
    **GÜVENLİ HEDEF — iki koşul birden:** hedef, o sektörün (1) `status='archived'` olan **ve**
    (2) arızalı kural sürümüyle damgalanmamış **en yüksek** sürümüdür.
    ⚠️ **Arşivlenmişlik koşulunun gerçek riski (ölçüldü):** onaylanmamış bir taslağın aktive
    edilmesi bu yoldan MÜMKÜN DEĞİL — Plan 1'in geri alma yordamı hedefin durumunu okuyup
    `archived` değilse hata veriyor (`sector_package_lifecycle.py::rollback_package`).
    Buradaki kusur daha küçük ama gerçek: **planlayıcı hedefi kısıtlamazsa yürütme anında
    ölecek bir plan satırı yazar.** Koşulamayan plan üreten planlayıcı kabul edilmez.
    **Güvenli sürüm YOKSA satır `hedefsiz` yazılır** — `target_version` NULL, `evidence_class`
    korunur, `reason` sebebi taşır. Geri alma UYDURULMAZ; tek çıkış deaktivasyondur (K-38).
  - **`runs.execute_rollback_plan(db, *, incident_id, actor) -> RollbackReport`** — planı
    **paket paket** yürütür (toplu-atomik mekanizma YOK). Her paket kendi işleminde,
    `observed_active_version` karşılaştır-ve-uygula ile; sonucu plan satırına yazılır.
    **Tekrar güvenli:** tamamlanmış satır atlanır, hedef YENİDEN HESAPLANMAZ.
    **`hedefsiz` satır HATA ÜRETMEDEN atlanır** ve `durum='hedefsiz'` olarak kalır; tekrar
    koşumda aynı sonucu korur (yeniden hedef aranmaz). Rapor onu ayrı sayar.
  - **`runs.attest_katman2(db, *, run_id, kosum_kimligi, ozet, actor) -> None`** —
    Katman-2'nin koşulduğu ve sunulduğu kanıtı; sonucu kapı DEĞİL.
  - **`runs.attest_katman1(db, *, run_id, kosum_kimligi, sonuc, actor) -> None`** (**F18**) —
    Katman-1 tasdikinin ADLANDIRILMIŞ üreticisi. Tur 3'te bu üreticinin adı yoktu, yani
    tasdik alanını kimin dolduracağı belirsizdi. CLI'nin Katman-1 adımı bunu çağırır.

**Bağlayıcı invariantlar (seam: `runs.py::record_artifact`):**
- Ham katman **salt-ekleme** — DB tetikleyicisi (032) zaten zorluyor; servis `UPDATE`
  denemez, deneseydi DB reddederdi (test bunu kanıtlar).
- **K-09:** aynı `(run_id, source, kind)` ikinci kez yazılamaz → benzersizlik ihlali.
- **K-80 tekrar-üretilebilirlik damgası ZORUNLU:** her artefakt satırı `source` alanında
  model/sürüm/tarih/girdi-özeti taşır; eksikse yazım REDDEDİLİR.
- **K-82:** yarım koşu `mark_incomplete` ile işaretlenir; dosya EZİLMEZ.
- Koşu klasörü adı DB `run_id`'sine EŞİTTİR (K-17).

- [ ] **Step 1:** Testleri yaz — `tests/test_pipeline_runs.py`:
  `test_open_run_and_record_artifact` (pozitif kontrol) ·
  `test_duplicate_artifact_rejected` (K-09) · `test_artifact_update_rejected_by_db` ·
  `test_stamp_missing_rejects_write` (K-80) · `test_mark_incomplete_preserves_row` ·
  `test_retry_gets_new_run_id_linked_by_parent` · `test_no_attempt_parameter_anywhere` · `test_no_change_run_recorded_without_package_row` (K-93) ·
  `test_load_verified_run_passes_on_complete_run` (pozitif kontrol) ·
  `test_load_verified_run_rejects_each_of_seven_gates` (kapı başına bir vaka) ·
  `test_load_verified_run_takes_row_lock` ·
  `test_attest_katman1_persists_run_and_result` (F18) ·
  `test_attest_katman2_persists_run_and_presentation` ·
  **K-24:** `test_barrier_report_persisted_for_all_three_outcomes` ·
  `test_completed_run_without_barrier_report_is_rejected` (eksik değer kapısı) ·
  `test_barrier_report_round_trip_matches_engine_output` ·
  **K-145 — evren ve sınıflandırma:** `test_universe_is_active_packages_only` ·
  `test_archived_and_draft_versions_not_in_universe` ·
  `test_mixed_active_draft_archived_fixture_yields_one_row_per_sector` ·
  `test_package_without_run_link_is_ayrilamaz` (evrene GİRER — eski tanımda giremiyordu) ·
  `test_package_with_missing_run_row_is_ayrilamaz` ·
  `test_incomplete_run_is_ayrilamaz` ·
  `test_unseparable_expands_to_all_active_packages` ·
  `test_cikar_decision_makes_package_kanitli` (yaşayan kümede YOK ama etkilenmiş) ·
  `test_kirp_decision_makes_package_kanitli` ·
  `test_same_rule_different_version_not_matched` (dörtlünün sürüm ayağı) ·
  `test_affected_set_separates_proven_and_unprovable` ·
  `test_proven_unaffected_not_in_any_rollback_set` ·
  **K-145 — hedef seçimi ve hedefsiz:** `test_rollback_plan_freezes_target_version` ·
  `test_target_is_highest_archived_version_without_faulty_stamp` ·
  `test_clean_draft_is_never_chosen_as_target` (planlayıcı koşulamayan satır yazmaz) ·
  `test_no_safe_archived_version_yields_persisted_hedefsiz_row` ·
  `test_executor_skips_hedefsiz_without_error` ·
  `test_rerun_preserves_hedefsiz_outcome` (yeniden hedef aranmaz) ·
  `test_execute_plan_skips_completed_entries_on_retry` (ikinci geri alma YOK) ·
  `test_execute_plan_cas_rejects_when_active_version_moved` ·
  **yerel arıza bildirimi:** `test_mark_incomplete_writes_admin_event` ·
  `test_admin_event_idempotent_per_run_and_stage` ·
  `test_mark_incomplete_requires_stage` · `test_stage_values_are_closed` ·
  `test_admin_event_payload_is_masked` ·
  **K-136:** `test_mask_filter_redacts_secret_shaped_values` ·
  `test_mask_filter_applies_to_error_messages` ·
  `test_mask_filter_applies_to_subprocess_stderr` ·
  `test_log_writer_cannot_bypass_mask_filter` (yapısal) ·
  `test_mask_filter_preserves_event_trace` (olay izi korunur — aşırı maskeleme yok) ·
  `test_open_correction_run_copies_package_target` (K-106 pozitif kontrol) ·
  `test_open_correction_run_refuses_non_rejected_parent` ·
  `test_open_correction_run_refuses_parent_without_decision` ·
  `test_open_correction_run_refuses_second_open_correction` (NEW-3) ·
  `test_open_correction_run_allowed_after_correction_rejected` (zincir sürebilir) ·
  `test_open_correction_run_allowed_after_correction_incomplete` ·
  `test_concurrent_open_correction_single_winner` ·
  `test_crashed_correction_retry_updates_same_draft` (NEW-2 uçtan uca) ·
  `test_blocked_run_recorded_with_reason` (K-90).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_pipeline_runs.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `runs.py`'yi yaz — koşu/artefakt yüzeyleri · `load_verified_run` ·
  `mask_secrets` + maskeleme süzgeçli günlük yazıcısı · `attest_katman1` · `attest_katman2` ·
  `open_correction_run` · **`affected_packages`** · **`build_rollback_plan`** ·
  **`execute_rollback_plan`** · `mark_incomplete`'in yönetici bildirimi ayağı.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_pipeline_runs.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add run and artifact service with append-only guarantees`

---

### Task 9: Denetçi girdi paketleyici — anonimleştirme · biçim kapısı · ön kontrol

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/auditors.py`
- Test: `apps/social/backend/tests/test_auditor_packaging.py`

**Interfaces:**
- Consumes: Task 4 sözleşme v2; Task 7 `DoctorReport`; Task 8 `runs`.
- Produces:
  - `auditors.build_packet(*, brief, sources, doctor_reports, active_package, dest: Path) -> PacketRef`
    — bayt-özdeş girdi kopyası + hash (K-79).
  - `auditors.anonymize(text: str) -> str` (K-137).
  - `auditors.validate_report(text: str, *, unit_snapshot: dict[str, dict]) -> list[str]` —
    beş bölümlü biçim kapısı (K-81) **+ K-100 veri sözleşmesi kapısı**.
  - `auditors.preflight(tool: str) -> PreflightResult` (K-14).

**Bağlayıcı invariantlar (seam: `auditors.py::anonymize`):**
- **K-137 yapısal garanti:** pakette araç kimliği BULUNMAZ — dosya adları `KAYNAK-1/2/3`,
  talimat metni ve rapor gövdesi dahil. Anonimleştirme kod düzeyindedir.
- **K-79:** iki denetçinin girdi kopyaları **bayt-özdeştir**; hash'leri koşu kaydına yazılır.
- **K-81 biçim kapısı:** beş bölüm (Task 4 sonrası) eksikse rapor GEÇERSİZ.
- **K-100 VERİ kapısı — biçim kapısından AYRI (review turu düzeltmesi):** ilk yazım yalnız
  "beş bölüm var mı" diye bakıyordu; bu **bölüm-varlığı** kontrolüdür, envanterin kendisini
  denetlemez. Eksik envanter, motorun mutabakat kapısına "uyum" gibi görünürdü.
  `validate_report` ayrıca şunları ZORLAR: her satır dört alanlı
  (`unit_id`·`statu`·`kanit`·`gerekce`) · `statu` beş değerden biri · **aktif paket anlık
  görüntüsündeki HER `unit_id` tam bir kez** · tanınmayan kimlik YOK · tekrar YOK ·
  iki denetçi **AYNI anlık görüntüye** karşı raporlamış (snapshot hash'i eşleşir, K-79).
  Biri bile ihlal edilirse rapor GEÇERSİZ → sentez başlamaz (K-150 yolu).
- **K-14 ön kontrol fail-closed:** Denetçi-2'nin web erişimi sınanır; başarısızsa tur BAŞLAMAZ.
- **URL örneklem yazımı koşulludur** (Task 2/5. düzeltme): sabit "dokuz satır" beklenmez —
  kalan kaynak sayısı × 3.

- [ ] **Step 1:** Testleri yaz — `tests/test_auditor_packaging.py`:
  `test_packet_bytes_identical_for_both_auditors` · `test_packet_contains_no_tool_identity`
  (araç adları için negatif tarama) · `test_anonymize_strips_tool_names` ·
  `test_validate_report_requires_five_sections` · `test_validate_report_accepts_valid_report`
  (pozitif kontrol) · `test_validate_report_url_sample_count_is_conditional` ·
  `test_preflight_failure_blocks_round` · `test_preflight_success_allows_round` (pozitif kontrol) ·
  **K-100 veri kapısı:** `test_inventory_requires_four_fields` (`gerekce` eksikse RED) ·
  `test_inventory_rejects_missing_unit` · `test_inventory_rejects_duplicate_unit` ·
  `test_inventory_rejects_unknown_unit` · `test_inventory_rejects_invalid_status` ·
  `test_inventory_rejects_divergent_snapshot_hash` ·
  `test_complete_inventory_accepted` (pozitif kontrol).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_auditor_packaging.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `auditors.py`'ın paketleyici/anonimleştirici/kapı/ön-kontrol yüzeylerini yaz.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_auditor_packaging.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add auditor packet builder with blindness and format gates`

---

### Task 10: İki kör denetçi orkestrasyonu (K-76/K-78/K-150)

**Files:**
- Modify: `apps/social/backend/app/services/sector_pipeline/auditors.py`
- Test: `apps/social/backend/tests/test_auditor_orchestration.py`

**Interfaces:**
- Consumes: Task 9 yüzeyleri.
- Produces:
  - `auditors.run_audit_round(db, packet: PacketRef, *, runner: Runner, run_id: str) -> AuditRound` —
    `AuditRound(reports: list[AuditReport], gecerli: bool, sebep: str | None)`.
    **`db` ve `run_id` public imzada ZORUNLU** (bağımsız hakem itirazı: alt açıklama
    `run_id` ekliyor ve `runs.mark_incomplete(db, ...)` çağırıyordu, ama imzada ikisi de
    yoktu — sözleşme kendi kendiyle çelişiyordu).
  - `Runner` protokolü: `run(tool: str, cwd: Path, prompt_path: Path) -> RunnerOutcome` —
    **test edilebilirlik dikişi**; gerçek koşumda yerel CLI alt süreci, testte sahte runner.
  - `RunnerOutcome(durum, stdout, stderr, exit_code)` — `durum` ∈ {`tamam`, `zaman-asimi`,
    `hata`}, kapalı. **Ham metin DÖNMEZ** (ilk yazım `-> str` diyordu, hemen ardından tipli
    sonuç istiyordu).
  - **`auditors.SubprocessRunner`** — protokolün GERÇEK uygulaması (bağımsız hakem itirazı,
    2026-08-27: ilk yazımda yalnız protokol ve sahte runner vardı; hiçbir görev gerçek
    çalıştırıcıyı üstlenmiyordu, yani resmî hat uygulanamazdı). Sözleşmesi:
    araç başına **kesin komut satırı**, kapalı bir `ToolSpec` eşlemesinde SABİT:
    `denetci-1` → Claude Code · `denetci-2` → Codex · **`sentez`** → sentez oturumu
    (Task 11 aynı `Runner`'ı kullanıyor; ilk yazım yalnız iki denetçiyi sayıyordu).
    **Argüman listeleri UYDURULMAZ — Step 3a'da KURULU CLI'lardan ölçülür ve dondurulur**
    (İlke 9: ölçülmemiş değer yazılmaz; bayrak adları sürümle değişir).
    **Test beklentisi eşlemeden OKUNMAZ** (bağımsız hakem itirazı: okusaydı yanlış bir
    eşlemeyi de geçirirdi — totolojik test). Test, ölçüm anında yazılmış **bağımsız
    sabitlere** karşı doğrular ·
    **dış zaman aşımı** (aşılırsa koşu `tamamlanmadi`, dosya EZİLMEZ — K-82) ·
    **çıkış kodu ayrımı** — runner **tipli sonuç** döner (`tamam` / `zaman-asimi` /
    `hata`), ham metin değil ·
    **DURUM SAHİPLİĞİ ORKESTRATÖRDE (bağımsız hakem itirazı):** runner imzasında koşu
    kimliği ya da veritabanı YOKTUR, dolayısıyla `tamamlanmadi` işaretini runner ATAMAZ.
    `run_audit_round(db, packet, *, runner, run_id)` denetim turunda, `synthesis.run(db, …)`
    sentezde — **her terminal hatada** `runs.mark_incomplete` çağıran yerler bunlardır ·
    stdout rapor gövdesidir, **stderr rapora KARIŞTIRILMAZ** (ayrı yakalanır, maskeleme
    süzgecinden geçirilip günlüğe yazılır — K-136) · çıktı boşsa **sessiz başarı YOK**, hata.

**Bağlayıcı invariantlar (seam: `auditors.py::run_audit_round`):**
- **K-76:** denetçiler yerel CLI alt süreci olarak koşar (ağ servisi yok, K-77 lokal tek kullanıcı).
- **K-78 SIRALI:** Denetçi-1 bitmeden Denetçi-2 başlamaz. Sıra deterministiktir.
- **K-79:** her denetçi kendi çalışma dizininde koşar; dizinler birbirini görmez.
- **K-150 fail-closed:** iki geçerli rapor yoksa **sentez BAŞLAMAZ**. Eksik denetçi yeniden
  koşulur; tek raporla ilerleme YOKTUR.
- **K-82:** koşum yarıda kalırsa `runs.mark_incomplete` çağrılır, kısmi rapor dosyası EZİLMEZ.
- **LLM çıktısı VERİDİR, talimat değil:** rapor gövdesindeki gömülü yönerge yürütülmez;
  yalnız `validate_report` biçim kapısından geçirilir.

- [ ] **Step 1:** Testleri yaz — `tests/test_auditor_orchestration.py` (sahte `Runner` ile):
  `test_two_valid_reports_produce_valid_round` (pozitif kontrol) ·
  `test_single_report_blocks_synthesis` (K-150) ·
  `test_invalid_format_report_blocks_synthesis` ·
  `test_auditors_run_sequentially` (sahte runner çağrı sırasını kaydeder) ·
  `test_auditors_get_separate_working_dirs` ·
  `test_crash_mid_round_marks_incomplete_and_preserves_files` (K-82).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_auditor_orchestration.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `run_audit_round` + `Runner` protokolünü yaz.
- [ ] **Step 3a:** **ÖLÇ — üç aracın gerçek komut satırı.** Kurulu Claude Code ve Codex
  CLI'larının yardım çıktısından koşum biçimini, çıktı yönlendirmesini ve zaman aşımı
  davranışını ölç; sonucu `docs/research/`'e yaz. `ToolSpec` bu ölçümden doldurulur.
- [ ] **Step 3b:** **`SubprocessRunner` + `ToolSpec` eşlemesini yaz** (gerçek çalıştırıcı)
  ve testlerini ekle:
  `test_toolspec_covers_all_three_tools` (iki denetçi + sentez) ·
  `test_runner_argv_matches_independent_literals` (beklenti eşlemeden DEĞİL, ölçüm anında
  yazılmış sabitlerden okunur) ·

  `test_runner_returns_typed_outcome_not_raw_text` ·
  `test_orchestrator_marks_incomplete_on_timeout` (durum sahibi orkestratör — K-82) ·
  `test_orchestrator_marks_incomplete_on_nonzero` ·
  `test_runner_nonzero_exit_is_error_not_empty_report` ·
  `test_runner_empty_stdout_is_failure` (sessiz başarı yok) ·
  `test_runner_stderr_not_mixed_into_report` ·
  `test_runner_stderr_is_masked_before_logging` (K-136).
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_auditor_orchestration.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add sequential blind two-auditor orchestration`

---

### Task 11: Sentez koşumu + çıktı doğrulayıcı — pakete YAZMAZ

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/synthesis.py`
- Test: `apps/social/backend/tests/test_synthesis.py`

**Interfaces:**
- Consumes: Task 10 `AuditRound`; Task 3 `identity`; Task 4 sözleşme v2.
- Produces:
  - `synthesis.run(db, round: AuditRound, *, run_id: str, active_package, removed_history,
    holiday_keys, runner: Runner) -> SynthesisResult` — **`db` + `run_id` ZORUNLU:** sentez
    aynı `Runner`'ı kullanıyor, dolayısıyla terminal hatada `runs.mark_incomplete` çağıran
    üst orkestratör BURASIDIR (denetim turunda `run_audit_round`, sentezde `synthesis.run`).
    İlk yazımda sentez tarafında durum sahibi yoktu — zaman aşımı K-82 kaydı üretmezdi.
  - `SynthesisResult(aday_json, karar_gunlugu, acik_sorular, onay_ozeti, tasma: bool)`
  - `synthesis.validate(result: SynthesisResult) -> list[str]`

**Bağlayıcı invariantlar (seam: `synthesis.py::validate`):**
- **PAKET tablosuna YAZMAZ** (bağımsız hakem itirazı: eski cümle düz "DB'ye YAZMAZ" diyordu
  ve hemen üstündeki `db` alan imzayla çelişiyordu). Kesin sınır: sentez **yalnız koşu
  DURUMUNU** (`runs.mark_incomplete`) ve **ham artefaktı** yazabilir; `social.sector_packages`
  tablosuna hiçbir şey yazamaz. `synthesis.py` `insert_draft`'ı import ETMEZ — yapısal test
  bunu kanıtlar. Kanonik sıra `sentez → motor → draft` kod düzeyinde zorlanır.
- Aday JSON `validate_package_content` şemasına birebir uyar (Plan 1 doğrulayıcısı yeniden
  kullanılır, kopyalanmaz).
- **K-02/K-113:** `video_kodlar` İKİ havuz üretir — `hareket` ve `sahne`, ikisi de LİSTE.
- **K-74/K-75 taşma:** açık soru sayısı 10'u, denetçi önerisi 5'i aşarsa maddeler
  DÜŞÜRÜLMEZ; `tasma=True` işaretlenir. **Kesme kapısı YOKTUR** (İlke 9).
- Her karar satırı `unit_id` + `oge_yolu` + `oge_sha` + `aktor="sentez"` taşır; `guncelle`
  kimliği korur, `cikar`+`ekle` çiftinde `ekle` satırı `yerine_gecer` taşır (K-86/K-154).
  Yol ve hash `identity.enumerate_content_units` + `identity.canonical_sha` ile üretilir —
  sentez kendi kuralını yazmaz.
- **K-122 churn koruması:** yeni-zayıf öğe salt yeniliğiyle doğrulanmış kalıbı çıkaramaz.
- **K-124:** `cikar` için normal bilgide ≥1 doğrulanmış kaynaklı kanıt satırı; mevzuat/
  güvenlik bilgisinde ek olarak iki denetçi mutabakatı — yoksa çıkarma YAPILMAZ, madde
  açık soruya düşer.

- [ ] **Step 1:** Testleri yaz — `tests/test_synthesis.py`:
  `test_valid_round_produces_four_outputs` (pozitif kontrol) ·
  `test_synthesis_module_does_not_import_insert_draft` (yapısal — kanonik sıra kapısı) ·
  `test_video_pools_are_two_lists` · `test_overflow_marks_flag_without_truncating` (K-74/75) ·
  `test_cikar_without_evidence_becomes_open_question` (K-124) ·
  `test_cikar_of_legislation_requires_both_auditors` (K-124) ·
  `test_churn_guard_blocks_weak_new_over_verified` (K-122) ·
  `test_guncelle_preserves_unit_id` · `test_cikar_ekle_pair_links_via_yerine_gecer` ·
  `test_every_decision_row_carries_path_and_sha` ·
  `test_produced_log_passes_check_unit_integrity` (üretici ↔ doğrulayıcı uçtan uca) ·
  `test_synthesis_timeout_marks_incomplete` (sentez tarafında da durum sahibi var —
  bağımsız hakem itirazı: bu test Task 10'un kapısındaydı ama sentez modülü BURADA doğuyor,
  yani Task 10 mevcut sırayla tamamlanamazdı).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_synthesis.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `synthesis.py` yaz.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_synthesis.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add synthesis runner producing candidate set only`

---

### Task 12: Politika motoru — zorunlu kontroller (§9.2) + K-112 takvim erişilemezliği

**Working directory:** `apps/social/backend`

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/engine.py`
- **Modify: özel gün enjeksiyon çağıranı** (Task 5 Step 1 ölçümünün ADLANDIRDIĞI yol;
  `sector_packages.py::match_special_day` saf eşleştiricidir, takvime erişmez — erişim
  hatasını yalnız çağıran görebilir) — **K-112 (a):** takvim okunamazsa özel gün bağlamı
  BOŞ döner, blok sessizce düşer, **zorunlu maskeli log** yazılır.
- **Modify: `apps/social/backend/app/services/sector_package_lifecycle.py::insert_draft`** —
  **K-112 (b):** takvim okunamazsa yazım **açık ve tipli bir hatayla fail-closed durur**
  (bugün hata yakalanmıyor, yani davranış doğru ama KAZARA; plan onu bilinçli kılar).
  Sessiz düşüş burada YANLIŞ olurdu — anahtar doğrulaması yapılmadan yazım, uydurma
  anahtarı içeri alırdı.
- Test: `apps/social/backend/tests/test_policy_engine_checks.py`
- Test: `apps/social/backend/tests/test_package_lifecycle.py` (yazım kapısı hata enjeksiyonu)
- Test: `apps/social/backend/tests/prompt_regression/` (üretim yolu hata enjeksiyonu)

**Interfaces:**
- Consumes: Task 11 `SynthesisResult`; Task 3 `identity.decision_units`; Task 10 `AuditRound`.
- Produces:
  - `engine.CHECKS: tuple[EngineCheck, ...]` — §9.2 kümesinin **kodda sabitlenmiş** hâli.
  - `engine.run_checks(inputs: EngineInputs) -> CheckOutcome` — **saf fonksiyon, DB'ye
    dokunmaz** (mutasyon testine açık kalması için).

**Bağlayıcı kontrol kümesi (spec §9.2 — "kesin küme planda sabitlenir" hükmünün karşılığı):**
şema+boyut · **karar kapsamı** (aktif paketin HER `unit_id`'si için tam bir sonuç — K-84
bağı) · yeni kimlik benzersizliği · **kanıt** (`guncelle`/`cikar` kanıtsızsa uygulanmaz,
kalıp korunur) · **mutabakat (K-125)** · yeni öğe `2-3` yapısal çoğunluk kuralı ·
bayrak tüketimi · geri-ekleme çelişkisi · kategori çakışması (K-03: paket türü üstün) ·
özel gün anahtarı · diff sayıları · **regresyon kapısı** · tek-aktif ön kontrolü.

**Bağlayıcı invariantlar (seam: `engine.py::run_checks`):**
- **Karar kapsamı:** aktif pakette karşılığı olmayan `unit_id` veya sonucu olmayan birim →
  kapsam ihlali → **`kapsam_ihlali` bulgusu** (sonuca `decide` çevirir, Task 13).
  Bu K-84=A'nın gerçek gerekçesidir. **Kısmi turda da
  geçerlidir:** değişmeyen birimler `koru` satırı taşıdığı için (K-107) kapsam tamdır —
  not satırı kapsamı KARŞILAMAZ.
- **K-125 mutabakat:** `guncelle`/`cikar` için **iki denetçi uyumu** aranır; girdi yalnız
  Task 9'un **doğrulanmış** envanteridir (biçim kapısını geçmiş rapor yetmez).
  Uyuşmazlıkta normal içerikte kalıp KORUNUR; mevzuat/güvenlik alanında (K-129 sabit
  listesi) **`mevzuat_uyusmazligi` bulgusu** üretilir. Onu `blocked`'a çeviren `decide`'dır
  ve **her zaman** çevirir — **bu, benimsenen K-125 kararının sonucudur, K-128'in DEĞİL.**
- **K-129 listesi kodda sabittir:** `yasaklar_ve_hassasiyetler` alanının tamamı + mevzuat/
  tarih/sayı iddiası içeren tüm maddeler.
- **K-128 ile karışma YASAK (review turu düzeltmesi):** ilk yazımda `run_checks` mevzuat
  uyuşmazlığında doğrudan `blocked` dönüyordu; Task 13'ün `block_on_legislation` bayrağı
  bu yüzden hiçbir şeyi pasifleştiremiyordu — plan aynı kapıyı hem "kurulmaz" hem
  "koşulsuz uygulanır" diye yazmış oluyordu. **Bağlanan hüküm:** `run_checks` bloklamaz;
  **tipli bulgu** üretir — `mevzuat_uyusmazligi` (K-125 yolu) ve `mevzuat_dogrulanamadi`
  (K-128 yolu, `risk_unverified` statüsünden). İkisini `blocked`'a çevirmek `decide`'ın
  işidir: birincisi **her zaman** (K-125 benimsendi), ikincisi **yalnız**
  `config.block_on_legislation=True` iken (K-128 açık → varsayılan `False`).
- **K-126 tek-kaynak istisnası:** yalnız (1) kaynak resmî (K-123 ölçütü) **VE** (2) en az
  bir denetçinin canlı URL doğrulaması birlikteyken çalışır.
- **`2-3` kuralı ölçülmüş eşik DEĞİL, yapısal çoğunluktur** — motor onu uygular, koymaz.
- **Regresyon kapısı zorunludur:** Katman-1 geçmemişse `regresyon_kapisi` bulgusu üretilir;
  `decide` onu gördüğü koşuyu `activation_eligible` YAPAMAZ.
- **K-128 pasif:** bu görev yalnız `mevzuat_dogrulanamadi` bulgusunu ÜRETİR; onu bloklamaya
  çeviren yapılandırma bayrağı Task 13'tedir ve varsayılanı kapalıdır.

- [ ] **Step 1:** Testleri yaz — `tests/test_policy_engine_checks.py`, kontrol başına en az
  bir pozitif + bir negatif. **Bu görev SONUÇ beklemez — `run_checks` tipli BULGU üretir;
  bulguyu `blocked`'a çeviren `decide` Task 13'te doğar.** İlk yazımda aynı listede hem
  "hiçbir zaman bloklamaz" hem "bloklar" testleri vardı; ikisi aynı anda doğru olamaz.
  `test_full_coverage_passes` (pozitif kontrol) ·
  `test_run_checks_never_returns_a_run_outcome` (sözleşme kapısı — yalnız bulgu döner) ·
  `test_missing_unit_result_emits_kapsam_ihlali_finding` ·
  `test_unknown_unit_id_emits_kapsam_ihlali_finding` ·
  `test_guncelle_without_evidence_is_not_applied` ·
  `test_cikar_without_two_auditor_agreement_keeps_pattern` (K-125) ·
  `test_legislation_disagreement_emits_mevzuat_uyusmazligi_finding` (K-129 alan listesi) ·
  `test_unverified_legislation_emits_mevzuat_dogrulanamadi_finding` ·
  `test_engine_consumes_only_validated_inventory` (ham rapor kabul edilmez) ·
  `test_partial_run_with_koru_rows_has_full_coverage` (K-107) ·
  `test_partial_run_missing_one_unit_emits_finding` ·
  `test_single_source_exception_requires_official_and_live_url` (K-126) ·
  `test_new_item_needs_two_of_three` · `test_flag_consumption_applied` ·
  `test_readd_conflict_emits_acik_soru_finding` ·
  `test_category_conflict_package_type_wins` (K-03) ·
  `test_unmatched_holiday_key_not_written` ·
  **K-112 hata enjeksiyonu (eşleşmeme DEĞİL, erişilemezlik):**
  `test_calendar_unavailable_yields_empty_special_day_context_and_logs` (üretim yolu) ·
  `test_calendar_unavailable_fails_draft_write_closed` (yazım kapısı) ·
  `test_calendar_unavailable_log_is_masked` (K-136) ·
  `test_regression_gate_failure_emits_finding` ·
  `test_second_active_precheck_emits_finding`.
- [ ] **Step 2:** Koş — **üç yüzeyin ÜÇÜ de** (kırmızı tarafı da kanıtlanmalı; bağımsız
  hakem itirazı: yalnız PASS tarafı üç yüzeyi koşuyordu, yani yaşam döngüsü ve üretim yolu
  testlerinin değişiklikten ÖNCE gerçekten kırıldığı hiç gösterilmiyordu):
  `cd apps/social/backend && python -m pytest tests/test_policy_engine_checks.py tests/test_package_lifecycle.py tests/prompt_regression/ -v`
  — Beklenen: FAIL (üç yüzeyde de yeni testler kırmızı).
- [ ] **Step 3:** `engine.py` kontrol kümesini yaz (saf fonksiyon; DB erişimi YOK) +
  K-112'nin iki dikişini bağla (üretim çağıranı · yazım kapısı).
- [ ] **Step 4:** Koş — **üç yüzeyin ÜÇÜ de** (bağımsız hakem itirazı: dosya listesinde üç
  yüzey vardı, adımlar yalnız birini koşuyordu):
  `cd apps/social/backend && python -m pytest tests/test_policy_engine_checks.py tests/test_package_lifecycle.py tests/prompt_regression/ -v`
  — Beklenen: PASS ve Katman-1'de tek bayt fark YOK.
- [ ] **Step 5:** **Mutasyon doğrulaması:** her kontrolü tek tek devre dışı bırakıp ilgili
  testin GERÇEKTEN kırıldığını ölç (kontrol başına bir mutasyon). Sonucu commit mesajında
  değil `docs/research/2026-08-27-motor-mutasyon-olcumu.md`'ye yaz. Kırılmayan kontrol =
  test kapısı sahte.
- [ ] **Step 6:** Commit: `feat: add policy engine mandatory check set`

---

### Task 13: Motor — güvenli fallback (K-23=B) · üç bariyer (eşikler pasif) · sonuç tipleri

**Files:**
- Modify: `apps/social/backend/app/services/sector_pipeline/engine.py`
- Create: `apps/social/backend/app/services/sector_pipeline/policy_config.py`
- Test: `apps/social/backend/tests/test_policy_engine_outcome.py`

**Interfaces:**
- Consumes: Task 12 `run_checks`.
- Produces:
  - `engine.decide(inputs: EngineInputs, config: PolicyConfig) -> EngineResult` —
    `EngineResult(sonuc, sebep, final_candidate, final_decision_log, engine_diff,
    kararsizlar, barrier_report, content_sha, decision_log_sha)`.
    **F19:** `final_decision_log` motorun UYGULADIĞI karar günlüğüdür — sentezin ham
    günlüğünden ayrıdır (motor bazı kararları uygulamaz; `aktor` alanı ikisini ayırır).
  - `policy_config.PolicyConfig` — `max_change_ratio: float | None = None` ·
    `max_add_ratio: float | None = None` · `max_undecided_ratio: float | None = None` ·
    `abs_limits: dict | None = None` · `block_on_legislation: bool = False` (K-128 pasif —
    **yalnız `mevzuat_dogrulanamadi` dalını yönetir**; K-125'in uyuşmazlık bloklaması bu
    bayraktan bağımsız ve her zaman açıktır).
  - `engine.canonical_content_sha(content: dict) -> str` (K-92) — **`identity.canonical_sha`'yı
    ÇAĞIRIR**, ikinci bir hash kuralı yazmaz (tek kanonik kural).
  *(K-145'in `affected_packages`'ı BURADA DEĞİL — `runs.py`'de. Bağımsız hakem itirazı:
  bu plan motoru "saf fonksiyon, DB'ye dokunmaz" diye tanımlıyor, `db` alan bir fonksiyonu
  ona koymak kendi kuralını çiğnerdi. Kabul ölçütleri Task 8'de.)*

**Bağlayıcı invariantlar (seam: `engine.py::decide`):**
- **K-23=B güvenli varsayılan:** motorun karar veremediği madde **mevcut kalıbı korur**,
  `kararsizlar` listesine ve koşu raporuna girer, **aktivasyonu BLOKLAMAZ.** Gerçek
  çelişkiler (denetçi uyuşmazlığı · geri-ekleme çelişkisi) zaten sentezin AÇIK SORUsu olarak
  gelir ve K-71 gereği bloklar — o yol ayrıdır.
- **Motor belirsizliği yeni içeriğin lehine YORUMLAMAZ** (spec §9.3 bağlayıcı yön).
- **Üç bariyer (K-130/131/132) mekanizması kurulur, eşikleri `None`:**
  - K-130 değişim büyüklüğü: `(guncelle + cikar + runtime-etkili kirp) / mevcut_birim_sayisi`
  - K-131 ekleme oranı: paketin şişmesi
  - K-132 kararsızlık oranı: motorun aczi
  - **Eşik `None` iken bariyer HİÇBİR ŞEYİ bloklamaz** — yalnız oranı `barrier_report`'a
    yazar. Bu, "gizli varsayılan eşik" sınıfını kapatan invariant'tır (İlke 9).
  - **İlk paket koşusunda payda 0** → oran hesaplanmaz; `abs_limits` doluysa mutlak limit
    uygulanır, boşsa kontrol atlanır.
- **K-90:** `sonuc` üç değerli; `tur durduruldu` = `blocked` + `sebep`.
- **K-91:** ilk paket koşusunda `no_change` sonucu **GEÇERSİZDİR** → `blocked`,
  `sebep="ilk-kosuda-degisiklik-yok-gecersiz"`.
- **K-96:** `final_candidate` sentez adayından AYRIdır; motorun reddettikleri `engine_diff`'e
  yazılır — sentez raporu YERİNDE DEĞİŞTİRİLMEZ.
- **K-145 teknik kabulü:** UYGULANAN her karar satırı `kural_kimligi` + `kural_surumu`
  taşır (karar günlüğünde — tüketicinin baktığı yer); `engine_diff` ise motorun
  REDDETTİKLERİNİN izini taşır. İkisi ayrı sorulara cevap verir.

- [ ] **Step 1:** Testleri yaz — `tests/test_policy_engine_outcome.py`:
  `test_undecided_item_keeps_pattern_and_does_not_block` (K-23=B çekirdeği) ·
  `test_undecided_item_appears_in_report` ·
  `test_open_question_from_synthesis_still_blocks` (iki yolun ayrıldığını kanıtlar) ·
  `test_barrier_with_none_threshold_never_blocks` (İlke 9 kapısı) ·
  `test_barrier_with_set_threshold_blocks` (mekanizmanın gerçekten çalıştığının pozitif kontrolü) ·
  `test_first_run_zero_denominator_uses_absolute_limits` ·
  `test_first_run_no_change_is_invalid` (K-91) ·
  `test_blocked_carries_reason` (K-90) ·
  `test_canonical_sha_stable_across_key_order` (K-92) ·
  `test_canonical_sha_changes_on_list_order` (sıra içeriğin parçası) ·
  `test_engine_diff_preserves_original_synthesis` (K-96) ·
  `test_engine_diff_records_rule_provenance` (K-145 — reddedilenlerin izi) ·
  `test_applied_motor_rows_carry_rule_stamp` (K-145 — uygulananların izi karar günlüğünde) ·
  **bulgu → sonuç dönüşümü (Task 12 bulgu üretir, BURASI sonuca çevirir):**
  `test_kapsam_ihlali_finding_becomes_blocked` ·
  `test_mevzuat_uyusmazligi_always_becomes_blocked` (K-125 benimsendi) ·
  `test_mevzuat_dogrulanamadi_does_not_block_by_default` (K-128 pasif) ·
  `test_mevzuat_dogrulanamadi_blocks_when_flag_enabled` (yetenek kurulu — pozitif kontrol) ·
  `test_regression_gate_finding_prevents_activation_eligible` ·
  `test_second_active_finding_becomes_blocked`.
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_policy_engine_outcome.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `decide` + `policy_config.py` + `canonical_content_sha` yaz (motor SAF kalır).
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_policy_engine_outcome.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add engine outcome, safe fallback and inert barriers`

---

### Task 14: Onay yüzeyi — değişmez anlık görüntü · sinyal sıralaması · onay olayı

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/approval.py`
- Test: `apps/social/backend/tests/test_approval_surface.py`

**Interfaces:**
- Consumes: Task 13 `EngineResult`; Task 6 `sector_package_runs`; `package_events.log_package_event`.
- Produces:
  - **`approval.build_and_freeze_from_run(db, *, run_id, actor) -> dict`** (**F18**) —
    snapshot'ı çağırandan ALMAZ, `runs.load_verified_run` + bağlı taslaktan **BASAR** ve
    aynı işlemde dondurur. İçerik hash'leri, açık sorular, motor sonucu, iki kapı tasdiki
    ve K-94 taban durumu hep o kilitli satırdan okunur. Çağıranın kurduğu snapshot'ı kabul
    eden yol YOKTUR — olsaydı bir görüntü üzerinden onay alıp başka bir koşuyu aktive etmek
    mümkün olurdu.
  - `approval.render_summary(snapshot: dict) -> str` — operatörün gördüğü metin.
  - `approval.render_removals_detail(snapshot: dict) -> str` — K-41 tam listesi (bir tık derin).
  - `approval.record_decision(db, *, run_id, karar, actor, seconds, snapshot_sha) -> None`
    — **F18:** karar dondurulmuş görüntünün HASH'ine bağlanır; onay sonrası koşu satırı
    değişirse aktivasyon eşleşmez ve reddedilir.
    (K-99/K-42) — `package_events`'e `approval`/`rejection` olayı yazar; yaşam döngüsü
    kapsam sınıfı gereği `sector_id` + `package_id` + `actor` taşır.
  - `approval.to_activation_evidence(snapshot: dict) -> ActivationGateEvidence` —
    **taban durumu HER ZAMAN açıkça ifade edilir** (K-94 kapanışı): ya
    `expected_active_version=<n>` ya `expected_no_active=True`; ikisi birden veya hiçbiri
    yapım hatasıdır. "Alan boşsa kontrol atlanır" davranışı KALKAR.

**Bağlayıcı invariantlar (seam: `approval.py::render_summary`):**
- **Yönetici kalıp listesi GÖRMEZ** (spec §9.6). Gördüğü: koşu sonucu · alan-bazlı + toplam
  sayılar · değişim oranları · çıkarılanlar · son 4 turun çıkarılanlar özeti · kararsızlar ·
  geri-ekleme çelişkileri · açık sorular · kapı sonuçları · uyarılar · içerik hash'leri ·
  motor koşu raporu.
- **K-42 sıralama ilkesi:** riskli sınıflar — geri-ekleme çelişkileri · motor kararsızları ·
  çıkarmalar — nötr sayıların ÖNÜNE konur. Sıra sabit ve test edilir.
- **K-41:** özet "Çıkarılanlar: N" der; **eşik YOK**, tam liste bir tık derinde
  (`render_removals_detail`).
- **K-42 (b):** onaya kaç saniyede basıldığı kaydedilir (`approval_seconds`) — R-21
  rubber-stamp tespit göstergesi. **Eşik YOKTUR**, yalnız kayıt.
- **K-98:** `build_and_freeze_from_run` bir kez yazar; ikinci yazım DB tetikleyicisiyle
  reddedilir. Snapshot **üretilir**, dışarıdan alınmaz.
- **K-71:** açık soru listesi boş değilse onay yüzeyi **onaylanabilir sonuç sunmaz**.
- **K-94 (review turu düzeltmesi):** ilk yazım "`expected_active_version` her zaman dolu"
  diyordu; **ölçüldü** ki Plan 1'in kanıt sınıfı `< 1` değerini reddediyor ve `None`'ı
  "kontrolü atla" sayıyor — ilk pakette gerçek aktif sürüm YOKTUR, yani hangi tam sayı
  yazılsa ya yapım hatası ya uyuşmazlık çıkardı ve pilotun ilk aktivasyonu **imkânsız**
  olurdu. Doğrusu: taban durumu açıkça ifade edilir — `expected_no_active=True` (ilk paket)
  veya `expected_active_version=<n>` (sonrakiler). Uyuşmazlıkta geçiş reddedilir; ayrıca
  `expected_no_active=True` iken sektörde aktif satır varsa da reddedilir.
- **Yalnız `activation_eligible` onaylanabilir** — otomatik aktivasyon YOK.

- [ ] **Step 1:** Testleri yaz — `tests/test_approval_surface.py`:
  `test_summary_never_lists_patterns` · `test_risky_classes_precede_neutral_counts` (K-42) ·
  `test_removal_count_without_threshold_and_detail_available` (K-41) ·
  `test_last_four_rounds_removals_included` ·
  `test_open_questions_prevent_approvable_result` (K-71) ·
  `test_snapshot_freeze_is_idempotent_write_once` (K-98) ·
  `test_second_freeze_rejected_by_db` ·
  `test_snapshot_minted_from_locked_run_not_caller` (F18 — çağıran snapshot veremez) ·
  `test_snapshot_fields_equal_persisted_run` (hash · açık sorular · motor sonucu · tasdikler) ·
  `test_run_mutation_after_freeze_invalidates_approval` (F18 — onay hash'e bağlı) ·
  `test_approval_refused_when_run_not_verified` (yedi kapıdan biri düşükse onay yok) ·
  `test_evidence_always_states_base_state` (K-94 — biri ya da öteki, asla ikisi/hiçbiri) ·
  `test_first_package_snapshot_yields_expected_no_active` ·
  `test_no_change_result_is_not_approvable` ·
  `test_approval_seconds_recorded` (K-42b) ·
  `test_approval_event_logged_with_actor_and_time` (K-99 pozitif kontrol) ·
  `test_rejection_event_logged` (ret de kaydedilir — sessiz düşmez).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_approval_surface.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `approval.py` yaz.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_approval_surface.py -v` — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add approval surface with immutable snapshot and signal ordering`

---

### Task 15: Draft yazımı · yerinde güncelleme (K-106) · aktivasyon zinciri · yetki zorlaması (K-103)

**Working directory:** `apps/social/backend`

**Files:**
- Modify: `apps/social/backend/app/services/sector_package_lifecycle.py`
  (`_update_draft_row` ÖZEL ilkel + `ActivationGateEvidence.expected_no_active`)
- Create: `apps/social/backend/app/services/sector_pipeline/writeback.py`
- **Modify (DAVRANIŞ DEĞİŞİKLİĞİ — Plan 1 testleri):**
  `apps/social/backend/tests/test_package_lifecycle.py` ve
  `apps/social/backend/tests/test_plan2_interface_contract.py` — `ActivationGateEvidence`
  kuran HER çağrı taban durumunu açıkça vermek zorunda. Eski "alan boşsa kontrol atlanır"
  yolu kalktığı için bu testler **kırılır ve güncellenmeleri bu görevin parçasıdır**;
  sessizce geçmeleri beklenmez (Plan 1 kapsamına giren bilinçli, kayıtlı bir kırılma).
- Test: `apps/social/backend/tests/test_pipeline_writeback.py`
- Test: `apps/social/backend/tests/test_write_surface_authorization.py`

**Interfaces:**
- Consumes: Task 14 `approval`; Task 6 `sector_package_runs`; Plan 1 `insert_draft` /
  `activate_package` / `rollback_package`.
- Produces:
  - `writeback.write_draft_from_run(db, *, run_id, actor) -> UUID`
  - `writeback.update_draft_from_run(db, *, run_id, actor) -> None` (K-106)
  - `writeback.activate_from_snapshot(db, *, run_id, actor) -> None`
  - `sector_package_lifecycle._update_draft_row(...)` — **ÖZEL**, public API değil.

**Bağlayıcı invariantlar (seam: `writeback.py::write_draft_from_run`):**
- **Kanıt DB'den okunur, çağırandan alınmaz (review turu düzeltmesi).** İlk yazım çağıranın
  verdiği bir `EngineResult` nesnesini kabul edip yalnız `sonuc` alanına bakıyordu — bir
  sentez adayı elle kurulmuş bir sonuç nesnesine sarılarak motor hiç koşmadan yazdırılabilirdi
  ve planlanan testler bunu GEÇİRİRDİ. **YEDİ kapı, hepsi aynı işlem içinde koşu satırından
  okunur:** `durum='tamamlandi'` · `sonuc='activation_eligible'` · `engine_version` dolu ·
  `engine_config_sha` dolu · `content_sha` yazılacak `final_candidate` ile eşleşiyor ·
  **`final_decision_log` dolu** · **`decision_log_sha` onunla eşleşiyor** (F19).
  Yazım `insert_draft(..., decision_log=<DB'den okunan final günlük>)` ile yapılır —
  yer tutucu ya da ham sentez günlüğü YAZILMAZ.
- **K-106:** ret sonrası düzeltme **aynı `draft` satırını yerinde** günceller — yeni sürüm
  yakılmaz. Tek public yol `update_draft_from_run`'dır ve **aynı `load_verified_run`
  doğrulayıcısından** geçer — ayrı bir kapı listesi taşımaz; ham
  satır mutasyonu (`_update_draft_row`) ÖZELDİR, dışarıdan çağrılamaz. İlk yazımdaki public
  `update_draft(package_id, content, decision_log, actor)` imzası **KALDIRILDI**: koşu, motor
  sonucu, regresyon kanıtı, denetçi envanteri ve dondurulmuş anlık görüntü taşımadığı için
  "tüm kapılar yeniden koşar" vaadini teknik olarak karşılayamıyordu.
- **Yarış (review turu düzeltmesi):** durum kontrolü ile güncelleme **aynı işlemde**,
  satır kilidi altında yapılır — eşzamanlı aktivasyonla yarışta tek kazanan olur.
  Güncelleme önceki onay anlık görüntüsünü **geçersizler** (bayat kanıtla aktivasyon yok).
- **K-72 + K-106 ayrımı kod düzeyinde zorlanır (tur 4 düzeltmesi):**
  `write_draft_from_run` **düzeltme koşusunu REDDEDER** (`kosu_turu='duzeltme'` → hata) —
  düzeltmenin ikinci bir sürüm yakması K-106'nın tam olarak yasakladığı sonuçtur.
  `update_draft_from_run` ise soyağacını **şart koşar**: `duzeltilen_run_id` boşsa çalışmaz.
  Hedef taslak parametreden DEĞİL, koşunun devraldığı `package_id`'den gelir — bu yüzden
  imzada `package_id` yoktur ve yanlış taslağı güncellemek mümkün değildir.
  Ana koşunun dondurulmuş görüntüsüne DOKUNULMAZ (K-98); düzeltme koşusu kendi taze
  görüntüsünü basar ve kendi onayını alır.
- **K-72:** düzeltme turu otomatik BAŞLAMAZ; yönetici `duzeltme-baslat` komutuyla tetikler.
- **F18 — aktivasyon kanıt zinciri DB'den doğrulanır (review turu düzeltmesi).** İlk yazımda
  `activate_from_snapshot(run_id, actor)` yalnız dondurulmuş anlık görüntüye bakıyordu;
  onayın gerçekten VERİLDİĞİNİ, Katman-1'in GEÇTİĞİNİ ve hazırlık listesinin ONAYLANDIĞINI
  bağlayan hiçbir invariant yoktu. Plan 1'in kanıt sınıfı bu üçünü boolean olarak olduğu
  gibi kabul eder — yani adaptör onları **uydurabilirdi** ve motor çıktısı yönetici onayı
  olmadan aktive edilebilirdi (K-69/K-28 atlatılırdı). **Bağlanan hüküm:**
  `activate_from_snapshot(db, *, run_id, actor)` aynı işlem içinde koşu satırından şunları
  yükler ve doğrular: koşu→paket bağı · `approval_karar='onay'` (ret veya karar yoksa RED) ·
  `katman1_attestation` PASS · `readiness_attestation` onaylı · **`katman2_attestation`
  koşuldu+sunuldu (SONUCU OKUNMAZ — spec §10.2)** · K-94 taban durumu.
  **+ İÇERİK BAĞI (tur 5 düzeltmesi):** taslak satırı kilitlenir ve o anki `content` ile
  `decision_log`'un hash'leri onaylanan görüntüdekilerle KARŞILAŞTIRILIR; uyuşmazsa
  aktivasyon REDDEDİLİR. Sebep: onaydan sonra taslağı değiştiren herhangi bir yol
  (düzeltme turu, elle müdahale) yöneticinin GÖRMEDİĞİ baytların aktive edilmesine yol
  açardı — kapı, kaç yazıcı olduğundan bağımsız olarak burada kapanır.
  Ancak hepsi sağlanınca `ActivationGateEvidence` kurulur.
- **K-94 ilk aktivasyon:** kanıt dondurulmuş anlık görüntüden kurulur; ilk pakette
  `expected_no_active=True`, sonrakilerde `expected_active_version=<n>`.
- **K-103 (a) yapısal — İKİ tarama:** (1) hiçbir HTTP router yaşam döngüsü yazıcılarını
  import ETMEZ; (2) depo genelinde (migration + lifecycle modülü hariç) `sector_packages`
  tablosuna doğrudan SQL yazan kod YOKTUR. İkincisi olmadan import taraması ham SQL'i
  kaçırırdı.
- **K-135:** paket tablosuna tek yazma yüzeyi yaşam döngüsü modülüdür.

- [ ] **Step 1:** Testleri yaz — `tests/test_pipeline_writeback.py`:
  `test_persisted_eligible_run_writes_draft` (pozitif kontrol) ·
  `test_unpersisted_result_object_rejected` (köken kapısı — asıl atlatma yolu) ·
  `test_synthesis_only_candidate_rejected` ·
  `test_hash_mismatch_rejected` · `test_missing_engine_stamp_rejected` ·
  `test_missing_final_decision_log_rejected` (F19) ·
  `test_decision_log_sha_mismatch_rejected` (F19) ·
  `test_written_draft_carries_engine_decision_log_not_placeholder` (F19 pozitif kontrol) ·
  `test_update_path_uses_same_seven_gates` (ayrı kapı listesi yok) ·
  `test_update_rejected_on_missing_decision_log` (F19 — güncelleme yolu) ·
  `test_update_rejected_on_decision_log_hash_mismatch` (F19 — güncelleme yolu) ·
  `test_replay_returns_existing_draft_without_new_version` (idempotency) ·
  `test_concurrent_writes_yield_single_draft` (idempotency) ·
  `test_writeback_cannot_read_run_row_outside_loader` (yapısal — tek kapı listesi) ·
  `test_write_path_refuses_correction_run` (K-106 — ikinci sürüm yakılamaz) ·
  `test_update_path_requires_correction_lineage` ·
  `test_correction_updates_parent_target_draft` (K-106 pozitif kontrol) ·
  `test_parent_snapshot_unchanged_after_correction` (K-98) ·
  `test_correction_mints_its_own_snapshot_and_approval` ·
  `test_correction_vs_stale_activation_single_winner` ·
  `test_activation_refused_when_draft_content_hash_differs` (NEW-3 — görülmeyen bayt aktive
  edilemez) ·
  `test_activation_refused_when_draft_decision_log_hash_differs` ·
  `test_activation_succeeds_when_draft_unchanged_since_approval` (pozitif kontrol) ·
  `test_periodic_run_after_rollback_or_deactivation_writes_new_version` (düzeltme
  soyağacı sıradan turu engellemez) ·
  `test_incomplete_run_rejected` · `test_no_change_and_blocked_write_no_draft` ·
  `test_update_from_run_keeps_version_number` (K-106) ·
  `test_update_from_run_rejected_on_active_row` ·
  `test_update_from_run_requires_eligible_persisted_run` ·
  `test_update_invalidates_previous_snapshot` ·
  `test_concurrent_update_and_activation_single_winner` ·
  `test_activation_requires_recorded_approval` (F18 — karar yokken RED) ·
  `test_activation_refused_after_rejection` (F18) ·
  `test_activation_refused_when_katman1_attestation_missing_or_failed` (F18) ·
  `test_activation_refused_when_readiness_not_approved` (F18) ·
  `test_activation_refused_when_katman2_attestation_missing` ·
  `test_activation_succeeds_with_negative_katman2_result` (sonuç kapı DEĞİL — pozitif kontrol) ·
  `test_activation_succeeds_with_full_attestation_chain` (F18 pozitif kontrol) ·
  `test_first_activation_uses_expected_no_active` (K-94 ilk aktivasyon) ·
  `test_expected_no_active_rejected_when_active_row_exists` ·
  `test_version_mismatch_rejects_activation` (K-94 uçtan uca).
- [ ] **Step 2:** `tests/test_write_surface_authorization.py` yaz:
  `test_no_router_imports_lifecycle_writers` · `test_no_direct_sql_writer_outside_lifecycle`
  (depo geneli tarama; migration + lifecycle modülü muaf).
- [ ] **Step 3:** Koş: `cd apps/social/backend && python -m pytest tests/test_pipeline_writeback.py tests/test_write_surface_authorization.py -v`
  — Beklenen: FAIL.
- [ ] **Step 4:** `_update_draft_row` + `expected_no_active` + `writeback.py` yaz.
- [ ] **Step 5:** Koş: aynı komut — Beklenen: PASS.
- [ ] **Step 5b:** Plan 1'in `ActivationGateEvidence` kuran testlerini taban durumunu
  açıkça verecek şekilde güncelle, sonra koş:
  `cd apps/social/backend && python -m pytest tests/test_package_lifecycle.py tests/test_plan2_interface_contract.py -v`
  — Beklenen: PASS. (Bu kırılma bilinçlidir; K-94'ün zorunlu hâle gelmesinin bedeli.)
- [ ] **Step 6:** **K-103 (b) ETKİN YETKİ ÖLÇÜMÜ — bağlamadan önce ölç.** `role_table_grants`
  TEK BAŞINA yetersizdir: üyelikle miras, sahiplik, `PUBLIC` grant'ı ve superuser görünmez,
  yani "zaten yetki yok" diye YANLIŞ kapanış üretebilir. Ölçüm: (a) API'nin gerçek
  `session_user`/`current_user` değeri; (b)
  `has_table_privilege(<rol>,'social.sector_packages','INSERT'|'UPDATE'|'DELETE'|'TRUNCATE')`;
  (c) rol üyeliği · tablo sahipliği · superuser · `PUBLIC` grant'ı; (d) **negatif yazma
  denemesi** — API kimliğiyle gerçekten reddediliyor mu. Sonucu `docs/research/`'e yaz.
  Yetki VARSA kaldırma MANUEL ADIM olarak Task 18 dağıtım listesine girer. **Rol adı
  ölçülmeden migration'a yazılmaz.**
- [ ] **Step 7:** Koş: `cd apps/social/backend && python -m pytest tests/prompt_regression/ -v`
  — Beklenen: tek bayt fark YOK.
- [ ] **Step 8:** Commit: `feat: add provenance-gated draft writeback and update path`

---

### Task 16: Komut ailesi — repo CLI + ince adaptörler + bildirim ayakları

**Files:**
- Create: `apps/social/backend/scripts/sector_pipeline_cli.py`
- Create: `~/.claude/commands/sektor-paket.md` (ince çağırıcı — iş mantığı YOK)
- Create: `shared/n8n-workflows/n8n-error-notifier.json`
- Modify: `apps/social/backend/app/services/notifications.py` (`recovered` modu)
- Modify: `apps/social/backend/app/routers/brands.py`
  (`GET /brands/{brand_id}/package-status` → `recovered` durumu + sabit mesaj)
- Modify: frontend marka paneli bandı (Plan 1'in K-45 devre-dışı bandının kardeşi)
- **Modify: `apps/social/backend/tests/test_notifications.py`** (yeni workflow'un sözleşme
  testleri buraya eklenir — Step 7b)
- Test: `apps/social/backend/tests/test_pipeline_cli.py`

**Working directory:** `apps/social/backend`

**Interfaces:**
- Consumes: Task 1-15'in tüm servis yüzeyleri.
- Produces: CLI alt komutları — `tur-ac` · `brief-doctor` · `denetim` · `sentez` · `motor` ·
  **`katman1`** (koşar + `runs.attest_katman1` ile tasdik yazar) ·
  **`katman2`** (kör örneklemi koşar, sonucu yöneticiye SUNAR ve `runs.attest_katman2` ile
  koşuldu+sunuldu tasdikini yazar; sonucu kapı DEĞİL) ·
  **`duzeltme-baslat`** (K-72 — reddedilmiş koşudan `runs.open_correction_run` ile düzeltme
  turu açar; otomatik tetik YOK) ·
  **`etki-analizi`** (K-145 — bir kural sürümünün etkilediği paket kümesini raporlar;
  ayrım yapılamıyorsa kümenin TÜM paketlere genişlediğini açıkça gösterir) ·
  **`olay-plani`** (K-145 — `runs.build_rollback_plan` ile DEĞİŞMEZ plan yazar, hedef
  sürümleri sabitler, olay kimliğini basar. **"Hiçbir şeyi değiştirmez" YANLIŞ bir ifadeydi**
  — komut plan satırları YAZAR; değiştirmediği şey **paket durumu ve paket olay kaydıdır**) ·
  **`olay-geri-al`** (K-145 — **olay kimliğiyle** çağrılır, planı paket paket yürütür;
  `hedefsiz` satırları **ayrı bir başlık altında** raporlar — sessizce başarı sayılmaz,
  tek çıkışları deaktivasyondur;
  toplu-atomik yeni mekanizma YOK, her paket kendi işlemi ve kendi olay kaydı;
  yarıda kalırsa aynı komut kaldığı yerden devam eder, hedefi yeniden hesaplamaz) ·
  `onay` · `aktive-et` · `geri-al` · `durum`. **F18:** iki tasdiğin de ADLANDIRILMIŞ bir
  operatör komutu vardır — tasdik alanlarının nasıl dolacağı belirsiz bırakılmaz. Her biri
  `scripts/sector_sweep.py` desenini izler: argparse · açık `--database-url` · deterministik
  çıktı · anlamlı çıkış kodu.

**Bağlayıcı invariantlar (seam: `sector_pipeline_cli.py::main`):**
- Resmî koşu başlatan HER alt komut **ilk iş olarak** `contracts.require_pin` çağırır —
  sözleşme drift'inde koşu BAŞLAMAZ (fail-closed).
- `~/.claude/commands/sektor-paket.md` yalnız CLI'yi çağırır; karar mantığı, eşik, sıra
  bilgisi ORADA BULUNMAZ (karar turu hükmü).
- **K-26 vade bildirimi:** periyodu (6 ay, sektör başına alan) dolan paket için
  `record_admin_event` ile bildirim — elle vade takibi kalmaz.
- **K-45 geri-dönüş (F23 devri) — MÜŞTERİ YÜZEYİ ŞART (review turu düzeltmesi):** ilk yazım
  yalnız `notifications.py`'a dokunuyordu; ama yönetici olay kuyruğu (outbox) **yöneticiye**
  teslim eder, marka sahibine DEĞİL — yani "Bakım çalışması tamamlandı, sektöre özel gönderi
  modu kullanıma açıldı." mesajının müşteriye ulaşacağı bir yol YOKTU. Plan 1'in K-45
  sözleşmesi bu mesajı `GET /brands/{brand_id}/package-status` + panel bandına bağlıyordu
  (devre-dışı metninin kardeşi). **Bağlanan hüküm:** `recovered` durumu o uca eklenir ve
  frontend bandı onu gösterir; Plan 1 durum modelini bilerek kapalı-enum değil string
  bırakmıştı, şema kırılmaz.
  **Maruziyet kanıtı:** `brand_sub_sector_history` kesişimi (Task 6 tetikleyicisi yazar).
  Bilinmeyen geçmiş retroaktif "tamamlandı" ÜRETMEZ — geçmişsiz marka bildirim almaz.
- **n8n hata bildirimi (CURRENT.md açık kalemi — tetiği bu görev):** **taze ölçüm
  (2026-08-27, bu oturumda koşuldu):** n8n yönetim ucundan (`/api/v1/workflows?limit=100`,
  kimlik başlığı `.env`'deki anahtardan okunur) çekilen liste JSON'ı saydırıldı
  → **toplam 18 · aktif 13 · `settings.errorWorkflow` taşıyan 0.** Yani başarısız bir tur
  bugün kimseye ulaşmıyor. Bu görev bir hata-bildirimi workflow'u kurar ve **sektör paketi
  yönetici olay workflow'una** bağlar. Diğer 17 workflow'a bağlanması bu görevin kapsamı
  DEĞİLDİR — dürüst etiket: kapsam bilinçle dar, kalan workflow'lar CRM turunda ele alınır.

- [ ] **Step 1:** Testleri yaz — `tests/test_pipeline_cli.py`:
  `test_every_run_subcommand_requires_pin` (pin bozukken rc≠0) ·
  `test_pin_clean_allows_run` (pozitif kontrol) ·
  `test_cli_output_is_deterministic` (aynı girdi → bayt-aynı çıktı) ·
  `test_database_url_not_inherited_from_env` (sector_sweep deseni) ·
  `test_due_notice_creates_admin_event` (K-26) ·
  `test_recovered_state_exposed_on_package_status_endpoint` (müşteri yüzeyi — K-45) ·
  `test_recovered_only_for_brands_with_maintenance_overlap` ·
  `test_recovered_skipped_when_history_unknown` ·
  **K-145:** `test_etki_analizi_reports_expanded_set_when_unseparable` ·
  `test_olay_plani_writes_plan_without_touching_package_state` ·
  `test_olay_plani_does_not_emit_package_events` ·
  `test_olay_geri_al_requires_incident_id` ·
  `test_olay_geri_al_rolls_back_each_package_separately` ·
  `test_olay_geri_al_logs_event_per_package` ·
  `test_olay_geri_al_resumes_without_double_rollback` ·
  `test_olay_geri_al_reports_hedefsiz_separately` ·
  `test_etki_analizi_requires_full_quad` (dört alan da zorunlu) ·
  **yerel arıza:** `test_cli_terminal_failure_produces_admin_event` ·
  `test_package_status_owner_scoped` (başka markanın durumu okunamaz).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_pipeline_cli.py -v`
  — Beklenen: FAIL.
- [ ] **Step 3:** `sector_pipeline_cli.py` + `notifications.py` `recovered` modu +
  `routers/brands.py` `package-status` genişlemesini yaz.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_pipeline_cli.py -v`
  — Beklenen: PASS.
- [ ] **Step 5:** Frontend panel bandını `recovered` durumunu gösterecek şekilde genişlet
  (Plan 1'in devre-dışı bandının kardeşi; sabit metin değiştirilmez).
- [ ] **Step 6:** `~/.claude/commands/sektor-paket.md` ince adaptörünü yaz; içinde iş mantığı
  OLMADIĞINI gözle doğrula (yalnız CLI çağrısı + argüman geçişi).
- [ ] **Step 7:** `shared/n8n-workflows/n8n-error-notifier.json` yaz ve
  `sector-package-admin-events.json`'a `errorWorkflow` olarak bağla.
- [ ] **Step 7b:** **Yeni workflow'u mevcut sözleşme testlerine SOK** (bağımsız hakem
  itirazı, 2026-08-27: bu kurallar bugün yalnız eski workflow üzerinde koşuyor —
  `tests/test_notifications.py`'daki sabit-kimlik · `$env` yasağı · credential bağı
  testleri). Yeni workflow için aynı üçlü: `test_error_notifier_carries_stable_id` ·
  `test_error_notifier_reads_no_process_env` · `test_error_notifier_credentials_are_bound`.
  Gerekçe ölçülü: canlı kurulumda `$env` kapalı ve import sabit kimlik istiyor
  ([[decisions/2026-08-26-n8n-credential-over-env]]).
- [ ] **Step 7c:** Koş: `cd apps/social/backend && python -m pytest tests/test_notifications.py -v`
  — Beklenen: PASS. (Bağımsız hakem itirazı: testler ekleniyordu ama bu görev içinde
  koşulmuyordu; dağıtım öncesi tam suite yakalardı, ama görev kendisi doğrulanmadan
  commit edilirdi.)
- [ ] **Step 8:** Commit: `feat: add operator CLI, thin command adapter and error notifier`

---

### Task 17: İşletime hazırlık kontrol listesi kapısı (K-69/K-70)

**Working directory:** `apps/social/backend`

**Files:**
- Create: `apps/social/backend/app/services/sector_pipeline/readiness.py`
- **Modify: `apps/social/backend/scripts/sector_pipeline_cli.py`** — `hazirlik-onayla`
  alt komutu BU görevde eklenir (bağımsız hakem itirazı: komut Task 16'dan buraya taşınmıştı
  ama dosya listesine ve adımlara yansımamıştı).
- Test: `apps/social/backend/tests/test_readiness_checklist.py`
- Test: `apps/social/backend/tests/test_pipeline_cli.py` (komut testi eklenir)

**Interfaces:**
- Consumes: Task 16 CLI; Task 1 `contracts`.
- Produces:
  - `readiness.CHECKLIST: tuple[Item, ...]` — spec §13.4'ün 20 maddesi.
  - `readiness.evaluate(db) -> ReadinessReport` — otomatik ön-kontrolle işaretlenebilenler
    ölçülür, kalanlar operatör onayı bekler.
  - **CLI alt komutu `hazirlik-onayla`** — listeyi sunar ve operatörün TEK onayını yazar.
    **Komut BU görevde üretilir, Task 16'da DEĞİL** (bağımsız hakem itirazı, 2026-08-27):
    ilk yazımda Task 16 bu komutu vaat ediyordu ama tükettiği işlev Task 17'de doğuyordu —
    Task 16 mevcut sırayla uygulanıp doğrulanamazdı. Komut, üreticisiyle aynı görevde durur.
  - `readiness.attest(db, *, run_id, report, actor) -> None` — **F18:** operatörün TEK onayını
    koşu satırındaki `readiness_attestation` alanına kalıcı yazar (kim · ne zaman · hangi
    maddeler). Aktivasyon bu kaydı okur; boolean uydurulamaz.

**Bağlayıcı invariantlar (seam: `readiness.py::evaluate`):**
- **K-69:** liste **ilk aktivasyon öncesi KAPIDIR** — tamamlanmadan
  `ActivationGateEvidence.checklist_approved` doldurulamaz. **Ama kapı yalnız `kapi`
  sınıfındaki maddeleri sayar:** sonuç iddia eden maddeler (bugün 15. madde — kör
  değerlendirmede ayrışma) `sinyal` sınıfındadır ve tamamlanma şartına girmez (İlke 9 +
  K-11 (b) açık).
- **K-70:** işaretleme sorumlusu operatördür; otomatik ön-kontrol yalnız **işaretler**,
  operatörün yerine ONAYLAMAZ. Yöneticiye özet + TEK onay düşer.
- Otomatik ölçülemeyen madde `elle` işaretlidir ve raporda öyle görünür — "ölçüldü" gibi
  sunulmaz (İlke 9).
- **F18 üretici zinciri:** hazırlık onayı, Katman-1 ve Katman-2 sonuçları **kalıcı
  tasdiklerdir**, geçici boolean değil. Katman-1 ve Katman-2 tasdiklerini koşu komutları
  yazar; hazırlık tasdikini `readiness.attest` yazar. Aktivasyon üçünü de DB'den doğrular.
- **KATMAN-2 AYRIMI — bağımsız hakem itirazının kapanışı (2026-08-27).** Spec §10.2 ve
  spec-input Katman-2 için iki AYRI şey söyler: **koşulması ve sunulması ÖN KOŞULDUR**,
  **sonucu KAPI DEĞİLDİR** (*"Bu katman başarısızlık koşulu üretmez"* — eşik K-11 (b)'de
  açık). İlk yazım ikisini de kaçırmıştı: kanıt zincirinde Katman-2 hiç yoktu, üstelik
  hazırlık listesinin **15. maddesi** (*"kör değerlendirmede sektörel ayrışma gözlendi"*)
  bir SONUÇ iddiasıdır ve listenin tamamı bloklayıcı sayılınca fiilen sert kapıya dönerdi —
  girdi bunu açıkça yasaklıyor: *"bu belgede kapıya çevrilmez."*
  **Bağlanan hüküm:** (a) `katman2_attestation` koşum kimliği · sunum zamanı · özet sonucu
  taşır; aktivasyon **yalnız koşulmuş+sunulmuş olmasını** arar, sonucuna BAKMAZ.
  (b) Hazırlık listesinde sonuç iddia eden maddeler `sinyal` olarak işaretlenir ve
  **tamamlanma kapısına GİRMEZ** — operatöre gösterilir, kararı etkiler, bloklamaz.
  (c) Eşik konulması K-11 (b)'ye bağlıdır ve bu plan onu KAPATMAZ.

- [ ] **Step 1:** Testleri yaz — `tests/test_readiness_checklist.py`:
  `test_checklist_has_twenty_items` · `test_incomplete_checklist_blocks_activation` (K-69) ·
  `test_complete_checklist_allows_activation` (pozitif kontrol) ·
  `test_manual_items_labelled_as_manual` (otomatik ölçüm iddiası yok) ·
  `test_signal_items_do_not_block_completion` (md.15 kapıya dönmüyor) ·
  `test_gate_items_still_block_completion` (pozitif kontrol) ·
  `test_activation_requires_katman2_run_and_presented` ·
  `test_activation_does_not_read_katman2_result` (sonuç kapı DEĞİL) ·
  `test_auto_precheck_does_not_self_approve` (K-70) ·
  `test_attest_persists_actor_and_time` (F18) ·
  `test_activation_reads_persisted_attestation_not_caller_flag` (F18).
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_readiness_checklist.py -v`
  — Beklenen: FAIL.
- [ ] **Step 3:** `readiness.py` yaz.
- [ ] **Step 3b:** `hazirlik-onayla` alt komutunu CLI'ye ekle; testi:
  `test_hazirlik_onayla_writes_attestation` (komut gerçekten tasdik yazıyor) ·
  `test_hazirlik_onayla_requires_run_id`. Koş:
  `cd apps/social/backend && python -m pytest tests/test_pipeline_cli.py -v` — Beklenen: PASS.
- [ ] **Step 4:** Koş: `cd apps/social/backend && python -m pytest tests/test_readiness_checklist.py -v`
  — Beklenen: PASS.
- [ ] **Step 5:** Commit: `feat: add operational readiness checklist gate`

---

### Task 18: Ön-pilot dağıtım — şema · arka uç · CLI · adaptör · workflow'lar

**Bu görev review turunda EKLENDİ.** İlk yazımda dağıtım KAPANIŞ görevine konmuştu, yani
pilot **kendi şemasından ve kodundan ÖNCE** koşacaktı: pilot, kuyumculuğun ilk `active`
paketini 035/036 tablolarıyla ve yeni CLI'yle üretmek zorunda, oysa ikisi de o noktada
canlıda kurulu değil. Atılabilir test veritabanında koşmak vaat edilen canlı
paketi üretmez; canlıda koşmak ise kurulu olmayan şema yüzünden düşer. Bu bir **sıra
bağımlılığıdır**, uygulama ayrıntısı değil.

**Files:**
- Create: `docs/plans/PLAN2-DAGITIM-RUNBOOK.md` (uygulama + geri alma sırası)

**Interfaces:**
- Consumes: Task 1-17'nin ürettiği her artefakt.
- Produces: koşmaya hazır canlı ortam + geri dönüş noktası.

**Bağlayıcı invariantlar:**
- **Sıra bağlayıcıdır ve geri alma TERS sıradadır.** Runbook her adımın geri alma karşılığını
  yazar; "git revert" DB için geri alma DEĞİLDİR.
- **F20 — İKİ AYRI geri alma rejimi, karıştırılmaz (review turu düzeltmesi).** İlk yazım
  koşulsuz ters-sıra geri alma vaat ediyordu; ama pilot bir onay/ret olayı ya da koşu satırı
  ürettikten SONRA şemayı geri almak ya teknik olarak başarısız olur (daraltılan CHECK mevcut
  satıra takılır) ya da denetim izini imha eder.
  **(a) Pilot ÖNCESİ (bu görev):** şema geri alması geçerlidir — Plan 2 verisi henüz yok,
  `036_down` → `035_down` temiz koşar. Prova adımı bunu kanıtlar.
  **(b) Pilot SONRASI:** şema geri alması bir seçenek DEĞİLDİR. `036_down` veri varken
  fail-closed durur (Task 6); geri dönüş yolu **veri-koruyan ileri düzeltme migration'ıdır**.
  Runbook bu ikisini ayrı başlıkta yazar ve (b) için "şema geri alma YOK" hükmünü açıkça
  kaydeder — sessiz bir vaat bırakmaz.
- **Sözleşme deposu da bir dağıtım kalemidir:** `require_pin` dış depoyu pinlenen commit'te
  bekler. Depo yoksa/bayatsa CLI fail-closed durur — yani kurulum yapılmadan komut ailesi
  hiç çalışmaz.
- Dağıtım **arka uç ile sınırlı değildir:** iki değiştirilmiş workflow (takvim + yönetici
  olayları) ve yeni hata-bildirimi workflow'u da import + aktive edilir; global adaptör
  kurulur ve bir kez çağrılarak sınanır.

- [ ] **Step 0 — DAĞITIM ÖNCESİ KALİTE KAPISI (bağımsız hakem itirazı, 2026-08-27).**
  İlk yazımda canlı ortam, son tam test ve güvenlik incelemesinden ÖNCE değişiyordu: tam
  test kümesi ve kabul eşlemesi kapanış görevindeydi, kalite zinciri de ondan sonra.
  Dağıtım geri alınması pahalı bir dış-dünya işlemidir; kapı ondan ÖNCE koşar.
  (a) Tam test kümesi taze: `cd apps/social/backend && python -m pytest tests/ -v` —
  çıktı raporlanır (geçen/kalan sayısı; "geçmeli" DEĞİL). (b) Katman-1 tam sweep: tek bayt
  fark YOK. (c) Sözleşme pin'i doğrulanır. (d) `/review-claude-codex` ve
  `/security-review-claude-codex` bu görevden ÖNCE koşulmuş olmalı; critical/high açık
  bulgu varsa dağıtım BAŞLAMAZ. Dördü de geçmeden Step 1'e geçilmez.
- [ ] **Step 1:** Canlı klonda prova: 035 ve 036'yı `psql -v ON_ERROR_STOP=1 --single-transaction`
  ile dosya dosya uygula; ardından `036_down` → `035_down` → tekrar ileri koş (up-down-up).
  **Bu prova YALNIZ pilot-öncesi rejimi kanıtlar** (F20 (a)); veri varken aynı yolun fail-closed
  durduğu Task 6'nın testlerinde kanıtlanır.
- [ ] **Step 2:** Canlıya uygula (aynı komut biçimi, dosya dosya). Geri dönüş noktasını
  runbook'a yaz.
- [ ] **Step 3:** Arka ucu ve CLI'yi dağıt; `sector_pipeline_cli.py --help` ve `durum`
  alt komutunun canlıda koştuğunu ölç.
- [ ] **Step 4:** Dış araştırma deposunu pinlenen commit'e getir; **dağıtılmış kullanıcı
  bağlamından** `contracts.require_pin` doğrulamasını koş — Beklenen: geçti.
- [ ] **Step 5:** `~/.claude/commands/sektor-paket.md` adaptörünü kur; bir alt komutu
  gerçekten çağırarak sınanır (kurulu ama çalışmayan adaptör sessiz arızadır).
- [ ] **Step 6:** Üç workflow'u n8n'e import + aktive et: `turkey-calendar-update.json`
  (dönem-farkında yeni sürüm) · `sector-package-admin-events.json` (errorWorkflow bağlı) ·
  `n8n-error-notifier.json`. Sentetik bir olayla TEK teslim smoke'u, sentetik bir hatayla
  TEK hata-bildirimi smoke'u koş.
- [ ] **Step 7:** Task 15 Step 6'nın etkin-yetki ölçümü "yetki var" dediyse API rolünün
  `sector_packages` yazma yetkisini kaldır ve **negatif yazma denemesiyle** doğrula (K-103 (b)).
- [ ] **Step 8:** Takvim ucunun dönem alanını döndürdüğünü ve önbelleğin bayat kalmadığını ölç.
- [ ] **Step 9:** Runbook'a **iki geri alma rejimini ayrı başlıkta** yaz (F20): pilot-öncesi
  şema geri alması · pilot-sonrası veri-koruyan ileri düzeltme. İkincisinde "şema geri alma
  YOK" hükmü açıkça yazılır.
- [ ] **Step 10:** Runbook'u commit et: `docs: add plan 2 deployment runbook`

---

### Task 19: Kuyumculuk pilotu — resmî tur

Bu görev **koda değil, koşuma** aittir. Kapsam: dört operatör kararının kapanması, test
markası, araştırmaların K-18 gereği yeniden üretilmesi, resmî zincirin uçtan uca koşması.

**Files:**
- Create: `docs/research/2026-XX-XX-kuyumculuk-pilot-turu.md` (koşu raporu)
- Create: `<arastirma-deposu>/kosu/<run_id>/` (koşu klasörü — K-17)

**Interfaces:**
- Consumes: Task 1-18'in tamamı (**dağıtım dahil** — Task 18 koşmadan bu görev başlayamaz).
- Produces: kuyumculuk alt sektörünün ilk `active` paketi + kalibrasyon verisi.

**Bağlayıcı sıra (spec §13.3 "İlk paket koşusu" + K-134 kalibrasyon çatalı):**
brief (A+B — ilk pakette yalnız-B geçersiz) → üç araç elle → koşu klasörü → mekanik kapı →
iki kör denetçi → sentez → **[K-134 çatalı: operatörün yalnız-sentez yargısı KAYDEDİLİR]** →
**motor** → karşılaştırma → yazım kapısı → `draft` → Katman-1 + Katman-2 → onay →
aktivasyon (ilk pakette yalnız ikinci adım) → markalara öneri/teyit → ilk üretim gözlemi.

**K-134 sıra hükmü (review turu düzeltmesi):** ilk yazımda motor ve onay birlikte
koşuluyor, operatörün "bağımsız yargısı" ondan SONRA isteniyordu — motor çıktısı ortadayken
verilen yargı **kör değildir** ve spec §15.2'nin istediği kalibrasyon kanıtı olamaz.
Operatörün yargısı motor koşmadan ÖNCE kaydedilir; `onay` bir kez, en sonda koşar.

- [ ] **Step 1:** **Dört operatör kararını kapat (K-04a–d) — DB'ye yazımdan ÖNCE:**
  gümüş pakete girsin mi · kasım indirim dönemi girsin mi · kampanya-aciliyet istisnası ·
  kültürel sahne eklentisi. Kararlar `docs/active/`'e işlenir.
- [ ] **Step 2:** **K-29=A test markası:** kontrollü kurgu kuyumcu markası açılır
  (kayıtlı iki markanın ikisi de kuyumcu DEĞİL — ölçüldü 2026-08-23).
- [ ] **Step 3:** **Alt sektör satırını aç** (Plan 1'de bilinçle dışarıda bırakıldı,
  korumalar hazır): `sector_sweep.py --database-url ... > before.txt` → satır aç →
  `sector_sweep.py --database-url ... --baseline before.txt` — Beklenen: eşleme farkı 0.
- [ ] **Step 4:** **"Kişisel veri içermez" doğrulaması** (spec §3.7/§14.3) — gerçek veri
  yazımı ve ilk aktivasyondan ÖNCE koşulur.
- [ ] **Step 5:** **K-18 yeniden üretim:** sözleşmeler donduktan sonra üç araştırma
  **tek seferde** yeniden üretilir. Eldeki eski çıktılar test verisi olarak SAKLANIR, silinmez.
- [ ] **Step 6:** Zinciri **sentez adımına kadar** koş: `tur-ac` → `brief-doctor` →
  `denetim` → `sentez`. Her adımın çıktısı koşu klasörüne ve DB'ye iner. **Motor burada
  KOŞMAZ.**
- [ ] **Step 7:** **K-134 çatalı — kalibrasyon tabanı:** operatör YALNIZ sentez çıktısına
  (karar günlüğü + açık sorular) bakar, yargısını yazar ve kaydeder. Motor çıktısı bu anda
  MEVCUT DEĞİLDİR — körlük kalibrasyonun ön koşuludur.
- [ ] **Step 8:** `motor` alt komutunu koş; operatörün kayıtlı yargısıyla motorun kararlarını
  karşılaştır ve farkı koşu raporuna yaz (spec §15.2'nin istediği kalibrasyon verisi).
- [ ] **Step 9:** Yazım kapısı → `draft`; ardından Katman-1 tam sweep + Katman-2 kör
  örneklem koş. Katman-2 **kapı değildir** — koşulması ve sunulması ön koşuldur, sonucu değil.
- [ ] **Step 10:** `onay` (TEK kez) + `aktive-et` (ilk pakette yalnız ikinci adım;
  kanıt `expected_no_active=True`).
- [ ] **Step 11:** **Task 15 elle arayüz doğrulaması (Plan 1'den devralınan borç — evi
  BURASI):** atama arayüzünün üçlüsü (onayla / değiştir / boşalt) + öneri ucunun GERÇEK
  model çağrısıyla koşumu. Bu doğrulama ancak aday küme dolduğunda anlamlıdır; ilk paket
  aktive edildiği an o koşul sağlanır. Ayrıca boş-aday hâlinde bileşenin pasif görünmesi
  ve kanal envanteri alanları — Eray'ın gözüyle, marka ayarları + onboarding sayfalarında.
- [ ] **Step 12:** **Pilot ölçümleri (değer üretilir, kapı ÜRETİLMEZ):** yöneticinin tur
  başına gerçek süresi (K-13 girdisi) · Katman-2 kör örneklem (K-11a) · gerçek alan dağılımı
  (K-12 girdisi) · motor kalibrasyon karşılaştırması (K-134 çıktısı) · bariyer oranlarının
  gerçek dağılımı (K-24/K-130/131/132 kalibrasyon girdisi).
- [ ] **Step 13:** Koşu raporunu yaz ve commit et: `docs: record jewellery pilot official round`

---

### Task 20: Kapanış — kabul eşlemesi · final sweep

**Files:**
- Create: `docs/plans/PLAN2-KAPANIS.md`
- Test: `apps/social/backend/tests/test_plan2_interface_contract.py` (genişletilir)

- [ ] **Step 1:** Tüm test kümesini taze koş: `cd apps/social/backend && python -m pytest tests/ -v`
  — çıktıyı raporla (FAIL sayısı dahil; "geçmeli" DEĞİL, geçen/kalan sayısı).
- [ ] **Step 2:** Katman-1 tam sweep: `cd apps/social/backend && python -m pytest tests/prompt_regression/ -v`
  — Beklenen: tek bayt fark YOK.
- [ ] **Step 3:** **Kabul eşlemesi:** spec §14.1 deterministik çekirdek + §14.2 iş kuralı
  senaryoları + §14.2 motor testleri (13 madde) → kanıtlayan test adı. Kapsam DIŞI kalanlar
  ("pilot sonrası" / "genişleme turu") açıkça etiketlenir. **Mutlaklık iddiası YOK** (İlke 3).
- [ ] **Step 4:** **Sözleşme pin'i son kez doğrula:**
  `cd apps/social/backend && python -m pytest tests/test_contract_pin.py -v` — dış depo ile
  monorepo aynı sürümde mi.
- [ ] **Step 5:** **30 devredilen teknik kalemin tek tek sweep'i:** karar turunun plana
  devrettiği K-ID listesinin her biri için "nerede bağlandı + hangi test kanıtlıyor"
  eşlemesi. Bağlanmamış çıkan varsa dürüst etiketle raporda kalır, sessizce düşmez.
- [ ] **Step 5b:** **13 kapalı ÜRÜN kararının sweep'i (bağımsız hakem itirazı, 2026-08-27).**
  İlk yazımda kapanış yalnız teknik kalemleri sayıyordu; ürün kararları eşlenmiyordu ve
  ölçüldü ki 13'ün 12'si planda kimlikle izlenebilirken **K-133 hiç geçmiyordu**. Sebep
  masum ama kontrolsüz: K-133'ün kararı *"kuru mod KURULMAZ"* — yani doğru uygulama
  **yokluktur** ve yokluk sessizce doğru görünür. **Bağlanan hüküm:** 13 karar tek tek
  eşlenir; K-133 için **yapısal yokluk kontrolü** koşulur — kod tabanında ayrı bir kuru
  koşu kipi, bayrağı ya da dalı YOK (grep-tabanlı, raporlanabilir). Yokluk da kanıtlanır.
- [ ] **Step 6:** `PLAN2-KAPANIS.md`'yi yaz: ne yapıldı · ne kalmadı · **kabul edilen
  riskler açıkça** · **hâlâ açık ürün kararları** (K-85 · K-153 · K-128 · K-52 · K-11 ·
  K-32…K-37) · evsiz kalan hiçbir kalem YOK (İlke 7 — her kalan iş ya tarihli bir eve gider
  ya dürüst etiketle DÜŞÜRÜLÜR).
- [ ] **Step 7:** Commit: `docs: close plan 2 with acceptance mapping`

---

## Self-Review notları (yazım sonrası kontrol edildi)

**Spec kapsama:** §8 hat → Task 2,4,7,8,9,10,11 · §9 motor → Task 12,13 · §9.6 onay yüzeyi →
Task 14 · §10 yaşam döngüsü (Plan 2 ayağı) → Task 15 · §12.2 kanal uzayı kapanışı → Task 2 ·
§13 işletim → Task 16,17 · §13.2 dağıtım sırası → Task 18 · §15 pilot → Task 19 ·
§14 kabul → Task 20 · §3.5 karar günlüğü genişlemesi → Task 3 · §11.1/§11.3 takvim ayağı → Task 5.

**Bilinçle kapsam dışı (evleriyle):** K-32…K-37 genişleme kapıları (pilot sonrası tur) ·
K-52 DNA girdisi (açık ürün kararı) · **K-85 / K-153** semantik eşleştirme ölçütü ve yöntemi
(açık ürün kararları — plan mevcut iddia-düzeyi eşleştirmeyi kabul eder, yeni ölçüt koymaz;
ayırt edilemeyen vaka açık soruya düşüp aktivasyonu bloklar) · K-128'in
"doğrulanamayan mevzuat" dalı (kod yeteneği kurulu, yapılandırma pasif; K-125'in uyuşmazlık
bloklaması bundan AYRI ve aktif) · K-47 yılbaşı kategori tutarsızlığı (spec §17.2
dokunulmaz) · K-10 prompt enjeksiyonu (kapalı: Faz 1'de kurulmaz) · diğer 17 n8n
workflow'unun hata bildirimi (Task 16'nın dar kapsamı — CRM turu).

**Sayaç dürüstlüğü:** Bu plan hiçbir ölçülmemiş sayıyı kapıya çevirmiyor. Kapı yapılan tek
sayısal değer K-127'nin "2 kaynak" tabanıdır ve o **mekanik alt sınırdır** (mutabakatın
mümkün olduğu en küçük sayı), ölçüm iddiası değil. Bariyer eşikleri `None` doğar ve `None`
iken hiçbir şeyi bloklamaz — Task 13'ün `test_barrier_with_none_threshold_never_blocks`
testi bu invariant'ın kapısıdır.

**Plan 1 arayüz değişikliği:** üç kalem — `insert_draft` `decision_log` parametresi (geriye
uyumlu) · `ActivationGateEvidence.expected_no_active` (K-94'ün ilk aktivasyonu ifade
edebilmesi için ZORUNLU; eski "boşsa atla" davranışı kalkar — **davranış değişikliğidir**,
Plan 1'in ilgili testleri güncellenir) · `_update_draft_row` özel ilkeli. Plan 1'in
arayüz-sözleşme testi silinmez, üstüne yazılır.

**Devralınan borçların evi:** Task 15 elle UI doğrulaması → Task 19 Step 11 · n8n hata
bildirimi → Task 16 Step 7 + Task 18 Step 6 (dar kapsam, dürüst etiketli) ·
033/034 down script'leri → Task 6 · K-103 etkin-yetki ölçümü → Task 15 Step 6, uygulaması
Task 18 Step 7.

**Review turu (Codex adversarial, 2026-08-27) — kapatılan sınıflar:** dağıtım-pilot sıra
bağımlılığı · K-94'ün ilk aktivasyonu ifade edememesi · K-99'un kapalı olay kümesine
çarpması · K-128'in hem pasif hem koşulsuz yazılması · köken ispatının tip düzeyinde
kalması · K-106'nın kapı atlatabilmesi · yeniden koşum kimliğinin iki uzayda modellenmesi ·
K-09 indeksinin 032'nin donmuş manifestini düşürmesi · K-100'ün `gerekce` alanını ve tamlık
kapısını kaybetmesi · K-107'nin `koru` satırı yerine nota bağlanması · K-85/K-153'ün
gereksiz ilan edilmesi · K-134 kalibrasyon körlüğünün bozulması · K-45'in üreticisiz ve
müşteri yüzeysiz kalması · 035 geri almasının dönem satırını bozması.

**Bağımsız ikinci hakem turu (2026-08-27, Codex zinciri DIŞINDA).** Onaylanmış plan ayrı
bir hakeme verildi ve **10 itiraz** geldi; **onu da ölçülerek doğrulandı, hiçbiri
reddedilmedi.** En ağırı planın kendi temelindeydi: kalıcı kalıp kimliğinin **saklanacağı
yer yoktu** — ölçüldü ki içerik doğrulayıcısı CTA ve özel gün girdilerini tam anahtar
eşitliğiyle, diğer liste öğelerini düz metin olarak zorluyor; kimlik eklemek reddedilirdi.
Kimlik artık karar günlüğünden türetiliyor ve çift yönlü bütünlük kontrolüyle içeriğe
bağlanıyor (şema göçü YOK). Diğer dokuz: Katman-2'nin kanıt zincirinde olmaması ve hazırlık
listesinin 15. maddesinin sessizce sert kapıya dönmesi · gerçek denetçi çalıştırıcısının
hiçbir göreve yazılmamış olması · bir komutun kendinden SONRAKİ görevde doğan işlevi
kullanması · sır maskeleme kararının uygulayıcısız kalması · yeni n8n artefaktının sözleşme
testlerine sokulmaması · K-145'in üç kuralının provenansa indirgenmesi · canlı dağıtımın
tam test ve güvenlik incelemesinden önce koşması · K-112'nin dikişsiz kalması · takvim seed
değerlerinin uygulayıcıya icat ettirilmesi · kapanış sweep'inin ürün kararlarını
kapsamaması (K-133'ün yokluğu sessizce doğru görünüyordu).

**Bunun kendi review zincirim hakkında söylediği şey:** altı Codex turu tek eksende —
koşu/yazım/onay köken zinciri — daralarak yakınsadı. Daralmayı sağlıklı saydım ve doğruydu;
ama o eksende yakınsamak **diğer eksenlerde körleşmek** demekti. Tek hakem zincirinin
yakınsaması kapsama kanıtı değildir.

**Review turu 5 — düzeltme yaşam döngüsünün kapanışı.** Tur 4'ün düzeltmesi iki çocuk
doğurdu, ikisi de kabul edildi: (a) koyduğum karşılıklı-dışlama kısıtı **yarıda kalmış bir
düzeltmenin kurtarılmasını imkânsız** kılıyordu — yeniden koşum hem yeni kimlik hem düzeltme
soyağacı taşımak zorunda, ikisi dik ilişkiler; dışlama kaldırıldı, devralma kondu.
(b) Aynı taslağa iki düzeltme açılabiliyor ve biri diğerinin onayladığı baytları ezebiliyordu.
**Makine kurulmadı:** tek operatörlü işletimde (K-54 · K-77) iki dar kural yetiyor —
taslak başına aynı anda TEK açık düzeltme, artı aktivasyon anında taslağın `content` ve
`decision_log` hash'lerinin onaylanan görüntüyle karşılaştırılması. İkincisi kaç yazıcı
olduğundan bağımsız olarak sınıfı kapatır: yöneticinin görmediği bayt aktive edilemez.

**Review turu 4 — kardinalite düzeltmesi.** Tur 3'te koyduğum `package_id UNIQUE` kısıtı
istediğimin TERSİNİ zorluyormuş: bir koşu satırı zaten tek `package_id` taşıdığı için
`UNIQUE` "bir koşu → bir taslak" değil "bir taslak → bir koşu" demek oluyordu — ve o kısıt
K-106 düzeltme turunu **imkânsız** kılıyordu (düzeltme yeni bir koşudur ama aynı taslağı
güncellemek zorundadır). Kısıt kaldırıldı; tekilliği kilit + dolu kolon sağlıyor. Yerine
**düzeltme soyağacı** kondu: `duzeltilen_run_id` + `kosu_turu`, reddedilmiş koşuyu kilitleyip
hedefi devralan bir düzeltme-koşusu üreticisi, yazma yolunun düzeltme koşusunu reddetmesi ve
güncelleme yolunun soyağacını şart koşması. Tur 4'te F18 · F19 · K-99 kapandı.

**Review turu 3 — sınıfın kapanışı.** Tur 2'de üç kez aynı hatayı yaptığım anlaşıldı:
düzeltmeyi bir yola uygulayıp kardeş yolda eski hâli bırakmak (yazım yolu yedi kapıya
çıktı, güncelleme yolu beşte kaldı; aktivasyon DB'den doğrularken onay hâlâ çağırandan
alınıyordu). Tur 3'te tek tek yamamak yerine **iki ayrı kapı listesinin var olamayacağı**
bir yapı kondu: `runs.load_verified_run` tek doğrulayıcıdır ve yazım · güncelleme · onay ·
aktivasyon dördü de ondan geçer; anlık görüntü çağırandan alınmaz, kilitli koşudan BASILIR;
onay o görüntünün hash'ine bağlanır. Ayrıca iki gerçek boşluk kapandı: **K-99'un Python
üreticisi** (`package_events.EVENT_TYPES` kapalıydı — yalnız DB CHECK'ini genişletmek onay
olayını yazılabilir yapmıyordu) ve **bir koşu → bir taslak idempotency'si** (cevabı kaybolan
yazım tekrarı aynı koşudan birden çok sürüm yakabiliyordu).

**Review turu 2 (kapanış-doğrulama) — 15/17 kapandı, 5 kalem daha kapatıldı:**
İki bulgu ilk turda EKSİK kapatılmıştı — düzeltmeyi karar katmanına yazıp görev gövdesinde
eski hâli bırakmışım: **F7** (Task 8 hâlâ `attempt` imzaları taşıyordu) ve **F10** (Task 3
hâlâ `kismi-tur-tasima`'yı not sınıfı sayıyordu). İkisi de artık her katmanda tarandı.
Üç YENİ bulgu çıktı ve üçü de birinci turun kendi düzeltmelerinin yan etkisiydi:
**F19** — `write_draft_from_run` çağırandan nesne kabul etmeyi bıraktı, ama koşu satırında
karar günlüğü alanı yoktu; yani yazacak doğru günlük kalmıyordu (`final_decision_log` +
hash eklendi). **F18** — aktivasyon, Katman-1 ve hazırlık listesi onayını boolean olarak
kabul ediyordu; kim ölçtü sorusunun cevabı hiçbir yerde durmuyordu (iki kalıcı tasdik alanı
eklendi, aktivasyon onları DB'den doğruluyor). **F20** — pilot veri ürettikten sonra 036'nın
geri alması ya patlıyor ya denetim izini siliyordu (veri-varken fail-closed ön kontrol +
iki ayrı geri alma rejimi).

**Hâlâ AÇIK ve Eray'a ait:** K-85 (kalıp semantik eşleştirme ölçütü) · K-153 (yöntem: 
deterministik mi hakemli mi — hakemli dal kalıp başına insan kararı doğurur) · K-128
(doğrulanamayan mevzuat bloklaması) · K-52 (DNA verisi motora girsin mi) · K-11(a/b) ·
K-32…K-37. Plan hiçbirini kapatmıyor; belirsiz vakalar açık soruya düşüp aktivasyonu
blokluyor.
