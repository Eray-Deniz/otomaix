---
task: sektor-bilgi-paketi-plan2
written: 2026-09-23 (on dördüncü oturum kapanışı)
---

# Resume From

**KUYUMCULUK PAKETİ CANLIDA AKTİF** (`66654971-d90e-4cec-92da-61e723a8ec8f`, sürüm 1, koşu
`kosu-23e19d03…`). Dal `main`'e fast-forward edildi (`11366af`), backend Coolify'da o commit'ten
koşuyor. **Kuyumculuğa atanmış marka YOK** → paket henüz hiçbir üretime girmiyor.

**Sıradaki işler (Eray'ın sırası):**
1. ~~n8n Telegram onay webhook düğümünü bağla~~ **2026-09-25 YAPILDI** (webhook + zamanlayıcı; TASK Decisions Log) —
   Ölçüldü: başlıksız 403 · yanlış başlık 403 · doğru başlık 200. Canlı yedekler oturum scratchpad'indeydi.
2. **Video üretim sistemi değişikliği** (Eray) → ardından **marka ataması** (Task 19 Step 11,
   `Deniz Kuyumculuk (TEST)` → kuyumculuk, arayüzden, Eray'ın gözüyle) + bir paylaşım üretimi →
   **md-17** (`posts.package_id/package_version` + `generation_stamps` okunur).
3. **md-18 (geri alma canlı denemesi):** Claude önerdi → paketin **2. sürümüne** bırak (bugün
   `deaktive-et` tek paketi arşivler, yeniden aktive EDİLEMEZ, kuyumculuk paketsiz kalır).
   **Eray ONAYLADI 2026-09-25.**
**2026-09-25 — paket yeterlilik analizi (13 bulgu, 3 küme):** TASK Open Problems ilk madde; hangi
   kümeden başlanacağı Eray'da. Ölçüm yolu A/B/C canlı paylaşım oluşturmaz.
4. Pilot ölçümleri + koşu raporu (Task 19 Step 12-13) → Task 20 kapanış → `/finish-branch-claude-codex`.

**Bugün (2026-09-23) ne oldu — sırayla:** K-129 metinleri modele hizalandı (dış depo `7fb81c3`,
pin) → "düzeltme turu" yolunun `blocked` koşuya UYGULANAMADIĞI ölçüldü (tasarım boşluğu) → Eray
"spec atla" dedi → **operatör kararları yolu** yazıldı (`operator-karar`, migration 037, `fa52d9d`)
→ 11 açık soru kapandı (26 işlem, 4 hukuki) → Katman-1 tazelendi → taslak → Katman-2 kör örneklem
(8 çağrı, 0,273 USD, paketli seçim 2/4) → onay (252 sn) → hazırlık listesinin iki probu düzeltildi
(`11366af`) → hazırlık tasdiki (md-17/md-18 koşullu) → **aktivasyon** → CTA ≥ 5 kapatıldı (kapı yok)
→ merge + deploy (review'lar Eray kararıyla BİLİNÇLİ geçildi) → yetki belgesi işine ev verildi (G8).

# Verification

| Ne | Taze çıktı |
|---|---|
| Tam takım (`11366af`) | **4841 passed / 0 failed / 407,8 s** (`fa52d9d`'de 4836) |
| Mutasyon | operatör kararları 10/10 · hazırlık düzeltmeleri 4/4; kaynaklar bayt bayt geri döndü |
| Katman-1 | `pytest tests/prompt_regression/ -q` @ `fa52d9d` → 124 passed; tasdik PASS |
| Operatör kararı canlı | `--kuru` rc=0 → yazım rc=0; `activation_eligible`, açık soru 11 → 0; `load_verified_run` yedi kapı geçti |
| Hazırlık | bloklayan 0; `--onayla` rc=0; `aktive-et` rc=0 → paket `active` |
| Canlı API | `/health` 200 (db ok, redis ok); `N8N_TELEGRAM_APPROVAL_SECRET` konteyner değeri dosyayla eşleşiyor (sha256, değer basılmadan); `app.main`/`calendar`/`sector_packages`/`lifecycle` import ok; 5 dk logda hata yok |

**DENENMEYEN / DOĞRULANMAYAN:**
- Takvim ucunun dönem alanı (uç kimlik istiyor, 401) — arayüzden takvim sayfasında görülür.
- md-17 · md-18 (yukarıda) · marka ataması arayüzü.
- Operatör kararları + hazırlık düzeltmeleri + 12 Eylül'den beri hakem görmemiş commit'ler bağımsız
  review/security review GÖRMEDİ (Eray kararı: bilinçli geçildi — TASK Decisions Log).
- `037_down.sql` testle sınanmadı. Operatör metinleri (Claude yazdı, Eray onayladı) üretimde yalnız
  4 konuluk Katman-2'de görüldü.

**TUZAKLAR:**
- **Coolify: `main`'e push dağıtımı TETİKLEMİYOR** (auto-deploy açık ama 150 sn kuyruk boş kaldı —
  ölçüldü). Deploy = Eray Coolify'da düğmeye basar. Watch path yok: üç uygulama da `main`'den.
- `sector_pipeline` motor/denetçi/sentez modülleri konteynerde import EDİLEMEZ (`auditors.py:201`,
  `parents[6]`); operatör CLI'si sunucudaki çalışma ağacından canlı DB'ye karşı koşar (12 Eylül kararı).
- Canlı model çağrısı gerekirse anahtar `/root/.anthropic-key` (0600, 2026-09-23 Eray oluşturdu);
  yalnız süreç ortamına verilir, dosyaya kopyalanmaz. Yerel `backend/.env`'de anahtar YOK.
- Dış depo (`otomaix-sosyal-medya-arastirmasi`) commit'i pin'i bayatlatır → sektör CLI'si reddeder;
  commit ederken pin aynı adımda güncellenir. G8 dış depoda `dfa55f8` olarak commit'lendi, pin ona
  taşındı (`b355822`); dış deponun remote'u YOK (push edilmez). Eray'ın silmeleri DOKUNULMADI.
- Mutasyonda `__pycache__` sil + `python -B`; geri dönüş dosya yedeğiyle.
- `~/.claude/settings.json`'da Eray'ın commit'lenmemiş değişiklikleri — dokunulmadı.

# Risks

- **Paket kuyumculuğa marka atandığı an üretime girer**; canlıdaki kod artık dalın kodu (`11366af`).
  Atama henüz yok, etkisi sıfır.
- Yetki belgesi numarası marka ayarlarında yok → üretimde numarasız "yetki belgesi … mağazamızda"
  satırı çıkabilir (Eray kabul etti). **Evi:** `marka-dna-mimari-karar-dokumani.md` §6.B G8; tarih Eray'da.
- Aktif paket kök perakende rehberini susturuyor (TASK Open Problems, tetik Plan 2 kapanışı).
- Operatör kararı tek seferlik; yanlış bir metnin düzeltilmesi = ret + düzeltme turu (canlıda hiç koşmadı).
- Geçerli iki eski Anthropic anahtarı (`…cV5…mwAA` Telegram bot, `…X0C…BgAA` 27 Temmuz'da
  karantinaya alınmış ama İPTAL EDİLMEMİŞ) Claude geçmiş dosyalarında açık metin — Eray'a iptal önerildi.

# Notes For Claude

- **Kayda bakmadan "yok" deme:** bu oturumda iki kez oldu — "düzeltme turu" yolu (önceki devir notu,
  ölçülmemişti) ve "sırrı yeniden üretelim" (değer 12 Eylül'de üretilmiş, `/root/otomaix-tg-approval.secret`).
  Önce `docs/active/CURRENT.md`, TASK, runbook, security-review grep'le.
- Eray soyut soruya "clarify" / sert tepki veriyor: önce somut örnek ve ham kanıt, sonra tek soru.
- Dar talimatı genişletme (Katman-1 "başla" = yalnız Katman-1); her canlı yazımdan önce ayrı onay.
- Hazırlık listesi ilk kez canlıda koştu; md-03/md-16 düzeltildi. Başka probların da ilk canlı koşumda
  yanlış yere bakıyor olabileceği ÖLÇÜLMEDİ.

# Notes For Codex

Bu dal review'sız merge edildi (Eray kararı). İleride bir review turu açılırsa dikkat listesi:
`operator_decisions.uygula` (karar dosyası dış girdi — işlem kümesi kapalı mı, motorun başka kapısını
aşabiliyor mu) · `runs.record_operator_resolution` (f-string SQL; kolon adları sabit eşlemeden) ·
`readiness` md-03/md-16 değişiklikleri ve parmak izinin operatör kaydını kapsaması · sentez geçici
sahne dizini ve `_HUKUKI_DIL_RE`/`_NICEL_IDDIA_RE` karmaşıklığı (önceki notlar).
