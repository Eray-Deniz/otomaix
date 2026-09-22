# Sentez aşamasında cevap kesilmesi — Codex'e soru brief'i

**Tarih:** 2026-09-22 · **Depo:** `/root/otomaix` · **Dal:** `feat/sektor-bilgi-paketi-plan2`

## 1. Sistem — sadece gereken kadarı

Sektör bilgi paketi üreten bir işletim hattı. İlgili aşama zinciri:

`tur-ac` → `brief-doctor` (3 kaynak, mekanik kapı) → `denetim` (2 kör denetçi) →
**`sentez`** → `motor`.

`sentez` aşaması bir LLM alt süreci koşturur ve ondan **tek bir metin** ister.
Metin dört bölümden oluşmak ZORUNDA ve sırası bağlayıcı:

1. `ADAY PAKET` (JSON)
2. `DECISION_LOG` (JSONL satırları)
3. `AÇIK SORULAR`
4. `ÖZET`

Biçim kapısı (`synthesis._bolumlere_ayir`) dördü eksiksiz ve sırayla yoksa turu
düşürür. Düşen koşu K-82 gereği TERMİNAL olur (`durum='tamamlanmadi'`) ve
canlandırılamaz — yeni koşu açmak, `denetim` aşamasını (ölçüldü: 24-25 dakika +
API parası) baştan koşturmak demektir.

## 2. Alt süreç nasıl çağrılıyor

`apps/social/backend/app/services/sector_pipeline/auditors.py` içinde,
`ARAC_KOMUTLARI` eşlemesi (satır ~1959):

```
claude -p --output-format text \
  --safe-mode --restricted \
  --tools Read,Glob,Grep \
  --strict-mcp-config \
  --disallowedTools Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch,Task
```

