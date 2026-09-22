# Review (single-reviewer: claude): sentez onarımı — okuyucu, düzeltme hakkı, akış kipi — 2026-09-22

Review aralığı: `a8882a0..be5c320`
- BASE_REF: `a8882a0` (bugünkü onarımdan önceki son devir commit'i) | BASE_SHA: `a8882a0` | HEAD_SHA: `be5c320` | REVIEW_BASE_SHA (merge-base): `a8882a0`
- Commit'ler: `95d846b` chore(contracts) pin · `4a260f2` fix(sentez) (asıl kod) · `ec5010e` / `be5c320` docs(active)
- 9 dosya, +1539 / −138

Reviewers: fresh Claude subagent (general-purpose; model config-default `claude-opus-5-5`) + Codex adversarial-review
dual-review: **false** (claude_status: ran; codex_status: **failed** — kota sınırı, tur yarıda kesildi)
review_confidence: **reduced**
Review workspace: pinned worktree @ `be5c320` (clean)
Main tree at review: clean
Requirement context (iki hakeme aynı pinli committed dosyalar — gömülmedi, işaretçiyle okutuldu; birleşim sha256 öneki `9746c997995f`):
`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` §Task 11 · `docs/active/sektor-bilgi-paketi-plan2/SENTEZ-KESILME-SORUNU.md` · `…-GUNCELLEME.md` — hepsi committed @ `be5c320`.
Ek bağlam (iki hakeme birebir aynı): HANDOFF "Notes For Codex"taki dört açık soru, nötr soru olarak.
security_surface_touched: **true** (alt süreç çıktı yolu, koşu köküne yeni dosyalar) → güvenlik-checklist eki konmadı; `/security-review-claude-codex` zorunlu.

**Codex neden sayılmadı:** tur 18:05 UTC'de başladı, kullanım sınırına çarptı ("try again at 7:09 PM"),
companion `rc=1`. Log'daki "Verdict: approve / No material findings" satırı, hiçbir prob/test tamamlanmadan
kesilmiş bir ara mesajdır — karar olarak KULLANILMADI. Eray Claude-only kapanışı seçti.

## Critical
Yok.

## High
Yok.

## Medium
Hepsi `[single-source: claude]` · hepsi **claude-confirmed** (orchestrator dosya açarak/prob koşarak ölçtü) ·
hepsi **introduced_by_fix (`4a260f2`)** → `accepted_risk`'e ALINMADI (kendi ürettiğimiz gerileme; düzeltilecek).

- **M1 — Akış okuyucusu gövde dışı metni belgeye katıyor** (`auditors.py` `_akisi_coz`, ~2579-2595).
  Bütün `assistant` metin blokları araç çağrısına bakılmadan birleştiriliyor. Ölçüldü (çevrimdışı prob,
  orchestrator tekrarladı): araç çağrısından önceki "Görev dosyasına bakayım." cümlesi ilk başlığa yapışıyor
  → 1. bölüm kayboluyor → ücretli düzeltme turu; belge ortasındaki ara metin ise sessizce bölüme giriyor
  (ÖZET'e "Belge tamamlandı." gibi). Kaç gerçek koşumda olduğu ölçülmedi.
- **M2 — Düzeltme denemesi önceki denemenin reddedilen çıktısını görüyor** (`synthesis.py:1235` `runner.run(…, kok, …)`
  + `auditors.py` `_sahne` → filtresiz `copytree`). 2. çağrının dizininde `01-SENTEZ-CIKTISI.md`,
  `01-SENTEZ-AKISI.jsonl`, `02-…` var; "belgeyi BAŞTAN yaz" talimatıyla çelişiyor, girdi beyansız değişiyor.
  Güven sınırı dışından yeni veri yok — sorun girdi bütünlüğü.
- **M3 — Ham akış hata yolunda diske yazılmıyor** (`auditors.py:2484-2490`, `synthesis.py:1236-1252`).
  `ham_akis` yalnız `kod==0` iken dolduruluyor ve `_kos` `durum!="tamam"`da yazmadan fırlatıyor; zaman aşımı
  ve ayrıştırılamayan akış (tam da kesilme vakası) kanıtsız kalıyor.
- **M4 — Düzeltilebilir sınıfın JSON/tip/boş-özet kolları testle sabitlenmemiş.** Test dosyalarında
  `SynthesisOutputError` 0 kez geçiyor (grep ile ölçüldü); negatif testler üst sınıf `SynthesisFailed`'i
  bekliyor. `synthesis.py:368/375/381/495/520` kollarını terminal sınıfa geri çeviren mutasyon yakalanmaz
  (akıl yürütme; mutasyon koşulmadı).
- **M5 — `test_duzeltme_istemi_SOMUT_hatalari_tasir` iddiasını sınamıyor** (`tests/test_synthesis.py:2009-2010`).
  Aradığı `"ADAY PAKET"` düzeltme ekinin sabit metninde zaten var (`synthesis.py:408`); `> {hata}` satırı
  silinse test yeşil kalır.

## Low
Hepsi `[single-source: claude]`; `accepted_risk` (policy_accepted, ch-only-v1) — M1-M5 düzeltmesinde aynı
dosyalara dokunulacağı için birlikte kapatılmaları ucuz.

- L1 — `json` çıktı kipinin üretimde çağıranı yok (`_zarfi_coz` + 4 test). Evi var: TASK Open Problems → `/simplify-claude-codex`.
- L2 — `olcum` sözlüğü `_zarfi_coz` ve `_akisi_coz`'da kopya (L1 ile birlikte kalkar).
- L3 — `_cikti_butcesini_dogrula` docstring/mesajı ve iki test docstring'i hâlâ "json kipi" diyor; ad da işi anlatmıyor.
- L4 — `CIKTI_BICIMLERI` docstring'i ilgisiz `MAX_THINKING_TOKENS` anlatısı taşıyor.
- L5 — `bitis_nedeni` ölçüm anahtarı docstring'de ve log satırında yok.
- L6 — hak tükenince terminal sebebe yalnız 2. denemenin hatası yazılıyor.
- L7 — düzeltme eki pinli sözleşme dışında yeni istem talimatı; Decisions Log'da istisna olarak kayıtlı değil.
- L8 — gereksiz list comprehension (`synthesis.py:483`).
- L9 — akış dosya adı `.replace()` ile türetiliyor (`synthesis.py:1248`).

## Dört açık soru (HANDOFF "Notes For Codex")
1. Düzeltme hakkının sınırı: **temiz** — `except SynthesisOutputError` yalnız `_cikti_bicimini_coz`'u sarıyor
   (`synthesis.py:1258-1263`); araç arızası, ölçüm kapısı, kimlik bağlama, DB yolları terminal. Toplam 2 çağrı.
2. Gövde dışı metin: **evet** → M1.
3. Sahne kopyası: **evet** → M2 (akış dosyasının düşünme metni taşıyıp taşımadığı ölçülmedi).
4. Çağıransız kip: **evet**, `json` → L1.

Plan uyumu (Task 11): pakete yazma yok, terminal yollar `mark_incomplete`'e gidiyor, deneme döngüsü aynı
koşu kimliğinde. Pin: dış depoda `38b475b` var, üç dosyanın sha256'ı pinle aynı (alt-hakem ölçtü).

## Disposition Ledger
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| M1 | claude | medium | medium | kept — open (fix) | claude-confirmed: prob tekrarlandı, çıktı birebir; introduced_by_fix |
| M2 | claude | medium | medium | kept — open (fix) | claude-confirmed: `kok` cwd + filtresiz copytree okundu; introduced_by_fix |
| M3 | claude | medium | medium | kept — open (fix) | claude-confirmed: `ham_akis` yalnız kod==0 dalında; introduced_by_fix |
| M4 | claude | medium | medium | kept — open (fix) | claude-confirmed: grep 0 isabet; mutasyon koşulmadı |
| M5 | claude | medium | medium | kept — open (fix) | claude-confirmed: sabit metin `synthesis.py:408` |
| L1-L9 | claude | low | low | accepted_risk | policy_accepted (ch-only-v1); L1'in tarihli evi var |
| C1 | codex | — | — | closed (not a finding) | kota ile kesilen tur; "approve" ara mesajı karar sayılmadı |

## Sonuç
- Kapatılan (push-back): 0
- Açık (devam): 5 medium (düzeltme gerekli) · 9 low accepted_risk
- Hakemler-arası çelişki: yok (ikinci hakem çalışmadı)
- Unresolved critical/high: **yok**

Tanımlı pas bütçesi tamamlandı (1 attempt; total_invocations=1, consecutive_degraded=1); ledger:
`task:sektor-bilgi-paketi-plan2` (completed_evaluations=1, single-reviewer). Kapsanan alanlar: iki kaynak
dosyanın diff'i, `_kos`/`run`, ayrıştırıcılar, `_sahne`, iki test dosyasının diff'i, gereksinim dosyaları, pin.
Kapsanmayan: `auditors.py` diff dışı gövdesi, pinli sözleşme metni (yalnız hash), kayıtlı sentez çıktıları;
test takımı bu review'da koşulmadı. İkinci bağımsız göz yok. Exhaustiveness iddiası yok.

## Ham kanıt — işaretçiler (bu makinede, bu kökten)
- Codex ham çıktısı (kesik tur): `/root/.claude/logs/otomaix--ffc87809/2026-09-22-review-feat-sektor-bilgi-paketi-plan2-sentez-onarimi-1.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-22-review-feat-sektor-bilgi-paketi-plan2-sentez-onarimi-1.claude.md`
