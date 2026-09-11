---
title: Sektör Bilgi Paketi — Plan 2 (işletim hattı)
status: active
started: 2026-08-27
last-touched: 2026-09-11
blocked-by: null
source_plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
---

# Goal

Sektör bilgi paketini ÜRETEN ve AKTİVE EDEN işletim hattını kurmak: sözleşme düzeltmeleri →
`brief-doctor` → iki kör denetçi orkestrasyonu → sentez → politika motoru → onay yüzeyi →
komut ailesi → migration'lar → kuyumculuk pilotu. Plan 1 runtime çekirdeğini kurdu ve
main'de; Plan 2 onun "Plan 2'ye teslim edilen arayüzler" listesini tüketir.

Şu anki aşama: **YÜRÜTME AÇIK.** (2026-09-11: Task 17 indi ve checkpoint 14
`approve` ile kapandı — BEŞ hakem turu sürdü. Sıradaki iş **Task 18**.) Task 1-17 indi. Task 8'in checkpoint'i 2026-09-08'de
KAPANDI: üretim tarafındaki beş yüksek bulgu kapandı ve iki bağımsız kapanış turuyla
doğrulandı; test tarafı (B turu) ayrıca incelendi, dört bulgusu kapandı ve mutasyonla
kanıtlandı. **Durum `active` KALIYOR.** Checkpoint 1, 2 ve **5** hakem `approve`'uyla kapandı;
checkpoint 3 ve 4 koştu ama `approve` ALMADAN kapatıldı — **ikisinin aralığı da checkpoint 5'in
tabanına dâhildi ve artık incelendi.** Checkpoint 6 override ile kapandı. Task 8'in
dispatch'inin önündeki dört kalemlik karar kapısı 2026-09-08'de kapandı (aşağıda).

> **"Sıradaki iş" bu paragrafta ÜÇ kez tekrarlanıyordu ve üçü de ayrı ayrı bayatladı
> (Task 8 → Task 9 → Task 10). 2026-09-09'da TEK eve indirildi: yukarıdaki ilk cümle.**
> Tekrarlanan durum cümlesi bayatlamaya davetiyedir; bir daha çoğaltma.

**Onay tarihçesi (değişmez kayıt, silinmez):** plan onayı hakem zinciriyle değil **Eray'ın
risk kabulüyle** alındı (2026-08-27); o an son iki düzeltme partisi incelenmemişti.

# Execution State

- execute_mode: inline
- execute_started: 2026-08-30 11:36
- execute_start_ref: a806e29a1ea6a2f82e097fb90fe9c6b8c07b7fb9
- ledger_window_ref: a806e29a1ea6a2f82e097fb90fe9c6b8c07b7fb9
- execute_review_log: /root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md
- execute_branch: feat/sektor-bilgi-paketi-plan2
- cp_count: 11
- last_checkpoint_ref: 4a9d98f8ae30c5eb19f97e5fd2d5e31fda5eb361

