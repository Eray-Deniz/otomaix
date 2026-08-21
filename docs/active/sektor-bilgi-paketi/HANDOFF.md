# Handoff

## Context
- Task: sektor-bilgi-paketi — **faz: spec yeniden yazımı** (sentez + denetim/sweep sonrası)
- Last updated: 2026-08-21 (Codex denetimi + yüksek-bulgu sweep oturumu)
- Girdi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — kanonik girdi
  snapshot'ı, **2026-08-21'de kaynak commit `c380e37` üzerinden yeniden alındı** (bayt-özdeşlik
  doğrulama komutu dosya başlığında; sha `f056988d…` birebir tuttu). Kanonik kaynak:
  `/root/otomaix-sosyal-medya-arastirmasi`.
- Hedef: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (henüz yok)
- ⚠️ **ID uzayı uyarısı:** `K-xx` ID'leri sentez belgesinin Bölüm 17 uzayıdır; eski spec'in
  `K1–K7` gündemiyle ve `K6` kapı protokolüyle KARIŞTIRILMAZ (`K-06` ≠ `K6`).

## Current State
- Sentez tamamlandı (Aşama 1 kapalı). Bölüm 17: **162 karar = 153 açık + 9 kapalı** (taze
  ölçüm, 2026-08-21 sweep sonrası); açık kararlar spec'e K-ID atfıyla taşınır.
- **Dört kapanış (Eray, 2026-08-21 — kanonik kayıt: snapshot Ek B):** K-22=A (politika motoru
  Faz 1'de) · K-27=A (yönetici turu Claude Code komut ailesinden; **varlığı doğrulanmadı**) ·
  K-30=A (sinyal beklenmez; risk kabulü) · K-05=B (kanal envanteri Faz 1'de bu işte).
  ✅ **Gövde sweep'i tamamlandı:** snapshot gövdesinde bu dört karar için bayat "açıktır"
  ifadesi KALMADI — önceki devirdeki çıpa-notu uyarısı geçersizleşti, belge güvenle okunur.
- **Codex denetimi + kapanış (bu oturum):** sentez commit'leri denetlendi (4 bulgu: 2 yüksek,
  2 orta). İki yüksek bulgu 4 commit'te giderildi (`8e298eb` sweep · `35c0df2` tur-2 ·
  `0912a88` koşullu-kalıp sınıfı · `c380e37` son kalıntı); 4 turlu Codex kapanış-doğrulaması
  **CONFIRMED**. Tur-3'te dört ID'nin tüm geçişleri (162 satır öğesi) tek tek sınıflandırıldı:
  0 bayat kaldı.
- **Bilinçli açık (Eray kapsamı: yalnız yüksekler):** iki orta bulgu — TASK.md Open
  Problems'ta. "Beş prompt yüzeyi" etiketi spec seansında Ek C maddesi işlenirken çözülür.
- Blocked: hayır

## Resume From — spec seansının sırası
1. **Eski spec/planla ilişki:** `docs/specs/2026-07-11-...` (spec-approved) ve
   `docs/plans/2026-07-12-...` (plan-approved) sentezden HABERSİZDİR. Devralma mı, supersede
   mi — seansın ilk gündem maddesi; TASK.md durum geçişi Eray'ındır.
2. **Kod çıpalarının taze doğrulanması:** spec-input'taki bütün kod/DB konumları 2026-07-11
   taramasının AKTARIMIDIR (snapshot Ek C "doğrulanması gereken varsayımlar"). K-27=A gereği
   Claude Code komut ailesinin bugünkü varlığı da burada ölçülür.
