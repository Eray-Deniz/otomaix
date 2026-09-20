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
