---
task: sektor-bilgi-paketi-plan2
written: 2026-09-25 (on altıncı oturum kapanışı)
---

# Resume From

**Kuyumculuk paketi canlıda aktif** (`66654971-d90e-4cec-92da-61e723a8ec8f`, sürüm 1), **kuyumculuğa atanmış
marka YOK** → hiçbir üretime girmiyor. Paket 25 Eylül sınavında **yetersiz** çıktı (0. madde: kural koyamıyor).

**Bu oturumun ürünü: 0. maddenin tasarımı yazıldı ve ONAYLANDI** —
`docs/specs/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md` (`spec-approved`, Codex 5 tur, son tur
`approve`, 18:11–18:43 UTC). Eray'ın yedi kararı (K-A..K-G) ve dört hakem turunun düzeltmeleri notun §2, §3, §7'sinde.
**Uygulama BAŞLAMADI, kod DEĞİŞMEDİ.**

**Sıradaki iş (Eray "başla" demedi; sor):** `/write-plan-claude-codex` ile uygulama planı → uygulama (kod: iki
blok + `resolve_post_type` + `kural_uyumu` kapısı + iki migration; paket 2. sürümü: anma günleri, `sektor_gercekleri`,
ton bölünmesi, takvim temaları kopya temizliği) → `KALIBRASYON-2.md` yazılır → sınav tekrarı (ücretli, ~1,6 USD tahmin,
Eray onayı). **Eray'ın diğer sırası değişmedi:** video üretim sistemi değişikliği → marka ataması (Task 19 Step 11)
→ md-17 → pilot ölçümleri → Task 20 → `/finish-branch-claude-codex`. md-18 paketin 2. sürümünde.

**Bugün (2026-09-25, 16. oturum) ne oldu:** Eray üç soruyu cevapladı (istek her kuralın üstünde · anma günleri
pakete+takvime · zorunlu/seçmeli ayrımı) → K-119 iptal → kalıp seçimi analizi (19 çıktı elle okundu) → gönderi türü
tasarımı (özel gün → kod · ürün modu → kod varsayılanı + model `bilgi` istisnası · genel mod → model) → sektör
şablonu reddi (vault + canlı DB ile ölçüldü) → tasarım notu → hakemin unuttuğu 7 alan nota işlendi → Codex 5 tur:
F1 critical (istek yasal sınırları da ezer) → **Eray: şimdilik her kuralın üstünde, onay anında çiğnenen kural
gösterilir** → kural-kural zorunlu beyan (`kural_uyumu`) + kod kapısı + "sessiz ihlal 0" sınav kapısı.

# Verification

| Ne | Taze çıktı |
|---|---|
| Codex zinciri | 5 tur rc=0; Tur 1 needs-attention (1C+3H) → Tur 5 approve; ham log `~/.claude/logs/otomaix--ffc87809/2026-09-25-feat-sektor-bilgi-paketi-plan2.md` |
| Notun kod/yol atıfları | `prompt_builder.py:154/366/390-398`, `sector_packages.py:487`, `generation_stamps` kolonları, `schema_version` kolonu, `ADMIN_NOTIFIED_EVENTS` — hepsi grep/sed ile doğrulandı |
| Takvim ↔ paket | canonical DB: takvim 25 gün, paket 16; pakette olup takvimde olmayan 0; takvimde olup pakette olmayan 9 (18 Mart, 10 Kasım dâhil); yıllık n8n işi 18 Mart + 10 Kasım üretiyor |
| Şablon kullanımı | vault: 22 sektör şablonu 2026-04-15 terk; DB 81 gönderi: ürün modu 39 · genel 36 · özel gün 6 · sektör şablonu 6 (terk öncesi) |
| Kalıp kullanımı (sınav, elle) | 19 paketli çıktı: kanca kalıbı açık 1 · CTA kalıbı açık 4 (Claude okuması, hakem ölçümü değil) |
| Tam takım / Katman-1 | **KOŞULMADI** (kod değişmedi) |

