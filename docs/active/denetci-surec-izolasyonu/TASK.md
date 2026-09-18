---
title: Denetçi alt süreçleri işletim sistemi kutusuna alınsın (S-2 kalıntısı)
status: active
started: 2026-09-17
last-touched: 2026-09-18
blocked-by: null
source_task: docs/active/sektor-bilgi-paketi-plan2/TASK.md
---

# Goal

İki denetçi alt sürecini root ayrıcalığından çıkarıp ayrı bir işletim sistemi kullanıcısının
altında koşturmak; ardından **ikisine de** ağ erişimi vermek. Bugün ağ yalnız Codex tarafında
tek kalan duvar olduğu için kapalı tutuluyor — kutu kurulunca o duvara gerek kalmaz.

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
- [ ] **T6** Kutulu kullanıcının kanonik `denetim/` ağacına GİREMEDİĞİNİ teste bağla
      (T2'deki tripwire'ın kapsamına alınır — bugün ölçüldü: **DENIED**).
- [ ] **T6b** Dış depoda `denetim/` **izlenmiyor ama `.gitignore`'da da DEĞİL** (`?? denetim/`).
      Yanlışlıkla commit edilirse pin düşer ve CLI'ın her alt komutu durur. `.gitignore`'a
      eklenmeli — `kosu/` zaten orada.

## Faz 3 — Alt süreci kutuya sok

- [ ] **T7** Ayrıcalık düşürme: alt süreç root değil, denetçi kullanıcısı olarak koşsun.
      Önce kırmızı test, sonra uygulama.
- [ ] **T8** Ortam beyaz listesi araç başına ayrışsın. Bugün `HOME` miras alınıyor ve `/root`'u
      gösteriyor; kutudaki süreç oradan kimliğini okuyamaz.
- [ ] **T9** İzolasyon profiline "hangi kullanıcı" alanı eklensin; bilinmeyen kullanıcı
      fail-closed düşsün (mevcut "her araç profilini beyan eder" yapısı genişletilir).

## Faz 4 — Ağı aç

- [ ] **T10** Codex denetçisi `workspace-write` + `network_access=true` ile koşsun.
- [ ] **T11** Claude denetçisinin `--tools` listesine `WebFetch` eklensin.
- [ ] **T12** K-14 ön kontrolü araç başına DOĞRU yolu ölçsün. Bugünkü tek biçimli prob
      canlı-getirme ölçüyor; yalnız arama dizini olan bir aracı haksız yere "erişimsiz" sayar.

## Faz 5 — Kanıt ve kapanış

- [ ] **T13** Kanarya testi — güvenlik review'ının kendi önerdiği üç ayak: paket dışı dosya
      okuma · iş dizini dışına yazma · yetkisiz geri çağrı. Üçü de DÜŞMELİ.
- [ ] **T14** Tam takım + mutasyon. Argv'yi bağımsız sabitlerle karşılaştıran mevcut test
      genişletilir (totoloji olmamalı).
- [ ] **T15** Review — `/review-claude-codex` ve güvenlik gözü, kapsam gerektirdiğinde.

# Open Problems

- **T7 ölçülmedi.** Ayrıcalık düşürmenin alt süreçte çalışacağı "çalışmalı" diye varsayılıyor;
  tutmazsa fazlar yeniden sıralanır. Tahmin kapıya çevrilmeyecek.
  *(T3 bu satırda da şüpheli sayılıyordu — artık iki kez ölçüldü, listeden çıkarıldı.)*
- **T3b'nin ağ-AÇIK varyantı bugün tekrar ölçülmedi.** Kutulu Codex'in ağ açıkken de sırlara
  erişemediği 2026-09-17'nin ilk turunda ölçüldü; kapanış turunda aynı probu koşturma denemesi
  harness sınıflandırıcısı tarafından engellendi. Bugün tazeliği olan ölçüm, aynı kullanıcıyı
  ölçen tripwire testidir (`3 passed`) — kum havuzu kipi uid iznini değiştirmediği için
  kapsam örtüşüyor, ama bu ÇIKARIM; ağ-açık varyantının taze ölçümü T13 kanaryasına düşer.
- **Codex denetçisi bugün, ağ olmadan da tüm sırları okuyabiliyor.** Dışarı gönderemiyor ama
  raporunu serbest metin alanlarıyla yazıyor (`gerekçe`, `iddia-özeti`) — enjekte edilmiş bir
  talimat bir anahtarı o alanların içine gömerse anahtar bizim veritabanımıza düz metin iner.
  Sızdırma değil, hijyen açığı. **Evi: bu görevin T13'ü** (kanarya kapsamına alınır).
- **`SIGKILL` sahneyi geride bırakır — DÜŞÜRÜLDÜ, evi yok (2026-09-17).** Sahne silme
  `finally`'dedir; süreç 9 sinyaliyle ölürse `/tmp/denetci-sahne-*` diskte kalır ve içindeki
  paket kopyası kutulu kullanıcıya aittir. Bakım işi KURULMADI: süreçleri biz öldürmüyoruz ve
  servis henüz dağıtılmadı, yani bugün tetikleyicisi yok. **Yeniden açma koşulu:** diskte
  kalmış bir sahne görülürse, ya da servis kapsayıcıda koşup `kill -9` rutin hâle gelirse.
  *(Erteleme değil düşürme — "sonra bakarız" demiyoruz, koşul gelmeden açılmaz.)*
- **Sahne GERÇEK denetçi araçlarıyla hiç koşmadı.** Dokuz test zararsız bir alt süreçle
  ölçüldü. `HOME` hâlâ `/root`'u gösteriyor ve kutulu kullanıcı oraya giremez — gerçek CLI
  sahnede kendi kimliğini bulamayabilir. **Evi: T8.**
- **Servis dağıtımı bağımlılığı.** Backend servisi henüz dağıtılmadı (Plan 2 Task 18'in kalan
  ayağı). Servis kapsayıcıda root olarak koşarsa ayrıcalık düşürmenin orada da çalıştığı ayrıca
  ölçülmeli. **Evi: Plan 2 Task 19 Step 11, servis dağıtımıyla aynı tur.**

# Bu görev bitince sırada ne var (Plan 2'ye dönüş)

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
