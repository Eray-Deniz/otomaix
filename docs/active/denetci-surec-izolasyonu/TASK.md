---
title: Denetçi alt süreçleri işletim sistemi kutusuna alınsın (S-2 kalıntısı)
status: active
started: 2026-09-17
last-touched: 2026-09-18
blocked-by: null
source_task: docs/active/sektor-bilgi-paketi-plan2/TASK.md
---

# Goal

**İkisine de ağ erişimi vermek.** Bugün ağ, yalnız Codex tarafında tek kalan duvar olduğu
için kapalı tutuluyor — kutu kurulunca o duvara gerek kalmaz.

⚠️ **KAPSAM DÜZELTMESİ 2026-09-18 (Eray itirazı, ölçümle doğrulandı).** Bu satır önce *"İki
denetçi alt sürecini root ayrıcalığından çıkar"* diyordu. Yanlıştı: kutunun ÖLÇÜLMÜŞ gerekçesi
**Codex'e özeldir.** Codex'in `read-only` kum havuzu yazmayı ve ağı kısıtlar, OKUMAYI kısıtlamaz
(`.env` 1658 B okundu). Claude'un okuması `--restricted` ile zaten kendi çalışma dizinine
hapsedilmiş — **bugün yeniden ölçüldü**, üç koşum: paket içi dosya OKUNDU (pozitif kontrol),
`/etc/hostname` ve `/root/.claude` denemeleri aracın kendi hatasıyla DÜŞTÜ
(*"--restricted confines the file tools to the working directory"*).

Yani kutuya giren **`denetci-2` (codex)**'dir. `denetci-1` (claude) bugünkü gibi root koşar.

Bu, 2026-09-12 güvenlik review'ının S-2 bulgusunun kendi kalıntı notudur:
*"gerçek süreç izolasyonu (kapsayıcı/ad-alanı ya da araçsız yapılandırılmış-çıktı API'si) bu
turda YAPILMADI"*.

# Neden şimdi

Task 19 Step 6'nın `denetim` ayağı, iki denetçi de "web erişimi yok" dediği için başlamadı
(K-14 sert kapı). Erişim vermek gerekiyor; ölçüm gösterdi ki iki denetçi aynı kutuda değil.

# Ölçülmüş taban (2026-09-17, bu oturum)

Hepsi taze koşumla alındı; sayıların yanında üreten komut vardır.

| Ölçüm | Sonuç |
|---|---|
| `claude` denetçisi, bugünkü argv | web YOK (`UNREACHABLE`) |
| `claude` + `--tools Read,Glob,Grep,WebFetch` | **web VAR** — taze commit kimliğini birebir bastı |
| `codex --sandbox read-only` | kabuktan ağ YOK (`Could not resolve host`) |
| `codex --sandbox workspace-write` | kabuktan ağ YOK |
| `codex workspace-write` + `network_access=true` | **ağ VAR** — canlı değeri doğru getirdi |
| `codex --sandbox danger-full-access` | ağ VAR |
| tam ortam ↔ minimal ortam | **fark YOK** — engel ortamda değil, kum havuzunda |
| `codex` yazma kapsamı (`/root` altında ölçüldü) | kendi klasörü + `/tmp` yazılır; **kardeş denetçi klasörü ve depo kökü REDDEDİLDİ** |
| `codex` **okuma** kapsamı (`read-only` kipinde) | **tüm dosya sistemi** — `.env` 1658 B, `settings.json` 7375 B, boyutlar birebir |
| `claude` okuma kapsamı (`--restricted`, 2026-09-12) | yalnız kendi çalışma dizini |
| `codex` kullanıcısı olarak `/root` erişimi | `.env` ENGELLİ · `auth.json` ENGELLİ · denetim ağacı GÖRÜNMÜYOR |
| `codex` kullanıcısının kimliği | ÇALIŞIYOR (`PONG` döndü) |
| `codex` kullanıcısının grupları | `codex`, **`sudo`**, `users` |
| boru hattı `/tmp`'den okuma yapıyor mu | HAYIR (grep ile tarandı) |

**Asimetrinin kökü:** `--restricted` Claude'un okumasını kendi klasörüne hapsediyor;
Codex'in `read-only` kum havuzu yalnız YAZMAYI ve AĞI kısıtlıyor, OKUMAYI kısıtlamıyor.
Yani Codex'e ağ vermek, tüm sırların dışarı çıkabileceği bir yol açardı. `/root` izni `700`
olduğu için kullanıcı değişikliği bu yolu tek hamlede kapatıyor.

# Onay ve kapsam kararı

- **Eray kararı (2026-09-17):** mevcut `codex` kullanıcısı kullanılacak, `sudo` üyeliği
  kaldırılacak. Temiz kullanıcı açılmayacak.
- **Eray kararı (2026-09-17):** spec seansı YAPILMAYACAK. ⚠️ Not düşüldü: paket kökünün
  taşınması gibi tasarım kararları uygulama sırasında alınacak; sonradan refactor riski kabul
  edildi. Review gerektiğinde koşulacak.

# BAĞLAYICI KISIT — kapsam sızmasın

**Bu görev YALNIZ denetçi alt süreçlerini etkiler.** `claude-codex` komut ailesi
(`/review-claude-codex`, `/spec-claude-codex`, `/write-plan-claude-codex`, …) Codex'i
**root olarak** koşuyor — ölçüldü (`ps`: `root … node /usr/bin/codex`). Onlara dokunulmaz.

Bunu güvence altına alan iki kural:

1. **`/root/.codex/config.toml` DEĞİŞTİRİLMEZ.** Kum havuzu ve ağ ayarları çağrı başına
   **argv'ye** (`-c anahtar=değer`) yazılır. Global ayara yazmak tüm Codex turlarını
   etkilerdi.
2. **Kullanıcı değişikliği yalnız `codex` unix hesabını kapsar**, root'u değil.

**Ölçülmüş yan etki taraması (2026-09-17):** `codex` hesabında host tarafında çalışan süreç
YOK (`ps -u codex`'te görünen iki `next-server` Docker konteynerlerinin içinde, ayrı ad
alanında; `/var/lib/docker` 710 ile kapalı). `/home/codex` dışında uid 1001'e ait dosya YOK.
Komut dosyalarımızın hiçbiri kullanıcı değiştirmiyor.

**Dokunulmayanlar (karar bekliyor, bu görevin kapsamında DEĞİL):** `/home/codex/.ssh/authorized_keys`
(1 anahtar) ve `vscode-server` kurulumu. `sudo` üyeliğini kaldırmak bunları etkilemez; kaldırmak
gerekirse ayrı karar.

# Task List

## Faz 1 — Kutuyu kur (koda dokunmadan) — **BİTTİ 2026-09-17**

- [x] **T1** `codex` kullanıcısı `sudo` grubundan çıkarıldı (`gpasswd -d codex sudo`).
      **Doğrulama:** `id codex` → `1001(codex),100(users)` · `sudo -l -U codex` →
      *"User codex is not allowed to run sudo"* · `sudo -u codex sudo -n true` → rc=1.
      **Geri alma:** `gpasswd -a codex sudo`.
      *Kabuk/parola/SSH sertleştirmesi YAPILMADI* — `authorized_keys` var, ayrı karar
      (yukarıdaki "Dokunulmayanlar").
