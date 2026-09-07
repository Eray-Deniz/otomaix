---
task: sektor-bilgi-paketi-plan2
written: 2026-09-07
---

# Resume From

**Sıradaki iş — İKİ seçenek, sırası ÖNEMLİ:**

1. **`brief-sozlesmesi-kaynak-bolumu-makine-okunur`** (kendi TASK dosyası var) — yuvası
   **Task 8 ile Task 9 ARASI**, yani Task 8'den hemen sonra. İki ürün kararı Eray'a sorulmadan
   sözleşme metni yazılamaz.
2. **Task 8 — koşu ve artefakt servisi** (plan satır 981).

Yani sıra: **Task 8 → sözleşme görevi → Task 9.** Sözleşme görevi Task 9/10'dan (denetçi katmanı)
ÖNCE bitmeli, yoksa o görevlerin yazdığı koda geri dönülür.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** → Task 8 dispatch.

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md` (git'e girmiyor).

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **BİLEREK İLERLETİLMEDİ.** Checkpoint 6 sekiz tur sürdü; son beş tur `approve` verdi ama
> kapanış Eray'ın risk kabulüyle alınan bir **override**'dır (bir high bilinçle onarılmadı,
> evi var). §8.6 mutasyon protokolü yalnız Clean/Accepted-risk dallarında koşar. Sonuç
> fail-safe: sonraki checkpoint'in tabanı `2b468e8d` KALIR ve Task 7'nin bütün commit'lerini
> kendiliğinden yeniden kapsar.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit **`7244ea0`**. **Push EDİLMEDİ.**
**`7244ea0` bağımsız hakem GÖRMEDİ** — tur 8 `628f784`'e kadar inceledi. Kontrolör kendi
probuyla ölçtü (yuva sahteciliği kapandı, liste işaretleri düzeldi, aşırı sıkılaştırma yok),
ama bu bağımsız yargı DEĞİLDİR. Final incelemenin tabanı `a806e29` olduğu için kapsanır.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: bu oturum ona DOKUNMADI.

## ERAY'IN CEVABINI BEKLEYEN İKİ KARAR (2026-09-07 oturumu kapanırken açık kaldı)

Bunlar olgu değil **karar**dır; oturum kapanırken cevaplanmadı. Yeni oturum bu ikisini
gündeminin BAŞINA alır — Task 8 dispatch'inden ÖNCE sorar.

1. **Dal push edilsin mi?** Şu an 21+ commit yalnız yerelde. Push edilmemesi bilinçliydi
   (yürütme protokolü push'u kullanıcı onayına bağlar), ama karar verilmedi.
   *Bağlam:* tam test kümesi `5002 passed`, defter kapısı `rc=0`, ağaç temiz.

2. **Hakem görmemiş commit'ler için bir tur daha koşulsun mu?** Checkpoint 6'nın son hakem
   turu (tur 8) `628f784`'e kadar inceledi. Ondan sonraki kod commit'i `7244ea0` (çit maskesinin
   ayrıştırmadan önceye alınması) **bağımsız yargı GÖRMEDİ** — kontrolör kendi probuyla ölçtü
   (yuva sahteciliği kapandı · liste işaretleri düzeldi · aşırı sıkılaştırma yok · gerçek veride
   kaybolan tek not yanlış-pozitifti, dosya açılıp doğrulandı), ama bu bağımsız yargı DEĞİLDİR.
   *Ev uydurulmadı:* final incelemenin tabanı `a806e29` olduğu için o commit oraya kendiliğinden
   girer; yani cevap "hayır" olursa da evsiz kalmaz — yalnız daha geç incelenir.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **Ek metni kodla uyumsuz, İKİ yerde** (değişmedi): R12(a2)(d) amende edildi; aktör kapısının
   tanım yeri ekin gösterdiği modül değil.
2. **Ekin kendi içinde çelişkisi:** ayak (d) düzyazısı `BEFORE UPDATE OR DELETE`, bağlayıcı SQL
   bloğu `BEFORE UPDATE`. **Evi Task 8 — yani sıradaki görev.**
3. **Onay mührü yüklemi:** dolu → BOŞ reddediliyor, yeniden mühürleme BİLEREK açık. Task 8'de
   ek metniyle karşılaştırılmalı.
4. **Kimlik kapıları migration dosyalarının BAŞINDA** — yeni migration yazılırken kapı ilk üst
   düzey DDL'den ÖNCE konmalı.
5. **Task 7 ve Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** (20 görevin 18'inde var).
   Task 7'de sorun çıkmadı çünkü ekin iki tüketici sözleşmesi yine de bağlıyordu ve dispatch'e
   harfiyen taşındı. **Task 11'de aynı kontrol ELLE yapılmalı.**
6. **Task 8/9/12 girdi kapısının tiplerini tüketecek.** Bugün depoda o tiplere modül ve kendi
   testi dışında **hiçbir atıf yok** (kontrolör taradı). Task 8 ilk tüketiciyi eklerse, TASK.md
   Open Problems'taki tetikli kalemler yeniden değerlendirilmeli.
7. **Substrat kapsam kaybı:** Codex kum havuzu `api_key=<ifade>` desenli üretim dosyalarını,
   aktif katman dosyalarını ve bağlayıcı eki dışlıyor. Hakem her turda bunları HEAD git
   nesnelerinden okuduğunu ve **tam test kümesini yeniden koşamadığını** açıkça yazdı.
8. **YENİ — girdi kapısının test dosyası büyük.** 3503 test, 25 sn (tam küme 5002 / 570 sn).
   Bir önceki turda 6929'du ve hakem "orantısız" dedi; kap ekseni aile temsilcisine indirilip
   kazanılan yer gerçekten ayırt eden eksenlere harcandı. Yeni matris eklerken aynı disiplin:
   **kap çarpımını büyütme, ayırt eden ekseni büyüt.**

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 5002**; bu sayı düşmeyecek.
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY, tahmin etme.
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır, **boş-küme kontrol
    kolu** eklenir.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
13. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
14. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testleri bayatlatabilir — **her turda eski test
    dosyasını yeni modüle karşı koştur.**
15. Kimlik kapısı ya kanonik değerle TAM eşleşmeli ya da kümeyi ÜRETEN yapıdan türemeli.
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
17. **Hakem/kontrolör önerisi ADAYDIR.** Bu görevde ölçümde yanlış çıkan öneri/teşhis sayısı
    **altı**. Uygulayıcı ölçüp reddetmekle yükümlü ve bunu YAPTI.
18. **Kendi probunu da sorgula.** Bu oturumda kontrolörün probu **dört kez** yanılttı: fazla
    masum vaka · boş gövdeli çit · not SAYISI karşılaştırması · yanlış yuva tipi. Üçünde de ilk
    okuma "sorun yok" diyordu.
19. **KAPANIŞ SAYIYLA DEĞİL MESAJ KÜMESİ FARKIYLA KANITLANIR.** Bir not kaybolurken toplam
    ARTABİLİR — bu oturumda tam olarak öyle oldu ve kaçtı.
20. **Üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.** Sınıfı adlandır, üretilmiş
    matrisle kapat; kapanmıyorsa çerçeve teşhisiyle Eray'a git.
21. **Bir KURAL beşinci kez kandırılıyorsa kural yazmayı bırak, DEĞİŞMEZ kur.** Bu oturumun en
    değerli dersi: beş sınır kuralı beş kez yenildi; *"tablo eklemek var olan notu kaldıramaz"*
    değişmezi sınıfı kapattı.
22. **Beyan bayatlarsa beyan olmamaktan kötüdür.** Bu oturumda altı kez yakalandı; çözüm
    envanteri TRIPWIRE'a çevirmek oldu — ilan edilen her açık için o açığın gerçekten var
    olduğunu ölçen bir test.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07, hepsi kontrolörün KENDİ koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **5002 passed in 569.66s**, exit 0, temiz ağaçta, HEAD `7244ea0`'da.
  Seyir: 1499 → 1552 → 1644 → 1758 → 1793 → 1821 → 2261 → 2350 → 2770 → 8428 → **5002**.
  (8428 → 5002 düşüşü **matris küçültmesidir**, iddia kaybı değil: kap ekseni aile temsilcisine
  indirildi, her küçültülen aile hâlâ temsilcisiyle ölçülüyor ve genel mutasyon kolunda beş
  ailenin beşi de kırmızıya düşüyor.) **Hiç test silinmedi, hiç davranış iddiası kaybolmadı.**
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- `bash ~/.claude/tools/command-blocks-maint.sh verify` → **PASS** (oturum başında).
- **Sözleşme pini:** `verify_pin` → **sıfır sapma**.
- **Codex çağrısı: 8** (checkpoint 6, tur 1-8; hepsi `rc=0`). Ham çıktı + kapanış denetim kaydı
  `/root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md`.
- **Kontrolörün bulgu doğrulaması:** sekiz turun HER bulgusu kontrolörün kendi probuyla yeniden
  ölçüldü; hiçbir turda hakemin sözüne dayanılmadı.
- **Gürültü ölçümü, gerçek veri:** dış depodaki 62 dosyada mesaj kümeleri; son turda **1 dosyada
  1 not düştü** ve kontrolör dosyayı açıp doğruladı — not 12. satırdan geliyordu, çit 3-13
  satırları arasındaydı, yani **yanlış-pozitifti**. Gerileme değil, gürültü azalması.
- **Çağıran taraması:** girdi kapısının tiplerine modül ve kendi testi dışında depoda atıf yok.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **`7244ea0` bağımsız hakem görmedi** (yukarıda).
- **Bölüm C'nin üçlü yapısı makineyle DOĞRULANMIYOR** — ilan edildi, onarılmadı, evi var.
- **Sözleşmeye uyan bir araştırma çıktısında yanlış-pozitif oranı ÖLÇÜLMEDİ** — dış depodaki
  dosyalar sözleşmenin şimdiki biçiminden eski ve hiçbirinde Bölüm B tablosu yok.
- **Kontrolörün 5002 sonucu bağımsız hakem tarafından yeniden üretilmedi** — Codex kum havuzunda
  dışlanan dosyalar toplama hatası veriyor; hakem bunu her turda kendisi yazdı.
- **Değişmez bir kez GEVŞETİLDİ:** dilsiz çit kolu ham mesaj kümesi yerine "konu" düzeyinde
  karşılaştırıyor. Sebep ölçülmüş (kökte kapanmamış çit belgenin gerisini yutunca sayım notu
  `5 madde` → `0 madde` olur; not susmaz, sayısı düşer). Ham kaybın çıktığı 15 hücre adıyla
  pinli ve ayrı bir test her birinde konunun konuştuğunu + sayının artmadığını ölçüyor.
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- PG 18.3 dışında sürüm denenmedi; çok-oturumlu eşzamanlılık denenmedi.
- Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı. **Dal push EDİLMEDİ.**
- Task 8–20 hiç yazılmadı.

# Risks

- **Checkpoint 6 `approve` ile DEĞİL, override ile kapandı.** Son beş tur `approve` verdi ama bir
  high (Bölüm C üçlüsü) bilinçle onarılmadı; evi ve son tarihi var. `cp_count` ilerletilmedi.
- **TARİHLİ — sözleşmenin kaynak bölümü makine-okunur değil.** Ev:
  `docs/active/brief-sozlesmesi-kaynak-bolumu-makine-okunur/`. **Yuva: Task 8 → Task 9 arası.**
  Task 9/10 denetçi katmanını kurar ve sözleşme değişikliği o metne de dokunur.
- **EN YÜKSEK — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI** (değişmedi).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor** (değişmedi; hakem
  bu oturumun sekiz turunda bu itirazı BİR KEZ BİLE tekrarlamadı).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **Codex maliyeti:** bu oturumda 8 çağrı (Eray "sayı önemli değil, eksiksiz bitsin" dedi).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Bu oturumun en değerli dersi (madde 21):** bir kural beşinci kez kandırılıyorsa altıncı kuralı
  yazma — **değişmez** kur. Beş sınır kuralı beş kez yenildi; *"ekleme var olan notu kaldıramaz"*
  değişmezi sınıfı kapattı ve sonrasında bulunan her şey o değişmezin KAPSAM sorusu oldu.
- **İkinci ders: beyanı ölçülebilir yap.** Beyan altı kez bayatladı. Çözüm envanteri tripwire'a
  çevirmek oldu: ilan edilen her açık için, o açığın gerçekten var olduğunu uçtan uca ölçen test.
- **Üçüncü ders: "doğrulanmadı" demek çözmek değil devretmektir** — devrin nereye gittiğini ölç.
  Bu oturumda ölçüldü: denetçi sözleşmesi kaynak başına 3 iddia örnekleyip bağlantıyı gerçekten
  açıyor (makinenin yapamayacağı kontrol), ama **bütünlük** sorusunu cevaplamıyor.
- **Hakem raporunu doğrulanmamış iddia say** — sekiz turun her bulgusu yeniden ölçüldü.
- **Kendi probunu da sorgula** — dört kez yanılttı.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma** — İlke-8 kapısı bu oturumda bir soruyu haklı olarak reddetti.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