> **`cp_count` ile düz yazıdaki checkpoint NUMARASI aynı şey DEĞİLDİR — sapma değil, iki ayrı
> sayaç (2026-09-11'de bir oturum açılışını yanılttı, o yüzden burada yazılı).** Numara KOŞAN
> denetimleri sayar (bugün 12); `cp_count` §8.6 mutasyon protokolünün ilerlettiklerini, yani
> Clean/Accepted-risk kapanışlarını sayar (bugün 9). Fark = hakem `approve`'u ALMADAN kapanan
> üç checkpoint (3 · 4 · Task 7-8'inki); üçünde de ilerletmeme BİLEREKTİ ve gerekçesi bu
> dosyada kendi bölümlerinde yazılı. Yön fail-safe: taban geride kaldığı için hakem görmemiş
> commit'ler sonraki turun kapsamına kendiliğinden girer.
>
> **ÖLÇÜLMÜŞ SONUÇ (2026-09-11, `ec_ceiling 20` → 9 · `ec_should_checkpoint 1 9 9` →
> `CEILING_RISK`):** sayaç TAVANA dayandı. Sıradaki riskli task otomatik `RUN_RISK` ALMAZ,
> §8.3a insan-checkpoint'ine düşer. Eray 2026-09-11'de Task 16 için ÖNDEN `RUN-anyway` onayı
> verdi (audit etiketi `ceiling-exceed`); bu onay Task 16 ile SINIRLIDIR.

# References

- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **kanonik**;
  spec damıtmadır, çelişkide girdi esastır
- Plan 1: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`, yürütüldü, arşiv
  `docs/task-archive/2026/08/sektor-bilgi-paketi/`)
- **Boşluk raporu:** `docs/research/2026-08-27-spec-input-bosluk-raporu.md` (`d16f228`)
- **Karar turu:** `docs/research/2026-08-27-plan2-karar-turu.md` (`a1bdc0c`, `cb7accf`)
- Codex ön-analizi: `~/.claude/logs/otomaix--ffc87809/2026-08-27-sektor-bilgi-paketi-plan2.md`
- Kanonik sözleşmeler (ayrı depo): `/root/otomaix-sosyal-medya-arastirmasi/` —
  `_SABLON.md` · `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`

# Current Status

**YÜRÜTME BAŞLADI (2026-08-30).** Plan onaylıydı; yürütme öncesi ön-tarama planda kapatılmamış
çapraz-görev sözleşmeleri buldu, onlar bir **arayüz eki** ile kapatıldı, sonra Task 1 indi.

- **Arayüz eki KAPANDI:** `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`
  (bağlayıcı; çelişkide EK geçerlidir). 17 hüküm — R1–R14 + AÇIK-1 · AÇIK-2 · AÇIK-3.
  Üç Codex karşıt-hakem turundan geçti (high sayısı 7 → 4 → 2); doktrin delikleri kapandı,
  zincir kontrolör kararıyla bitirildi (dördüncü tur AÇILMADI).
- **Task 1 TAMAM** — sözleşme pin doğrulayıcısı, commit `32791b1`. Hakem: spec ✅, kalite onaylı.
- **Task 2 TAMAM** — dış depodaki altı bloklayıcı sözleşme düzeltmesi + 13 kalemlik yansıma
  sweep'i + gerçek pin. Monorepo `1186d44` + `77dd268`; **dış depo** (`/root/otomaix-sosyal-
  medya-arastirmasi`) `6d2a033` + `d901eb4`. Hakem: spec ✅; bir Important + beş Minor düzeltme
  turunda kapandı, yeniden inceleme altısını da ADDRESSED verdi. Task 1'in üç Minor bulgusu
  burada kapandı.
- **Checkpoint 1 KOŞTU** (Codex karşıt-hakem, taban `a806e29`): bir **high** buldu — bozuk
  manifest, fail-closed doğrulayıcıyı geçirebiliyordu (üç yol: hata-işareti commit değeri ·
  mutlak yol anahtarı · `..` gezinmesi). Üçü de ölçümle doğrulandı ve `72f5744` ile kapatıldı;
  kapanış turu **approve** verdi. Kalan tek medium kabul edilmiş risk (aşağıda).
- **Task 3 TAMAM (2026-08-31)** — kalıp kimliği + karar günlüğü şeması (K-84 ailesi).
  `1dd8c5e` (ana) + `411c767` (düzeltme 1) + `a34d3f6` (düzeltme 2) + `ad95846` (düzeltme 3).
  Zincir: hakem turu spec ❌ (3 Important + 5 Minor) → düzeltme 1 → yeniden inceleme (hepsi
  ADDRESSED ama **kendi sınıfından yeni bir Important**) → düzeltme 2 → yeniden inceleme
  (iki kalemin ikisi de KISMEN kapanmış: 2 Important + 2 Minor) → düzeltme 3 → kontrolör
  **sınıfı mekanik kapattı** (47 atıflık üretilmiş matris, 0 hata), dördüncü yargı turu
  AÇILMADI. Test tabanı 744 → 745.
  **Dürüst etiket:** son tur bağımsız bir hakemin "kusursuz" yargısını almadı; kapanış
  kontrolör kararıdır. Gerekçe: üç tur da AYNI ekseni buluyordu (düzeltme metninin kendi
  içinde ölçülmemiş atıf), ve o eksen örnekle değil matrisle kapatıldı.
- **Commit etiketleri düzeltildi (`f79f28f`, Eray onayı).** Defter denetimi iki MECH-FAIL
  veriyordu; altı yerel commit aynı içerikle doğru etiketle yeniden yazıldı, denetim `rc=0`.
  Yedek etiket: `backup/pre-footer-fix-20260830`.
- **Task 4 İNDİ (2026-08-31)** — sözleşme v2. Dış depo `6d5d90db9537b516413d31f091b4d475526bcb73`
  (`master`; önceki `d901eb4` ARTIK ANA HÂL DEĞİL), monorepo `3d08db6` (pin yenilemesi).
  Devralınan üç sözleşme kalemi de kapandı: sürüm damgası çakışması ayrıştırıldı, iki genel
  hüküm kanal maddesinden çıkarılıp kendi başlıklarına taşındı, `[muhtemel-uydurma]`nın bayrak
  sanılması ölçülerek düzeltildi (kapalı bayrak kümesi 8 üye, o küme içinde değil).
- **Checkpoint 2 KOŞTU** (Codex karşıt-hakem, taban `72f5744`): **needs-attention** — 3 high,
  1 medium, 1 low. Kapsam Task 3'ün TAMAMINI da içeriyordu, yani aşağıdaki "düzeltme turu 3
  bağımsız hakem görmedi" borcu bu turda KAPANDI: hakem o aralıkta yeni kusur bulmadı.
- **Düzeltme turu 1 İNDİ (`f15e640`)** — iki high kapatıldı:
  (1) kanonik hash, ekin ileride BAĞLADIĞI girdi biçimlerini (donmuş veri sınıfı demeti,
  kimlik taşıyan yük) kabul edemiyordu; kapalı bir ön-serileştirme kuralı eklendi, eski
  hash'lerin kaymadığı ölçüldü, fail-closed vaadi korundu.
  (2) Bağımlılık sınırı: ekin iki hükmü de ihlal ediliyordu. İçerik şeması + yazım kapısı
  `sector_content_schema.py` yaprağına ÇIKARILDI (kopya değil, taşıma — 27 üst düzey adın
  27'si bayt-aynı ölçüldü) ve üç yapısal AST kapısı ŞİMDİ yazıldı (Task 8'e ertelenmedi).
  Test tabanı 745 → 758.
  **KAPANMAYAN AYAK — dürüst etiket:** ekin "kullanılan TEK ad `identity.canonical_sha`"
  hükmü kapanmadı; yaşam döngüsü gerçekten iki adı daha kullanıyor (şema kapısı orada koşar
  ve kural kopyalanamaz). İmport BİÇİMİ hükme çevrildi, ad kümesi ayağı AÇIK. Kapanması ek
  belgesinin revizyonunu ister — **tasarım katmanının işi, yürütücü ek metnini yeniden
  yazmaz.** Sapma kodda, testte ve commit mesajında etiketli.
- **Checkpoint 2'nin yeniden inceleme turu KOŞTU (2026-08-31)** ve ÜÇ bulgu onaylandı;
  üçü de kontrolörün kendi ölçümüyle doğrulandı, hakemin sözüne dayanmadı.
- **Düzeltme turu 2 İNDİ (2026-08-31).** Üç bulgu TDD ile kapatıldı:
  (F4, high) yapısal bağımlılık kapısı GÖRECELİ ve DOLAYLI import biçimlerini kaçırıyordu —
  `from .. import sector_packages` ve `from app.services import sector_pipeline` mutasyonları
  kapıyı düşürmüyordu (ölçüldü: 3 passed). Çözümleyici artık her düğümü TAM NİTELİKLİ kenara
  çevirir (import EDİLEN ADLAR dâhil; göreceli seviye modülün kendi paket yoluyla
  mutlaklaştırılır; çözülemeyen seviye fail-closed düşer) ve kapanış 44 hücrelik ÜRETİLMİŞ
  sözdizimi matrisiyle kanıtlandı, elle seçilmiş örnekle değil.
  (F3, high) aktif katmanın kendi içindeki çelişkili durum iddiaları — bu sweep.
  (F1, high'a yükseltilmiş medium) `canonical_sha` ortak `int`/`float` dalı `math.isfinite`'ı
  tamsayıya da uyguluyordu; `10**309` `OverflowError` ile patlıyordu. Bu hem eski özeti
  (`7fe8362b13128003…`) hesaplanamaz kılıyor hem de docstring'in `TypeError` vaadini kırıyordu.
  Tamsayı artık değiştirilmeden geçer; sonluluk yalnız `float`'a uygulanır.
  Test tabanı 758 → 914.
- **Checkpoint 2 KAPANDI — tur 3 verdict `approve` (2026-08-31).** Zincir üç tur sürdü ve her
  tur FARKLI bir eksende bulgu verdi (aynı şeyin dar varyantları değil — o olsaydı yeni tur
  açılmaz, çerçeve teşhisi raporlanırdı):
  tur 1 → 3 high + 1 medium + 1 low · tur 2 → 3 high · tur 3 → **approve** + 1 medium.
- **Düzeltme turu 3 İNDİ (`a6e053f`)** — tur 3'ün medium'u kapatıldı. Ölçüm bir ayrım gösterdi:
  `10**4300` **eski kuralda da** düşüyordu (Python'un süreç düzeyindeki basamak sınırı, 4300),
  yani davranış gerileme DEĞİL; **fazla-geniş İDDİA** yeniydi — düzeltme turu 2'de yazılan
  testin adı "her büyüklükte tamsayı kabul edilir" diyordu. İddia ölçülene daraltıldı, eşik
  koddan OKUNUYOR (`4300` hiçbir yere gömülmedi) ve sınır üstü artık docstring'in vaat ettiği
  istisna tipiyle düşüyor. **Süreç güvenlik sınırı YÜKSELTİLMEDİ** (kaynak taraması: yalnız
  "neden çağırmıyoruz" açıklaması var). Test tabanı 914 → 921.
  **Dürüst etiket:** bu son düzeltme bağımsız yargı GÖRMEDİ. **Ev uydurulmadı:** dal
  kapanışındaki final incelemenin tabanı `a806e29` olduğu için bu commit o incelemenin
  aralığına ZATEN giriyor — kendiliğinden kapsanır. Aynı kapsanma yolu bu oturumda bir kez
  ölçümle gerçekleşti (Task 3'ün düzeltme turu 3'ü checkpoint 2 tarafından kapsandı), yani
  bu bir tahmin değil, işlediği görülmüş bir yol.
- **Task 5 KAPANDI (2026-09-06).** Kod indi, çalışıyor; test tabanı **921 → 963**.
  Commit'ler: `331fe7a` · `39379c8` · `16a8ab1`+`a3dd22f` · `d4adea3`+`fc1df7f` ·
  `8d227d2`+`44bd8e2` · `8f596d8`+`389d5e0` · `6120962`+`468be6a` (tur 1-4) ·
  `8add7df`+`bf615aa`+`94eb6a2` (tur 5) · `5c26493`+`60fc75a`+`412a895` (tur 6).
  Defter kapısı her commit'ten sonra koşuldu, hepsi `rc=0`.

- **CHECKPOINT 3 KOŞTU (2026-09-06) — kaçırılan kapı kapatıldı ve karşılığını verdi.**
  Önceki oturum bu kapıyı atlamıştı; kadans kararı taze koşuldu (`ec_should_checkpoint 1 2 9`
  → `RUN_RISK`, 15 commit'in 11'i riskli sınıfta) ve iki Codex turu yapıldı.
  **Tur 1 — 3 high + 3 medium, `needs-attention`.** Dört turluk Claude-ailesi zincirinin
  bulamadığı üç kusur; üçü de kontrolörün KENDİ probuyla, pozitif kontrollü olarak ölçüldü:
  (F1) geri alma sahipliği içerik/şekil eşitliğinden türetiliyordu — 035'ten önce var olan
  birebir satır siliniyordu VE üretici şekilli sonraki-yıl dönemi sessizce düzleşiyordu;
  (F2) kısıt kimliği yalnız ADdan okunuyordu — aynı adla `CHECK (true)` konursa migration
  `rc=0` ile başarılı dönüyor ve ters dönem yazılabiliyordu; (F3) kalıcı DDL düşebilen
  kapıdan ÖNCE koşuyordu — çıplak `psql` + indeks squatter'ı `rc=0` ile yarım şema bırakıyordu.
  **Tur 2 (kapanış-doğrulama) — F2/F4/F5 KAPALI, F1/F3 AÇIK (yeni alt-vakalar).** İkisi de
  yine ölçümle doğrulandı: (F1) silme yüklemi 035'in kendi yazdığı `end_date`'i atlıyordu →
  besleme yalnız dönemi düzeltirse satır sessizce siliniyordu; (F3) **tur 1'in kendi çözümü
  (sabit id) yeni bir yol açtı** → ayrılmış UUID başka satırdaysa şema commit edilip seed
  düşüyordu.
  **Tur 6 ikisini de YAPIYLA kapattı** (sayarak değil): silme yüklemi artık `pg_attribute`den
  türetiliyor ve `IS NOT DISTINCT FROM` ile NULL-güvenli — "bir alan daha unutulmuş" hücresi
  DOĞAMAZ; kalıcı olan her şey tek `DO $apply_035$` deyimine alındı — "şu kapıyı da yukarı
  taşı" ekseni kapandı. Kontrolör ikisinin de kapandığını kendi probuyla ölçtü
  (pozitif kontroller yeşil).
  **Hakemin F6'sı ÖLÇÜMLE REDDEDİLDİ:** "commit'ler tek-commit TDD modelini ihlal ediyor"
  dedi; ölçüldü ki yürürlükteki S1 footer grameri `Exec-Kind: red-only`/`green-only` ayrımını
  AÇIKÇA meşru sayıyor, commit'ler tam o kind'leri taşıyor ve defter kapısı `rc=0` veriyor.
  Önerisi (squash) incelenmiş commit'leri yeniden yazardı.

- **DÜRÜST ETİKET — tur 6 bağımsız hakem yargısı ALMADI.** Üçüncü inceleme turu **Eray
  kararıyla açılmadı** (2026-09-06: zincirin süresi maliyetli bulundu). Kapanış kontrolör
  kararıdır, hakem `approve`'u DEĞİLDİR. **Ev uydurulmadı:** dal kapanışındaki final
  incelemenin tabanı `a806e29` olduğu için tur 5 ve tur 6 commit'leri o incelemenin aralığına
  ZATEN giriyor. Aynı kapsanma yolu bu görevde iki kez ölçümle gerçekleşti.
  **`cp_count` ve `last_checkpoint_ref` BİLEREK İLERLETİLMEDİ** — §8.6 mutasyon protokolü
  yalnız Clean/Accepted-risk dallarında koşar, bu koşum onlardan biri değil. Sonuç fail-safe
  yöndedir: sonraki checkpoint'in tabanı `a6e053f` kalır, yani hakem görmemiş tur 5/6
  commit'lerini kendiliğinden kapsar.

- **KONTROLÖRÜN ÖNERİLERİ YİNE ÖLÇÜMDE YANLIŞ ÇIKTI (bu oturumda 2 kez daha).**
  (1) F1 için kalıcı `m035_seed_provenance` tablosu önerdim; uygulayıcı reddetti — satırlara
  sabit `id` vermek aynı ayrımı yeni kalıcı nesne açmadan kuruyor, şema yüzeyi büyümüyor.
  (2) F3 için "düşebilen kapıyı yukarı taşı" önerdim; uygulayıcı ölçtü ve reddetti —
  `ON_ERROR_STOP` yokken psql hatadan sonra devam ediyor ve sonraki `ALTER TABLE` yine
  commit ediliyor. **Ders sabit: dispatch'e taşınan öneri aday'dır, cevap değil.**

> **KALDIRILDI (2026-09-08).** Burada "yürütme defteri (kanonik ilerleme + tüm kararlar):
> `.superpowers/sdd/.../progress.md`" yazıyordu. O dizini Superpowers'ın
> `subagent-driven-development` skill'i kendi kendine yazar, `.gitignore`'u `*` olduğu için
> git'e hiç girmez ve bu projenin task-handoff yapısının parçası DEĞİLDİR. **Kanonik kayıt bu
> dosyadır (TASK.md); yanında HANDOFF.md ve git defteri.** Başka defter yok.

- **Task 6 TAMAM (2026-09-06)** — migration 036 (koşu kaydı · politika raporu · onay anlık
  görüntüsü · atama geçmişi) + `033_down.sql` / `034_down.sql` / `036_down.sql` + iki donmuş
  sözleşmenin sürüm-farkında yapılması. Sekiz commit: `6694b0b` `d1edd51` `c53ec9d` `1fb98d6`
  (ana) + `d1a1091` `93c8120` `c73f9b0` `5db07b1` `7b0bc86` (beş düzeltme turu).
  Hakem turu: **spec ✅, kalite onaylı**, Critical yok, 2 Important + 7 Minor.
  Zincir: Important'lar → tur 1 → yeniden inceleme (ikisi de ADDRESSED, **iki yeni Important**)
  → tur 2 → yeniden inceleme (ikisi de ADDRESSED, iki küçük kalem) → tur 3 → yeniden inceleme
  (biri ADDRESSED, biri **yeni bir şekilde yanlış**) → tur 4 → kontrolör iki örnek daha buldu →
  tur 5 → yeniden inceleme (**S1 ADDRESSED**, bir yeni Important) → **KAPAK, kesici çalıştı.**
  Test tabanı: 963 → 965 → 1133 → 1175 → 1176 → 1179 → **1181**, hiç düşmeden. Her sayı
  kontrolörün KENDİ taze koşumundan, sessiz veritabanında.

- **CHECKPOINT 4 KOŞTU (2026-09-06) — iki Codex turu, taban `a6e053f`.** Kapsam Task 5'in hakem
  görmemiş tur 5/6 commit'lerini VE Task 6'nın tamamını içeriyordu (tasarım gereği: `cp_count`
  ilerletilmediği için taban geride kalmıştı).
  **Tur 1 — 2 high + 1 medium + 1 low, `needs-attention`.** Dördü de kontrolörün KENDİ ölçümüyle
  doğrulandı, hakemin sözüne dayanılmadı:
  (F1, high) bağlayıcı ekin ayak (d) hükmü UYGULANMAMIŞTI — onaylanmış geri alma planının
  kimlik/hedef alanları değiştirilebiliyordu; 036'nın kapalı tetikleyici manifesti `<yok>` diyordu.
  (F2, high) onay/ret denetim satırı **yalnız boşluktan ibaret** bir aktör kabul ediyordu
  (`bool(actor)` kapısı; `package_events.actor` kolonunda ne NOT NULL ne CHECK var — ölçüldü).
  Kapı bu partiden ÖNCE de zayıftı, ama parti onu kimliğin en çok önemli olduğu yüzeye taşıdı.
  (F3, medium) `036_down.sql` kilitleri üretici yönünün TERSİNDE alıyordu → deadlock penceresi.
  (F4, low) bir test açıklaması güncel davranışı yanlış anlatıyordu. **Kontrolör hakemi daralttı:**
  aynı dosyadaki diğer iki "beş alan" cümlesi geçmişi anlatıyor, onlar doğru — dokunulmadı.
  **Tur 1'in F6'sı ölçümle reddedildi** (yine "tek-commit TDD ihlali"; S1 grameri `red-only`/
  `green-only` ayrımını açıkça meşru sayıyor, defter kapısı `rc=0`).
  **Düzeltme turu 1 İNDİ:** `7071ffa` + `8362f5f` + `4d293bb` + `16f9fe7`. Test tabanı 1181 → 1436.
  **Tur 2 (kapanış-doğrulama) — F1·F2·F3·F4 KAPALI doğrulandı, hiçbiri yeniden açılmadı**, ama
  fix diff'inin İÇİNDE yeni bir high çıktı:
  (F7, high) migration aynı adı taşıyan **YABANCI** bir fonksiyonu/tetikleyiciyi sessizce
  devralıyordu — üç çiftin üçü de koşulsuz `CREATE OR REPLACE` / `DROP TRIGGER IF EXISTS` ile
  yazılıyordu ve kapalı manifest bunu YAKALAYAMAZ (ezme işleminden SONRAKİ durumu okur).
  **Kontrolör doğruladı ve sınıfı adlandırdı:** aynı dosya bu disiplini KISITLAR için zaten
  uyguluyor (KAPI 2 / KAPI 3, `pg_get_constraintdef` + `contype` + `convalidated`); açık kalan
  fonksiyon/tetikleyici VARYANTIYDI — daha önce kapatılmış bir sınıfın gözden kaçmış ayağı.
  **Düzeltme turu 2 İNDİ:** `9a65c0e` + `4b1e354` + `5d42db5`. KAPI 4 kalıcı DDL'den ÖNCE koşuyor
  (ölçüldü: satır 277, "BURADAN SONRASI KALICI" satır 348), `036_down.sql` aynadaki eşini taşıyor
  (kapı satır 245, ilk `DROP` satır 313). Tetikleyici metni TEK KAYNAK: aynı sabit hem kimlik
  karşılaştırması hem tetikleyici yaratımı hem manifest beklentisi.
  **Uygulayıcı kendi düzeltmesinin yan etkisini kendisi yakaladı ve kayda geçir:** gövdeleri
  `DECLARE`e taşımak F1 ve F3'ün ayrıştırıcılarını bayatlattı; iki testin **boş-küme kontrol
  kolları ateşledi** (iddialar hâlâ doğruydu, okuyucuları bayatlamıştı) ve `5d42db5` ikisini de
  kavramdan yeniden türetti. Kontrol kolu tam da bunun için vardı.
- **CHECKPOINT 4 `approve` ALMADAN kapandı — Eray kararı (2026-09-06): oturum burada kapanacak.**
  Üçüncü tur AÇILMADI, yani **F7 düzeltmesi bağımsız hakem yargısı GÖRMEDİ.**
  **Ev uydurulmadı:** `cp_count` ve `last_checkpoint_ref` yine BİLEREK ilerletilmedi (§8.6 mutasyon
  protokolü yalnız Clean/Accepted-risk dallarında koşar; bu koşum onlardan biri değil), dolayısıyla
  sıradaki checkpoint'in tabanı `a6e053f` KALIR ve bu turun yedi commit'ini kendiliğinden kapsar.
  Aynı kapsanma yolu bu görevde daha önce iki kez ölçümle işledi.
  **Dürüst etiket: kapanış kontrolör kararıdır, hakem `approve`'u DEĞİLDİR.**
- **Kontrolörün ölçümleri (hepsi bu oturumda, kendi koşumları):** tam test kümesi giriş `1181` →
  düzeltme turu 1 sonrası `1436` → düzeltme turu 2 sonrası **`1452 passed in 453.65s`**, exit 0,
  temiz ağaçta; defter kapısı her turda `rc=0`; `ec_should_checkpoint 1 2 9` → `RUN_RISK`;
  `command-blocks-maint.sh verify` → PASS.

## Bilinçli bırakılan dört kalemin kapanışı + checkpoint 5 (2026-09-07)

Eray'ın talebi: "bilinçli bıraktıklarımızı bitirelim, arkada iş bırakmayı sevmem." Dördü de
ele alındı; ikisi kapandı, biri kapandı ve YENİ bir kalem doğurdu, biri hakem turuyla kapandı.

1. **n8n canlıya import — KAPANDI.** Yedi workflow yüklendi (yalnız `nodes`+`connections`;
   `settings` ve `name` canlıdan korundu). Yükleme sonrası tek tek ölçüldü: çıplak token **0**,
   credential bağlı, yedisi de aktifti. **Yüklemeden ÖNCE iki depo kusuru bulundu ve
   düzeltildi** — körlemesine import canlıyı bozardı (var olmayan credential kimliği `id=1`;
   CRM-3'ün yarım kalmış webhook yolu). İki sınıf kapısı eklendi.
   **Ölçülmeyen, etiketli:** `telegramApi` credential'ının canlı token taşıyıp taşımadığı —
   hiçbir koşum Telegram düğümüne ulaşmadı.
2. **DDL nesne kimliği sınıfı — KAPANDI.** Beş dosya (001·023·026·032·rollback/032_down).
   Kanonik sabitler dosyaların kendi metinlerinden türetildi. Yeni test modülü sınıfı kapatıyor:
   dosya listesi de nesne listesi de kavramdan türetiliyor, mutasyon kolu kapının ETKİSİNİ
   ölçüyor ve zararın iki biçimini ayırıyor (yazan dosya ezer · bağlanan dosya yabancı gövdeye
   bağlanır).
3. **Checkpoint 4'ün `approve` borcu + görülmemiş yedi düzeltme commit'i — KAPANDI.**
   Checkpoint 5, taban `a6e053f`, iki tur. Tur 1 `needs-attention` (3 high, 3 medium), tur 2
   **`approve`**. Beş bulgunun beşi de kontrolör tarafından yeniden ölçüldü; biri (H2) geri
   alınan bir transaction'da ampirik olarak kanıtlandı, biri (H1) ölçüm sonucu ÖNCEDEN VAR olan
   bir yüzey çıktı, biri (M3) gerekçesiyle REDDEDİLDİ.
4. **YENİ KALEM DOĞDU — kimlik doğrulamasız CRM webhook'ları + SQL enterpolasyonu.**
   Bu partinin ürünü DEĞİL; canlıda ölçüldü, üç workflow **pasife alındı** (Eray kararı),
   gerçek onarım CRM turuna evlendirildi. Ayrıntı CURRENT.md'de.

**Test tabanı:** 1452 → 1493 → **1499**, hiç düşmedi (üçü de kontrolörün taze koşumu).

## Task 7 + checkpoint 6 (2026-09-07)

- **Task 7 İNDİ** — `brief-doctor` mekanik girdi kapısı, commit `d7827e4`. Kontrol kümesi
  spec-input §7.3 tablosunun dokuz satırından **sekizi** (dokuzuncusu — görsel alanlarda metin
  unsuru — o tablonun kendisi tarafından bugün denetçinin kuralı sayılıyor, gerekçesiyle
  dışlandı). **12 kontrol, 8 aile, hepsinin seviyesi `not`** — İlke 9 uyum hükmü gereği eleme
  üreten kontrol kümesi BOŞ ve dört düzeltme turu boyunca öyle kaldı.
  Sözleşme sabitleri (sekiz alan adı · dört tür etiketi · dört kanal anahtarı · beş bölüm harfi)
  elle yazılmadı: testte pinli sözleşmeden hash doğrulanarak çıkarılıyor.

- **CHECKPOINT 6 KOŞTU — SEKİZ Codex turu, taban `2b468e8d`.** Aralık checkpoint 5'in kapanış
  belgelerini de içeriyordu (mutasyon protokolü gereği `last_checkpoint_ref` yazımdan ÖNCEKİ
  HEAD'e set edilir), yani o iki commit de ilk kez hakem gördü.
  **Tur 1:** 2 high + 1 medium. **Tur 2:** F1/F2 yeniden açıldı (yeni alt-vakalar) + 2 medium.
  **Tur 3:** F1/F2 yine yeniden açıldı + F5 kısmi.
  **Beş bulgunun HEPSİ ve her turdaki yeniden açılma kontrolörün KENDİ probuyla doğrulandı** —
  hakemin sözüne hiçbir turda dayanılmadı. Bir vakada (F5, tur 3) kontrolörün ilk probu bulguyu
  ÜRETEMEDİ; prob sorgulandı, zayıf olduğu görüldü, güçlendirilince bulgu birebir çıktı.

- **§8.5'in "2.-reopen" DUR koşulu ateşlendi ve otonom döngü DURDURULDU.** Üç tur aynı iki
  ekseni getiriyordu; dördüncü bir nokta-düzeltme turu açmak yerine çerçeve teşhisi Eray'a
  sunuldu. **Eray kararı (2026-09-07): kapanabilirler kapatılsın, kapanamayan kalem dürüstçe
  ilan edilsin, kök çözüm ayrı iş olarak kaydedilsin.**

- **TUR 4-8: BEŞİ DE `approve`.** Eray "codex sayısı önemli değil, task'lar eksiksiz bitsin" dedi
  ve zincir sürdürüldü. Her tur `approve` + TEK medium verdi, her medium bir öncekinden dar —
  salınım değil yakınsama. **Tur 7'de kontrolörün "her şey mekanik olarak kapandı" iddiası
  hakem tarafından KANITLA REDDEDİLDİ:** kalan açıkların bir kısmı mekanik olarak kapatılabilir,
  hiçbiri high değil. İddia düzeltildi.

- **ON DÖRT düzeltme turu indi.** Kapanan sınıflar, hepsi kontrolörün KENDİ probuyla doğrulandı:
  · **kaynak kimliği** — hiç yok → birebir ad → kanonik ad+içerik denkliği → özetsiz rapor sayılmaz.
  · **iç içe koleksiyonda tekrar/sıra kaybı** — bölüm+alan → dönem/havuz/eşleme; üretilmiş matris.
  · **kapsam beyanı** — çağıran uydurabiliyordu → `CHECKS`'ten türeyen `init=False` alan.
  · **yem tablonun gerçek tabloyu gizlemesi** — BEŞ tur sürdü. Kök neden bir **fail-open geri
    dönüş**tü; kaldırıldı ve yerine bir **DEĞİŞMEZ** kondu: *"tablo eklemek var olan notu
    kaldıramaz"*, ilkeli istisnası yapısal (`kap_iddiasi_mi`), mesaj metnine DEĞİL.
  · **bulgu sınıflandırması** — mesaj önekine dayalıydı ve iki yönde de kırıldığı ölçüldü →
    her bulgu kategorisini üretildiği yerden taşır; beyan edilmeyen yol fail-closed bloğa-ait.
  · **kod çiti** — dilsiz çit kabı dolduruyordu → doluluk, sonra KARDEŞ SİTELER (adet sayımı ·
    bölüm boşluğu · eşleme · tablo tanıma), sonra bağlam (madde altı · girintili · tilde ·
    dört backtick), en sonunda **ayrıştırmanın tamamı**.
  · **çit içinde başlık → TAM YUVA SAHTECİLİĞİ** — belgeden tamamen silinmiş bir alan, dilsiz
    çit içine konan sahte başlık + maddelerle dolu ve eksiksiz gösterilebiliyordu (ölçüldü:
    `notlu-gecti/2 not` → `gecti/0 not`). Çit maskesi artık belgenin TAMAMI üstünde, BİR KEZ,
    **ayrıştırmadan ÖNCE** hesaplanıyor.

- **BAYAT BEYAN ALTI KEZ YAKALANDI.** Kapsam beyanları ölçümle yalanlandıkça düzeltildi; sonunda
  envanterin KENDİSİ tripwire'a çevrildi (ilan edilen her açık biçim için, o biçimin gerçekten
  not kaldırdığını uçtan uca ölçen bir test). **Kontrolörün Eray'a aktardığı bir iddia da
  yanlıştı ve düzeltildi:** `baslik-ve-bolum-tanima` yolunun "fail-closed, yalnız not ekler"
  olduğu söylenmişti; ölçüm NOT KALDIRDIĞINI gösterdi.

- **KONTROLÖRÜN ÖNERİSİ/TEŞHİSİ ALTI KEZ ÖLÇÜMDE YANLIŞ ÇIKTI, KENDİ PROBU DÖRT KEZ YANILTTI.**
  Prob hataları: fazla masum vaka · boş gövdeli çit (gövdeli olanı kaçırdı) · not SAYISI
  karşılaştırması (küme yerine) · yanlış yuva tipinde deneme. Üçünde de ilk okuma "sorun yok"
  diyordu. **Ders: kapanış SAYIYLA değil mesaj KÜMESİ farkıyla kanıtlanır.**

- **Kontrolörün önerileri bu turda İKİ KEZ daha ölçümde yanlış çıktı** (görevdeki toplam beşe
  çıktı): (1) "kapsam sınırını bulgu olarak rapora düş" dedim — uygulayıcı ölçtü, o çözüm HER
  kaynağı `notlu-gecti` yapıp pozitif kontrolü düşürürdü; bulgu-olmayan beyan alanı kurdu.
  (2) Hakemin "içerik özeti kimliğe bağlansın" önerisini uygulayıcı tek başına yetersiz buldu ve
  ölçtü — özet yazım takma adlarını çözmüyor; iki ayaklı tek denklik bağıntısı kurdu.
  **Ders sabit: dispatch'e taşınan öneri aday'dır, cevap değil.**

- **Kontrolörün kendi kapanış taraması:** uygulayıcı "Task 9/12 tüketicileri yeni `dur=True`
  dalına karşı denenmedi, çağıran taraması YAPMADIM" diye dürüstçe bildirdi. Kontrolör taradı:
  modül ve kendi testi dışında depoda **hiçbir atıf yok** — davranış değişikliği bugün hiçbir
  şeyi kıramaz. Varsayımla değil ölçümle kapandı.

## Task 7 — checkpoint 6'nın devamı (2026-09-07, ikinci oturum)

Bu oturum tek bir ekseni kapattı: **çit maskesi**. Üç hakem turu koşuldu (9, 10, 11) ve
zincir kontrolör kararıyla BİTİRİLDİ — dördüncüsü açılmadı.

- **Tur 9** iki medium bildirdi (girintili kök çiti · bitişik kök ayıracı). Kontrolör kendi
  probuyla ikisini de doğruladı ve **etiketi tartıştı:** aynı dosyada aynı şekilli bir bulgu
  daha önce `[high]` almıştı (*"structurally invalid reports are silently classified as
  clean"*). Eray'ın kararıyla P1 **high** sayıldı ve otonom düzeltme döngüsü açıldı.
  `4d107e8` indi: kap üyeliği ham girintiye eşitlenmişti ve kapatıcı kap kontrolünden ÖNCE
  koşuyordu; ikisi de düzeltildi, matris iki kavramsal eksende genişledi.
- **Tur 10** `needs-attention` + bir **high**: `_kapatici_mi` kapatıcının GİRİNTİSİNE hiç
  bakmıyordu. Beş varyant bildirildi; kontrolör **üçünü doğruladı, ikisini yanlış-pozitif
  olarak ölçtü** (gramere sorularak).
- **ÇERÇEVE TEŞHİSİ — altıncı sınır kuralı YAZILMADI.** Tur 8'den beri her tur CommonMark'ın
  kodlanmamış bir kuralını getiriyordu. Eray'a üç seçenekli çerçeve teşhisi sunuldu; **(A)
  seçildi:** maske `markdown-it-py`'ye devredildi (`4167401`), elle yazılmış durum makinesi ve
  dört yardımcısı SİLİNDİ. Bu, yürütme protokolünün **M6** hükmünün karşılığıdır — dış gramer
  modelleyen guardrail'de çalıştırılabilir ground-truth ZORUNLUDUR ve hiç kurulmamıştı.
- **Tur 11** `needs-attention`: ayrıştırıcının `maxNesting` koruması bir fail-open üretiyor.
  Kontrolör doğruladı ve **sınırı ölçtü** (10'da kapalı, 11'de açık). `cad705c` indi.

**Bu oturumun kalıcı dersleri:**

- **Beklenti GRAMERE bağlandı ve GÜÇLENDİ.** Eski iddia "çit eklemek not kaldıramaz" idi ve
  enjeksiyon NOKTASINI yok sayıyordu; ölçüldü ki bazı noktalarda blok hiç çit açmaz ve içerik
  GERÇEKTEN görünür olur. Yeni iddia: bir not ancak içerik gramere göre görünürse düşebilir.
- **Oracle İMPLEMENTASYONDAN BAĞIMSIZ olmalı.** İlk yazımda beklenti `bd._cit_maskesi`'yi
  okuyordu; ölçüldü ki o fonksiyonu değiştiren her mutasyon beklentiyi de kaydırıyor ve
  mutasyon kolları SESSİZCE yeşile dönüyordu.
- **Gönderdiğimiz her elle yazılmış makine DONMUŞ MUTANT olarak testte yaşıyor** (tur9 · tur10 ·
  tur12); her biri en az bir kaçış bırakıyor, bugünkü maske hiçbirini bırakmıyor. Bağımlılığın
  yerini hak ettiği bir iddia değil, ölçülen bir farktır.
- **`dört boşluk` bağlamı matristen ÇIKARILDI.** CommonMark'ta 4 sütun girinti çit AÇMAZ; onu
  çit bağlamı saymak ölçtüğünü sandığın şeyi ölçmemekti. Girintili kod bloğu maskeye AYRI
  olarak dahil (`code_block`).
- **PROB HATASI ÜÇ KEZ.** Sahte içerik kapatıcıdan ÖNCE konmuştu · iç içe yuvalama sözleşmenin
  GERÇEK maddeleriyle kurulmuştu (kabı meşru doldurdular) · tripwire çökme beklentisiyle
  yazılmıştı. **Üçü de İNANDIRICI sonuç verdi.** Her birinde `md.render(doc)` beş saniyede kesin
  cevabı verdi ve o adım en sona bırakılmıştı. Görevdeki prob-hatası sayısı dörtten YEDİYE çıktı.
- **YÜKSELTMEDE GERİ ALMA.** `maxNesting` önce 1000 denendi, bütün derinlikleri kapattı — ama
  tripwire o eşikte 1200 kat iç içe blockquote'un ayrıştırıcıyı `RecursionError` ile düşürdüğünü
  gösterdi: fail-open'ı kapatan değişiklik bir ÇÖKME yolu açıyordu. 100'e çekildi.

## Sözleşme görevi — DÖRT AYAK DA İNDİ, görev KAPANDI (2026-09-07)

`brief-sozlesmesi-kaynak-bolumu-makine-okunur` görevinin dört ayağı da indi;
gövde o görevin kendi dosyasında yaşar. Dördü de Eray kararıyla: 1-3 kontrolör kararı + veto
hakkı, **4. ayak (a) seçeneği Eray'ın kendi kararı** (iddia başına bir satır).

- Dış depo `7964ed6`: `ÇIKTI FORMATI` yapısal sözleşmeye çevrildi.
- Monorepo `868f50a`: pin yenilendi; testin sütun türetmesi düzyazı cümlesinden **birebir
  başlık satırına** taşındı.
- **`tarih` sütunu OKUYARAK eklendi**, tasarlayarak değil: Bölüm 2 "yayın tarihini Bölüm C'de
  belirt" diyor ve denetçi sözleşmesi "TARİHLİ güncellik" arayan bir güçlü-kaynak testi koşuyor.
- **4. ayak — monorepo `854373d`:** kapının Bölüm C ailesi olumsuz çıkarımdan **olumlu yapısal
  sözleşmeye** çevrildi (birebir başlık satırı · altı sütun · hücre doluluğu · `alan/dönem`
  kapalı kümesi · `iddia` kelime sınırı · `URL` biçimi · `tarih` yazımı · `tek kaynak` kümesi)
  ve **BÜTÜNLÜK** eklendi: her alan/dönem için en az bir kaynak satırı aranıyor. Task 7'nin
  "makineyle DOĞRULANMADI" kapsam beyanı ÜÇ yerden de KALKTI. Serbest düzyazı kaçışı artık
  NOT üretiyor; onu ilan eden tripwire testi ateşlendi ve TERSİNİ ölçüyor.

## Task 10 TAMAM (2026-09-09) — iki kör denetçi orkestrasyonu

Dokuz commit: `e83e9d4` (CLI ölçümü) · `0503bd0` (iskelet + kırmızı küme) · `df92c0b` (ana) ·
`29fd099` · `47cb0da` · `1588f89` · `4c868c6` · `3af4331` (beş düzeltme turu). Tam küme
**3595 passed** (`python -m pytest tests/ -q`, 294.20s, exit 0); taban 3458 → 3595.

**Step 3a ÖLÇÜLDÜ, uydurulmadı:** üç aracın komut satırı kurulu CLI'lardan ölçüldü ve donduruldu
(`docs/research/2026-09-09-denetci-cli-olcumu.md`; `claude 2.1.266`, `codex-cli 0.151.0`).
Ölçüm iki hatayı yakaladı — argv'ye konan `--search` bayrağı `codex exec`'te YOK, ve ölçüm
probunun kendisi var olan bir bayrağı "yok" raporluyordu.

**Checkpoint 7 — BEŞ hakem turu** (1 tam inceleme + 4 kapanış-doğrulama), taban `f1f897c`.
Taban BİLEREK daraltıldı: `2b468e8d` yerine Task 9 düzeltmesinin hemen öncesi. Gerekçe ölçüldü —
devir notu "`a488769` hakem görmedi" diyordu ama 2026-09-08 20:05 turunun kapsama ifadesi onu
ADIYLA sayıyor; buna karşılık devir notunun HİÇ saymadığı `4831015` (Task 9'un iki
`needs-attention` verdict'ini kapatan düzeltme) hakem GÖRMEMİŞTİ.

Kapanan bulgular: kaynak-rapor eşleşmesi · sözleşme baytlarının yeniden okunması (F1, F2 —
`4831015`'te kapanmış, bu turda doğrulandı) · URL tamlığının yetkili sayıya bağlanması (F3) ·
K-79 körlüğünün yol ayağı (F5) · K-82 istisna koruması (F6) · koşu kimliğinin pakete bağlanması
(F7) · prob dönüşünün tip kapısı (B5) · rol başına kanıt kalıcılaştırma (B6) · paket kiralaması
ve koşum anı bayt bütünlüğü (B7) · yapım sonrası kök symlink kaçağı (B7-symlink).

**Kapanış ÜRETİLMİŞ MATRİSLE kanıtlandı:** 28 → 52+ hücre (kapı × çıkış yolu × arıza rolü ×
prob tipi × mutasyon × kiralama × symlink zamanı), `parametrize` ile üretiliyor, boş-küme
kontrol kolu var. Her kapı için mutasyon kanıtı alındı; kırmızıya dönmeyen iki kapı GİZLENMEDİ,
kapsam olarak ilan edildi (kardeş-ağaç karşılaştırması ve göreli-kök hücresi).

**K-14 GERÇEK KAPIYA çevrildi.** Önceden ön kontrol koşuyor, sonucu yazılıyor ama HİÇ
okunmuyordu; üstelik başarısızlık URL doğrulamasını tümden atlama iznine dönüşüyordu — kural
ters yönde çalışıyordu. Artık dört durum ayrı: erişim var · erişim yok · ölçülmedi · ölçüm
arızalandı. Turu yalnız birincisi başlatır, muafiyeti yalnız ikincisi meşrulaştırır.

## Task 11 TAMAM (2026-09-09) — sentez koşumu + çıktı doğrulayıcı

Üç commit: `0f4a20c` (iskelet + kırmızı küme) · `0f39d0c` (ana) · `a44d9ec` (düzeltme turu).
Tam küme **3649 passed** (`python -m pytest tests/ -q`, 299.03s, exit 0); taban 3595 → 3649.

**Yürütme kipi bu görevde `inline`** (Eray talebi). Task 1-10 alt-ajanlıydı; kip alanı
güncellendi, kapılar değişmedi.

**Checkpoint 8 — İKİ tur** (1 tam inceleme + 1 kapanış-doğrulama), taban `3af4331`.
Tur 1: `needs-attention`, altı yüksek + iki orta. Tur 2: **`approve`, maddi bulgu yok.**

Kapanan yüksek bulgular: koşu kimliği grameri (mutlak kimlik hedef kökünü sessizce
düşürüyordu — ölçüldü) · tur ↔ aktif paket görüntü bağı · çıkarma kanıtının statü
dizgesinden doğrulanmış-referans TAM eşleşmesine çevrilmesi · churn korumasının karar
etiketinden birimin düşmesine taşınması (`kirp` kaçağı) · sonuç içeriğinin derinlemesine
dondurulması.

**Altıncı yüksek bulgu kod değil SAHİPLİK kalemiydi** ve reddedildi + yeniden evlendirildi:
aşağıda Open Problems'ta.

**Bilinçle DAR tutulan iki kol (kapsam beyanı, sessiz değil):**
- `kanit` alanındaki `#<no>` biçimi bu katmanda ÇÖZÜLEMEZ (denetim tablosu satırları tipli
  nesneye ayrıştırılmıyor). Çözülemeyen referans çıkarmayı AÇMAZ; madde açık soruya düşer.
  Fail-closed yön; yanlış-pozitif riski var ve kabul edildi.
- `risk_unverified` de çıkarma açmaz. Sonuç kayıp değil açık sorudur.

## Task 13 TAMAM (2026-09-09) — motor sonuç katmanı + checkpoint 10

Dört commit: `8b569a0` (ana) · `3365574` · `5d7c1ab` · `33bfae6` (üç düzeltme turu).
Tam küme **3876 passed** (`python -m pytest tests/ -q`, 302.66s, exit 0); taban 3774 → 3876.
Testler: 102 (`tests/test_policy_engine_outcome.py`).

**Checkpoint 10 — DÖRT tur** (1 tam inceleme + 3 kapanış-doğrulama), taban `692e4d9`.
Tur 1: `needs-attention`, DÖRT yüksek + bir orta + bir düşük. Tur 2: F1-F6 kapalı doğrulandı,
BİR yeni yüksek (F7). Tur 3: F7 kapalı doğrulandı; `approve` verdi ama **cümle ortasında kesildi**
(rc=1) — başladığı probu bitirmeden. Kontrolör o ölçümü tamamladı: şüphe GERÇEKTİ (F8).
Tur 4 **HİÇ KOŞMADI** — Codex kota sınırı (20:34'e kadar).

**Kapanan yüksek bulgular:** (F1) `koru` satırı "değişmedi" derken aday yükü farklıysa değişiklik
kanıt/mutabakat/bariyer üçünü birden atlıyordu · (F2) kabul edilen çıkarma günlükten ve uygulanan
kümesinden düşüyor, reddedilen çıkarma iki satır üretip günlüğü geçersiz kılıyordu · (F3) donmuş
yapılandırılmış değer yazım kapısına takılıp sıradan bir kanıtsız güncellemeyi bloklıyordu ·
(F4) geri konan çıkarma ham sıra numarasına yerleşiyordu · (F7) takvim yüklemi yalnız adaya
baktığı için geri koyma takvim kapısını atlıyordu.

**Orta/düşük:** (F5) bir birim iki sebeple reddedilince kararsızlık oranı şişiyordu · (F6) "tek
kural, iki tüketici" iddiası yanlıştı · (F8) düşen-birim sayımına takvim anahtarı karışıyordu.
Üçü de kontrolörün KENDİ ürettiği gerilemeydi; `accepted_risk`'e ALINMADAN düzeltildi.

**Ölçüm:** altı bulgunun altısı + F7 + F8, kontrolörün kendi probuyla doğrulandı (ezberden kabul
YOK). ON yeni kapının ONU mutasyonla kanıtlandı (kapıyı sustur → hedef test kırmızı).
Sıra sınıfı ÜRETİLMİŞ matrisle kapatıldı (konum × kabul × çıkarma × yinelenen değer + boş-küme
kontrol kolu), elle seçilmiş örnekle değil.

**DÜRÜST BOŞLUK:** F8'in kapanışını bağımsız hakem GÖRMEDİ (kota). Kapanış kontrolörün ölçümüne
dayanır; aralığı Adım 11'in koşulsuz final incelemesi kapsayacak.

## Task 14 TAMAM (2026-09-10) — onay yüzeyi + checkpoint 11

Dört commit: `4bbbc3e` (ana) · `83ab8ab` · `cc56fdc` · `576569e` (üç düzeltme turu).
Tam küme **4002 passed** (`python -m pytest tests/ -q`, 314.46s, exit 0); taban 3931 → 4002.
Testler: 65 (`tests/test_approval_surface.py`) + 6 (motor atfı, `test_policy_engine_checks.py`).

**Ne kuruldu:** `approval.py` — kilitli koşudan BASILAN değişmez görüntü (F18), K-42 sinyal
sıralaması, K-41 eşiksiz çıkarma sayısı + bir tık derin tam liste, K-71 açık-soru kapısı,
K-99 onay/ret olayı. Yönetici kalıp listesi GÖRMEZ (spec §9.6).

**ÖNKOŞUL — motor bulguya ÜRETİCİSİNİ yazıyor** (`BulguIzi.kontrol`). `sinif` riskli sınıfları
ayırt ETMİYORDU: `acik_soru` sınıfını BEŞ ayrı kontrol üretiyor (ölçüldü). Atıf TEK yazıcıda
damgalanır (`run_checks`, değer `EngineCheck.ad`); kontrol gövdesi kendi adını yazarsa toplayıcı
DURUR. Sınıf tek örnekle değil TOPLAYICIDAN kapatıldı — sonradan eklenen herhangi bir kontrol de
atfını alır. Etki alanı ölçüldü: 13 üretim kurulum noktasının HİÇBİRİ değişmedi.

**Checkpoint 11 — DÖRT tur** (1 tam inceleme + 3 kapanış-doğrulama), taban `33bfae6`.
Tur 1: `needs-attention`, İKİ yüksek + iki orta + bir düşük. Tur 2: F1 · F3 kapalı doğrulandı,
F2'nin İKİNCİ ayağı açık. Tur 3: F2'nin ÜÇÜNCÜ ayağı açık → **aynı eksen üç varyant verdi**,
yamama BIRAKILDI ve çerçeve teşhisi Eray'a götürüldü (kararı: "ev desenini uygula, bir tur daha").
Tur 4: **`approve`, bulgu YOK.**

**Kapanan yüksek bulgular:** (F1) karar ile denetim olayı atomik değildi — `log_package_event`
altyapı hatasında `None` döner ve dönüş kontrol edilmiyordu; otomatik-commit'te sonuç İZSİZ ONAY.
Yaşam döngüsünün F24 deseni uygulandı: olay ÖNCE, `None` HATA, hepsi tek işlemde ·
(F2) onay, onaylanabilir bir ekranın gösterildiğini KANITLAMADAN kaydedilebiliyordu; üç ayağı
kapandı (görüntü/hash/çekirdek doğrulaması + `onaylanabilir` kapısı · hedef kimliği çekirdekte ·
paket İLİŞKİSİ kapısı dondurmada ve karar anında).

**Orta/düşük:** (F3) atıf doğrulaması anahtar VARLIĞINA bakıyordu, `kontrol=""` varsayılanı nötr
"uyarı"ya düşüyordu — kontrolörün KENDİ ürünü, üç satırlık iş, `accepted_risk`'e ALINMADAN
düzeltildi · (F4) Task 14 `BulguIzi`'yi Task 8 sözleşmesinin içinden değiştirdi — DÜZELTİLEMEZ
(yürütücü ek düzenlemez), Open Problems'a yazıldı · (F5) "kendi kırmızısı olmayan test" beyanı
eksikti ve Task 15'in iki K-94 testini "taşıyor" demek fazla iddiaydı (onlar PLAN kalemi).

**Ölçüm:** OTUZ kapının OTUZU mutasyonla kanıtlandı (rc=0). Mutasyon İKİ gerçek boşluk buldu:
"ikinci karar reddedilir" kapısı TESTSİZ yazılmıştı ve `package_id is None` için İKİ gereksiz
kapı vardı (paket kapısı ikisini de yakalıyordu → kanıtlanamayan kapı gereksiz kapıdır, tek
kapıya indi). Üç autocommit testi işlem sarmallarını kanıtlıyor — fixture'ın DIŞ transaction'ı
onları maskeliyordu.

**YARIM HAKEM KARARI SAYILMADI:** tur 4 ilk denemede kota sınırında kesildi ve `approve`
yazıyordu; rc=1, 9 komut, metin GELECEK zamanlı (giriş anlatısı, karar değil). Reset sonrası
baştan koşuldu (rc=0, 32 komut).

**DÜRÜST BOŞLUK:** uçtan uca koşum hâlâ YOK; motor gerçek bir koşuda hiç çağrılmadı (ilk gerçek
ölçüm Task 19). Görüntü şeması sürüm 1'de KALDI — canlı veritabanında `sector_package_runs`
tablosu HİÇ YOK (036 dağıtılmadı, psql ile ölçüldü), yani kalıcı görüntü yoktur.

# ÖN KOŞUL — Task 10'dan ÖNCE: test matrisi küçültme (BİTTİ 2026-09-09)

> **Eray kararı (2026-09-08): Plan 2'nin yürütmesi bu iş bitene kadar DURAKLAR.** Ayrı görev
> klasörü AÇILMADI — bu iş Plan 2'nin kendi görevinin (Task 7) ürünüdür ve Task 10'u bekletir,
> bağımsız bir iş değildir. (Kısa süre `docs/active/test-matris-kucultme/` diye ayrı bir klasör
> açıldı ve Eray itirazıyla aynı gün geri alındı; kayıt burada yaşar.)

### Amaç

Arka uç test kümesini **ayırt eden eksenlere** indirmek. Bugün küme, davranış sayısıyla değil
**kombinasyon çarpımıyla** büyüyor; her hakem turu, her düzeltme turu ve her doğrulama o çarpımı
baştan koşuyor.

**Eray'ın kararı (2026-09-08): Plan 2'nin Task 10'una geçmeden ÖNCE bu iş yapılır.** Gerekçesi
kendi cümlesiyle: bu şekilde test olmaz, bu şekilde plan bitmez.

### Ölçüm (2026-09-08, taze koşum)

```
$ cd apps/social/backend && source .venv/bin/activate
$ python -m pytest tests/ --collect-only -q | grep -oE '^tests/[a-z_0-9]+\.py' | sort | uniq -c | sort -rn | head -4
   4414 tests/test_brief_doctor.py
    484 tests/test_migration_036.py
    411 tests/test_pipeline_runs.py
    169 tests/test_unit_identity.py
```

Toplam **6380 vaka**; `test_brief_doctor.py` tek başına **%69**'u.

O dosyanın içinde kütle iki fonksiyonda toplanıyor:

```
$ python -m pytest tests/test_brief_doctor.py --collect-only -q | grep -oE '::test_[a-z_0-9]+' | sort | uniq -c | sort -rn | head -3
   3240 ::test_kod_citi_ekseni
    432 ::test_tablo_eklemek_var_olan_notu_kaldiramaz
    108 ::test_cit_icindeki_baslik_yuva_
```

- **`test_kod_citi_ekseni` TEK BAŞINA 3240 vaka** = bütün arka uç kümesinin **%51'i**.
- İlk iki fonksiyon birlikte **3672 vaka** = kümenin **%58'i**.
- Dosyada **123 test fonksiyonu**, **31 `parametrize`** bloğu var; fonksiyon başına ortalama
  36 katlık çarpım.

**Kıyas — Plan 1 (arşiv kaydı, `docs/task-archive/2026/08/sektor-bilgi-paketi/`):**

```
pytest tests/ -q  →  660 passed (105s)
pytest tests/ -q  →  659 passed (106s)
Plan 1 kapanışı   →  577 passed
```

Yani pratik değişmedi (Plan 1'de de tam küme koşuluyordu); **küme değişti**: 577 → 6380 vaka,
105 saniye → 715 saniye. Büyümenin çoğu tek bir Plan 2 görevinin (Task 7, `brief-doctor`) test
dosyasından geliyor.

**ÖLÇÜLMEDİ — tahmin değil, ölçülmemiş:** `test_kod_citi_ekseni`'nin küme süresindeki payı
sayılmadı. Vaka sayısı payı (%51) süre payına EŞİT DEĞİLDİR ve öyle varsayılamaz. Süreyi
küçültmenin ne kadar kazandıracağı, işe başlarken şu komutla ölçülür:

```
python -m pytest tests/test_brief_doctor.py::test_kod_citi_ekseni -q --durations=0
```

### Neden ŞİMDİ

Her hakem turu, her düzeltme turu ve her kapanış doğrulaması tam kümeyi koşuyor. Task 9'un tek
oturumunda küme **iki kez** koştu (24 dakika). Task 10-20 önümüzde; aynı çarpım her turda
yeniden ödenecek.

### Kapsam

**Ana hedef:** `tests/test_brief_doctor.py` — özellikle `test_kod_citi_ekseni` ve
`test_tablo_eklemek_var_olan_notu_kaldiramaz`.

**Kural:** kombinasyon çarpımı yerine **ayırt eden eksen**. Bir vaka, ancak başka hiçbir vakanın
yakalayamadığı bir mutasyonu yakalıyorsa kalır.

**Kapanış ölçütü — sayı değil, MUTASYON:** küçültme "vaka sayısı düştü" diye kapatılamaz.
Küçültülen her eksen için, küçültmeden ÖNCE kırmızı olan mutasyonların küçültmeden SONRA da
kırmızı kaldığı gösterilir. Kaybolan bir kırmızı = geri alınacak küçültme.
İlgili disiplin: [[feedback_measure_your_own_fix_side_effects]].

**Kapsam DIŞI:** diğer test dosyaları (`test_migration_036.py`, `test_pipeline_runs.py`) bu turda
ellenmez — ikisi birlikte kümenin %14'ü, önce %69'luk kalem ölçülür.

### Açık kalemler — KAPANDI (2026-09-09, hepsi ölçüldü)

- ~~Küçültmenin süre kazancı ölçülmedi~~ → **ölçüldü ve ÖNCÜLÜ YALANLADI.** `--durations=0`
  ile alınan aşama dökümünde `test_kod_citi_ekseni` **33.0s / 704s = %4.7**. Vaka payı (%51)
  süre payına eşit değilmiş; bu bölümün ilk hâli o eşitliği varsaymıyordu ama kapsamı yine de
  yanlış hedefe kurmuştu. **Gerçek maliyet setup'tı:** 693.7s'in **355.0s'i** fixture kurulumu,
  çünkü 128 test veritabanını düşürüp yaratıp 36 migration'ı baştan uyguluyordu.
- ~~3240 vakanın kaçı ayırt ediyor bilinmiyor~~ → **ölçüldü:** çit kuralı tamamen sökülünce
  dilsiz yarının **924** hücresi yeşil kalıyor, dilli yarının **1080** hücresi zaten boş
  beklenti taşıyor (%62 ölü). Ayrıca `tur12` mutantını **hiçbir hücre** yakalamıyor — onu
  yakalayan şey CommonMark sınır problarıdır, matris değil.

### Sonuç (2026-09-09, commit `458661b`)

Üç kaldıraç indi, üçü de önce/sonra ölçüldü:

| kaldıraç | ölçüm |
|---|---|
| şablon veritabanı (`CREATE DATABASE ... TEMPLATE`) | scratch kurulumu **2.54s → 0.24s**, 128 kurulum |
| not kümesi önbelleği | çit testleri **115.48s → 79.30s**; 18011 çağrının %45.3'ü tekrar |
| matris → 3-yollu kapsama dizisi | **3240 → 280 hücre**; dosya **155.5s → 38.8s** |

**Tam küme: 6416 passed / 704.37s → 3458 passed / 286.36s, ikisi de exit 0.**

**Kapanış ölçütü (mutasyon) karşılandı, küçültmeden ÖNCE ölçülerek:** maske söküldü
696 → 59 kırmızı · tur9 540 → 48 · tur10 396 → 35 · tur12 0 → 0 (ikisi de yakalamıyor).
Ayrıca ÜRETİM kodundaki `_cit_maskesi` gerçekten bozuldu → küçültülmüş dosyada **279 test
kırmızı**; mutasyon geri alındı, ağaç temiz doğrulandı.

**Kabul edilmiş risk:** dört/beş boyutun aynı anda tuttuğu bir çit hatası kaçabilir. Yeniden
açılma koşulu ve tek satırlık düzeltmesi (`_KAPSAMA_DERECESI`) dosyanın içinde.

**Düşürülen iddia (park DEĞİL, dürüst etiketli):** "vacuous'luk ayıraç biçiminden bağımsızdır"
kolu kaldırıldı — küçültülmüş kümede o iddiayı sınayan grup sayısı ölçüldü ve **0**. Boşa yeşil
kol beyanı bayatlatır. Yeniden açılma koşulu dosyada.

### Kararlar

- **2026-09-08 — Eray: Task 10'dan ÖNCE.** Plan 2'nin yürütmesi bu iş bitene kadar duraklar.
- **2026-09-08 — kapanış ölçütü mutasyon kanıtıdır**, vaka sayısı değil.
- **2026-09-09 — ölçüm hedefi değiştirdi.** İş "matrisi küçült" diye başladı; aşama dökümü
  alınınca sürenin yarısının DB fixture'ı olduğu çıktı. Matris yine küçültüldü (%8.6'ya) ama
  kümedeki kazancın büyük kısmı şablon veritabanından geldi. Ders: kapsamı vaka sayısıyla
  değil, ÖLÇÜLMÜŞ süre payıyla kur.
- **2026-09-08 — bu kalem Eray sormasaydı çıkmayacaktı.** HANDOFF'ta yalnız *yeni* matrisler için
  yarım bir uyarı vardı ("kap çarpımını değil ayırt eden ekseni büyüt"); var olan 4414 vakaya
  karşı hiç çevrilmemişti. Kayda geçiyor: ölçülmüş bir sürtünme kaynağı, adlandırılmış bir ev
  bulana kadar aktif borç sayılmaz.


# Kapanışta Yapılacaklar

Plan 2 kapanırken (`/finish-branch-claude-codex`) unutulmaması gereken, başka hiçbir adımın
tetiklemediği kalemler. Buraya yazılmayan "sonra yaparız" sözü tutulmaz.

- **Birlikte arşivleme.** `docs/active/brief-sozlesmesi-kaynak-bolumu-makine-okunur/` bu
  planın içinden doğdu, 2026-09-07'de bitti (`status: done`) ve plan koşarken bilerek
  `docs/active/` altında tutuluyor — değiştirdiği sözleşme metnine Task 9/10 dokunacak.
  **Kapanışta bu görev ana görevle BİRLİKTE arşivlenir**, her biri kendi bitiş tarihinin
  `docs/task-archive/YYYY/MM/` klasörüne. Tek başına erken taşınmaz (2026-09-08'de bir kez
  taşındı ve geri alındı: kaydı ikiye bölüyordu).

# Decisions Log

- **2026-09-11 — Task 17 hazırlık kapısı = indi; checkpoint 14 BEŞ turda kapandı:**
  hakem F1-F5 üretti; F2 (üretici kimliği damgadan değil `model`'den), F3 (kalıcı raporun TİPLİ
  okuyucusu + yaprak tip değişmezleri), F4 (bloklayan sınıflar motorun etki tablosundan türetilir),
  F5 (artefakt türü kapısı test taramasından YAZICININ değişmezine yükseltildi) kapandı ve tur 5
  `approve` verdi. F1 sahibinin kararıyla açık kaldı (yukarıda, Open Problems).
  **Süreç kararı:** dört turun dördü de gerçek kusur bulduğu için beşinci doğrulama turu koşuldu
  (Eray onayı); "muhtemelen temizdir" varsayımı bu zincirde beş kez de yanlış çıkardı.
- **2026-09-11 — hazırlık maddelerinin DÖRT `otomatik` bayrağı düzeltildi (md-04 · md-08 · md-17 ·
  md-20):** ölçülemedikleri görüldü, planın açık izniyle `readiness_items`'ta `False` yapıldı.
  `MADDE_KUMESI_SHA` değişti; eski tasdikler kendiliğinden geçersizleşir (zaten yoktu).
- **2026-09-11 — arşiv dosyasındaki bot token'ı = kapandı, yeni iş açılmaz** (yukarıdaki kayıt).
- **2026-09-11 — arşivdeki Telegram bot token'ı = KAPANDI, yeni iş AÇILMAZ (Eray):**
  geçen oturumun "EVSİZ KALEM" ilanı bayattı. Token 2026-09-06'da döndürülmüştü
  (`n8n-workflow-sir-hijyeni` (a) ayağı, `dadb343`); eskisi `401 Unauthorized` ölçülmüştü.
  `docs/archive/CLAUDE_crm_pre_cleanup.md`'deki dizi ölü metindir; geçmiş temizliği
  yapılmıyor. HANDOFF'un evsiz kovası artık BOŞ.
- **2026-08-27 — K-84 = A:** kalıp kimliği sürümler arası korunur. Değeri eşleştirmek
  değil, sentez ajanının atladıklarını motorun yakalayabilmesi. Doğurduğu teknik kalemler
  K-151/K-152/K-86/K-154 planın işi.
- **2026-08-27 — K-23 = B:** motorun kararsız kaldığı madde güvenli varsayılana düşer
  (kalıp korunur) + rapora yazılır; aktivasyonu bloklamaz. Gerçek çelişkiler zaten sentezin
  açık soruları olarak gelip K-71 gereği bloklar. Önce A seçildi, üç kademeli yapı
  gösterilince B'ye çevrildi.
- **2026-08-27 — K-125 + K-100 = benimsendi:** denetçiler her turda aktif paketin her karar
  birimini de tarar (beş statü); motor `guncelle`/`cikar` için iki denetçi uyumu arar.
  Denetçi sözleşmesinin yeni sürümü gerekiyor.
- **2026-08-27 — K-133 = kurulmasın:** kuru mod ayrı koşu kipi olarak yazılmaz. Provenans
  ölçüldü: dokuz kaynak dosyanın hiçbirinde yok, tek hakemden geliyor. Çözdüğü temizlik
  sorunu K-106 (yerinde güncelleme) ile kapatılır. Yeniden açılma: motor ikinci sektöre
  yayıldığında.
- **2026-08-27 — K-130 · K-131 · K-132 = mekanizma kurulsun, eşik boş:** üç bariyerin kodu
  yazılır, değerleri pilot kalibrasyonunda konur. Ölçüldü: hiçbir kaynakta önerilmiş sayısal
  eşik YOK.
- **2026-08-27 — K-41 = eşik yok:** onay özeti "Çıkarılanlar: N" der, tam liste bir tık
  derinde. "Eşik üstü" boyutu hiçbir katmanda tanımlı değil.
- **2026-08-27 — K-42 = sıralama + aktivasyon süresi metriği:** özet riskli sınıfları nötr
  sayıların önüne koyar; onaya kaç saniyede basıldığı kaydedilir (R-21 tespit göstergesi).
  Geçmişe karşı anormallik tespiti dışarıda — geçmiş birikince.
- **2026-08-27 — K-134 = pilotta paralel, sonra tek geçiş:** pilot turlarında operatör önce
  sentez çıktısına bakıp yargısını kaydeder, sonra motorla karşılaştırılır — spec §15.2'nin
  istediği kalibrasyon verisi böyle doğar.
- **2026-08-27 — K-01a · K-146 · K-147 = üçü de eklensin:** 10 Kasım · 24 Kasım Öğretmenler
  Günü · okula dönüş. Sebep mekanik: sistem takviminde olmayan dönem pakete giremiyor.
  K-147 dönem taşıdığı için migration gerektiriyor.
- **2026-08-27 — Plan 2 tek planda yazılır.** Codex'in kademeli bölme önerisi reddedildi;
  ama kuralı korundu: sentez tek başına `draft` yazamaz, kanonik sıra sentez → motor → draft.
- **2026-08-27 — Komut ailesi: iş mantığı repoda CLI, `~/.claude/commands/` ince çağırıcı.**
  Kaynak sözleşmeler araştırma deposunda kalır; monorepo tarafında pin manifesti.

- **2026-08-27 — Genel review turu DURDURULDU.** Plan yeni bir kapsamlı hakem turuna
  sokulmuyor; yalnız iki kök tasarım sorunu (K-145 sözleşmesi · Task 12/13 sonuç sahipliği)
  uçtan uca kapatıldı. **Kalan risk ölçülmedi, bilinçle kabul edildi** — durdurmak kapanmak
  değildir.
- **2026-08-27 — Plan RİSK KABULÜYLE ONAYLANDI (Eray).** Son iki düzeltme partisi hiçbir
  hakem görmedi; zincirin son yargısı `needs-attention`'dı. Onay bu bilgiyle verildi.
  Frontmatter bunu yansıtır: `approved-by-iteration-limit` + `unresolved_high_severity_override: true`.

- **2026-08-30 — Yürütme öncesi ön-tarama koşuldu ve arayüz eki yazıldı (Eray onayı).**
  66 görev çifti tarandı: 8 çelişki · 12 boşluk · 20 görevin 18'inde iç tutarsızlık. Sebep
  yapısal: her görev KENDİ brief'ine karşı incelenir, komşusuna karşı değil — iki görevin
  farklı icat edeceği bir sözleşme görev-başı review'a görünmez. Eray "ek + tek hakem turu"
  seçti (ben karara bağlayıp yürütmek ve planı tam onarım turuna sokmak reddedildi).
- **2026-08-30 — AÇIK-1: geri alma onayı, onayladığı plan satırının yanında saklanır.**
  Bildirim kuyruğu seçilmedi (kuyruğun temizlik döngüsü onayı silebilir; yürütücü zaten
  kilitlediği satırın yanında ikinci tablo okumak zorunda kalırdı). Onay OLAY düzeyindedir,
  paket düzeyinde değil — K-145 N paketi birden geri alır, paket başına onay tek operatörde
  taşınamaz. Maliyet ölçüldü: migration henüz yazılmadığı için alanlar bedava.
- **2026-08-30 — AÇIK-2: tek-paketlik geri alma da olay kimliği ister.** İlk içgüdüm "acilde
  üç komut fazla" diye tersiydi; ölçünce döndüm — acil kol (deaktive-et) kanıt zinciri
  istemez ve bu karardan ETKİLENMEZ. Kapanan tek şey "önceki sürüme kanıtsız dönme", ki o
  acil değil düşünülmüş bir hamledir. Örtük olay üretmek kalıcı kirlilik yaratırdı.
- **2026-08-30 — AÇIK-3: parmak izi yardımcıları Task 8'de, Plan 1 modülünde doğar.**
  **Verdiğim gerekçe YANLIŞTI ve düzeltildi:** "bağımlılık yönü hiç ters çevrilmedi" dedim,
  ölçüldü ki bir tur önceki kendi metnim onu zaten çevirmişti. Karar geçerli, sebep düzeltildi,
  tek izinli kenar açıkça yazılı ve yapısal testi var.
- **2026-08-30 — Hakem zinciri kontrolör kararıyla BİTİRİLDİ (dördüncü tur yok).** Doktrin
  delikleri kapandı; kalan bulgular henüz var olmayan kodun davranışı. Bir belge çalışma
  zamanı kuralını uygulayamaz, yalnız anlatır — devamı Türkçe kod yazmak olurdu. Çıkış
  koşulu olarak mekanik öz-denetim koşuldu (50 hüküm→görev çifti, 0 eksik).

- **2026-09-02 — Task 5 Step 1b: takvim seed değerleri KAPANDI (Eray kararı).** Plan bu beş
  değeri uydurmayı YASAKLIYOR; operatöre soruldu ve karara bağlandı. Migration üç satırı
  **sabit** yazar:

  | tarih | `name_tr` | `name_en` | `category` | `end_date` |
  |---|---|---|---|---|
  | 2026-11-10 | 10 Kasım Atatürk'ü Anma Günü | Atatürk Memorial Day | `national` | — |
  | 2026-11-24 | 24 Kasım Öğretmenler Günü | Teachers' Day | `commercial` | — |
  | 2026-08-15 | Okula Dönüş | Back to School | `commercial` | 2026-09-15 |

  **Yıl = 2026 (mekanik):** tabloda tek yıl bu (ölçüldü: 22 satırın 22'si 2026); yıllık n8n
  işi her 1 Ocak yalnız içinde bulunduğu yılı yazar, yani 2027 kendi turunda doğar.
  **10 Kasım → `national` (emsal ölçüldü):** "Çanakkale Şehitlerini Anma Günü" de `national`;
  ton talimatı (vatan/gurur + uydurma alıntı yasağı) birebir uyuyor.
  **Öğretmenler Günü → `commercial` (Eray kararı):** hediye/teşekkür günü olarak Anneler ve
  Babalar Günü kovasına konur; milli ton ("vatan/gurur/birlik") bu güne oturmuyor.
  **Okula Dönüş → `commercial`:** kalan iki kova (milli, dini) hiç uymuyor.
  **Anahtar çakışması YOK (ölçüldü):** `10-kasim-ataturk-u-anma-gunu` · `24-kasim-ogretmenler-gunu`
  · `okula-donus` — üçü de mevcut 22 satırın hiçbiriyle çakışmıyor.
  **Yanlış bir çerçeve düzeltildi:** kategorinin satış diliyle ilgisi YOK. Üretimdeki
  "satış formülü uygulanmaz" hükmü **özel gün akışının kendisine** ait ve her kategoride
  basılıyor (ölçüldü: `prompt_builder` özel gün bloğunun kapanış cümlesi + üç özel gün
  şablonunun ortak metni). Üç kova yalnız **ton**u ayırır. Satışın meşru yolu `cta_url` +
  `cta_label`. Bu yüzden "dördüncü kategori açalım mı" seçeneği konusuz kaldı.

- **2026-09-02 — Okula dönüş satırının 2026'da seçilemez olması KABUL EDİLDİ (Eray kararı).**
  Ölçüldü: içerik oluşturma ekranı her özel gün satırı için `isPast = başlangıç < bugün`
  testi yapar ve geçmiş satırı `disabled` basar. Bugün 2 Eylül olduğu için 15 Ağustos
  başlangıçlı satır oluştuğu anda bu yıl tıklanamaz.
  **Kontrolörün ilk çerçevesi FAZLA GENİŞTİ ve daraltıldı:** "her yıl dönemin ortasında
  kapanır, 2027'de düzelmez" dedim; ekranın modeli **planlama** olduğu için (içerik gün
  gelmeden hazırlanır — tek günlük bayramlarda da aynı) davranış tutarlıdır ve satır yılın
  büyük kısmında seçilebilir. Kalıcı kusur DEĞİL.
  **Karar:** önyüze DOKUNULMAZ, Task 5'in dosya kapsamı genişletilmez; 2026 için satır ölü
  kalır, 2027'den itibaren aynı dönemle (15 Ağustos – 15 Eylül) normal koşar.
  **Yeniden açılma koşulu:** operatörün SÜREN bir dönem içinde içerik üretmesi gerekirse —
  o zaman "geçti mi" testinin bitiş tarihini okuması gerekir.
  **Dürüst etiket:** dönem kolonunun bugün önyüzde tüketicisi YOK; bu bilinçli, gizlenmiyor.

- **2026-09-06 — R12(a2)(d) AMENDE EDİLDİ (kontrolör kararı, ölçümle):** manifest muafiyeti
  `indexes` yanında `constraints` yüzeyine de uzanır. Ek kendi içinde çelişiyordu — adın
  `CONSTRAINT ... UNIQUE` biçiminde yazılmasını şart koşarken `constraints` yüzeyinin hiç
  gevşememesini de istiyordu. Canlı PG 18.3'te ölçüldü: adlandırılmış UNIQUE kısıt HEM bir
  `pg_constraint` satırı HEM bir indeks üretir; `CREATE UNIQUE INDEX` yalnız indeks üretir.
  Sözleşmedeki ad `_key` ile bitiyor (PostgreSQL'in KISIT son eki), yani yazar kısıt istemiş.
  Muafiyet tek ada + tam tanıma bağlı; `columns`/`triggers`/`relation` kapalı kaldı.
  **Ek metni artık kodla uyumsuz — kapanışta düzeltilmeli, "çözüldü" DEĞİL.**
- **2026-09-06 — sürüm sözleşmesi için DB CHECK EKLENMEZ (kontrolör kararı):** üç geçiş
  sözleşmesi ilişkiseldir (olay yazıldığı ANDA canlı olan aktif sürümle tam eşleşme) ve bir
  CHECK'te ifade edilemez; yalnız ifade edilebilir kısmı kodlamak aynı sözleşmeyi iki katmana
  böler ve iki ölçünün ıraksamasına izin verir. Asimetri ölçüldü: eksik/ölü bir PYTHON beyanını
  import kapısı yakalar, bayat bir DB CHECK'ini hiçbir şey yakalamaz. Kalan risk açıkça duruyor:
  ham SQL kapıyı atlar — on bir türün hepsi için. Geri alma maliyeti adlandırıldı (bir CHECK +
  bir muafiyet satırı + bir düşürme adımı).
- **2026-09-06 — `ON_ERROR_STOP` konvansiyonu (kontrolör kararı):** yeni geri alma dosyaları
  çağıranın psql oturumunu değiştirmeden bırakır (ayarla, sonunda geri koy). `032_down`/
  `035_down` bu turda DEĞİŞMEDİ; tutarsızlık kayda geçti. **Ölçülmüş sınır:** ret yolunda psql
  dosyayı okumayı bırakır, o yüzden geri koyma satırına ULAŞILMAZ ve çağıran `on` ile kalır —
  kapatılamaz, çünkü `rc=3` yalnız `ON_ERROR_STOP` açıkken üretilir. Üç dosyanın başlığında yazılı.
- **2026-09-06 — tur 4-5'te model yükseltmesi YAPILMADI (kontrolör kararı):** SDD kuralı "üç
  turdur takılan uygulayıcı kendi sorununu göremiyor" gerekçesine dayanır; bu döngü takılmadı —
  her tur kendi bulgularını kapattı, her yeni bulgu tazeydi. Model tabanı zaten mevcut en
  güçlüsü, yani "yükseltme" karar kılığında bir no-op olurdu.
- **2026-09-06 — aktör kapısının TANIM YERİ taşındı (kontrolör kararı, ekten SAPMA — etiketli):**
  bağlayıcı ek kanonik kimlik kapısını `sector_package_lifecycle._require_actor` diye SATIR
  NUMARASIYLA adlandırıyor. Olay yazıcısının da aynı kapıyı kullanması gerekiyordu (F2), ama
  bağımlılık ZATEN ters yönde kurulu: `sector_package_lifecycle` → `package_events`. Ölçüldü:
  ters yönde ikinci bir import DÖNGÜdür ve `ImportError` ile düşer. Tanım `package_events.
  require_actor`a taşındı, eski ad import ile bağlandı — **ad ve davranış AYNI**, ikinci bir
  kural kopyası YAZILMADI (ekin kapattığı sınıf tam olarak kopya yazmaktır). **Sapma: tanım
  YERİ ekin gösterdiği modül değil.** Bu, ekin ad-kümesi hükmüyle ilgili ZATEN AÇIK olan
  tasarım maddesinin (`plan2-ek-bagimlilik-hukmu-ad-kumesi`) kanıt kümesine eklenir; yürütücü
  ek metnini yeniden yazmaz.
- **2026-09-06 — onaylı geri alma planı satırının SİLİNMESİ bilerek korumasız BIRAKILDI
  (kontrolör kararı):** ekin DÜZYAZISI mekanizmayı "032'nin `sector_research_artifacts_
  append_only` tetikleyicisinin aynısı" diye tarif ediyor ve o tetikleyici `BEFORE UPDATE OR
  DELETE`; ama ekin BAĞLAYICI SQL BLOĞU `BEFORE UPDATE` diyor. Uygulama SQL bloğunu izledi.
  **Neden DELETE ayağı eklenmedi:** aynı ek, yürütme penceresi açıkken üyeliğin küçülebileceğini
  (satır çıkarma, `amend_rollback_plan`) söylüyor ve onay damgası `durum='bekliyor'` satırlara
  yazılıyor — onaya bakan bir DELETE kapısı belgelenmiş ama henüz yazılmamış bir akışı
  bloklayabilirdi. Ölçüldü (2026-09-06): bugün hiçbir üretim yolu o satırları silmiyor (tek
  eşleşme `036_down.sql`in tabloyu tümden düşürmesi). **Ekin kendi içindeki düzyazı-SQL
  çelişkisi ÇÖZÜLMEDİ**; madde Task 8'e (üyelik değiştiren `amend_rollback_plan`) ev verildi.
- **2026-09-06 — DDL nesne kimliği sınıfı 036 + 036_down'da kapatıldı, KALAN BEŞ DOSYADA
  AÇIK (kontrolör kararı):** F7 düzeltmesi yalnız bu turun dosyalarını kapsadı. Uygulayıcının
  kavramdan türettiği tarama ("adıyla aranıp koşulsuz yazılan/düşürülen katalog nesnesi")
  `shared/db/migrations/` genelinde beş dosyanın sınıfı hâlâ taşıdığını ölçtü: `001_initial_
  social.sql` · `023_brands_updated_at.sql` · `026_brand_products.sql` · `032_sector_packages.sql`
  · `rollback/032_down.sql`. 032'nin `pg_get_triggerdef` kullanımı YAZIMDAN SONRAKİ manifesttir,
  yani tam da F7'nin adlandırdığı kör noktayı taşır. **Bu turda bilerek dokunulmadı** (kapsam
  Task 6'nın dosyaları); aktif katmana tetikli madde olarak yazıldı, sessizce düşürülmedi.

## Task 10 kararları (2026-09-09)

- **Hakem bulgusunun severity'si kontrolör tarafından İNDİRİLDİ — bir kez, gerekçesiyle.**
  Round 5'in tek bulgusu (`B7-toctou`: yollar kabul anında doğrulanıyor, kullanım anında
  atomik değil) `high` geldi; kontrolör `medium`'a indirdi ve `accepted_risk` yazdı.
  Gerekçe: mekanizma gerçek, ama erişilebilirliği ilan edilmiş tehdit modelinin DIŞINDA —
  girdi özensiz araştırma çıktısıdır, saldırgan değildir; yerel tek kullanıcılı hat.
  Rol dizininin tur koşarken bayt-özdeş bir dış ikize symlink'le değiştirilmesi kazara
  üretilebilir bir olay değil. Hakemin KENDİ fallback'i de bunu "unresolved concurrency
  residual olarak tut" diye öneriyor. Kısmi kapanış yine de uygulandı (`3af4331`).
  **Bu bir emsal DEĞİL:** severity indirimi ancak erişilebilirlik tehdit modeline karşı
  ÖLÇÜLDÜĞÜNDE yapılır; "kapsam büyüyor" ya da "maliyet artıyor" gerekçe değildir.

- **OS kum havuzu / konteyner Task 10 kapsamı DIŞINDA tutuldu (kontrolör kararı).**
  Hakem K-79 için OS düzeyinde izolasyon önerdi; reddedildi — dağıtım katmanının işi.
  Uygulanan asgari kapanış: raporlar iki denetçi de bitene kadar diske yazılmıyor, rol
  yolları takma ad/symlink/paylaşım kabul etmiyor, paket kiralaması ve koşum anı bayt
  bütünlüğü kapıları eklendi, kalan risk kodda beyan + tripwire.

- **Kilit devralma politikası: ASLA devralınmaz** (zaman aşımı yok, PID canlılığı yok).
  Gerekçe yapısaldır ve hakem tarafından koddan doğrulandı: kiralama paket kökü başına,
  kök `<dest>/<run_id>`, ham katman salt-eklemeli — her yeniden koşum yeni kimlik, yeni kök,
  yeni kiralama alır. Sahibi ölmüş bir kiralama yalnız zaten tekrar koşulamayacak bir kökü
  bloke eder. İnsan kurtarması: o dizini silmek.

- **Arayüz eki kodun ARKASINDA kaldı (R-A…R-D deseninin beşinci tekrarı).** Task 10 ekin
  `PacketRef` alan listesine `yetkili_kaynak_sayisi` ekledi ve `run_audit_round`'a
  `web_prob` parametresi koydu. Ek dosyasına DOKUNULMADI (yürütücü sınırı). Ekin
  güncellenmesi bekleyen bir karar.

- **Süreç ağırlığı azaltıldı (Eray talebi, 2026-09-09).** Mutasyon kanıtı artık yalnız YENİ
  kapıya isteniyor; inceleme turu üretim/test diye BÖLÜNMÜYOR; düzeltme brief'leri kısa.
  Ölçüm: uzun brief'li turlar 16-24 dk sürdü, kısa brief'li tur 7,4 dk.

- **Yürütme kipi Task 11 için `inline`'a çevrildi (Eray talebi, 2026-09-09 14:27).** Task 1-10
  alt-ajanlı koştu; Task 11 ana oturumda yazılacak. Kip bir HAFIZA değil CANLI AYAR olduğu
  için alan güncellendi — sessiz kayma DEĞİL, açık talimat. İnceleme/checkpoint kapıları
  DEĞİŞMEDİ (daraltma yalnız dispatch kipini kapsar).

## Task 11 kararları (2026-09-09)

- **Plan imzasına `dest` EKLENDİ ve sapma beyan edildi.** `Runner` protokolü çalışma dizini
  ve istem dosyası ister; kök gizli bir sabitten türetilseydi testler gerçek araştırma
  deposuna yazardı. `build_packet`'in `dest` deseniyle simetrik.

- **`kirp` churn kapısına GİRER, kanıt kapısına GİRMEZ.** Sözleşme churn korumasını
  "kırpmanın ve `cikar` kararının SONUCUNA konan kısıt" diye yazar; ama kırpma bir BOYUT
  kararıdır (spec §8.6), kanıt kararı değil. İki kolun ayrılması bilinçli — kanıt eşiği
  kırpmaya da konsaydı sözleşmede olmayan bir kural yazılmış olurdu.

- **Çözme kuralı `identity.cozulmus`'a taşındı; `runs._coz` oraya devretti.** Dondurma ile
  çözme bir çifttir ve iki kopya sürüm sürüm ayrışırdı. Hakem, "şema `list` ister, o yüzden
  donduramayız" gerekçemi çürüttü: çözme şema SINIRINDA yapılır, kalıcı temsil donabilir.

- **Reddedilen çıkarmanın eşi olan `ekle` satırı `yerine_gecer` bağını KAYBEDER.** Bağ
  bırakılsaydı günlük olmamış bir değiştirmeyi olmuş gibi gösterirdi. Aday düşürülmez.

- **[Task 12, 2026-09-09] Motor SONUÇ üretmez, ÖLÇÜM üretir.** `run_checks` dört kanal
  döndürür (bulgu · uygulanmayan karar · not · ölçüm) ve dördünün de tanımlı tüketicisi
  vardır. Kapalı kümeye sığmayan ihlal BULGU İCAT ETTİRMEZ: bozuk şema ve durmuş mekanik
  tur girdi kapısında fail-closed durur (`identity.decision_units` emsali).

- **[Task 12, 2026-09-09] K-126 tek-kaynak istisnası bu katmanda İŞLEMEZ.** Sözleşme iki
  koşulu BİRLİKTE ister; resmîlik ayağı (K-123) tipli girdide taşınmıyor. Bir AND koşulunun
  tek ayağını zorlamak istisnayı canlı HER kaynağa açardı — o yüzden istisna kapalı doğar.
  Açılması arayüz eki revizyonu ister.

- **[Task 12, 2026-09-09] Kanıt alanı KAPALI DİLBİLGİSİDİR.** Dört hakem turu aynı eksende
  dört sızıntı verdi (metnin herhangi bir yerinde desen → bileşen içinde sarmalanmış etiket
  → komşu bileşene taşan düzyazı → gevşek URL kolu). Varyant yamamak yerine alan BÜTÜN olarak
  doğrulanıyor: her bileşen ya geçerli kör etiket, ya tam biçimli URL, ya denetçi satır atfı.
  Olumsuzlama ARANMAZ — düzyazı zaten dilbilgisi dışıdır. Kabul edilen bedel: karışık yazılmış
  meşru kanıt da reddedilir (yön fail-closed).

- **[Task 12, 2026-09-09] Kör etiket KONUMDAN türer, addan değil.** `build_packet` kimliği
  pakete yazmaz; `doctor_reports[i]` ↔ `sources[i]` hizasını fail-closed zorlar. Motor
  eligibility'yi bu konumdan okur — gerçek kaynak adıyla karşılaştırmak (ilk yazım) her yeni
  öğeyi reddederdi.

- **[Task 12, 2026-09-09] Task 10'un tarayıcısı BİÇİME bakar oldu.** "`ValidatedAuditPair`
  adı `auditors.py` dışında geçemez" kuralı, arayüz eki R5'in zorunlu kıldığı tip kapısını
  imkânsız kılıyordu. Üretici invariantı aynı güçle korunuyor (çağrı ve takma ad her dosyada
  kaçak); muafiyet yalnız üretemeyen biçimlerde ve sınırı kendi kontrol koluyla ölçülü.

- **Kontrolörün kendi test tarayıcısı mutasyon matrisiyle yakalandı.** `insert_draft` yasağı
  önce ham dizge taramasıydı ve kendi düzyazısına takıldı; AST'ye taşındıktan sonra ekilen
  beş ihlalden biri (`from app.services import sector_package_lifecycle`) hâlâ görülmüyordu.
  Elle seçilmiş örnek değil ÜRETİLMİŞ matris yakaladı.

## Task 14 kararları (2026-09-10)

- **`to_activation_evidence` YAZILMADI.** Plan onu Task 14'ün üretimi sayıyor; bağlayıcı ek (R8)
  TAMAMEN siliyor. Çağıranın verdiği sözlükten kanıt üreten ikinci kurucu, "kanıt veritabanından
  okunur" doktrinindeki deliğin kendisiydi. Kanıtın tek kurulum yeri aktivasyon yolunun içidir
  (Task 15). Modülün böyle bir kurucu göstermediği **AST taramasıyla** kanıtlanır — metin
  taraması DEĞİL, çünkü ad docstring'te meşru olarak geçiyor.

- **Planın iki testi Task 15'e AİT** (`test_evidence_always_states_base_state` ·
  `test_first_package_snapshot_yields_expected_no_active`) — konuları silinen fonksiyondu.
  **DÜZELTME (hakem turu 1, F5):** Task 15'in bunları "TAŞIDIĞI" söylenmişti; doğrusu Task 15
  PLANI onları listeliyor (`test_first_activation_uses_expected_no_active` ·
  `test_expected_no_active_rejected_when_active_row_exists`), HEAD'de MEVCUT DEĞİL.
  **Task 15'e bağlayıcı kalem:** taban durumunun "ikisi birden ya da hiçbiri yapım hatasıdır"
  ayağı için DOĞRUDAN test de eklenir; aktivasyon-yolu testleri onu ikame etmez.

- **Katman-2 kapı sonucu görüntüye "PASS" olarak YAZILMAZ.** Spec §10.2 onun sonucunun
  OKUNMADIĞINI söylüyor; koşulması ve sunulması ön koşuldur. Görüntü yalnız `sunuldu` taşır.
  İlk kırmızı bunu yakaladı: test "PASS" bekliyordu, `attest_katman2` imzasında `sonuc` YOK.

- **K-94 taban durumu görüntüye KONMADI ve taslak satırı OKUNMAZ.** Aktivasyon kanıtını Task 15
  kilitli satırlardan KENDİSİ türetir; aynı gerçeği görüntüye de yazmak onu iki kaynaklı yapardı
  (R2'nin yasakladığı desen). Spec §9.6'nın ekran listesinde de yok.

- **Atıf TOPLAYICIDA damgalanır, kontrol gövdesinde DEĞİL.** Gövdeler kendi adlarını yazsaydı her
  yeni kontrol atfı unutabilir ve onay yüzeyi riskli bir sınıfı sessizce kaybederdi. Gövdenin
  yazdığı atıf EZİLMEZ, DURDURULUR (uydurma atıf = sessiz sınıf kayması).

- **Hedef kimliği bir İLİŞKİDİR, iki gevşek değer değil** (kapanış turu 3). Kapı dondurmada VE
  karar anında koşar; ikinci çağrı birincinin tekrarı DEĞİLDİR — çekirdek karşılaştırması paket
  satırının KENDİ kaymasını görmez (koşunun iki kolonu aynı kalır). Dürüst sınır koda yazıldı:
  pencere KAPATILMAZ (paket satırı ancak okunarak öğrenilir), FAIL-CLOSED yapılır. Kalıcı çözümün
  evi zaten kayıtlı (`sector-package-sector-id-immutability`, tetikli) ve tetiği bu işle
  KURULMADI — bu modül o kolona yazmaz.

- **Kanıtlanamayan kapı gereksiz kapıdır.** `package_id is None` için iki ayrı kapı yazılmıştı;
  mutasyon ikisinin de bağımsız kanıtlanamadığını gösterdi (paket kapısı zaten yakalıyordu) →
  üç kapı TEK kapıya indi. Aynı üç yol hâlâ reddediliyor.

- **Adı yalan söyleyen iki test düzeltildi.** `test_run_mutation_after_freeze_invalidates_approval`
  koşuyu hiç mutasyona sokmuyordu (hakem yakaladı) → adı değiştirmek yerine INVARIANT gerçek
  yapıldı, eski senaryo `test_foreign_hash_is_refused` olarak kaldı.
  `test_missing_package_row_refuses_freeze` "satır yok" diyordu ama "bağ NULL"u ölçüyordu
  (kontrolör yakaladı) → kapsamı başka testte olduğu için SİLİNDİ.

## Task 13 kararları (2026-09-09)

- **`decide` girdi kapısının istisnasını YUTMAZ.** `EngineInputError` çağırana gider; `blocked`'a
  çevrilseydi motor hiç koşmadığı hâlde "karar verdi" görünür ve koşu satırına bir sonuç yazılırdı.

- **`koru` satırının iddiası uygulanır, aday yükünün iddiası DEĞİL.** Reddedilmemiş olmak "yükü
  kabul et" demek değildir; iki taraf çelişirse mevcut kalıp geri konur (spec §9.3: motor
  belirsizliği yeni içeriğin lehine yorumlamaz). İz `engine_diff.koru_ihlalleri`'nde.

- **Sınıflandırma KİMLİĞE göre, nihai yolun VARLIĞINA göre değil.** Yol-varlığı kabul edilen
  çıkarmayı "hiç olmamış" gösteriyordu. Yaşayan olmayan satır (kabul edilen `cikar`/`kirp`) kendi
  yoluyla KALIR ve uygulanan sayılır.

- **Motorun ürettiği çift, tüketicinin koşacağı kapılardan geçer.** `decide` nihai içerik+günlük
  çiftini `validate_decision_log` + `check_unit_integrity` ile sınar; geçmezse sonuç üretmez.
  Sınıf noktasal testle değil KAPIYLA kapandı.

- **Bariyer payı UYGULANAN kararlardan sayılır**, sentezin ham önerisinden değil. Bariyer
  gerçekleşecek değişimi ölçer; reddedilen bir öneri hiç olmayan bir değişikliği bloklardı.
  Aday dağılımı `engine_diff.diff`'te ayrıca durur.

- **Reddedilen ekleme DEĞİŞİKLİK DEĞİLDİR, düşen takvim dönemi DEĞİŞİKLİKTİR.** İkisi tek kovaya
  konsaydı tek bir reddedilen ekleme ilk koşuyu "değişiklik oldu" gösterir ve K-91 sessizce düşerdi.

- **Uygulanmama sebebinin önceliği BİLDİRİLMİŞTİR** (`UYGULANMAMA_SEBEPLERI` sırası). "Son yazan
  kazanır" bir kural değildir: kontrol kümesinin sırası değişince aynı girdi başka bir kural
  kimliği damgalardı.

- **Kural yüklemi KONUSUNU argüman alır.** Yüklem kendi konusunu içeriden okursa, aynı kuralın
  başka bir konuya (yeniden kurulmuş içerik) sorulması İMKÂNSIZ olur — F7 tam olarak buydu.

- **Farklı TÜRLER farklı kovalara konur.** Toplayan tarafın türleri ayırt etmesi beklenemez;
  ayrım sözleşmede kurulur (F8). Kova testi TÜRÜ sınar, varyantı kovalamaz.

## Arayüz eki revizyonu 2 + Task 19 penceresi (2026-09-11)

- **2026-09-11 — Eray kararı (F1):** hazırlık onayı **mühürlenmiş kanıta BAĞLANIR ve kapı
  FAIL-CLOSED olur.** Onay anında görülen kanıt kümesinin parmak izi tasdike YAZILIR;
  aktivasyon aynı izi yeniden hesaplar ve tutmuyorsa paketi AKTİVE ETMEZ, operatörü yeniden
  onaya çağırır. Reddedilen iki seçenek: "uyar ama devam et" (fark okunmazsa bugünkü
  durumdan farkı yok) ve "bugünkü hâli Task 20'ye taşı" (yüksek bulgu açık kalırdı).
  **Eray-seviyesinde sorulan şey mekanizma DEĞİL, risk tercihiydi** (İlke 8).

- **2026-09-11 — Eray kararı (tur şekli):** dış araştırma sözleşmesi turu **hafif yolla**
  koşar — tasarım bu oturumda yapılır, sonunda TEK bağımsız hakem turu. `/spec-claude-codex`
  zinciri açılmadı; gerekçe süreç ağırlığının risk ağırlığına denk olması.

- **2026-09-11 — arayüz eki REVİZE EDİLDİ (R-G1…R-G8).** Sekiz kalem; altısı ekin metnini
  kodun yaptığına uyarladı, biri (R-G7) bağlayıcı bir kararı TERSİNE çevirdi, biri (R-G8)
  ekte hiç olmayan bir sözleşmeyi ekledi. **Beşi bu turun taramasında bulundu** — ekin kod
  bloklarında beyan ettiği 65 yüzeyin hepsi kodla karşılaştırıldı; tarama fix'ten sonra
  yeniden koştu ve **kalan fark 0**.
  **Kapsam sınırı (dürüst etiket):** tarama ekin DÜZ YAZIDA beyan ettiği yüzeyleri
  KAPSAMIYOR ve ekte HİÇ GEÇMEYEN bir yüzeyi (R-G8 gibi) göremez. "Sapma kalmadı"
  İDDİA EDİLMEZ; iddia edilen, kod bloğu kolunun bugün temiz olduğudur.
  **Sınıfın kendisi kapanmadı** — ek↔kod ıraksaması süreç kusurudur; üretilmiş bir kapı
  önerisi ekin revizyon kaydında ÖLÇÜLMEMİŞ ÖNERİ etiketiyle duruyor.

- **2026-09-11 — F1 UYGULANDI (R-G9).** Kapı kod tarafında indi: `runs.kanit_parmakizi`
  (TEK türetici) · `readiness_items.KANIT_KOLONLARI` (üretilmiş küme) · tasdik yükünde
  `kanit_parmakizi` · `_checklist_approved`'ın BEŞİNCİ koşulu · iki çağıranın taze ölçümü ·
  operatöre "yeniden onaya gel" diyen CLI mesajı.
  **Ölçüm:** tam takım **4254 passed**, exit 0 (taban 4234 → **+20 test**);
  komut `.venv/bin/python -m pytest tests/ -q`, süre 318 s.
  **Mutasyon: DOKUZ yeni kapının DOKUZU da ayrı ayrı susturuldu ve hedef testini KIRDI**
  (sahte yeşil YOK).
  **Bekleyen bir taahhüt de bu partide kapandı:** F1 kararına bağlanmış olan *iki bağlantılı
  eşzamanlılık DAVRANIŞ testi* yazıldı — başka bir bağlantının COMMIT ettiği kanıt
  değişikliği aktivasyonu düşürüyor; testin pozitif kontrolü de var (değişiklikten ÖNCE kapı
  gerçekten AÇIK).

- **2026-09-11 — Eray kararı (atıf bağı): TAM BAĞ.** Yeni bir kalıbın pakete girmesi artık
  araştırma iddiasının NUMARASINA kadar izlenir. Reddedilen iki seçenek: "iki ucuz ayak"
  (özel gün yol bağı + bir satır bir ekleme) ve "yalnız özel gün ayağı". Gerekçe: pencere
  Task 19'da kapanıyor — araştırmalar bu biçimde henüz üretilmedi, yani bugün bedelsiz;
  pilottan sonra aynı değişiklik bütün araştırmaları ikinci kez ürettirirdi.

- **2026-09-11 — dış sözleşme deposu `12beec1`e ilerledi; pin yenilendi (`4636847`).**
  Üç dosya: araştırma şablonunda Bölüm C `no` sütunu · denetçi tablosunda
  `kaynak-iddialari` sütunu · sentezin `ekle` satırında `kaynak_iddia` alanı. Ayrıca Görev B
  dönem adı EK-J slug'ına bağlandı (tam yol bağının ölçülmüş engeli buydu) ve KAYNAK PROFİLİ
  tipli tabloya çevrildi (K-126). Üç dosyanın sürüm damgası da artırıldı — "her içerik
  değişikliği yeni damga alır" kuralı gereği.
  **Bağ İKİ UÇLU kuruldu:** numaranın gösterdiği satır araştırma raporunda gerçekten var mı
  (mekanik ayrıştırıcı doğrular, beyan değil) VE atıf yapılan denetçi satırı aynı numarayı
  taşıyor mu. Tek uçlu olsaydı iki tarafı da aynı model yazdığı için bağ kendini onaylardı.

# Open Problems

- **[YÜKSEK — AÇIK 2026-09-11, hakem turu] DIŞ SÖZLEŞME REVİZYONU — üç borç, TEK tur.**
  İki dual hakem turu (attempt-1 + kapanış) üç kalemi kod içinde KAPANAMAZ buldu. Üçü de aynı
  sınıftan: **sözleşme bugün taşımadığı bir KİMLİĞİ taşımadıkça kod onu uyduramaz.** Ayrı ayrı
  kapatmak sözleşme-turu makinesini üç kez çalıştırmak demek; tek revizyonda kapanırlar.
  **PENCERE:** revizyon bugün BEDELSİZ — araştırmalar bu biçimde henüz ÜRETİLMEDİ. Pilot
  (Task 19) araştırma ürettiği an kapanır ve aynı değişiklik BÜTÜN araştırmaları ikinci kez
  ürettirir (uyarı sözleşmenin kendi commit mesajında yazılı, `12beec1`).
  **EV: Task 18'den ÖNCE, tek sözleşme turu** (Eray kararı 2026-09-11).

  1. **F3 — Bölüm C dönem satırı KANONİK SİSTEM ANAHTARI taşımalı.** Araştırma dönem adını
     GÜNLÜK DİLDE yazıyor (`29 Ekim`), karar satırı SİSTEM adının slug'ını (`cumhuriyet-bayrami`);
     köprü YOK. ÖLÇÜLDÜ: şablonun 15 aday adından yalnız 4'ü sistem slug'ına düşüyor.
     **Bedeli: bu kapanana kadar Görev B (özel gün) eklemelerinin pratikte TAMAMI reddedilir.**
     Kod fail-closed ve teşhis dürüst (`donem-kimligi-cozulemedi`); sessiz bulanık eşleştirme
     YAZILMAZ.
  2. **F4 — URL örneklem satırı İDDİA NUMARASI taşımalı** (`K<kaynak>#<iddia>`). Bugün K-126
     istisnasının ikinci ayağı KAYNAK düzeyinde: o kaynağın örneklemdeki herhangi bir doğrulanmış
     URL'si, o kaynağın pakete giren HER tekil iddiasına yetiyor. **İstisna AÇIK ve ikinci ayağı
     beyan edildiğinden ZAYIF.**
  3. **F1 günlük ayağı — ÜÇÜNCÜ NOT SINIFI yetkilendirilmeli.** Not satırının alan kümesi
     `hakem-sentez-gorevi.md`'de KAPALI (iki değer); K-03 çatışması bu yüzden karar günlüğüne
     yazılamıyor. Bugün ölçüm olarak `engine_diff`'te duruyor.

- **[YÜKSEK — AÇIK 2026-09-11, kapanış turu N2] K-03 çatışması hiçbir OPERATÖR yüzeyine
  ulaşmıyor.** ÖLÇÜLDÜ (iki hakem + kontrolör, üçü de aynı sonuç): `kategori_cakismalari`
  koşu satırında kalıcılaşıyor ama onu ADIYLA okuyan tüketici YOK — onay anlık görüntüsü
  sürüm/ayar/bariyer taşıyor, CLI koşu kimliği ve sonucu basıyor, hazırlık kontrolü diff'in boş
  olup olmadığına bakıyor. **Bugün operatör bu çatışmayı hiçbir yerde görmez; kayıt yalnız
  denetim içindir.**
  **HAKEMLER AYRIŞTI** — Codex: yüksek bulgu (*"operatör çatışmayı görmeden onaylayabilir"*);
  alt-hakem: beyan dürüst, bulgu değil. Severity otonom İNDİRİLMEDİ.
  **Eray kararı (2026-09-11): B — geçici tüketici EKLENMEZ**, beyan sonucuyla birlikte yazılır.
  Gerekçe: aynı sözleşme turu gerçek günlük kaydını getirecek, geçici tüketici çöpe giderdi;
  risk penceresi kapalı, pilot koşmadan hiçbir çatışma operatöre ulaşamaz.
  **EV: yukarıdaki sözleşme turunun 3. kalemi ile BİRLİKTE kapanır.**

- **[KAPANDI 2026-09-11 — hakem turu + kapanış turu] Dış sözleşme ilerledi, kod uyarlanmadı —
  ağaçta İKİ KIRMIZI TEST vardı.** `test_denetim_basligi_matches_pinned_contract_header` ve
  `test_bolum_c_sabitleri_pinlenmis_sablondan_okunur`. İkisi de **sapma alarmıdır ve
  görevlerini yapıyorlar**: koddaki başlık sabitlerini pinlenmiş sözleşmeye karşı ölçüyorlar.
  Kırmızı, uyarlanacak iki noktanın ADINI söylüyor.
  **Neden yarım bırakılmadı:** ölçüldü — sabitleri değiştirmek `test_brief_doctor.py`'yi
  TOPLAMA aşamasında kırıyor (fixture satırları indeksle kuruluyor) ve motor tarafı (iddia
  bağı · K-126 resmîlik · K-03 kategori) hiç yazılmadı. Yeni sütunları ayrıştırıp TÜKETMEYEN
  yarım bir uyarlama sessiz bir ara durum olurdu; kırmızı alarm daha dürüsttür.
  **KAPANIŞ:** altı kalemin altısı uygulandı (`080aa7f`), iki dual hakem turundan geçti
  (`2188e06` + `T18-review-fix2`) ve iki kırmızı test kapandı. Tam takım 4335 passed.
  Kapanamayan üç ayak yukarıdaki sözleşme turu kalemine taşındı — düşürülmedi, EV verildi.

- **[KAPANDI 2026-09-11 — R-G9; KALAN YARISI ETİKETLİ] Hazırlık onayı mühürlenmiş bir kanıt
  kümesine bağlı DEĞİL.** Eray kararı: **fail-closed** — onay anında görülen kanıt kümesinin
  parmak izi tasdike YAZILIR, aktivasyon onu YENİDEN hesaplar, ayrışma varsa paket AKTİVE
  EDİLMEZ ve operatör yeniden onaya çağrılır (komut bunu açıkça söyler).
  **Kanıt kümesinin TANIMI genişletildi:** yalnız ham artefaktlar değil, hazırlık
  PROBLARININ okuduğu dokuz koşu satırı kolonu da kapsanır. Kolon kümesi elle tutulmaz —
  probların kaynağından AST ile üretilir ve kapısı vardır (yeni prob yeni kolon okursa test
  kırılır).
  **Açık sorunun tarif ettiği arıza ölçümle ÇÜRÜDÜ:** *"onaydan sonra DÜŞEN satır"* yolu
  yoktur — ham artefakt tablosu veritabanı düzeyinde salt-eklemedir (canlı ölçüm:
  `sector_research_artifacts_append_only`). Erişilebilir yönler EKLEME ve koşu satırı
  kolonlarının GÜNCELLENMESİDİR; kapı ikisini de kapsar.
  **KAPANMAYAN yarı — dürüst etiket:** `runs.attest_readiness` prob SONUÇLARINI hâlâ görmez,
  çağıranın madde kümesi iddiasını yazar. Probları yazıcıya koymak `runs` → `readiness`
  bağımlılığı olurdu, **R9 yasaklıyor**. Gerçek kapı `hazirlik-onayla` komutundadır ve
  "üretimde başka çağıran yok" iddiası artık tarama sonucu DEĞİL, tekrar koşulabilir bir
  testtir (`test_attest_readiness_URETIM_cagirani_YALNIZ_cli_onay_yoludur`); ikinci bir
  üretim çağıranı eklenirse kırılır.
  **Bir sıra hatası da bu turda ortaya çıktı:** test fixture'ları hazırlık tasdikini yönetici
  onayından ÖNCE yazıyordu — `md-19` kapı maddesi onay kaydını okuduğu için üretimde
  ULAŞILAMAZ bir sıraydı ve yalnız kanıt bağı olmadığı için görünmüyordu. Sıra düzeltildi.
  Önceki kayıt tarihsel bağlam olarak duruyor: Checkpoint 14'ün F1'i; beş hakem turunun ikisinde aynı eksende çıktı.
  Onay, okuduğu kanıtın (ham artefakt satırları) o ANKİ hâlini belgeler; tablo EKLEMELİDİR ve
  tasdik kaydının "ne gördüm" alanı YOKTUR (Task 8 sözleşmesi). **Daraltıldı:** değerlendirme ile
  yazım tek işlemde, koşu satırı `FOR UPDATE` kilitli ve yazımdan hemen önce kanıt kümesinin
  parmak izi TAZE okunup karşılaştırılıyor (`T17-fix3`). **Kapanmadı:** onaydan SONRA düşen bir
  satır damgayı hâlâ geçerli gösterir; ayrıca `runs.attest_readiness` prob sonuçlarını görmez,
  çağıranın küme iddiasını yazar. Gerçek kapanış iki yoldan birini ister — tasdik gördüğü kümeyi
  KAYDETSİN ya da aktivasyon hazırlığı YENİDEN ölçsün — ve ikisi de sözleşme kararıdır;
  prob kapısını yazıcıya koymak `runs → readiness` bağımlılığı demek olurdu, **R9 yasaklıyor**.
  **EV: arayüz eki revizyonu · sert son tarih Task 19** (bekleyen kümeye katılır).

- **[KAPANDI 2026-09-11 — R-G6] `readiness.evaluate` imzası ekten IRAKSIYOR.** Ek
  `evaluate(db, *, run_id)` yazacak biçimde düzeltildi; gerekçe (koşu kimliği olmadan
  okunacak artefakt YOKTUR) ekin metnine girdi. Kayıt tarihsel bağlam olarak duruyor: Ek yüzeyi
  `evaluate(db)` yazıyor; kod `evaluate(db, *, run_id)`. Koşu kimliği olmadan ön-kontrolün
  okuyacağı artefakt YOKTUR — on bir probun on biri koşu satırını ya da o koşunun ham
  artefaktlarını okur. Hakem ıraksamayı GEREKÇELİ buldu ve bloker saymadı.
  **EV: arayüz eki revizyonu · son tarih Task 19** (AÇIK-2 ile aynı partide).

- **[YÜKSEK — EVİ VAR 2026-09-11] Mekanik kapı raporunun artefakt türü şemada YOK.**
  Task 17 dispatch'inde ölçüldü (canlı yerel veritabanı, `sector_research_artifacts_kind_check`):
  şema yalnız `research` · `review` · `synthesis` kabul ediyor; CLI üç yerde Türkçe etiket
  yazıyordu ve hiçbir test o değerleri gerçek veritabanına karşı koşmadığı için kusur 4134 yeşil
  testin altında görünmüyordu. **İki ayak `T16-fix5` ile kapandı** (`review` · `synthesis`,
  sınıf düzeyinde AST kapısı + bayat-borç kapısı, ikisi de mutasyonla kanıtlandı).
  **Üçüncü ayak ÇÖZÜLMEDİ:** mekanik kapı raporu üç türden hiçbirine oturmuyor — `review`'a
  yazılırsa hazırlık listesinin "iki hakem raporu" ölçümü kirlenir. Yeni tür şema değişikliği
  ister; o güne dek `brief-doctor` alt komutu ham artefakt yazımında DÜŞER.
  **EV: Task 18 (ön-pilot dağıtım — şema ayağı), Eray kararı 2026-09-11.** Kod tarafındaki
  kaydı: `scripts/sector_pipeline_cli.py::SEMA_DISI_ARTEFAKT_TURLERI`.

- **[KAPANDI 2026-09-11 — R-G1 + R-G8] `BulguIzi`'nin dördüncü alanı arayüz ekinde SAHİPSİZ.**
  İKİ ayak da indi: (a) dördüncü alan gerekçesiyle ekin tip tanımına yazıldı (R-G1);
  (b) kaydın istediği ikinci ayak — `policy_report` kolonuna yazılan **kalıcı yük şekli** —
  ekte HİÇ GEÇMİYORDU ve `as_payload`/`from_payload` sözleşmesi olarak eklendi (R-G8).
  Kayıt tarihsel bağlam olarak duruyor:
  Task 14, atıf alanını (`kontrol`) Task 8 sözleşmesinin İÇİNDEN ekledi; ek `BulguIzi`'yi ÜÇ
  alanlı tanımlıyor ve Task 14'ün dosya yüzeyi yalnız `approval.py`. Bağımsız hakem R9'un
  (bağımlılık yönü) KIRILMADIĞINI teyit etti — kırılan sahiplik/dosya sınırı. Alan gereklidir ve
  gerekçesi ölçülmüştür (`sinif` riskli sınıfları ayırt etmiyor); eksik olan ekin bunu SÖYLEMESİ
  ve `policy_report` yükünün şekil sözleşmesini taşıması. Yürütücü spec/plan/ek DÜZENLEMEZ.
  **EV: arayüz eki revizyonu** — bekleyen kümede K-126 resmîlik ayağı ve K-03 kategori ayağıyla
  BİRLİKTE; sert son tarih Task 19 (sözleşme penceresi orada kapanıyor).

- **[YÜKSEK — kök sebep, EVİ VAR 2026-09-09] Motor çoğunluğu düz yazıdan sayıyor.**
  Denetçinin sekiz sütunlu denetim tablosu tipli okunmuyor (`validate_report` yalnız iki
  tabloyu ayrıştırıyor), bu yüzden `2-3` sınıfı ve destekleyen kaynak listesi denetçinin
  sütununda dururken motor onu sentezin `kanit` düz yazısından çıkarmak zorunda. Kapı bugün
  fail-closed ve dört sızıntısı kapalı, ama okuduğu şey hâlâ düz yazı.
  **EV: `docs/active/denetci-denetim-tablosu-tipli-okuma/TASK.md`** (yuva: Task 13 sonrası,
  Task 16 öncesi; sert son tarih Task 19).

- **[YÜKSEK — kapanışı DOĞRULANMADI 2026-09-09] Kanıt dilbilgisinin son düzeltmesi bağımsız
  hakem görmedi.** F2 kümesi dört-tavana ulaştı; kullanıcı kararıyla beşinci tur açılmadı.
  Son iki fix'in (`3c0f9e8` · `2697de6`) kapanışı kontrolörün kendi ölçümüne dayanır.
  Yeniden değerlendirme yeri: Adım 11 final incelemesi (tabanı `a806e29` olduğu için oraya
  kendiliğinden girer) ve `/review-claude-codex`.

- **[KAPANDI 2026-09-10 — bu kayıt 2026-09-11'e kadar BAYAT DURDU] `EngineInputs` paket/koşu
  bağı taşımıyor.** Kardeş görevde (`denetci-denetim-tablosu-tipli-okuma`) Eray kararıyla AYNI
  turda kapatıldı: bağ, motorun girdi alan kümesi AÇILMADAN kuruldu — kimlik `build_packet`'te
  mekanik rapor kümesinden TÜRETİLİR, denetçi çifti üzerinden TAŞINIR, `EngineInputs` yapımında
  KARŞILAŞTIRILIR. **Kalan kapsam sınırı (dürüst etiket):** kimlik `run_id` TAŞIMAZ, yani AYNI
  kaynaklarla koşulmuş iki ayrı koşuyu ayırmaz.
  **Defter dersi:** kapanış kardeş görevin dosyasına yazıldı, buraya YAZILMADI; kalem bu
  listede bir gün boyunca (2026-09-10 → 2026-09-11) "kabul edilmiş risk" göründü ve bu turun
  denetimiyle yakalandı. Bir kalem iki deftere bakıyorsa kapanışı İKİSİNE de işlenir.

- **[accepted_risk, medium — 2026-09-09] K-03'ün takvim-kategorisi ayağı UYGULANMADI.**
  `takvim_anahtarlari` yalnız anahtar taşır, kategori taşımaz. Motor yalnız paket içi tür
  etiketi değişimini ölçer ve ölçümün adı artık bunu iddia eder
  (`paket_turu_degisiklikleri`). Kategori ayağı arayüz eki revizyonu ister.

- **[EV BULDU ve SÖZLEŞME AYAĞI İNDİ 2026-09-11] K-126'nın resmîlik ayağı ve K-03'ün
  kategori ayağı.** Yeniden açılma koşulu ("arayüz eki revizyonu için bir spec açıldığında")
  GERÇEKLEŞTİ ve ikisi de ele alındı. **Ölçümle ayrıştılar — aynı kalem DEĞİLLERMİŞ:**
  · **K-126 resmîlik:** yargı denetçide yaşıyor ve düz yazıya gömülüydü. Sözleşme ayağı
    İNDİ (`12beec1`): KAYNAK PROFİLİ tabloya çevrildi, `resmi` sütunu (evet/hayır) eklendi.
    **Kalan:** denetçi raporu ayrıştırıcısının bu sütunu tipli okuması + motorun K-126
    kapısının onu tüketmesi. **EV: bir sonraki oturumun kod uyarlaması.**
  · **K-03 kategori:** DIŞ SÖZLEŞMEYE HİÇ DOKUNMUYOR. Kategori zaten sistemin takvim
    tablosunda (`social.public_holidays.category`, ölçüldü); eksik olan onu `EngineInputs`'a
    taşımak — yani R5 alan kümesi değişikliği, tamamen İÇERİDE. Eski kayıt bunu denetçi
    sözleşmesi eksiği sanıyordu; **yanlıştı, düzeltiliyor.**
    **EV: bir sonraki oturumun kod uyarlaması.**
  Aşağıdaki eski kayıt tarihsel bağlam olarak duruyor: İkisi de aynı eksiğe bakar: denetçi sözleşmesi
  bu iki bilgiyi (kaynağın resmî/birincil olması · takvim anahtarının kategorisi) TİPLİ
  taşımıyor, o yüzden motor onları ölçemiyor. Bugüne dek "arayüz eki revizyonu ister" diye
  yazılıydılar — bu bir AD, tarih değil; hiçbir plana, faza ya da göreve bağlı değiller.
  **Yeniden açılma koşulu:** denetçi sözleşmesi bu alanları tipli taşımaya başladığında ya da
  arayüz eki revizyonu için bir spec açıldığında; gövdeleri o spec'in girdisi olarak burada
  durur. **Aktif borçtan ÇIKARILDI** — reflekssel ev vermek kova döngüsünü besler.
  *Bitişik ama AYNI DEĞİL:* `denetci-denetim-tablosu-tipli-okuma` görevi denetim TABLOSUNUN
  tipli okunmasıdır; bu iki alanı kapsamaz ve onlara ev diye GÖSTERİLMEZ.

- **[accepted_risk, medium — 2026-09-09] K-129 yüklemi mekanik yaklaşımdır.** Rakam kolu
  sıradan sayısal metni de mevzuat sayar (yön fail-closed); alt-dize eşlemesi Türkçe eklemeli
  olduğu için bilinçlidir. Genişletmesi spec revizyonudur.

- **[YÜKSEK — yeniden evlendirildi 2026-09-09] Denetçi web erişim probunun ÜRETİM sahibi
  Task 11 DEĞİL, Task 16'dır.** Devir notu bu yükümlülüğü Task 11'in dispatch'ine yazmıştı;
  yanlıştı ve düzeltiliyor. **Ölçüldü:** `grep -rn 'run_audit_round(' --include='*.py'` test
  dışında yalnız tanımı buluyor, `synthesis.run(` için üretim çağıranı HİÇ YOK. Yani prob,
  Task 11'in eksik bir parçası değil — Task 11 zaten kurulmuş bir `AuditRound`'dan sonra
  başlar. Gerçek ev, üretim orkestrasyonunu kuran CLI'dır:
  `apps/social/backend/scripts/sector_pipeline_cli.py` (**Task 16, planda zamanlanmış**).
  **Etiket dürüst: ÇÖZÜLMEDİ.** Bugün K-14 kapısı probsuz her turu bloke ediyor (doğru
  davranış), yani hat üretimde HÂLÂ koşamaz.

- **[accepted_risk, medium] Reddedilen çıkarmanın metin/özel-gün kolu (2026-09-09).**
  `_geri_koy` birim hâlâ yerindeyse NO-OP'tur (yaygın hâl kapandı), ama gerçekten adaydan
  düşmüş bir düz metin alanı ya da özel gün yuvası geri KONULAMAZ ve koşu yarım işaretlenir.
  Yeniden açılma koşulu: gerçek koşumda bu kolun tetiklendiği ölçülürse.

- **[accepted_risk, medium] Sentezin koşu başına kiralaması YOK (2026-09-09).** Hedef dizin
  kontrolü kontrol-sonra-yarat desenidir; aynı `run_id` ile iki çağrı çakışırsa kaybeden
  koşuyu `tamamlanmadi` işaretlerken kazanan geçerli sonuç dönebilir. Denetçi tarafında
  kiralama VAR, sentezde yok. Yeniden açılma koşulu: hat gerçekten eşzamanlı çağrılırsa.

- **[accepted_risk, medium] TOCTOU penceresi daraltıldı, KAPANMADI (2026-09-09).**
  `run_audit_round` her alt süreç çağrısından önce rol yolunu yeniden doğruluyor, ama
  doğrulama ile kullanım arası atomik değil; kapanması dosya tanımlayıcı tabanlı koşum
  (`openat`/`fchdir`) ister. Kodda beyan + tripwire testi var. Yeniden açılma koşulu:
  tehdit modeli değişirse (çok kullanıcılı ya da ağ erişimli hat) bu KAPANMALIDIR.

- **[Task 11'in devraldığı] Denetçi web erişim probu YOK.** K-14 kapısı bugün probsuz her
  turu bloke ediyor — doğru davranış, ama probu sağlayacak katman Task 11. Bu yüzden
  "erişim gerçekten yoktu" iddiası hâlâ DOĞRULANMADI; yalnız "erişim ölçüldüyse muafiyet
  yasak" ölçüldü. Task 11 dispatch'ine ZORUNLU kalem.

- **[düşük] Tip denetleyicisi uyarıları (2026-09-09, ölçülmedi).** Pyright
  `auditors.py::check_snapshot_agreement`'ta 11, `test_auditor_orchestration.py`'de 10 uyarı
  veriyor (`ValidatedReport.rapor` `AuditReport | None` olduğu için `gecerli` kontrolünden
  sonra daraltılamıyor; testlerde `list` vs `tuple` değişmezliği). Testler geçiyor, çalışma
  hatası değil. `ruff` bu ortamda KURULU DEĞİL, lint hiç koşmadı.


- **[risk kabulü — Eray onayı] Bölüm C'nin üçlü yapısı makineyle doğrulanmıyor (high, RİSK
  KABULÜ — Eray onayı 2026-09-07).** Mekanik girdi kapısı, kaynak eşlemesinin gerçekten
  `alan/dönem → iddia → kaynak` üçlüsü olduğunu serbest düzyazıdan çıkaramıyor. Ölçüldü:
  `- Düz yazı, devamı https://example.com/kaynak` → `gecti`, 0 not. Üç hakem turunda yakınsamadı
  (semantik-negatif sınıfı: kapı bypass ile yanlış-pozitif arasında salınır).
  **ONARILMADI — raporda `url-bicimi` kapsam beyanı olarak DÜRÜSTÇE İLAN EDİLDİ**, denetçi
  görüyor. Ayıraç vekili bilinçle SERTLEŞTİRİLMEDİ.
  **Kısmen devredildi, tam çözülmedi (ölçüldü):** denetçi sözleşmesinin ADIM 1'i kaynak başına
  3 iddia örnekleyip bağlantıyı GERÇEKTEN açıyor — makinenin yapamayacağı daha güçlü kontrol.
  Ama örnekleme, "her alan için kaynak gösterilmiş mi" BÜTÜNLÜK sorusunu cevaplamıyor; kaybedilen
  tam olarak bu, ve spec'in "mekanik iş dil modeline verilmez" hükmüyle gerilim taşıyor.
  **EV: kendi görevi vardı (2026-09-07'de açıldı) ve AYNI GÜN BİTTİ** (`status: done`) —
  `docs/active/brief-sozlesmesi-kaynak-bolumu-makine-okunur/TASK.md`. **Arşive Plan 2 ile
  BİRLİKTE gider**, tek başına taşınmaz: değiştirdiği sözleşme metnine Task 9/10 dokunacak,
  kayıt plan koşarken ana görevle aynı yerde kalır.
  **Yuva GERÇEKTE Task 8'den ÖNCE doldu** (görevin kendi düzeltme notu, 2026-09-07);
  aşağıdaki "Task 8'den sonra" tarifi o günün planıydı, gerçekleşen bu DEĞİL — Task 9'un
  önünde bu kalemden gelen bir kapı YOKTUR.
  **O günkü yuva tarifi (kayıt için): Task 8 bittikten SONRA, Task 9'a girmeden ÖNCE.** Son tarih değil YUVA:
  Task 9/10 denetçi katmanını kurar ve sözleşme değişikliği o metne de dokunur; ayrıca Task 19
  Step 5 araştırmaları tek seferde yeniden üretir. Ölçüldü: şu anki sözleşme biçiminde üretilmiş
  gerçek çıktı bugün YOK, yani değişiklik şimdi bedelsiz.
  **KAPATILDI 2026-09-07 (monorepo `854373d`).** Dört ayak da indi; Task 7'nin kapsam beyanı
  üç yerden de kalktı. BÜTÜNLÜK sorusu artık makineyle cevaplanıyor — kaybedilen şey geri
  alındı. **Kalan ve ETİKETLİ:** sözleşmenin yeni biçiminde üretilmiş gerçek araştırma çıktısı
  YOK, dolayısıyla araçların tabloyu ne kadar düzgün ürettiği ve katı biçimin yanlış-pozitif
  oranı ÖLÇÜLMEDİ; ilk gerçek ölçüm Task 19 Step 5'te doğacak.

- **[risk kabulü] Uydurma içerik özeti kapıyı geçebiliyor (medium, kabul).**
  Biçimi geçerli ama `run`'ın üretmediği bir özet yazan doğrudan-kurucu K-127 tabanını geçiyor
  (ölçüldü: `dur=False gecerli=2`). Metne sahip olmayan çağıran için kapatılamaz; beyan edildi.
  **Bugün depoda böyle bir çağıran YOK** (kontrolör taradı). Yeniden açılma koşulu: Task 9 ya da
  Task 12 `run` yolunu atlayan bir rapor kurucusu eklerse.

- **Kanonik gerekçe-tablosu başlığı taklit edilebilir (low, kabul).** Belirsizlik notu düşer ve
  dönem öncesindeki BÜTÜN tablolar denetlenir — **gizlenme YOK** (ölçüldü, üretilmiş matrisle) —
  ama hangisinin gerçek olduğu doğrulanmıyor.
  **NOT: bu kalemin bir önceki yazımı YANLIŞTI.** "Aday 2 olur, gizlenme yok" deniyordu; ölçüm
  gerçek tablonun başlığı eşiğin ALTINDAYSA aday sayısının 1 kaldığını ve gizlenmenin
  GERÇEKLEŞTİĞİNİ gösterdi. Seçim tamamen bırakıldı, sonra bir DEĞİŞMEZ kondu.

- **Sözleşme-biçimli ama ALAKASIZ içerik kabı doldurur (kabul, SEMANTİK — kapatılamaz).**
  Bir düz yazı satırının o alanla ilgili olup olmadığı makineyle ölçülemez. Hakem tur 7'de bunu
  "gerçekten semantik" diye sınıflandırdı. Aynı sınıf: dilli kod çiti · blockquote · HTML bloğu
  hâlâ kabı doldurur — bunlar mekanik olarak kapatılabilir ama daraltmanın gerçek çıktıdaki
  yanlış-pozitif maliyeti ÖLÇÜLEMEDİ (o biçimde üretilmiş gerçek çıktı yok). Envanter tripwire'ı
  bu kalemleri sabitliyor: biri kapatılırsa test kırılır ve beyan güncellenmek zorunda kalır.

- **Düzey 1-2 ara başlık Bölüm B'yi kapatır (kabul, gürültülü ama SESSİZ DEĞİL).**
  Ölçüldü: 63 başlık enjeksiyonunun **sıfırı** raporu temiz yapabildi; kaybolan bloğa-ait notların
  yerine gürültülü küme notları geliyor. Hakem tur 6'da bağımsız olarak aynı 63 enjeksiyonu
  tekrarladı ve aynı sonucu aldı. Kapatmak bölüm tanımayı markdown düzeyinden koparmayı ister.

- **Task 1'in üç Minor bulgusu Task 2'de KAPANDI** (`1186d44`): depo-yok kapısı artık kendi
  sebebine assert ediyor · `_head_commit` çözümlemeyi verilen köke sabitliyor · hiçbir sözleşme
  dosyası adlandırmayan manifest `load_pin`'de reddediliyor (kapı kümesi DÖRT kaldı — ek R14).
- **Hakemin doğrulayamadığı iki durum EV BULDU (2026-08-30 kapanış sweep'i): Task 18 Step 8b.**
  `git` ikilisi olmayan ortamda davranış ve `GIT_DIR`/`GIT_WORK_TREE` ezilmesi. Neden orası:
  pin doğrulayıcısı commit'i `git rev-parse` ile okur, yani ikili yoksa resmî koşuyu başlatan
  HER CLI alt komutu ilk adımda patlar — bu bir **dağıtım** sorusudur, kod sorusu değil.
  Tarih: Task 18 koşana kadar yok; yürütme oraya varmadı. Dürüst etiket: *doğrulanmadı; evi ve
  adımı var.*
- **KABUL EDİLMİŞ RİSK (arayüz eki, tur 3 sonrası):** "annotation çalışma zamanı zorlaması
  değildir" sınıfının kalıntısı ve kimlik karşılaştırmalarındaki hoşgörülü normalleştirme.
  Dördüncü hakem turuyla kovalanmadı; kod yazılırken kırmızı-yeşil döngüsüne ve görev-başı
  review'a devredildi. Bu bir **kabul**, sınıfın kapandığı iddiası DEĞİL.
- **Ortam gerçeği (ölçüldü, plandan farklı):** planın yazdığı `python -m pytest` bu makinede
  çalışmaz — `python` PATH'te yok. Her test komutu
  `cd apps/social/backend && source .venv/bin/activate && python -m pytest …` biçiminde koşar.
- **Task 5'in operatör kararı KAPANDI (2026-09-02)** — beş seed değeri Decisions Log'da
  tablo hâlinde sabit. **Task 19'un dört operatör kararı hâlâ açık** (o göreve gelindiğinde
  sorulur, şimdi değil).
- **30 teknik kalem BAĞLANDI** (plan yazımında); kapanış görevi (Task 20) 30 teknik + 13 ürün
  kararını tek tek sweep eder.
- **§8.7'nin sözleşme düzeltmeleri KAPANDI** (Task 2, dış depo `6d2a033`+`d901eb4`): altı kalem
  + yedi yansıma kalemi, sweep 13/13 "var". Resmî turu artık bloklamıyorlar.
- **Task 2'den Task 4'e devredilen üç sözleşme kalemi — Task 4'te KAPANDI (2026-08-31).**
  Ölçüldü (dış depo `6d5d90d`): sürüm damgası düzeltmesi `hakem-sentez-gorevi.md` satır 18 ve
  `hakem-denetci-gorevi.md` satır 12'de yazılı; `muhtemel-uydurma`nın bayrak OLMADIĞI
  `hakem-sentez-gorevi.md` satır 129 ve 133'te açıkça duruyor. Kayıt tarihsel bağlam olarak
  kalıyor — devralınan hâlleri şunlardı: (a) iki farklı bayt kümesi aynı sürüm damgasını
  taşıyor (`6d2a033` ve `d901eb4` ikisi de "Sürüm 1.3"/"Sürüm 1.2") — kapı sha256'ya baktığı
  için mekanik risk yok, izlenebilirlik pürüzü; (b) iki genel hüküm kanal-bayrağı maddesinin
  içine yerleşmiş (28 satırlık madde), içerik doğru yer yanıltıcı; (c) `hakem-sentez-gorevi.md`
  satır 100 `[muhtemel-uydurma]`yı bayrak biçiminde anıyor ama kapalı bayrak kümesi sekiz üye
  ve onu içermiyor.
- **CTA köşeli ayraç çelişkisi — ÇÖZÜLMEDİ, park edildi, tetiği var:** yazım kapısı
  `cta_kaliplari` ve `ozel_gun[*].cta` içinde bayrak olmayan HER ayracı reddediyor, ama
  `_SABLON.md` araştırmacıya CTA kalıplarını ayraçlı değişkenlerle soyutlatıyor. Task 2 bunu
  sözleşme metninde **açıkça açık** bıraktı ("BİLİNEN ve AÇIK bir kalem"), gizlice çözmedi.
  Task 2'nin ürünü DEĞİL, önceden var. Tetik: ilk kuru koşum (Task 11 veya Task 19), ya da
  `_check_channel_markers`'a dokunan herhangi bir değişiklik.
- **Task 15'in elle arayüz doğrulaması** Task 19 Step 11'de; plan onaylı, tarih pilot görevinin
  koşmasına bağlı. Dürüst etiket: *çözülmedi; evi var.*
- **n8n hata bildirimi** Task 16 Step 7/7b'de; kapsam bilinçle dar (yalnız sektör paketi
  zinciri), kalan workflow'lar CRM turunda.
- Plan 1 bölümlerinin kart geçişi taranmadı (boşluk raporu kapsam sınırı) — Plan 1 alanında
  kusur çıkarsa koşulur.

- **Geri alma artık bir OPERATÖR ADIMI isteyebilir — bilinçli, evi VAR (Task 18 Step 9).**
  Tur 6 öncesinde: yıllık takvim işi bir 035 dönem satırını düzeltmişse geri alma o satırı
  sessizce siliyordu (ölçüldü). Şimdi **fail-closed durur** ve etkilenen satırları adıyla
  söyler; operatör `end_date`leri boşaltıp geri almayı tekrar koşar. Alternatifi sessiz veri
  kaybıydı. **Ölçüldü (2026-09-06): geri almayı OTOMATİK çağıran hiçbir yol yok** — depo
  genelinde ne betik, ne uygulama, ne n8n işi. Yani günlük iş yükü YARATMAZ; yalnız biri
  bilerek geri alma koşarsa görünür. **Ev:** Task 18 Step 9 dağıtım runbook'u
  (`docs/plans/PLAN2-DAGITIM-RUNBOOK.md`, planda `Create:` kalemi — doğrulandı) geri alma
  sırasını yazarken bu adımı içermek ZORUNDA. Tarihi Task 18'in koşmasına bağlı.
  Dürüst etiket: *çözülmedi değil — bilinçli tasarım kararı; runbook'a yazılması borç.*

- **KAPANDI (2026-08-31, checkpoint 2).** Aşağıdaki borç artık açık DEĞİL: checkpoint 2'nin
  tabanı `72f5744` olduğu için `ad95846` o incelemenin aralığına girdi ve bağımsız hakem o
  aralıkta yeni kusur bulmadı. Adlandırılmış kapsanma yolu gerçekleşti — tahmin değil, ölçüm.
  Kayıt tarihsel bağlam olarak duruyor:

- **Düzeltme turu 3 bağımsız hakem GÖRMEDİ — kabul, evi VAR.** Kapanış kontrolör kararıdır
  (sınıf 47 atıflık üretilmiş matrisle kapatıldı; dördüncü yargı turu açılmadı çünkü üç tur
  da aynı ekseni buluyordu). **Ev uydurulmadı:** dal kapanışındaki final inceleme tabanı
  `a806e29` olduğu için bu commit (`ad95846`) o incelemenin aralığına ZATEN giriyor —
  kendiliğinden kapsanır. **Yeniden açılma koşulu:** Task 3 yüzeyinde (`insert_draft`,
  `check_unit_integrity`, kimlik modülü) bir kusur çıkarsa ilk bakılacak yer bu turdur.
  Dürüst etiket: *bağımsız yargı alınmadı; kapsanma yolu adlandırılmış.*

## Task 6'nın doğurduğu kalemler (2026-09-06 kapağında karara bağlandı)

- **YAPISAL BULGU — düzyazıdaki sayı iddiaları review turlarıyla doğru tutulamıyor.**
  Tek görevde **yedi** örnek: (1) yanlış `ÖLÇÜLMÜŞ` etiketli katalog-bağımlılığı yorumu ·
  (2) yarısı kapalı bir sınıf "kapandı" diye sunuldu · (3) bayatlamış "yalnız yarısı çevrilebilir" ·
  (4) 9/12 yerine 8/11 · (5) uygulayıcının kendi mutasyon etiketi · (6) düzeltme paragrafının
  içinde iki `dokuz` daha · (7) tur 5'in kendi yorumu kapı kapsamını 16 diyor, kapı 11 kapsıyor.
  **Yedisinin de çalışma zamanı etkisi SIFIR.** Bağımsız hakemin ölçümü: yedi arızanın yedisi de
  korumasız düzyazı bölgesinde; tur 5'in kurduğu iki kapı **hiç arıza çıkmamış** bir bölgeyi
  koruyor ve yedi örneğin hiçbirini yakalayamazdı.
  **İKİYE BÖLÜNDÜ (İlke 7 lighter-version testi — ilk park etme over-bundling'di):**
  - **(A) ŞİMDİ, maliyeti sıfır — HANDOFF'ta bağlayıcı taşınıyor:** kalan 14 görevin her dispatch
    brief'ine ve her hakem prompt'una tek paragraflık kural — *gönderilen düzyazıya sayı yazma;
    ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.* Akan borcu bu yarı durdurur.
    **Dürüst sınır: bu bir KURAL, kapı değil — davranış katmanında, testle zorlanmıyor.**
  - **(B) PARK — çözülmedi, evi var, tarihi yok:** mevcut düzyazı yüzeyinin geriye dönük taranması
    (ölçüldü: Task 6'nın dokunduğu 11 dosyada sayı+sayılan-isim taşıyan **303** aday yorum satırı)
    **ve** politikanın seçilmesi (düzyazıda sayı yazma / sayıları üret / "doğrulanmadı" etiketle).
    **Ev: dal-sonu bütün-dal incelemesinin triage listesi.** O ev bir **KARAR** noktasıdır,
    düzeltme değil; düzeltme kararı orada verilirse ayrı iş olarak planlanır.
    Uydurma bir görev numarasına yapıştırılmadı.
- **F1 (Important, park edildi — sessizce DEĞİL):** `tests/test_migration_036.py:1510`
  "(16 iddia, tek kapı)" diyor; kapı AST ile ölçüldü, **11** iddia kapsıyor — kapsamı %45 abartıyor.
  Beş satırlık fark, `N hücre` docstring'i taşımayan testler; elle ölçülmüşler, kapının dışındalar.
  **Codex checkpoint dispatch'inde ÖNDEN bildirilecek** (hakemin takılıp bulması beklenmiyor) ve
  dal-sonu triage listesine düzeltmesi yazılmış hâlde gidiyor (16 → 11).
- **F2 (Minor, park edildi):** `:1504` "beş turda DÖRT kez aynı kusuru üretti" — doğru sayı **yedi**.
  Üreten komutu olamayacak bir sayı; bu turun kendi kuralıyla ölçüm değil düzyazı.
- **İlk hakem turunun YEDİ Minor'u** dal-sonu incelemesine ertelendi (defterde tek tek yazılı).
  İçlerinden biri operasyonel: **036 uygulandıktan sonra tek bir atama geçmişi satırı bile varsa
  `032_down.sql` kalıcı olarak erişilemez** — fail-closed, tehlikeli değil, ama **Task 18
  runbook'una bir satır gerekiyor**.
- **Devir — Task 18:** (a) `get_holidays` önbelleği (Task 5'ten) · (b) geri alma sırası +
  operatör adımı · (c) yukarıdaki `032_down` erişilemezliği · (d) düzeltilmiş iki n8n workflow'unun
  canlıya import edilmesi (CURRENT.md `n8n-workflow-sir-hijyeni`).
- **İki commit mesajı geri çekilmiş iddia taşıyor ve DEĞİŞTİRİLEMEZ:** `d1edd51` (katalog
  bağımlılığı) ve `c73f9b0` ("twelve types that exist today"). Raporda kayıtlı.

## Task 3'ün doğurduğu evler (2026-08-30 kapanış sweep'i — hepsi TARİHLİ)

- **Taslağın yaratıcısı kayboluyor — KAPSAM DIŞI BIRAKILDI (Eray kararı, 2026-09-10).**
  Önceki kaydı burada "EŞLİ yükümlülük, Task 6 + Task 15" diyordu ve o kayıt
  **yanlıştı** — ölçüldü (2026-09-10): bu gereksinim spec girdisinde (0 geçiş),
  spec'te (0 geçiş) ve arayüz ekinde (0 geçiş) YOK. Plandaki tek geçiş MEVCUT
  davranışın tarifi; yapılacak işin değil. Spec'in tablo sözleşmesi alanları tek tek
  sayıyor ve aktör alanı listede yok. Planın "Plan 1 arayüzünde yapılan değişiklikler"
  listesinde de yok. Plan 037 numaralı bir migration ÖNGÖRMÜYOR. Kalem yürütme
  sırasında bir hakem bulgusundan doğdu ve **plan hiç güncellenmedi** — Task 6 kendi
  ayağını bu yüzden indirmedi, çünkü planında öyle bir madde yoktu.

  **Kapatma DENENDİ ve ölçülerek geri alındı (Task 15, 2026-09-10).** Olay türünü açan
  bir migration yazıldı; yayılma yarıçapı önceki migration'ların sürüm-farkında kabul
  tablolarına, geri alma script'lerine ve çapraz migration fail-closed testlerine ulaştı.
  Her yama kapattığı kadar yeni kırık açtı (düşen test: **25 → 21 → 22**). Son harness
  düzeltmesi, amacı *"üstteki migration uygulanmışken reddetmeli"* olan bir testin
  premisini yok etti — o noktada şeyin kendisi değil ÖLÇÜM ARACI yamalanıyordu.
  Yarım inen şema bırakmamak için değişiklik **BÜTÜNÜYLE** geri alındı: iki migration
  dosyası silindi, dokunulan her dosya eski hâline döndü, takım yeşil.

  **DÜRÜST ETİKET: çözülmedi. "Halledildi" DEĞİL, "kapsam dışı bırakıldı".**
  **YENİDEN AÇILMA KOŞULU:** ikinci bir operatör eklendiğinde, ya da paket üretimine
  müşteri/dış taraf eriştiğinde. O gün kendi tasarım turunu ister; kapanışa
  sıkıştırılmaz.

  **Task 20 kapanış belgesine bu etiketle YAZILIR** (plan Task 20 Step 6: "her kalan iş
  ya tarihli bir eve gider ya dürüst etiketle DÜŞÜRÜLÜR" — bu, düşürme koludur).

  **Kapsamın dürüst sınırı — bugün atıflı olanlar:** taslağı ÜRETEN koşu (paket
  satırındaki koşu bağı), kontrol listelerini İMZALAYAN operatör (tasdik yükleri),
  ONAY/RET veren yönetici ve GERİ ALAN operatör (olay kayıtları). Atıfsız kalan tek
  halka, taslak yazımını/düzeltmesini TETİKLEYEN kişidir.

  **Plan 2'nin tamamlanmasını ENGELLEMEZ — ölçüldü:** kabul ölçütleri (spec §14.1 +
  §14.2) bu kalemi içermiyor; yirmi maddelik işletime hazırlık listesinin hiçbir maddesi
  taslağın yazarını sormuyor; Task 16-20'de "aktör" yalnız geri alma komutunun argümanı
  ve hazırlık onayının imzası olarak geçiyor — ikisi de kayıtlı.

- **`GIT_DIR`/`GIT_WORK_TREE` ezilmesi ekseni — Task 18 Step 8b, İKİ örnek birden.** Üretim
  tarafı (`contracts.py::_head_commit`) ve test tarafı
  (`test_external_repo_gitignores_run_folder`). Tek süpürme ikisini kapatır; ayrı ayrı
  yapmak yarım sınıf kapatır.
- **Yol sıra numaraları KONUMSAL.** Bir liste öğesi silinince ya da sırası değişince sonraki
  her öğenin `oge_yolu`'su kayar; kimlik `unit_id` ile yaşar. **Sürümler arasında yol
  karşılaştıran her tüketici `unit_id`'ye anahtarlamalı, `oge_yolu`'na ASLA.**
  Task 9, 12 ve 13 dispatch'lerine taşınır.
- **"Not" satırının alan kümesi bir ÇIKARIMDIR ve kanonik dayanağı yok.** Ölçüldü: `sinif`
  spec-input'ta ve spec'te HİÇ geçmiyor; yalnız plan 579-580 iki kapalı değeri sabitliyor.
  Hakem kapalı tutmayı doğru yön saydı (reddedilen satır sesli patlar). Ama içinde gerçek bir
  boşluk var: iki not sınıfının da *not edilen şeyi* koyacak alanı yok ve bu, spec-input
  728/1099'da **K-87 ve K-108 olarak hâlâ AÇIK**. Yukarıda kapanmamış, burada kapatılamaz.
  Task 9 ve Task 13 dispatch'lerine taşınır; uyarı: `gerekce`'ye tıkıştırmak fiilî cevap
  hâline GELMESİN.
- **Dış deponun İÇİNDE dışarıyı gösteren sembolik bağ — çözülmedi, park edildi, koşulu var.**
  Kapatmak `verify_pin`'e içerilik çözümlemesi eklemeyi gerektirir; bu, ekin R14 hükmünün
  yasakladığı beşinci kapıdır. Modül belgesinde dürüst etiketiyle ve yeniden açılma
  koşuluyla duruyor. **"Ele alındı" DEĞİL.**
- **033'ün geri alma dosyası YOK — çözülmedi, evi var, tarihi Task 6'ya bağlı.** Ölçüldü
  (2026-08-31): `shared/db/migrations/rollback/` yalnız `032_down.sql` taşıyor. Hem kod
  belgesi hem rapor, olay türü yolunun bedelini "migration + rollback" diye yazıyor; o yol
  seçilirse `033_down.sql` sıfırdan yazılacak. Ev: **Task 6** — zaten olay türü genişletmesini
  ve migration'ını F1 eşli yükümlülüğü altında sahipleniyor.
  Dürüst etiket: *çözülmedi; evi ve adımı var.*

## Arayüz eki revizyonu (2026-09-08) — Task 8 karar kapısı KAPANDI

Task 8 dispatch'inin önünde dört kalemlik bir karar kapısı vardı (hepsi ekin metnine aitti);
dördü de ölçülerek kapatıldı ve ek revize edildi. **Hiçbiri yeni kapsam açmadı.**

- **R-A — hüküm (a)'nın ad kümesi.** Eski hüküm "kullanılan TEK ad `identity.canonical_sha`"
  diyordu. Ölçüldü: `sector_package_lifecycle.py` `identity`den İKİ ad kullanıyor
  (`validate_decision_log` · `check_unit_integrity`) ve `canonical_sha`'yı HİÇ çağırmıyor —
  645 satırda tek hash hesabı yok. Sebep meşru: Task 3'ün şema kapısı `insert_draft` içinde
  koşar, kuralın ikinci kopyası yazılamaz. **Karar: ad sayısı değil KENAR bağlanır** — tek
  import, MODÜL biçiminde, hedef YAPRAK, başka `sector_pipeline` modülü yok; kullanılabilir
  ad kümesi `identity`nin ÜRETİLMİŞ public yüzeyi. **Kapısı yazıldı** (elle liste YOK):
  `test_lifecycle_uses_only_identitys_public_surface` + ayırt edicilik kolu
  `test_identity_name_gate_rejects_a_name_outside_the_surface`.
- **R-B — düzyazı ↔ SQL çelişkisi.** Yukarıda Open Problems'ta.
- **R-C — onay mührünün yüklemi metinde YAZILI DEĞİLDİ.** Kod ekten öndeydi: 036 dolu → BOŞ
  geçişini REDDEDİYOR (satır 190-199), çünkü mühür silinebilseydi değişmezlik İKİ ADIMDA
  atlatılırdı (temizle → hedefi değiştir → yeniden mühürle) ve `num_nonnulls ∈ {0,3}` CHECK'i
  buna izin verirdi (ölçülen zincir `target_version`'ı 3'ten 99'a taşıyordu). Üç geçişin
  üçü de artık ekte tablo hâlinde yazılı; yeniden mühürleme BİLEREK açık kalıyor.
- **R-D — aktör kapısının tanım yeri.** Ek üç yerde tanımı `sector_package_lifecycle`
  satır 147-150'de gösteriyordu. Ölçüldü: o ad bir YENİDEN-DIŞAVURUMDUR; tanım
  `package_events.require_actor`tadır (satır 258-280). Sebep ölçülmüş bir DÖNGÜdür.
  Import biçimi ve davranış DEĞİŞMEDİ — yalnız yanlış adres düzeltildi.

**Bu revizyonun sınırı — dürüst etiket:** dördünü de **bağımsız hakem GÖRMEDİ**; kontrolör
kararıyla yazıldılar. Evleri var: final incelemenin tabanı `a806e29`.

**Ön-yürütme taraması BİR GERÇEK BULGU verdi ve kapandı (`e854add`).** R-B turunda SQL'e
eklediğim DELETE kolunu 036 ile hizalamak için geri almıştım, ama düzyazıdaki *"...ve satırın
kendisinin silinmesidir"* cümlesini geri ALMAMIŞTIM — ekin aynı bölümü iki şey birden
söylüyordu. Kendi açtığım tutarsızlıktı, park edilmedi. Aynı taramanın iki "önkoşul" bulgusu
(DB yanıt vermiyor · `.venv` yok) ÖLÇÜLEREK çürütüldü: PostgreSQL 18.3 ayakta, `.venv` var —
ikisi de Codex kum havuzunun kendi sınırı, kanıt sayılmadı.

**R-B'nin açık ayağı Task 8'de KAPANDI (2026-09-08).** Karar: **hard DELETE**. Gerekçe
ölçülmüş: `incident_scope_sha` üyelik parmak izini `durum`'u dışarıda bırakarak kurar, yani
durum tabanlı bir "çıkarma" satırı hash'in içinde bırakır ve üyelik daralması her kapıda
görünmez olurdu. Bağlanan sınır iki ayakla karşılandı — 036'nın tetikleyicisi
`BEFORE DELETE OR UPDATE`e genişletildi (`TG_OP` kolu EN BAŞTA; yürütülmüş satır silinemez,
`bekliyor`/`hedefsiz` silinebilir) ve `amend_rollback_plan` mühür düşürünce yönetici olayı
yazıyor. **Ekin metni bu karara göre güncellendi**; ekin SQL bloğu ile 036'nın kilitli alan
kümesi bağımsız çıkarıldı ve EŞİT.

## Task 8 (2026-09-08) — indi

**Commit `3b4beec`** — koşu ve artefakt servisi. `runs.py` (1836 satır) + `engine_contract.py`
+ `readiness_items.py` yeni; `sector_package_lifecycle.py` genişledi; `036_package_runs.sql`
ve `rollback/036_down.sql` **yerinde** değiştirildi (037 denendi, 036'nın kapalı tetikleyici
manifestini kırdığı için geri alındı — bu ekin harfiyen yazdığı yoldu).

**Uygulayıcının kendi dürüst etiketleri (kontrolör tarafından doğrulanmadı, hakem turuna
girdi olarak taşınır):**
- **TDD sırası ders kitabı değildi:** modüller önce, testler sonra yazıldı; Step-2 FAIL'i
  modüller kaldırılıp geri konarak üretildi. Sonraki kırmızı→yeşil turları (26 → 12 → 0)
  gerçek.
- **A4'ün dördüncü koşulu DARALTILDI.** `activation_evidence_payload`'ın
  `checklist_approved`'ı ekin dört koşulundan ÜÇÜNÜ uyguluyor; dördüncüsü
  (`sha == readiness_items.MADDE_KUMESI_SHA`) yaşam döngüsü modülünde KOŞAMAZ, çünkü AÇIK-3
  `identity` dışında hiçbir `sector_pipeline` modülünün import edilmesini yasaklıyor ve
  `readiness*` orada adıyla sayılı. Uygulayıcı import kenarını değil boolean'ı daralttı;
  eşitliğin adı konmuş sahibi Task 15 (`writeback.activate_from_snapshot`). **Sonuç: bayat
  sha taşıyan bir tasdik JETON BASTIRABİLİR; aktivasyon Task 15'in kapısında reddedilir.**
  Bu ekin bir hükmünden sapmadır ve hakem turunun ilk kalemidir.
- **Aktivasyon yükünün anahtar kümesi YEDİ değil ALTI.** Eksik ad `expected_no_active`,
  Task 15'in kalemi; küme dataclass'tan TÜRETİLDİĞİ için Task 15 inince kendiliğinden yediye
  çıkar. Geri alma yükü ekin bağladığı gibi tam BEŞ.
- Jeton tüketimi hiçbir yerde koşmuyor (`_consume_provenance` Task 15); bugün elle kurulmuş
  bir kanıt nesnesi iki geçişten de geçer, yalnız ŞEKİL kapıları koşar.

## Yürütme kadansı kararı (2026-09-08, Eray) — bölerek dispatch

> **KARAR DARALTILDI (2026-09-08, Eray — Task 9 dispatch'inden hemen önce).** Aşağıdaki
> **uygulama-bölmesi UYGULANMIYOR**: plan görevleri TEK PARÇA dispatch edilir. Bölünen yalnız
> **inceleme turudur** (aşağıdaki genişletme). Gerekçe: inceleme bölmesinin ölçümü var (1200 sn
> tavanında rapor üretemeyen tur, bölününce beş bulgu); uygulama bölmesinin kuyruğu kısaltacağı
> ÖLÇÜLMEDİ ve metnin kendisi "kontrollü bir deney DEĞİLDİR" diyor. **Yeniden açılma koşulu:**
> tek parça dispatch edilen bir görev yine 30+ commit'lik düzeltme kuyruğu üretirse.
> Aşağıdaki gövde, o gün ölçülmüş sayıların kaydı olarak DURUYOR — kural olarak DEĞİL.

~~Task 9'dan itibaren her plan görevi **tek parça değil, alt parçalar hâlinde** dispatch edilir.~~
Gerekçe ölçüldü: Plan 1'de görev başına ortanca ~6 commit'ti (20 görev / 137 commit); Plan 2'de
T5 = 21, T6 = 32, T7 = 36. Maliyeti büyüten şey görev başına düzeltme turu kuyruğudur ve her
tur tam test kümesini yeniden koşturur.

**Kıyas ölçüsü ÖNCEDEN sabitlendi** (sonradan uydurulmuş kıyas olmasın): bölünmüş dispatch'te
bir plan görevinin parçalarının commit'leri TOPLANIR (T9a + T9b = T9), yanına kaç hakem turu
koştuğu ve görevin baştan sona süresi yazılır. **Dürüst uyarı: bu kontrollü bir deney
DEĞİLDİR** — T9-T20 ile T5-T7 aynı zorlukta değil. Anlamlı sinyal: bir PARÇA 36 commit'lik bir
kuyruk üretmiyorsa bölme işe yaramıştır.

**KARAR AYNI GÜN GENİŞLETİLDİ — İNCELEMELER DE BÖLÜNÜR (2026-09-08, ölçülmüş kanıtla).**
Karar önce yalnız uygulama dispatch'i için yazılmıştı; aynı gün inceleme tarafında da ölçüldü:
- Tek parça checkpoint turu (42 commit, 6161 satır) **1200 sn tavanında zaman aşımına uğradı ve
  HİÇ RAPOR ÜRETMEDİ** — hakem 125 araç çağrısı yaptı, yazmaya vakit kalmadı.
- Aynı kapsam ikiye bölününce (A = üretim yüzeyleri, B = test tarafı) **A turu tam rapor verdi:
  beş yüksek bulgu**, dördü kontrolör ölçümüyle doğrulandı ve düzeltildi.
**Bağlanan kural:** bir inceleme turunun kapsamı tek pencerede rapor üretemeyecek kadar
büyükse tur AÇILMADAN bölünür; prompt'un başına "keşfi bütçele, raporu YAZ" talimatı ve
öncelik sırası konur. Bölme ekseni dosya türüdür (üretim yüzeyleri ↔ test tarafı), commit
aralığı değil — aralığı bölmek bulguyu iki turun arasına düşürür.

## Task 8 düzeltme turu (2026-09-08) — dört yüksek bulgu kapandı

Bağımsız hakem (A turu, taban `2b468e8d`) **beş yüksek** bulgu verdi. Kontrolör tahkimi:
**dördü ölçümle doğrulandı ve düzeltildi, biri ölçümde ÇÜRÜDÜ.**

- **F1 `a03207b`** — aktivasyon kanıtı İKİ yerde fail-open'dı: kontrol listesi imzası hiç
  karşılaştırılmıyordu (boş olmayan her dize geçiyordu) ve onay anlık görüntüsü YOKKEN "açık
  soru sayısı 0" yazılıyordu. Erişilebilirlik ÖLÇÜLDÜ: `activate_package` iki booleana da
  olduğu gibi güveniyor, jeton tüketimi yok; kodun "sonraki görevin kapısı reddeder" gerekçesi
  Task 15'e aitti ve o kapı YOK. **Kapanış import kenarını AÇMADAN yapıldı** — beklenen imza
  yalnız-anahtar parametreyle çağırandan gelir, kaynağın kapalılığını bir AST kapısı ölçer.
- **F2 `f6c37bb`** — geri alma hatası kaydı kilit bırakıldıktan SONRA yazılıyordu; o pencerede
  satır silinebiliyor, güncelleme sıfır satır etkileyip sessizce geçiyordu. Deneme artık iç
  kayıt noktasında koşuyor, hata durumu kilit altındayken yazılıyor ve bir satır etkilendiği
  dönen değerle kanıtlanıyor.
- **F3 `797bd0c`** — `record_result` son-yazan-kazanırdı; tamamlanmış bir koşunun bütün motor
  alanları sonradan ezilebiliyordu. Karşılaştır-ve-yaz oldu.
- **F4 `e5225a4`** — kanıt üreticileri sözleşmelerinin gerektirdiği işlemi denetlemiyordu;
  otomatik-commit altında kilitler anında düşüyordu. Giriş kapısı eklendi (fail-closed).
- **F5 REDDEDİLDİ — kabul edilmiş risk, bağlayıcı koşuluyla.** Hakem, migration'ın yerinde
  düzenlenmesinin "onu zaten uygulamış ortamları güncellenemez bıraktığını" söyledi. Mekanizma
  doğru, **öncül ölçümde çürüdü:** öyle bir ortam YOK — geliştirme veritabanında iki tablonun
  ikisi de yok (`to_regclass` → NULL), dal main'e merge edilmemiş, hiçbir yere dağıtılmamış.
  Hakemin önerisi (dosyayı geri al + çift kimlikli yeni migration) var olmayan bir soruna
  kalıcı karmaşıklık eklerdi. **Koşul: bu dal merge edilene kadar yerinde düzenleme serbest;
  merge sonrası her değişiklik yeni numaralı migration ister.**
- **`466d1d4`** — F1 bir imzayı genişletti, ekin örnek imzası ve iki çağrı örneği geride kaldı;
  üçü hizalandı ve revizyon kaydına **R-E** olarak yazıldı. Hüküm değişmedi, beklenen değerin
  nereden geldiği belirlendi.

**Uygulayıcının kendi yakaladığı ölçüm tuzağı (kayda değer):** F4'ün ilk kırmızı testi
kirliymiş — test altyapısı zaten her testi bir işlem içine sarıyor, dolayısıyla kapı orada
görünmüyor. Taslak atıldı, işlemsiz bağlantı kuran ayrı bir altyapı yazıldı, kırmızı kapının
iki satırı sökülerek kanıtlandı (4 düştü, 1 geçti — geçen, kontrol kolu).

- **Yedek etiket `backup/pre-footer-fix-20260830` süresiz durmaz.** Silinme koşulu: dal
  main'e merge edildiğinde VEYA final inceleme temiz geçtiğinde. O ana kadar commit etiketi
  yeniden yazımının geri dönüş yolu.

- **Ekin düzyazısı ile bağlayıcı SQL bloğu ÇELİŞİYORDU — ÇELİŞKİ ÇÖZÜLDÜ 2026-09-08
  (revizyon R-B); ARTIK KALAN dar bir açık ve evi Task 8.** Karar: **SQL bloğu bağlar
  (`BEFORE UPDATE`)** — uygulanmış `036_package_runs.sql` de öyle kuruyor (manifest satır
  122) ve salt-ekleme analojisi zaten yanlıştı (o desen HER `UPDATE`i reddeder, oysa
  `durum`/`onay_*`/`kanit_jetonu_*` yazılabilir kalmak zorunda). Düzyazının yanlış emsali ve
  yanlış satır alıntısı (032 "49-51" → gerçekte 187-188) düzeltildi.
  **Kalan açık — dürüst etiket: çözülmedi, evi var (Task 8).** `BEFORE UPDATE` yalnız
  UPDATE'i kapılar; onaylanmış bir satır veri katmanında hâlâ hard DELETE ile silinebilir.
  Ölçüldü (2026-09-08): `package_rollback_plans`a değen üretim Python yolu YOK ve 036'da
  DELETE/TRUNCATE tetikleyicisi yok — bugün erişilebilir bir kayıp yolu yok. Kararı Task 8
  verir (`amend_rollback_plan` çıkarmayı hard DELETE mi DURUM değişikliği mi yapacak);
  hard DELETE seçilirse tetikleyici AYNI turda `TG_OP` ayrımlı bir DELETE koluna genişler.
- **F7 düzeltmesi bağımsız hakem GÖRMEDİ (kabul edilmiş risk, 2026-09-06 Eray kararı).**
  Üçüncü Codex turu açılmadı. Kapısı adlandırıldı: sıradaki checkpoint tabanı `a6e053f`
  kaldığı için bu turun yedi commit'ini kendiliğinden kapsar.
- **Uygulayıcının ölçemediği dört kalem (F7 turu, "doğrulanmadı" etiketiyle):** (a) temiz
  şemaya yabancı nesne dikilip 036'nın ilk kez koşturulması AYRI bir hücre değil — altı kapı
  hücresi de zaten göçmüş bir veritabanına YENİDEN uygulama yoluyla koşuyor (üç tetikleyicinin
  ikisi için bu senaryo zaten erişilemez, tabloları 036'dan önce yok); (b) geri alma
  dosyasındaki fonksiyon kimliği gövde değil `md5(prosrc)` özeti — çakışma direnci VARSAYIM;
  (c) kapı `to_regprocedure('<ad>()')` bakıyor, aynı adı taşıyan FARKLI imzalı bir aşırı yükleme
  incelenmedi (gerekçe akıl yürütmedir, ölçüm değil); (d) bizim dokunmadığımız BAŞKA bir tabloda
  aynı adı taşıyan yabancı tetikleyici sınanmadı.


## Task 8 — kapanış-doğrulama ve test tarafı turları (2026-09-08, ikinci oturum)

Bir önceki oturum iki turu kotaya takıldığı için açık bırakmıştı; ikisi de bu oturumda koştu.

**Kapanış-doğrulama turu 2 (taban `a21d2c9`).** F2/F4/F5 ve F1'in imza bacağı KAPALI
doğrulandı; R-E doküman hizası doğrulandı. **F1'in ikinci bacağı AÇIK çıktı** ve öncülü
kontrolör tarafından ölçüldü: `acik_sorular` değerinin ŞEKLİ doğrulanmadan `len()`
çağrılıyordu, yani `""` ve `{}` "açık soru YOK" anlamına geliyor ve K-71 kapısını açıyordu.
**`79c3570`** kapalı ve NOMİNAL bir kabul kümesi koydu (`list`/`tuple`, boşlar dâhil;
`tuple` zorunlu çünkü `identity.donmus` kuralı (2) `list|tuple → tuple`), `Sized`/`Iterable`
gevşekliği YOK. Aynı turda süpürme AYNI sınıftan **dört örnek daha** buldu ve kapattı
(anlık görüntünün kendi `in` kapısı `str` ve `set` için geçiyordu; iki tasdik indekslemesi).
Sapma ekin bağlayıcı örnek koduna aykırı olduğu için revizyon kaydına **R-F** yazıldı
(**`f0371e9`**). **Kapanış-doğrulama turu 3 `approve` — bulgu YOK**; hakem kendi matrisini
kurup koştu (10 ret + iki meşru boş-küme kabulü).

**B turu — test yüzeyi (taban `3c41b24`), hiçbir hakemin görmediği yüzey.** Tam da aranan
sınıfı buldu: **tespit edemediği bir güvenceyi onaylayan test.** Üç yüksek + bir orta, dördü
de kontrolör tarafından dosya açılarak doğrulandı, dördü de Task 8'in KENDİ ürünü:
- **B1** — A1(b)'nin "ana ispatı" dört yoldan yalnız `amend_rollback_plan`'i deniyordu;
  `approve_incident_rollback` ve `build_rollback_evidence` KAPISIZDI.
- **B2** — "anahtar kümesi türetilir" iddiası testte SABİTLENMEMİŞTİ (elle yazılmış küme ile
  karşılaştırıyordu) ve hem testin hem `_yuk_anahtarlari`'nın docstring'i "kendiliğinden
  yediye çıkar" diye YANLIŞ beyan taşıyordu.
- **B3** — "istisna yutulmaz" testi `execute_rollback_plan`'i HİÇ çağırmıyordu.
- **B4 (orta)** — eksik-alan matrisinin aktivasyon yarısı, test edilen kapıya ulaşmadan
  argüman bağlamada düşüyordu.

**B4 park EDİLMEDİ.** Politika orta bulguyu advisory sayar ama o izin ÖNCEDEN VAR OLAN borç
içindir; bu gerileme görevin kendi ürünüydü ve düzeltmesi tek satırdı. Ayrıca diğer üçüyle
AYNI sınıftandı — üç örneği kapatıp dördüncüsünü etiketi düşük diye bırakmak sınıfı değil
varyantı kapatmak olurdu.

**Turun kapanış ölçütü MUTASYON KANITIYDI** (`ae06bb9`): testler koddan sonra yazıldığı için
"kırmızıyı gördüm" güvencesi yapısal olarak elde edilememişti; karşılığı, her yeni testin
koruduğu davranışı geçici bozup kırmızıyı ÖLÇMEKTİR. Kontrolör bunlardan ikisini BAĞIMSIZ
olarak tekrarladı (yürütücünün `except` kolu genişletildi → yeni test kırmızı, eski taksonomi
testi yeşil; yeni bir kilit çağrı yeri eklendi → kapı kırmızı).

**B5 — kontrolörün kendi inisiyatifi, ve DERSİ.** Kilit listesi hâlâ ELLE olduğu için
türetilmiş bir AST kapısı eklendi (`cc0a129`). Eray'a "ucuz, sınıfı kalıcı kapatır" diye
sunuldu; **kapatmadı.** Kapanış turu kapının kimliği fonksiyon ADINA indirgediğini (aynı
fonksiyona eklenen ikinci çağrı görünmez) ve korunan-yol değerlerinin çözülmeyen düz metin
olduğunu (adı geçen test silinse kapı yeşil kalır) buldu; kontrolör ikisini de ölçtü.
**Aynı eksenin ÜÇÜNCÜ turuydu** (el listesi → türetilmiş liste → türetmenin çözünürlüğü) ve
sistemik-sınıf kuralı gereği dördüncü nokta-düzeltmesi AÇILMADI. Çerçeve teşhisi: davranışsal
bir garanti muhasebe mekanizmasıyla kurulamaz — AST kapısı "bu kilit yük taşıyor mu" sorusunu
asla cevaplayamaz, yalnız "her kilit noktası beyan edilmiş mi" der; muhasebenin her zaman bir
deliği daha olur. **Eray'ın kararı: açıklamayı gerçeğe indir, kapıyı bırak** (`a488769`).
Kapı artık NE YAKALAR / NE YAKALAMAZ ayrımını adıyla taşıyor ve kapsama MUHASEBESİ tuttuğunu
söylüyor, kilidin yük taşıdığını kanıtladığını değil.

**`a488769` bağımsız hakem GÖRMEDİ — dürüst etiket, kabul edilmiş risk.** Bulgu "test
söylediğinden azını yapıyor"du, düzeltme tam olarak o cümleyi gerçeğe indirmek; bunun için
ayrı bir dış inceleme turu koşmak orantısızdı. Kontrolör metni kodla karşılaştırarak
doğruladı. Kapısı: sıradaki checkpoint tabanı `2b468e8d` KALDIĞI için bu commit'i
kendiliğinden kapsar.

**Kontrolörün KENDİ hatası, kayda geçiyor:** fix turu 2'nin brief'inde commit etiketi
`T8-fix2` diye yazdırıldı; o etiket 1. turda `f6c37bb`'de zaten kullanılmıştı. Defterde iki
farklı iş aynı adı taşıyor. Kapı `rc=0` veriyor, geçmiş değişmez — düzeltilemez, yalnız
kayda geçer. Sonraki turlar `T8-fixB`, `T8-fixB5`, `T8-fixB6` ile çakışmasız ilerledi.

**`last_checkpoint_ref` ve `cp_count` BİLEREK İLERLETİLMEDİ.** §8.6 mutasyon protokolü yalnız
Clean/Accepted-risk dallarında koşar; son bağımsız hakem verdict'i `needs-attention`'dı ve
onun blokeri (B5) bağımsız yeniden-doğrulama GÖRMEDEN kapatıldı. Fail-safe yön: taban
`2b468e8d` KALIR ve Task 7 + Task 8 + bütün düzeltmeleri kendiliğinden yeniden kapsar.