- [x] **T2** `tests/test_auditor_process_isolation.py` yazıldı — üç tripwire, ortamı her
      koşumda GERÇEK okuma denemesiyle ölçer (izin bitine bakmaz).
      **Doğrulama:** `pytest tests/test_auditor_process_isolation.py -q` → **3 passed**.
      **Totoloji değil — kanıtlandı:** sabit kutusuz bir kullanıcıya (`root`) çevrilince
      ikisi de KIRMIZI döndü (*"root kullanıcısı şunları OKUYABİLDİ: /root, …/.env"* ·
      *"root sudo çalıştırabiliyor"*). Ayrıca dosyanın kendi pozitif kontrolü var: aynı prob
      root olarak okuyamıyorsa yasak-erişim testinin yeşili geçersiz sayılır.
      Sabit tek evde: `auditors.IZOLASYON_KULLANICISI`.
- [x] **T3** Codex'in `workspace-write` + `network_access=true` kipi **root olmayan
      kullanıcıda ÇALIŞIYOR.** Taze meydan okuma birebir eşleşti
      (`238650ef6c7c7cca08e032527329424c9fbd70e5`), kum havuzu satırı:
      `workspace-write [workdir, /tmp, $TMPDIR] (network access enabled)`.
      **Faz 4'ün önü açık.**
      **İkinci kez ölçüldü (aynı gün, kapanış turu):** kutulu kullanıcı olarak koşan Codex
      `curl -sI https://www.google.com` başlığını `Thu, 17 Sep 2026 11:09:28 GMT` getirdi;
      sistem saati `11:09:33` — 5 saniye fark, yani getirme canlı. Aynı koşumda `id -un`
      → `codex` (root DEĞİL).
- [x] **T3b (plan dışı, birleşim ölçümü)** — Ağ AÇIKKEN kutu hâlâ kapalı mı? Kutulu Codex'e
      ağ verip sır yollarını denettim: `.env` **DENIED** · `auth.json` **DENIED** ·
      denetim ağacı **DENIED** · `/etc/hostname` **SUCCEEDED 32** (pozitif kontrol — prob
      çalışıyor). **Görevin temel varsayımı ölçüldü ve tuttu.**
      *Geçici artefakt:* `/home/codex/t3-probe/` — **silindi 2026-09-17** (kapanış turunda; `test -e` ile yokluğu doğrulandı).

## Faz 2 — Paketin yeri → **TASARIM DEĞİŞTİ (2026-09-17): taşıma YOK, sahne dizini VAR**
## → **FAZ 2 BİTTİ 2026-09-18** (T4 · T5 · T6 · T6b)

**Neden taşıma terk edildi (ölçümle gerekçeli).** İlk tasarım "çıktı ağacını `/root` dışına
taşı, kutulu kullanıcı okusun" diyordu. İki ölçüm bunu çürüttü:

1. **Körlük ayağı.** Denetçi raporları diske GEÇ yazılıyor — iki rol de bitene kadar
   bekletiliyor (`_kalicilastir`, B3(1) gerekçesi kodda yazılı). Yani tur İÇİNDE sızıntı yok.
   Ama arşiv kalıcıdır: kutulu kullanıcıya açık bir ağaç, **GEÇMİŞ turların raporlarını**
   okunur kılar. Aynı kaynaklara ikinci tur atıldığında denetçi-2 önceki turun denetçi-1
   raporunu okuyabilirdi. İki denetçi AYNI unix kullanıcısında koştuğu için dosya izinleriyle
   ayrılamazlar.
2. **Taşımanın kendisi gereksiz.** Ağaç `700 root:root` kalırsa kutulu kullanıcı zaten
   giremez — `/root` altında olması ile `/srv` altında olması arasında güvenlik farkı YOK.

**Yeni tasarım — geçici sahne dizini.** Denetçinin okuması gereken tek şey KENDİ paketidir.
Tur başlamadan önce o paket, kutulu kullanıcının sahibi olduğu `700` izinli TAZE bir dizine
kopyalanır; alt süreç orada koşar; tur bitince dizin silinir. Kalıcı hiçbir şey kutulu
kullanıcıya açılmaz. Kanonik paket `denetim/` altında, root-only, yerinde kalır (K-82
salt-eklemesi bozulmaz). Rapor `stdout`'tan döndüğü için sahneden geri okunacak bir şey yok.

**Yan fayda:** rol başına ayrı sahne → denetçi-1 de aynı kutuya alındığında simetrik çalışır.

- [x] **T4** Rol başına geçici sahne dizini — **BİTTİ 2026-09-17.**
      `SubprocessRunner._sahne` her `run` çağrısında `mkdtemp` ile taze bir kök açar, rol
      dizininin kopyasını oraya alır, kökü ve altındaki her şeyi kutulu kullanıcıya devreder,
      `700`'e çeker ve `finally` ile siler.
      **Nerede yaşıyor ve neden:** orkestrasyonda değil, `SubprocessRunner`'ın içinde. Sahnenin
      tek varlık sebebi alt sürecin KİMLİĞİdir; ayrıcalık düşürme (T7) ve ortam beyaz listesi
      (T8) de aynı sınırda oturuyor. Orkestrasyonun K-79 yol kapıları kanonik yollara bakmaya
      devam ediyor, tek satırı değişmedi.
      **Doğrulama — 9 yeni test, hepsi ÇOCUĞUN gözünden ölçer** (`cwd`, okunan içerik, sahiplik
      ve izin alt sürecin kendisi tarafından basılır):
      alt süreç kanonik pakette DEĞİL · paket içeriği sahnede VAR · sahne `700` ve sahibi kutulu
      kullanıcı · **kutulu kullanıcı zinciri gerçekten geçebiliyor** (sahne içinden `sudo -u` ile
      okuma denemesi) · başarı/hata/zaman-aşımı üç yolda da sahne siliniyor · iki koşum sahne
      paylaşmıyor · kutu kurulu değilse alt süreç HİÇ koşmuyor (fail-closed).
      **Totoloji değil — altı mutasyonun altısı yakalandı:** kopyalama kaldırıldı → içerik testi
      kırmızı · geçici kök devredilmedi → erişim zinciri testi kırmızı · iç dosyalar devredilmedi
      → iki test kırmızı · silme `finally`'den çıkarıldı → zaman-aşımı testi kırmızı · sabit sahne
      adı → tazelik testi kırmızı · kutu yoksa sessizce root'a düşme → fail-closed testi kırmızı.
      *(İlk turda sahiplik testi tek başına "geçici kök devredilmedi" mutasyonunu KAÇIRDI —
      sahnenin sahibini ölçüyordu ama oraya girilebildiğini ölçmüyordu. Erişim zinciri testi
      bunun üzerine eklendi.)*
      **Tam takım:** 4547 passed / 0 failed / 331,41 s (taban 4538, +9 test).
