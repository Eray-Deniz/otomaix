# Review (dual): denetçi süreç izolasyonu — 2026-09-18

Review aralığı: `496ddbd..d215452`
- BASE_REF: `496ddbd` | BASE_SHA: `496ddbd` | HEAD_SHA: `d215452` | REVIEW_BASE_SHA (merge-base): `496ddbd` (sapma YOK)
Reviewers: fresh Claude subagent (`general-purpose`, code-reviewer personası) + Codex `adversarial-review`
dual-review: **true** (claude_status: ran; codex_status: ran)
Review workspace: pinli worktree @ `d215452` (temiz)
Main tree at review: clean (0 uncommitted dosya)
Requirement context: `docs/active/denetci-surec-izolasyonu/TASK.md` **TABAN sürümü** (`git show 496ddbd:…`) — committed, hash `baeec71f237dcf3c`, 236 satır.

> **Sözleşme sapması (beyan).** Gereksinim metni prompt'a GÖMÜLMEDİ; iki hakem de **aynı pinli
> dosyayı** okudu (`/tmp/review-wt.xJaPWs/REQUIREMENT_SNAPSHOT.md`, taban sürümün birebir kopyası).
> Sebep: argüman boyut sınırı. Ortak-mod riski: ikisi de aynı baytları gördü — amaçlanan buydu.
> Yürütücünün sonradan yazdığı "bitti/ölçüldü" iddiaları BİLEREK dışarıda bırakıldı ki hakemler
> iddiaları koddan doğrulasın.

---

## Critical

**F1 — Kutulu codex kendi kimlik dosyasını okuyabiliyor ve ağı açık: kimlik sızdırma yolu.**
`auditors.py` (`_alt_surec_ortami`, `denetci-2` `ToolSpec`) · [single-source: codex] · **claude-confirmed**

`HOME=/home/codex` (T8) kutulu sürece kendi evini gösteriyor; o evde `~/.codex/auth.json` **canlı
kimlik** olarak duruyor. Aynı profil `workspace-write` + **ağ açık** (T10) koşuyor ve Codex kum
havuzu YAZMAYI kısıtlar, OKUMAYI kısıtlamaz. Yani pakete gömülü bir talimat kimliği okuyup dışarı
gönderebilir.

**Kontrolörün kendi ölçümü (2026-09-18):** üretim argv'si ve üretim yoluyla koşan kutulu codex'e
`sha256sum ~/.codex/auth.json | cut -c1-16` ve `wc -c` yaptırıldı → **`eebdf1ca1d57413b` / 3981
bayt**; kontrolörün bağımsız ölçümü birebir aynı. (İçerik BASTIRILMADI.)

Bu yolu **bu dal açtı**: kimlik zaten oradaydı (T3 turlarından), ama ağ yoktu. T10 ağı açınca
okuma+gönderme zinciri tamamlandı. T13 kanaryası bunu GÖREMEZ — hedefi root'un `.env`'i, kutulu
kullanıcının KENDİ evi değil.

## High

**F2 — Kutulu ev turlar arası tam oturum kaydı tutuyor; "kalıcı hiçbir şey açılmaz" iddiası düşüyor.**
`auditors.py` (`_alt_surec_ortami`) · [single-source: claude — hakem "doğrulanmadı" etiketiyle verdi] · **claude-confirmed**

Sahne tasarımının merkez gerekçesi şuydu: *"Kalıcı hiçbir şey kutulu kullanıcıya açılmaz"* — çünkü
kalıcı bir arşiv GEÇMİŞ turların içeriğini okunur kılardı. CLI bu arşivi kutunun İÇİNDE yeniden
kuruyor: `~/.codex/sessions/<yıl>/<ay>/<gün>/rollout-*.jsonl`.

**Kontrolörün kendi ölçümü:** bugün **28 oturum kaydı**; izler aranınca `PAKET-ICI` 4 dosyada,
`paket icerigi` 4 dosyada, `KARDES TURUN PAKETI` 1 dosyada, K-14 meydan okuma URL'i 7 dosyada.
Dizin izni `drwxrwxr-x codex codex`, kutulu kullanıcı için **OKUNABİLİR**. Ayrıca altı `*.sqlite`
(memories/state/thread_history/goals/queue/logs) bugün yazılmış.

