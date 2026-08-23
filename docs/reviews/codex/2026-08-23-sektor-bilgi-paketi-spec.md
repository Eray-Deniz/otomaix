# Codex Adversarial Review — Sektör Bilgi Paketi Spec (2026-08-23)

- **Hedef:** `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (~1.360 satır)
- **Girdi referansı:** `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`
- **Codex session:** `01a02e3f-9ff3-7ad3-b493-ac4cb070a8d3` (3 tur, aynı oturum)
- **Sonuç: SHIP** (tur-3; tur-1 NO-SHIP → düzeltme → tur-2 NO-SHIP → düzeltme → tur-3 SHIP)

## Tur-1 (tam dosya, 6 eksen): 11 bulgu — 8 HIGH, 3 MEDIUM

| F | Özet | Akıbet |
|---|---|---|
| F1 | Genişleme kapıları içerik-karar ID'leriyle yazılmış (K-20/K-01b'yi yeniden açıyor); kapı kimlikleri K-32…K-37 kullanılmamış | Tur-2 RESOLVED |
| F2 | K-29 (pilot test markası) sessizce A ile kapatılmış | Tur-2 RESOLVED (+tur-2'de seçenek-uzayı regresyonu, tur-3 RESOLVED) |
| F3 | K-31 (pilot süresi) sessizce B ile kapatılmış | Tur-2 RESOLVED |
| F4 | "İnsan onayı yalnız aktivasyonda" hükümleri K-23'ün açıklığıyla çelişiyor | Tur-2 RESOLVED (4 kardeş site K-23'e koşullandı) |
| F5 | Mevzuat/güvenlik bloklama kapısı K-128 açıkken yürürlükte varsayılmış | Tur-2 RESOLVED |
| F6 | 10 açık karar "ID sweep'te" yer tutucusuyla; snapshot'ta ID'leri zaten var | Tur-2 RESOLVED (K-110, K-82/83, K-115/116, K-43/44/45, K-84/151/152, K-78/79, K-54, K-47, K-52, K-107, K-69/70; "snapshot Bölüm 17" ayrıştırması) |
| F7 | Fixture/enjeksiyon kurulum sırası çelişkili | Tur-2 RESOLVED (sıra spec hükmü olarak bağlandı: düzenek+fixture önce) |
| F8 | Ölçülmemiş sayılar mekanik kapı gibi davranıyor (adet alt sınırları, 2-3, ≤10/≤5) | Tur-2 PARTIAL → tur-3 RESOLVED (K-88'e kadar "notlu geçti" varsayılanı; ≤10/≤5 kesme kapısı değil; `2-3` = kaynakta yürürlükte yapısal çoğunluk kuralı, ampirik eşik değil — Codex kabul etti) |
| F9 | K-26 ile K-149 tek karara katlanmış | Tur-2 RESOLVED |
| F10 | Kabul matrisi "30 satır" sayımı yanlış (doğrusu 33) | Tur-2 RESOLVED |
| F11 | Etiketsiz sayılar (~563 KB, 2-3, ≥2 kaynak, 13/20/35 sayımları) | Tur-2 PARTIAL → tur-3 RESOLVED |

## Tur-2 (kapanış doğrulama): 9 RESOLVED, 2 PARTIAL, 1 yeni regresyon (K-29 seçenek uzayı)
## Tur-3 (hedefli): 3/3 RESOLVED; yeni çelişki/kapalı-karar regresyonu YOK → **SHIP**

Kapalı kararların tam occurrence sweep'i (tur-2): K-22 8/8 · K-27 5/5 · K-30 4/4 ·
K-05 8/8 · K-20 8/8 · K-21 5/5 · K-15(b) 3/3 · K-03 5/5 — tümü uyumlu.

**Codex'in doğrulamadıkları (dürüst sınır):** canlı kod/DB/Redis/n8n yeniden
koşulmadı — spec'teki "taze ölçüm" iddiaları belge tutarlılığı düzeyinde okundu
(ölçümler ana oturumda 2026-08-23'te koşulmuştu); runtime/migration/komut ailesi
çalıştırılmadı.
