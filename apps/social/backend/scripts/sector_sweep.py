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
* **Taban hedefe BAĞLI.** Rapor, üretildiği veritabanının kimliğini taşır:
  küme kimliği / oid / ad **artı bağlantı ucu** (`sunucu:port/veritabanı`).
  `--baseline` başka bir hedefin raporunu REDDEDER (rc=2). Aksi hâlde başka bir
  veritabanından gelen geçerli biçimli bir taban her markayı "yeni" gösterir ve
  kaymayı gizlerdi. Bağlantı ucu şart, çünkü fiziksel bir kopya (yedekten geri
  yükleme, standby) veritabanı-içi kimliğin ÜÇÜNÜ DE aynen taşır — prod
  yedeğinden kurulmuş bir staging bu yüzden orijinalden ayırt edilemezdi.
  Uç İKİ kaynaktan gelir: kanonik bağlantı dizesi ve sunucunun KENDİ gördüğü
  adres. Yalnız dizeye bakmak yetmezdi — `PGPORT` ve `?host=` gibi yollar iki
  farklı sunucuya giden iki dizeyi aynı metne indirger. Bilinen bedel: sunucu
  adresi değişirse (ör. kap yeniden başlar ve yeni IP alır) eski taban
  reddedilir; bu FAIL-CLOSED yöndür, taban yeniden alınır.
* **Bilinçli sınır (BELGELİ KALINTI).** Araç, tabanın geçmişte DOĞRU olduğunu
  kanıtlayamaz; taban geçmiş bir durumdur ve güveni onu bu script'in yazmış
  olmasından alır. Elle düzenlenmiş (sayacı da güncellenmiş) bir taban, aynı
  hedefe aitse kabul edilir. Kimlik doğrulamalı özet (HMAC) bunu kapatırdı ama
  salt-okunur bir işletim raporu için orantısızdır. Yeniden açılma koşulu: taban
  dosyaları güvenilmeyen bir kanaldan taşınmaya başlarsa.
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
from urllib.parse import parse_qs, urlsplit

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

# Hedef kimliğinin veritabanı-içi yarısı: küme kimliği / veritabanı oid'i /
# veritabanı adı. Salt-okunur rolde erişilebilirliği ÖLÇÜLDÜ (PostgreSQL 18.3,
# 127.0.0.1:5433).
#
# Bu üçlü TEK BAŞINA yetmez (Codex checkpoint 5 tur 4): fiziksel bir kopya —
# yedekten geri yükleme, standby, depolama anlık görüntüsü — üçünü de AYNEN
# taşır. PostgreSQL küme kimliğini zaten "aynı kümeden türedi" kanıtı olarak
# kullanır. Prod yedeğinden kurulmuş bir staging veritabanı bu yüzden orijinalden
# ayırt edilemezdi. Kimliğe bu yüzden BAĞLANTI UCU da eklenir: kopya başka bir
# adreste durur.
_TARGET_SQL = """
SELECT format(
    '%s/%s/%s',
    (SELECT system_identifier FROM pg_control_system()),
    (SELECT oid FROM pg_database WHERE datname = current_database()),
    current_database()
)
"""


class InvalidTarget(ValueError):
    """Bağlantı dizesi belirsiz — hangi sunucuya gidileceği metinden okunamıyor."""


# Bağlantı ucunu METİNDEN okumak yetmez: asyncpg `PGPORT` gibi ortam
# değişkenlerini ve `?host=`/`?port=` sorgu parametrelerini de dikkate alır.
# İki FARKLI sunucuya giden iki dize aynı metni üretebilir (Codex checkpoint 5
# tur 5). O yüzden iki kapı birden:
#   1. Dize KANONİK olmak zorunda — tek TCP sunucusu, açık sayısal port, açık
#      veritabanı adı, uç-değiştiren sorgu parametresi YOK. Belirsiz dize
#      bağlanmadan ÖNCE reddedilir.
#   2. Kimliğe sunucunun KENDİ gördüğü uç eklenir. Metne değil sunucunun
#      cevabına dayanır; yönlendirilmiş port veya yeniden yönlendirilmiş ad
#      buradan yakalanır.
_ENDPOINT_QUERY_KEYS = frozenset({"host", "port", "dbname", "database"})

