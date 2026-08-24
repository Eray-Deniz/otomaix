#!/usr/bin/env python3
"""Marka → kök sektör tam sweep'i (salt-okunur, deterministik, re-runnable).

Spec §5.3 / plan Task 5. Tek iddiası var ve o iddia TAM kümede ölçülür:

    Her markanın `sector_id`'si bir KÖK sektör satırına (`parent_sector_id IS NULL`)
    bağlıdır.

Alt sektör satırları yalnız paket katmanının adresidir; markanın kendi sektörü
asla oraya kaymamalıdır (R-01). Bu script o kaymayı canlıda da görünür kılar —
Plan 2'nin satır-açma adımının ÖNCESİNDE ve SONRASINDA aynı komut koşulur, iki
rapor karşılaştırılır.

Sözleşme:

* **Salt-okunur.** Bağlantı `BEGIN TRANSACTION READ ONLY` içinde açılır: yetkili
  bir bağlantı dizesiyle koşulsa bile yazma girişimi veritabanı tarafından
  reddedilir. Testte ayrıca salt-okunur ROL ile koşulur.
* **Deterministik.** Rapor zaman damgası, süre, rastgele sıra içermez; satırlar
  marka kimliğine göre sıralıdır. Aynı veri → bayt-aynı çıktı.
* **Ortamdan miras almaz.** Bağlantı dizesi `--database-url` ile AÇIKÇA verilir;
  `DATABASE_URL` ortam değişkeni okunmaz (yanlış veritabanına koşma riski yok).
* **Çıkış kodu.** Fark yoksa 0, fark varsa 1 — CI/operasyon zincirine takılabilir.

Kullanım:

    python scripts/sector_sweep.py --database-url postgresql://... --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import sys

import asyncpg

# Rapor biçimi değişirse artar — iki koşumun karşılaştırılabilirliği buna bağlı.
REPORT_SCHEMA_VERSION = 1

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
    """Markanın kök bağlanmasını bozan sebep — yoksa None."""
    if row["sector_id"] is None:
        return "null_sector"
    if not row["sector_exists"]:
        # FK bunu engelliyor; yine de sessiz geçilmez.
        return "missing_sector"
    if row["parent_sector_id"] is not None:
        return "sub_sector"
    return None


def _render(rows: list[asyncpg.Record], sub_sector_rows: int) -> str:
    differences = [
        (row["brand_id"], row["sector_id"], reason, row["parent_sector_id"])
        for row in rows
        if (reason := _difference_reason(row)) is not None
    ]

    lines = [
        "sector_sweep report",
        f"schema_version: {REPORT_SCHEMA_VERSION}",
        f"brands_total: {len(rows)}",
        f"brands_root_anchored: {len(rows) - len(differences)}",
        f"sub_sector_rows: {sub_sector_rows}",
        f"differences: {len(differences)}",
    ]
    for brand_id, sector_id, reason, parent_sector_id in differences:
        lines.append(
            f"- brand={brand_id} sector_id={sector_id} "
            f"reason={reason} parent_sector_id={parent_sector_id}"
        )
    return "\n".join(lines) + "\n"


async def sweep(database_url: str) -> tuple[str, int]:
    """Raporu ve fark sayısını döner. Yazma YOK — salt-okunur transaction."""
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

    report = _render(rows, sub_sector_rows)
    difference_count = sum(1 for row in rows if _difference_reason(row) is not None)
    return report, difference_count


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
        "--dry-run",
        action="store_true",
        help=(
            "Açık salt-okunurluk beyanı. Script zaten hiçbir koşulda yazmaz; "
            "bayrak operasyonel çağrıda niyeti görünür kılar."
        ),
    )
    args = parser.parse_args(argv)

    report, difference_count = asyncio.run(sweep(args.database_url))
    sys.stdout.write(report)
    return 1 if difference_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
