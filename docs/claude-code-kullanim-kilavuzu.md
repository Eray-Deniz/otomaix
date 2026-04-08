# Claude Code Kullanım Kılavuzu
> Otomaix projesi için — terminali açmadan önce bu dosyayı oku

---

## Claude Code Nedir, Nasıl Çalışır?

Claude Code, terminalden konuştuğun bir AI asistanıdır. Sana kod yazar, dosya oluşturur, komut çalıştırır. Ama her session (oturum) bağımsızdır — önceki konuşmayı **hatırlamaz**.

Bu yüzden her projede bir `CLAUDE.md` dosyası tutuyoruz. Bu dosya Claude Code'un "hafızası" görevini görür. Sen güncellettikçe, Claude Code her session başında okuyarak kaldığı yerden devam eder.

---

## Temel Kavramlar

**Session:** Terminal'i açıp `claude` yazdığın andan kapattığın ana kadar olan süre. Her session bağımsızdır.

**CLAUDE.md:** Her proje klasöründe bulunan hafıza dosyası. Tamamlanan işler, devam eden iş ve bir sonraki adım buraya yazılır.

**Kılavuz MD dosyaları:** Sana ait planlama dosyaları (`01-social-phase1.md` gibi). Claude Code bunları okuyarak ne yapması gerektiğini anlar.

---

## Klasör Yapısı — Başlamadan Önce Kur

```
/home/eray/otomaix/
├── apps/
│   ├── social/
│   │   ├── frontend/
│   │   │   └── CLAUDE.md   ← frontend session'ının hafızası
│   │   └── backend/
│   │       └── CLAUDE.md   ← backend session'ının hafızası
│   └── crm/
│       └── CLAUDE.md       ← crm session'ının hafızası
├── shared/
│   ├── db/
│   └── n8n-workflows/
└── docs/                   ← kılavuz MD dosyaları buraya
    ├── 00-platform-mimari.md
    ├── 01-social-phase1.md
    ├── 02-social-phase2.md
    └── ...
```

---

## 4 Temel Komut — Hepsini Ezberle

### 1. Yeni bir adıma başlarken
```
Read ~/otomaix/docs/[dosya-adı].md and complete Step [N]
```
Örnek:
```
Read ~/otomaix/docs/01-social-phase1.md and complete Step 2
```

### 2. Kaldığın yerden devam ederken
```
Read CLAUDE.md and continue from where we left off
```

### 3. Bir adım bitince (HEMEN ver, unutma)
```
Update CLAUDE.md: mark Step [N] as done, next step is Step [N+1]
```

### 4. Terminali kapatmadan önce
```
Update CLAUDE.md with everything completed today and what comes next
```

---

## Günlük Kullanım Akışı — Adım Adım

### Sabah: Güne başlarken

**1.** Terminal'i aç, ilgili proje klasörüne git:
```bash
cd ~/otomaix/apps/social/backend
claude
```

**2.** Her zaman önce CLAUDE.md'yi oku:
```
Read CLAUDE.md and continue from where we left off
```

**3.** Claude Code CLAUDE.md'yi okur ve şöyle bir şey söyler:
```
"Dün Step 3'ü tamamladık. Şimdi Step 4'e geçiyorum:
FastAPI'ye fal.ai webhook endpoint'i ekleyeceğim..."
```

**4.** Onaylarsan çalışmaya başlar. Onaylamak için:
```
yes, go ahead
```
veya Türkçe:
```
evet devam et
```

---

### Gün içi: Normal çalışma

Claude Code çalışırken yapman gerekenler:

**Soru sorduğunda:** Kısa ve net yanıt ver.
```
Claude: "Which port should the API run on?"
Sen:   "8000"
```

**Bir şeyi test etmeni istediğinde:** Test et, sonucu bildir.
```
Claude: "Run this and tell me the output"
Sen:   [komutu çalıştır]
Sen:   "output: [çıktıyı yapıştır]"
```

**Emin olmadığın bir karar önerdiğinde:** Kılavuz MD'ye bak.
```
Sen: "Check ~/otomaix/docs/01-social-phase1.md Step 3 
      for the decision on this"
```

---

### Bir adım bittiğinde: CLAUDE.md güncelle

Bir adım tamamlandığında **hemen** şunu ver:
```
Update CLAUDE.md: Step 3 is complete. 
Mark it done and set next step as Step 4.
```

Claude Code CLAUDE.md'yi şöyle günceller:
```markdown
## Tamamlanan İşler
- [x] Step 1: Proje kurulumu
- [x] Step 2: PostgreSQL bağlantısı
- [x] Step 3: Auth middleware   ← yeni eklendi

## Devam Eden İş
- [ ] Step 4: Storage abstraction  ← güncellendi

## Bir Sonraki Adım
app/services/storage.py oluşturulacak. R2 upload/download/delete metodları...
```

---

### Akşam: Terminali kapatmadan önce

Bitirmeden önce mutlaka şunu ver:
```
Update CLAUDE.md with everything we did today and 
exactly where to continue next time
```

Sonra terminali kapat. Ertesi gün "Read CLAUDE.md" ile kaldığın yerden devam edersin.

---

## Session Kesilirse Ne Yaparsın?

Claude Code bazen yanıt kesilir veya hata verir. Paniklemene gerek yok.

**Durum 1: Yanıt yarım kaldı**
```
continue
```
veya
```
you were cut off, please continue from where you stopped
```

