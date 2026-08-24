---
title: Sektör Bilgi Paketi — Runtime Çekirdek Uygulaması
status: active
started: 2026-07-12
last-touched: 2026-08-24
blocked-by: null
source_plan: docs/plans/2026-08-23-sektor-bilgi-paketi.md
---

# Goal

Onaylı plana göre sektör bilgi paketi runtime çekirdeğini kurmak: Tier-1 hiyerarşi satırı +
K6 byte-exact golden kapısı (Faz 0), migration 032 + taksonomi korumaları (Faz 1), tek-kapı
enjeksiyon + K7 damga + preview (Faz 2), atama akışı (Faz 3), elle kuyumculuk pilotu (Faz 4).
Başarı ölçütü: spec §15 kriterleri — özellikle paketsiz markada prompt'ların bit-değişmezliği
(K6) ve pilotta kör değerlendirmede sektörel ayrışma.

# References

- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (Plan 1/2 runtime çekirdeği, `plan-approved`)
- Review: `docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-plan.md` (7 tur; approved)
- Superseded: `docs/specs/2026-07-11-...` + `docs/plans/2026-07-12-...` (2026-08-23 Eray kararı)

# Execution State

- execute_mode: subagent-driven
- execute_started: 2026-08-24 07:05
- execute_start_ref: 5a9d5d4220d0a58db84dc23f274199491d91216b
- ledger_window_ref: 5a9d5d4220d0a58db84dc23f274199491d91216b
- execute_review_log: /root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md
- execute_branch: feat/sektor-bilgi-paketi

# Current Status

**2026-08-24 (beşinci oturum) — PLAN 1 ONAYLANDI (`plan-approved`, Tur 7 `verdict: approve`).**
Eray yol seçimi: "sadeleştir + fix" — F23 kaldırmayla kapandı (recovered bandı + K-45
geri-dönüş teslimi Plan 2'ye; atama-geçmişi kanıtı Plan 2 kalemi; metin/karar korunur),
F22 (olay-türüne özgü sürüm şekilleri) + F24 (geçiş+olay tek transaction) mekanik fix.
Tur 7 kapanış-doğrulaması: F22/F23/F24 CONFIRMED, yeni bulgu YOK. 24/24 bulgu kapalı
(23 fix/devir + F17 Eray risk-kabulü). EXECUTE-NOTES kozmetikleri uygulandı. Repo
HİS-özet review log yazıldı (`docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-plan.md`).
Commit onayı Eray'da; sonrası `/execute-plan-claude-codex`.

**Önceki durum (2026-08-23, dördüncü oturum):** Plan 1 yazıldı, 6 Codex review turu
koştu; 3 açık high bulgu + YOL SEÇİMİ Eray kararı bekliyordu; oturum Eray talebiyle o
noktada kapatıldı. Kapsam kararı: 2 planlı staged split (Eray) — Plan 1 = runtime çekirdeği
(bu oturumda yazıldı: `docs/plans/2026-08-23-sektor-bilgi-paketi.md`, 16 task,
status `plan-draft`, **COMMIT EDİLMEDİ — working tree'de untracked**), Plan 2 =
işletim hattı (hat/motor/komut ailesi/pilot; açık K-84 ailesi kapanınca).
Review: 24 bulgu (F1-F24), 21'i kapandı (19 fix+CONFIRMED · F17 Eray risk-kabulü:
damga = edited-lineage atfı · F20/F21 tur-6 CONFIRMED). **Açık: F22 (yaşam-döngüsü
olay şekilleri sınır durumları) · F23 (recovered bandı atama-geçmişi kanıtı) ·
F24 (geçiş+olay atomikliği)** — üçünün de Codex yapılandırılmış çözümü review
log'unda. Sıradaki adım SEÇİM: (1) sadeleştir+fix (geri-dönüş bandı Plan 2'ye →
F23 yok olur; önerilen) / (2) üçünü düzelt / (3) durdur — Eray henüz SEÇMEDİ;
yeni oturum bu sorudan başlar. Süreç notu: oturum sonunda belirsiz-mesajı onay
sayma ihlali yaşandı (Eray yakaladı; plan dosyasına dokunulmadan durduruldu).

