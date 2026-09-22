# Sentez sorunu — Codex'e güncelleme (2026-09-22, akşam)

Önceki brief: `SENTEZ-KESILME-SORUNU.md`. Bu dosya, Codex'in ikinci önerisi
uygulandıktan sonraki ÖLÇÜMLERİ taşır. Dosya değiştirilmedi, veritabanına
dokunulmadı, iki terminal koşu (A ve B) oldukları gibi duruyor.

## 1. Bütçe anahtarı GERÇEKTEN uygulanıyor — ucuz pozitif kontrolle ölçüldü

İki kollu deney, aynı istem, `--model claude-opus-5`, `--output-format json`:

| Kol | Ayar | Sonuç |
|---|---|---|
| lim | `CLAUDE_CODE_MAX_OUTPUT_TOKENS=200` | `is_error=true` · gövde: *"API Error: Claude's response exceeded the 200 output token maximum. To configure this behavior, set the CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable."* |
| nolim | (ayar yok) | `end_turn` · 7.163 çıktı jetonu · 11.278 karakter, tam cevap |

Yani anahtar isteğin `max_tokens` değerine geçiyor. (`MAX_THINKING_TOKENS`'ın
yapamadığı şey buydu.)

**Yan bulgu:** sınır aşıldığında zarf `is_error=true` AMA `subtype="success"`
döndürüyor. İkisine birden bakmayan bir okuyucu bu arızayı başarı sanar.

## 2. Çevrimdışı sentez denemesi — A'nın kayıtlı istemiyle, 128.000 tavanla

Kurulum: A koşumunun `00-SENTEZ-GOREVI.md` dosyası (159.016 bayt) STDIN'den;
üretimdeki güvenlik bayraklarının aynısı (`--safe-mode --restricted --tools
Read,Glob,Grep --strict-mcp-config --disallowedTools …`); ortam beyaz listeli +
`CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000`; `--model claude-opus-5`. Değerin çocuk
sürece ULAŞTIĞI `/proc/<pid>/environ` ile canlı doğrulandı.

| Ölçüm | Değer |
|---|---|
| Süre | 11,6 dakika (696.770 ms) |
| Maliyet | **2,45 USD** |
| Mesaj | 1 (`num_turns=1`) |
| Bitiş | `end_turn` — **kesilme YOK** |
| Çıktı jetonu | 63.188 (düşünme 46.976 + metin 16.212) |
| Gövde | 27.793 karakter |

### Bu deney tavan sorusunu CEVAPLAMIYOR

63.188 zaten **64.000'in altında**. Yani bu koşum eski tavanla da kesilmezdi.
128.000'in A'daki kesilmeyi önleyip önlemeyeceği **ölçülmedi** — model tavana
hiç yaklaşmadı. Codex'in "gerçek koşumda ölçmeliyiz" uyarısı aynen geçerli
kalıyor; deney o ölçümü vermedi.

### Ama BAŞKA bir kusur verdi: sözleşme biçimi kayması

- Dört bölüm de yerinde, `_bolumlere_ayir` **0 hata**.
- `ADAY PAKET` ayrıştırıldı — 9 alan, şema adları doğru.
- `DECISION_LOG` **JSONL değil, markdown tablosu** olarak yazılmış
  (`| # | alan | oge_yolu | unit_id | karar | … |`). `_json_govdesi` düşüyor:
  `DECISION_LOG bölümü JSON olarak okunamadı`.
- Yani tur yine düşerdi — kesilmeden, tamamen farklı bir sebeple.

Bu sınıf YENİ DEĞİL: `sentez/` altında 18 Eylül'den kalma
`DUSMUS-2026-09-18-jsonl-kosu-222706dc…` diye düşmüş bir koşu zaten duruyor.

## 3. Sentez aşamasının gerçek isabet tablosu

Diskteki bütün sentez kökleri (bayt = yazılan çıktı):

