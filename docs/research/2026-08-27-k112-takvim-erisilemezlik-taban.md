---
title: K-112 — takvim erişilemezken bugünkü davranış (regresyon TABANI)
status: done
date: 2026-09-02
kaynak: Task 5 Step 1 (arayüz eki R13 ile YENİDEN YAZILMIŞ hâli)
yontem: Atılabilir pytest probu (`tests/_k112_probe.py`, koşumdan sonra silindi);
  her satırın yanında onu üreten komut + taze çıktı (İlke 9).
baglayicilik: YOK — bu not hiçbir davranışı bağlamaz, hiçbir kapı kurmaz.
---

# K-112 taban notu — takvim erişilemezken ne oluyor

**Bu not bir KAPI DEĞİLDİR.** Tek işlevi, Task 12'nin hata-enjeksiyon testlerinin karşı
koşacağı ölçülmüş tabanı vermektir. Ölçülen davranış, Task 12'nin *bağladığı* davranıştan
farklı çıkarsa bu bir REGRESYON değil, planın istediği değişikliktir (plan 230-242 ·
1356-1366: bağlama spec §11/§3.4 türevidir, bu ölçümün türevi değil).

## Koşulan komut

```
cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/_k112_probe.py -v -s
```

## Taze çıktı (2026-09-02)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /root/otomaix/apps/social/backend/.venv/bin/python
cachedir: .pytest_cache
rootdir: /root/otomaix/apps/social/backend
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-1.4.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 4 items

tests/_k112_probe.py::test_probe_a1_calendar_endpoint_when_table_missing 
[A1] uc nokta donusu: OkResponse(success=True, data=[])
PASSED
tests/_k112_probe.py::test_probe_a2_prompt_builder_without_special_day 
[A2] special_day=None -> 'ÖZEL GÜN' blogu var mi: False
[A2] uretilen govde: "=== KULLANICI İSTEĞİ (EN YÜKSEK ÖNCELİK — ŞABLON DEFAULT'LARINI GEÇERSİZ KILAR) ===\ntest\n=== KULLANICI İSTEĞİ SONU ===\n\n=== PLATFORM-SPESİFİK CAPTION'LAR ===\nAşağıdaki her platform için AYRI caption üret. Response'da JSON formatında `platform_captions` objesi dön, her platform için ayrı key ile.\n\ninstagram:\n  Uzunluk: 50-150 kelime, emoji kullanılabilir\n  Max hashtag: 15\n  Hashtag'leri CAPTION'DAN AYIR, response'da `instagram.first_comment` key'inde dön\n\n=== PLATFORM BİTİŞ ==="
PASSED
tests/_k112_probe.py::test_probe_b1_insert_draft_when_table_missing 
[B1] ISTISNA asyncpg.exceptions.UndefinedTableError: relation "social.public_holidays" does not exist
[B1] yazilan paket satiri: 0
PASSED
tests/_k112_probe.py::test_probe_b2_insert_draft_when_calendar_empty 
[B2] ISTISNA builtins.ValueError: paket içeriği yazım kapısını geçmedi: özel gün anahtarı sistem takviminde YOK: 'cumhuriyet-bayrami' — karşılıksız dönem pakete giremez (spec §4.4)
[B2] yazilan paket satiri: 0
PASSED

============================== 4 passed in 2.87s ===============================
```

## Ölçülen taban — tek paragraf

Bugün iki yüzey **ZIT** yönde düşüyor. **Okuma yüzeyi fail-OPEN:** `calendar.py::get_holidays`
kendi gövdesini bir `except Exception` ile sarıyor ve tablo yokken `data=[]` dönüyor
([A1]) — yani önyüz "bu yıl hiç özel gün yok" görür, hata görmez; kullanıcı özel gün
SEÇEMEZ, `special_day` boş gider ve `build_dynamic_content` ÖZEL GÜN bloğunu hiç basmaz
([A2]) — paket dönem kalıpları da o blokla birlikte sessizce düşer, çünkü
`render_special_day_lines` yalnız o bloğun içinden çağrılır (`prompt_builder.py:373`).
**Yazma yüzeyi fail-CLOSED:** `sector_package_lifecycle.insert_draft` takvimi DB'den
okur; tablo erişilemezse `asyncpg.exceptions.UndefinedTableError` çağırana kadar
yükselir ve hiçbir paket satırı yazılmaz ([B1]), tablo erişilebilir ama BOŞ ise
doğrulayıcı `ozel_gun` anahtarını sistem takviminde bulamaz ve `ValueError` ile reddeder
([B2]) — her iki hâlde de yazılan satır sayısı 0. Ek ölçülmüş ayrıntı: [B1] yolunda
istisna asyncpg transaction'ını da abort ediyor (`InFailedSQLTransactionError`, ilk
prob koşumunda gözlendi), yani aynı transaction'da devam eden bir çağıran da yazamaz —
fail-closed davranış tesadüfi değil, transaction düzeyinde de tutuyor.

**Etiket:** Yukarıdakilerin hepsi ÖLÇÜLMÜŞTÜR (komut + çıktı yukarıda). Doğrulanmayan tek
şey canlı ortamda takvimin nasıl erişilemez olacağıdır (tablo düşmesi mi, bağlantı hatası
mı, ağ mı) — prob tabloyu düşürerek en sert biçimi ölçtü; bağlantı-düzeyi hatalar ayrıca
ölçülmedi.
