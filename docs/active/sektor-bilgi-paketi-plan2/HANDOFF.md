---
task: sektor-bilgi-paketi-plan2
written: 2026-09-22
---

# Resume From

**SIRADAKİ İŞ, TEK CÜMLE: Grup 3 kodu review'dan geçti ve KAPANDI (attempt-1 dual → düzeltme `fceb2d2`
→ attempt-2 kapanış dual, unresolved C/H = 0); sırada Eray'ın üç araştırmayı YENİ brief'le
(`Kuyumculuk/kuyumculuk.md`, üçüncü revizyon) alması → tek tur.** Push EDİLMEDİ. Kalem listesi ve ilk
turda ölçülecekler TASK.md Open Problems ilk iki maddede; kararlar Decisions Log "Grup 3 — kod tarafı".

**Bugün ne oldu (2026-09-22):**
1. `/review-claude-codex` (dual) koştu: 2 high · 3 medium · 4 low. İki high'ı da orkestratör kendi probuyla
   doğruladı: **H1** zorunlu `[C: n]` etiketi tekrar/adet anahtarına giriyordu (özdeş beş CTA farklı etiketle
   `gecti/0 not`); **H2** eski 7 sütunlu rapor 0 iddiayla tura giriyor, denetçi anınca motor çoğunluğa
   sayıyordu ("eski raporlar yeni hatta girmez" hükmü kodda zorlanmıyordu).
2. Eray kararı: H1 + H2 (+ M1) düzeltilir → kapanış turu → üç araştırma. M2 (Katman-1 tasdiği ölü koşuda
   yazılabilir; hakemler çelişti) **Eray kararı: BIRAK** (örnekli açıklama sonrası; kodun belgeli gerekçesi) — `accepted_risk`.
3. Düzeltme `fceb2d2` (TDD: 10 test önce kırmızı, 10/10 mutasyon yakalandı): `_madde_anahtari` etiketi
   düşürür; `iddiasiz_kaynaklar` tek üretici, paket kurucu ve sentez karışık kümeyi REDDEDER (süzmez);
   motor yalnız iddia bağı taşıyan kaynağı sayar (üretimde no-op — ayrıştırıcı zaten eşitlik zorluyor,
   savunma katmanı); üç `RunAlreadyTerminal` sarması + `ALAN_HATALARI`; tekrar notu `{ad}` literali gitti.
4. Kapanış turu (attempt-2, dual, sözleşme hash'i EŞİT): dördü de KAPANDI; Codex bulgu yok; Claude 6 low
   (N1-N6). N1 · N2 · N4 · N5 · N6 gönüllü düzeltildi (belge/test/log; **bağımsız hakem görmedi**), N3
   `accepted_risk`.
5. Commit'ler: `1e9a133` docs(reviews) attempt-1 · `fceb2d2` fix(hat) H1+H2+M1+L4 · `317664f` fix(hat) gönüllü low
   düzeltmeleri · son docs commit'i kapanış raporu + TASK/HANDOFF (bu dosya). Push EDİLMEDİ.

**Dosya durumu:**
- Dış depo: `34a34db` (iki sözleşme; pin ona bağlı). Eray'ın 41 silinmiş dosyası + 3 yeni (`.bak`, `sentez/`)
  çalışma ağacında hâlâ commit'lenmemiş — bana ait değil, dokunulmadı.
- Brief `Kuyumculuk/kuyumculuk.md`: bilinçli olarak depo dışı (`.git/info/exclude`), 2-5. bölümleri şablonla
  BAYT BAYT aynı (bugün ölçüldü); sürümü araştırma kaydedilirken `girdi_ozeti` hash'iyle DB'ye iner.
- Monorepo: ağaç temiz; push Eray kararı (sayı `git log @{u}..HEAD` ile ölçülür, buraya yazılmaz).

# Verification

| Ne | Taze çıktı |
|---|---|
| Tam takım, gönüllü low düzeltmeleri SONRASI (`pytest -q`) | **4714 passed / 0 failed / 417,0 s** |
| Tam takım, `fceb2d2` için | 4714 passed / 402,5 s |
| Tam takım, review ÖNCESİ (`8f54f15`) | 4704 passed / 402,6 s |
| Mutasyon (dosya yedeğiyle geri alındı) | attempt-1 düzeltmeleri 10/10 yakalandı · N2 1/1 |
| Orkestratör probları (düzeltme sonrası) | aynı gövde + farklı etiket → `notlu-gecti / 2 not`; eski rapor → 0 iddia, adıyla bildiriliyor |
| Codex kapanış turu | rc=0, 491 s, çıktı tam, "no material findings" |
| Tasarım dokümanı ↔ kod (Ek §1-§4 tek tek) | Ek'in tek açık kalemi H2 idi → kapandı; "atıf artıkları silinir" satırı kodda NOT olarak (6 gerçek raporda 0 artık) — Eray kararı: böyle kalsın |

**DENENMEYEN / DOĞRULANMAYAN:**
- Yeni şablonla hiçbir gerçek rapor alınmadı; LLM'lerin 9 sütunu, `[C: …]`'yi, `kaynak-bulunamadı`yı doğru
  yazması ÖLÇÜLMEDİ. Bu turun amacı tam olarak bu.
- **K-129 rakam kuralı** canlıda kaç içerik maddesini açık soruya düşürecek — ÖLÇÜLMEDİ (L2). İlk turda
  `kanit-turu-yetersiz` sebepli açık soruların alan dağılımı sayılacak.
- Gönüllü low düzeltmeleri (N1 · N2 · N4 · N5 · N6) bağımsız hakem GÖRMEDİ — yalnız tam takım + N2 mutasyonu.
- N3: motor aşamasında bağımsız iddiasız-kaynak kapısı yok; erişilebilirlik ÖLÇÜLMEDİ (taze koşuda denetim ve
  sentez kapıları önce reddeder).
- M3 (kapı TOCTOU): canlı yarış penceresi ölçülmedi; tek operatör CLI.
- `/security-review-claude-codex` dalda hâlâ borç (security_surface `uncertain → true`).
- Grup 3 kod oturumunun süresi hâlâ ölçülmedi; review turu: iki hakem ~12 dk (Codex 701 s), kapanış ~12 dk (Codex 491 s).

**TUZAKLAR:**
- **Codex review turu 480 s'ye SIĞMIYOR** (ölçüldü: 701 s ve 491 s); doğrudan 1200 s ile arka planda koş, yoksa
  tur boşa gider. Kota kapısı bayat okuyup PAUSE diyebilir — `resets_at_primary` ile pencerenin geçtiğini ölç.
- `iddiasiz_kaynaklar` ELENMİŞ raporu atlar (elenmiş zaten girdi değil); testte doğrudan kurulan `DoctorReport`
  artık `iddialar=` taşımalı, yoksa paket/sentez reddeder (fixture yardımcıları güncellendi).
- Pin'i dış commit'ten ÖNCE bump etme; dış commit'e Eray'ın silinmiş 41 dosyasını KATMA.
- Koşu `kosu-222706dc…` terminal; eski Kaynak-1..6 yeni hatta girdi olamaz (artık MEKANİK olarak reddedilir).

# Risks

- Yeni şablon + 9 sütun + geri bağlantı LLM'e yapısal yük; ilk turda brief-doctor notu artabilir (not elemez,
  ama sentez girdisi kirlenir). Bir rapor Bölüm C'yi hiç çözemezse artık TUR DURUR (H2 kapısı) — "yeniden üret"
  cevabı doğru ama tur maliyeti tekrar eder.
