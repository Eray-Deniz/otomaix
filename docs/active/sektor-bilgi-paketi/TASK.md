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
**Aynı gün ikinci oturum:** sentez commit'lerinin Codex denetimi koşuldu (4 bulgu: 2 yüksek,
2 orta); iki yüksek bulgu (bayat karar statüleri + K-05 kapsam tersliği) 4 commit'lik gövde
sweep'iyle giderildi ve 4 turlu Codex kapanış-doğrulaması **CONFIRMED** ile kapandı; snapshot
yeni kaynak commit `c380e37` üzerinden yeniden alındı (bayt-özdeşlik sha ile doğrulandı).
**Sıradaki iş: yeni spec'in yazımı** (`docs/specs/2026-08-21-sektor-bilgi-paketi.md`) —
seans sırası ve yöntem HANDOFF.md'de. Eski spec/plan sentezden habersizdir; ilişkileri
(devralma / supersede) spec seansında netleşecek, durum geçişi Eray'ındır.

# Open Problems

- Eski plan (2026-07-12) ↔ sentez uyumu doğrulanmadı — özellikle politika motoru artık
  Faz 1'de (K-22=A); eski planın motoru kapsayıp kapsamadığı ölçülmedi.
- K-21 netleştirmesi: 22 · 12 · ≤5 rakamlarının neyi saydığı tanımsız; motor ölçek gerekçesi
  buna dayanıyor (Eray'a sorulacak).
- Denetimin iki orta bulgusu bilinçli açık (Eray kapsamı: yalnız yüksekler): (1) sentez
  deposu commit mesajı `432738b`'deki "35 benzersiz K/R-ID" sayımı yanlış (doğrusu 38;
  git geçmişinde, içerik hatası değil), (2) snapshot Ek C'deki "beş prompt yüzeyi" sayısı
  etiketsiz — küme kapalı değil (K-15 (b) açık). Spec seansında Ek C maddesi yazılırken
  etiketlenerek çözülür.

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
- **2026-08-21 — Denetim + sweep (Eray: "yüksek bulguları giderelim" + commit onayı):**
  Codex denetiminin iki yüksek bulgusu sentez deposunda giderildi (commit'ler
  `8e298eb → c380e37`); dört kapanışın statü/kapsam izleri gövdeye işlendi, karar-durumu
  ölçümü tazelendi (162 = 153 açık + 9 kapalı). Kapanış 4 turlu Codex doğrulamasıyla
  CONFIRMED. Orta bulgular bilinçli açık bırakıldı (Open Problems'ta).
