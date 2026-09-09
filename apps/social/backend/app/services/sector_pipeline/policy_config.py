"""Politika motorunun AYAR sözleşmesi (Plan 2 Task 13).

**Ayar motorun girdisi DEĞİLDİR, ikinci parametresidir.** `PolicyConfig`
`EngineInputs`'a GİRMEZ (arayüz eki R5): `decide(inputs, config)` onu ayrı alır
ve tek kanonik yeri burasıdır.

**Üç bariyerin eşiği varsayılan olarak `None`'dır ve bu bilinçlidir (İlke 9).**
Ölçülmemiş bir sayı kapı yapılmaz: eşik `None` iken bariyer HİÇBİR ŞEYİ
bloklamaz, yalnız oranı `barrier_report`'a yazar. Eşiği dolduran, ölçümü yapan
kişidir — kod değil.
"""

from __future__ import annotations

from dataclasses import dataclass, fields as dataclass_fields
from typing import Any, Mapping

from app.services.sector_pipeline import identity

ABS_LIMIT_ANAHTARLARI: tuple[str, ...] = ("degisim", "ekleme", "kararsizlik")
"""`abs_limits`'in KAPALI anahtar kümesi — üç bariyerin mutlak karşılığı.

İlk paket koşusunda payda (mevcut birim sayısı) sıfırdır ve oran hesaplanamaz;
o koşuda kullanılabilecek TEK kapı mutlak limittir. Anahtar kümesi kapalıdır ki
uydurulmuş bir anahtar sessizce YOK SAYILMASIN.
"""

_ORAN_ALANLARI: tuple[str, ...] = (
    "max_change_ratio",
    "max_add_ratio",
    "max_undecided_ratio",
)


@dataclass(frozen=True)
class PolicyConfig:
    """Motorun ayar yüzeyi — alan kümesi KAPALI, eşikler varsayılan olarak pasif."""

    max_change_ratio: float | None = None
    max_add_ratio: float | None = None
    max_undecided_ratio: float | None = None
    abs_limits: Mapping[str, int] | None = None
    block_on_legislation: bool = False

    def __post_init__(self) -> None:
        # F4 emsali (checkpoint 9): anotasyon çalışma zamanı kapısı DEĞİLDİR.
        # Serileştirmeden gelen `"false"` DİZESİ doğruluk-değeriyle DOĞRUdur ve
        # `block_on_legislation` ayarını sessizce AÇARDI.
        if type(self.block_on_legislation) is not bool:
            raise TypeError(
                "block_on_legislation GERÇEKTEN bool olmalı "
                f"({type(self.block_on_legislation).__name__} verildi) — "
                "doğru-görünen değer ayar kanıtı DEĞİLDİR"
            )
        for _alan in _ORAN_ALANLARI:
            _deger = getattr(self, _alan)
            if _deger is None:
                continue
            # `bool` `int`'in alt sınıfıdır: `max_change_ratio=True` bir oran
            # DEĞİLDİR ve sessizce 1.0 gibi davranırdı.
            if type(_deger) not in (int, float):
                raise TypeError(
                    f"{_alan} oran olmalı ({type(_deger).__name__} verildi)"
                )
            if _deger < 0:
                raise ValueError(f"{_alan} negatif olamaz: {_deger!r}")
        if self.abs_limits is not None:
            bilinmeyen = sorted(set(self.abs_limits) - set(ABS_LIMIT_ANAHTARLARI))
            if bilinmeyen:
                raise ValueError(
                    f"abs_limits kapalı anahtar kümesinin dışında: {bilinmeyen} — "
                    f"kabul edilenler: {list(ABS_LIMIT_ANAHTARLARI)}"
                )
            for _ad, _limit in self.abs_limits.items():
                if type(_limit) is not int or _limit < 0:
                    raise ValueError(
                        f"abs_limits[{_ad!r}] negatif olmayan tamsayı olmalı: {_limit!r}"
                    )
        object.__setattr__(self, "abs_limits", identity.donmus(self.abs_limits))


def config_sha(config: PolicyConfig) -> str:
    """`PolicyConfig`'in kanonik hash'i (K-97).

    `identity.canonical_sha`'yı ÇAĞIRIR (K-92) — ikinci bir hash kuralı
    yazılmaz. Alan listesi dataclass'tan TÜRETİLİR: sözleşmeye alan eklenip
    hash'e yansımaması sessiz bir sürüm çakışması olurdu.
    """
    yuk: dict[str, Any] = {
        alan.name: getattr(config, alan.name) for alan in dataclass_fields(config)
    }
    return identity.canonical_sha(yuk)
