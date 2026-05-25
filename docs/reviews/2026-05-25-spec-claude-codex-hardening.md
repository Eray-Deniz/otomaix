# Review: spec-claude-codex Robustness Hardening — 2026-05-25

BASE: working-tree (komut dosyası ~/.claude/commands/ git'te değil; spec working-tree diff)
HEAD: working-tree
Reviewer: fresh general-purpose subagent (superpowers:requesting-code-review akışı)

Kapsam: `~/.claude/commands/spec-claude-codex.md` 6 edit + drift kapatma; repo
`docs/specs/2026-05-20-spec-claude-codex-command.md` §11 amendment.

## Companion iddiası doğrulaması (taşıyıcı karar)
Reviewer kaynak koddan satır satır doğruladı, **doğru çıktı**:
- `handleReviewCommand` (codex-companion.mjs:682-723) `--background`/`--wait`'i parse
  edip kullanmıyor; koşulsuz `runForegroundCommand` (709). Job-lifecycle yalnız
  `handleTask` (758).
- `adversarial-review` → `runAppServerTurn` `sandbox: "read-only"` hardcoded (411).
  `task` `--write`'sız → read-only (488). `--cwd` + positional prompt doğru.
- "foreground + dış timeout" kararı sağlam.

## Critical
_(yok)_

## Important
1. **`timeout 240s` çok dar** (`spec-claude-codex.md:60`). Codex'in normal uzun
   review'ı bu sınırda SIGTERM yiyip sahte "timeout" olarak degradation'a düşebilir;
   "tekrar dene" aynı duvara çarpar. → **Düzeltildi:** 480s'e çıkarıldı (komut bash +
   Sözleşme Notları + spec §11, 4 yer). Not: reviewer'ın "240s = Codex iç bütçesi"
   gerekçesi tam isabetli değil (o sabit `status --wait` polling içindir, kullanılmıyor)
   — ama endişe geçerli, fix uygulandı.
2. **`$SCOPE` tırnaksız sözleşmesi örtük** (`spec-claude-codex.md:58-60, 327`).
   `<CALL> = adversarial-review $SCOPE`'da `$SCOPE` tırnaksız kalmalı (word-splitting),
   boş olabilir. → **Düzeltildi:** bash yorumuna "TIRNAKSIZ bırak, boş olabilir" notu.

## Minor (hepsi pozitif teyit — aksiyon yok)
- Untracked taze spec `git status --short` ile non-empty → working-tree scope doğru;
  `collectWorkingTreeContext` `--untracked-files=all` ile untracked'i de kapsıyor.
- Degradation "Claude-only devam" her iki downstream adım için güvenli (Adım 3 fallback
  string, Adım 6 review atlanır); `<DROPPED_ALT>` boşsa Adım 6 prompt "skip" ile korumalı.
- Adım 0 read-only ↔ Adım 11 onayla-yaz üç noktada (Adım 0, 11, Checklist) tutarlı.
- Referans bütünlüğü temiz: Adım no 0-12, protokol referansları, 4 placeholder tutarlı;
  silinen bölümlere dangling ref yok; stale `--wait`/`HEAD~1`/rescue komut dosyasından
  tamamen temizlenmiş (spec §3'te kasıtlı tarihsel kayıt, §11 ile supersede).

## Sonuç
- Reviewer genel değerlendirmesi: **merge-ready**.
- Kapatılan: 2 Important (240s→480s, $SCOPE notu) — uygulandı.
- Açık: _(yok)_
- Push-back: _(yok)_
