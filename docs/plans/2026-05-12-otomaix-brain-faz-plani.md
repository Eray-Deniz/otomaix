# Otomaix Brain + Hermes — Faz Planı

**Tarih:** 2026-05-12
**Durum:** Roadmap (henüz spec değil — Faz 1 spec'i `/brainstorm` ile çıkarılacak)
**Sahip:** Eray (operatör), Claude Code (interactive yazıcı), ileride Hermes (background agent)

---

## Vizyon

Otomaix'in (bugün social, yarın crm + diğer uygulamalar) **ortak beyni**. Tek operatör (Eray) için, multi-tenant değil. İki ayak üstüne oturuyor:

- **Kalıcı bilgi katmanı** (Obsidian wiki, `/root/otomaix-brain/`) — kararların, araştırmaların, dış dünya bilgisinin çapraz bağlantılı havuzu
- **Background agent** (Hermes, VPS'te Coolify container) — sen yokken çalışan; tarayan, hatırlatan, not eden

Operatör merkez, ikisi yardımcı. Hiçbiri otonom karar almıyor.

---

## Üst seviye mimari (her iki fazın hedefi)

```
            ┌─────────────────────────────────┐
            │      Sen (operatör)             │
            └────┬───────────────┬────────────┘
                 │               │
          interactive       background
                 │               │
       ┌─────────▼──────┐  ┌────▼──────────────┐
       │  Claude Code   │  │  Hermes (Coolify) │
       │  Pro/Max sub   │  │  Anthropic API    │
       │  (Faz 1+2)     │  │  (Faz 2)          │
       └─────────┬──────┘  └─────┬─────────────┘
                 │               │ cron + Telegram
                 │               │
                 ▼               ▼
       ┌──────────────────────────────────┐
       │   /root/otomaix-brain/  (vault)  │
       │                                  │
       │   cross-project/                 │
       │   apps/social/                   │
       │   apps/crm/                      │
       │   decisions/                     │
       │   research/                      │
       │   sources/                       │
       │   inbox/  ← Faz 2'de aktif       │
       └─────────────┬────────────────────┘
                     │ pointer
                     ▼
       ┌──────────────────────────────────┐
       │   /root/otomaix/  (kod repo)     │
       │   - CLAUDE.md → vault'a pointer  │
       │   - docs/ zamanla küçülür        │
       └──────────────────────────────────┘
```

---

## FAZ 1 — Vault (otomaix-brain) Kurulumu

### Hedef
Otomaix'in cross-project beynini ayağa kaldırmak. Sadece Eray + Claude Code ile çalışan, Hermes'siz, kendi başına değer üreten bir sistem.

### Yapılacaklar

1. **Vault iskeleti** — `/root/otomaix-brain/` oluştur, klasör hiyerarşisi kurulur, git başlatılır
2. **Karpathy pattern uyarlaması** — vault root'una CLAUDE.md (wiki yazma kuralları, çapraz link disiplini, Otomaix bağlamına özel)
   - Kaynak: `docs/brain-CLAUDE.md` (claude.ai tarafından hazırlandı, 9 düzeltme yapılacak — aşağıda)
3. **Repo bağlantısı** — `/root/otomaix/CLAUDE.md`'ye 2-3 satır pointer (vault'un yeri ve nasıl kullanılacağı)
4. **İlk migration: `decisions_*.md`** — `~/.claude/projects/-root-otomaix/memory/decisions_backend.md`, `decisions_frontend.md`, `decisions_crm.md` zaten karar formatında, parçalanması kolay → vault'a dağıt
5. **İkinci migration: kritik spec'ler** — `00-platform-mimari.md` ve `07-social-template-system.md` parçalanır (en sık başvurulan iki kaynak)
6. **Backup stratejisi** — git push + ayrı GitHub private repo (`eraydeniz/otomaix-brain-private` benzeri)
7. **Sürdürülebilirlik disiplini** — sprint sonu wiki update protokolü (Claude Code ile)

### Faz 1 sonunda elde edilecekler

- Çalışan Obsidian vault, ~50-100 wiki sayfası, çapraz bağlantılı
- "FLUX neden seçilmedi" gibi sorulara saniyeler içinde cevap
- Git versionlu, GitHub yedekli
- Yeni karar alındığında nereye yazılacağı belli (`decisions/`)
- Hermes sıfır bağımlılığı — Faz 2'ye geçmesen de değerli

### Faz 1'in açık soruları (`/brainstorm`'da çözülecek)

1. **Vault VPS'te mi lokal'de mi?** — VPS'teyse Obsidian'ı nasıl açacaksın? (Obsidian Sync, SSHFS mount, lokal sync ile Git pull?)
2. **Klasör hiyerarşisi detayı** — `cross-project/` içi nasıl bölünüyor (database/, n8n/, copywriting/, legal/...)? `decisions/` tarih mi konu mu?
3. **Karpathy CLAUDE.md** — orijinal generic, Otomaix'e nasıl uyarlanacak?
4. **Migration kapsamı** — Faz 1'de sadece decisions + 2 spec mi, yoksa tüm `docs/` mi?
5. **Mevcut `docs/`** — migrate edilen dosya silinir mi, "deprecated" notu ile durur mu, başka klasöre arşivlenir mi?
6. **Sources klasörü** — ham metin (örn. Karpathy gist'i, Anthropic doc'ları) saklanıyor mu, yoksa sadece işlenmiş wiki sayfası mı kalıyor?
7. **Sprint sonu update disiplini** — manuel ("commit'ten sonra wiki güncelle" kuralı) mu, hatırlatıcı mı, otomatik mi (Faz 1'de otomatik yok)?

---

## FAZ 1 ÖN-ADIM — `brain-CLAUDE.md`'de 9 düzeltme

Faz 1'e başlamadan önce `docs/brain-CLAUDE.md` schema dosyasında yapılacak düzeltmeler. Schema sistemin "anayasası" — drift varsa sistemin tümü drift'e açık olur.

### 6 ana düzeltme

1. **Stack listesi (Otomaix bağlamı bölümü) DRIFT bombası** ⚠️
   - `Stack: Claude Opus 4.7, ElevenLabs eleven_flash_v2_5, fal.ai (Wan, Kling V3 Standard...)` satırı sil
   - Yerine: *"Stack bilgisi için `cross-project/vendors/` altına bak"*
   - Sebep: Bu **fact**, kural değil. 6 ayda bir stale olur. CLAUDE.md kuralları öğretir, bilgileri vault'tan alırsın.

2. **"Mid-conversation öneri değişikliği sevmez" — yanlış yer**
   - Bu satır + "Eray solo founder" satırını sil
   - `~/.claude/projects/-root-otomaix/memory/feedback_*.md` formatına taşı (zaten benzeri orada var)
   - Sebep: Schema convention'ları içerir, kullanıcı karakteristikleri değil

3. **`sources/decisions-raw/` duplikasyon yaratıyor**
   - Bu alt-klasörü schema'dan çıkar
   - Yerine: source olarak link ver (`sources: ["@/root/.claude/projects/-root-otomaix/memory/decisions_backend.md"]`)
   - Sebep: 3 kopya (memory + sources + wiki) = kaçınılmaz drift

4. **Boş klasörler YAGNI ihlali**
   - `apps/crm/` "hazır" diye boş açılmasın
   - Faz 1'de sadece içine sayfa konacak klasörler açılsın
   - Sebep: Boş klasör graph view'ı kirletir, lint'i karıştırır

5. **Backup stratejisi tanımsız**
   - Schema'ya 2 satır ekle: vault git'i ayrı GitHub private repo'ya push (örn. `eraydeniz/otomaix-brain-private`)
   - Sebep: "Git ile versiyonlu" diyor ama nereye push net değil

6. **Karpathy quote zorlama**
   - *"Obsidian (ya da bu durumda Claude Code) IDE, LLM programcı, wiki ise codebase"* — Karpathy gist'inde böyle bir cümle yok
   - Sadeleştir: *"wiki = codebase, LLM = programcı"* veya tamamen çıkar (referans linki yeterli)

### 3 küçük öneri

7. **`inbox/` README placeholder** — Faz 1'de boş ama bir `README.md` koy: *"Faz 2'de Hermes yazacak. Şu an dokunulmaz."*
8. **Decisions frontmatter'a `area: backend | frontend | infrastructure`** ekle — lint zenginleşir
9. **"Cevap değerli sentezse Eray'a sor" subjective** — threshold ekle: *"3+ farklı sayfayı birleştirdiysen file et"*

---

## FAZ 2 — Hermes Entegrasyonu

### Önkoşul
**Faz 1 çalışıyor olmalı** — vault dolu, kullanılıyor, hangi sayfaların var olduğu biliniyor. Aksi halde Hermes boş bir wiki'ye yazar, anlamsız olur.

### Hedef
Vault'u **canlı tutan** ve **dış dünyayla bağlayan** background agent katmanı. Sen yokken çalışan, sana hatırlatan, dış değişiklikleri takip eden.

### Yapılacaklar

1. **Hermes Coolify deploy** — Docker compose ile container, environment variables
2. **API key + budget cap** — `console.anthropic.com` üzerinden ayrı key + ayda max harcama tavanı
3. **Vault'a okuma + `inbox/`'a yazma yetkisi** — Hermes container'ından mount
4. **Telegram bot kurulumu** — yeni bot, webhook, auth (sadece Eray erişebil)
5. **İlk skill seti** (~3-4 skill, hepsi birden değil):
   - `git-log-checker` — haftalık, repo değişikliklerini wiki ile karşılaştır
   - `daily-research-scan` — fal.ai, Anthropic, Meta API release notes
   - `telegram-capture` — mobile quick note → `inbox/`
   - `weekly-summary` — Pazar gecesi haftalık özet
6. **Onay UX** — `inbox/` review akışı (Telegram inline button mı, sabah özet maili mi)
7. **Monitoring** — Hermes sağlık kontrolü, log'a erişim

### Faz 2 sonunda elde edilecekler

- Hermes 7/24 çalışıyor, cron'lar tetikleniyor
- Telegram'dan mobil quick capture çalışıyor
- `inbox/` her sabah dolu geliyor, Eray onaylıyor → vault'a taşınıyor
- Dış dünya değişiklikleri kaçmıyor (fal.ai yeni model çıkarsa biliyorsun)
- Wiki güncel kalıyor (Hermes hatırlatıyor)

### Faz 2'nin açık soruları (`/brainstorm`'da çözülecek — Faz 1 bittikten sonra)

1. **Hermes hangi LLM'e bağlansın?** — sadece Sonnet 4.6 mı, küçük işler için Haiku 4.5 mix mi?
2. **Telegram bot** — yeni bot mu açıyoruz, mevcut Otomaix bot'u var mı?
3. **Hermes ilk skill detayları** — her birinin tam tetik koşulu, çıktı formatı, hata davranışı
4. **`inbox/` onay UX** — Telegram'dan inline button ile onayla mı, sabah Claude Code ile manuel review mı, mail özet mi?
5. **Hermes'in vault'a yazma yetkisi sınırı** — sadece `inbox/`'a mı, hiçbir yerde değil mi (sadece Telegram'a önerir)?
6. **Coolify deploy detayları** — Hermes resmi Docker image var mı, kendimiz Dockerfile yazacak mıyız?
7. **Backup ve recovery** — Hermes container çökerse cron'lar kaçar mı, history nasıl tutulur?
8. **Skill self-improvement** — Hermes'in özelliği var ama kullansın mı kullanmasın mı (production risk)?
9. **Cost monitoring** — ayda gerçek harcama nasıl izlenir, alarm hangi seviyede tetiklenir?

---

## Açıkça kapsam dışı (her iki faz için)

- ❌ Multi-tenant — sadece Eray
- ❌ Otomaix müşterilerine açık değil — kişisel/iç araç
- ❌ Otomaix kodunu otomatik değiştirmek
- ❌ Hermes prod data'ya yazma yetkili değil
- ❌ Hermes wiki'ye direkt yazma — her şey `inbox/` + onay
- ❌ Çoklu domain agent (ileride olabilir, şimdi değil)
- ❌ Skill self-improvement (Hermes'te var ama deneme; production yapma)

---

## Sıralama

1. **Şimdi:** `brain-CLAUDE.md`'de 9 düzeltme
2. **Sonra:** `/brainstorm "otomaix-brain Faz 1: vault kurulumu"` → spec çıkar (`docs/specs/2026-05-12-otomaix-brain-faz1.md`)
3. **Sonra:** `/write-plan` ile Faz 1 implementation planı (`docs/plans/2026-05-12-otomaix-brain-faz1-impl.md`)
4. **Sonra:** Faz 1 implementation
5. **Sonra:** Faz 1'i 1-2 hafta kullan, sezgi topla
6. **Sonra:** Faz 2 değerlendirme — eğer Faz 1 olgunlaştıysa Faz 2 brainstorm'una gir
