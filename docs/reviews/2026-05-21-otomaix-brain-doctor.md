# Review: Otomaix Brain Doctor v1 — 2026-05-21

BASE: 9b0376d
HEAD: 7577a61
Reviewer: superpowers:requesting-code-review (fresh general-purpose subagent)
Kapsam: 16 commit, `tooling/brain-doctor/` (brain_doctor.py 544 satır + test 387 + config + README)
Doğrulama: reviewer 35 unittest çalıştırdı (PASS) + gerçek vault smoke (124 sayfa, 28 bulgu, exit 1, vault `diff -rq` ile değişmedi)

## Critical

Yok. Spec temel invariant'ları doğru implement edilmiş ve testlerle korunmuş:
- §7 link çözümleme sırası (resolve_link): path-qualified typo basename'e düşmüyor → broken; dup-basename+full-path → step 2'de ok. Doğru.
- Vault-output guard (main): çıktı vault altına düşerse `--allow-vault-output` olmadan exit 2.
- Read-only doğrulandı (vault değişmedi).
- §6 severity coverage guard: 16/16 kategori eşleşiyor.
- Exit code önceliği: had_error filtre öncesi hesaplanıyor; `--min-severity info` ile bile error → exit 1.
- `--json` saf stdout; özet/diagnostic stderr'e.

## Important

- **index.md ambiguous referans sessizce yutuluyor** (brain_doctor.py:341-348). `check_index` yalnız `broken` + çözülen ref'i işliyor; `status == "ambiguous"` (rel=None) ne issue üretiyor ne `referenced`'a ekliyor. Sonuç: index'teki belirsiz atıf görünmez kalır + o sayfalar yanlışlıkla page_not_in_index/orphan işaretlenebilir. Spec §7 "ambiguous = error" der → index için sessiz geçiş bu invariant'ı deliyor. **Latent** (vault şu an basename-only index girişi kullanmıyor). Düzeltme: `elif status == "ambiguous"` dalı + ambiguous_link emit.

## Minor

1. Başlıklı md link `[t](path.md "title")` sessizce atlanıyor — `_MDLINK_RE` (brain_doctor.py:159) title kısmını yakalıyor, target `.md` ile bitmiyor → false-negative. Vault'ta böyle link yok.
2. Kapanmamış tek ``` fence — `strip_code` (brain_doctor.py:163) DOTALL içeriyi temizlemez → olası false-positive broken link. Vault'ta odd-fence dosya yok.
3. `deprecated_visibility` (brain_doctor.py:395) `"deprecated"` status'ünü de kontrol ediyor ama config enum'unda yok (sadece `"superseded"`) → ölü dal. Enum'a eklenmeli ya da çıkarılmalı.
4. Bozuk `last-verified` tarihi (check_stale, brain_doctor.py:289-291) ValueError yutulup atlanıyor — ne stale ne ayrı uyarı. Spec-uyumlu (bozuk-tarih kategorisi yok) ama gözlemlenebilirlik eksiği.

## Sonuç

- Kapatılan: 🟡 index ambiguous-yutma → TDD ile düzeltildi (check_index'e `elif status=="ambiguous"` dalı + `test_index_ambiguous_ref_emitted`). 36 unittest PASS, gerçek vault smoke birebir aynı (28 bulgu — fix latent).
- Açık (devam ediyor): yok
- Push-back (kullanıcı reddetti): yok
- 🟢 Minor (1-4): not düşüldü, v1.1 değerlendirmesine bırakıldı (latent edge'ler + ölü `"deprecated"` dalı)

**Reviewer yargısı: Merge'e hazır.** Critical yok; tek 🟡 bu branch'te kapatıldı.
