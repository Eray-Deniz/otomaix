# Review (dual): kusur 3 — bayrak tüketimi kapısının yüzeyi — 2026-09-20

Review aralığı: `022d75d..1611d1f`
- BASE_REF: `HEAD~1` | BASE_SHA: `022d75d` | HEAD_SHA: `1611d1f` | REVIEW_BASE_SHA (merge-base): `022d75d`

Reviewers: fresh Claude subagent (general-purpose; `superpowers:code-reviewer` bu kurulumda
çözülemedi, persona aynı prompt'la kullanıldı) + Codex `adversarial-review`
dual-review: **true** (claude_status: ran · codex_status: ran)
Review workspace: pinned worktree @ HEAD_SHA (clean)
Main tree at review: clean (0 uncommitted — review dışı bırakılan iş YOK)
security_surface_touched: **uncertain → true** (fail-closed) — bu değişiklik paketin
aktivasyon kapısının anlamına dokunuyor; güvenlik-checklist eki KONMADI,
`/security-review-claude-codex` zorunlu kalır.

Requirement context (snapshot, iki hakeme BİREBİR aynı):
- `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (§8.4 · §8.5) — committed, YOLLA verildi
- `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` (Task 12/13/19) — committed, YOLLA verildi
- `hakem-sentez-gorevi.md` bayrak hükümleri — dış depo (`d907e05`), prompt'a BİREBİR gömüldü
- **Dürüst sapma:** spec 104 KB, plan 173 KB → tek argüman sınırını (131.072 bayt) aşıyor;
  gömülmedi, iki hakem de AYNI pinli committed dosyayı okudu.

## Critical
Yok.

## High
- **H1 — Tipli bayrak bilgisi tümden atıldı; bayrak başına kural hiçbir yerde doğrulanmıyor**
  `engine.py` `_yeni_oge_cogunlugu` / `_bayrak_tuketimi` · [both-agree] (Codex high ·
  subagent medium 2 — aynı eksen, severity en yüksekten alındı)
  **Premis kısmen ÇÜRÜTÜLDÜ (claude-confirmed ölçüm):** Codex "marka-adı bayraklı içerik
  aktive edilebilir" dedi; `sector_packages._check_banned_brand_names` GERÇEK marka adlarını
  DB'den çekip paket içeriğinde arıyor ve `synthesis.py:993` turu düşürüyor — işaret arayan bir
  kontrolden güçlü. Ayakta kalan ayak: kaldırılan blok operatöre bilgi veriyordu, artık
  vermiyordu; subagent ölçtü ki `AuditRow.bayraklar`'ı okuyan üretim kodu KALMAMIŞ, yani
  dürüst etiketin yeniden-açılma koşulu TETİKLEYİCİSİZ.
  **Disposition: fixed** — BLOKLAMAYAN `bayrak_kaydi` bulgu sınıfı (`ETKI_KAYIT`).
- **H2 — Motorun REDDETTİĞİ kalemin metni koşuyu bloklıyor**
  `engine.py` `_bayrak_tuketimi` · [single-source: codex] · **claude-confirmed**
  Ölçtüm: kaynak sayısı yetersiz → karar `cogunluk-yok` ile düşüyor, öğe nihai içerikte YOK,
  ama kapı `acik_soru` üretip koşuyu blokluyor. Kapatılan kilit sınıfı yeni bir yoldan geri
  gelmişti. **Disposition: fixed** — `decide` (uygulama katmanı) bulgunun sınıfını `bayrak_kaydi`'na
  düşürür; bulgu sessizce DÜŞMEZ, bloklama etkisi düşer.

## Medium
- **M1 — Ölü satırın aktif yolu, sıra kayması yüzünden adaydaki yaşayan yolla çakışıyor**
  `engine.py` `_bayrak_tuketimi` · [single-source: claude] · **claude-confirmed** (kendi
  fixture'ımda üretim şekliyle yeniden üretildi: 1 yerine 2 bulgu, biri ÇIKARILAN birime atıf)
  **Disposition: fixed** — ölü satırlar (`cikar`/`kirp`) taranmaz; `identity.YASAYAN_KARARLAR` süzgeci.
- **M2 — Kanal bayrağı muafiyeti, yazım kapısının ve basım filtresinin kapsamından GENİŞ**
  `engine.py` `_bayrak_tuketimi` · [both-agree] · **claude-confirmed** (gerçek `render_package_block`
  çıktısında `[kanal-bagimli: whatsapp_hatti]` kanca satırında AYNEN basıldı; aynı çıktıda CTA
  kalıbı filtreye takılıp elendi)
  **Disposition: fixed — Eray kararı 2026-09-20: DARALT.** Muafiyet artık yalnız çalışma zamanı
  filtresinin koştuğu yüzeylerde (`cta_kaliplari` · `ozel_gun[*].cta`); yüklem doktrinin evine
  eklendi (`sector_content_schema.channel_flag_scope_path`), ikinci kapsam ifadesi yazılmadı.
  Gerçek koşudaki faturası ÖLÇÜLDÜ: 7 kanal etiketinin 6'sı CTA'da, 1'i (`gorsel_kodlar`) değil
  → tam 1 açık soru.
- **M3 — Pinlenen ölçüm sayıları deponun kaydıyla uzlaşmıyor, yanında üreten komut yok (İlke 9)**
  `engine.py` · `tests/` docstring'leri · [single-source: claude] · **claude-confirmed**
  **Disposition: fixed** — çıplak sayılar koddan ÇIKARILDI; uzlaştırma tablosu (hangi sayı hangi
  motor sürümünde), yüzey tanımları ve üreten komutun bağlayıcı tarifi
  `K134-MOTOR-KARSILASTIRMA.md` → "Bayrak kapılarının iki ölçümü" bölümüne yazıldı.

## Low
- **L1 — Bayat fixture yorumu ("motor artık tipli sütundan okur"; o okuyucu silinmişti)** →
  **fixed**.
- **L2 — Komşu YAZIM NOTU'nun iddiası ölçümle yanlış** ("`_katla` noktasız `ı`'yı katlamaz →
  `[marka-adı]` tanınmaz"). ÖLÇTÜM: kapalı kümenin SEKİZ üyesi sözleşmenin Türkçe yazımıyla
  **8/8 tanınıyor**. → **fixed** (üretilmiş matris testine atıf düzeltilmiş adla verildi).
- **L3 — Docstring garantiyi yanlış kontrole atfediyor** (`karar_kapsami` ≠ kapsama eşitliği;
  gerçek kapı `identity.check_unit_integrity` + `_sema_ve_boyut`) → **fixed** (İlke 1).
- **L4 — `cikar` kolunun testi yok** → **fixed** ama BAŞKA biçimde: yazdığım ilk test VAKUMDU
  (çıkarılan öğenin metni AKTİF paketten gelir, oraya bayrak konamıyor → test tespit edemediği
  bir garantiyi onaylıyordu) → SİLDİM; kolun gerçek oracle'ı M1'in çakışma testidir.

## Disposition Ledger
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| H1 | codex + claude | high / medium | high | **fixed** | premis kısmen çürütüldü (marka adı kapısı VAR); kalan ayak `bayrak_kaydi` ile kapandı |
| H2 | codex | high | high | **fixed** | claude-confirmed; `decide` sınıf düşürmesi |
| M1 | claude | medium | medium | **fixed** | claude-confirmed; ölü satır süzgeci |
| M2 | codex + claude | medium | medium | **fixed** | Eray kararı: daralt |
| M3 | claude | medium | medium | **fixed** | sayılar koddan çıktı, uzlaştırma kayda geçti |
| L1–L4 | claude | low | low | **fixed** | dördü de düzeltildi (L4 biçim değiştirerek) |
| — | codex | high (H1 alt-ayağı) | — | **rejected** | "marka adı bayraklı içerik serbest kalır": `_check_banned_brand_names` ölçümle çürüttü |

**Politika notu:** medium/low bu komutta `accepted_risk` olabilirdi; hepsi DÜZELTİLDİ çünkü
biri hariç hepsi bu oturumun KENDİ gerilemesiydi (M2'nin muafiyet genişliği önceden vardı, ama
onu kodlaştıran ve testle meşru gösteren commit bu commit'ti).

## Sonuç
- Kapatılan (push-back ile): 0 · **Premis çürütmesiyle reddedilen: 1** (Codex H1 alt-ayağı)
- Açık (devam): 0 · Hakemler-arası çelişki: yok (aynı eksenlerde farklı severity — en yüksek alındı)
- Unresolved critical/high: **yok** (ikisi de fixed; `fixed_confirmed` kapanış-doğrulama turuna bağlı)

## Doğrulama (taze çıktı)
| Ne | Sonuç |
|---|---|
| Tam takım (düzeltmelerden SONRA) | **4625 passed / 0 failed**, 337,31 s |
| Test sayısı | 4619 → 4625 (+6 yeni; aritmetik tutuyor) |
| Motor sürümü | 2.18.0 → **2.19.0** (parmak izi değişikliği YAKALADI — damga kapıyla arttı) |
| Mutasyon (4 kapı) | 4/4 yakalandı, doğru testlerle; hepsi yedekten bayt-eşit geri alındı |
| Gerçek koşu (yeni motor) | 3 `bayrak_kaydi` (bloklamıyor) + 1 `acik_soru` (öngörülen `gorsel_kodlar`) + 1 `regresyon_kapisi` (kusur 4) |

**Alt-hakem takımı bağımsız koşturdu:** 4619 passed / 332,44 s (düzeltmelerden ÖNCEKİ hâl) —
benim o anki sayımı doğruladı.

## Kapsanmayan / denenmeyen
- `yazim` · `katman1/2` · `onay` · `aktive-et` ayakları bu turda da KOŞMADI.
- Yeni kapının `koru` kolu: aktif paketi OLAN bir sektörde davranış **doğrulanmadı** (pilot
  sektörün aktif paketi yok).
- Bayrak başına kuralın ANLAM ayağı (ör. "kopya şüphesi soyutlanarak giderildi mi") mekanik
  DEĞİLDİR ve olmayacak; `bayrak_kaydi` onun yerine geçmez, operatör denetimine dayanak olur.
- `eski-kaynak` bayrağının çoğunluk eşiği kuralı HÂLÂ hiçbir yerde uygulanmıyor (bu koşudaki
  parası ölçüldü: sıfır). Yeniden açılma koşulu: bir kararın çoğunluğu YALNIZ `eski-kaynak`
  bayraklı atıfa dayandığı ilk vaka.
- Exhaustiveness iddiası YOK.

## Ham kanıt — işaretçiler (bu makinede, bu kökten)
- Codex ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-20-review-feat-sektor-bilgi-paketi-plan2-1.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-20-review-feat-sektor-bilgi-paketi-plan2-1.claude.md`
- **Dürüst etiket:** işaretçiler MUTLAK yoldur, ham kanıt proje klonuyla TAŞINMAZ (K4 kabul
  edilen risk). Alt-hakemin `.claude.md` dosyası onun KENDİ raporudur; ana Claude'un sentezi
  ve disposition'ı bu dosyadır.

---

# Attempt 2 — kapanış-doğrulama (aynı pinli sözleşme, sınırlı etki zarfı)

Aralık: `022d75d..81d5ed6` · workspace: pinned worktree @ `81d5ed6` (clean)
dual-review: **true** (Codex `adversarial-review` + taze Claude alt-hakemi, ikisi de KOŞTU)
Contract-widening istenmedi; zarf dışı yeni C/H sinyali YOK.

## Adlandırılmış bulguların kapanış yargısı

| # | Codex | Claude alt-hakemi | Sonuç |
|---|---|---|---|
| H1 | kapandı | kapandı (kapsamı dar → low) | **kapandı**, kapsam sınırı etiketlendi |
| H2 | "adlandırılmış vaka kapandı, ama genelleştirme YENİ high açtı" | kapandı; maskeleme riskini ölçtü, bulgu çıkmadı | **yeni high → düzeltildi** (aşağıda) |
| M1 · M2 · M3 · L1–L4 | kapandı | kapandı | **kapandı** |

**Geriledi: hiçbiri.** İki hakem de bunu ayrı ayrı ölçtü (mutasyonla).

## YENİ high (attempt-2'nin ürünü) — ve kapanışı

**[H3 — high, single-source: codex, claude-confirmed] Reddedilen `guncelle` AKTİF değeri geri
yükler; 2.19.0'ın düzeltmesi FAIL-OPEN açmıştı.** Sınıf düşürmesi "birim ret kümesinde mi" diye
bakıyordu; oysa yalnız reddedilen bir `ekle` pakete girmemeyi GARANTİ eder. Kendi ölçümüm
(Codex'in iddiasını olduğu gibi almadım):

```
SONUC             : activation_eligible   sebep=None
NİHAİ kanca_kaliplari: ('Eski aktif kanca [kopya-şüphesi]', ...)
>>> BLOKLANDI MI: HAYIR — fail-open
```

Yani paket yasak bir bayrakla aktive edilebiliyordu. Önceki hâl fazla bulgu üretiyordu; bu
düzeltme SESSİZ kalıyordu — daha kötü yön.

**Disposition: fixed — VARYANT DEĞİL SINIF kapatıldı.** Bu eksen üç turda üç varyantla açıldı
(düz yazı → aday → ret kümesi). Yamamak bırakıldı: doğru yüklem "karar reddedildi mi" DEĞİL,
"pakete girecek nihai metin kirli mi". Kural TEK fonksiyonda (`bayrak_ihlalleri`) ve İKİ yerde
koşuyor — kontrol adayı ölçer, `decide` nihai içeriği yargılar. Adayda görünmemiş bir ihlal
(geri yüklenen aktif değer) `decide`'da YENİ bulgu olarak doğar.

**Kapanış kanıtı ÜRETİLMİŞ MATRİS** (`test_blocking_matches_the_final_package_text_exactly`):
aktif metin (bayraklı/temiz) × aday metin (bayraklı/temiz) × karar (uygulandı/reddedildi) = 8
vakanın TAM ÇARPIMI, çift yönlü iddia ("bloklar ⟺ nihai metin kirli"), oracle ELLE yazılı.
İki mutasyonla dişi sınandı: fail-open geri konunca tam o vaka kırmızı; düşürme tümden
kaldırılınca ters yöndeki vaka kırmızı.

## Attempt-2'nin öteki bulguları

- **[medium — claude] `/cta` kolu ÖLÇÜLMÜYOR; mutasyon SAĞ KALDI.** Hakem
  `channel_flag_scope_path`'in `or unit_path.endswith("/cta")` kolunu sildi ve 639 test yeşil
  kaldı. **Disposition: fixed** — kol için test yazıldı.
  **Kapatırken KENDİ testimde daha kötü bir kusur buldum:** ilk yazımın süzgeci
  `"bayrak" in b.detay` idi ve kanal mesajı **"bayrağı"** yazıyor (ğ ≠ k) → süzgeç onu HİÇ
  görmüyordu. Yani test tespit edemediği bir garantiyi onaylıyordu; mutasyon düzeltmeden SONRA
  da sağ kaldı. Üç süzgeç yapısal ölçüte (`b.kontrol == "bayrak_tuketimi"`) çevrildi; mutasyon
  ancak ondan sonra yakalandı.
- **[low — claude] `_bayrak_tuketimi`'nin ilan ettiği yüzey taradığından geniş; reddedilen
  `cikar` aktif birimi geri koyuyor ve taranmıyor.** **ÖLÇÜMLE GEÇERSİZ:** hakem `81d5ed6`'yı
  inceledi; yargı nihai içeriğe taşındıktan sonra bu kol KAPANDI — kendi probum `blocked` +
  `acik-soru-var` veriyor ve nihai içerikte bayraklı birim görülüyor. Yine de kola test yazıldı
  (`test_a_rejected_removal_that_restores_a_flagged_item_blocks`).
- **[low ×4 — claude] fixed:** modül başlığı "ALTI bulgu sınıfı" → yedi · `bayrak_kaydi`'nın
  test anlatımında "NOT" denmesi (o küme pinli dış sözleşmeyle çivili, üretilen şey BULGU) ·
  2.19.0 damga notunun "parmak izi YAKALAR" iddiası (üç değişiklikten yalnız biri yakalanıyor) ·
  `channel_flag_scope_path(_metin(yol))` nit'i.
- **[low — claude] H1 tetikleyicisinin KAPSAMI:** kayıt yalnız `ekle` yolunda ve altı kapıyı
  geçen kararlar için doğar. **Disposition: fixed (etiketleme)** — kodda iki ayaklı dürüst etiket
  + yeniden açılma koşulu.
- **[low pre-existing — claude] "`acik_soru` sınıfını BEŞ ayrı kontrol üretir" yanlış.**
  Kendi ölçümüm: `sinif="acik_soru"` beş fonksiyonda geçiyor ama biri kontrol DEĞİL, o sınıfı
  OKUYAN süzgeç (`_acik_soru_kimlikleri`) → üreten **dört** kontrol. İki sitede düzeltildi.

## Hakemlerin ölçüp BULGU ÇIKARMADIĞI riskler (kayda geçer)

- Bloklamayan sınıfı yanlış işleyen tüketici **YOK** — depo geneli tarandı: `decide` açık
  `ETKI_KAYIT` kolu · `readiness.BLOKLAYAN_BULGU_SINIFLARI` etkiden TÜREİYOR · `_acik_soru_kimlikleri`
  sınıf bazlı süzüyor · `approval._bulgu_ayrimi` sınıfı `uyarilar`'a taşıyor ve operatör özetinde
  **basıyor** (yani "onay yüzeyine taşır" iddiası DOĞRULANDI) · migration'larda sınıf sayan
  CHECK/enum yok.
- Sınıf düşürmesinin bloklaması gerekeni maskeleme yolu ölçüldü; tek şüpheli yol
  (`_eylem`'in `birim is None` kolu) `_karar_kapsami` tarafından `kapsam_ihlali` ile zaten
  bloklanıyor.
- Codex'in attempt-1'de reddedilen ayağının reddi DOĞRULANDI (marka adı kapısı motordan önce,
  fail-closed).

## Doğrulama (taze çıktı, düzeltmelerden SONRA)

| Ne | Sonuç |
|---|---|
| Tam takım (TEMİZ koşum) | **4635 passed / 0 failed**, 334,21 s |
| Test sayısı | 4625 → 4635 (+10: 8 matris vakası + 2 test; aritmetik tutuyor) |
| Motor sürümü | 2.19.0 → **2.20.0** (parmak izi bunu YAKALAMAZ — dürüst etiket damganın yanında) |
| Matris | 8/8, çift yönlü, iki mutasyonla sınandı |
| `/cta` kolu mutasyonu | süzgeç düzeltildikten SONRA yakalanıyor |

**TAM TAKIM SAPMASI — dürüst etiket ve çözümü.** Hem alt-hakem hem ben, düzeltme turu sırasında
temiz tam koşum ÜRETEMEDİK (46/20 · 58/51 · 39/22 hata). Düşen kümenin TAMAMI DB/migration
altyapısıydı, zarf modüllerinde sıfır düşüş, küme koşumlar arası DEĞİŞİYOR ve izole koşumda
geçiyor. **Sebep alt-hakem bitince ölçüldü:** `otomaix_test_scratch` scratch veritabanını iki
koşum birlikte kurup düşürüyor. Alt-hakem "kesinlikle çevresel demiyorum, tabanda kontrol
koşumu yapmadım" diye dürüstçe sınırladı; **kontrol koşumu SONRADAN yapıldı ve temiz geldi
(4635/0)** — atıf artık ölçülmüş.

## Stop-rule durumu — kullanıcı checkpoint'i

- `completed_evaluations` = **2** (attempt-1 dual, attempt-2 dual) · `consecutive_degraded` = 0 ·
  `total_invocations` = 2 → terminal backstop (6) DOLMADI.
- Unresolved critical/high: **yok.**
- **AMA:** attempt-2'nin açtığı high'ın (H3) düzeltmesi **attempt-2'den SONRA** yapıldı, yani
  **bağımsız hakem onu görmedi.** Stop-rule "attempt-2 sonrası otomatik 3. pas YOK → human
  checkpoint" diyor; bu yüzden üçüncü tur KENDİLİĞİNDEN koşulmadı. Kapanış kanıtı şu an
  **kontrolörün üretilmiş matrisi**, hakem `approve`'u DEĞİL — dürüst etiket.

---

# Attempt 3 — kapanış-doğrulama, CODEX-ONLY (Eray kararı 2026-09-20)

Aralık: `81d5ed6..4865a45` (attempt-2'nin açtığı high'ın düzeltmesi) · workspace: pinned
worktree @ `4865a45` (clean)
**dual-review: FALSE · review_confidence: reduced · single-source: codex.**
Bu tek-hakem KASITLIDIR: Eray "sadece Codex ile üçüncü turu koş" dedi. Gerekçe ölçüme dayanıyordu
— attempt-1/2'de fail-open'ı Codex, matrisin kör noktasını Claude alt-hakemi bulmuştu; bu tur DAR
bir soru sınıyor ve Codex turu ~9 dk, alt-hakem turu 21-31 dk sürüyor. **Damga dürüstlük gereği
düşürülür:** tek hakem, azaltılmış güven.

## Verdict: **approve — materyal bulgu YOK**

Codex'in doğruladıkları (kendi cümleleriyle özetlenmiş, ham çıktı log'da):
- **H3 KAPANDI.** Nihai içerikte kirli metin HER ZAMAN damgalı bir `bayrak_tuketimi` açık sorusu
  üretiyor; nihai pakette OLMAYAN reddedilmiş içerik yalnız kayıt üretiyor.
- **Kalıcılık aynı doğrulanmış nihai içeriği yazıyor** — yani `nihai` ile yazılan ayrışmıyor
  (sorduğum (a) maddesi).
- **M4 (süzgeç):** iddialar kontrolü artık YAPISAL olarak tanıyor.
- **M5 (matris):** iddia edilen 2×2×2 çarpımı gerçekten kapsıyor, oracle BAĞIMSIZ, ve pytest'in
  `monkeypatch` fixture'ı vakalar arası state sızıntısını engelliyor.
- Zarf dışı yeniden-keşif yapılmadı, contract-widening istenmedi.

**Codex'in taze ölçümü:** iki motor takımı **392/392 passed**. Komşu bir grup 317 passed + 272
setup error verdi çünkü `DATABASE_URL` sandbox'ta yok — **asserted failure DEĞİL**. Bu, benim
ölçümümle tutarlı (aynı sebep: DB erişimi).

## Stop-rule durumu — CHECKPOINT KAPANDI

- `completed_evaluations` = **3** (attempt-1 dual · attempt-2 dual · attempt-3 single) ·
  `consecutive_degraded` = 0 · `total_invocations` = 3 → terminal backstop (6) DOLMADI.
- Unresolved critical/high: **yok.**
- **H3'ün kapanışı artık bağımsız hakem teyidi taşıyor** (`fixed_confirmed`), yalnız kontrolörün
  matrisi değil. Dürüst sınır: teyit TEK hakemden geldi (`dual-review: false`).
- **`risk_acceptance` / `dual_review_override` event'i YAZILMADI** — unresolved C/H yok, ve
  tek-hakem seçimi zincir-ilerlemesini geçmek için değil KAPANIŞI DOĞRULAMAK için yapıldı.
  Zincirin sonraki adımı (`/security-review-claude-codex`) hâlâ koşmadı ve
  `security_surface_touched: true` olduğu için ZORUNLU kalıyor.

## Bu review zincirinin toplam maliyeti (ölçüldü)

| Tur | Hakemler | Süre |
|---|---|---|
| attempt-1 | Codex + Claude alt-hakemi | Codex ~4 dk · alt-hakem 21 dk |
| attempt-2 | Codex + Claude alt-hakemi | Codex ~6 dk · alt-hakem 31 dk |
| attempt-3 | yalnız Codex | ~7 dk |
| Tam takım koşumları | 4 temiz koşum | 335 + 337 + 334 s (+ çakışma yüzünden boşa giden 3 koşum) |

## Prosedürel kapanış (overclaim YASAK)

Tanımlı pas bütçesi tamamlandı (3 attempt; `total_invocations=3`, `consecutive_degraded=0);
adlandırılmış closure kontrolleri çalıştı; ledger: `task:sektor-bilgi-paketi-plan2`
(`completed_evaluations=3`). **Kapsanan alanlar:** bayrak tüketimi kapısının yüzeyi ve dayanağı ·
kanal bayrağı muafiyetinin kapsamı · ölü satır/sıra kayması · bloklamayan bulgu sınıfının tüm
tüketicileri · nihai içerik ↔ kalıcılık bağı · testlerin gözlem gücü (süzgeç sınıfı).
**Denenmeyen/kapsanmayan alanlar:** `yazim` · `katman1/2` · `onay` · `aktive-et` uçtan-uca
ayakları · aktif paketi OLAN sektörde `koru` kolu · bayrak başına kuralın anlam ayağı ·
`eski-kaynak` çoğunluk kuralı · attempt-3'te ikinci hakem. **Residual'lar:** dördü TASK.md'de
koşullu kalemler olarak adlandırıldı. **Exhaustiveness iddiası YOK.**
