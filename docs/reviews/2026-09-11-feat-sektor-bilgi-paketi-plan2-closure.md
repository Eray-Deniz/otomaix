# Closure review (attempt 2, dual): düzeltme turunun kapanışı — 2026-09-11

Review aralığı: `080aa7f..2188e06` (düzeltme diff'i)
Reviewers: fresh Claude subagent + Codex `adversarial-review`
dual-review: **true** (claude_status: ran; codex_status: ran — rc=0, 49 komut koşumu, kararla kapandı)
Review workspace: pinli worktree @ `2188e06` (temiz)
Attempt-1 raporu: `docs/reviews/2026-09-11-feat-sektor-bilgi-paketi-plan2.md`

**Sözleşme aynılığı — DÜRÜST ETİKET.** Attempt-1'de kalıcı bir review-defteri (ledger locator)
OLUŞTURULMADI, dolayısıyla bu tur pinli sözleşmeyi **hash karşılaştırmasıyla doğrulamadı.**
Aynılık KURULUM GEREĞİDİR: aynı komut · aynı mercek (`code-review`) · aynı severity rubriği ·
aynı disposition politikası (C/H fix-required) · aynı kapanış şablonu · aynı kapsam kuralı.
Bu bir ölçüm DEĞİL, bir beyandır — sonraki turlarda defter kurulmalıdır.

**Dış sözleşme snapshot'ı** yine pin (`12beec1`) ile sha256 byte-eşit doğrulandı (her iki hakem de
bağımsız ölçtü).

**Contract-widening TALEP EDİLMEDİ.** İki hakem de zarf dışında mercek genişletmeyi gerektiren
critical/high sinyali görmediğini ayrıca beyan etti.

---

## 1. Adlandırılmış on bulgunun kapanış durumu

| # | sev | Claude | Codex | SENTEZ |
|---|-----|--------|-------|--------|
| **F1** | critical | kapandı (davranış) + günlük ayağı borç | closed (inverted-blocking) · K-03 logging unsatisfied | **KAPANDI (davranış); günlük ayağı AÇIK BORÇ** |
| **F2** | high | kapandı | closed | **KAPANDI** |
| **F3** | high | kısmen; yeni yanlış teşhis sınıfı | still-open; diagnosis over-broad | **AÇIK** (beyan edilmiş borç) + yeni orta bulgu |
| **F4** | high | kapatılmadı; beyan dürüst ama kardeş siteler bayat | still-open; declaration not adequately lodged | **AÇIK** (beyan edilmiş borç) + yerleştirme eksik |
| **F5** | high | kapandı, aşırı-sıkı DEĞİL | closed | **KAPANDI** |
| **F6** | medium | kapandı (R5 ekseni) ama F1 ekseninde yeni çelişki | closed | **KAPANDI** + yeni orta bulgu |
| **F7** | medium | kapandı | closed | **KAPANDI** |
| **F8** | low | kapandı | closed | **KAPANDI** |
| **F9** | low | kapandı | closed | **KAPANDI** |
| **F10** | low | kapandı | closed | **KAPANDI** |

**Hiçbir bulgu GERİLEMEDİ.** Yedi bulgu tam kapandı; F1 davranış ayağıyla kapandı; F3 ve F4 zaten
sözleşme borcu olarak beyan edilmişti ve öyle kaldı.

**F5 aşırı-sıkı DEĞİL — ölçüldü.** Alt-hakem denetçi sözleşmesinin kendi cümlesini gösterdi:
*"Denetime giren HER kaynak için TEK satır"*. Kural motorun icadı değil, sözleşmenin kendisi.

**F2 meşru çoğunluğu kapatmıyor — ölçüldü.** Alt-hakem üç ayrı meşru şekli koşturdu (tek satır/iki
kaynak/iki iddia · tek satır/iki kaynak/tek iddia · **iki ayrı satır, satır başına tek kaynak, iki
iddia**); üçü de geçiyor.

---

## 2. Bu turun YENİ bulguları (hepsi etki zarfı İÇİNDE)

### N1 — `ENGINE_VERSION` kural değişirken sabit kaldı `[single-source: codex → kontrolör DOĞRULADI]`

`ENGINE_VERSION` kendi belgesinde *"uygulama kuralı değiştiğinde ARTAR: eski koşuların sonucu
yenisiyle karşılaştırılamaz"* der. **KONTROLÖR ÖLÇÜMÜ:** iki commit boyunca yetkilendirme iddia
düzeyine taşındı · K-126 istisnası kapalıdan açığa geçti · K-03 kategori ayağı çalışmaya başladı ·
uygulanmama sebepleri yediden on bire çıktı — damga `2.13.0` kaldı ve her sonuca `kural_surumu`
olarak yazıldı.

Severity: Codex `high`. Alt-hakem bulmadı → tek kaynaklı; **ama kontrolörün kendi ölçümü doğruladı**
(claude-confirmed) → fix-required.

