# Review: Claude–Codex Aktif Task Layer — 2026-05-19

**BASE:** `5a8d22e` (plan commit)
**HEAD:** `8aa5ae7` (plan progress closure)
**Kapsam:** 6 commit plan execution (spec/plan kendisi kapsam dışı — Eray ile iteratif refine edildi)
**Reviewer:** fresh subagent (`general-purpose`, superpowers:requesting-code-review prompt yapısı)
**Genel durum:** 0 Critical, 4 Important, 7 Minor. Plan implementation kalitesi yüksek; sapmalar bilinçli ve belgeli; spec uyumu güçlü.

---

## Critical

Yok.

---

## Important

### #1 `finish-branch.md` Adım 6/7 sıra bug'ı — DÜZELTİLDİ

**Bulgu:** Adım 6 (Seçime Göre Uygula, branch action) Adım 7'den (Aktif Task Layer Closure) ÖNCE çalışıyordu. "D (sil)" path'inde `git checkout main` + `git branch -D` working tree'yi değiştirir → Adım 7 closure çalışınca taşınacak task dosyalarına erişim kaybedilir. Spec §8.2 "Konumlandırma: Closure adımı kullanıcı seçiminden sonra, branch işleminden önce" ile çelişiyor.

**Fix:** `~/.claude/commands/finish-branch.md` — Adım 6 ile Adım 7 yer değiştirildi:
- Yeni Adım 6: Aktif Task Layer Closure Matrix (önce çalışır)
- Yeni Adım 7: Seçime Göre Branch İşlemini Uygula (sonra çalışır)
- Her ikisinin başına explicit **Sıra disiplini** notu eklendi

**Durum:** ✅ kapatıldı.

### #2 Smoke test "cancelled" path test edilmedi — NOT EKLENDİ

**Bulgu:** Plan Task 12 Step 5 açıkça `status: cancelled` simülasyonu istiyordu (`finish-branch` SİL yolu). Execution `status: done` kullandı (gerekçe HANDOFF'ta belgeli ve makul). Sonuç: cancelled path closure davranışı end-to-end test edilmedi.

**Fix:** Plan dosyasında Phase H satırına parantez içi not düşüldü: *"done path test edildi, cancelled path test edilmedi — ileride gerçek cancel ile doğrulanmalı"*. CLAUDE.md İlke 3 (mutlaklık iddiası yasak) uyumu.

**Durum:** ✅ kapatıldı (not düşüldü, gerçek cancel ileride yapılır).

### #3 `/handoff` bash prompt `<slug>` escape riski — NOT EKLENDİ

**Bulgu:** `~/.claude/commands/handoff.md` Codex companion çağrısında `<slug>` placeholder Claude tarafından run-time substitute edilir. Sade slug için sorun yok, dinamik/özel karakter için escape gerek.

**Fix:** Prompt notu genişletildi: *"Sade kebab-case slug'lar için sorun yok; dinamik/özel karakter içeren slug için `printf %q` ile escape öner"*.

**Durum:** ✅ kapatıldı.

### #4 `templates/` "opsiyonel" denmiş, mecburi olmuş — FALLBACK NOTU EKLENDİ

**Bulgu:** Spec §10.1 templates'i opsiyonel dedi, plan/execution mecburi yaptı. Template silinirse `/write-plan` Aktif Task Layer hatırlatması kırılır.

**Fix:** `~/.claude/commands/write-plan.md` hatırlatma bloğuna fallback notu eklendi: *"Template yoksa, spec §4.2 ve §4.3 inline schema'sını manuel kullan"*.

**Durum:** ✅ kapatıldı.

---

## Minor

### #5 AGENTS.md damıtması Codex policy ifadesi sadece active layer'ı kapsıyor

**Bulgu:** Repo `/root/otomaix/AGENTS.md:87-91` "Codex Yetkisi" sadece Active Task Layer. Vault AGENTS.md memory/vault yazımı yasağını da içeriyor; damıtmaya eklenmemiş.

**Aksiyon:** Bir sonraki `/sync-agents-md project` çağrısında CLAUDE.md'ye "Codex: memory + vault + active layer'a yazmaz" tek satırı eklenirse otomatik düzelir. Şimdi düzeltme yapılmadı.

### #6 AGENTS.md damıtma başlık satırı bozuk İngilizce

**Bulgu:** `/root/otomaix/AGENTS.md:8` *"from distilled"* gramer hatası (`'den damitilmistir` olmalıydı).

**Aksiyon:** Bir sonraki `/sync-agents-md project` çağrısında Codex damıtması düzeltir; manuel müdahale gerekmez.

### #7 CURRENT.md değişikliği commit'te görünmüyor

**Bulgu:** Smoke test commit'inde CURRENT.md staged değil çünkü ön/son hali aynı (`_(no active tasks)_`). İz bırakmıyor.

**Aksiyon:** Yok — beklenen davranış.

### #8 `/handoff` `<slug>` placeholder run-time substitution AI agent ilk kullanım riski

**Bulgu:** `<slug>` literal placeholder; ilk kez kullanan AI agent (özellikle Codex) "literally write `<slug>`" yapma riski. Spec §6.2 + handoff.md Notlar bunu söylüyor.

**Aksiyon:** Yok — risk düşük, notlar yeterli.

### #9 Vault `verification-status` değişmedi, sadece `last-verified` bump

**Bulgu:** `8dd5c34` codex-entegrasyonu.md `last-verified` güncelledi, içerik değişikliği var ama `a-verified` korundu. Yeni blok ayrı verification döngüsünden geçmedi.

**Aksiyon:** Yok — değişiklik deklaratif (spec dosyasına işaret), Eray'ın takdiriyle bırakıldı.

### #10 `/commit` Adım 8 cwd guard ifadesi

**Bulgu:** `commit.md:138` cwd guard `/root/otomaix` veya `/root/otomaix-brain`. Vault cwd'sinde `docs/active/CURRENT.md` yok → 8a, 8b no-op, 8c fallback tetiklenir. İstenen davranış mı, açık yazılmamış.

**Aksiyon:** Yok — çalışıyor, netlik için bir cümle eklenebilir ileride.

### #11 Smoke test commit `git mv` değil `mv` kullanıldı

**Bulgu:** Plan Task 12 Step 5.6 `git mv` istiyordu. Dummy task hiç repo history'ye girmediği için `mv` kullanıldı (`git mv` untracked dosyada çalışmaz). Sonuç-eşdeğer.

**Aksiyon:** Yok — meşru execution sadeleştirmesi, raporlandı.

---

## Plan-task eşlemesi (özet doğrulama)

13/13 task beklenen artifact üretti. Lifecycle transition'lar slash command'lerde birebir doğru kodlanmış:
- `/handoff` TASK.md'ye dokunmaz ✓
- `/commit` HANDOFF.md'ye dokunmaz ✓
- `/review` status değiştirmez ✓
- `/finish-branch` PR archive yapmaz ✓
- `status: archived` move'dan önce ✓

Canonical/ephemeral ayrımı template'lerde korundu (drift riski yok).

---

## Sonuç

- **Kapatılan:** 4 Important (#1 fix, #2-3-4 not eklendi)
- **Açık (devam ediyor):** 7 Minor — bir sonraki `/sync-agents-md project` veya periyodik bakımda ele alınabilir
- **Push-back (kullanıcı reddetti):** 0 (hiçbir bulgu reddedilmedi)

**Push hazır:** Otomaix repo `8aa5ae7` + fix commit (bu commit). Vault hazır (zaten push edildi).
