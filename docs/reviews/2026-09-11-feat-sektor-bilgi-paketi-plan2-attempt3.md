# Review (dual, attempt 3): dış sözleşme turunun kod uyarlaması — 2026-09-11

Review aralığı: `10f22da4ff72ae2c2cacd53d0f4c0060a566c08c..4cf6aa38e8aad57cb591618ab217ace6e1162ece`
- BASE_REF: `10f22da` | BASE_SHA: `10f22da` | HEAD_SHA: `4cf6aa3` | REVIEW_BASE_SHA (merge-base): `10f22da` (sapma yok)
- Commit'ler: `2739797` (pin → dış depo `d9dc289`) · `4cf6aa3` (kod uyarlaması, 13 dosya)
Reviewers: fresh Claude subagent (`general-purpose`, code-reviewer personası) + Codex `adversarial-review`
dual-review: **true** (claude_status: ran — 67 araç çağrısı, 1010 s; codex_status: ran — rc=0, 52 komut koşumu, verdict `needs-attention`)
Review workspace: pinli worktree @ `4cf6aa3` (temiz)
Main tree at review: clean (0 uncommitted)
Requirement context (snapshot, iki hakeme birebir aynı — sha256 `f2389427…085df`): dış sözleşme `d9dc289` commit mesajı + üç dosyanın sha256 pini (iki hakem de byte-eşit doğruladı) · spec §9.4/§11.2 · arayüz eki "2026-09-11/d" (beyan olarak) · TASK.md ilk açık kalem — hepsi committed.
Güvenlik yüzeyi: `security_surface_touched: true` (pin/config dosyası değişti) → güvenlik-checklist eki KONMADI; `/security-review-claude-codex` zorunlu kalır.

**Review-defteri (ledger) — BU TURDA KURULDU.** `review_target_id = code-review:feat-sektor-bilgi-paketi-plan2:10f22da4ff72ae2c2cacd53d0f4c0060a566c08c`;
locator `docs/reviews/.ledger-index/296deb84…542d3.locator` → `task:sektor-bilgi-paketi-plan2` (authoritative ledger: TASK.md `# Review Ledger`);
`pinned_contract_hash = a76100bd551cefc7474b35b6c68ecec85cb4b87deb201770a503770b905808d0` (7 alan; `ch-only-v1`). Attempt-2 (kapanış) bu hash'i assert eder.

**Sapma beyanı:** Codex 480 s + retry deseni yerine tek koşum, 1200 s dış zaman aşımı, arka planda (uzun tur deseni; ölçülmüş süre 5 dk 30 s). Codex worktree'de sistem Python'ıyla test toplamaya çalıştı ve bazı dosyalarda bağımlılık eksikliğinden collection geçemedi; Claude alt-hakem venv ile **tam takımı taze koştu: 4370 passed, 315 s.**

---

## Critical
Yok.

## High

