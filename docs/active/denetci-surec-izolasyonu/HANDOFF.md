---
task: denetci-surec-izolasyonu
written: 2026-09-18
---

# Resume From

**Sıradaki iş: dual review'ın ucuz iki fix'i (Eray kararı 2026-09-18).**

1. **F4 — sahne devretme sırası.** `SubprocessRunner._sahne` içinde `sahne.chmod(0o700)` devretmeden
   SONRA koşuyor; `Path.chmod` symlink İZLER (ölçüldü). Sıra ters çevrilecek: `chmod`'lar önce,
   `kok`'un devri EN SON. Önce kırmızı test.
2. **F3'ün bir ayağı — sahne kökü `/tmp` dışına.** Kutulu codex `/tmp`'yi yazılabilir görüyor
   (`workspace-write` kum havuzu), dolayısıyla kardeş/kalıntı sahneleri okuyabiliyor. Sahne kökü
   kutulu kullanıcının listeleyemediği bir üst dizine taşınacak. **Ayrıca:**
   `/tmp/denetci-sahne-uoiaj30t` (2026-09-17 11:23'ten kalma) temizlenecek.

**Ertelenmeyen ama AYRI konuşulacak:** F1 (kritik — kutulu kimlik + ağ), F2 (oturum kayıtları
kutulu evde kalıcı), F5 (`denetci-1` root + `WebFetch`, sürekli kapı yok), F6 (hedef allowlist'i
yok). Dördü de tasarım kararı gerektiriyor; **evleri TASK.md "Review bulguları" bölümü.**

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest -q` → beklenen **4562 passed**.
⚠️ **Tek koşum.** İki pytest oturumu aynı anda koşarsa ortak test şablon veritabanını birbirinden
çekerler ve sahte hatalar üretirler.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, HEAD `0683749`. Çalışma ağacı: TASK+HANDOFF güncel
(commit bekliyor). **22 commit push EDİLMEDİ.**

# Verification

**Bu oturumda KOŞAN komutlar ve TAZE çıktıları:**

| Ne | Sonuç |
|---|---|
| Tam takım (oturum başı, taban) | **4547 passed** / 333,90 s / rc=0 |
| Tam takım (T5 sonrası) | 4554 passed / 333,45 s |
| Tam takım (T6 sonrası) | 4555 passed / 334,91 s |
| Tam takım (T6b sonrası) | 4556 passed / 333,66 s |
| Tam takım (T7/T8/T9 sonrası) | 4560 passed / 337,66 s |
| Tam takım (Faz 4 + kanarya sonrası) | **4562 passed / 0 failed / 338,48 s / rc=0** |
| Mutasyon | **22 mutasyon, 22'si yakalandı** (T5'te 5 · T6'da 2 · T6b'de 1 · T7-T9'da 5 · Faz 4'te 6 · T13'te 1) |
| Gerçek araçlar, üretim yolu | claude (kutusuz) rc=0 `PONG` 2,7 s · codex (kutulu) rc=0 `PONG` 6,0 s |
| **K-14 canlı ön kontrol** | **iki araç da `erisim-var`, `tur_baslayabilir=True`** (claude 9,9 s · codex 22,8 s) |
| T13 kanaryası | sekiz ayağın sekizi tuttu, `rc=0` (pozitif kontroller dahil) |
| Kanarya totoloji sınaması | kutu söküldü → araç `.env` satırını bastı, imza YAKALANDI |

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**

- **Hiçbir hakem test takımını koşturamadı** (Codex: yazılabilir temp yok; Claude alt-hakemi:
  worktree'de `.venv` yok). Yukarıdaki takım/mutasyon sayıları **kontrolörün kendi koşumlarıdır**,
  hakem teyidi YOK.
- **`denetim` · `sentez` · `motor` ayakları hâlâ HİÇ koşmadı** (Plan 2'nin kendi durumu). Bu görev
  önlerindeki K-14 engelini kaldırdı; tur henüz atılmadı.
- **CLI bayraklarının (`--restricted`, sandbox kipleri) DAVRANIŞI** yalnız kanaryayla ölçülüyor;
  kanarya takım dışında, elle koşuluyor ve **zamanlanmış evi yok** (review bulgusu F5).
- **F2'nin tur-içi etkisi ölçülmedi:** oturum kayıtlarının kalıcılığı ölçüldü, ama bir sonraki
  turun bunları FİİLEN okuyup raporuna kattığı denenmedi.

# Risks

- **F1 kritik ve BU DAL açtı.** Kutulu codex `~/.codex/auth.json`'u okuyabiliyor ve ağı açık.
  Kimlik bugün root'unkiyle AYNI hesabı taşıyor (`account_id` birebir) — yani sızarsa etkisi kutulu
  hesapla sınırlı değil.
- **`/tmp/denetci-sahne-uoiaj30t` şu an diskte** (2026-09-17). Düşürülen `SIGKILL` kalıntısının
  yeniden-açma koşulu GERÇEKLEŞTİ; kutulu codex onu okuyabiliyor (ölçüldü).
- **`/home/codex/.ssh/authorized_keys`** duruyor (1 anahtar) — kutulu kullanıcıya SSH ile
  girilebilir. Kapsam dışı bırakılmıştı; F1 ile birlikte yeniden değerlendirilmeli.
- **Oturum dökümünde gerçek `DATABASE_URL` var.** Kanaryanın kutu-söküldü mutasyonunda basıldı.
  Lokal DB (`127.0.0.1:5433`), dışarı kapalı; döndürme kararı Eray'da. Kanaryaya maskeleme eklendi,
  ama hedefin kendisi hâlâ gerçek `.env` (review bulgusu F9).

# Notes For Claude

- **Kanaryanın hedef kümesi sınırla birlikte yeniden türetilir.** Hedefi "root'un sırrı" diye
  seçmiştim; T10 ağı açınca asıl değerli sır kutulu kullanıcının KENDİ kimliği oldu ve kanarya onu
  hiç denemedi. F1'i hakem buldu, kanarya değil.
- **Serbest metinden "şu olmadı" kanıtlanmaz.** Kanaryanın ilk hâli "DENIED" kelimesini arıyordu ve
  yanlış pozitif verdi. Kontrol artık olguya bakıyor (imza taraması · diskten doğrulama · pozitif
  kontrol). Aynı ders yeni kapılar için de geçerli.
- **Sahne runner'ın içinde yaşıyor**, orkestrasyonda değil; sahte runner kullanan testler sahneyi
  GÖRMEZ. Sahne davranışı yalnız gerçek alt süreçle ölçülür.
- **Ölçüm çocuğun gözünden yapılır** — ebeveynin niyetini ölçen test bu dosyalarda yeri olmayan
  testtir. **Sahiplik ölçmek erişim ölçmek DEĞİLDİR.**
- **Mutasyon kanıtı YENİ kapıya yazılır**; değişmemiş yardımcıları yeniden mutasyona sokma.

# Notes For Codex

Codex bu oturumda **hakem olarak koştu** (`adversarial-review`, 496ddbd..d215452): 1 critical,
3 high, 1 medium. Ham çıktı:
`/root/.claude/logs/otomaix--ffc87809/2026-09-18-review-feat-sektor-bilgi-paketi-plan2-1.md`.
Bulguların hepsi sentezde kontrolörün kendi ölçümüyle doğrulandı; hiçbiri sessizce düşürülmedi.
