# Active Tasks

- `sektor-bilgi-paketi/` — sektör bilgi paketi runtime çekirdeği (Plan 1; dal `feat/sektor-bilgi-paketi`)

## Proposed (spun-off)
- **s1-substrate-tracked-secret-scan** (proposed, güvenlik/defense-in-depth) — `CODEX-SCAN-SUBSTRATE` (byte-locked 4-way) tracked-dirty diff'i secret-scan ETMİYOR (yalnız untracked REQUIRED taranıyor; `git apply` execute-plan:1228-1231 vs `_css_secret_scan` 1233-1238). Dar (committed içerik zaten in-scope; yalnız tracked-dosyada-uncommitted-secret) ama düzeltmeli. Detay + structured fix: security-review **SF1** (`docs/security-reviews/2026-06-04-codex-review-scope-contract.md`). Kapsam: substrate bloğu (4 dosya) + `codex-scan-substrate-harness.sh` tracked-secret fixture.

- **stale-sweeper-vs-late-webhook-terminality** (proposed, ürün kararı + arka uç tutarlılığı) —
  Süpürücü `generating`i **10 dakikada** `failed` yapıyor (`internal.py`
  `interval '10 minutes'`), ama `fal_webhook` tek görsel/video satırını
  `fal_job_id` ile bulup durum kapısı OLMADAN sonradan `ready` + `output_url`
  yazabiliyor. Yani arka uçta `failed` terminal DEĞİL; iki mekanizma aynı satır
  hakkında çelişebiliyor. **10 dakikanın ölçülmüş bir dayanağı YOK:** vault
  kararı ([[decisions/2026-03-25-stale-job-sweeper]]) gerekçeyi "webhook kaybı
  güvenlik ağı" diye yazıyor, model süresi ölçümüne ya da sağlayıcı belgesine
  dayanmıyor (kaydın kendisi `verification-status: unverified`).
  **Karar Eray'a ait:** geç gelen başarı kabul edilsin mi, yoksa eşikten sonrası
  kesin başarısız mı sayılsın — ve eşik hangi ölçüme dayansın.
  **Tetik (Eray, 2026-08-25): sektör bilgi paketi işi TAMAMEN bittikten sonra
  ele alınacak** (fal.ai model değişikliği de o dönemde planlanıyor; eşik o
  modellerin gerçek süreleriyle birlikte gözden geçirilmeli).
  Şimdilik yalnız arayüz arka uçla tutarlı hâle getirildi (`532825e`);
  sözleşmenin kendisi ÇÖZÜLMEDİ.

<!-- Son kapanan: codex-review-scope-contract → done 2026-06-04, arşiv docs/task-archive/2026/06/ -->

