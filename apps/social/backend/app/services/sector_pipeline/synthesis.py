"""Sentez koşumu + çıktı doğrulayıcı (Plan 2 Task 11) — İSKELET.

Bu dosya şu an yalnız YÜZEYİ taşır: adlar tanımlıdır, davranış YOKTUR. Amaç
her testin KENDİ kırmızısını ayrı ölçebilmesidir; modül hiç yokken alınan tek
`ImportError` kırmızı SAYILMAZ (yürütme sözleşmesi, kural 9).

Kanonik sıra BAĞLAYICIDIR: sentez → motor → draft. Bu modül `sector_packages`
tablosuna hiçbir şey YAZMAZ.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from app.services.sector_pipeline.auditors import AuditRound, Runner

SENTEZ_ASAMASI = "sentez"

SENTEZ_BOLUM_ANAHTARLARI: tuple[str, ...] = ()
"""İSKELET — sözleşmeden ÖLÇÜLECEK; bugün boş, uydurulmadı."""

K74_ACIK_SORU_TAVANI = 0
K75_DENETCI_ONERI_TAVANI = 0

GOREV_DOSYASI = "hakem-sentez-gorevi.md"
GOREV_DOSYA_ADI = "00-SENTEZ-GOREVI.md"


class SynthesisFailed(RuntimeError):
    """Sentez terminal arızası — yarım sonuç motora ULAŞMAZ."""


@dataclass(frozen=True)
class SynthesisResult:
    """Sentezin dört çıktısı + taşma işareti (İSKELET)."""

    aday_json: Mapping
    karar_gunlugu: tuple[Mapping, ...]
    acik_sorular: tuple[str, ...]
    onay_ozeti: str
    tasma: bool


def validate(result: SynthesisResult) -> list[str]:
    raise NotImplementedError("Task 11 Step 3")


async def run(
    db,
    round: AuditRound,
    *,
    run_id: str,
    active_package: Mapping | None,
    removed_history: Sequence[Mapping],
    holiday_keys: set[str],
    runner: Runner,
    dest: Path,
) -> SynthesisResult:
    raise NotImplementedError("Task 11 Step 3")
