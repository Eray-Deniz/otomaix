#!/usr/bin/env python3
"""Marka → kök sektör tam sweep'i (salt-okunur, deterministik, re-runnable).

Spec §5.3 / plan Task 5. İKİ iddiası var ve ikisi de TAM kümede ölçülür:

1. **Kök bağlanma.** Her markanın `sector_id`'si bir KÖK sektör satırına
   (`parent_sector_id IS NULL`) bağlıdır. Alt sektör satırları yalnız paket
   katmanının adresidir; markanın kendi sektörü asla oraya kaymamalıdır (R-01).
2. **Eşleme değişmezliği.** Mevcut her markanın `(brand_id, sector_id)` çifti
   ÖNCE ve SONRA birebir AYNIdır — kökten köke kayma da ihlaldir.

İkinci iddia birincisinden TÜRETİLEMEZ: A kökünden B köküne kayan bir marka
"kök bağlı" kalmaya devam eder. Bu yüzden rapor toplam sayı değil TAM EŞLEME
LİSTESİ taşır ve `--baseline` ile önceki bir rapora karşı çift çift
karşılaştırılır. (Codex checkpoint 5, yüksek bulgu: ilk sürüm yalnız toplam
sayı basıyordu ve kökten köke kaymayı `differences: 0` ile geçiriyordu.)

Kullanım deseni — Plan 2'nin satır-açma adımı:

    sector_sweep.py --database-url ... > before.txt
    <satır açma adımı>
    sector_sweep.py --database-url ... --baseline before.txt

`--baseline` karşılaştırması YALNIZ eşlemeye bakar; taksonomi sayıları
(`sub_sector_rows`) satır açılınca DOĞAL olarak değişir ve karşılaştırmaya
girmez. İki ham raporu bayt olarak kıyaslamak bu yüzden yanlış alarm verirdi —
kıyas aracın kendi içindedir, operatörün gözünde değil.

Sözleşme:

* **Salt-okunur.** Bağlantı `BEGIN TRANSACTION READ ONLY` içinde açılır: yetkili
  bir bağlantı dizesiyle koşulsa bile yazma girişimi veritabanı tarafından
  reddedilir. Testte ayrıca salt-okunur ROL ile koşulur.
* **Deterministik.** Rapor zaman damgası, süre, rastgele sıra içermez; satırlar
  marka kimliğine göre sıralıdır. Aynı veri → bayt-aynı çıktı.
* **Ortamdan miras almaz.** Bağlantı dizesi `--database-url` ile AÇIKÇA verilir;
  `DATABASE_URL` ortam değişkeni okunmaz (yanlış veritabanına koşma riski yok).
* **Çıkış kodu.** 0 = temiz. 1 = kök bağlanma ihlali VEYA eşleme kayması
  (remapped/removed). Yeni marka (`added`) raporlanır ama BAŞARISIZLIK SAYILMAZ:
  marka açmak olağan işletimdir, ihlal değildir.

Kullanım:

    python scripts/sector_sweep.py --database-url postgresql://... --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import asyncpg

# Rapor biçimi değişirse artar — iki koşumun karşılaştırılabilirliği buna bağlı.
# v2: rapor tam eşleme listesi taşır (v1 yalnız toplam sayı taşıyordu).
REPORT_SCHEMA_VERSION = 2

# Eşleme bloğunun başlığı — `--baseline` ayrıştırıcısı bu işareti arar.
MAPPING_HEADER = "--- mapping ---"
COMPARISON_HEADER = "--- baseline comparison ---"

# Eşlemesi olmayan marka için basılan yer tutucu. Boş dize basmak satırı
# ayrıştırılamaz yapardı.
NO_SECTOR = "-"

_SWEEP_SQL = """
SELECT
    b.id::text        AS brand_id,
    b.sector_id::text AS sector_id,
    s.id IS NOT NULL  AS sector_exists,
    s.parent_sector_id::text AS parent_sector_id