**DENENMEYEN / DOĞRULANMAYAN:**
- Notun hiçbir mekanizması kodda yok: `resolve_post_type`, `kural_uyumu` kapısı, iki blok, şema-2 okuyucu, iki migration.
- "Sessiz ihlal" oranı (model `uyuldu` deyip çiğner mi) ÖLÇÜLMEDİ — sınav tekrarında kapı.
- Şablon "link yoksa CTA ekleme" kuralı ile paket CTA çatışması canlıda ölçülmedi (sınav şablonsuz koştu).
- Kota kapısı bayat okuma veriyor (17 %/3 %, 4 saat eski); beş tur sorunsuz koştu, gerçek kalan kota bilinmiyor.
- Önceki devirden: zamanlayıcının başlıklı onay çağrısı canlıda hiç koşmadı; madde 16 kanal satırı; 11(b); S06 ret
  mesajı arayüzde; "ysatisfa"; kısa video/fikir yüzeyi ölçülmedi.

**TUZAKLAR:**
- Hakem turu: `run_codex_scan` arka planda (`run_in_background`, `CSS_CALL_TIMEOUT=1200s`), prompt Write tool ile
  `~/.claude/tmp/<log-basename>.prompt`'a, SETUP fence her turdan önce (dosya trap'le silinir). Substrat eski
  review/migration/test dosyalarını "sır" diye dışlıyor (yanlış pozitif sınıfı, promptta not düşüyor) — bulgu değil.
- Kapanış turundan ÖNCE sınıf süpürmesi: kaldırılan alan adını grep'le, "her X kimlik alır" kümesini KODDAN say
  (F1 bu yüzden 4 tur sürdü — memory `feedback_close_the_class_not_the_variant`).
- Katalogdan sayma: `templates_data.py` 28 şablon tanımlı ama 6'sı canlı; önce vault, sonra DB (memory
  `feedback_count_from_usage_not_catalog`).
- Coolify: `main`'e push dağıtımı TETİKLEMİYOR; Eray düğmeye basar. Canlı model anahtarı `/root/.anthropic-key`.
- Ücretli koşu öncesi tutar + açık onay (Eray 2026-09-25: "sizin hatanızın bedelini ödeyemem").

# Risks

- **K-A (şimdilik):** kullanıcı isteği mevzuat yasaklarını, kişisel veriyi ve uydurma yasağını da ezer; azaltıcı
  yalnız onay anında ifşa. Eray tetik/tarih vermedi; canlıya müşteri alınmadan yeniden değerlendirme Claude'un notu.
- Paket bu hâliyle markaya atanırsa sınavdaki kritik hatalar gerçek paylaşımda çıkabilir — **atama 0. madde
  uygulanmadan yapılmamalı** (Claude risk notu; Eray'a söylendi).
- Paketli Katman-1 fixture'ları uygulamada yeniden temellenecek (kasıtlı); paketsiz yol bayt-bayt korunur (kapı).
- Önceki devirden: yetki belgesi numarası (G8) · kök perakende rehberi susuyor · iki eski Anthropic anahtarı iptal
  edilmedi.

# Notes For Claude

- **Eray'ın sorduğunu cevapla; kısa tut; kanıtla gel.** Bu oturumda "madde ne demek", "seçmeli olunca hiç seçmeyebilir
  mi", "türü kim belirleyecek", "hangi mod" soruları geldi — her biri ölçümle cevaplandı, öneri menüsü değil.
- Sektör şablonu önerme; tür şablonun değil gönderinin özelliği (K-F). Kullanıcıya tür seçtirme yalnız sınav tür hatası
  gösterirse.
- `uyarilar` alanı YOK — `kural_uyumu` (kural başına karar). Bu adı kullanan eski cümle görürsen tarihçedir.
- Commit: HANDOFF/TASK/spec oturum sonunda Eray onayıyla tek commit'te (bu dosyanın commit'i); push EDİLMEDİ.

# Notes For Codex

Uygulama planı review'ında dikkat: (1) `resolve_post_type` üç dal × gün türü × ürün türü matrisi; (2) `kural_uyumu`
kapısı: kimlik tamlığı + karar değeri + kanıt alanları + gün bloğu `G*` kimlikleri (üretilmiş matris); (3) şema-2
okuyucu geriye uyumlu (sürüm 1 dokuz alanla okunur), geri dönüş tabanı runbook satırı + `package_read_error` testi;
(4) paketsiz yol bayt-bayt (Katman-1); (5) `KALIBRASYON-2.md` sınavdan önce sabit, eski ölçüt aynen yanında.
