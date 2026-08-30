"""Dış araştırma deposu sözleşme pin'i — okuma + fail-closed doğrulama (Task 1).

Pin manifesti (`shared/contracts/research-contracts.pin.json`) iki şey taşır:
dış deponun **commit sha**'sı ve pinlenen sözleşme dosyalarının **sha256**'sı.
Resmî koşuyu başlatan her CLI alt komutu ilk iş olarak `require_pin` çağırır;
sözleşme sapmışsa koşu BAŞLAMAZ.

Kapı kümesi TAM OLARAK dörttür (plan 423-426):
  1. depo dizini yok
  2. pinlenen dosya yok
  3. hash uyuşmuyor
  4. commit uyuşmuyor
"Uyarıp devam" dalı YOKTUR ve bu küme GENİŞLETİLMEZ (arayüz eki R14).

Manifestin ŞEKLİ kapı değildir, okuma koşuludur: `load_pin` hiçbir sözleşme
dosyası adlandırmayan manifesti reddeder. Kapı sayısı yine dörttür — boş bir
manifest zaten doğrulanacak bir şey vermez.

NEGATİF invariant (arayüz eki R1 · R14): **kirli çalışma ağacı tek başına pini
DÜŞÜRMEZ.** Manifestte adı geçmeyen hiçbir dosya veya dizin — izlenmeyen
`kosu/<run_id>/` klasörleri dâhil — uyuşmazlık üretmez. Bu modül `git status`
ya da `git diff` çağırmaz; dış depoda hiçbir şey değiştirmez (salt-okunur).
Pinlenen dosyaların baytı değişirse kapı zaten hash ile düşer; bu kirlilik
değil **içerik drift'idir** ve iki hâl karıştırılmaz.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

# HEAD çözülemediğinde (depo git deposu değil, git yok, bozuk depo) kullanılan
# işaret. Pin'deki commit sha'sına asla eşit olamaz → commit kapısı düşer.
_HEAD_OKUNAMADI = "<HEAD okunamadı>"


class ContractDriftError(RuntimeError):
    """Dış sözleşme deposu pinden sapmış — resmî koşu başlamaz."""


@dataclass(frozen=True)
class ContractPin:
    """Pin manifestinin bellekteki hâli.

    `files`: depo köküne göreli yol → beklenen sha256 (onaltılık).
    """

    commit: str
    files: Mapping[str, str]

    def __post_init__(self) -> None:
        # Donmuş sarmalayıcının içinde değiştirilebilir sözlük bırakılmaz.
        object.__setattr__(self, "files", MappingProxyType(dict(self.files)))


def load_pin(pin_path: Path) -> ContractPin:
    """Manifesti diskten okur. Bozuk/eksik manifest hata fırlatır (fail-closed).

    Manifest en az bir sözleşme dosyası adlandırmak ZORUNDADIR. Boş `files`
    ile `verify_pin` hiçbir dosyaya bakmadan geçerdi: commit'i tutan her depo
    pinli sayılırdı. Bu bir doğrulama değil, doğrulama görüntüsüdür — ve
    kapıyı genişletmeden burada, manifest okunurken kapanır (arayüz eki R14:
    `verify_pin`'in DÖRT kapılık kümesi değişmez).
    """
    data = json.loads(Path(pin_path).read_text(encoding="utf-8"))
    files = data["files"]
    if not isinstance(files, dict) or not files:
        raise ContractDriftError(
            f"pin manifesti hiçbir sözleşme dosyası adlandırmıyor: {pin_path}"
        )
    return ContractPin(commit=data["commit"], files=files)


def verify_pin(pin: ContractPin, repo_root: Path) -> list[str]:
    """Pin'i dış depoya karşı doğrular.

    Boş liste = geçti. Dolu liste = uyuşmazlık sebepleri (fail-closed).
    """
    repo_root = Path(repo_root)
    if not repo_root.is_dir():
        return [f"depo dizini yok: {repo_root}"]

    reasons: list[str] = []
    for rel_path, beklenen_sha in sorted(pin.files.items()):
        dosya = repo_root / rel_path
        if not dosya.is_file():
            reasons.append(f"sözleşme dosyası yok: {dosya}")
            continue
        bulunan_sha = hashlib.sha256(dosya.read_bytes()).hexdigest()
        if bulunan_sha != beklenen_sha:
            reasons.append(
                f"hash uyuşmuyor: {rel_path} (pin {beklenen_sha}, disk {bulunan_sha})"
            )

    head = _head_commit(repo_root)
    if head != pin.commit:
        reasons.append(f"commit uyuşmuyor: pin {pin.commit}, depo {head}")

    return reasons


def require_pin(pin_path: Path, repo_root: Path) -> None:
    """Uyuşmazlıkta `ContractDriftError` fırlatır; uyumda sessizce döner."""
    reasons = verify_pin(load_pin(pin_path), repo_root)
    if reasons:
        raise ContractDriftError(
            "Dış sözleşme deposu pinden sapmış (fail-closed): " + " · ".join(reasons)
        )


def _head_commit(repo_root: Path) -> str:
    """Deponun HEAD commit sha'sı. SALT-OKUNUR: yalnız `git rev-parse HEAD`.

    Çözümleme VERİLEN köke sabitlenir. `git rev-parse` kendi başına dizin
    ağacında YUKARI yürür: git deposu olmayan bir kök verilirse KAPSAYAN
    deponun HEAD'ini rc=0 ile döndürür (Task 1 review'ında ölçüldü). Bu, pin'i
    yabancı bir deponun commit'iyle onaylatabilirdi. `.git` girdisi (dizin ya
    da worktree'deki dosya) kökün kendisinde yoksa yürüyüş hiç başlamaz,
    sentinel döner ve commit kapısı düşer.
    """
    if not (Path(repo_root) / ".git").exists():
        return _HEAD_OKUNAMADI
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return _HEAD_OKUNAMADI
    if result.returncode != 0:
        return _HEAD_OKUNAMADI
    return result.stdout.strip()