**KAPANDI:** `2.14.0` + damgayı KURAL YÜZEYİNE bağlayan test (sebep kümesi boyu · kural kimlikleri ·
bulgu etkileri · kontrol adları). Tautolojik bir sürüm testi değil: yüzey değişip damga değişmezse
de, damga değişip yüzey değişmezse de DÜŞER.

### N2 — K-03 çatışması hiçbir operatör yüzeyine ULAŞMIYOR `[HAKEMLER AYRIŞTI]`

**Ortak ölçüm (iki hakem + kontrolör, üçü de aynı sonucu buldu):** çatışma `engine_diff
["kategori_cakismalari"]`'ya yazılıyor ve koşu satırında kalıcılaşıyor; **ama onu adıyla okuyan hiçbir
tüketici yok** — onay anlık görüntüsü yalnız sürüm/ayar/bariyer taşıyor, CLI koşu kimliği ve sonucu
basıyor, hazırlık kontrolü diff'in boş olup olmadığına bakıyor.

**AYRIŞMA — sessizce çözülmedi, kullanıcıya taşınır:**
- **Codex: `high` bulgu.** *"Operatör çatışmayı görmeden onaylayabilir; spec §11.2 hâlâ onu karar
  günlüğünde istiyor. Yeni test yalnız üretici tarafındaki sözlük girdisini kontrol ediyor ve bu
  aşağı akış kaybını MASKELİYOR."*
- **Alt-hakem: bulgu DEĞİL.** *"Ek ve kod docstring'i bunu dürüst etiketliyor; o yüzden bulgu değil —
  ama 'kim okuyor' sorusunun ölçülmüş cevabı budur: bugün kimse."*

**Kontrolörün değerlendirmesi:** ikisi de kendi çerçevesinde tutarlı. Beyan GERÇEKTEN var (günlük
ayağı açık borç diye yazılı); beyan edilMEYEN şey **sonucudur** — "ölçüm olarak taşınır" cümlesi,
okuyan birinin olduğunu ima eder. Bu yüzden Codex'in işaret ettiği boşluk gerçektir.

**Severity KORUNDU (`high`).** Otonom indirme YAPILMADI: politika raw C/H'ın indirilmesini gated
`severity_downgrade` kararına bağlar. **Kullanıcı kararına taşındı** — bkz. §4.

### N3 — `donem-kimligi-cozulemedi` AŞIRI GENİŞTİ `[both-agree]`

`anahtar not in takvim_anahtarlari` yüklemi *"dönem adı mı"* sorusunu değil *"takvimde var mı"*
sorusunu cevaplıyor. **Alt-hakem ölçümü (eski gövdeyi kopyalayıp aynı girdiyle koştu):**

```
'cta_kaliplari'  ESKİ=['iddia-arastirmada-yok']  YENİ=['donem-kimligi-cozulemedi']   ← gerileme
'zzz alakasiz'   ESKİ=['iddia-arastirmada-yok']  YENİ=['donem-kimligi-cozulemedi']   ← gerileme
'14 Şubat'       ESKİ=['iddia-arastirmada-yok']  YENİ=['donem-kimligi-cozulemedi']   ← doğru
```

`cta_kaliplari` bir dönem adı değil, BAŞKA BİR ALAN — tam da iki uçlu bağın yakalamak için kurulduğu
sentez sapması. Operatör onu bilinen sözleşme borcu sanıp araştırmayı bırakırdı.

**KAPANDI:** bilinen Bölüm A alan adı artık dönem teşhisi ALMAZ (`_TEMEL_ALAN_ANAHTARLARI`); pozitif
kontrol kolu gerçek dönem adının hâlâ dönem teşhisi aldığını ölçüyor.

### N4 — F4 borcunun beyanı KARDEŞ SİTELERE süpürülmedi `[both-agree]`

