---
title: Sektör Bilgi Paketi — Runtime Çekirdek Uygulaması
status: proposed
started: 2026-07-12
last-touched: 2026-08-21
blocked-by: null
---

# Goal

Onaylı plana göre sektör bilgi paketi runtime çekirdeğini kurmak: Tier-1 hiyerarşi satırı +
K6 byte-exact golden kapısı (Faz 0), migration 032 + taksonomi korumaları (Faz 1), tek-kapı
enjeksiyon + K7 damga + preview (Faz 2), atama akışı (Faz 3), elle kuyumculuk pilotu (Faz 4).
Başarı ölçütü: spec §15 kriterleri — özellikle paketsiz markada prompt'ların bit-değişmezliği
(K6) ve pilotta kör değerlendirmede sektörel ayrışma.

# References

- Spec: `docs/specs/2026-07-11-sektor-bilgi-paketi.md`
- Plan: `docs/plans/2026-07-12-sektor-bilgi-paketi.md`
- Review: `docs/reviews/codex/2026-07-12-sektor-bilgi-paketi-plan.md` (12 tur; approved)

# Current Status

Plan onaylandı (plan-approved, 2026-07-12), henüz başlanmadı.

**2026-08-21 güncellemesi:** İki hakem mimari belgesinin sentezi tamamlandı ve kanonik girdi
snapshot olarak alındı (`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`).
**Sıradaki iş: yeni spec'in yazımı** (`docs/specs/2026-08-21-sektor-bilgi-paketi.md`) —
seans sırası ve yöntem HANDOFF.md'de. Eski spec/plan sentezden habersizdir; ilişkileri
(devralma / supersede) spec seansında netleşecek, durum geçişi Eray'ındır.

# Open Problems

- Eski plan (2026-07-12) ↔ sentez uyumu doğrulanmadı — özellikle politika motoru artık
  Faz 1'de (K-22=A); eski planın motoru kapsayıp kapsamadığı ölçülmedi.
- K-21 netleştirmesi: 22 · 12 · ≤5 rakamlarının neyi saydığı tanımsız; motor ölçek gerekçesi
  buna dayanıyor (Eray'a sorulacak).
- Sentez deposunun son üç commit'i bağımsız denetimden geçmedi (HANDOFF Resume From/1).

# Decisions Log

> ⚠️ Aşağıdaki `K-xx` ID'leri sentez belgesinin (snapshot Bölüm 17) uzayıdır — eski spec'in
> `K1–K7` gündemiyle karıştırılmaz. Kanonik kapanış kayıtları snapshot **Ek B**'dedir.

- **2026-08-19 — Spec'e geçiş hükmü (Eray):** "Spec yazımı başlayabilir; Bölüm 17'deki ürün
  kararları ilgili sözleşme kesinleşmeden kapatılmalıdır." Karar uydurulmaz; açık karar K-ID
  atfıyla taşınır.
- **2026-08-21 — K-22 = A (Eray):** politika motoru Faz 1'e girer. Belge önerisi (B) TERSİYDİ;
  motor kararları (K-23 · K-24 · K-25 · K-133) Faz 1 spec gündemine girdi.
- **2026-08-21 — K-27 = A (Eray):** yönetici turu Claude Code komut ailesinden koşulur; panel
  geliştirilmez. Komut ailesinin varlığı doğrulanmadı — spec seansında ölçülür.
- **2026-08-21 — K-30 = A (Eray):** gerçek kullanım sinyali beklenmez; aktivasyon Faz 1'de
  (risk kabulü). K-29'dan bağımsız.
- **2026-08-21 — K-05 = B (Eray):** kanal envanteri Faz 1'de kurulur. Belge önerisi (A)
  TERSİYDİ; Marka DNA işiyle sınır spec'te çizilecek.
