# Security Review: Otomaix Brain Doctor v1 — 2026-05-21

Kapsam: BASE 9b0376d..HEAD f8e1503, `tooling/brain-doctor/`
Reviewer: bağımsız fresh general-purpose subagent + Claude doğrulaması (ampirik)
Bağlam: pre-merge
Tehdit modeli: saf stdlib yerel CLI — ağ/DB/subprocess/eval/auth/secret YOK. Tek-kullanıcılı geliştirici aracı; güvenilmeyen girdi = vault `.md` içeriği + dosya adları. Uzak saldırgan yok → bulgular klasik "vuln"den çok robustness/availability.

## Kritik

Sorun bulunmadı.

## Yüksek

- **ReDoS (kuadratik backtracking)** — `_MDLINK_RE` + `_WIKILINK_RE`, brain_doctor.py:144-145.
  Bracket-yoğun (`[`*N) vault içeriği O(n²) backtracking yapıyordu (ölçüldü: 60k=1.6s, extract_links(100k)≈10s+, ~1MB dakikalar). strip_code yalnız code-fence içini temizliyor; fence dışı bracket'ler regex'e ulaşıyor.
  **DURUM: DÜZELTİLDİ.** Negated class'lara `{1,512}` sınırı eklendi → lineer (1M bracket: md 0.46s, wiki 2.7s). Reviewer'ın `[^\]\n]+` önerisi yanlıştı (tek-satır payload'da daha yavaş — ampirik doğrulandı), uzunluk sınırı doğru çözüm. Gerçek linkler <512 char → davranış değişmedi (smoke birebir aynı). Regresyon testi: `TestSecurity.test_extract_links_no_redos` (timing, 100k bracket < 3s).

## Orta

- **Symlink ile vault dışı okuma** — `iter_markdown_files`/`read_pages`, brain_doctor.py.
  Vault içindeki bir `.md` symlink'i vault dışı dosyayı gösterirse rglob listeliyor, read_text izleyip dış içeriği okuyordu (test: 'TOP SECRET' okundu). Body raporlanmadığı için exfiltration sınırlı ama dış dosyadaki frontmatter/link değerleri rapora `detail` olarak sızabilirdi.
  **DURUM: DÜZELTİLDİ.** `iter_markdown_files`'a `if p.is_symlink(): continue` eklendi. Vault'ta symlink yok → davranış değişmedi. Test: `TestSecurity.test_symlinked_md_is_skipped`.

- **Sınırsız bellek tüketimi** — `read_pages`, brain_doctor.py:138-145. Tüm sayfalar tek dict'e okunuyor, üst boyut sınırı yok; GB'lık dosya bellek patlatabilir.
  **DURUM: ERTELENDİ (v1.1 hardening).** Gerekçe: en büyük gerçek vault dosyası 20KB, tek-kullanıcılı elle bakımlı vault → YAGNI. Vault ileride dış dosya auto-import ederse `read_text` öncesi `stat().st_size` tavanı eklenmeli.

## Düşük

- **Markdown rapor escape eksikliği** — `render_markdown`, brain_doctor.py. Vault'tan gelen link target/detail string'leri report.md'ye escape'siz gömülüyor (raporu okuyan başka markdown render'ı yanıltabilir; kod-çalıştırma yok). JSON çıktı `json.dumps` ile düzgün escape'li (sorun yok).
  **DURUM: ERTELENDİ (v1.1).** Rapor bir trust boundary değil (kullanıcı/Claude okuyor).
- **rglob symlink-dizin döngüsü** — Python 3.12 symlinked dizinleri default izlemiyor (test: döngü sonsuza gitmedi). Aksiyon gerekmiyor.
- **Hata mesajı bilgisi** — exception mesajları stderr'e (yol/IO); secret yok, yerel araç. Aksiyon gerekmiyor.

## Kapatılan / False Positive

- Reviewer'ın ReDoS için önerdiği `[^\]\n]+` düzeltmesi → **yanlış** (tek-satır payload'da quadratic'i kesmiyor, daha yavaş). Doğru fix `{1,512}` uzunluk sınırı (ampirik doğrulandı, uygulandı).
- Injection (subprocess/eval/exec): kaynakta yok — doğrulandı.
- Hardcoded secret: yok (config'deki `vault_path` bir yol).
- vault-output guard: reviewer `..` traversal + dış symlink ile test etti → sağlam, atlatma yok.

## Sonuç

0 Kritik, 1 Yüksek (kapatıldı), 2 Orta (1 kapatıldı / 1 ertelendi), 3 Düşük (ertelendi/aksiyon yok). 38 unittest PASS, gerçek vault smoke birebir aynı (28 bulgu, exit 1, vault değişmedi). **Merge'e güvenli** — tek Yüksek (ReDoS) ve thin Orta (symlink) bu branch'te kapatıldı; kalan Orta/Düşük tek-kullanıcılı yerel araç için v1.1 hardening notu.
