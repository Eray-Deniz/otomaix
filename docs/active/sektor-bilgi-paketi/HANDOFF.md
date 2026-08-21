# Handoff

## Context
- Task: sektor-bilgi-paketi — **faz değişti: spec yeniden yazımı** (sentez sonrası)
- Last updated: 2026-08-21 (devir, sentez deposu kapanış oturumundan)
- Girdi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — iki hakem mimari
  belgesinin sentezinden çıkan kanonik girdi (salt-okunur snapshot; bayt-özdeşlik doğrulama
  komutu dosya başlığında). Kanonik kaynak: `/root/otomaix-sosyal-medya-arastirmasi`
  (orada protokol Bölüm 5.0 = devir kaydı; Bölüm 17 final sweep'i orada, tarihsiz).
- Hedef: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (henüz yok)
- ⚠️ **ID uzayı uyarısı:** bu devirdeki `K-xx` ID'leri (K-22, K-27…) **sentez belgesinin
  Bölüm 17 uzayıdır**; eski spec'in `K1–K7` karar gündemiyle ve `K6` kapı protokolüyle
  KARIŞTIRILMAZ (`K-06` ≠ `K6`).

## Current State
- Sentez tamamlandı ve teslim edildi (Aşama 1 kapandı). Spec-input: 21 bölüm + Ek B/C dolu;
  Bölüm 17'de 162 karar (9'u kapalı), kalanlar spec'te K-ID atfıyla açık taşınır.
- **Spec'e geçiş hükmü (Eray, 2026-08-19):** *"Spec yazımı başlayabilir; Bölüm 17'deki ürün
  kararları ilgili sözleşme kesinleşmeden kapatılmalıdır."* Karar uydurulmaz; açık karar
  K-ID atfıyla işaretlenir.
- **Kapsam turu (Eray, 2026-08-21 — kanonik kayıt: snapshot Ek B):** K-22=A (politika motoru
  Faz 1'e girer; belge önerisi B'nin TERSİ) · K-27=A (yönetici turu Claude Code komut
  ailesinden; **varlığı doğrulanmadı**) · K-30=A (sinyal beklenmez, aktivasyon Faz 1'de; risk
  kabulü) · K-05=B (kanal envanteri Faz 1'de; belge önerisi A'nın TERSİ).
  ⚠️ Snapshot gövdesindeki "açıktır" ifadeleri bu dört karar için **bayattır** — Ek C girişinde
  çıpa notu var.
- Blocked: hayır

## Resume From — spec seansının sırası
1. **Codex denetimi (önce):** sentez deposunun son üç commit'i (`553453d` · `432738b` ·
   `dc3a427`) bağımsız denetimden geçmedi; önceki oturumların ölçümü (bulguların ~tamamı
   bağımsız denetimden geldi) bu riski büyütür.
2. **Eski spec/planla ilişki:** `docs/specs/2026-07-11-...` (spec-approved) ve
   `docs/plans/2026-07-12-...` (plan-approved) sentezden HABERSİZDİR. Devralma mı, supersede
   mi — seansın ilk gündem maddesi; TASK.md durum geçişi Eray'ındır.
3. **Kod çıpalarının taze doğrulanması:** spec-input'taki bütün kod/DB konumları 2026-07-11
   taramasının AKTARIMIDIR (snapshot Ek C "doğrulanması gereken varsayımlar"). K-27 gereği
   komut ailesinin varlığı da burada ölçülür.