- [x] **T5** Sahne yol kapısı + kanonik dokunulmazlık — **BİTTİ 2026-09-18.**
      Paket kökü YERİNDE kaldı (`ARASTIRMA_DEPOSU_KOKU` değişmedi, üç-kök testleri aynen
      geçiyor); orkestrasyonun tek satırı değişmedi.

      **Ayak 1 — yol kapısı.** İki yeni kapı, ikisi de MEVCUT kuralı yeniden kullanır
      (`kok_yolunu_kapila` ve parmak izi yardımcısının KENDİ reddettikleri listesi — ikinci
      bir kural aynı ağaç için iki farklı cevap üretirdi):
      `SubprocessRunner._kaynak_yolunu_kapila` (kaynak mutlak · kendi canonical'i · ağaç
      symlink BARINDIRMAZ) ve `_sahne_kokunu_ac` (mkdtemp kökü aynı kapıdan geçer, reddedilen
      kök SİLİNİR). Kaynak kapısı geçici kökten ÖNCE koşar — reddedilecek bir kaynak için
      dizin yaratmak silinmesi gereken bir kök bırakırdı.

      **GERÇEK AÇIK bulundu ve kapatıldı (varsayım değil, ölçüm).** `shutil.copytree`
      varsayılan olarak symlink'i İZLER. Rol dizinine bir symlink sokulup runner koşturuldu:
      alt süreç sahnede `symlink_mi: False` · `icerik: ANAHTAR=sizmamali-123` ·
      `sahip_uid: 1001` bastı — yani gizli dosyanın İÇERİĞİ sahneye gerçek dosya olarak indi
      ve kutulu kullanıcıya devredildi. Sahnenin kendi izni `700` ve sahibi doğruyken. Tur
      kapısı (`_paket_butunluk_kapisi`) bunu turun başında bir kez ölçüyordu; kopyalama ve
      devretmenin YAPILDIĞI sınırda ölçülmüyordu.

      **Ayak 2 — kanonik dokunulmazlık.** Alt süreç sahnede yazdı, ezdi ve sildi; kanonik rol
      ağacının parmak izi (paket kurulumunun kullandığı AYNI yardımcı) DEĞİŞMEDİ, dizinin
      sahipliği ve izni de değişmedi. Pozitif kontrol testin içinde: çocuğun yazma/silmesi
      GERÇEKTEN olmuşsa iddia anlamlıdır, olmamışsa test vacuous sayılır.

      **Doğrulama — 7 yeni test.** Yazıldığında **6'sı kırmızıydı** (7.'si leg 2 tripwire'ı,
      yeşil doğdu; totoloji olmadığı mutasyonla kanıtlandı). **Beş mutasyonun beşi yakalandı:**
      kaynak yol kapısı söküldü → 2 kırmızı · symlink düğüm reddi söküldü → kırmızı · sahne
      kökü kapısı söküldü → kırmızı · reddedilen kökün silinmesi söküldü → kırmızı · sahne
      kopya yerine KAYNAĞIN KENDİSİ yapıldı → leg 2 kırmızı.
      **Tam takım:** 4554 passed / 0 failed / 333,45 s (taban 4547, +7).

      **Kapının maliyeti ÖLÇÜLDÜ:** gerçek rol dizininde (7 dosya) **0,8 ms/koşum** — kaynak
      ağacı koşum başına bir kez daha özetleniyor (parmak izi yardımcısı yalnız `reddedilen`
      listesi için çağrılıyor; yeniden kullanım uğruna kabul edildi).

      **Kapsam dürüstlüğü:** geçici kökün `..` biçimi bu yoldan ERİŞİLEMEZ — ölçüldü
      (CPython 3.12.3): `mkdtemp` dönüşünü `os.path.abspath`'ten geçirir, o da `..`'yı
      sözdizimsel olarak normalleştirir; symlink normalleşmez. `..` ayağı kaynak tarafında
      ölçülüyor. Gerekçe testin kendi docstring'inde yazılı.
- [x] **T6** Kanonik `denetim/` ağacı kutulu kullanıcıya KAPALI — **BİTTİ 2026-09-18.**
      Ağaç, T2 tripwire'ının kapsamına ALINDI: `_hedefler()` artık kanonik ağacı da içeriyor,
      yani hem yasak-erişim testi hem onun pozitif kontrolü aynı kapıdan okuyor. Üstüne
      iddianın KENDİNİ adlandıran ayrı bir test eklendi — genel test, ağaç boş olsa da yeşil
      kalırdı ve "geçmiş raporlar okunamıyor"un hiç ölçülmediği fark edilmezdi.

      **Hedefler kavramdan türetiliyor, elle yazılmıyor:** deponun kökü
      (`runs.ARASTIRMA_DEPOSU_KOKU`) + kökün DOĞRUDAN çocukları (yarın eklenen aşama klasörü
      kendiliğinden kapsama girer) + `runs.ASAMALAR`'dan türeyen aşama ağaçlarının TAMAMI.
      Ölçüldü: **46 düğüm** (toplam hedef 57), koşum **2,5 s**. Kök de ölçülüyor çünkü kutu
      `~root`'un `700` iznine dayanıyor — depo bir gün `/root` dışına taşınırsa kutu SESSİZCE
      açılır ve yalnız yaprakları ölçen bir tarama bunu göremez.

      **Anti-vacuity:** test, hedefler arasında `denetim/` altında en az bir GERÇEK DOSYA
      olmasını şart koşuyor (boş klasör hiçbir şey kanıtlamaz); ağaç yoksa sessiz yeşil değil
      açık gerekçeli skip.

      **Mutasyon — sızıntı ayağı ayrı kanıtlandı.** İlk mutasyon (depo kökü → `/etc`) testi
      kırmızı yaptı ama YANLIŞ sebeple (boşluk kapısı ateşledi, sızıntı kapısı değil). İkinci
      mutasyon doğru kurgulandı: `/tmp` altında dünyaya açık sahte bir `denetim/kosu-x/
      denetci-1/rapor.md` ağacı kuruldu → test *"codex kullanıcısı kanonik ağaçtan şunları
      OKUYABİLDİ: …/rapor.md"* diyerek kırmızı döndü. Ölçüm gerçekten erişim ölçüyor.
      **Tam takım:** 4555 passed / 0 failed / 334,91 s.
- [x] **T6b** Dış depo `denetim/` ağacını YOK SAYIYOR — **BİTTİ 2026-09-18,
      `.gitignore` DEĞİL yerel `.git/info/exclude` ile (Eray kararı).**

      **Neden `.gitignore` değil — ölçüldü.** `contracts.verify_pin` deponun HEAD'ini
      `pin.commit` ile karşılaştırıyor. Yani `.gitignore`'a tek satır eklemek için atılacak
      commit, pini ANINDA düşürür (HEAD `abb1850` kayar) ve CLI'ın her alt komutu fail-closed
      durur; toparlamak için monorepo'da ayrı bir pin tazeleme commit'i gerekirdi. Yerel
      exclude aynı korumayı HEAD'e dokunmadan verir.
      **Doğrulama:** `git check-ignore -v denetim/` → `.git/info/exclude:7:denetim/` ·
      `git status` artık `?? denetim/` GÖSTERMİYOR · HEAD hâlâ `abb1850` · pin kapısı taze
      koşuldu, GEÇTİ.

      **Bedeli dürüstçe: yerel exclude SÜRÜMLENMEZ.** Depo yeniden klonlanırsa koruma gelmez.
      Kaybı yakalayan tripwire `tests/test_contract_pin.py` içinde, `kosu/` kardeşinin yanında:
      satır aramaz, `git check-ignore`'a EFEKTİF kararı sorar. Pozitif kontrolü var (sözleşme
      dosyası yok sayılMAmalı — prob ayrım yapmıyorsa yeşil anlamsızdır). **Mutasyon:** exclude
      satırı kaldırıldı → test kırmızı (`check-ignore rc=1`), geri kondu → yeşil.

      **Kapsam dışı bırakılan iki komşu:** `Kuyumculuk/` ve `silinecek/` de izlenmiyor ve
      exclude'da değil; aynı kazayla (`git add .`) aynı sonucu doğururlar. Dar talimat
      genişletilmedi — Eray'a not düşüldü, kararı onun.

