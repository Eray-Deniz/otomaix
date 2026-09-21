---
task: sektor-bilgi-paketi-plan2
written: 2026-09-21
---

# Resume From

**SIRADAKİ İŞ, TEK CÜMLE: Grup 3'ün KOD TARAFINI indir — brief-doctor 9 sütunlu Bölüm C'yi,
kapsama kuralını, `[C: …]` geri bağlantısını ve `kaynak-bulunamadı` değerini tanısın; EK-M ve
motor kabul eşlemesi peşinden; iki sözleşme + pin + testler aynı commit'te.** Tasarım belgesi:
`/root/otomaix-sosyal-medya-arastirmasi/_sablon-duzenleme.md` (Grup 3 bölümü + "Ek — Sonraki
aşamalara etki analizi" §2.1-2.3 ve §3 senaryo tablosu). Kalem listesi TASK.md Open Problems
ilk maddede. **Araştırma bu iş inmeden ALINMAZ.**

**Bugün ne oldu:** "Raporlar kötü" hipotezi ölçüldü ve yön değiştirdi. Altı raporun dördü kalıp
düzeyinde ve sektöre özgü; kırılma, kalıpların Bölüm C'de satırı olmaması (denetçi-1 satır 10-11:
"üç kaynakta da var" ama `tekil`). Eşik kararı belirtiye bakıyordu, PARKA alındı. Şablon üçüncü
revizyona çekildi, brief yeniden türetildi. Eray: "orta yol yok, dosyadakileri yapıyoruz."

**Dosya durumu:**
- Dış depo: `_SABLON.md` DEĞİŞTİ (346 → 466 satır, commit yok; önceki sürüm `.SABLON.md.d9dc289.bak`),
  `Kuyumculuk/kuyumculuk.md` yeniden türetildi (git'te takip DIŞI, önceki gibi), `_sablon-duzenleme.md`
  takip dışı (karar kaydı + Codex eki). Koşu klasörleri `.gitignore`'da.
- Monorepo: TASK.md + bu dosya değişik, commit yok; `1596384` PUSH EDİLMEDİ.

# Verification

| Ne | Taze çıktı |
|---|---|
| `tests/test_contract_pin.py` | **1 failed / 32 passed** — `_SABLON.md` hash uyuşmuyor. BEKLENEN: pin Grup 3 commit'iyle bump edilir |
| Ayrıştırıcı, 9 sütun | `_ayristir`+`_c_iddialari` doğrudan çağrıldı: Kaynak-3 orijinal **42 iddia**, `destek`+`yer` eklenince **0** |
| Ayrıştırıcı, 7 sütun + `URL=kaynak-yok` satırı | **43 iddia**, satır çözülüyor (kapsama kuralı için kod şart değil; sütunlar için şart) |
| Şablon 2-5 ↔ brief 2-5 | `diff` boş, birebir |
| Codex şablon aktarım kontrolü | 1. tur 4 işlevsel tutarsızlık (mutlak kural↔kaynaksız kayıt · kanca bağımlılık yolu · kaynak kapsamı · URL istisnası) — dördü düzeltildi; 2. tur **itiraz yok** |
| Tam takım | BU OTURUMDA KOŞMADI (kod değişmedi) |

**DENENMEYEN / DOĞRULANMAYAN:**
- Yeni şablonla hiçbir rapor alınmadı; LLM'lerin `[C: …]` ve 9 sütunu doğru yazıp yazmayacağı ÖLÇÜLMEDİ.
- `kaynak-bulunamadı` değerine bugünkü brief-doctor'un ne yaptığı (not mu, eleme mi) ÖLÇÜLMEDİ —
  şablon "not düşer, elemez" diyor, bu Grup 3'ün yazacağı davranıştır, mevcut davranış değil.
- Grup 3'ün süresi ÖLÇÜLMEDİ; altı kalem, dört sözleşme/kod yüzeyi.
- `yazim` · `katman2` · `onay` · `aktive-et` ayakları bu dalda hâlâ koşmadı; security-review borç;
  paket tablosu 0 satır.

**TUZAKLAR:**
- Şablonu commit edip pin'i bump etmek ama ayrıştırıcıyı değiştirmemek = tur açılır, 0 iddia, sentez
  fail-closed. Sıra: ayrıştırıcı → sözleşmeler → pin, TEK commit.
- Koşu `kosu-7705437723ce4730ac0ae70cf6986bc8` hâlâ `calisiyor`; motor koşturulmadı; sentez klasörü
  dolu, o koşuda sentez tekrar koşmaz. Yeni tur = yeni koşu.
- Kaynak-1..6 ESKİ sürümün çıktısıdır (7 sütun); yeni hatta girdi olarak KULLANILMAZ, test verisi.
- Kaynak-4/5/6 ile açılan `kosu-11391477…` sahipsiz: denetim çıktısı var, sentez ve defter kaydı yok.

# Risks

- Yeni şablon LLM'e daha çok yapısal yük bindiriyor (9 sütun + geri bağlantı + iki muafiyet değeri);
  ilk turda brief-doctor notu artabilir. Kapı notu eleme değildir, ama sentez girdisi kirlenir.
- Kanıt kapısı içerik alanında `öneri` desteğini kabul ediyor (Eray onaylı Grup 2); tarihsiz ajans
  blogu "öneri" sayılırsa zayıf kaynaklı kalıp mutabakatla girer. Kopyalama koruması ayrı bayraklarda.
- "Aynı dış kaynak → 3-3 sayılır" kararı (Eray) araştırma-arası mutabakatı kanıt sayısından ayırmıyor;
  bilinçli, kayıtlı.

# Notes For Claude

- Eray bugün iki kez sinirlendi: (1) önceki oturumda brief'e yargıları yazmadan tur koşturulmuştu,
  (2) "neredeyse bitiriyorduk, yeniden mi başlıyoruz" — cevap: HAYIR, hat duruyor; değişen araştırma
  girdisinin sözleşmesi. Kısa yol (eşik gevşet) ve orta yol (sütunsuz) önerildi, ikisini de REDDETTİ:
  "orta yol yok, direkt dosyadakileri yapıyoruz." Sonraki oturum seçenek sunmasın, Grup 3'ü indirsin.
- Kararlar sorulmayacak: Grup 1-2 onaylı, aynı-kaynak 3-3 karar, eşik parkta. Tek açık karar: Grup 3'ün
  evi (Task 19 ek adım mı ayrı task mı) — süre ölçülünce sor.
- İlke 9: şablon başlığındaki "42 → 0" ölçümü taze; başka sayı yazma.
- Codex Ek'i (dosya §"Ek") ayrı analizdir, dokunulmadı; §3 senaryo tablosu test listesi olarak kullanılır.

# Notes For Codex

Bu oturumda Codex hakem olarak koşmadı; Eray Codex'i dışarıdan koşturup üç bulgu setini getirdi
(ilk itiraz, 8 bulgu, etki analizi) — hepsi işlendi. Grup 3 kodu inince `/review-claude-codex`
zorunlu (ayrıştırıcı + motor değişiyor); `/security-review-claude-codex` dalda hâlâ borç.
