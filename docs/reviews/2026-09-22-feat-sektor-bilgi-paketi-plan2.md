# Review (dual): Grup 3 — üçüncü şablon revizyonu uçtan uca + ölü koşu kapısı — 2026-09-22

Review aralığı: `c0d073a..8f54f15`
- BASE_REF: `c0d073a` (bu daldaki son review-kapanış commit'i; sonrası hiç hakem görmemişti) | BASE_SHA: `c0d073a` | HEAD_SHA: `8f54f15` | REVIEW_BASE_SHA (merge-base): `c0d073a`
- Commit'ler: `2bf3d71` fix(hat) ölü koşu iş kabul etmez · `1596384` docs(spec) iki doğrulama katmanı ayrıldı · `65beb34`/`c54437a` docs(active) · `8f54f15` feat(hat) Grup 3 (brief_doctor · engine · synthesis · pin · 47+8 test)
- 17 dosya, +2108 / −244

Reviewers: fresh Claude subagent (general-purpose; `superpowers:code-reviewer` bu kurulumda
çözülemedi, persona aynı prompt'la kullanıldı) + Codex `adversarial-review`
dual-review: **true** (claude_status: ran · codex_status: ran)
Review workspace: pinned worktree @ HEAD_SHA (clean)
Main tree at review: clean (0 uncommitted — review dışı bırakılan iş YOK)
security_surface_touched: **uncertain → true** (fail-closed) — `runs.py`/CLI koşu-durumu kapısına
dokunuldu; güvenlik-checklist eki KONMADI, `/security-review-claude-codex` zorunlu kalır.

Requirement context (iki hakeme BİREBİR aynı küme, pinli):
- Grup 3 tasarımı `_sablon-duzenleme.md` — dış depo `34a34db`, sha256 `126c86ca…6fca` (pinli export `ext/`)
- Sözleşmeler `hakem-denetci-gorevi.md` `b8ae41…`, `hakem-sentez-gorevi.md` `108b43…`, `_SABLON.md` `197404…` — üçü de `research-contracts.pin.json` ile birebir (iki hakem de ayrıca doğruladı)
- `docs/specs/2026-08-21-sektor-bilgi-paketi.md` §13.3 (`:1319-1345`) + `docs/plans/2026-08-27-…plan2.md` Task 19 Step 8/9 — committed, YOLLA verildi
- **Dürüst sapma:** spec 105 KB + plan 175 KB tek argüman sınırını (131.072 bayt) aşar; gömülmedi,
  iki hakem de aynı pinli dosyaları okudu. Tasarım dokümanı da gömülmedi (prompt shell'e gömme
  yasağı); pinli export + hash ile verildi.

Codex koşumu: ilk çağrı 480 s dış timeout'ta düştü (0 bayt; ilerleme akışı kesilene dek komut
koşuyordu → uzun koşum, asılma değil); 124-deseni gereği 1200 s ile tek tekrar → **701 s, rc=0**.
Kota kapısı bayat %89 okuyup PAUSE dedi; o pencerenin sıfırlanma damgası çağrıdan 10 saat önce
geçmişti (ölçüldü: `resets_at_primary` < now) — tekrar bu ölçüme dayanarak koşuldu.

Taze test takımı (ana depo, HEAD `8f54f15`, `.venv/bin/python -m pytest -q`): **4704 passed / 0 failed / 402,6 s**.

## Critical

Yok.

## High

- **H1 `brief-doctor/geri-baglanti-etiketi-tekrar-ve-adet-yuzeyi`** [single-source: claude → **claude-confirmed**]
  `brief_doctor.py:2823` (`_madde_izi`) ve `:1414` (`essiz_maddeler`) HAM madde metnini karşılaştırıyor;
  yeni zorunlu `[C: n]` etiketi metnin parçası ve madde başına farklı olduğu için birebir aynı beş
  kalıp "benzersiz" sayılıyor → tekrar izi VE adet alt sınırı (`cta ≥ 5`) sessizce susuyor. Aynı iki
  yüzeyi `kanca_kaliplari` · `gorsel_kodlar` · `video_kodlar.*` · dönem yuvaları da okuyor.
  **Orkestratör ölçümü (kontrol kollu, `bd.run`, worktree değişmedi):** aynı gövde + farklı `[C: n]`
  → `gecti / 0 not`; aynı gövde + aynı `[C: 4]` → `notlu-gecti / 3 not` ("bir madde 5 kez
  yazılmış", "1 madde taşıyor, alt sınır 5", çoklu-bağ notu). Alt-hakemin fix-yönü simülasyonu
  (anahtarda etiketi düşürünce) iki notu geri getirdi.
  *Fix:* anahtar üretiminde `_GERI_BAGLANTI_RE.sub("", madde)` sonra `_sadelestir` (tek yardımcı;
  `_sadelestir`'in kendisine dokunulmaz — alan/dönem anahtarı için de kullanılıyor). Regresyon testi:
  beş özdeş CTA + farklı etiket → iki not. L4 ile birlikte kapatılır (aynı mesaj yolu).
  **Not (kalibrasyon, minimization değil):** iki aile de `SEVIYE_NOT`; kaybolan şey eleme değil
  operatör sinyali — ama alt sınır kuralının var oluş sebebi tam olarak bu doldurma desenidir.

- **H2 `hat/eski-surum-rapor-mutabakata-oy-verir`** [single-source: codex → **claude-confirmed**]
  Eski (7 sütun) rapor kapıdan `notlu-gecti` ile geçiyor ve **0 iddia** üretiyor; sentez kapısı
  yalnız TOPLU iddia dizininin boş olmadığına bakıyor (`synthesis.py:986`); `gate_round` ve
  `_kabul_edilen_etiketler` `kimlik_bolumlemesi`'nin "elenmeyen" kümesini okuyor (eski rapor içinde).
  Motor `_yeni_oge_cogunlugu` kaynak sayısını `satir_evreni[parca].kaynaklar ∩ kabul_edilen`'dan
  kuruyor (`engine.py:1243-1247`) — satırın listelediği HER kaynak sayılıyor, kaynak başına bağlı
  iddia şartı YOK. Sonuç: eski + iki yeni rapor karışımı denetime girer, denetçi satırı K1'i
  anarsa K1 iddiasız hâlde çoğunluğa oy verir — "eski raporlar yeni hatta girdi olmaz" hükmü
  (tasarım + `brief_doctor.py:3136-3142` yorumu) kodda ZORLANMIYOR.
  **Orkestratör ölçümü:** fixture'dan türetilen 7 sütunlu rapor → `notlu-gecti`, 1 not, 0 eleme;
  `iddia_evreni([eski, yeni2, yeni3])` = 220 etiket, K1# etiketi YOK → sentez kapısı geçer.
  Zincirin 3. halkası (motorun satır kaynak listesini sayması) kod okumasıyla doğrulandı
  (`engine.py:1243-1247`, `:649`); uçtan uca motor koşumu YAPILMADI.
  *Fix:* (a) `gate_round`'da rapor başına sözleşme-sürümü durumu — eski/karışık küme denetçi
  koşmadan reddedilir (K-127 tabanına eski rapor sayılmaz); (b) savunma: motor yalnız satırın
  `kaynak_iddialari`'nda iddia taşıyan kaynakları sayar. Fallback: karışık sürümde hard-stop;
  kaynak süzüp yeniden numaralandırma YAPILMAZ (K etiketleri kayar).

## Medium (`accepted_risk` — politika ch-only-v1; fix zorunlu DEĞİL, ama aşağıdaki öneriye bak)

- **M1 `runs/RunAlreadyTerminal-sarilmamis-cagri-yerleri`** [single-source: claude; kod okumasıyla doğrulandı]
  `mark_incomplete` terminal satırda artık `RunAlreadyTerminal` fırlatıyor (`runs.py:750`);
  docstring "çağıranların hepsi sarılı" diyor ama `synthesis.py:1164` (`except SynthesisFailed`
  kolu — `raise`'a hiç gelinmez, çağıran yanlış istisnayı görür), `auditors.py:3188`, `cli:367`
  sarılı DEĞİL; istisna `ALAN_HATALARI`'nda da yok → ham traceback. Ulaşılabilirlik dar
  (CLI kapısı zaten `calisiyor` ister; eşzamanlı yazar gerekir) — ölçülmedi.
  **Bu aralığın kendi açtığı gerileme** (`2bf3d71`). *Öneri:* H1/H2 ile aynı executor turunda
  kapat (3 sarma + `ALAN_HATALARI` + docstring; ucuz) — kendi açtığımız medium'u park etmiyoruz.
- **M2 `cli/katman1-canlilik-kapisi-disinda`** [single-source: codex — **hakemler-arası çelişki**]
  Codex: `katman1` ölü (`tamamlanmadi`) koşuya tasdik yazabilir; sıra artık motordan önce.
  Claude alt-hakemi aynı yeri "spec §13.3 ile tutarlı" okudu. Kod: `sector_pipeline_cli.py:1418`
  tasdik adımlarını **bilinçle** dışarıda tutuyor ve gerekçesini yazıyor (aktivasyon
  `load_verified_run`'ın `tamamlandi` kapısından geçer; tasdik ölü koşuyu aktive edilebilir
  yapmaz). Davranış Codex'in dediği gibi; anlaşmazlık "kusur mu, belgeli karar mı". Kalan risk:
  ölü koşu taze tasdik kaydı taşır (yanıltıcı kayıt, aktivasyon etkisi yok). **Karar Eray'ın.**
- **M3 `cli/canlilik-kapisi-toctou`** [single-source: codex; statik, kanıt kısmi]
  Kapı tek okuma; `denetim`/`sentez` dakikalarca sürer, bu arada başka süreç koşuyu
  `tamamlanmadi` yapabilir, `record_artifact` koşulsuz ekler. Kapıdan ÖNCE hiç kapı yoktu —
  pencere daraldı, kapanmadı. Tek-operatör CLI; güvenlik-nitelikli değil → `accepted_risk`.
  Ucuz fallback: her kalıcı yazımdan hemen önce koşullu (durum='calisiyor') yazım.

## Low (`accepted_risk`)

- **L1** `brief_doctor.py:3730` `_c_kapsama_ihlalleri` docstring'i "kaynak satırı" diyor, kod "satır (kaynaksız dâhil)" sayıyor — beyan bayat.
- **L2** `engine.py:409` `_mevzuat_mi` "herhangi bir rakam" vekili artık kanıt kapısında `ekle` kabulünü belirliyor; kapsam etkisi ölçülmedi (TASK'ta K-129 notuyla zaten kayıtlı). Kod değişikliği önerilmez; ilk turda `kanit-turu-yetersiz` açık sorularının alan dağılımı sayılır.
- **L3** `sector_pipeline_cli.py:1487` tek boş satır (E305) — lint yapılandırması yok, CI düşmez.
- **L4** (ARALIK DIŞI, `ce69294`) `brief_doctor.py:2886/2896/2920` tekrar notu `{{ad}}` düz string'de f-string'den geçmiyor → operatör literal `{ad}` görüyor. H1 fix'i bu notu canlandıracağı için birlikte düzeltilir.

## Disposition Ledger (her ham bulgu — sessiz drop yok)

| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| H1 | claude | high | high | kept (fix-required) | orkestratör probu: deney 0 not / kontrol 3 not |
| H2 | codex | high | high | kept (fix-required) | orkestratör probu: eski rapor notlu-gecti + 0 iddia + dizin dolu; motor sayımı kod okuması |
| M1 | claude | medium | medium | accepted_risk (policy_accepted) + fix önerisi | kendi açtığımız gerileme; 3 çağrı yeri kodda doğrulandı |
| M2 | codex | medium | medium | accepted_risk (policy_accepted) — çelişki açık | belgeli bilinçli dışlama (`cli:1418`) vs Codex; Eray kararı |
| M3 | codex | medium | medium | accepted_risk (policy_accepted) | statik; kapı öncesi durumdan daha dar; güvenlik-nitelikli değil |
| L1 | claude | low | low | accepted_risk | docstring |
| L2 | claude | low | low | accepted_risk | ölçüm ilk turda; TASK'ta zaten kayıtlı |
| L3 | claude | low | low | accepted_risk | stil |
| L4 | claude | low | low | accepted_risk (aralık dışı, pre_existing) | H1 ile birlikte kapatılır |

Codex'in ayrıca "temiz" bildirdikleri: kanıt eşlemesi · EK-M kurulumu · sızıntı kapısı · pin
bütünlüğü — ayrı bulgu yok. Claude alt-hakemi: Grup 3'ün adı geçen her kalemi kodda karşılığını
buldu; Ek §2.3 "paketsiz üretim byte-exact" ayağı bu aralıkta yeni test almadı (mevcut
`tests/prompt_regression/` takımına dayanıyor; tam takımda yeşil — yukarıdaki taze koşum).

## Sonuç

- Kapatılan (push-back): 0
- Açık (devam): **2 high fix-required** (H1, H2) + 3 medium + 4 low `accepted_risk`
- Hakemler-arası çelişki: **M2** (Katman-1 kapısı — kusur mu, belgeli karar mı)
- both-agree: 0 | single-source: 9 (claude 6, codex 3) — iki hakem farklı yüzeylere baktı; tek ortak
  konu ölü-koşu kapısı (Claude: istisna sarma; Codex: küme + yarış)
- Chain-advance: dual ✓ **AMA unresolved C/H VAR → `/security-review-claude-codex` hard-block**;
  önce executor fix (H1 + H2, öneri: M1 + L4 birlikte) + `/review-claude-codex` kapanış turu.

## Ham kanıt — işaretçiler (bu makinede, bu kökten)
- Codex ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-22-review-feat-sektor-bilgi-paketi-plan2-1.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-22-review-feat-sektor-bilgi-paketi-plan2-1.claude.md`
- Orkestratör probları: scratchpad `probe_high.py` · `probe_legacy.py` (oturum geçici dizini; kalıcı değil — sonuçları yukarıda)