- Kanıt kapısı içerikte `öneri`yi kabul ediyor; tarihsiz ajans blogu "öneri" sayılırsa zayıf kaynaklı kalıp
  mutabakatla girer.
- Denetçi örneklemi kaynak başına 3 satır; örneklenmeyen iddiada beyan olduğu gibi geçer (kanıt kapısı
  beyanı örneklemsiz KABUL eder — tasarım gereği).
- M2: ölü koşuya Katman-1 tasdiği yazılabilir (aktivasyon etkisi yok, yanıltıcı kayıt riski) — Eray kararı (2026-09-22): bırak.

# Notes For Claude

- Eray'ın talimat sırası: "H1 + H2 (+ M1) düzeltmesi → kapanış turu → yeni kaynak dosyaları". Üçü tamam;
  sıradaki adım Eray'da (araştırma üretimi). Bu oturumda Claude'a düşen tek şey commit onayı.
- Review komut disiplininden bugün ölçülenler: hakem prompt'una spec/plan gömülmez (280 KB), pinli dosya +
  hash; tasarım dokümanı da gömülmedi (shell'e gömme yasağı). Tek-kaynaklı C/H orkestratör probuyla
  "claude-confirmed" yapıldı (ikisi de).
- İlke 9: buradaki sayılar bu oturumun koşumlarıdır; sonraki oturum tam takımı yeniden koşar.
- Kapanış turu Codex'in TASK/HANDOFF'u okuduğunu gösterdi (worktree'de commit'li) — hakem bağımsızlığı için
  active layer prompt'a enjekte edilmez ama dosya ağaçta görünür; kabul edilen sınır.

# Notes For Codex

Attempt-1 (701 s): 1 high (H2), 2 medium (M2 Katman-1 kapı dışı — Claude hakemiyle çelişti, Eray kararı: bırak;
M3 TOCTOU). Kapanış (491 s): approve, dört bulgu da closed, bulgu yok; kapsam beyanı tam. Kalan dikkat
listesi bir sonraki `/security-review-claude-codex` için: (1) `iddiasiz_kaynaklar` elenmiş-atlama sınırı,
(2) paket/sentez reddinin operatör görünürlüğü (bildirim metni), (3) `RunAlreadyTerminal` yakalamalarının
başka DB hatalarını yutmadığı (Claude hakemi kod okumasıyla "yutmuyor" dedi; ölçülmedi), (4) N3 motor kapısı.