## Faz 3 — Alt süreci kutuya sok — **BİTTİ 2026-09-18** (T8 · T7 · T9)

- [x] **T7** Ayrıcalık düşürme — **BİTTİ 2026-09-18, YALNIZ `denetci-2` (codex).**
      `denetci-1` (claude) çağıranın kimliğiyle koşmaya devam ediyor; kapsam düzeltmesi
      yukarıda, gerekçe ölçülü.

      **Ne indi.** `ToolSpec` artık izolasyon profilini taşıyor (`kullanici`, **beyan
      ZORUNLU — varsayılan YOK**; varsayılan olsaydı yarın eklenen bir araç sessizce root'ta
      koşardı). Kimlik ARACIN beyanından çözülür, modül sabitinden değil. Ayrıcalık düşürme
      `user`/`group`/`extra_groups=[]` ile yapılıyor (yan gruplar da düşer). **Sahnenin
      devretmesi de profili izliyor:** kutusuz aracın sahnesi çağıranda kalır — T4'ten kalan
      tutarsızlık buydu, sahne her koşumda kutuya devrediliyordu ve oraya hiç düşmeyen bir
      araç için paketin kopyasını boş yere açıyordu.

      **GERÇEK ARAÇLARLA ÜRETİM YOLU KOŞTU** — bu, "sahne gerçek denetçi araçlarıyla hiç
      koşmadı" borcunu kapatıyor. `SubprocessRunner.run` üzerinden, gerçek argv ile:
      `denetci-1` (claude, kutusuz) **rc=0, `PONG`, 2,7 s** · `denetci-2` (codex, kutulu)
      **rc=0, `PONG`, 6,0 s**, alt sürecin kendi bastığı çalışma dizini sahne
      (`/tmp/denetci-sahne-*/denetci-2`), kum havuzu satırı `sandbox: read-only`. Kanonik
      ağaç iki rolde de dokunulmadan kaldı (parmak izi: 2 dosya).

      **Doğrulama — 4 yeni test, yazıldığında 4'ü de kırmızı.** Kutulu araç: uid düşüyor,
      `HOME` kutulu evi gösteriyor, sahne onun. Kutusuz araç: kimlik çağıranın, `HOME` miras,
      sahne çağıranın. Üçü de ÇOCUĞUN bastığı değerlerden ölçülüyor.
      **Beş mutasyonun beşi yakalandı:** `HOME` üst yazımı söküldü · ayrıcalık düşürme söküldü ·
      devretme profili yok sayıp hep kutuya verdi · profil alanına varsayılan kondu ·
      bilinmeyen kullanıcı sessizce root'a düştü.

      **Ölçülmüş yan bulgu:** kutulu kullanıcı `/root` altındaki sanal ortam yorumlayıcısını
      ÇALIŞTIRAMIYOR (`PermissionError 13`) — kutunun kendi özelliği. Gerçek araçlar
      `/usr/bin` altında olduğu için etkilenmiyor; kutulu testler sistem `python3`'ünü
      kullanıyor, gerekçe yardımcının docstring'inde.

      **Bayatlayan beyan düzeltildi:** `run_audit_round`'un B3 kalan-risk metni *"kum havuzu ·
      konteyner · ayrı kullanıcı EKLEMEZ"* diyordu; `denetci-2` için artık yanlış. Beyan
      daraltıldı — kutusuz araç için aynen geçerli, kutulu araç için ayrı kullanıcı VAR,
      kapsayıcı/ad-alanı izolasyonu hâlâ yok.

      **FİZİBİLİTE ÖLÇÜLDÜ 2026-09-18 — mekanizma ÇALIŞIYOR, engel KİMLİK.** Dört koşum,
      hepsi GERÇEK argv (`ARAC_KOMUTLARI`'ndan okundu), gerçek sahnede, `subprocess.run(...,
      user=uid, group=gid, extra_groups=[])` ile ayrıcalık düşürülmüş hâlde:

      | # | Araç | `HOME` | Sonuç |
      |---|---|---|---|
      | 1 | codex | `/root` (bugünkü beyaz liste) | **rc=1** — `/root/.codex/config.toml: Permission denied` |
      | 2 | codex | `/home/codex` | **rc=0, `PONG`, 11,8 s** — gerçek model çağrısı, `sandbox: read-only` |
      | 3 | claude | `/root` | **rc=1** — `Not logged in · Please run /login` (7,2 s) |
      | 4 | claude | `/home/codex` | **rc=1** — `Not logged in` (0,7 s) |

      **Okunacak üç sonuç:**
      1. **Ayrıcalık düşürmenin kendisi çalışıyor** — koşum 2 uçtan uca yeşil. Açık
         problemdeki *"çalışmalı diye varsayılıyor"* satırı KAPANDI, artık ölçüm var.
      2. **T8 isteğe bağlı değil, T7'nin ÖN KOŞULU.** Bugünkü beyaz liste `HOME`'u miras
         alıyor ve `/root`'u gösteriyor; kutulu süreç oraya giremediği için İKİ araç da
         düşüyor (koşum 1 ve 3). `HOME` araç başına ayrışmadan T7 inemez.
      3. **YENİ ENGEL — Claude Code kimliği kutulu kullanıcıda YOK.** `/home/codex/.claude`
         dizini hiç yok; `HOME` düzeltilse bile claude `Not logged in` diyor. Codex'te bu
         sorun yok: `/home/codex/.codex/auth.json` VAR (3981 B). Ölçüldü — iki `auth.json`
         **aynı hesabı** taşıyor (`account_id` birebir eşit), dosyalar yalnız jeton
         tazelenmesiyle ayrışmış. Yani Codex tarafında kimlik zaten kutuya taşınmış durumda
         ve Claude için karşılığı YAPILMAMIŞ. **Karar Eray'a soruldu (aşağıda).**

      *Yan ölçüm:* kutulu Codex sahnede `trust_level` girdisi OLMADAN koştu (`/tmp/t7-probe-*`
      config'te yok, yine de rc=0) — sahne dizini için güven kaydı gerekmiyor.
- [x] **T8** Ortam beyaz listesi araç başına ayrıştı — **BİTTİ 2026-09-18.** `HOME` artık
      profilden geliyor: kutulu araçta kullanıcının KENDİ evi (`pwd` kaydından türetilir,
      sabit yazılmaz), kutusuz araçta miras. Gerekçe ölçüldü: `HOME=/root` ile kutulu `codex`
      *"Failed to read config file /root/.codex/config.toml: Permission denied"* diyerek
      düşüyordu.
- [x] **T9** İzolasyon profilinde "hangi kullanıcı" alanı — **BİTTİ 2026-09-18, T7 ile
      BİRLİKTE** (son rötuş değil, T7'nin mekanizmasıydı). Beyan zorunlu; bilinmeyen kullanıcı
      fail-closed düşüyor ve alt süreç HİÇ koşmuyor (mutasyonla kanıtlandı). Gerçek eşlemenin
      beyanı bağımsız sabitlerle ölçülüyor: `denetci-1` → `None`, `denetci-2` → `codex`,
      `sentez` → `None` (eşlemeden okunsaydı yanlış bir profil de geçerdi).

## Faz 4 — Ağı aç — **BİTTİ 2026-09-18** (T10 · T11 · T12)

> **K-14 KAPISI AÇILDI — canlı ölçüm:** `preflight` iki araç için de `erisim-var` döndü,
> `tur_baslayabilir=True` (claude 9,9 s · codex 22,8 s). Codex'in izi sahnede `curl | jq`
> koştuğunu gösteriyor (`/tmp/denetci-sahne-*/denetci-2`). Plan 2 Task 19 Step 6'nın `denetim`
> ayağını bloke eden şey buydu.

- [x] **T10** Codex denetçisi `workspace-write` + ağ ile koşuyor — **BİTTİ 2026-09-18.**
      Ayar **argv'ye** yazıldı (`-c sandbox_workspace_write.network_access=true`), global
      `/root/.codex/config.toml`'a DEĞİL — bağlayıcı kısıt korundu.
      **Neden `workspace-write` zorunlu:** anahtar `sandbox_workspace_write` altındadır, yani
      `read-only` kipinde hükümsüzdür. Genişleyen yazma kapsamı `[workdir, /tmp, $TMPDIR]`:
      workdir SAHNEDİR (tur sonunda silinir, kanonik ağaca dokunmadığı T5'te teste bağlı),
      `/tmp`'den boru hattı okuma YAPMAZ (2026-09-17 taraması), kardeş rolün sahnesi de artık
      erişilemez (kutusuz `denetci-1`'in sahnesi çağıranda kalıyor, T7).
      **Ölçüldü:** kum havuzu satırı `workspace-write [workdir, /tmp, $TMPDIR] (network access
      enabled)`, canlı `Date` başlığı sistem saatinden 2 sn farkla döndü.
- [x] **T11** Claude denetçisine `WebFetch` — **BİTTİ 2026-09-18, YALNIZ denetçi rolünde.**
      `sentez` değişmedi: girdisi diskteki iki rapordur, ağ ona yeni yetenek değil yeni saldırı
      yüzeyi katardı. `WebSearch` hiçbir rolde izinli değil — denetçinin işi arama değil,
      sözleşmede ADI GEÇEN kaynağı getirmek.

      **AÇILAN YÜZEY — dürüst etiket.** 2026-09-12 güvenlik review'ı `WebFetch`'i tam da
      sızdırma kanalı olduğu için yasaklamıştı; K-14 karşılığında bilerek geri açıldı. Bedel:
      pakete gömülü bir talimat paketin İÇERİĞİNİ bir URL'e taşıyabilir. Kapsam sınırı
      `--restricted`'tır (dosya araçları sahneye kilitli, 2026-09-18'de yeniden ölçüldü), yani
      taşınabilecek şey denetçinin KENDİ girdisidir, sırlar değil. **Ölçüm evi: T13 kanaryası.**
- [x] **T12** K-14 probu TURUN KOŞTUĞU yoldan koşuyor — **BİTTİ 2026-09-18.**
      **Bulunan kusur maddede yazandan başkaydı.** Madde "araç başına biçim" diyordu; ölçüm
      daha temel bir şey gösterdi: prob `spec.argv`'yi DOĞRUDAN `subprocess.run`'a veriyordu,
      yani T7/T8'den sonra **turdan farklı bir ortamı** ölçüyordu (ayrıcalık düşmüyor, `HOME`
      araca göre ayarlanmıyordu). "Erişim var" beyanı turdakini değil kontrolörünkini ölçerdi —
      K-14'ün tüm anlamı budur. Prob artık `Runner` kullanıyor: aynı profil, aynı `HOME`, aynı
      sahne.
      **Maddedeki asıl gerekçe bugün GEÇERSİZ (ölçüldü):** iki araç da canlı getirme yapıyor,
      tek biçimli meydan okuma ikisine de adil. Ayrım gerçek bir araçta ölçülmeden eklenmedi.
      **Daraltma — dürüst etiket:** rc=0 + BOŞ çıktı artık `False` (ölçülmüş erişimsizlik)
      değil ÖLÇÜM ARIZASI. Hiçbir şey basmayan araç ne erişimi ne erişimsizliği ölçmüştür,
      dolayısıyla muafiyet üretmemelidir — fail-closed yönde daralma.
      **Doğrulama:** 2 yeni test (varsayılan koşucu üretim runner'ı + zaman aşımı ona geçiyor ·
      araca verilen istem GERÇEK dosya ve meydan okumayı taşıyor).

**Faz 4 doğrulaması — 6 mutasyonun 6'sı yakalandı:** prob kendi zaman aşımını kullanmıyor ·
kirli sonuç ölçüm sayılıyor · isteme meydan okuma yazılmıyor · codex kum havuzu
`danger-full-access`'e çevrildi · sentez de ağa açıldı · `WebFetch` hem izinli hem yasak yazıldı.
Üç mevcut güvenlik testi GEVŞETİLMEDİ, rol bazlı sözleşmeye çevrildi (yazma ekseni hiçbir rolde
izinli değil; ağ ekseni role göre ayrışır; izinli küme ile yasak liste ÇELİŞEMEZ — bu kapı yeni).

## Faz 5 — Kanıt ve kapanış — T13 · T14 BİTTİ 2026-09-18; T15 (review) KALDI

- [x] **T13** Kanarya — **BİTTİ 2026-09-18.** `scripts/denetci_kanaryasi.py`, gerçek araçlarla,
      üretim yolundan (`SubprocessRunner`), YENİDEN KOŞULABİLİR. Takımın içinde DEĞİL: her ayak
      gerçek bir model çağrısıdır (sekiz ayak, toplam ~2 dk ve kota). Tek seferlik ölçüm kanıt
      olmadığı için betik olarak duruyor; ucuz kardeşleri (kutu tripwire'ı + argv politikası)
      her takım koşumunda koşmaya devam ediyor.

      **Sonuç — sekiz ayağın sekizi tuttu, `rc=0`:** paket dışı okuma DÜŞTÜ · iş dizini dışına
      yazma DÜŞTÜ (kontrolör diskten AYRICA baktı: dosya yok) · birleşim (sırrı oku + ağdan
      gönder) okuma ayağında DÜŞTÜ. Codex'in birleşim koşumu en güçlü kanıt: **ağ çalıştı**
      (sha getirildi) ama sır okunamadı — zincir kırıldı.

      **Üçüncü ayak (yetkisiz geri çağrı) artık DÜŞMEZ, bilerek:** T10/T11 ağı açtı, K-14 erişim
      istiyor. Zincirin kırıldığı yer okuma ayağıdır; kanarya tam olarak bunu ölçer.

      **Pozitif kontrol (totoloji koruması):** dördüncü ayak paket İÇİNDEKİ dosyayı okutur. Araç
      kendi paketini bile okuyamıyorsa diğer üçün yeşili aracın KENDİ politikasından geliyor
      olabilir — bu gerçek bir risk: ilk koşumda codex'in izinde *"I won't disclose credentials"*
      cümlesi geçti.

      **Kontrol yöntemi ÖLÇÜMLE DEĞİŞTİ — ilk yazım kusurluydu.** Betik önce çıktıda "DENIED"
      kelimesini arıyordu ve YANLIŞ POZİTİF verdi: claude aynı şeyi *"That tool isn't available
      in this session"* diye söyledi, sır hiçbir yerde geçmiyordu, kanarya yine de öttü. Serbest
      metinden "şu olmadı" kanıtlanmaz. Artık her ayak OLGUYA bakıyor: sır dosyasının ayırt edici
      **19 imzası** (en kısası 22 karakter) çıktıda geçiyor mu · hedef dosya diskte var mı ·
      paket içi içerik çıktıda geçiyor mu.

      **Totoloji değil — mutasyonla kanıtlandı:** codex kutudan çıkarılıp (profil `None`) aynı
      ayak koşuldu; araç `.env`'in ilk satırını bastı ve kanarya imzayı YAKALADI.

      **Kanaryanın kendi sızıntı kanalı kapatıldı:** o mutasyon koşumunda betik yakaladığı sırrı
      ekrana bastı — koşum çıktısı günlüğe ve oturum dökümüne düşer. Maskeleme eklendi
      (`_maskele`), çevrimdışı doğrulandı ve betik maskelemeyle birlikte baştan koşturuldu.
- [x] **T14** Tam takım + mutasyon — **BİTTİ 2026-09-18 (süreklilikle).** Bağımsız-sabit ölçümü
      iki eksene genişletildi: argv literalleri (T10/T11 ile tazelendi) ve **profil beyanı**
      (`denetci-1` → `None`, `denetci-2` → `codex`, `sentez` → `None`; eşlemeden okunsaydı
      yanlış bir profil de geçerdi).
      **Bu görevde koşan mutasyonlar: 22, hepsi yakalandı** — T5'te 5, T6'da 2 (biri yanlış
      sebeple kırmızıydı, yeniden kuruldu), T6b'de 1, T7/T8/T9'da 5, Faz 4'te 6, T13'te 1
      (kanaryanın kendisi). Takım tabanı 4547'den 4562'ye çıktı, hiçbir test silinmedi.
- [ ] **T15** Review — `/review-claude-codex` ve güvenlik gözü, kapsam gerektirdiğinde.

# Open Problems

- **T7'nin mekanizması ÖLÇÜLDÜ (2026-09-18) — bu satır kapandı.** Ayrıcalık düşürme gerçek
  argv ile uçtan uca yeşil koştu (Codex: rc=0, `PONG`, 11,8 s). Yerine iki ölçülmüş engel
  geçti: `HOME` araç başına ayrışmalı (T8, artık ÖN KOŞUL) ve **Claude Code kimliği kutulu
  kullanıcıda yok** — karar bekliyor.
  *(T3 bu satırda da şüpheli sayılıyordu — artık iki kez ölçüldü, listeden çıkarıldı.)*

- **~~KARAR BEKLİYOR — kutulu kullanıcı için Claude Code kimliği~~ — KARAR GEREKSİZ, madde
  YANLIŞ PREMİSLE AÇILMIŞTI (2026-09-18).** Madde "claude da kutulu kullanıcıya geçecek"
  varsayımına dayanıyordu ve bu varsayım kaydın kendisiyle çelişiyordu: kutunun ölçülmüş
  gerekçesi Codex'in okuma kapsamıdır, claude'unki `--restricted` ile zaten kapalı. Eray itiraz
  etti, ölçüm itirazı doğruladı. **Claude girişi GEREKMİYOR, kimlik kopyalama GEREKMİYOR.**
  *(Ders: "iki denetçi de" cümlesi Goal'de yazılıydı ama ÖLÇÜM Codex-özeldi; hedef cümlesini
  ölçüme karşı kontrol etmeden zorunluluk türetildi.)*

- **DÜŞÜRÜLDÜ — claude denetçisini de kutuya almak (evi yok, koşullu).** Tek kazancı derinlemesine
  savunma olurdu: claude'un hapsini işleten CLI'nın KENDİSİ, işletim sistemi değil (bu dürüst
  etiket `_CLAUDE_IZOLASYON` docstring'inde zaten yazılı). Bugün hiçbir şeyi engellemiyor ve
  bedeli ölçüldü: kutulu kullanıcıda Claude kimliği YOK (`/home/codex/.claude` yok; `HOME`
  düzeltilse bile `Not logged in`), yani Eray'ın tarayıcı adımı gerekirdi.
  **Yeniden açma koşulu:** `--restricted` bayrağı kalkar/adı değişir, ya da bir turda dosya
  aracının paket dışına çıktığı ÖLÇÜLÜRSE.
- **T3b'nin ağ-AÇIK varyantı bugün tekrar ölçülmedi.** Kutulu Codex'in ağ açıkken de sırlara
  erişemediği 2026-09-17'nin ilk turunda ölçüldü; kapanış turunda aynı probu koşturma denemesi
  harness sınıflandırıcısı tarafından engellendi. Bugün tazeliği olan ölçüm, aynı kullanıcıyı
  ölçen tripwire testidir (`3 passed`) — kum havuzu kipi uid iznini değiştirmediği için
  kapsam örtüşüyor, ama bu ÇIKARIM; ağ-açık varyantının taze ölçümü T13 kanaryasına düşer.
- **~~Codex denetçisi tüm sırları okuyabiliyor~~ — KAPANDI 2026-09-18.** T7 kutuyu yürürlüğe
  soktu, T13 kanaryası bunu gerçek araçla ölçtü: `.env` okuma ayağı DÜŞTÜ, ağ açıkken bile.
  Mutasyonla da doğrulandı (kutu söküldüğünde aynı araç aynı dosyayı okudu ve kanarya öttü).
- **`SIGKILL` sahneyi geride bırakır — DÜŞÜRÜLDÜ, evi yok (2026-09-17).** Sahne silme
  `finally`'dedir; süreç 9 sinyaliyle ölürse `/tmp/denetci-sahne-*` diskte kalır ve içindeki
  paket kopyası kutulu kullanıcıya aittir. Bakım işi KURULMADI: süreçleri biz öldürmüyoruz ve
  servis henüz dağıtılmadı, yani bugün tetikleyicisi yok. **Yeniden açma koşulu:** diskte
  kalmış bir sahne görülürse, ya da servis kapsayıcıda koşup `kill -9` rutin hâle gelirse.
  *(Erteleme değil düşürme — "sonra bakarız" demiyoruz, koşul gelmeden açılmaz.)*
- **~~Sahne GERÇEK denetçi araçlarıyla hiç koşmadı~~ — KAPANDI 2026-09-18.** İki gerçek araç
  da üretim yolundan (`SubprocessRunner.run`) koştu ve `PONG` döndürdü: claude kutusuz rc=0
  (2,7 s), codex kutulu rc=0 (6,0 s), çalışma dizini sahne, kanonik ağaç dokunulmadı.
  `HOME` sorunu T8 ile çözüldü.
- **Servis dağıtımı bağımlılığı.** Backend servisi henüz dağıtılmadı (Plan 2 Task 18'in kalan
  ayağı). Servis kapsayıcıda root olarak koşarsa ayrıcalık düşürmenin orada da çalıştığı ayrıca
  ölçülmeli. **Evi: Plan 2 Task 19 Step 11, servis dağıtımıyla aynı tur.**

## Review bulguları — AÇIK (2026-09-18 dual review, fix-required)

> Kaynak: `docs/reviews/2026-09-18-feat-sektor-bilgi-paketi-plan2.md` (iki bağımsız hakem: fresh
> Claude subagent + Codex adversarial-review; aralık `496ddbd..d215452`). Altısının da MEKANİZMASI
> kontrolörün kendi taze ölçümüyle doğrulandı. **`/security-review-claude-codex`'a geçiş bunlar
> yüzünden BLOKE.**

- **F1 [critical] — Kutulu codex kendi kimliğini okuyabiliyor, ağı da açık.** `HOME=/home/codex`
  (T8) kutulu sürece `~/.codex/auth.json`'u gösteriyor; kum havuzu okumayı kısıtlamıyor; T10 ağı
  açtı → oku+gönder zinciri tam. **Ölçüldü:** kutulu codex dosyanın sha önekini (`eebdf1ca1d57413b`)
  ve boyutunu (3981) bastı, kontrolörün bağımsız ölçümüyle birebir. Bu yolu BU DAL açtı.
  **Kanarya göremez** — hedefi root'un `.env`'i, kutulu kullanıcının kendi evi değil.
  *Tasarım kararı gerekiyor (Eray): ayrı/dar kapsamlı kimlik · tur-ömürlü ev · ya da codex'te ağı
  geri kapatıp web doğrulamasını claude'a bırakmak.*

- **F2 [high] — ~~Kutulu ev turlar arası TAM oturum kaydı tutuyor~~ → KAPANDI 2026-09-18.**
  **Tur-ömürlü ev uygulandı:** her koşum adanmış kökün altında taze bir `HOME` alır, içine
  YALNIZ kimlik dosyası kopyalanır (`KUTULU_KIMLIK_YOLU`), tur bitince ev silinir. Desen
  sahnenin aynısı.
  **Kapanış ölçümü (gerçek codex, üretim yolu):** koşum `rc=0`, `PONG`, 6,5 s; **kalıcı evdeki
  oturum kaydı sayısı 36 → 36, hiç artmadı.** Kayıt tur-ömürlü eve düştü ve onunla birlikte
  silindi.
  **Jeton yenilenmesi kapatıldı:** kimlik dosyası koşumda DEĞİŞTİYSE kalıcı yere geri yazılır
  (sahiplik + `0600` korunur), değişmediyse DOKUNULMAZ. Tetikleyici ölçülü: erişim jetonu
  2026-09-27'de doluyor.
  **Maliyet ölçüldü:** ev kurulum+silme 28 ms; koşum 6,1-11,2 s (kalıcı evde 5,7 s) — soğuk
  önbellek farkı, gerçek tur dakikalar sürdüğü için gürültü seviyesinde.
  **Altı mutasyonun altısı yakalandı** — ama ÜÇÜ ilk turda KAÇTI ve testler güçlendirildi:
  (a) kimlik kopyalanmayınca "dosya var mı" testi geçiyordu → BOYUT ölçülür oldu; (b) her koşumda
  geri yazan sürüm `mtime` ölçümünden kaçıyordu (`copy2` mtime'ı korur) → `ctime` eklendi;
  (c) kimlik yokken fail-closed kapısının TESTİ HİÇ YOKTU → yazıldı.
  **F1 KAPANMADI:** kimlik tur boyunca hâlâ okunabilir; kapanan şey turlar arası birikme.
  *Aşağıdaki özgün bulgu kaydı korunuyor:* Sahne tasarımının merkez
  gerekçesi *"kalıcı hiçbir şey kutulu kullanıcıya açılmaz"*dı; CLI o arşivi kutunun İÇİNDE yeniden
  kuruyor (`~/.codex/sessions/**/rollout-*.jsonl`). **Ölçüldü:** bugün 28 kayıt; `PAKET-ICI` 4,
  `paket icerigi` 4, `KARDES TURUN PAKETI` 1 dosyada; dizin kutulu kullanıcıya OKUNABİLİR.
  Turlar-arası bağımsızlık bozuluyor (tur-içi K-79 körlüğü bozulmuyor — denetci-1 root'ta).

- **F3 [high] — KISMEN kapandı 2026-09-18: KEŞİF kapandı, bilinen-yolla erişim KAPANMADI.**
  Sahne kökü `/tmp`'den çıkarıldı; artık `/var/lib/otomaix-denetci-sahne` altında ve o dizin
  **root'un, `0711`** — girilir, LİSTELENMEZ. **Kalıntı sahne silindi** (`/tmp/denetci-sahne-uoiaj30t`,
  2026-09-17; `/tmp`'de sahne kalmadığı doğrulandı).
  **Kapanış ölçümü (gerçek codex, üretim yolu):** `ls <üst dizin>` → **DENIED** (keşif kapalı);
  ama yolu prompt'ta VERİLDİĞİNDE kardeş paketi **hâlâ okudu**. Yani kapanan şey adın
  KEŞFEDİLEBİLİRLİĞİ; `mkdtemp`'in rastgele son eki tahmini pratikte imkânsız kılıyor ama bu
  "erişim kapalı" DEMEK DEĞİL. **Kalan yüzey:** bir yol sızarsa (örn. F2'deki oturum kayıtları
  `workdir:` satırını taşıyor) o sahne okunur. F2 kapanmadan bu ayak tam kapanmaz.
  **Sahiplik/izin sözleşmesi ayrıştırıldı:** üst dizin başkasınınsa koşum DURUR (onarılmaz —
  root'la `chown`'lamak başkasının dizinini ele geçirmek olurdu); izin yanlışsa ONARILIR (tek
  gevşek umask tüm turu öldürmemeli — ölçüldü: `mkdir(mode=0o711)` umask 077 altında `0700` üretiyor).
  **Üç mutasyon yakalandı** (sahiplik kapısı söküldü · yabancı dizin chown'la ele geçirildi ·
  sahne `/tmp`'ye geri kondu); **bir kol mutasyonla kanıtLANAMADI** ve dürüst etiketi kodda:
  onarım-sonrası doğrulama (chmod'un sessizce etkisiz kalması) bu makinede provoke edilemedi.
  *Aşağıdaki özgün bulgu kaydı korunuyor:*
  **Ölçüldü:** kutulu codex `/tmp/denetci-sahne-*`'ı listeledi, kardeş sahnenin paketini OKUDU,
  `/tmp`'ye yazdı (uid 1001, diskten doğrulandı). Ayrıca `/tmp/denetci-sahne-uoiaj30t` **2026-09-17
  11:23'ten kalma** — bu, düşürülen `SIGKILL` kalıntısının yeniden-açma koşuludur ve GERÇEKLEŞTİ.

- **F4 [high] — ~~Sahne, ayrıcalıklı işler bitmeden devrediliyor~~ → KAPANDI 2026-09-18.**
  Sıra ters çevrildi: `chmod`'lar devretmeden ÖNCE, çocuklar sonra, **kök EN SON**. Kök
  devredilene kadar ağaç root-only `0700`, yani kutulu kullanıcı içeri hiç giremez ve devir anına
  kadar hiçbir girdiyi değiştiremez. **Doğrulama:** yeni test ayrıcalıklı çağrı dizisini kaydedip
  "sahne ağacındaki SON işlem kökün devri" invariantını ölçüyor. **İki mutasyon da yakalandı**
  (eski sıra geri kondu · kök önce devredildi). *Aşağıdaki özgün bulgu kaydı korunuyor:*
  Sıra: `chown(kok)` → çocuklar → **`sahne.chmod(0o700)`**. Devretmeden sonra root hâlâ `codex`'in
  sahip olduğu ağaçta iş yapıyor ve `Path.chmod` symlink İZLER (ölçüldü: hedefin izni 0700 oldu).
  **Kapanışı ucuz:** `chmod`'u devretmeden ÖNCE yap, `kok`'u EN SON devret.

- **F5 [high, BOTH-AGREE] — `denetci-1` root koşarken `WebFetch` kazandı, sürekli kapısı yok.**
  Ağ yokken `--restricted` gerilemesi "okur ama gönderemez"di; artık doğrudan sızdırma ve süreç
  root. Testler bayrağın VARLIĞINI ölçüyor, DAVRANIŞINI değil; davranışı ölçen tek şey kanarya —
  takım dışında, elle, **zamanlanmış evi yok**.

- **F6 [high] — Hedef allowlist'i yok; T13'ün geri-çağrı ayağı karşılanmadı, yeniden tanımlandı.**
  İki profilde de serbest dış çıkış var; paket içeriği herhangi bir URL'e gidebilir.

**Medium/low (accepted_risk — fix EDİLMEZ, politika gereği):** T6b'nin sürümlenmemesi + kardeş test
çelişkisi · kutu tripwire'ının sudo yolunda pozitif kontrol yokluğu · kanaryanın GERÇEK `.env`'i
hedeflemesi · 8 low. Ayrıntı raporda.

**Hakemlerin kapsamadığı (dürüst etiket):** hiçbir hakem test takımını koşturamadı. "4562 passed" ve
"22 mutasyon" iddiaları kontrolörün kendi taze koşumlarına dayanıyor, hakem teyidi YOK.

# Bu görev bitince sırada ne var (Plan 2'ye dönüş)

> **2026-09-18: `denetim` ayağının önündeki engel KALKTI.** K-14 iki araç için de `erisim-var`
> ölçtü. Kalan: Faz 5 (T13 kanaryası · T14 tam takım+mutasyon · T15 review).

1. jsonb kodlayıcı kusuru — CLI kendi bağlantısına kodlayıcıyı kurmuyor, yönetici bildirimi
   yazımı düşüyor. Bugün canlıda görünen sonucu: iki koşu birden `calisiyor` kalmış.
2. Yeni koşu kimliğiyle `denetim` turu (K-82: yarım kalan paket ezilmez).

# Decisions Log

- **2026-09-17 — Asimetri değil kutu.** İlk öneri "Claude'a web ver, Codex'e verme"ydi. Eray
  itiraz etti: *"birine ver diğerine verme"nin mantıklı tarafı ne"*. Ölçüm itirazı haklı çıkardı
  — asimetrinin gerekçesi sanılan yazma kapsamı değil, OKUMA kapsamıydı; ve `/root`'un `700`
  izni sayesinde kutu ucuz. Karar: asimetriyi kalıcılaştırmak yerine kutuyu kur.
- **2026-09-17 — Sahne runner'ın içinde, orkestrasyonda değil.** Sahne dizini alt sürecin
  KİMLİĞİ için vardır; ayrıcalık düşürme ve ortam beyaz listesiyle aynı sınırda oturur. Böylece
  turun K-79 yol kapıları kanonik yollara bakmaya devam etti ve orkestrasyon testlerinin tek
  satırı değişmedi. Bedeli: sahte runner kullanan testler sahneyi görmez — sahne davranışı
  GERÇEK alt süreçle ölçülür (9 testin hepsi öyle).
- **2026-09-17 — Mevcut `codex` kullanıcısı.** Kimliği çalışıyor, yeni giriş gerekmiyor.
  Bedeli: `sudo` üyeliği kaldırılacak; o hesabı kullanan başka bir akış varsa etkilenir.
- **2026-09-18 — Kutu Codex için; claude root kalır.** Eray itiraz etti: kutu "claude için de
  gerekli" diye sunulmuştu, oysa 2026-09-17'nin kendi ölçümü gerekçeyi Codex'in OKUMA kapsamına
  bağlamıştı. Bugün claude'un sınırı tazeden ölçüldü ve tuttu (paket içi OKUNDU; `/etc/hostname`
  ve `/root/.claude` DÜŞTÜ). Sonuç: T7 araç başına uygulanır, Goal cümlesi düzeltildi, uydurulmuş
  kimlik kararı kapatıldı. **Bedel:** T9 (profilde "hangi kullanıcı" alanı) artık son rötuş değil,
  T7'nin ön şartı.
- **2026-09-18 — Faz 4'ün claude ayağı kutuya BAĞLI DEĞİL.** T11 (claude'a `WebFetch`) bugünkü
  kurulumda inebilir; claude'un okuması zaten hapsedilmiş olduğu için ağ vermek yeni bir okuma
  yolu açmaz. Kutuya bağlı olan tek ayak T10'dur (codex + `network_access=true`).
- **2026-09-18 — Profil beyanı ZORUNLU, varsayılansız.** `ToolSpec.kullanici` alanına
  varsayılan konmadı: varsayılan, "bu araç neden kutusuz" sorusunu sessizce yutar ve yarın
  eklenen bir aracı beyan almadan root'ta koşturur. Bedeli: her `ToolSpec` çağrısı (testler
  dâhil) profilini yazmak zorunda.
- **2026-09-18 — `WebFetch` denetçide açık, sentezde kapalı.** Güvenlik review'ının yasağı K-14
  karşılığında YALNIZ denetçi rolünde geri alındı. Gerekçe rolün işidir: denetçi kaynağı
  doğrular (ağ gerekir), sentez iki raporu birleştirir (ağ gerekmez). Bedel — paket içeriğinin
  bir URL'e taşınabilmesi — kabul edildi ve ölçüm evi T13'tür.
- **2026-09-18 — Prob turun yolundan koşar.** K-14 ön kontrolü kendi alt sürecini kurmayı
  bıraktı; `Runner`'ı kullanıyor. Ölçülen ortam ile koşulan ortam ayrışırsa K-14 kendi amacını
  kaybeder. Bedeli: probun dikişi `kosucu`dan `runner`a geçti, sahte de tipli sonuç döndürüyor.