Sonuç: aynı kaynaklara ikinci tur atıldığında kutulu codex ÖNCEKİ turun paketini ve kendi raporunu
okuyabilir. Tur-İÇİ K-79 körlüğü bozulmuyor (denetci-1 root'ta, kaydı `/root` altında), ama
**turlar-arası** bağımsızlık bozuluyor.

**F3 — `/tmp` paylaşımı sahne izolasyonunu kırıyor; diskte ŞU AN kalıntı sahne var.**
`auditors.py` (`_sahne_kokunu_ac`, `_sahne`) + `denetci-2` sandbox kipi · [single-source: codex] · **claude-confirmed**

Sahneler `/tmp` altında ve tek bir `codex` UID'sine devrediliyor; `workspace-write` kum havuzu
`/tmp`'yi açıkça yazılabilir sayıyor. **Kontrolörün ölçümü:** kutulu codex (a) `/tmp/denetci-sahne-*`
dizinlerini listeledi, (b) kardeş bir sahnenin paket dosyasını **okudu** (`KARDES TURUN PAKETI`),
(c) `/tmp/h2-kanit.txt` yazdı (sahibi uid 1001, kontrolör ayrıca diskten doğruladı).

Üstüne: **`/tmp/denetci-sahne-uoiaj30t` 2026-09-17 11:23'ten kalma, sahibi `codex`, içinde
`denetci-1` var.** Bu, önceki oturumun bilinçli DÜŞÜRDÜĞÜ `SIGKILL` kalıntısının **yeniden açma
koşuludur** (*"diskte kalmış bir sahne görülürse"*) — koşul gerçekleşti. Kanarya bu ekseni
ıskalıyor: yazma ayağı `/root/…` hedefliyor, yani izinle zaten reddedilen bir yol.

**F4 — Sahne, ayrıcalıklı işlemler bitmeden devrediliyor; `chmod` symlink izliyor.**
`auditors.py` `_sahne` · [single-source: claude] · **claude-confirmed**

Sıra: `kok.chmod(700)` → `os.chown(kok)` → çocukları `chown` → **`sahne.chmod(0o700)`**.
İkinci adımdan sonra `kok` artık `codex`'in; root hâlâ o ağaçta iş yapıyor. `os.chown` çağrıları
`follow_symlinks=False` taşıyor (güvenli), ama `Path.chmod` symlink **İZLER** — ölçüldü: symlink'e
`chmod(0o700)` uygulandığında HEDEFİN izni 0700 oldu. `codex` kimliğiyle koşan bir süreç `sahne`
girdisini symlink'le değiştirirse root, saldırganın seçtiği yolu `0700` yapar.

Ön koşul uzak değil: F3 gösterdi ki kutulu denetçi `/tmp`'de gezinip yazabiliyor. Kapanış ucuz:
`chmod`'u devretmeden ÖNCE yap, `kok`'u EN SON devret.

**F5 — `denetci-1` root koşarken `WebFetch` kazandı; tek duvar CLI'da ve SÜREKLİ kapısı yok.**
`auditors.py` (`_CLAUDE_DENETCI_ARAC_KUMESI`, `ARAC_KOMUTLARI`) · **[both-agree]**

Codex: donmuş hedef iki denetçinin de root'tan çıkmasını istiyor; `denetci-1` `kullanici=None` ile
root kalıyor ve yeni test bu sapmayı beklenen politika olarak **yeniden sözleşmeleştiriyor**.
Claude: itiraz karara değil — ağ açılmadan önce `--restricted` gerilemesi "okur ama gönderemez"
demekti; şimdi aynı gerileme **doğrudan sızdırma** olur, üstelik süreç root. Kodun kendi dürüst
etiketi zaten *"hapsi işleten CLI'nın kendisi, işletim sistemi DEĞİL"* diyor; testler bayrağın
VARLIĞINI ölçüyor, DAVRANIŞINI değil. Davranışı ölçen tek şey kanarya — takım dışında, elle,
**zamanlanmış evi olmadan**.

**F6 — Hedef allowlist'i yok; T13'ün "yetkisiz geri çağrı" ayağı karşılanmadı, yeniden tanımlandı.**
`denetci_kanaryasi.py` + iki araç profili · [single-source: codex] · **claude-confirmed**

İki profilde de serbest dış çıkış var; denetlenen kaynaklara bağlı bir hedef kısıtı YOK. Pakete
gömülü bir talimat brief'i, kaynakları ya da aktif paket içeriğini saldırganın URL'ine gönderebilir —
root sırları okunamasa bile. Kanarya bunu ölçmüyor; betiğin kendisi ayağı "artık bilerek düşmez"
diye yeniden tanımlıyor. Kontrolör ölçümü: kanarya koşumunda codex `curl | jq` ile dış veri getirdi.

## Medium (accepted_risk — fix EDİLMEZ, re-review AÇMAZ)

**F7 — T6b sürümlenmeyen yerde çözüldü; kardeş test çelişiyor; iki klasör kapsam taşması.** **[both-agree]**
Snapshot `.gitignore` diyor, inen çözüm yerel `.git/info/exclude`. Pin gerekçesi ölçülmüş ve
geçerli, ama koruma yeniden klonlamada kaybolur ve tripwire tek makineye bağlı. Aynı dosyadaki
kardeş test (`test_external_repo_gitignores_run_folder`) **tam tersi** gerekçeyi yazılı taşıyor.
`Kuyumculuk/` + `silinecek/` operatörün yerel klasörleri — commit'li teste sabitlenmeleri kapsam
taşması. *(Karar kaydı: mekanizma tercihi Eray'ındır, 2026-09-18; iki klasör de onun talebiyle
eklendi. Bulgu kararı değil, sonucunu işaret ediyor.)*

**F8 — Kutu tripwire'ının `sudo` yolunun pozitif kontrolü YOK — sessiz-yeşil sınıfı açık.** [single-source: claude] · **claude-confirmed**
`_okuma_denemesi(..., kullanici=KULLANICI)` sudo ile koşuyor; pozitif kontrol ise `kullanici=None`
(sudo'suz) yolu ölçüyor. Sudo mekanizması herhangi bir sebeple rc≠0 dönmeye başlarsa TÜM hedefler
"okunamadı" olur ve iki test de yeşil kalır. T6 ile bu yolun yükü arttı (kanonik ağaç da buradan
kapanıyor). Ucuz kapanış: dünyaya açık bir hedefin kutulu kullanıcı adına **True** dönmesi.

**F9 — Kanarya hedefi GERÇEK `.env`; yem dosya aynı iddiayı riske atmadan ölçer.** [single-source: claude] · **claude-confirmed**
(d) ayağı ağı açık bir ajana kendi sırlarının yolunu veriyor. Sınır düşerse sır ÖNCE ağdan çıkar,
kanarya olaydan SONRA rapor eder. *(Kontrolör notu: bu risk bu oturumda fiilen gerçekleşti —
kutu-söküldü mutasyonunda gerçek `DATABASE_URL` satırı oturum dökümüne düştü. `/root` altında `0600`
bir yem dosya aynı iddiayı ölçerdi.)*

## Low (accepted_risk)

- **L1** Docstring sahibi değişti ve bayatladı: büyük izolasyon docstring'i artık `_CLAUDE_DENETCI_IZOLASYON`'da ve hâlâ *"`read-only`'nin karşılığı, simetri KASITLIDIR"* diyor — oysa `denetci-2` artık `workspace-write` + ağ. `_CLAUDE_IZOLASYON` docstring'siz kaldı. [claude]
- **L2** Ölü sabit: `AG_ARACLARI` tanımlı, hiçbir yerde okunmuyor. [claude]
- **L3** Sihirli dilim: `YAZAN_ARACLAR[:4]` — sabit yeniden sıralanırsa yasak-liste beklentisi sessizce kayar. [claude]
- **L4** T6 tripwire maliyeti arşivle doğrusal büyüyor (bugün 46 düğüm / 2,5 s; her tur büyütür). [claude]
- **L5** Kanarya gerçek sızıntıdan sonra kendini kilitliyor (hedef dosya kalır → sonraki koşum rc=1) ve yazma ayağını role bağlamıyor. [claude]
- **L6** Ölçülmemiş biçim iddiası: docstring "satır kırma"yı da yakaladığını söylüyor; `imza in cikti` tam alt-dize eşleşmesi, değerin ortasına giren satır sonu hem tespiti hem maskelemeyi atlatır. [claude]
- **L7** Kapı ihtiyacı olmayan tam parmak izini hesaplayıp atıyor (`_rol_agaci_parmagi`'nin yalnız `reddedilen`'i kullanılıyor). [claude]
- **L8 (kapsam notu)** T12 snapshot'taki maddeyi aynen karşılamıyor; daha temel bir kusuru kapatıyor ve maddenin gerekçesinin bugün geçersiz olduğunu ölçümle gösteriyor. Dürüstçe etiketlenmiş. [claude]

---

## Disposition Ledger

| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| F1 | codex | critical | critical | kept | claude-confirmed (hash+boyut birebir) |
| F2 | claude | medium (doğrulanmadı) | **high** | kept, **yükseltildi** | hakem ölçemedi; kontrolör ölçtü: 28 oturum kaydı + paket izleri okunabilir → tasarımın merkez iddiası düşüyor |
| F3 | codex | high | high | kept | claude-confirmed; ayrıca kalıntı sahne diskte bulundu |
| F4 | claude | high | high | kept | claude-confirmed (sıra + `chmod` symlink davranışı ölçüldü) |
| F5 | codex + claude | high + high | high | kept | **both-agree** (farklı çerçeve, aynı eksen) |
| F6 | codex | high | high | kept | claude-confirmed (argv + kanarya koşumu) |
| F7 | codex + claude | medium + medium | medium | kept (accepted_risk) | **both-agree** |
| F8 | claude | medium | medium | kept (accepted_risk) | claude-confirmed (kod okumasıyla) |
| F9 | claude | medium | medium | kept (accepted_risk) | claude-confirmed; oturumda fiilen gerçekleşti |
| L1–L8 | claude | low | low | kept (accepted_risk) | — |
| — | codex | — | — | merged-into F5 | Codex'in "denetci-1 root" + Claude'un "root+WebFetch sürekli kapı yok" aynı eksen |
| — | claude | — | — | merged-into F1/F2 | Claude'un `HOME` kalıcılık bulgusu F2'ye, kimlik ayağı F1'e |

Sessizce düşürülen ham bulgu YOK.

## Sonuç

- Kapatılan (push-back): 0 (push-back turu kullanıcıya açık)
- Açık: **1 critical + 5 high** (fix-required) · 3 medium + 8 low (`accepted_risk`)
- Hakemler-arası çelişki: yok. İki hakem **farklı** eksenler buldu; tek örtüşme F5 ve F7.
- **Ortak-mod kontrolü:** bulguların hiçbiri orchestrator'ın bağlam cümlesine iz sürmüyor —
  bağlam nötr betimlemeydi ("bu bileşenlerin ne garanti ettiğini koddan değerlendir"), rol iddiası
  yazılmadı. `both-agree` sinyali geçerli.

## Kapsanan / kapsanmayan (overclaim YOK)

- **Kapsanan:** sekiz değişen dosyanın tamamı, iki hakem tarafından bağımsız; gereksinim tabanı;
  ilgili yardımcılar (`kok_yolunu_kapila`, `_rol_agaci_parmagi`, `_paket_butunluk_kapisi`, `_web_probu`).
- **Kapsanmayan:** hiçbir hakem test takımını koşturamadı (Codex: yazılabilir temp yok; Claude:
  worktree'de `.venv` yok). TASK.md'nin "4562 passed", "22 mutasyonun 22'si", süre sayıları ve
  kanaryanın "sekiz ayak" iddiaları **bu review'da doğrulanmadı** — kontrolörün kendi taze
  koşumlarına dayanıyor (oturum içinde ölçüldü, hakem teyidi YOK).
- **Ölçülemeyen:** CLI bayraklarının (`--restricted`, `--tools`, sandbox kipleri) gerçek davranışı
  hakemlerce ölçülmedi; kontrolörün kanarya koşumları bu boşluğun bir kısmını kapatıyor.
- **Exhaustiveness iddiası YOK.**

## Ham kanıt — işaretçiler (bu makinede, bu kökten)

- Codex ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-18-review-feat-sektor-bilgi-paketi-plan2-1.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-09-18-review-feat-sektor-bilgi-paketi-plan2-1.claude.md`