### F1 — Aday takvimde OLMAYAN dönem başka bir dönemin sistem anahtarını sahiplenebiliyor `[both-agree]` — kontrolör DOĞRULADI
`brief_doctor.py` `_aday_kopyasi_mi`: aday listesinde bulunmayan dönem adı için "kopya kuralı yok, geç" döndürüyor; geriye yalnız üyelik kontrolü kalıyor. Sözleşme aday dışı dönem için `—` (tek istisna: adıyla sayılan üç aday-dışı sistem günü) ister ve *"tablodakinden farklıysa hiçbir iddiası hiçbir kararı yetkilendiremez"* der.
**Kontrolör ölçümü (taze):** `| Sezon Açılışı | black-friday |` → 0 not, `gecti`, köprü `('black-friday',)` ile kuruldu. Alt-hakem zinciri sonuna kadar ölçtü: bu iddia `ozel_gun/sevgililer-gunu/...` eklemesini yetkilendiriyor; kümeler birleştirildiği için `cumhuriyet-bayrami` anahtarlı denetçi satırı `sevgililer-gunu` kararını yetkilendiriyor (R-D4'ün kapattığı sınıf bir basamak aşağıda).
**Minimal fix:** aday dışı dönemde yalnız `()` ya da tek bir aday-dışı sistem anahtarı kabul; `_kontrol_sistem_anahtari` + köprü aynı yüklemi kullanır. Negatif test: `Sezon Açılışı → black-friday` ve `sahte ad → aday-dışı anahtar dışı`.

### F2 — K-126 ikinci ayağı iddia KİMLİĞİNE bağlı, o iddianın URL'sine DEĞİL `[both-agree; severity ayrıştı: Codex high · Claude low → en yüksek]` — kontrolör DOĞRULADI
`CIddia` URL taşımıyor; `_url_orneklemi` boş olmayan herhangi bir URL'yi verilen kimlikle eşliyor; `_tek_kaynak_istisnasi` yalnız kimlik üyeliği + DOĞRULANDI bayraklarına bakıyor. Sözleşme: *"`URL` sütunu o Bölüm C satırının URL hücresidir — aynen kopyala."*
**Kontrolör ölçümü (taze):** `K1#2` kimliği korunup URL tamamen başka adrese çevrildiğinde istisna yine AÇILDI (`uygulanmayan_kararlar == ()`).
**Ayrışma notu:** alt-hakem "low" dedi (ikinci ayak zaten denetçi beyanı; kontrol yalnız dikkatsiz kopyayı yakalar, kasıtlı yanlış beyanı yakalamaz). Codex "high" dedi (resmî tek kaynaktan desteklenmeyen iddia pakete girebilir). Politika gereği en yüksek alındı; otonom indirme YOK.
**Minimal fix:** `CIddia.url` (Bölüm C'den aynen), `_tek_kaynak_istisnasi`'nda `UrlCheck.url == iddia.url` tam eşitlik; pozitif (tam URL) + negatif (doğru kimlik, başka satırın URL'si) test.

### F3 — K-03 notu karar günlüğüne yazılıyor ama ONAY YÜZEYİNE ulaşmıyor `[both-agree; severity ayrıştı: Codex high · Claude medium → en yüksek]` — kontrolör DOĞRULADI
`approval._goruntu_kur` uyarıları politika bulgularından (`_bulgu_ayrimi`) kuruyor; `tur="not"` satırları görüntüye girmiyor (`_sayilar` yalnız alan bazlı sayıyor); `render_summary` yalnız `uyarilar`ı basıyor; CLI onay akışı yalnız bu iki render'ı çağırıyor. Sözleşme 2.3 notun amacını *"operatörün onay anında GÖRMESİ"* diye yazıyor; kod docstring'i ve R-D8 de *"onay anında GÖRÜLÜR"* iddia ediyor — ölçülmemiş iddia (İlke 9(4)). Önceki turun N2 borcunun aynı ölçütle tekrarı.
**Kontrolör ölçümü:** `approval.py` içinde `"not"`/`tur-kategori`/`NOT_KONU` geçmiyor (grep boş); snapshot alanlarında not satırı yok.
**Minimal fix:** `final_decision_log`'daki bu sınıf notları görüntüye yapılandırılmış `kategori_catismalari` alanı olarak taşı (üç `konu` alanı), `render_summary`'de bloklamayan uyarı olarak bas; `SNAPSHOT_SEMA` ilerlet (dondurulmuş görüntü henüz üretilmedi — pilot koşmadı).

## Medium

### F4 — `engine.py` modül docstring'i K-126 ikinci ayağını hâlâ "KAYNAK düzeyinde, ZAYIF" ilan ediyor `[single-source: claude]`
Aynı commit onu iddia düzeyine indirdi; fonksiyon docstring'i, `engine_contract.py` ve ek güncellendi, modülün kendi dürüstlük beyanı süpürülmedi. **Politika:** medium → `accepted_risk`; **ama bu zincirin kendi ürünü (süpürme eksiği)** → düzeltme partisinde kapatılır (fix-required DEĞİL, gönüllü).

## Low

### F5 — `kaynak_seti_sha` mührü `CIddia.anahtarlar`'ı kapsamıyor `[single-source: claude]`
Elle sayılan alan kümesi (`no`, `alan`). `run()` yolunda metin kimliği geçişli kapsıyor; açık kalan yalnız `run`'ı atlayan çağıran. **Politika:** `accepted_risk`; F2'nin dokunduğu yerle aynı → düzeltme partisinde alan kümesi `CIddia` alanlarından türetilir (gönüllü).

### F6 — "Kaynak başına 3 satır" dağılımı ölçülmüyor (ÖNCEDEN VAR OLAN) `[single-source: claude]`
Yalnız toplam ölçülüyor; 9 satırın 9'u `K1#…` olsa geçer. Bu commit'in ürünü değil; kimlik içinde kaynak numarası olduğu için ilk kez mekanik ölçülebilir. **Politika:** `accepted_risk` — **ev:** Task 18 ön-pilot listesi (denetçi rapor kapıları).

---

## Disposition Ledger (her ham bulgu — sessiz drop yok)

| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| X1 | codex | high | high | kept → **F2** | kontrolör taze ölçümle doğruladı (yanlış URL ile istisna açıldı) |
| X2 | codex | high | high | kept → **F1** | kontrolör doğruladı (`Sezon Açılışı → black-friday` notsuz geçti) |
| X3 | codex | high | high | kept → **F3** | kontrolör `approval.py`'yi okudu: not satırı görüntüye girmiyor |
| C1 | claude | high | high | merged-into **F1** | aynı kök neden; zincir sonuna kadar ölçülmüş |
| C2 | claude | medium | medium | kept → **F4** | `accepted_risk` (politika) — kendi ürünümüz, gönüllü düzeltme |
| C3 | claude | medium | high | merged-into **F3** | severity uzlaştırma: en yüksek (Codex high); indirme YOK |
| C4 | claude | low | low | kept → **F5** | `accepted_risk`; F2 ile aynı dokunuş, gönüllü |
| C5 | claude | low | high | merged-into **F2** | severity uzlaştırma: en yüksek (Codex high); ayrışma F2'de açık |
| C6 | claude | low | low | kept → **F6** | `accepted_risk` (önceden var olan), ev Task 18 |

**Severity indirme (`severity_downgrade`) YAPILMADI.** F2 ve F3 raw `high` olarak duruyor.
**`policy_accepted` (otonom, medium/low):** F4 · F5 · F6. Üçü de sentez-sonrası geçerli, açık, `rejected` değil (INV-A).

## Sonuç
- Kapatılan (push-back): 0
- Açık (devam): **3 high fix-required** (F1 · F2 · F3) + 3 `accepted_risk` (F4 · F5 · F6; F4/F5 gönüllü düzeltilecek)
- Hakemler-arası çelişki: **yok** (üç high'ın üçünü de iki hakem buldu; ayrışma yalnız severity'de — F2 low↔high, F3 medium↔high; en yüksek alındı)
- Sorun bulunmayan alanlar (alt-hakem ölçerek geçti): not sınıfı/`konu` şeması · sentezin yazdığı üçüncü sınıf → blok · `—`/boş küme · çelişen ikinci satır · çok anahtarlı dönem · eski biçim URL satırı · değişen imzaların tüketicileri (synthesis, CLI, lifecycle) · R5 alan kümesi · `ENGINE_VERSION` · güvenlik (bariz açık yok) · performans.
- Alt-hakemin bağımsız mutasyon probu: 4 mutasyon, 4/4 kırıldı (kalan 8 bağımsız doğrulanmadı — orchestrator ölçümü 12/12).

**Chain-advance: HARD-BLOCK** — unresolved high var → `/security-review-claude-codex`'a geçilmez. Yol: düzeltme partisi (executor) → attempt-2 kapanış turu (aynı pinli sözleşme, `a76100bd…`).

## Ham kanıt — işaretçiler (bu makinede, bu kökten)
- Codex ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-11-review-feat-sektor-bilgi-paketi-plan2-3.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-11-review-feat-sektor-bilgi-paketi-plan2-3.claude.md`

**Dürüst etiket:** işaretçiler MUTLAK yoldur; ham kanıt proje klonuyla TAŞINMAZ (K4 kabul edilen risk).