# Sunucunun kendi gördüğü uç. Unix soketinde `inet_server_addr()` NULL döner;
# `port` ayarı okunabilir (ÖLÇÜLDÜ — `unix_socket_directories` ve
# `data_directory` salt-okunur role KAPALI, onlara dayanılmaz).
_SERVER_PEER_SQL = """
SELECT format(
    '%s:%s',
    coalesce(host(inet_server_addr()), 'local'),
    coalesce(inet_server_port()::text, current_setting('port'))
)
"""


def canonical_endpoint(database_url: str) -> str:
    """Kanonik `sunucu:port/veritabanı` — belirsiz dizeyi REDDEDER.

    Parola ve kullanıcı adı çıktıya GİRMEZ; hata mesajları da ham dizeyi
    basmaz, yalnız hangi kuralın çiğnendiğini söyler.
    """
    parts = urlsplit(database_url)

    if parts.scheme not in ("postgresql", "postgres"):
        raise InvalidTarget(f"şema {parts.scheme!r} desteklenmiyor")

    authority = parts.netloc.rsplit("@", 1)[-1]
    if "," in authority:
        raise InvalidTarget("çok-sunuculu dize: hangi sunucu olduğu belirsiz")

    host = parts.hostname
    if not host:
        raise InvalidTarget("sunucu adı yok (soket/varsayılan uç belirsizdir)")

    try:
        port = parts.port
    except ValueError:
        raise InvalidTarget("port sayısal değil") from None
    if port is None:
        raise InvalidTarget("port açıkça verilmeli (PGPORT'a düşülmez)")

    database = parts.path.lstrip("/")
    if not database:
        raise InvalidTarget("veritabanı adı açıkça verilmeli")

    overrides = sorted(_ENDPOINT_QUERY_KEYS & set(parse_qs(parts.query)))
    if overrides:
        raise InvalidTarget(f"uç-değiştiren sorgu parametresi: {', '.join(overrides)}")

    return f"{host}:{port}/{database}"


class BaselineMismatch(ValueError):
    """Taban BAŞKA bir veritabanından — karşılaştırma anlamsız, koşmaz."""


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


