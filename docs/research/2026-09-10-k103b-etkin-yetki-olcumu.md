---
title: K-103 (b) — Paket tablolarına ETKİN yazma yetkisi ölçümü
date: 2026-09-10
kaynak_plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
kaynak_gorev: Task 15, Step 6
tur: olcum
---

# Neden bu ölçüm var

Plan Task 15, Step 6 bağlayıcı olarak şunu söyler: `role_table_grants` TEK BAŞINA
yetersizdir — üyelikle miras, sahiplik, `PUBLIC` grant'ı ve superuser görünmez, yani
*"zaten yetki yok"* diye YANLIŞ bir kapanış üretebilir. Ölçüm arayüz eki A2 ile **üç tabloya**
genişletildi: köken jetonu (`R8(c)`) yalnız `social.sector_packages`'a değil,
`social.sector_package_runs` ve `social.package_rollback_plans` satırlarına da yazılır; o iki
tabloya `UPDATE` edebilen kod **kendi kanıtı için jeton basabilir**.

# Ölçüm yöntemi

Betik: `k103b.py` (oturum scratchpad'i, kalıcı değil). Bağlantı dizesi betikte GÖRÜNMEZ;
uygulamanın kendi yapılandırmasından (`app.core.config.settings.DATABASE_URL`) alınır — yani
ölçülen kimlik API'nin **gerçek** kimliğidir, varsayılan bir tahmin değil.

Negatif yazma denemesi (d ayağı) iki kat güvenlidir: geri alınan bir işlemin içinde koşar **ve**
hiçbir satırla eşleşmeyen bir `WHERE` kullanır. Yetki denetimi satır eşleşmesinden önce
yapıldığı için kapı yine de ölçülür, ama hiçbir üretim satırı değişmez.

**Koşum:** `source .venv/bin/activate && python k103b.py` — 2026-09-10, `apps/social/backend`.

# Taze çıktı (birebir)

```
### (a) API kimliği
session_user   = otomaix
current_user   = otomaix
database       = otomaix
server_version = 18.3 (Debian 18.3-1.pgdg12+1)

### (c) Rol nitelikleri · üyelik · sahiplik · PUBLIC
superuser=True  inherit=True  bypassrls=True
rol üyelikleri = (yok)

social.sector_packages
  sahip = otomaix
  acl   = (acl yok → yalnız sahip; PUBLIC grant YOK)
  PUBLIC grant var mı = False
  (b) tablo yetkisi: INSERT=True  UPDATE=True  DELETE=True  TRUNCATE=True

social.sector_package_runs: TABLO YOK (migration dağıtılmamış)

social.package_rollback_plans: TABLO YOK (migration dağıtılmamış)

### (d) NEGATİF YAZMA DENEMESİ (geri alınan işlem, 0 satır eşleşir)
social.sector_packages: YAZMA KABUL EDİLDİ (yetki VAR)
social.sector_package_runs: atlandı (tablo yok)
social.package_rollback_plans: atlandı (tablo yok)
```

# Bulgular

1. **API kimliği `otomaix`'tir ve SUPERUSER'dır.** Ayrıca `bypassrls=True` ve üç tablonun da
   (var olanının) SAHİBİDİR. Bu, ölçümün en önemli sonucudur: `role_table_grants` sorgusu tek
   başına koşulsaydı `acl` boş göründüğü için *"grant yok"* okunur ve yanlış bir kapanış
   yazılırdı. Gerçek şudur — grant'a **ihtiyaç yok**, çünkü superuser tüm yetki denetimlerini
   atlar ve sahip zaten tam yetkilidir.

2. **`social.sector_packages`'a yazma yetkisi VARDIR ve ölçülmüştür** (d ayağı: yazma kabul
   edildi). Dört ayrıcalığın dördü de `True`.

3. **İki jeton tablosu CANLIDA YOKTUR** — migration `036` dağıtılmamıştır. Bu yüzden (b2)
   kolon-bazlı jeton ölçümü ve o iki tablonun negatif yazma denemesi **KOŞULAMADI**. Bu bir
   atlama değil, ölçümün sınırıdır: 036 dağıtıldığında (Task 18) tablolar aynı kimliğin
   sahipliğinde doğacaktır, yani sonucun aynı çıkması BEKLENİR — ama **bu bir tahmindir,
   ölçüm değildir** ve dağıtımdan sonra yeniden koşulmalıdır.

4. **PUBLIC grant'ı YOKTUR.** Ölçülen tek tabloda `relacl` boştur.

# Dürüst etiket — jetonun kalan riski AÇIKTIR

Plan Step 6'nın öngördüğü dürüst etiket bugün şu hâlini alır:

> Köken jetonunun *"aynı veritabanı kimliğiyle koşan kod kendi jetonunu basabilir"* kalanı
> **AÇIKTIR ve kapatıldığı İDDİA EDİLMEZ.**

Ölçüm bu kalanı yalnız doğrulamakla kalmıyor, **kapatma yolunu da daraltıyor**: kimlik
superuser VE tablo sahibi olduğu için `REVOKE` ile kapatılamaz — superuser yetki denetimini
atlar, sahip de kendine yeniden `GRANT` verebilir. Gerçek kapanış AYRI bir veritabanı
kimliği ister (uygulama için superuser olmayan, tabloların sahibi olmayan bir rol).

**Jetonun bugün ne yaptığı yine de gerçektir ve küçümsenmemelidir:** kanıtın uydurulmasını
uygulama katmanında imkânsız kılar (literal kanıt hiçbir geçişten geçmez), tek kullanımlığı
zorlar ve alanları parmak iziyle mühürler. Kapatmadığı şey, **veritabanına doğrudan bağlanıp
kendi jetonunu basan** bir saldırgandır — ve o saldırgan zaten paketi doğrudan da
yazabilirdi, yani jeton o senaryoda hiçbir zaman tek savunma hattı olarak tasarlanmadı.

# Sonraki adım — ADLANDIRILMIŞ EV

**Task 18 (ön-pilot dağıtım) manuel adım listesine girer:**

- **M-1 (yeni):** Uygulama için superuser OLMAYAN, `social` şemasındaki tabloların sahibi
  OLMAYAN ayrı bir veritabanı rolü açılır; API o rolle bağlanır. Yaşam döngüsü tabloları
  üzerinde yalnız gerekli `SELECT/INSERT/UPDATE` verilir, jeton kolonlarına `UPDATE`
  VERİLMEZ. **Rol adı bu ölçüm tekrarlanmadan migration'a YAZILMAZ** (plan Step 6 hükmü).
- **M-2 (yeni):** `036` dağıtıldıktan SONRA bu ölçüm yeniden koşulur; (b2) ve iki tablonun
  (d) ayağı o zaman ilk kez gerçek sonuç üretir.

Bu iki kalem **evsiz değildir**: evi Task 18'in dağıtım listesidir ve tetiği `036`'nın
canlıya çıkmasıdır.