4. **K-21 netleştirmesi** (22 · 12 · ≤5 rakamları neyi sayıyor — K-22=A ile koşulu tetiklendi;
   Eray'a sorulacak) ve **K-20 kapanışı** (harness ortaklığı; belge önerisi A hazır).
5. Sonra bölüm bölüm spec yazımı (aşağıdaki yöntemle).

## Spec yazım yöntemi (öneren: Claude/sentezci; onaylayan: Eray, 2026-08-21 — kayıtlı kural değil)
- **Parçalı yazım:** her spec bölümü için spec-input'un ilgili bölümü + Bölüm 17'nin ilgili
  kararları okunur; ~563 KB'lik girdi hiçbir adımda tek geçişte açılmaz.
- **Kopyalama değil atıf:** kanonik ayrıntı spec-input'ta kalır; spec uygulanabilir
  sözleşmeleri damıtır, açık kararlara K-ID ile atıf yapar.
- **Gündem:** snapshot Ek C'nin 14 teknik konusu + dört kapsam kararının sonuçları (motor
  bölümü Faz 1'de; komut ailesi doğrulaması; Marka DNA sınırının çizilmesi — K-05=B).
- **Kapanışta Codex adversarial review** (tam dosya üzerinde).

## Parçalı yazımda bütünlük koruması (öneri — Eray'ın 2026-08-21 sorusuna cevaben)
1. **İskelet önce:** bölüm yazımına başlamadan tüm spec'in iskeleti çıkarılır — başlıklar,
   her bölümün tek cümlelik sorumluluğu, bölümler arası bağımlılık haritası. Küçüktür; her
   parça yazılırken bağlamda tutulur.
2. **Bağımlılığın taşıyıcısı K-ID'dir:** birden çok bölümü etkileyen karar her bölümde AYNI
   K-ID ile görünür, tanımı tek yerde yaşar (spec-input Bölüm 17). Parçalar karar metnini
   kopyalamadığı için parçalar arası çelişki yapısal olarak azalır.
3. **Sözleşmeler tek bölümde tanımlanır:** şema alanı, enum, kapı gibi bölümler arası
   yüzeyler tek bölümde tanımlanır, diğerleri atıf yapar. Yazım sırası bağımlılık yönünde:
   önce veri mimarisi + sözleşmeler, sonra onları tüketen akışlar.
4. **Her parça sonunda mekanik tutarlılık taraması:** kullanılan K-ID / alan adı / enum
   değerleri, iskelet ve önceki bölümlerdeki tanımlarla grep'le karşılaştırılır (referans
   bütünlüğü pinpoint testi; sentez oturumlarının K-ID taraması emsal).
5. **Final bütünlük turu + bağımsız denetim:** yazım parçalı, DENETİM BÜTÜNDÜR — bölümler
   bitince çapraz referans taraması ve tam dosya üzerinde Codex review. Sentezin ölçülmüş
   dersi: bütünlük hatalarını (statü, provenans, kapsam) öz-denetim yakalamadı, bağımsız
   inceleme yakaladı; bu tur atlanamaz.

## Verification (devir oturumu — sentez deposunda)
- Passed: her düzeltmede diff sınır kontrolü · Bölüm 17 bayt-özdeşliği (`51c7fd87d382`,
  üç işlemde) · K-ID geçerlilik taramaları · snapshot bayt-özdeşliği (sha birebir).
- Not run: ⚠️ **Codex denetimi bu oturumda HİÇ koşulmadı** (Resume From/1) · canlı kod/DB
  taranmadı · Otomaix'te kod işi yapılmadı.

## Risks
- Üç sentez commit'i denetimsiz (Resume From/1).
- Eski plan (2026-07-12) sentezle uyumsuz olabilir — özellikle motor artık Faz 1'de (K-22=A);
  eski plan motoru içermiyor olabilir, doğrulanmadı.
- İki-depo drift: kanonik kaynak sentez deposunda; kaynak değişirse snapshot yeniden alınır
  (kural snapshot başlığında).
- **Eski plan bağlamından taşınan riskler (geçerliliği spec seansında netleşecek):** K7 echo
  zincirinin frontend ayağı davranışsal test edilmiyor (plan T29) · migration 032 tek dosya,
  T10'a kadar commit'lenmez (F20) · dokunulmaz alanlar: `brands.sector` TEXT + `sector_id`
  semantiği, legacy `/posts/generate-short-video` (bozuk-boş korunur), SECTOR_GUIDANCE
  yan-yana basım yasağı · K7 damga semantiği version-governance'tır (içerik-bütünlüğü değil).

## Notes For Claude
- Bu HANDOFF rolling'dir — her oturum sonunda baştan yazılır; karar izi TASK.md Decisions
  Log'da.
- Eski HANDOFF'un execute-başlangıç talimatı (`/execute-plan-claude-codex` plan T1'den) askıya
  alındı: önce yeni spec, sonra plan revizyonu gündemi.

## Notes For Codex
- Review'da öncelik: sentez commit'leri (Bölüm 20/Ek B/Ek C değişiklikleri) — İlke 9 (ölçülmemiş
  sayı), H-16 (statü yükseltme), K-ID referans bütünlüğü.
- Spec review'ında: dört kapalı kararın spec'e doğru yansıması; açık kararların karar
  uydurmadan K-ID ile taşınması; eski spec'le çelişki taraması.