**Durum 2: Claude Code kayboldu, yeni session açtın**
```
Read CLAUDE.md and continue from where we left off
```

**Durum 3: Ne yaptığından emin değilsin**
```
Read CLAUDE.md and tell me what was completed and what's next
```

**Durum 4: Claude Code yanlış bir şey yaptı**
```
That's wrong. Revert that change and try again. 
The correct approach is [açıklama]
```

---

## Farklı Projeler İçin Farklı Session'lar

Her proje klasörü **ayrı bir session**dır. Aynı anda iki farklı terminal açıp iki farklı projede çalışabilirsin.

```
Terminal 1:                    Terminal 2:
cd ~/otomaix/apps/social/backend    cd ~/otomaix/apps/social/frontend
claude                              claude
(backend session)                   (frontend session)
```

**Kesin kural:** Backend session'ında frontend kodu yazdırma. Her session kendi klasöründe çalışır.

---

## Kılavuz MD Dosyalarını Nasıl Kullanırsın?

Kılavuz MD dosyaları (`01-social-phase1.md` gibi) senin planın. Claude Code bunları okuyarak ne yapacağını anlar.

**Bir phase'e ilk kez başlarken:**
```
Read ~/otomaix/docs/01-social-phase1.md 
and start with Step 1
```

**Belirli bir adıma atlamak istersen:**
```
Read ~/otomaix/docs/01-social-phase1.md 
and go directly to Step 3
```

**Claude Code'un kılavuzdan sapmasını fark edersen:**
```
Stop. Read ~/otomaix/docs/01-social-phase1.md Step 3 again.
Follow it exactly as written.
```

**Bir adımı tamamlayıp bir sonrakine geçerken:**
```
Step 3 is done and tested. 
Now read Step 4 from the same file and proceed.
```

---

## Sık Yapılan Hatalar

### ❌ CLAUDE.md güncellemeden terminali kapatmak
Ertesi gün ne yaptığını anlatmak zorunda kalırsın.
**Çözüm:** Her adım bitişinde güncelle, kapatmadan önce güncelle.

### ❌ Birden fazla adımı aynı anda vermek
```
# YANLIŞ:
Read the file and complete Steps 1, 2, 3 and 4
```
Claude Code hepsini yarım yapar veya karıştırır.
```
# DOĞRU:
Read the file and complete Step 1 only
```
Step 1 bitince Step 2'yi ver.

### ❌ Farklı projeleri aynı session'da karıştırmak
```
# YANLIŞ (backend session'ında):
Also update the frontend login page
```
**Çözüm:** Yeni terminal aç, frontend klasörüne git, orada ver.

### ❌ Claude Code'un çıktısını test etmeden bir sonraki adıma geçmek
Her adımın sonunda kılavuz MD'deki "Kontrol" bölümünü uygula.
Çalışmayan bir şeyin üzerine inşa edersen sonra çözmesi çok zorlaşır.

### ❌ Hata mesajını Claude Code'a göstermemek
```
# YANLIŞ:
it doesn't work
```
```
# DOĞRU:
it failed with this error:
[hata mesajını buraya yapıştır]
```

---

## n8n Workflow'ları İçin

n8n-mcp kurulu olduğu için herhangi bir session'dan n8n'e workflow oluşturabilirsin.

```
Using the n8n MCP tool, create a workflow called "..." 
[workflow açıklaması]

After creating it, export the JSON to 
~/otomaix/shared/n8n-workflows/[dosya-adı].json
```

Workflow oluştuktan sonra n8n arayüzünden kontrol et: `https://n8n.otomaix.com`

---

## Hızlı Başvuru Kartı

```
┌─────────────────────────────────────────────────────┐
│           CLAUDE CODE — HIZLI BAŞVURU               │
├─────────────────────────────────────────────────────┤
│ Güne başlarken:                                     │
│   Read CLAUDE.md and continue from where            │
│   we left off                                       │
│                                                     │
│ Yeni adıma başlarken:                               │
│   Read ~/otomaix/docs/[dosya].md                    │
│   and complete Step [N]                             │
│                                                     │
│ Adım bitince (HEMEN):                               │
│   Update CLAUDE.md: Step [N] done,                  │
│   next is Step [N+1]                                │
│                                                     │
│ Terminali kapatmadan önce:                          │
│   Update CLAUDE.md with today's progress            │
│   and what comes next                               │
│                                                     │
│ Session kesilirse:                                  │
│   Read CLAUDE.md and continue from                  │
│   where we left off                                 │
└─────────────────────────────────────────────────────┘
```

---

## Proje Sırası — Ne Zaman Ne Yaparsın?

```
Şu an:        00-platform-mimari.md oku (bir kez, genel resim)
              ↓
Ay 1-2:       01-social-phase1.md (altyapı)
              ↓
Ay 2-3:       02-social-phase2.md (temel özellikler)
              Paralelde: 05-crm-admin.md başlatılabilir
              ↓
Ay 3-4:       03-social-phase3.md (gelişmiş özellikler)
              ↓
Ay 4-6:       04-social-phase4.md (SaaS hazırlık)
              ↓
Sonrası:      Yeni Otomaix uygulamaları için
              00-platform-mimari.md güncelle
              Yeni kılavuz MD dosyası oluştur
```

---

*Bu dosyayı ~/otomaix/docs/ klasörüne koy. Bir şeyleri unuttuğunda buraya bak.*
