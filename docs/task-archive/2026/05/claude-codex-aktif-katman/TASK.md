---
title: Claude-Codex Aktif Task Layer
status: archived
started: 2026-05-19
last-touched: 2026-05-19
blocked-by: null
---

# Goal

Otomaix repo'sunda Claude ↔ Codex arasında session-boundary devir teslim + canlı task state için overlay (`docs/active/<slug>/{TASK,HANDOFF}.md`) kurmak. Başarı: 5 mevcut slash command'e hatırlatma entegrasyonu + yeni `/handoff` komutu + vault dokunulmadan canonical/ephemeral ayrımı.

# References

- Spec: `docs/specs/2026-05-19-claude-codex-aktif-katman.md`
- Plan: `docs/plans/2026-05-19-claude-codex-aktif-katman.md`
- Review: _(yok — smoke test sırasında yazılıyor)_

# Current Status

Phase A–H tamamlandı (Task 1–12). Smoke test başarılı: dummy task lifecycle (yarat → /handoff → /handoff --with-codex → P1 simülasyon → closure → archive) end-to-end walkthrough geçti. Task 13 (Phase I) closure adımlarıyla aynı commit'te bitiyor.

**Plan progress:** 12/13 task tamam — Task 13 closure ile aynı anda finalize.

# Open Problems

_(yok — Task 13 closure'da memory önerisi üretilecek)_

# Decisions Log

- 2026-05-19: Split lokasyon — kalıcı vault'ta, geçici `docs/active/` repo'da. Alternatifler B (flat in vault), C (karma); reddetme: branch-aware kayıp + vault disiplini gevşemesi
- 2026-05-19: CURRENT.md pointer model — branch-agnostic discovery. Alternatif: branch adından discovery; reddetme: main ağırlıklı çalışma + paralel feature gerçeği
- 2026-05-19: Klasör per task (TASK.md + HANDOFF.md ayrı) — lifecycle ayrımı için. Alternatif: tek .md per task; reddetme: TASK ve HANDOFF farklı lifecycle'a sahip, aynı dosyada drift riski
- 2026-05-19: TASK.md schema = Lean + References (Goal/References/Current Status/Open Problems/Decisions Log). Alternatifler: Fat (Constraints+Risks+Test Plan+Vault Promotion ayrı), Minimal; tercih: lean + References standardize
- 2026-05-19: Status set = `proposed | active | blocked | waiting-review | done | archived | cancelled`. `waiting-review` "review" yerine (aksiyon mu durum mu netliği), `cancelled` ayrı terminal state
- 2026-05-19: HANDOFF.md rolling (append-only journal yerine) + 7 section schema (Context/Current State/Resume From/Verification/Risks/Notes For Claude/Notes For Codex). git zaten append history sağlıyor
- 2026-05-19: HANDOFF.md `/commit`'te dokunulmaz — sadece session-boundary, blocker, review, closure. Aksi halde progress log'a dönüşür → TASK ile duplication
- 2026-05-19: Slash command entegrasyonu Z hibrit (task aware ama task driven değil, hatırlatma soruları). Alternatifler: X tight coupling, Y loose; tercih: manuel mod uyumu
- 2026-05-19: `/handoff` opt-in Codex (`--with-codex` flag). Default Claude tek başına yazar. Otomatik Codex çağrısı YOK (maliyet + non-determinism)
- 2026-05-19: Vault promotion P1 — Claude candidate listeler, kullanıcı seçer, Claude vault'a yazar. Alternatifler: P2 manuel command, P3 sadece reminder; tercih: friction-low + onay kapısı
- 2026-05-19: Archive `docs/task-archive/YYYY/MM/<slug>/` (bitiş tarihine göre). Alternatif yol 2 (nest in docs/archive/) ve yol 3 (nest in active/); reddetme: semantik karışıklığı
- 2026-05-19: status=archived TASK.md'de move'dan ÖNCE yazılır (mantıksal sıra: archive klasöründeki dosya archived olmalı, move sonrası edit ters)
- 2026-05-19: /finish-branch closure conditional — sadece merge ve sil tetikler full closure+archive; PR → `waiting-review` + HANDOFF rolling (archive YOK); tut → no-op
- 2026-05-19: Codex memory'ye ve vault'a yazmaz — öneri olarak stdout çıkarır, Claude/kullanıcı uygular (Phase G, Phase I memory entry)
- 2026-05-19: Dummy karar — smoke test için P1 heuristic'ini tetiklemek; bu satır promote edilmemeli (task-scope-only)
