"""Politika motoru — §9.2 zorunlu kontrol kümesi (Plan 2 Task 12).

**İSKELET — davranış YOK.** Yüzey burada tanımlanır ki her testin kendi
kırmızısı ayrı ölçülebilsin; tek bir `ImportError` kırmızı sayılmaz.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from app.services.sector_pipeline.auditors import ValidatedAuditPair
from app.services.sector_pipeline.brief_doctor import RoundGate
from app.services.sector_pipeline.engine_contract import BulguIzi, UygulanmayanKarar
from app.services.sector_pipeline.synthesis import SynthesisResult


class EngineInputError(ValueError):
    """Motor girdisi kapıdan geçmedi — kontrol KOŞMAZ (fail-closed)."""


@dataclass(frozen=True)
class GateResults:
    katman1_passed: bool
    tek_aktif_ihlali: bool


@dataclass(frozen=True)
class EngineInputs:
    sentez: SynthesisResult
    aktif_paket: Mapping | None
    aktif_schema_version: int | None
    aktif_birimler: Mapping[str, Mapping]
    mevcut_birim_sayisi: int
    ilk_kosu: bool
    son_turlarin_cikarmalari: tuple[Mapping, ...]
    denetci_envanterleri: ValidatedAuditPair
    mekanik_eleme: RoundGate
    takvim_anahtarlari: frozenset[str]
    otomatik_kapilar: GateResults


@dataclass(frozen=True)
class CheckOutput:
    bulgular: tuple[BulguIzi, ...] = ()
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...] = ()
    notlar: tuple[Mapping, ...] = ()
    olcumler: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class CheckOutcome:
    bulgular: tuple[BulguIzi, ...]
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...]
    notlar: tuple[Mapping, ...]
    olcumler: Mapping[str, Any]


@dataclass(frozen=True)
class EngineCheck:
    ad: str
    aciklama: str
    calistir: Callable[[EngineInputs], CheckOutput]


CHECKS: tuple[EngineCheck, ...] = ()


def run_checks(inputs: EngineInputs) -> CheckOutcome:
    raise NotImplementedError("Task 12 Step 3")