FROM social.brands AS b
LEFT JOIN social.sectors AS s ON s.id = b.sector_id
ORDER BY b.id
"""

_SUB_SECTOR_COUNT_SQL = """
SELECT count(*) FROM social.sectors WHERE parent_sector_id IS NOT NULL
"""


def _difference_reason(row: asyncpg.Record) -> str | None:
    """Markanın KÖK BAĞLANMASINI bozan sebep — yoksa None."""
    if row["sector_id"] is None:
        return "null_sector"
    if not row["sector_exists"]:
        # FK bunu engelliyor; yine de sessiz geçilmez.
        return "missing_sector"
    if row["parent_sector_id"] is not None:
        return "sub_sector"
    return None


def parse_mapping(report: str) -> dict[str, str]:
    """Bir raporun eşleme bloğunu `{brand_id: sector_id}` olarak okur.

    Yalnız `--- mapping ---` ile sonraki blok başlığı arasını okur; özet
    satırları ve karşılaştırma bloğu ayrıştırmaya GİRMEZ.
    """
    mapping: dict[str, str] = {}
    inside = False
    for line in report.splitlines():
        if line == MAPPING_HEADER:
            inside = True
            continue
        if not inside:
            continue
        if line.startswith("--- "):
            break
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"eşleme satırı ayrıştırılamadı: {line!r}")
        mapping[parts[0]] = parts[1]
    if not inside:
        raise ValueError(
            f"baseline raporunda {MAPPING_HEADER!r} bloğu yok — "
            "eski şemalı (v1) bir rapor olabilir; taze bir taban al."
        )
    return mapping


def _compare(baseline: dict[str, str], current: dict[str, str]) -> tuple[list[str], int]:
    """Baseline ile şimdiki eşlemeyi çift çift karşılaştırır.

    `remapped` ve `removed` ihlaldir; `added` olağan işletimdir.
    """
    remapped = sorted(
        brand_id
        for brand_id, sector_id in current.items()
        if brand_id in baseline and baseline[brand_id] != sector_id
    )
    removed = sorted(set(baseline) - set(current))
    added = sorted(set(current) - set(baseline))

    lines = [
        COMPARISON_HEADER,
        f"baseline_brands: {len(baseline)}",
        f"remapped: {len(remapped)}",
        f"removed: {len(removed)}",
        f"added: {len(added)}",
    ]
    for brand_id in remapped:
        lines.append(
            f"- remapped brand={brand_id} "
            f"from={baseline[brand_id]} to={current[brand_id]}"
        )
    for brand_id in removed:
        lines.append(f"- removed brand={brand_id} was={baseline[brand_id]}")
    for brand_id in added:
        lines.append(f"- added brand={brand_id} sector_id={current[brand_id]}")

    return lines, len(remapped) + len(removed)


def _render(
    rows: list[asyncpg.Record],
    sub_sector_rows: int,
    baseline: dict[str, str] | None,
) -> tuple[str, int]:
    """Raporu ve İHLAL sayısını üretir (ihlal = kök bağlanma + eşleme kayması)."""
    reasons = {row["brand_id"]: _difference_reason(row) for row in rows}
    differences = [row for row in rows if reasons[row["brand_id"]] is not None]

    mapping = {
        row["brand_id"]: row["sector_id"] if row["sector_id"] else NO_SECTOR
        for row in rows
    }

    lines = [
        "sector_sweep report",
        f"schema_version: {REPORT_SCHEMA_VERSION}",
        f"brands_total: {len(rows)}",
        f"brands_root_anchored: {len(rows) - len(differences)}",
        f"sub_sector_rows: {sub_sector_rows}",
        f"differences: {len(differences)}",
    ]
    for row in differences:
        lines.append(
            f"- brand={row['brand_id']} sector_id={row['sector_id']} "
            f"reason={reasons[row['brand_id']]} "
            f"parent_sector_id={row['parent_sector_id']}"
        )

    # Eşleme bloğu: satır sırası sorgudan gelir (brand_id'ye göre sıralı).
    lines.append(MAPPING_HEADER)
    for row in rows:
        lines.append(f"{row['brand_id']} {mapping[row['brand_id']]}")

    violations = len(differences)
    if baseline is not None:
        comparison, drift = _compare(baseline, mapping)
        lines.append("")
        lines.extend(comparison)
        violations += drift

    return "\n".join(lines) + "\n", violations


async def sweep(
    database_url: str, baseline: dict[str, str] | None = None
) -> tuple[str, int]:
    """Raporu ve ihlal sayısını döner. Yazma YOK — salt-okunur transaction."""
    connection = await asyncpg.connect(database_url)
    try:
        # Yapısal salt-okunurluk: yetkili dizeyle koşulsa bile yazamaz.
        await connection.execute("BEGIN TRANSACTION READ ONLY")
        try:
            rows = await connection.fetch(_SWEEP_SQL)
            sub_sector_rows = await connection.fetchval(_SUB_SECTOR_COUNT_SQL)
        finally:
            await connection.execute("COMMIT")
    finally:
        await connection.close()

    return _render(rows, sub_sector_rows, baseline)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Marka → kök sektör tam sweep'i (salt-okunur)."
    )
    parser.add_argument(
        "--database-url",
        required=True,
        help="Bağlantı dizesi — AÇIKÇA verilir, ortamdan miras alınmaz.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help=(
            "Önceki bir sweep raporu. Eşlemeler çift çift karşılaştırılır; "
            "kökten köke kayma da ihlal sayılır. Taksonomi sayıları "
            "karşılaştırmaya girmez."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Açık salt-okunurluk beyanı. Script zaten hiçbir koşulda yazmaz; "
            "bayrak operasyonel çağrıda niyeti görünür kılar."
        ),
    )
    args = parser.parse_args(argv)

    baseline = None
    if args.baseline is not None:
        try:
            baseline = parse_mapping(args.baseline.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            # Okunamayan/bozuk taban SESSİZ GEÇİLMEZ: karşılaştırmasız "temiz"
            # rapor, tam da bu aracın engellemek için var olduğu yanılgıdır.
            sys.stderr.write(f"baseline okunamadı: {exc}\n")
            return 2

    report, violations = asyncio.run(sweep(args.database_url, baseline))
    sys.stdout.write(report)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
