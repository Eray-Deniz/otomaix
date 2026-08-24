# Codex Adversarial Plan Review — Sektör Bilgi Paketi Plan 1/2 (2026-08-23 → 2026-08-24)

- **Hedef:** `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (Plan 1: runtime çekirdeği, 16 task)
- **Spec:** `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- **Ham kanıt (byte-exact, tee-append):** `~/.claude/logs/otomaix--ffc87809/2026-08-23-sektor-bilgi-paketi-plan.md` (bu makinede, bu kökten — K4b log-evi)
- **Sonuç: APPROVE** (Tur 7; Tur 1 tam review → Tur 2-7 kapanış-doğrulama + derin-pass)
- **Yol seçimi (Eray, 2026-08-24):** "sadeleştir + fix" — F23 kapsam-taşımayla, F22/F24 mekanik fix'le kapandı.

## Bulgu defteri (24 bulgu: 20 high · 4 medium)

| F | Sev | Özet | Akıbet |
|---|---|---|---|
| F1 | high | K-07 damgası iki-aşamalı üretimde taşınmıyor | Tur-2 fixed (opak generation_id taşıma; F14/F15/F17 zinciriyle rafine) |
| F2 | high | İki-kolon damga şeması çelişkili çifte izinli | Tur-2 fixed (MATCH FULL bileşik FK) |
| F3 | high | Aktivasyon dikişi kapıları zorlayamıyor | Tur-2 fixed (kanıt arayüzü; K-103 tekniği bilinçli açık) |
| F4 | high | Rollback sırası veri varken imkânsız | Tur-2 fixed (veri-varken-reddet + teardown sırası) |
| F5 | high | Yeni alanlar public Pydantic şemalarında yok | Tur-2 fixed (şema + roundtrip testleri) |
| F6 | high | Migration runner dağıtılabilir değil | Tur-2 fixed (kanonik glob + cwd bağımsızlığı + ON_ERROR_STOP) |
| F7 | high | n8n bildirimi versiyonlu artefaktsız | Tur-2 fixed (versiyonlu JSON + manuel smoke) |
| F8 | high | Outbox dispatcher/kurtarma sahibi yok | Tur-4 CONFIRMED (sending kirası + süre-dolumu reclaim + korumalı finalize + internal endpoint + n8n schedule) |
| F9 | med | K-08b reparenting deliği | Tur-2 fixed (reparenting yasağı tetikleyicisi) |
| F10 | med | Plan-2 teslim listesi tutarsız | Tur-2 fixed (tek kanonik liste + insert_draft) |
| F11 | med | Recovered bandı yaşam-döngüsü tanımsız | Tur-2 fixed (event_id modeli); F23 devriyle konu bütünüyle Plan 2'ye taşındı |
| F12 | med | Bağlayıcı kabul dalları testsiz | Tur-2 fixed (davranışsal testler; K-45 geri-dönüş satırı Plan 2 etiketli) |
| F13 | high | Task 13 açık K-94/K-101/K-102'yi sessizce karara bağlıyor | Tur-3 CONFIRMED (K-94 opsiyonel mekanizma; K-101/102 açık teknik bağlama + dar-refactor fallback) |
| F14 | high | İstemci-taşınan ham çift sahtelenebilir | Tur-4 CONFIRMED (sunucu-kayıtlı damga + atomik tek-kullanım) |
| F15 | high | Task 10, Task 12'nin tablosuna muhtaç (sıra hatası) | Tur-4 CONFIRMED (generation_stamps → migration 032) |
| F16 | high | Rollback kanıt sözleşmesi belirsiz | Tur-4 CONFIRMED (ayrı RollbackGateEvidence + yönetici onayı) |
| F17 | high | Kullanılmamış geçerli makbuz başka içeriğe takılabilir | **Eray risk-kabulü 2026-08-23** (damga = edited-lineage atfı; içerik-özeti bağlaması bilinçli kurulmadı; yeniden açılma: müşteri/ürünleşme artışı) |
| F18 | high | generation_stamps marka silmeyi kırıyor | Tur-5 fixed (ON DELETE CASCADE + silme testleri) |
| F19 | high | Crash yeniden-teslimi 3-deneme sınırını aşıyor | Tur-5 fixed (claim = kalıcı deneme; attempt_count claim'de artar) |
| F20 | high | Süpürücü aktif üçüncü teslimi terminalleştirebilir | Tur-6 CONFIRMED (aktif kira süpürülmez + yarış testleri) |
| F21 | high | Marka-zorunlu olay API'si paket-seviyesi geçişleri temsil edemiyor | Tur-6 CONFIRMED (iki kapsam sınıfı; lifecycle'da brand_id opsiyonel) |
| F22 | high | Yaşam-döngüsü olay sürüm alanları sınır geçişlerini temsil edemiyor | **Tur-7 CONFIRMED** (olay-türüne özgü şekiller + 5 şekil testi) |
| F23 | high | Recovered bandı marka maruziyetini kanıtlayamıyor | **Tur-7 CONFIRMED — kaldırmayla kapandı (Eray yol seçimi):** recovered + geri-dönüş teslimi Plan 2'ye (atama-geçmişi kanıtı Plan 2 kalemi; metin/karar korunur) |
| F24 | high | Geçiş + olay kaydı atomiklik sözleşmesiz | **Tur-7 CONFIRMED** (olay yazımı geçişle aynı transaction + 2 yön testi) |

## Tur özeti

Tur 1: 13 bulgu (F1-F12 + EXECUTE-NOTES) · Tur 2: F13-F14 (F8 açık kaldı) · Tur 3: F15-F16 (F8/F14 derinleşti) · Tur 4: F17-F19 · Tur 5: F20-F21 · Tur 6: F22-F24 · **Tur 7: yeni bulgu YOK → approve**. Desen teşhisi: tur 2-6 bulgularının tamamına yakını önceki fix'lerin eklediği yeni mekanizmalardan doğdu (lean-plan-contracts dersi); Tur 7 fix'leri bilinçli olarak yeni mekanizma eklemedi.

## Tur-7 EXECUTE-DEVİR hasadı

- EXECUTE-DEVİR: Task 16 Step 3 K-71 eşlemesi netleştirildi (Tur-7 sonrası kozmetik sweep'te UYGULANDI — plan metninde çözüldü)
- EXECUTE-DEVİR: Task 14 commit mesajından "two-way" düşürüldü (UYGULANDI)
- EXECUTE-DEVİR: satır-284 trailing whitespace (UYGULANDI)
- EXECUTE-DEVİR: TASK/HANDOFF tazeleme (approve sonrası aktif katman güncellemesiyle UYGULANDI)

## Kapanış

- `verdict: approve` — unresolved contract-level critical/high: NONE.
- Accepted risk: F17 (Eray tahkimi, plan bağlanan-karar 1'de belgeli); medium residual yok.
- Full plan iterations: 0/3 (yapısal rewrite olmadı; 7 review TURU koştu — tur kanıtı ham log'da).
