---
task: sektor-bilgi-paketi-plan2
written: 2026-09-06
---

# Resume From

**Task 6 KAPANDI. Sıradaki iş, kod değil bir KAPI: Codex checkpoint'i.**

Bu, protokolün zorunlu kıldığı adım — Task 6'nın **altı commit'inin altısı da `RISKY`**
sınıfında ve `ec_should_checkpoint 1 2 9` → `RUN_RISK` veriyor. Şimdiye kadarki sekiz
incelemenin hepsi taze **Claude** alt-ajanıydı; Codex **bağımsız ikinci bir model** ve ikisi
birbirinin yerine geçmez. Task 5'te bu kapı bir oturum boyunca kaçırılmıştı (defterde
"atlandı değil, kaçırıldı" diye kayıtlı) — tekrarlanmasın.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** → Adım 8.2/8.4.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
**Bu dosya git'e girmiyor** — kaybolursa git defteri ve commit mesajları esastır.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 2`** · **`last_checkpoint_ref: a6e053f`**.

> **İkisi de hâlâ BİLEREK ilerletilmedi** (Task 5'ten devralındı). Checkpoint 3 koşmuş ama
> `approve` almadan kapatılmıştı, yani §8.6 mutasyon protokolüne hiç girilmedi. Sonuç
> fail-safe: sıradaki checkpoint'in tabanı `a6e053f` kalır ve **hem Task 5'in hakem görmemiş
> tur 5/6 commit'lerini hem Task 6'nın tamamını kendiliğinden kapsar.** "Unutulmuş" sanıp elle
> ilerletme.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Task 6'nın son commit'i **`100a6d7`**; HEAD
bu devir commit'inin kendisidir (`docs-only`, kod taşımaz). **Push EDİLMEDİ.**
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: `master`, HEAD
`6d5d90db9537b516413d31f091b4d475526bcb73`, temiz. Bu oturum ona dokunmadı.

**Yedek etiket `backup/pre-footer-fix-20260830`** duruyor; silinme koşulu TASK.md'de.

## Checkpoint dispatch'inde ÖNDEN bildirilecekler (hakemin bulması beklenmiyor)

1. **F1 ve F2 KAPANDI** (`100a6d7`, `T6-fix6`) — kapak sonrası düzeltildiler, park EDİLMEDİLER.
   `:1510` artık "11 iddia", `:1504` artık "YEDİ kez". İkisi de yalnız yorum satırı.
   **Kayda geçsin:** bunları önce park etmek yanlıştı — kapak düzeltme TURLARINI sınırlar,
   iki sayılık bir yorum düzeltmesini tören hâline getirmek görevin borcunu olduğundan büyük
   gösterdi. Eray itiraz etti, haklıydı.
3. **Yapısal bulgu (B yarısı)** — düzyazıdaki sayı iddiaları korumasız; yedi arızanın yedisi de
   orada. Tur 5'in kurduğu iki kapı bu bölgeyi KAPSAMIYOR.
4. **Ek metni kodla uyumsuz** — R12(a2)(d) amende edildi (TASK.md Decisions Log).
5. **Substrat kapsam kaybı** — Codex kum havuzu `api_key=<ifade>` desenli **34 üretim dosyasını**
   sır sanıp dışlıyor (bilinen yanlış pozitif sınıfı, CURRENT.md
   `codex-substrate-dirty-secret-excluded-file`). Task 6 saf SQL + olay modülü olduğu için bu
   turda kayıp sınırlı, ama **rapora dürüstçe yazılmalı: hakem her şeyi görmedi.**

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar (sayılar taze)

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 1181**; bu sayı düşmeyecek. (921 → … → 963 → 965 → 1133 → 1175 → 1176 → 1179 → 1181.)
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ —
   SQL-only commit `migration` alır; `.py` ve `.json` GİRER.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, `Co-Authored-By` / `Claude-Session` **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter.**
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz.
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris de **mutasyonla** sınanır — ve mutasyona
    **boş-küme kontrol kolu** eklenir (hiç bulamayınca da düşsün, sahte yeşil vermesin).
11. **YENİ, BAĞLAYICI (Task 6'nın dersi — yapısal bulgunun A yarısı):** *gönderilen düzyazıya
    sayı yazma.* Ya üreten komutu **yanına** koy, ya "doğrulanmadı" etiketle. Bu satır her
    dispatch brief'ine VE her hakem prompt'una geçer. Gerekçe ölçüldü: Task 6 bu sınıftan
    **yedi** örnek üretti, hepsi düzyazıda, hepsinin çalışma zamanı etkisi sıfır.
12. **YENİ (bu oturumun ikinci dersi):** bir taramanın deseni **bulunan örneklerden** türetilirse
    o tarama değil, zaten bulunanın tekrar kontrolüdür. Desen KAVRAMDAN türetilir. Bu oturumda
    iki kez ihlal edildi ve ikisi de ölçüldü: preflight tarayıcım `...py::sembol` biçimini
    kaçırdı; `dokuz` hem uygulayıcının hem benim grep'imden geçti (ikimiz de `DOKUZU` aradık).
13. **YENİ (üçüncü ders):** kontrolörün tam test kümesi, **veritabanına dokunan bir alt-ajanla
    ASLA üst üste binmez.** Sıraya koy. Arıza biçimi çökme değil, inandırıcı bir kırmızıdır —
    bu oturumda bir teşhis turuna mal oldu.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-06, hepsi kontrolörün KENDİ koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **1181 passed in 399.39s**, temiz ağaçta, **sessiz veritabanında**, HEAD `100a6d7`'de
  (yani F1/F2 düzeltmesinden SONRA). Seyir: 965 (giriş) → 1133 → 1175 → 1176 → 1179 → 1181.
  Hiç düşmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, sıfır kırmızı satır,
  her Task 6 commit'inden sonra tekrar koşuldu.
- Dört commit'in `Exec-Kind`'ı sınıflandırıcıya karşı tek tek doğrulandı; başlıklar 61-69 karakter.
- **Codex çağrısı: 1** (Adım 6 ön-yürütme, `task-fresh`, `rc=0`) — drift YOK. Ham çıktı
  `/root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.
- **Kontrolörün kendi probları** (hepsi POZİTİF KONTROL kollu): kısıt/indeks ikiliği
  (`CONSTRAINT` → 1 kısıt + 1 indeks; `CREATE UNIQUE INDEX` → 0 kısıt + 1 indeks) · plpgsql geç
  bağlanma (gövde atıfı → `DROP COLUMN` rc=0; kolon listesi → rc=1) · canlı sözleşme sayımı
  (`11 {'gecis': 3, 'surumsuz': 8}`) · kavramdan türetilmiş sayı taraması (3 isabet, üçü de
  anlamsal kullanım, bulgu değil) · kapı kapsamı AST ile (11, yorumdaki 16 değil).
- **`ec_classify_diff`** altı Task 6 commit'i üzerinde: **altısı da RISKY**.
- **Preflight conflict scan** (bu oturumda İLK KEZ koştu, Task 6-20 kapsamlı): 7 paylaşılan yüzey,
  **çelişki YOK**; tabloya ve gerekçesine defterden bakılır.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Task 6 Codex'i GÖRMEDİ.** Sekiz incelemenin sekizi de taze Claude alt-ajanıydı. Checkpoint
  bir sonraki oturumun İLK işidir.
- **Task 5'in tur 6 commit'leri hâlâ bağımsız hakem görmedi** (Task 5'ten devralınan kabul
  edilmiş risk). Sıradaki checkpoint tabanı onları da kapsar.
- **Checkpoint 3'ün son verdict'i `needs-attention`** (tur 2) ve yürürlükte.
- PG 18.3 dışında sürüm denenmedi; **gerçek çok-oturumlu eşzamanlılık denenmedi.**
- Canlıya hiçbir şey dağıtılmadı; **035 ve 036 hiçbir gerçek ortama uygulanmadı**, pilot koşulmadı.
- **Düzeltilmiş iki n8n workflow'u canlıya import EDİLMEDİ** — yani CRM + takvim bildirimleri
  şu an sessiz (operatör işlemi, CURRENT.md'de yazılı).
- **Dal push EDİLMEDİ.**
- Task 7–20 hiç yazılmadı.

# Risks

- **KABUL EDİLMİŞ RİSK — Task 6 bağımsız model görmedi.** "Ele alındı" DEĞİL; kapısı adlandırıldı.
- **F1 ve F2 ARTIK RİSK DEĞİL — kapandı** (`100a6d7`). Park kararı geri alındı.
- **EVSİZ DEĞİL AMA TARİHSİZ — yapısal bulgunun B yarısı** (düzyazı sayı yüzeyi + politika
  kararı). Evi dal-sonu triage listesi; o ev bir KARAR noktası, düzeltme değil.
  **Dürüst etiket: çözülmedi + evi var + tarihi Plan 2'nin bitişine bağlı.**
- **EVSİZ PARK (Task 5'ten devralındı) — atomiklik sınıfı depo GENELİ.** 035 tek başına atomik
  olan tek migration; onaylı koşum yolu her dosyayı `--single-transaction` ile sardığı için bugün
  zararsız. Yeniden açılma koşulu: sarmalayıcı kalkarsa VEYA elle uygulama bir olayda kök sebep olursa.
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (ölçüldü, kapatılamaz;
  üç dosyanın başlığında yazılı).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **Codex maliyeti:** bu oturumda 1 çağrı. Final için ≥3 tur rezerve kuralı yerinde.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Bu oturum SÜRE AÇISINDAN uzundu ama boş değildi:** beş düzeltme turu **dört gerçek kusur**
  buldu, ikisi sessiz veri kaybı sınıfındaydı (denetim iznine uydurma sürüm yazılabilmesi;
  K-45 geçmiş üreticisinin kolon yeniden adlandırılınca sessizce durması). Kalan üç tur bir
  **alışkanlığı** kovaladı ve o alışkanlık yapısal bulgu olarak adlandırıldı.
- **Uygulayıcı iyiydi ve bunu kayda geçir:** üç kez kontrolörün saymadığı şeyi kendi buldu
  (dördüncü yanlış-iddia yeri · yanlış sebeple geçen bir mutasyon hücresini gönüllü bildirmesi ·
  tarama dosya listesini kavramdan türetip iki dosya eklemesi). Kendi iddiasını iki kez çürüttü.
- **Kontrolör düzeltme YAPMAZ.** Bu oturumda istisna kullanılmadı.
- **Uygulayıcı raporunu doğrulanmamış iddia say — hakem raporunu da.** Bu oturumda her Important
  bulgu kontrolör tarafından yeniden ölçüldü ve hepsi doğrulandı; ama bir kez de kontrolörün
  KENDİ ölçümü kirlendi (paralel koşum) ve düzeltilmesi bir tur aldı.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor; alanı
  boş bırakmak opus-5 tabanını miras alır.
- **Spec değil, spec-input kanoniktir.**
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