**Önceki durum (üçüncü oturum):** Kayıt üçlemesi: liste Durum sütunu dolu +
spec K-ID satırları "KAPANDI" statüsünde (kardeş-site sweep'li) + Decisions Log
altında tam döküm. Öneriden farklı 3 karar: K-71 (açık sorular aktivasyonu BLOKLAR),
K-45 (çift yönlü bakım bildirimi — Faz 1'e bildirim mekanizması iş kalemi eklendi),
K-56 (olay-bazlı anında uyarı — eşik değil). K-26 genişlemeli kapandı (vade
bildirimi eklendi). **Spec ONAYLANDI (Eray, aynı oturum)** — frontmatter
`spec-approved`. **Üçüncü oturum (aynı gün): sentez deposu sweep borcu kapsam
daraltmasıyla kapatıldı** — tam geriye dönük sweep İPTAL (Eray), yerine kaynak
belgeye statü notu + snapshot yeniden eşitleme. Sırada: `/write-plan-claude-codex`
ile sıfırdan plan.

**Önceki durum (aynı gün, ilk oturum):** Spec yazıldı, Codex review 3 tur SHIP
(11+1 bulgu çözüldü; log: `docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-spec.md`).
Eski spec/plan superseded. Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md`
(status: reviewed-pending-user-approval).

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

- (Bu oturumdan yeni açık problem kalmadı — plan onaylı + commit'li `15db2cf`; sıradaki
  iş yeni oturumda `/execute-plan-claude-codex`. Açık K-ID'ler planın "Karar Kapıları"
  tablosunda yönetiliyor; Plan 2 evi: K-84/K-151/K-152 kapanınca ayrı plan. Aşağıdaki
  iki kayıt önceki oturumlardan, bilinçli açık.)
- Spec'in ~45 kapanış metninin bağımsız kapanış-sweep'i Eray kararıyla ATLANDI
  (2026-08-23 dördüncü oturum, "vazgeçtim plan yazımına geç") — kısmi hafifletme:
  6 Codex plan-review turu spec'i tekrar tekrar okudu, K-ID çelişkisi raporlamadı.
  Yeniden açılma: spec kapanış metinlerinden şüphe doğarsa.
- Denetimin iki orta bulgusu bilinçli açık (Eray kapsamı: yalnız yüksekler): (1) sentez
  deposu commit mesajı `432738b`'deki "35 benzersiz K/R-ID" sayımı yanlış (doğrusu 38;
  git geçmişinde, içerik hatası değil), (2) snapshot Ek C'deki "beş prompt yüzeyi" sayısı
  etiketsiz — küme kapalı değil. (Evi olan "spec seansı" tamamlandı ve K-15 (b) spec'te
  kapandı; snapshot arşiv belgesi statü-notuyla spec'e bağlı. DÜŞÜRÜLDÜ — yeniden
  açılma: arşiv belgesi ileride yeniden canlı girdi olursa, sweep-borcu kararıyla aynı
  koşul.)

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
- **2026-08-23 — Supersede (Eray):** yeni spec TAMAMEN sentez spec-input'undan yazılır; eski
  spec (2026-07-11) ve eski plan (2026-07-12) dikkate ALINMAZ. İkisi de `superseded` işaretlendi.
  Ölçülen çelişki kaydı: politika motoru eski planda yok (K-22=A ile çelişir), kanal envanteri
  eski spec/planda açıkça kapsam dışıydı (K-05=B ile çelişir). Yeni spec sonrası plan sıfırdan.
- **2026-08-23 — Spec-içi teknik kapanışlar (İlke 8: review zinciri doğrular, Eray
  onayı gerekmez):** K-15 (b) = carousel ayrı yüzey değil, caption dalı (taze kod
  ölçümü) · K-01b anahtar sözleşmesi bağlandı (tek normalize modülü, ortak kod yolu) ·
  aday küme kanonik sorgu tanımı · kanal envanteri tasarımı (brand_kit.channels,
  kapalı 4'lü anahtar uzayı, muhafazakâr filtre) · migration rollback sırası ·
  önbellek hükmü (aktivasyon ya anahtara sürüm koyar ya açık invalidate — taze ölçüm:
  bugün kendiliğinden tazeleme yok). Tümü spec Bölüm 17.3'te listeli; Codex review
  sınayacak.
- **2026-08-23 — K-20 = A (kaynak-kanıtlı kapanış):** Katman-1 düzeneği Marka DNA işiyle
  ORTAK; DNA karar belgesi md. 7 hükmü birebir: "iki sistem aynı regresyon koşumunu paylaşır,
  ikinci altyapı kurulmaz" (`marka-dna-mimari-karar-dokumani.md:265-267`). Sentezin açık
  bıraktığı "bağlayıcılık" formalitesi kaynak hükmüyle kapandı. Eray vetosuna açık sunuldu.
- **2026-08-23 — K-21 = C (kaynaksız sayı, düşürüldü):** "22 sektör hedefi" ifadesinin tüm
  araştırma deposunda izi sürüldü — ilk kez 2026-08-11 sonradan-eklenen analiz katmanında
  beliriyor; öncesinde hiçbir kaynak/iş belgesinde/kodda yok (grep tüm depo). Taze ölçümler:
  12 kök sektör (DB) · 22 legacy şablon (templates_data.py: 28 şablonun 22'si) · 22 takvim
  kaydı (2026) — Ç-37 sayı-çakışması hipoteziyle uyumlu. Sonuç: ölçek gerekçesi 22'ye
  dayandırılmaz; 12 kök sektör ölçülmüş gerçek, ≤5 Faz 1 tavanı tahmin etiketiyle kalır
  (kapı yapılmaz), gerçek ölçek pilotta tur süresiyle ölçülür. Eray vetosuna açık sunuldu.
- **2026-08-23 — Karar kapanış turu (Eray, tek tek):** K-118 = kullanıcının somut isteği
  kazanır (ses profili yumuşak yönlendirme; yasak kelimeler mutlak kısıt kalır — öneri kabul) ·
  K-119 = anma satış-dili yasağı kullanıcı isteğini geçersiz kılar; K-118'in TEK istisnası
  (öneri kabul) · K-38 = yeni sürümsüz geri çekme (deaktivasyon) desteklenir; marka paketsiz
  yola döner, olay loglanır (öneri kabul) · **K-71 = BLOKLAR (öneriden FARKLI):** açık
  sorular kapanmadan aktivasyon yapılamaz; K-30 ile çelişmez (K-30 kullanım-sinyali,
  K-71 araştırma-sorusu düzenler) · K-10 = prompt-injection'a özel savunma Faz 1'de
  KURULMAZ (bilinçli risk kabulü; R-09 risk kaydı açık; yeniden açılma: paket/kaynak
  çeşitliliği artınca — öneri kabul) · K-144 = Faz 1'de ayrı hukuk onayı gerekmez (risk
  kabulü; ürünleştirme/platform-kazıma kapsama girerse yeniden açılır — öneri kabul) ·
  K-29 = A: pilot kontrollü TEST MARKASIYLA koşulur (kayıtlı iki marka kuyumcu değil;
  test markası kurulumu Faz 4 iş kalemi — öneri kabul) · K-149 = tur periyodu 6 ayla
  başlar (ilk tur süresi ölçülünce revize edilebilir; acil mevzuat tur-dışı kol —
  öneri kabul) · K-39 = geçmiş post kayıtları geriye dönük DEĞİŞMEZ (damganın kanıt
  değeri korunur — öneri kabul) · K-40 = "değerli bilgi sessizce kaybolmaz" HEDEF'tir,
  bağlayıcı garanti değil (tur başına kanıt yükü doğmaz — öneri kabul) · K-43 = bayat
  atama kaydı KORUNUR (paket geri gelirse marka kendiliğinden paketli çalışır — öneri
  kabul) · K-44 = bayat durum sistem içinde işaretlenir, log/işaret düzeyi (öneri kabul) ·
  **K-45 = ÇİFT YÖNLÜ bildirim (öneriden FARKLI, geniş):** yöneticiye aktif bildirim +
  marka sahibine devre-dışı mesajı ("Bakım çalışmaları nedeniyle gönderileriniz genel
  modda üretilmektedir...") + geri-dönüş mesajı ("Bakım çalışması tamamlandı, sektöre
  özel gönderi modu kullanıma açıldı") — metinler sabit, yüzey seçimi plan işi; Faz 1'e
  bildirim mekanizması iş kalemi eklendi · K-54 = yönetici rolü BÖLÜNMEZ (solo işletim;
  ölçek gelince yeniden açılır — öneri kabul) · K-69 = 20 maddelik hazırlık listesi ilk
  aktivasyon öncesi KAPI; otomatik ön-kontrol + tek onay; K-70 sorumlusu = operatör
  (öneri kabul) · **K-26 = sektör başına periyot alanı + VADE BİLDİRİMİ (öneri +
  genişleme):** vadesi dolan paket yöneticiye bildirilir (K-45 mekanizmasıyla aynı
  altyapı; Faz 1 iş kalemi) — Eray sorusu üzerine ölçüldü: spec'te vade uyarısı yoktu,
  bu kararla eklendi · K-72 = taslak reddi otomatik düzeltme turu BAŞLATMAZ; yeni koşuyu
  yönetici elle tetikler (öneri kabul) · K-73 = acil güncellemede tam tur ZORUNLU DEĞİL;
  şart: resmî kaynak kanıtı + iki denetçinin dar hızlı doğrulaması; onay kapısı kalkmaz
  (öneri kabul) · **K-56 = OLAY-BAZLI anında uyarı Faz 1'de kurulur (öneriden FARKLI,
  Eray yeniden çerçeveledi):** eşik/oran alarmı değil — sektörel modda üretilmesi gereken
  post paketsiz üretilirse yöneticiye derhal bildirim (K-45/K-26 mekanizmasıyla aynı
  altyapı); alarm sorumlusu = yönetici (rol sorusu da kapandı) · K-77 = denetim için
  yeni kimlik/yetki modeli kurulmaz, lokal tek kullanıcı (öneri kabul) · K-79 = denetçi
  izolasyonu + aynı-girdi hafif teknik garanti: komut ailesi kod düzeyinde zorlar
  (öneri kabul) · K-80 = tekrar-üretilebilirlik damgası ZORUNLU (model/sürüm/tarih/girdi
  özeti her artefaktta — öneri kabul) · K-81 = denetçi çıktısına otomatik biçim kontrolü
  EVET (mekanik, sentez öncesi — öneri kabul) · K-150 = tek geçerli raporla sentez
  ENGELLENİR; eksik denetçi yeniden koşulur (öneri kabul) · K-82 = yarım koşu
  "tamamlanmadı" işaretlenir, dosya ezilmez; yeniden koşum yeni deneme kimliği alır
  (K-83'ü de kapatır — öneri kabul) · K-105 = ara-pencere okuyucu testi zorunlu DEĞİL,
  isteğe bağlı plan kalemi (pencere emniyetli + K-56 uyarısı — öneri kabul) · K-120 =
  çelişki "boş alanın özel temsili" ile çözülür: sözleşmeye resmî `içerik-önerilmez`
  değeri; kontrol bilinçli-boşu geçirir (öneri kabul) · K-121 = kırpma sırası
  mevzuat-öncelikli ALTILI sıra; mevzuat/güvenlik asla ilk kırpılan olmaz (öneri kabul) ·
  K-122 = churn koruması BENİMSENİR: yeni-zayıf öğe sırf yeniliğiyle doğrulanmışı
  çıkaramaz (öneri kabul) · K-123 = "güçlü kaynak" TANIMLANIR; çekirdek: kaynağın aslı
  (resmî/birincil) + tarihli güncellik; tam metin sözleşme revizyonu (öneri kabul) ·
  K-124 = çıkarma kanıt eşiği: normal bilgide ≥1 doğrulanmış kanıt satırı;
  mevzuat/güvenlikte + iki denetçi mutabakatı, yoksa açık soruya düşer (öneri kabul) ·
  K-126 = tek-resmî-kaynak istisnası TANIMLANIR: resmî kaynak (K-123) + en az bir
  denetçinin canlı URL doğrulaması (öneri kabul) · K-127 = asgari kaynak tabanı 2;
  1'e düşerse koşu durur, karar yöneticide (öneri kabul) · K-129 = mevzuat/güvenlik
  alan listesi SABİT: yasaklar-ve-hassasiyetler tamamı + mevzuat/tarih/sayı içeren tüm
  iddialar (öneri kabul) · K-135 = paketlere yazma yalnız operatör + koşu yüzeyi —
  bağlayıcı kural; ikinci yazma yüzeyi ancak açık kural değişikliğiyle (öneri kabul) ·
  K-136 = günlüklerde sır tutulmaz; günlük yazıcısına maskeleme süzgeci, hata mesajları
  dahil (öneri kabul) · K-137 = araç kimliği denetçi ortamına sızmaz — yapısal garanti,
  anonimleştirme kod düzeyinde (öneri kabul) · K-16 = paket içeriği iç kullanım +
  yönetici; müşteriye KAPALI (öneri kabul) · K-138 = araç↔rapor eşlemesi kalıcı
  KAYDEDİLİR; körlük erişimle korunur (öneri kabul) · K-139 = ham katman + eşlemeyi
  yalnız operatör/yönetici okur (öneri kabul) · K-140/K-141 = ham katman + paket
  sürümleri SÜRESİZ saklanır; yeniden bakış: hacim/KVKK sinyali (öneri kabul) · K-142 =
  taslaklara ayrı saklama kuralı YOK, onlar da kalıcı; K-143 hiç doğmaz (öneri kabul) ·
  K-31 = pilot bitişi ÖN KOŞUL modeliyle; takvim süresi tanımlanmaz, şartlar K-32…K-37'de
  (öneri kabul) · K-19 = alt sektör teyit bileşeni onboarding + marka ayarlarında,
  mevcut sektör seçiminin yanında; yeni yüzey yok (öneri kabul). **TUR TAMAMLANDI:
  45/45 karar kapandı** — 41 öneri kabul (2'si genişlemeli: K-26 vade bildirimi,
  K-69+K-70), 3 öneriden farklı (K-71 bloklar · K-45 çift yönlü bildirim · K-56
  olay-bazlı anında uyarı), 1 öneri+yeniden-çerçeveleme (K-56'da eşik→olay). Ek
  kapanışlar: K-70, K-83, K-143 (bağlı kararlar kendiliğinden çözüldü) ve K-57
  (alarm sorumlusu = yönetici; K-56 kapanışının "rol sorusu da kapandı" hükmüyle —
  sweep hazırlığında tespit edilip 2026-08-23 üçüncü oturumda bu listeye eklendi).
- **2026-08-23 — Spec ONAYLANDI (Eray):** karar turu kapanışının ardından frontmatter
  `reviewed-pending-user-approval` → `spec-approved`. Plan `/write-plan-claude-codex`
  ile SIFIRDAN yazılacak (eski plan superseded).
- **2026-08-23 (dördüncü oturum) — Plan yapısı: 2 planlı staged split (Eray):** Plan 1 =
  runtime çekirdeği ("paketi TÜKETEN her şey"), Plan 2 = işletim hattı ("paketi ÜRETEN ve
  AKTİVE EDEN her şey"); tek arayüz DB sözleşmesi + kanonik teslim listesi. Gerekçe: motor
  ön-koşul kararları (K-84/K-151/K-152) açıkken detay-plan karar uydururdu.
- **2026-08-23 (dördüncü oturum) — F17 risk kabulü (Eray):** K-07 damgası "üretim-oturumu
  atfı"dır (edited lineage) — bayt-bayt içerik kanıtı iddia edilmez (caption düzenlenebilir);
  aynı-marka kullanılmamış makbuz ikamesi kabul edilen risk; yeniden açılma: müşteri
  sayısı/ürünleşme artışı. Plana işlendi (bağlanan teknik karar 1).
- **2026-08-23 (dördüncü oturum) — Plan-içi teknik bağlamalar (İlke 8, review zinciri
  sınadı):** K-07 bileşik FK + opak generation_id · K-08a TEXT · K-08b DB trigger +
  reparenting yasağı · paket okuması önbelleksiz · Katman-1 = Anthropic istemci kesişimi ·
  bildirim = transactional outbox + versiyonlu n8n workflow · K-101/K-102 tek-transaction
  (dar-refactor fallback'li) · K-94 mekanizma-var-kural-açık (opsiyonel alan).
- **2026-08-23 — Sentez deposu sweep borcu KAPSAM DARALTMASIYLA kapandı (Eray):**
  kapanan kararların kanonik kaynağa (araştırma deposu, Bölüm 17 + Ek B + gövde)
  geriye dönük işlenmesi İPTAL — spec onaylandıktan sonra arşiv belgesini yeniden
  yazmak (51 satır + ~30 kalan gövde düzenlemesi + ~47 Ek B kaydı + Codex doğrulama
  turu) risk/fayda dengesini aşıyor; "süreç ağırlığı ≈ risk ağırlığı". Başlanan
  düzenlemeler (51 satır + ~35 gövde) commit edilmeden geri alındı; baseline sha
  doğrulandı. Yerine: kaynak belgeye statü notu (belge başı + Bölüm 17 başlığı —
  51 kapanışın ID listesi + "çelişkide spec esastır" hükmü) + snapshot yeniden
  eşitleme. Yeniden açılma koşulu: arşiv belgesi ileride yeniden canlı girdi olursa.
- **2026-08-24 — Yol seçimi: "sadeleştir + fix" (Eray) + Plan 1 ONAYI:** F23'ün konusu
  (recovered bandı + K-45 geri-dönüş mesajının teslimi) Plan 2'ye taşındı — gerekçe:
  tetiği (reaktivasyon) yalnız Plan 2 komut ailesinden koşulabilir, Plan 1 ömründe
  recovered durumu hiç doğamaz; K-45 kararı ve sabit metinler KORUNUR, Plan 2 kalemi
  atama-geçmişi kanıtını da içerir. F22 = olay-türüne özgü sürüm şekilleri (sentinelsiz),
  F24 = olay kaydı geçişle aynı transaction. Tur 7 approve → `plan-approved`.
- **2026-08-21 — Denetim + sweep (Eray: "yüksek bulguları giderelim" + commit onayı):**
  Codex denetiminin iki yüksek bulgusu sentez deposunda giderildi (commit'ler
  `8e298eb → c380e37`); dört kapanışın statü/kapsam izleri gövdeye işlendi, karar-durumu
  ölçümü tazelendi (162 = 153 açık + 9 kapalı). Kapanış 4 turlu Codex doğrulamasıyla
  CONFIRMED. Orta bulgular bilinçli açık bırakıldı (Open Problems'ta).