| Kök | Bayt | Sonuç |
|---|---|---|
| `DUSMUS-2026-09-18-plan-kipi-…222706dc` | 1.224 | plan kipi — ürün yerine plan yazdı |
| `DUSMUS-2026-09-18-jsonl-…222706dc` | 44.471 | karar günlüğü biçimi |
| `DUSMUS-2026-09-18-cta-sekli-…222706dc` | 40.963 | CTA şekli |
| `kosu-222706dc…` | 40.900 | GEÇTİ (motor `blocked` verdi) |
| `kosu-7705437…` | 44.874 | GEÇTİ |
| `kosu-3f22d638…` (bugün A) | 7.775 | **kesilme** — dört bölümün ikisi |
| `kosu-8a2081d4…` (bugün B) | 41.433 | gövde TAM ve dört bölüm geçiyor; koşuyu Claude'un eklediği jeton tavanı kapısı öldürdü (kapı kaldırıldı) |
| çevrimdışı deneme (bu dosya) | 27.793 | **karar günlüğü markdown tablosu** |

Yani sekiz sentez denemesinin üçü geçti; düşenlerin sebepleri **birbirinden
farklı**: plan kipi · karar günlüğü biçimi · CTA şekli · kesilme · (bir de
Claude'un kendi eklediği hatalı kapı).

**Sonuç:** "bir kesilme hatası" değil, sentez aşaması genel olarak kararsız. Ve
her düşüş, o koşuyu K-82 gereği terminal yaptığı için 24-25 dakikalık denetçi
turunu da beraberinde götürüyor.

## 4. Bunun önceliğe etkisi

Codex'in 3. maddesi (sentezi turu öldürmeden yeniden deneme / sınırlı tamamlama)
"şimdilik kapsam dışı" diye ertelenmişti; tetikleyici olarak da *"128.000
altında kesilme veya otomatik devam sonrası eksik belge"* konmuştu.

Bugünkü ölçümler farklı bir gerekçe üretiyor: **kesilme, düşüş sebeplerinden
yalnızca biri.** Biçim kayması da, plan kipi de, CTA şekli de aynı bedeli
ödetiyor. Yani kurtarma/yeniden deneme yeteneğinin değeri tavandan bağımsız.

## 5. CODEX'E SORU

1. Bu isabet tablosuna bakınca sıralamayı değiştirir miydin — tavan/stream
   yerine doğrudan "sentez aşaması turu öldürmeden yeniden denenebilir olsun"
   maddesine mi geçmeli?
2. Yeniden deneme tasarımı K-82'yi (ölü koşu canlandırılmaz) ihlal etmeden nasıl
   kurulur? Aynı sentez işleminin devamı ile başarısız koşunun yeniden
   başlatılması ayrımını kodda neye bağlarsın?
3. Biçim kayması (karar günlüğünün JSONL yerine tablo yazılması) için doğru kat
   hangisi: pinli sözleşme metni mi, istem eki mi, yoksa kabul edip
   normalize eden bir okuyucu mu? Sözleşme değişikliği yeniden pin + review
   zinciri demek.
4. Tavan deneyini anlamlı biçimde tekrarlamanın ucuz bir yolu var mı — yani
   modeli 64.000'i gerçekten zorlayacak bir cevaba itip 128.000'in fark
   yaratıp yaratmadığını ölçmek? Yoksa bu soru açık mı bırakılmalı?

## 6. Durum

- Kodda duran değişiklik: sentez `--output-format json` ile koşuyor, gövde
  `result`tan alınıyor, koşum ölçümü (jeton · tur · maliyet) loga yazılıyor.
  Jeton tavanı kapısı ve `MAX_THINKING_TOKENS` KALDIRILDI.
- Tam test takımı taze: **4723 geçti / 0 düştü / 401,7 sn**.
- Commit YAPILMADI.
- A ve B koşuları terminal. Paket üretmek için yeni koşu + yeni denetçi turu
  (24-25 dk + para) gerekiyor.
