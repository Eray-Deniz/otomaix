"""Dış sözleşme pin'inin fail-closed doğrulayıcısı (plan Task 1).

Kapı kümesi TAM OLARAK dörttür (plan 423-426): dosya yok · hash uyuşmuyor ·
commit uyuşmuyor · depo dizini yok. Arayüz eki R1/R14 bunun üstüne bir NEGATİF
invariant bağlar: **kirli çalışma ağacı tek başına pini DÜŞÜRMEZ** — manifestte
adı geçmeyen hiçbir dosya/dizin (izlenmeyen `kosu/<run_id>/` dâhil) uyuşmazlık
üretmez ve doğrulama salt-okunurdur.

Fixture disiplini: gerçek araştırma deposu (`/root/otomaix-sosyal-medya-
arastirmasi`) hiçbir testte DEĞİŞTİRİLMEZ. Davranış testleri `tmp_path` altında
kendi sahte üç dosyalı git deposunu kurar; ölçülen şey gerçek dosya sistemi ve
gerçek `git` HEAD'idir, sahte nesnenin davranışı değil. Task 2'nin eklediği üç
test (gerçek pin + `.gitignore`) gerçek artefaktları SALT-OKUR — pin'in işi
zaten yürürlükteki sözleşme sürümünü bağlamaktır.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from app.services.sector_pipeline.contracts import (
    _HEAD_OKUNAMADI,
    ContractDriftError,
    ContractPin,
    load_pin,
    require_pin,
    verify_pin,
)

# Pinlenen üç sözleşme dosyası (arayüz eki R1, madde (a)).
CONTRACT_FILES = (
    "_SABLON.md",
    "hakem-denetci-gorevi.md",
    "hakem-sentez-gorevi.md",
)

# GERÇEK artefaktlar (dosyanın sonundaki üç test bunları salt-okur). Yollar
# plan 81/450-457'de kanonik olarak yazılıdır; depo yoksa test ATLANMAZ,
# DÜŞER (fail-closed) — atlanan bir pin testi pin'i olmayan bir sistemi
# yeşil gösterirdi.
MONOREPO_KOK = Path(__file__).resolve().parents[4]
GERCEK_PIN_PATH = MONOREPO_KOK / "shared/contracts/research-contracts.pin.json"
GERCEK_ARASTIRMA_DEPOSU = Path("/root/otomaix-sosyal-medya-arastirmasi")


# ─── Sahte dış depo kurulumu ────────────────────────────────────────────────


def _git(repo: Path, *args: str) -> str:
    """Sahte depoda git çalıştırır. Kurulum aracıdır — üretim kodu değil."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_fake_repo(tmp_path: Path) -> Path:
    """`tmp_path` altında üç sözleşme dosyalı, tek commit'li sahte depo."""
    repo = tmp_path / "arastirma-deposu"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "master")
    _git(repo, "config", "user.email", "test@otomaix")
    _git(repo, "config", "user.name", "Test")

    for name in CONTRACT_FILES:
        (repo / name).write_text(f"# {name}\n\nsözleşme gövdesi\n", encoding="utf-8")
    # Pinlenmeyen ama izlenen bir dosya — kirlilik testinin malzemesi.
    (repo / "README.md").write_text("pinlenmeyen dosya\n", encoding="utf-8")

    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "ilk sözleşme sürümü")
    return repo


def _pin_for(repo: Path, *, commit: str | None = None) -> ContractPin:
    """Deponun BUGÜNKÜ hâlinden eşleşen bir pin üretir."""
    return ContractPin(
        commit=commit if commit is not None else _git(repo, "rev-parse", "HEAD"),
        files={name: _sha256(repo / name) for name in CONTRACT_FILES},
    )


def _write_pin_file(hedef_dizin: Path, pin: ContractPin) -> Path:
    hedef_dizin.mkdir(parents=True, exist_ok=True)
    pin_path = hedef_dizin / "research-contracts.pin.json"
    pin_path.write_text(
        json.dumps({"commit": pin.commit, "files": dict(pin.files)}, indent=2),
        encoding="utf-8",
    )
    return pin_path


