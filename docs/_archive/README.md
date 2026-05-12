# Docs Archive

Bu dosyalar `/root/otomaix-brain/` vault'una migrate edildi. **Tek hakikat artık vault.**

Burası tarihsel arşiv — dosyalara dokunma, güncelleme yapma. Yeni karar / sprint çıktısı doğrudan vault'a yazılır (sprint sonu `/commit` skill'i hatırlatır).

Migrate tarihi: 2026-05-12

## Vault'a referans

Her vault sayfası frontmatter'da bu klasördeki orijinal dosyaya `@/root/otomaix/docs/_archive/<dosya>.md` ile link veriyor. Tarihsel iz takibi için orijinaller burada saklanıyor.

## Arşivdeki dosyalar

| Dosya | Vault hedefi |
|---|---|
| `00-platform-mimari.md` | `cross-project/infrastructure/` (Task 7) |
| `01-social-phase1.md` | `apps/social/architecture/history/phase-1-altyapi-kurulumu` |
| `02-social-phase2.md` | `apps/social/architecture/history/phase-2-temel-ozellikler` |
| `03-social-phase3.md` | `apps/social/architecture/history/phase-3-gelismis-ozellikler` |
| `04-social-phase4.md` | `apps/social/architecture/history/phase-4-saas-hazirlik` |
| `05-crm-admin.md` | `apps/crm/architecture/` |
| `06-social-trends-phase6.md` | `apps/social/architecture/history/phase-6-trend-sistemi` |
| `07-social-template-system.md` | `apps/social/templates/` + `apps/social/architecture/template-system-design` + `cross-project/vendors/` |
| `11-social-marketingskills.md` | `cross-project/copywriting/` + `apps/social/architecture/marketingskills-entegrasyon` |
| `12-social-carousel.md` | `apps/social/pipeline/carousel` + `apps/social/architecture/carousel-design` |

`marketingskills.md` (raw analiz) ayrı bir kategoride: tam kopya `vault/sources/research/2026-04-marketing-skills-analizi.md`'a alındı, bu dosya silindi (canonical orası).