3. **K-21 netleştirmesi** (22 · 12 · ≤5 rakamları neyi sayıyor — K-22=A ile koşul tetiklendi;
   Eray'a sorulacak) ve **K-20 kapanışı** (harness ortaklığı; belge önerisi A hazır).
4. Sonra iskelet çıkarımı ve bölüm bölüm spec yazımı (aşağıdaki yöntemle).

## Spec yazım yöntemi (öneren: Claude/sentezci; onaylayan: Eray, 2026-08-21 — kayıtlı kural değil)
- **Parçalı yazım:** her spec bölümü için spec-input'un ilgili bölümü + Bölüm 17'nin ilgili
  kararları okunur; ~563 KB'lik girdi hiçbir adımda tek geçişte açılmaz.
- **Kopyalama değil atıf:** kanonik ayrıntı spec-input'ta kalır; spec uygulanabilir
  sözleşmeleri damıtır, açık kararlara K-ID ile atıf yapar.
- **Gündem:** snapshot Ek C'nin 14 teknik konusu + dört kapanışın sonuçları (motor bölümü
  Faz 1'de — motor kararları K-23 · K-24 · K-25 · K-133 gündemde; komut ailesi doğrulaması;
  Marka DNA sınırının çizilmesi — K-05=B).
- **Kapanışta Codex adversarial review** (tam dosya üzerinde).

## Parçalı yazımda bütünlük koruması (öneri — Eray'ın 2026-08-21 sorusuna cevaben)

> ⚠️ **Kalıcılık kuralı (Eray onayı, 2026-08-21):** bu yöntem bölümü, spec tamamlanana kadar
> HANDOFF'un her rolling yazımında KORUNUR; ilk spec oturumunda iskelet çıkarılırken yöntem
> notu spec dosyasının kendisine (iskeletle birlikte) taşınır ve asıl evi orası olur.
> Uygulamanın kanıt artefaktları: iskelet + bağımlılık haritası (madde 1, bölüm yazımından
> önce Eray'a sunulur) · bölüm sonu tarama raporları (madde 4) · tam dosya Codex review
> raporu (madde 5).
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

## Verification (bu oturum)
- Passed: Codex bağımsız denetimi (3 sentez commit'i; 4 bulgu) · yüksek bulguların sweep'i
  4 turlu Codex kapanış-doğrulamasıyla **CONFIRMED** (tur-3 exhaustive: dört ID'nin tüm
  geçişleri sınıflandırıldı, 0 bayat) · her düzeltme sonrası bayat-kalıp grep'leri 0 isabet ·
  Bölüm 17 tablo bütünlüğü (162 satır NF=9) · Bölüm 1 sayıları taze grep sayımlarıyla
  (162/153/9; 43/47/35/36/1; 39+4) · snapshot bayt-özdeşliği (sha birebir).
- Not run: canlı kod/DB taranmadı · Otomaix'te kod işi yapılmadı · eski plan ↔ sentez uyumu
  ölçülmedi · Claude Code komut ailesinin varlığı doğrulanmadı (Resume From/2).

## Risks
- Eski plan (2026-07-12) sentezle uyumsuz olabilir — motor artık Faz 1'de (K-22=A); eski
  plan motoru içermiyor olabilir, doğrulanmadı.
- İki-depo drift: kanonik kaynak sentez deposunda (`c380e37`); kaynak değişirse snapshot
  yeniden alınır (kural snapshot başlığında).
- Denetim kapsam notu: Codex sınıflandırması "LEGITIMATE-CONTEXT" saydığı ~91 satırda
  bağımlılık etiketlerinin (örn. "üreticisi K-22'ye bağlı") kapalı Bölüm 17 satırından
  çözülmesine güvenir — spec yazarken bu etiketler görüldüğünde Bölüm 17/Ek B'den okunur.
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
- Codex kapanış-doğrulama oturumu sentez deposunda resume edilebilir durumda (4 tur bağlam
  taşıyor); yeni denetim gerekirse aynı oturumdan devam etmek bağlam kazandırır.

## Notes For Codex
- Spec review'ında: dört kapalı kararın (K-22=A · K-27=A · K-30=A · K-05=B) spec'e doğru
  yansıması; açık kararların karar uydurmadan K-ID ile taşınması; eski spec'le çelişki
  taraması; "beş prompt yüzeyi" tarzı etiketsiz sayıların spec'e sızmaması (İlke 9).