# ─── Dört kapı ──────────────────────────────────────────────────────────────


def test_verify_passes_on_matching_hashes(tmp_path: Path) -> None:
    """Pozitif kontrol: kapı gerçekten GEÇEBİLİYOR (hep-RED doğrulayıcı değil)."""
    repo = _make_fake_repo(tmp_path)

    assert verify_pin(_pin_for(repo), repo) == []


def test_verify_fails_on_content_drift(tmp_path: Path) -> None:
    """Tek bayt değişir → RED, ve sebep DEĞİŞEN dosyayı adıyla söyler."""
    repo = _make_fake_repo(tmp_path)
    pin = _pin_for(repo)

    drifted = repo / "hakem-denetci-gorevi.md"
    drifted.write_bytes(drifted.read_bytes() + b"x")

    reasons = verify_pin(pin, repo)

    assert reasons != []
    assert any("hakem-denetci-gorevi.md" in reason for reason in reasons)
    # Commit kaymadı: yalnız içerik kapısı düşmeli, commit kapısı değil.
    assert not any(_git(repo, "rev-parse", "HEAD") in reason for reason in reasons)


def test_verify_fails_on_commit_drift(tmp_path: Path) -> None:
    """Üç dosya AYNI kalsa bile HEAD kayarsa RED (izole commit kapısı)."""
    repo = _make_fake_repo(tmp_path)
    pin = _pin_for(repo)

    (repo / "baska-dosya.md").write_text("sonraki commit\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "ikinci commit")

    reasons = verify_pin(pin, repo)

    assert reasons != []
    # Üç sözleşme dosyasının hiçbiri değişmedi; tek sebep commit olmalı.
    assert not any(name in reason for reason in reasons for name in CONTRACT_FILES)
    assert any(pin.commit in reason for reason in reasons)


def test_verify_fails_on_missing_file(tmp_path: Path) -> None:
    """Pinlenen dosya silinirse RED."""
    repo = _make_fake_repo(tmp_path)
    pin = _pin_for(repo)

    (repo / "hakem-sentez-gorevi.md").unlink()

    reasons = verify_pin(pin, repo)

    assert reasons != []
    assert any("hakem-sentez-gorevi.md" in reason for reason in reasons)


def test_verify_fails_on_missing_repo(tmp_path: Path) -> None:
    """Depo dizini hiç yoksa RED — 'depo yok = sorun yok' dalı YOKTUR.

    Assert kapının KENDİ sebebine bakar, "bir sebep döndü"ye değil. Eski hâli
    ayırt etmiyordu: dizin yokken üç dosya da bulunamadığı için `str(yok)`
    zaten dosya-yok sebeplerinin içinde geçiyordu; `is_dir()` erken dönüşü
    silindiğinde test yeşil kalıyordu (Task 1 review'ında mutasyonla ölçüldü).
    Erken dönüş TEK sebep üretir — sayı da, metin de bunu söylemeli.
    """
    repo = _make_fake_repo(tmp_path)
    pin = _pin_for(repo)
    yok = tmp_path / "olmayan-depo"

    reasons = verify_pin(pin, yok)

    assert reasons == [f"depo dizini yok: {yok}"]


def test_require_pin_raises_contract_drift_error(tmp_path: Path) -> None:
    """`require_pin` manifesti diskten okur; uyuşmazlıkta fırlatır, uyumda susar."""
    repo = _make_fake_repo(tmp_path)

    # Pozitif kontrol: eşleşen manifest sessizce geçer (hep-fırlatan kapı değil).
    iyi_pin_path = _write_pin_file(tmp_path, _pin_for(repo))
    assert require_pin(iyi_pin_path, repo) is None
    assert load_pin(iyi_pin_path) == _pin_for(repo)

    # Negatif: commit drift'li manifest.
    kotu_pin_path = _write_pin_file(tmp_path / "kotu", _pin_for(repo, commit="0" * 40))

    with pytest.raises(ContractDriftError):
        require_pin(kotu_pin_path, repo)


# ─── Negatif invariant (arayüz eki R1 · R14, Sahip: Task 1) ─────────────────


def test_verify_passes_with_dirty_external_worktree(tmp_path: Path) -> None:
    """Kirli çalışma ağacı TEK BAŞINA pini DÜŞÜRMEZ; doğrulama salt-okunurdur.

    Manifestte adı geçmeyen hiçbir şey uyuşmazlık üretmez: izlenmeyen
    `kosu/<run_id>/` klasörü de, pinlenmeyen izlenen bir dosyanın değişmesi de.
    """
    repo = _make_fake_repo(tmp_path)
    pin = _pin_for(repo)

    kosu = repo / "kosu" / "run-2026-08-30-001"
    kosu.mkdir(parents=True)
    (kosu / "x.md").write_text("koşu artefaktı\n", encoding="utf-8")
    (repo / "README.md").write_text("pinlenmeyen dosya DEĞİŞTİ\n", encoding="utf-8")

    # Ağacın gerçekten kirli olduğunun kanıtı (fixture pozitif kontrolü).
    kirlilik_once = _git(repo, "status", "--porcelain")
    assert kirlilik_once != ""

    assert verify_pin(pin, repo) == []

    # Salt-okunurluk: doğrulama depoyu ve HEAD'i değiştirmedi.
    assert _git(repo, "status", "--porcelain") == kirlilik_once
    assert _git(repo, "rev-parse", "HEAD") == pin.commit


# ─── Çözümleme sınırı: HEAD ÜST dizine yürümez (Task 1 devri, bulgu 2) ──────


def test_head_commit_does_not_walk_up_to_parent_repo(tmp_path: Path) -> None:
    """`repo_root` git deposu DEĞİLSE kapı düşer — kapsayan deponun HEAD'i değil.

    Kurgu bilinçli olarak en kötü hâli üretir: verilen kök bir git deposu
    değildir ama KAPSAYAN bir depo vardır ve pin tam da o kapsayan deponun
    commit'ine pinlidir. Çözümleme üst dizine yürürse üç dosya da eşleştiği
    için doğrulama SESSİZCE GEÇER — yabancı bir deponun HEAD'i pini onaylamış
    olur. Kapı, verilen köke sabitlenmiş olmalıdır.
    """
    ust_depo = _make_fake_repo(tmp_path)
    ust_head = _git(ust_depo, "rev-parse", "HEAD")

    # Kapsayan deponun İÇİNDE, kendisi depo OLMAYAN bir dizin.
    alt_kok = ust_depo / "alt-dizin"
    alt_kok.mkdir()
    for name in CONTRACT_FILES:
        (alt_kok / name).write_text(f"# {name}\n\nsözleşme gövdesi\n", encoding="utf-8")

    pin = ContractPin(
        commit=ust_head,
        files={name: _sha256(alt_kok / name) for name in CONTRACT_FILES},
    )

    reasons = verify_pin(pin, alt_kok)

    # Üç dosya eşleşiyor; tek düşmesi gereken kapı commit kapısı — ve sebep
    # kapsayan deponun sha'sını DEĞİL, çözümlenemedi işaretini taşımalı.
    assert reasons != [], "git deposu olmayan kök yabancı HEAD ile onaylandı"
    assert reasons == [f"commit uyuşmuyor: pin {ust_head}, depo {_HEAD_OKUNAMADI}"]


# ─── Manifest şekli (Task 1 devri, bulgu 3) ────────────────────────────────


def test_load_pin_rejects_manifest_naming_no_contract_file(tmp_path: Path) -> None:
    """Boş `files` manifesti REDDEDİLİR — sessizce commit-only kapıya düşmez.

    Ölçülen davranış (Task 1 review'ı): `files: {}` ile `verify_pin` hiçbir
    dosyaya bakmadan `[]` döndürüyordu; commit'i tutan her depo pinli
    sayılıyordu. Manifest hiçbir sözleşme dosyası adlandırmıyorsa bu bir
    doğrulama değil, doğrulama görüntüsüdür.
    """
    bos_manifest = tmp_path / "bos.pin.json"
    bos_manifest.write_text(
        json.dumps({"commit": "0" * 40, "files": {}}, indent=2), encoding="utf-8"
    )

    with pytest.raises(ContractDriftError) as hata:
        load_pin(bos_manifest)

    assert "hiçbir sözleşme dosyası" in str(hata.value)


# ─── GERÇEK pin doğrulaması (Task 2 Step 5) ────────────────────────────────


def test_real_pin_names_the_three_contract_files() -> None:
    """Gerçek manifest ÜÇ sözleşme dosyasını adıyla taşır — eksiği kabul yok."""
    pin = load_pin(GERCEK_PIN_PATH)

    assert set(pin.files) == set(CONTRACT_FILES)
    assert pin.commit != ""
    assert all(sha != "" for sha in pin.files.values())


def test_real_pin_verifies_clean() -> None:
    """Gerçek manifest gerçek dış depoya karşı GEÇER (Task 2 Step 5/6).

    Bu, sonraki tüm görevlerin girdi tabanıdır: pin bugünkü sözleşme
    sürümünü bağlar. Düşerse ya sözleşme sapmıştır ya pin bayatlamıştır —
    iki hâlde de resmî tur başlamamalıdır.
    """
    reasons = verify_pin(load_pin(GERCEK_PIN_PATH), GERCEK_ARASTIRMA_DEPOSU)

    assert reasons == [], reasons


def test_external_repo_gitignores_run_folder() -> None:
    """Dış deponun COMMIT EDİLMİŞ `.gitignore`'u `kosu/` satırını taşır (R1).

    Negatif invariant izlenmeyen koşu klasörünün pini DÜŞÜRMEDİĞİNİ söyler;
    onu düşürecek olan tek şey klasörün COMMIT EDİLMESİDİR (HEAD kayar →
    commit uyuşmazlığı). Bu satır o yolu kapatır.

    Ölçüm COMMIT EDİLMİŞ içeriğe bakar, çalışma ağacına değil: invariant
    "bu depoya koşu klasörü commit edilemez"dir ve onu kapatan şey de
    commit'lenmiş satırdır. Çalışma ağacını okumak, yalnız yerelde duran
    (henüz commit edilmemiş) bir satırı da geçerli sayardı.
    """
    satirlar = subprocess.run(
        ["git", "-C", str(GERCEK_ARASTIRMA_DEPOSU), "show", "HEAD:.gitignore"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    assert "kosu/" in satirlar, satirlar


# ─── H1: bozuk manifest fail-closed'ı bozamaz (checkpoint bulgusu) ──────────


def _plain_dir_case(tmp_path: Path) -> tuple[str, dict[str, str], Path]:
    """(1) `commit` = HEAD-okunamadı işareti · kök git deposu DEĞİL.

    İşaret "hiçbir gerçek sha'ya eşit olamaz" diye seçilmişti; ama manifestte
    GÖRÜNMESİ engellenmemişti. Görününce `_head_commit`'in her başarısızlık
    yolu (git yok · depo değil · bozuk depo) uyuşmazlık değil EŞLEŞME olur.
    """
    kok = tmp_path / "depo-degil"
    kok.mkdir()
    for name in CONTRACT_FILES:
        (kok / name).write_text(f"# {name}\n", encoding="utf-8")
    files = {name: _sha256(kok / name) for name in CONTRACT_FILES}
    return _HEAD_OKUNAMADI, files, kok


def _absolute_key_case(tmp_path: Path) -> tuple[str, dict[str, str], Path]:
    """(2) Manifest anahtarı MUTLAK yol → `repo_root` tamamen devre dışı.

    `Path(kok) / "/mutlak"` == `Path("/mutlak")` — pathlib'de mutlak sağ
    taraf tabanı EZER. Manifest böylece diskin herhangi bir yerindeki bir
    dosyayı "sözleşme dosyası" diye hash'letebilir.
    """
    repo = _make_fake_repo(tmp_path)
    disarida = tmp_path / "disarida.md"
    disarida.write_text("depo DIŞINDAKİ dosya\n", encoding="utf-8")
    files = {name: _sha256(repo / name) for name in CONTRACT_FILES}
    files[str(disarida)] = _sha256(disarida)
    return _git(repo, "rev-parse", "HEAD"), files, repo


def _traversal_key_case(tmp_path: Path) -> tuple[str, dict[str, str], Path]:
    """(3) Manifest anahtarı `..` ile depo sınırının DIŞINA çıkar."""
    repo = _make_fake_repo(tmp_path)
    disarida = tmp_path / "disarida.md"
    disarida.write_text("depo DIŞINDAKİ dosya\n", encoding="utf-8")
    files = {name: _sha256(repo / name) for name in CONTRACT_FILES}
    files["../disarida.md"] = _sha256(disarida)
    return _git(repo, "rev-parse", "HEAD"), files, repo


@pytest.mark.parametrize(
    "kurulum, aciklama",
    [
        (_plain_dir_case, "HEAD-okunamadı işareti commit olarak"),
        (_absolute_key_case, "mutlak manifest anahtarı"),
        (_traversal_key_case, "`..` ile depo dışına çıkan anahtar"),
    ],
)
def test_malformed_pin_can_never_verify_clean(
    tmp_path: Path, kurulum, aciklama: str
) -> None:
    """Bozuk manifest TEMİZ doğrulama üretemez — üç delik de kapalı.

    Fail-closed'ın önermesi şudur: sözleşme sapmışsa resmî koşu BAŞLAMAZ.
    Aşağıdaki üç girdi, düzeltmeden önce koşuyu BAŞLATIYORDU: `verify_pin`
    boş liste, yani "pinli ve temiz" döndürüyordu.

    Kapanış YÜKLEME katmanındadır: böyle bir pin nesnesi hiç KURULAMAZ.
    Bu, arayüz eki R14'ü korur — `verify_pin`'in kapı kümesi DÖRT kalır,
    beşinci kapı eklenmez; bozuk girdi kapıya hiç ulaşmaz.
    """
    commit, files, kok = kurulum(tmp_path)

    with pytest.raises(ContractDriftError):
        pin = ContractPin(commit=commit, files=files)
        # Düzeltmeden ÖNCE akış buraya düşer: nesne kurulur ve doğrulama
        # sessizce geçer. Assert o hâli görünür kılar (RED kanıtı).
        assert verify_pin(pin, kok) != [], f"{aciklama}: bozuk manifest TEMİZ doğrulandı"


def test_pin_rejects_head_sentinel_as_commit() -> None:
    """İşaret değeri manifeste YAZILAMAZ — sebep adıyla söylenir."""
    with pytest.raises(ContractDriftError) as hata:
        ContractPin(commit=_HEAD_OKUNAMADI, files={"_SABLON.md": "a" * 64})

    assert "işaret" in str(hata.value)


@pytest.mark.parametrize(
    "bozuk_anahtar",
    ["/etc/passwd", "../disarida.md", "alt/../../disarida.md", "", "C:/x.md"],
)
def test_pin_rejects_file_key_escaping_repo_root(bozuk_anahtar: str) -> None:
    """Anahtar depo kökünün İÇİNDE kalmalı: mutlak yok, `..` yok, boş yok."""
    with pytest.raises(ContractDriftError) as hata:
        ContractPin(commit="a" * 40, files={bozuk_anahtar: "b" * 64})

    assert "depo kökü" in str(hata.value)


@pytest.mark.parametrize(
    "bozuk_commit", ["", "xyz", "a" * 39, "a" * 41, "A" * 40, "  " + "a" * 38]
)
def test_pin_rejects_malformed_commit(bozuk_commit: str) -> None:
    """`commit` gerçek bir git nesne kimliği biçiminde olmalı."""
    with pytest.raises(ContractDriftError) as hata:
        ContractPin(commit=bozuk_commit, files={"_SABLON.md": "c" * 64})

    assert "commit" in str(hata.value)


@pytest.mark.parametrize("bozuk_hash", ["", "abc", "d" * 63, "d" * 65, "D" * 64])
def test_pin_rejects_malformed_hash(bozuk_hash: str) -> None:
    """Her değer 64 haneli KÜÇÜK harf onaltılık sha256 olmalı."""
    with pytest.raises(ContractDriftError) as hata:
        ContractPin(commit="e" * 40, files={"_SABLON.md": bozuk_hash})

    assert "sha256" in str(hata.value)