def _declared(report: str, field: str) -> str | None:
    """Rapor başlığındaki `<field>: <değer>` satırını okur (ilk eşleşme)."""
    prefix = f"{field}: "
    for line in report.splitlines():
        if line == MAPPING_HEADER:
            break
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def parse_baseline(report: str) -> tuple[str, dict[str, str]]:
    """Bir raporun eşleme bloğunu `{brand_id: sector_id}` olarak okur.

    Yalnız `--- mapping ---` ile sonraki blok başlığı arasını okur; özet
    satırları ve karşılaştırma bloğu ayrıştırmaya GİRMEZ.

    TAMLIK DENETİMİ (Codex checkpoint 5 tur 2, yüksek bulgu): yarıda kesilmiş
    bir taban FAIL-OPEN'dı. Eksik kalan markalar `_compare`'de "yeni eklenmiş"
    sayılıyordu, `added` ise ihlal DEĞİLDİR — yani o markalardan birinin kökten
    köke kayması `remapped: 0` + rc=0 ile geçiyordu. Kesilme olağan bir kaza
    (yarıda kalmış yönlendirme yazımı), o yüzden taban artık kendi beyanına
    karşı doğrulanır: sürüm tam eşleşmeli, satır sayısı beyan edilen
    `brands_total` ile aynı olmalı, marka kimliği tekrar etmemeli.
    """
    declared_target = _declared(report, "target")
    if not declared_target:
        raise ValueError("baseline 'target' beyanı yok — taze bir taban al.")

    declared_version = _declared(report, "schema_version")
    if declared_version != str(REPORT_SCHEMA_VERSION):
        raise ValueError(
            f"baseline şema sürümü {declared_version!r}, beklenen "
            f"{str(REPORT_SCHEMA_VERSION)!r} — taze bir taban al."
        )

    declared_total = _declared(report, "brands_total")
    if declared_total is None or not declared_total.isdigit():
        raise ValueError(
            f"baseline 'brands_total' beyanı okunamadı: {declared_total!r}"
        )

    mapping: dict[str, str] = {}
    inside = False
    seen = 0
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
        if parts[0] in mapping:
            # Sözlük sessizce üzerine yazardı; tekrar eden kimlik bozuk tabandır.
            raise ValueError(f"baseline'da tekrar eden marka kimliği: {parts[0]}")
        mapping[parts[0]] = parts[1]
        seen += 1
    if not inside:
        raise ValueError(
            f"baseline raporunda {MAPPING_HEADER!r} bloğu yok — "
            "eski şemalı (v1) bir rapor olabilir; taze bir taban al."
        )
    if seen != int(declared_total):
        raise ValueError(
            f"baseline eksik: {declared_total} marka beyan edilmiş, eşleme "
            f"bloğunda {seen} satır var — dosya yarıda kesilmiş olabilir."
        )
    return declared_target, mapping


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
    target: str,
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
        f"target: {target}",
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
    database_url: str, baseline: tuple[str, dict[str, str]] | None = None
) -> tuple[str, int]:
    """Raporu ve ihlal sayısını döner. Yazma YOK — salt-okunur transaction."""
    # Belirsiz dize sunucuya HİÇ gitmez — doğrulama bağlantıdan ÖNCE.
    canonical_endpoint(database_url)

    connection = await asyncpg.connect(database_url)
    try:
        # Yapısal salt-okunurluk: yetkili dizeyle koşulsa bile yazamaz.
        await connection.execute("BEGIN TRANSACTION READ ONLY")
        try:
            cluster_identity = await connection.fetchval(_TARGET_SQL)
            server_peer = await connection.fetchval(_SERVER_PEER_SQL)
            rows = await connection.fetch(_SWEEP_SQL)
            sub_sector_rows = await connection.fetchval(_SUB_SECTOR_COUNT_SQL)
        finally:
            await connection.execute("COMMIT")
    finally:
        await connection.close()

    if not cluster_identity or not server_peer:
        raise ValueError("hedef kimliği okunamadı — karşılaştırma yapılamaz")
    target = f"{cluster_identity}@{canonical_endpoint(database_url)}~{server_peer}"

    baseline_mapping = None
    if baseline is not None:
        baseline_target, baseline_mapping = baseline
        if baseline_target != target:
            # BAŞKA bir veritabanının tabanı: her marka "yeni" görünür, kayma
            # gizlenirdi (Codex checkpoint 5 tur 3).
            raise BaselineMismatch(
                f"taban başka bir hedeften: baseline={baseline_target!r} "
                f"target={target!r}"
            )

    return _render(rows, sub_sector_rows, target, baseline_mapping)


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
            baseline = parse_baseline(args.baseline.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            # Okunamayan/bozuk taban SESSİZ GEÇİLMEZ: karşılaştırmasız "temiz"
            # rapor, tam da bu aracın engellemek için var olduğu yanılgıdır.
            sys.stderr.write(f"baseline okunamadı: {exc}\n")
            return 2

    try:
        report, violations = asyncio.run(sweep(args.database_url, baseline))
    except BaselineMismatch as exc:
        sys.stderr.write(f"baseline okunamadı: {exc}\n")
        return 2
    except InvalidTarget as exc:
        sys.stderr.write(f"bağlantı dizesi kanonik değil: {exc}\n")
        return 2
    except Exception as exc:
        # Bağlantı/sorgu hatası da FAIL-CLOSED olmalı: yakalanmayan istisna
        # rc=1 ile çıkardı ve rc=1 "fark bulundu" anlamına gelir — karışırdı.
        # Ham istisna metni BASILMAZ: bağlantı dizesini (dolayısıyla parolayı)
        # taşıyabilir. Yalnız tür adı + kimlik bilgisi taşımayan uç basılır.
        try:
            where = canonical_endpoint(args.database_url)
        except InvalidTarget:
            where = "<kanonik olmayan uç>"
        sys.stderr.write(f"sweep koşulamadı ({type(exc).__name__}) — hedef: {where}\n")
        return 2

    sys.stdout.write(report)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
