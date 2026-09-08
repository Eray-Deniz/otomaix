"""Dış araştırma deposu sözleşme pin'i — okuma + fail-closed doğrulama (Task 1).

Pin manifesti (`shared/contracts/research-contracts.pin.json`) iki şey taşır:
dış deponun **commit sha**'sı ve pinlenen sözleşme dosyalarının **sha256**'sı.
Resmî koşuyu başlatan her CLI alt komutu ilk iş olarak `require_pin` çağırır;
sözleşme sapmışsa koşu BAŞLAMAZ. Pinlenmiş bir dosyanın İÇERİĞİNİ kullanacak
çağıran `require_pinned_text` kullanır: doğrulanan baytla kullanılan bayt AYNI
okumadan gelir, ikinci bir okuma penceresi açılmaz.

Kapı kümesi TAM OLARAK dörttür (plan 423-426):
  1. depo dizini yok
  2. pinlenen dosya yok
  3. hash uyuşmuyor
  4. commit uyuşmuyor
"Uyarıp devam" dalı YOKTUR ve bu küme GENİŞLETİLMEZ (arayüz eki R14).

Manifestin ŞEKLİ kapı değildir, okuma koşuludur. Kapı sayısı yine dörttür;
bozuk girdi kapıya HİÇ ULAŞMAZ, çünkü ondan bir `ContractPin` kurulamaz.
Doğrulama iki katmana ayrılmıştır:

* `ContractPin.__post_init__` — pin'in KENDİ yapısal değişmezleri (bir depo
  kökü bilmeden karara bağlanabilen her şey): `commit` biçimi, dosya
  anahtarlarının depo kökü içinde kalan göreli yollar olması, sha256
  değerlerinin biçimi, kümenin boş olmaması. Buraya konmasının nedeni,
  `load_pin`'i atlayıp doğrudan `ContractPin(...)` kuran çağrıcıların da
  kapsanmasıdır — bozuk pin TEMSİL EDİLEMEZ hâle gelir.
* `load_pin` — manifest DOSYASINA özgü olan: okunabilir JSON mu, `files`
  bir nesne mi ve en az bir sözleşme dosyası adlandırıyor mu (hata mesajı
  manifest yolunu da söyleyebilsin diye burada durur).

Neden `verify_pin` DEĞİL: arayüz eki R14 kapı kümesini genişletmeyi
yasaklar. Anahtarın depo kökü içinde kalması `repo_root`'tan bağımsız bir
manifest özelliğidir (mutlak yol yok · `..` yok · kanonik göreli yazım), bu
yüzden `repo_root` bilinmeden zorlanabilir ve `verify_pin`'e yalnız zaten
güvenli anahtarlar ulaşır. Kapsam sınırı dürüstçe: depo İÇİNDEKİ bir
sembolik bağın dışarı işaret etmesi bu katmanda ELE ALINMAZ.

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
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping

# HEAD çözülemediğinde (depo git deposu değil, git yok, bozuk depo) kullanılan
# işaret. Gerçek bir sha'ya benzemez, bu yüzden commit kapısı düşer — AMA bu
# tek başına yetmiyordu: işaretin MANİFESTE yazılması engellenmedikçe her
# okuma-başarısızlığı eşleşmeye dönüyordu. `_validate_commit` o yolu kapatır.
_HEAD_OKUNAMADI = "<HEAD okunamadı>"

# Git nesne kimliği: sha1 (40) ya da sha256 (64), küçük harf onaltılık.
_GIT_OBJECT_ID_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


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
        files = dict(self.files)
        _validate_commit(self.commit)
        if not files:
            raise ContractDriftError(
                "pin hiçbir sözleşme dosyası adlandırmıyor — boş küme "
                "doğrulamayı sessizce commit-only kapıya düşürürdü"
            )
        for rel_path, sha in files.items():
            _validate_rel_path(rel_path)
            _validate_sha256(rel_path, sha)
        # Donmuş sarmalayıcının içinde değiştirilebilir sözlük bırakılmaz.
        object.__setattr__(self, "files", MappingProxyType(files))


def _validate_commit(commit: Any) -> None:
    """`commit` gerçek bir git nesne kimliği olmalı — ve İŞARET olmamalı.

    `_HEAD_OKUNAMADI` "hiçbir gerçek sha'ya eşit olamaz" diye seçilmişti ve o
    akıl yürütme doğrudur; eksik olan, işaretin MANİFESTTE görünmesinin
    engellenmemesiydi. Göründüğü anda `_head_commit`'in her başarısızlık yolu
    (git yok · dizin depo değil · bozuk depo) uyuşmazlık değil EŞLEŞME üretir
    ve fail-closed kapı fail-open'a döner. İşaret bu yüzden ADIYLA reddedilir
    (biçim kontrolü zaten yakalar; bu satır niyeti sabitler ve işaretin ileride
    değişmesine karşı da dayanır).
    """
    if not isinstance(commit, str):
        raise ContractDriftError(
            f"pin commit değeri metin değil: {type(commit).__name__}"
        )
    if commit == _HEAD_OKUNAMADI:
        raise ContractDriftError(
            f"pin commit değeri HEAD-okunamadı işareti ({_HEAD_OKUNAMADI!r}) — "
            "bu değer manifeste yazılamaz: yazılırsa git'in okunamadığı her "
            "durum uyuşmazlık yerine EŞLEŞME sayılırdı"
        )
    if not _GIT_OBJECT_ID_RE.fullmatch(commit):
        raise ContractDriftError(
            f"pin commit değeri git nesne kimliği biçiminde değil: {commit!r} "
            "(40 ya da 64 haneli küçük harf onaltılık beklenir)"
        )


def _validate_rel_path(rel_path: Any) -> None:
    """Anahtar, depo kökünün İÇİNDE kalan kanonik göreli bir yol olmalı.

    Eksik olan, `repo_root / rel_path` birleşimine hiç güvenlik sorulmamasıydı:
    pathlib'de MUTLAK bir sağ taraf tabanı tamamen EZER (`Path("/a") / "/b"`
    → `/b`), `..` ise sınırın dışına yürür. İkisi de manifeste diskin herhangi
    bir yerindeki dosyayı "sözleşme dosyası" diye hash'letme yetkisi verirdi.
    """
    if not isinstance(rel_path, str):
        raise ContractDriftError(
            f"pin dosya anahtarı metin değil: {type(rel_path).__name__}"
        )
    kusur: str | None = None
    if "\\" in rel_path or ":" in rel_path:
        kusur = "sürücü harfi ya da ters bölü içeriyor"
    else:
        posix = PurePosixPath(rel_path)
        parcalar = posix.parts
        if posix.is_absolute():
            kusur = "mutlak yol"
        elif not parcalar:
            kusur = "boş"
        elif any(parca in ("..", ".") for parca in parcalar):
            kusur = "`..`/`.` parçası içeriyor"
        elif str(posix) != rel_path:
            kusur = "kanonik göreli yazımda değil"
    if kusur is not None:
        raise ContractDriftError(
            f"pin dosya anahtarı depo kökü içinde kalmıyor ({kusur}): "
            f"{rel_path!r}"
        )


def _validate_sha256(rel_path: str, sha: Any) -> None:
    """Beklenen değer 64 haneli küçük harf onaltılık sha256 olmalı."""
    if not isinstance(sha, str) or not _SHA256_RE.fullmatch(sha):
        raise ContractDriftError(
            f"pin sha256 değeri biçimsiz: {rel_path!r} -> {sha!r} "
            "(64 haneli küçük harf onaltılık beklenir)"
        )


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


def verify_pin(
    pin: ContractPin,
    repo_root: Path,
    *,
    snapshots: Mapping[str, bytes | None] | None = None,
) -> list[str]:
    """Pin'i dış depoya karşı doğrular.

    Boş liste = geçti. Dolu liste = uyuşmazlık sebepleri (fail-closed).

    `snapshots` KAPI EKLEMEZ (arayüz eki R14: kapı kümesi TAM OLARAK dört
    kalır) — yalnız kapının **hangi baytları** ölçtüğünü değiştirir. Çağıran
    bir sözleşme dosyasını zaten okuduysa o anlık görüntüyü buraya verir ve
    hash kapısı diskten İKİNCİ bir okuma yapmadan aynı baytları ölçer. Gerekçe
    ölçüldü: doğrulanan bayt ile kullanılan bayt farklı iki okumadan gelirse
    aralarındaki pencerede dosya değişebilir ve pinlenmemiş içerik
    doğrulanmış sayılırdı. Anlık görüntü `None` ise dosya okunamamıştır ve
    ikinci kapı ("sözleşme dosyası yok") düşer.
    """
    repo_root = Path(repo_root)
    if not repo_root.is_dir():
        return [f"depo dizini yok: {repo_root}"]

    goruntuler = dict(snapshots or {})
    reasons: list[str] = []
    for rel_path, beklenen_sha in sorted(pin.files.items()):
        dosya = repo_root / rel_path
        if rel_path in goruntuler:
            ham = goruntuler[rel_path]
            if ham is None:
                reasons.append(f"sözleşme dosyası yok: {dosya}")
                continue
        else:
            if not dosya.is_file():
                reasons.append(f"sözleşme dosyası yok: {dosya}")
                continue
            ham = dosya.read_bytes()
        bulunan_sha = hashlib.sha256(ham).hexdigest()
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
    _require(verify_pin(load_pin(pin_path), repo_root))


def require_pinned_text(
    pin_path: Path, repo_root: Path, rel_path: str, *, encoding: str = "utf-8"
) -> str:
    """Pin kapısını koşturur VE **doğrulanan baytların kendisini** döndürür.

    `require_pin` + ayrı bir `read_text` deseni iki BAĞIMSIZ okuma üretir:
    kapı bir anlık görüntüyü ölçer, tüketici başka bir anlık görüntüyü
    kullanır. İkisi arasındaki pencerede dosya değişirse pinlenmemiş baytlar
    doğrulanmış sayılır — ve tüketici baytları kendi içinde tutarlı olduğu
    için hiçbir bayt-eşitliği kontrolü bunu göstermez. "Önce kontrol, sonra
    ikinci okuma" o pencereyi küçültür, KAPATMAZ; bu yüzden okuma BİR KEZDİR
    ve doğrulanan anlık görüntü çağırana geri verilir.

    Kapı kümesi büyümez (arayüz eki R14): dosya `verify_pin`'in DÖRT kapısıyla
    aynı ölçümden geçer, yalnız hash'i çağıranın elindeki anlık görüntüden
    hesaplanır. `rel_path`'in pinde adlandırılmış olması bir kapı değil çağrı
    ön koşuludur — pinlenmemiş bir dosyanın baytları hiçbir kapıdan geçemez,
    o yüzden bu fonksiyon onu hiç döndürmez.
    """
    pin = load_pin(pin_path)
    rel = str(rel_path)
    if rel not in pin.files:
        raise ContractDriftError(
            f"istenen sözleşme dosyası pinde adlandırılmamış: {rel!r} — "
            f"pinlenen küme {sorted(pin.files)}; pinlenmemiş bayt paketlenemez"
        )
    try:
        ham: bytes | None = (Path(repo_root) / rel).read_bytes()
    except OSError:
        ham = None
    _require(verify_pin(pin, repo_root, snapshots={rel: ham}))
    if ham is None:
        # Ulaşılmaz olmalı (ikinci kapı düşerdi) — ama "olmalı" bir kapı
        # değildir; okunamayan bayt hiçbir koşulda geri verilmez.
        raise ContractDriftError(f"sözleşme dosyası okunamadı: {rel!r}")
    return ham.decode(encoding)


def _require(reasons: list[str]) -> None:
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