- İstem STDIN'den gider (argv'ye gömülmez; görev dosyası ~159 KB).
- Alt süreç ortamı BEYAZ LİSTEDİR (`SubprocessRunner._alt_surec_ortami`,
  satır ~2103): `PATH · HOME · LANG · LC_ALL · LC_CTYPE · TERM · TMPDIR`.
  Çağıranın sırları çocuğa MİRAS KALMAZ (2026-09-12 güvenlik review'ı, S-2).
- Sentez rolü çağıranın kimliğiyle (root) koşar, kum havuzu YOKTUR; yazma
  araçları bilinçli olarak KAPALIDIR — girdi metni web'den derlenmiş araştırma
  raporlarından gelir, yani enjeksiyon yüzeyidir.
- `stdout` rapor gövdesi sayılır (`SubprocessRunner.run`, satır ~2407).

## 3. ARIZA — iki koşum, ham ölçümler

`claude -p --output-format text` **yalnız SON asistan mesajını** basar.

### Koşum A — `kosu-3f22d638453f4ba798761f59a92f5baf` (14:34, DÜŞTÜ)

Oturum kaydından (`~/.claude/projects/.../*.jsonl`) okunan mesaj dökümü:

| mesaj | bloklar | stop_reason | output_tokens | thinking_tokens | metin |
|---|---|---|---|---|---|
| 1 | thinking + text | **max_tokens** | 64.000 | 51.564 | 22.230 karakter |
| 2 | thinking + text | end_turn | 4.781 | 220 | 7.478 karakter |

- Diske yazılan dosya: **7.775 bayt**, ortadan başlıyor
  (`## Karar satırları — devam (ozel_gun)`). İlk mesajın 22.230 karakteri KAYIP.
- İki mesaj elle birleştirildi: dört bölümün yalnız İKİSİ var
  (`ADAY PAKET`, `DECISION_LOG`). Yani içerik gerçekten yarım — sadece yakalama
  sorunu değil; model devam mesajında da 3. ve 4. bölümü yazmadan bitirdi.
- Biçim kapısı turu düşürdü: `bulunan []`.

### Koşum B — `kosu-8a2081d4c65a4eeb9ba7b5be3cf684a2` (14:34-14:48, cevap TAM)

| mesaj | bloklar | stop_reason | output_tokens | thinking_tokens | metin |
|---|---|---|---|---|---|
| 1 | thinking | tool_use | 56.554 | 56.502 | 0 |
| 2 | tool_use | tool_use | — | — | 0 |
| 3-4 | thinking + text | **end_turn** | 22.468 | 36 | **39.082 karakter** |

- Diske yazılan dosya: **41.433 bayt**, dört bölümün DÖRDÜ de yerinde,
  biçim kapısı **0 hata**.
- Yani model düşünmesini AYRI bir mesaja koyunca cevap tek mesaja sığdı.

### Karşılaştırma — 21 Eylül'ün başarılı koşumu

`kosu-7705437723ce4730ac0ae70cf6986bc8`: tek mesaj, `end_turn`,
output_tokens **24.178**, thinking **33**, metin **42.326 karakter**.

**Özet:** tek mesajın ölçülmüş çıktı bütçesi 64.000 jeton. Cevabın kendisi
~24.000 jeton (≈42.000 karakter) tutuyor, yani bütçenin %38'i. Sorun cevabın
boyutu DEĞİL; düşünmenin aynı mesajda bütçeyi yemesi.

## 4. BENİM DENEDİĞİM VE TUTMAYAN İKİ ŞEY (tekrar edilmesin)

### (a) `MAX_THINKING_TOKENS=16000` ortama yazıldı — BAĞLAMADI

- Değerin çocuğa ULAŞTIĞI canlı ölçüldü:
  `/proc/<pid>/environ` → `MAX_THINKING_TOKENS=16000`.
- Aynı koşumda model **56.502** jeton düşündü. Ayar bu sürümde/modelde sınır
  koymuyor.
- Öncesindeki iki kollu prob (kapaksız 1.511 → kapaklı 1.053 jeton) kol başına
  TEK koşumdu; gürültüydü, kanıt değildi.
- Kurulu sürümler: Claude Code **2.1.278**, model `claude-opus-5`.

### (b) "Kümülatif çıktı jetonu ≥ 48.000 ise kesilmiştir" kapısı — ZARAR VERDİ

- Zarfın `usage.output_tokens` alanı TÜM turların toplamıdır (ölçüldü: iki
  mesajlık koşumda zarf 160 dedi, kayıttaki iki mesajın toplamı da 160).
- Model düşünmesini ayrı bir tura koyunca toplam 79.022 oldu ve kapı **TAM olan**
  Koşum B'yi öldürdü. Bir denetçi turu (24 dk + para) çöpe gitti.
- Kesilmenin doğru işareti **bir mesajın `max_tokens` ile bitmesidir**; `json`
  zarfı yalnız SON mesajın `stop_reason`'ını verir, yani bu zarfla ölçülemez.

İkisi de geri alındı. Şu an kodda duran tek değişiklik: sentez
`--output-format json` ile koşuyor, gövde `result` alanından alınıyor ve
koşum ölçümü (jeton · tur · maliyet) loga yazılıyor. Hiçbir şeyi kapıya
bağlamıyor.

## 5. SORU

**Aynı istem tek mesaja sığan bir cevabı bazen üretiyor, bazen düşünmeyi aynı
mesaja koyup `max_tokens` ile kesiliyor. Bu hattın bundan bağımsız hâle gelmesi
için doğru çözüm nedir?**

Alt sorular:

1. `claude -p` ile koşan bir alt süreçten, cevabın TAMAMINI (birden çok asistan
   mesajına yayılsa bile) ve her mesajın `stop_reason`'ını güvenilir biçimde
   almanın yolu nedir? `--output-format stream-json` doğru araç mı, üretimde
   dayanıklı mı?
2. Uzun düşünmeyi metin bütçesinden ayırmanın / sınırlamanın çalışan bir yolu
   var mı (env, bayrak, istem düzeyi)? `MAX_THINKING_TOKENS` bu sürümde
   bağlamadı — ölçüldü.
3. Kesilmiş bir cevabı, turu öldürmeden KURTARMAK mümkün mü (devam ettirme,
   bölüm bölüm isteme)? Sözleşme dosyası PİNLİDİR (dış depo,
   `hakem-sentez-gorevi.md`, hash + commit pinli) — istemi değiştirmek
   sözleşme değişikliği + yeniden pin + review zinciri demektir.
4. "Dosyaya yazdır" seçeneği: yazma araçları 2026-09-12 güvenlik review'ıyla
   (S-2) bilinçli kapatıldı; sentez root olarak, kum havuzsuz koşuyor ve girdisi
   güvenilmez dış metin. Bu kısıtı bozmadan aynı dayanıklılığı sağlamanın bir
   yolu var mı?

## 6. DOSYALAR

Değişen (hepsi commit EDİLMEDİ, çalışma ağacında):

| Dosya | Ne yapıldı |
|---|---|
| `apps/social/backend/app/services/sector_pipeline/auditors.py` | `ToolSpec.cikti_bicimi` alanı (1661) · `CIKTI_BICIMLERI` (1713) · `ARAC_KOMUTLARI` sentez satırı `text`→`json` (1959) · `RunnerOutcome.olcum` (1987) · `SubprocessRunner.run` json dalı (2457) · `SubprocessRunner._zarfi_coz` (2486) |
| `apps/social/backend/app/services/sector_pipeline/synthesis.py` | `_cikti_butcesini_dogrula` (278) — şu an yalnız "ölçüm var mı" kontrolü · çağrı yeri (1082) |
| `apps/social/backend/tests/test_auditor_orchestration.py` | ölçülmüş argv sabiti (`OLCULEN_ARGV`, satır 71) güncellendi · yeni testler (bölüm 14) |
| `apps/social/backend/tests/test_synthesis.py` | `_tamam`/`_olcumsuz` yardımcıları · ölçüm kapısı testi |
| `shared/contracts/research-contracts.pin.json` | dış depo commit'i `34a34db` → `38b475b` (sözleşme dosyalarının hash'leri DEĞİŞMEDİ) |

