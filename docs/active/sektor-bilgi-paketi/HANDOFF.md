# Handoff

## Context
- Task: sektor-bilgi-paketi (runtime çekirdek uygulaması)
- Linked spec: docs/specs/2026-07-11-sektor-bilgi-paketi.md
- Linked plan: docs/plans/2026-07-12-sektor-bilgi-paketi.md
- Branch: main (execute başlarken branch açılması önerilir)
- Last updated: 2026-07-12

## Current State
- Summary: Plan yazıldı ve 12-turlu Codex adversarial review'dan approved çıktı (commit
  bda53f7). Uygulamaya başlanmadı.
- Blocked: hayır

## Resume From
- Start here: `/execute-plan-claude-codex docs/plans/2026-07-12-sektor-bilgi-paketi.md`
  (Task 1'den — Tier-1 hiyerarşi satırı)
- Relevant files: plan dosyası + spec §14 faz sırası
- Next command: —

## Verification
- Passed: plan-review zinciri (Codex 12 tur; hedefli final tur: F27/F28/K7 zinciri closed)
- Failed: —
- Not run: tüm implementation testleri (henüz kod yok)

## Risks
- K7 echo zinciri frontend ayağı davranışsal test edilmiyor (operatör-kabullü kalıntı; statik
  5-nokta script + Faz 4 canlı teyit — plan T29).
- Migration 032 tek dosya, T10'a kadar commit'lenmez (F20 kuralı) — ara durumda deploy edilemez.

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: K7 damga semantiği version-governance'tır
  (içerik-bütünlüğü DEĞİL — plan T23'te bağlı); aktivasyon ön-kontrolü `publishing` dahil.
- Claude'un sonraki session'da işlemesi gereken şeyler: execute başında plan T1'den; komut
  konvansiyonu cwd=apps/social/backend.
- Vault'a yazılması gerekebilecek kalıcı kararlar: eşitlik-reddi damga tasarımı; K6 kapsam
  netleştirmesi (analyze-website K6-dışı) — closure'da promote edilebilir.
- Spec/plan güncellemesi gerektiren noktalar: yok (plan spec'le hizalı; Codex yön onayı verdi).
- Kullanıcıdan karar bekleyen konular: yok (execute onayı dışında).

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: K7 echo zinciri (üretici→state→
  tüketici→matris), migration 032 trigger aileleri, K6 golden byte-exact disiplini.
- Bilinen riskler: HANDOFF Risks bölümü.
- Dokunmaması gereken alanlar: `brands.sector` TEXT + `brands.sector_id` semantiği; legacy
  `/posts/generate-short-video` (bozuk-boş korunur); SECTOR_GUIDANCE yan-yana basım yasağı.
- Önce okunması gereken dosyalar: plan Global Constraints + Plan-Düzeyi Karar Kayıtları (D1-D10).
