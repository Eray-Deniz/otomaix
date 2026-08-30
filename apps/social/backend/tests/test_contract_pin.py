"""Dış sözleşme pin'inin fail-closed doğrulayıcısı (plan Task 1).

Kapı kümesi TAM OLARAK dörttür (plan 423-426): dosya yok · hash uyuşmuyor ·
commit uyuşmuyor · depo dizini yok. Arayüz eki R1/R14 bunun üstüne bir NEGATİF
invariant bağlar: **kirli çalışma ağacı tek başına pini DÜŞÜRMEZ** — manifestte
adı geçmeyen hiçbir dosya/dizin (izlenmeyen `kosu/<run_id>/` dâhil) uyuşmazlık
üretmez ve doğrulama salt-okunurdur.

Fixture disiplini: gerçek araştırma deposuna (`/root/otomaix-sosyal-medya-
arastirmasi`) DOKUNULMAZ. Her test `tmp_path` altında kendi sahte üç dosyalı
git deposunu kurar; ölçülen şey gerçek dosya sistemi ve gerçek `git` HEAD'idir,
sahte nesnenin davranışı değil.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from app.services.sector_pipeline.contracts import (
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
    """Depo dizini hiç yoksa RED — 'depo yok = sorun yok' dalı YOKTUR."""
    repo = _make_fake_repo(tmp_path)
    pin = _pin_for(repo)
    yok = tmp_path / "olmayan-depo"

    reasons = verify_pin(pin, yok)

    assert reasons != []
    assert any(str(yok) in reason for reason in reasons)


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