Okunması gereken (değişmedi):

- `apps/social/backend/app/services/sector_pipeline/synthesis.py` — `run()`,
  `_bolumlere_ayir()`, `CIKTI_DOSYA_ADI` (112)
- `apps/social/backend/app/services/sector_pipeline/auditors.py` —
  `_claude_izolasyon()` (~1875), `_CLAUDE_ARAC_KUMESI`, `_CLAUDE_YASAK_ARACLAR`
- `docs/security-reviews/2026-09-12-feat-sektor-bilgi-paketi-plan2.md` — S-2
  bulgusu (yazma araçlarının neden kapalı olduğu)
- `/root/otomaix-sosyal-medya-arastirmasi/hakem-sentez-gorevi.md` — pinli
  sentez sözleşmesi (650 satır)

Kanıt dosyaları:

- Koşum A çıktısı: `/root/otomaix-sosyal-medya-arastirmasi/sentez/kosu-3f22d638453f4ba798761f59a92f5baf/01-SENTEZ-CIKTISI.md` (7.775 bayt, yarım)
- Koşum B çıktısı: `/root/otomaix-sosyal-medya-arastirmasi/sentez/kosu-8a2081d4c65a4eeb9ba7b5be3cf684a2/01-SENTEZ-CIKTISI.md` (41.433 bayt, TAM)
- Oturum kayıtları: `/root/.claude/projects/-var-lib-otomaix-denetci-sahne-*/`

## 7. DURUM

- Tam test takımı taze koşuldu: **4723 geçti / 0 düştü / 401,7 sn**.
- İki koşu da terminal (`tamamlanmadi`); ilerlemek yeni koşu + yeni denetim turu
  (24-25 dk + para) gerektiriyor.