Ek'in yeni revizyon bloğu dürüsttü ama **aynı iddiayı yapan iki yer değişmemişti**: modülün
"ÖLÇÜLEMEYEN üç kalem" listesi (K-126'nın iki ayağının da ölçüldüğünü söylüyordu) ve ek'in R-H6
satırı. Codex ayrıca: *"'aynı kapanış turu' bir DOĞRULAMA YERİDİR, adlandırılmış bir iş kalemi
değil; aktif katmanda bu borcun kaydı yok."*

**KAPANDI (metin ayağı):** iki kardeş site de daralmayı artık yazıyor + `CHECKS` açıklamasındaki iki
bayat cümle (`K-126 istisnası dar ve kapalı`, `kategori ayağı girdide YOK`) düzeltildi.
**AÇIK (yerleştirme ayağı):** aktif katman kaydı — bkz. §4.

### N5 — Bağlayıcı ek F1 ekseninde KENDİ İÇİNDE çelişiyordu `[single-source: claude]`

Ek `binding-addendum`'dur ve çelişkide o geçerlidir; iki yeri hâlâ kaldırılan notu bağlıyordu
(R-H8 satırı ve K-03 bölümünün gövdesi: *"not ÜRETİLİR ve …"*). F6 "R5 alan kümesi" ekseninde
kapanmıştı; aynı belge aynı commit'te F1 ekseninde aynı kusuru yeniden üretti.

**KAPANDI:** iki yer de düzeltildi, düzeltme gerekçesiyle birlikte yazıldı.

### N6 — Ek'in sebep kümesi bloğu ve frontmatter'ı BAYAT `[single-source: claude]`

Blok *"KAPALI — YEDİ değer"* diyordu, kod on bir taşıyor; R-H5 satırı *"üç yeni sebep"* diyordu,
dördüncüsü eklendi; frontmatter `revised: 2026-09-08` / `revisions: 6` derken dosyada dört revizyon
bloğu ve en yenisi 2026-09-11.

**KAPANDI:** blok on bir değere güncellendi (bayatlığın kendisi not düşüldü), R-H5 satırı düzeltildi,
frontmatter `2026-09-11` / `9`.

### N7 — `CHECKS` açıklaması K-03 kapısı hakkında tersini söylüyordu `[single-source: claude]`

`"kategori ayağı girdide YOK"` — oysa modül ve fonksiyon docstring'i artık olduğunu söylüyor.
`080aa7f`'ten devrediyordu. **KAPANDI.**

---

## 3. Disposition Ledger — attempt 2

| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| N1 | codex | high | high | **fixed** | kontrolör doğruladı; `2.14.0` + kural-yüzeyi testi |
| N2 | codex | high | high | **needs_human** | alt-hakem bulgu saymadı; severity KORUNDU, karar kullanıcıya |
| N2' | claude | — (bulgu değil) | — | measured-not-a-finding | ölçüm aynı, yargı farklı — ayrışma §2'de açık |
| N3 | claude+codex | medium | medium | **fixed** | iki hakem de buldu; pozitif kontrol kolu var |
| N4 | claude+codex | medium | medium | **fixed (metin)** / açık (yerleştirme) | aktif katman kaydı §4'te |
| N5 | claude | medium | medium | **fixed** | — |
| N6 | claude | low | low | **fixed** | — |
| N7 | claude | low | low | **fixed** | `080aa7f`'ten devralınan |

**Severity indirme (`severity_downgrade`) YAPILMADI.** N2 raw `high` olarak duruyor.
**Medium/low'un hiçbiri `accepted_risk` yazılmadı** — hepsi bu zincirin kendi ürünü.

---

## 4. Bounded-pass durumu + human-checkpoint

**Pas bütçesi:** attempt-1 (tam dual) + fix + attempt-2 (kapanış, dual) **TAMAMLANDI.**
Attempt-2 sonrası **unresolved high VAR** → stop-rule gereği otonom döngü DURUR, karar insana geçer.

**Açık kalemler ve neden açık:**

| kalem | sev | neden kapanmadı | ev |
|---|---|---|---|
| **F3** — dönem kanonik anahtarı | high | sözleşme dönem satırında kanonik sistem anahtarı TAŞIMIYOR | dış sözleşme turu |
| **F4** — URL'de iddia numarası | high | sözleşmenin URL tablosu iddia numarası TAŞIMIYOR | dış sözleşme turu |
| **F1 günlük ayağı** — üçüncü not sınıfı | high | not sınıfı kümesi dış sözleşmede KAPALI | dış sözleşme turu |
| **N2** — çatışmanın operatöre ulaşması | high | hakemler ayrıştı; kanal değişti, tüketici eklenmedi | **KULLANICI KARARI** |
| **N4 yerleştirme** | medium | borçlar aktif katmanda adlandırılmış kalem değil | **KULLANICI ONAYI** (aktif katman yazımı) |

**Chain-advance: HARD-BLOCK.** Unresolved high var → `/security-review-claude-codex`'a geçilmez.

**Prosedürel kapanış (overclaim YASAK):** Tanımlı pas bütçesi tamamlandı (2 attempt;
her ikisi de dual). Adlandırılmış kapanış kontrolleri koştu: on adlandırılmış bulgunun yedisi
kapandı, biri davranış ayağıyla kapandı, ikisi beyan edilmiş sözleşme borcu olarak açık kaldı;
zarf içinde yedi yeni bulgu doğdu ve altısı kapandı. Kapsanan alanlar: etki zarfı (düzeltmenin
dokunduğu sekiz dosya + `auditors` · `identity` · `synthesis` · `readiness` · `runs` · `approval` ·
CLI). **Denenmeyen/kapsanmayan:** komple takım hakem ortamında koşulmadı (`.env` yok → DB testleri
hata veriyor; kontrolör ana ağaçta ayrıca koştu) · uçtan uca CLI koşumu · `ruff`/`pyright` (ortamda
yok) · zarf dışı genel yeniden keşif (talimat gereği yapılmadı). **Exhaustiveness iddiası YOK.**

## 5. Ham kanıt — işaretçiler (bu makinede, bu kökten)

- Codex kapanış turu: `/root/.claude/logs/otomaix--ffc87809/2026-09-11-review-feat-sektor-bilgi-paketi-plan2-2.md`
- Attempt-1 Codex: `…-1.md` · Attempt-1 Claude: `…-1.claude.md`

**Dürüst etiket:** işaretçiler MUTLAK yoldur; ham kanıt proje klonuyla TAŞINMAZ.
