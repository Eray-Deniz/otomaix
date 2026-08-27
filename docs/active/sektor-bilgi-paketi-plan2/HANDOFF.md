---
task: sektor-bilgi-paketi-plan2
written: 2026-08-27
---

# Resume From

**Plan ONAYLANDI (Eray, risk kabulüyle) — sıradaki adım YÜRÜTME.**
`/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
Önerilen kip: **subagent'lı** (her görev taze bağlam, aralarda review) — 20 görev tek
bağlamda taşınmaz.

- Plan: `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` — 20 görev,
  **`plan-approved` + `approved-by-iteration-limit`**, `unresolved_high_severity_override: true`.
- Tahkim kaydı: `docs/reviews/codex/2026-08-27-sektor-bilgi-paketi-plan2.md`
  (tur özeti · disposition ledger · DUR notu · bağımsız hakem itirazları).
- Dal: `feat/sektor-bilgi-paketi-plan2`, son commit **`367d059`** (onay + tüm hakem
  düzeltmeleri). **Hiçbir şey push EDİLMEDİ** (ölçüldü 2026-08-27): dal yerel `main`'in
  2 commit önünde (`f18e389`, `367d059`); yerel `main` de `origin/main`'in 4 commit önünde
  (`origin/main` = `38ea98f`).

**Oturum kuralı — KAPSAMI YALNIZ O OTURUMDU, YENİ OTURUMDA TEYİT ET.** 2026-08-27'de Eray
"hakem turlarını ben koşarım" dedi ve bunun kalıcı hafızaya yazılmamasını istedi. Yani bu
kural **otomatik devredilmez**: yeni oturumda bir hakem turu gerekirse önce sor —
"ben mi koşayım, sen mi koşacaksın?". Yürütme sırasındaki checkpoint review'ları bu sorunun
dışındadır; onlar komutun kendi akışıdır.

# Verification

**Koşulan komutlar ve taze çıktıları:**
- Task başlık kapısı (`_ec_plan_headers`) → bozuk başlık YOK, dizi `1..20` kesintisiz.
- `plan-lint.sh` → temiz (karar-katmanı sözleşmesine uygun).
- `command-blocks-maint.sh verify` → PASS.
- Placeholder taraması (`TBD|TODO|implement here`) → 0.
- Sır deseni taraması → 0. (Bir tur bu yüzden yanmıştı: plana yazdığım ölçüm komutu bir
  kimlik başlığı adı içeriyordu, substrat plan dosyasını dışladı, hakem planı hiç görmedi.)
- Çalışma dizini taraması → `cd`'siz pytest komutu 0.
- İçerik şeması ölçümü → CTA ve özel gün girdileri **tam anahtar eşitliğiyle**, diğer liste
  öğeleri **düz metin** olarak doğrulanıyor → kimlik içerikte SAKLANAMAZ (tasarımı bu belirledi).
- `kirp` kanonik anlamı ölçüldü (spec-input:1160): *"paketten çıkarır, kayıttan çıkarmaz"*.
- Canlı takvim workflow'u ölçüldü: `ON CONFLICT (year,date) DO UPDATE` ile ad/kategori
  düzeltiyor → "ezme" kuralı canlı davranışla çelişiyordu, düzeltildi.
- n8n ölçümü: 18 workflow · 13 aktif · `errorWorkflow` taşıyan 0.

**Kapanış turu (2026-08-27, bağlantı koptuktan sonra tamamlandı):**
- Push durumu ölçüldü (`git branch -vv`, `git rev-list`): dal yerel `main`'in 2 commit,
  yerel `main` de `origin/main`'in 4 commit önünde. Hiçbir şey push edilmedi.
- Bayat-kayıt taraması: 4 çelişki bulundu ve düzeltildi — HANDOFF'ta yanlış push cümlesi ·
  "plan onaylı değil" (artık onaylı) · "commit onayı bekliyor" (işlendi) · devralınmış
  hakem-turu kuralı; TASK.md'de Task 15'in "plan onaylı değil" gerekçesi.
- Evsiz-kova sweep (İlke 7), CURRENT.md'nin 10 proposed kalemi tek tek: 8'i sağlam tetikliydi.
  İkisinin evi plan onaylanınca somutlaştı → **Task 16 Step 7/7b** (n8n hata bildirimi) ve
  **Task 19 Step 11** (atama arayüzü elle doğrulaması) olarak adlandırıldı.
  Biri (`s1-substrate-tracked-secret-scan`) **tetiksizdi** → kardeş iki `~/.claude` kalemiyle
  aynı pin'li bloğa bağlandı, üçü tek turda.
- `git diff --check` → temiz. CURRENT.md'de statü sızıntısı taraması → 0.

**Denenmemiş senaryolar:**
- **Hiçbir kod yazılmadı, hiçbir test koşulmadı** — bu oturum tamamen doküman işiydi.
  Plandaki tüm test adları henüz var olmayan dosyalara aittir.
- Plan 1 bölümlerinin kart geçişi hâlâ koşulmadı (boşluk raporu kapsam sınırı).
- **Son parti hiçbir hakem tarafından görülmedi.** Sıra: bağımsız hakem 10 itiraz →
  düzeltildi → 9 kalan boşluk → düzeltildi → 6 kalan boşluk → düzeltildi → **kök tasarım
  turu** (K-145 sözleşmesi + Task 12/13 sahipliği). Bu son parti incelenmedi ve
  **genel review turu bilinçle DURDURULDU** — kalan risk ölçülmedi, kabul edildi.

# Risks

- **Onay bir kez ERKEN verildi ve geri alındı** (tarihçe; plan bugün onaylı). Zincir tur 6'da `approve`
  verdi; sonra bağımsız hakem 10 itiraz getirdi, onu da doğrulandı. Onay geri alındı.
  **Ders:** tek hakem zincirinin yakınsaması kapsama kanıtı değildir — altı tur tek eksende
  (köken/kapı zinciri) daralırken diğer eksenler hiç taranmadı.
- **Tekrarlayan kusur sınıfı: karar katmanını yazıp tüketicilerini bağlamamak.** Bu oturumda
  en az beş kez tekrarladı (kapı listesi · kimlik alanları · Katman-2 · CLI komutu · K-145).
  Bir invariant yazarken **onu tüketen HER görevi** aynı turda güncelle.
- **KABUL EDİLMİŞ RİSK: onay temiz hakem zinciriyle alınmadı.** Dört ardışık bağımsız tur
  "gerçek düzeltme var ama eksik" dedi; yakınsama gözlenmedi. **Son iki düzeltme partisi
  hiçbir hakem görmedi.** Eray bunu bilerek onayladı. **Kalan kusurlar yazım anında
  çıkacak** — yürütmedeki kırmızı-yeşil döngüsü ve checkpoint review'ları asıl ağı budur.
- Plan 1 arayüzünde bir **davranış değişikliği** var (aktivasyon kanıtının taban durumu artık
  açıkça ifade ediliyor); Plan 1'in ilgili testleri bilinçli olarak kırılacak, Task 15'te
  güncelleniyor.

# Notes For Claude/Codex

- **Hakem turu kimin? ÖNCE SOR.** 2026-08-27 oturumunda "Claude başlatmaz" kuralı
  konmuştu; kapsamı o oturumdu (bkz. Resume From). Yeni oturumda bir hakem turu gerekirse
  teyit al — devralınmış kural gibi davranma.
- Bulgu geldiğinde: **önce ölç, sonra kabul et.** Bu oturumda 24 + 10 + 9 bulgunun hepsi
  ölçülerek doğrulandı, hiçbiri reddedilmedi; ama iki kez yanlış şeyi ölçüp sıfırları
  "yok" diye sunmaya yaklaştım — komutun gerçekten o soruyu ölçtüğünü doğrula.
- **Spec değil, spec-input kanonik.** Bu oturumda üç kez fark yarattı (K-100'ün dördüncü
  alanı · K-145'in üç kuralı · `kirp` semantiği).
- Plan hiçbir açık ürün kararını kapatmıyor: K-85 · K-153 · K-128 · K-52 · K-11(a/b) ·
  K-32…K-37. Belirsiz vakalar açık soruya düşüp aktivasyonu blokluyor.
- Diskte bekleyen düzeltme YOK: onay ve tüm hakem düzeltmeleri `367d059`'de işlendi.
