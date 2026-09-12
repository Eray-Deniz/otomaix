#!/usr/bin/env python3
"""Sektör bilgi paketi işletim hattının operatör komut ailesi (plan Task 16).

Hattın her adımının **adlandırılmış bir CLI girişi** vardır (arayüz eki R10):
operatörün elle koşmak zorunda olduğu hiçbir adım servis katmanında erişilemez
kalmaz. Komut ailesi iş mantığı TAŞIMAZ — her alt komut Task 1-15'in servis
yüzeyini çağırır, çıktıyı deterministik biçimde basar ve anlamlı bir çıkış kodu
döner.

Desen `scripts/sector_sweep.py`'den alınır ve BAĞLAYICIDIR:

* **argparse** — alt komutlar ve argümanlar açıkça adlandırılır.
* **Açık kanal** (`--database-url-env` / `--database-url-file`; argv'ye yazılmaz,
  2026-09-12 güvenlik review'ı S-3) — bağlantı dizesi ortamdan sessizce MİRAS ALINMAZ; yanlış
  veritabanına koşma yolu yoktur.
* **Deterministik çıktı** — zaman damgası, süre, rastgele sıra içermez; aynı
  girdi bayt-aynı çıktı üretir. Operatör iki koşumu `diff`'leyebilir.
* **Anlamlı çıkış kodu** — aşağıdaki `RC_*` sabitleri.

**Sözleşme pini (plan Task 16 invariantı).** Resmî koşu başlatan her alt komut
İLK İŞ olarak `contracts.require_pin` çağırır: dış sözleşme deposu pinden
saparsa koşu HİÇ BAŞLAMAZ. Kapı bağlantıdan ÖNCE koşar — sürüklenmiş bir
sözleşmeyle açılmış bir veritabanı oturumu bile istenmez.

**Adımlar arası devir koşu klasörüdür** (spec-input §7.5 "Çıktıların saklanması
— iki katman"): dosya çalışma kopyasıdır, veri tabanı kalıcı kanıt katmanıdır.
Her adım çıktısını koşu klasörüne yazar ve aynı içerik `record_artifact` ile ham
artefakt tablosuna iner; sonraki adım ekleri o yoldan toplar.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from uuid import UUID

import _dsn_channel
import asyncpg

_BACKEND_KOKU = Path(__file__).resolve().parents[1]
if str(_BACKEND_KOKU) not in sys.path:
    sys.path.insert(0, str(_BACKEND_KOKU))

from app.services import notifications, sector_packages  # noqa: E402
from app.services import sector_package_lifecycle as lifecycle  # noqa: E402
from app.services.sector_pipeline import (  # noqa: E402
    approval,
    auditors,
    brief_doctor,
    contracts,
    engine,
    identity,
    policy_config,
    readiness,
    readiness_items,
    runs,
    synthesis,
    writeback,
)

# ─── Çıkış kodları — anlamlı ve KAPALI ──────────────────────────────────────

RC_OK = 0
"""Adım koştu ve kabul edildi."""

RC_REFUSED = 1
"""Alan kuralı REDDETTİ: kapı sağlanmadı, kanıt kurulamadı, onay yok."""

dsn_coz = _dsn_channel.dsn_coz
"""Bağlantı dizesi çözücüsü — kanal sözleşmesi `scripts/_dsn_channel.py`'de."""

RC_USAGE = 2
"""Çağrı ya da ortam hatası: argüman, sözleşme pini sürüklenmiş, bağlanılamadı."""

RC_LOCKED = 3
"""Olay üyeliği KİLİTLİ — yürütme başlamış, hiçbir satır yazılmadı (AÇIK-1)."""

# ─── Sözleşme pini ──────────────────────────────────────────────────────────

PIN_PATH = auditors.PIN_PATH
"""Pin manifesti — denetçi modülünün sabitinden ALINIR, yeniden türetilmez.

İkinci bir türetim (`parents[N]` sayarak aynı yolu kurmak) aynı dosyayı bugün
gösterir ve dizin yapısı değiştiği gün sessizce ayrışırdı."""

PIN_DEPO_KOKU = auditors.ARASTIRMA_DEPOSU_KOKU
"""Pinin ölçtüğü depo — dış sözleşme deposunun kökü, yine tek kaynaktan."""

RUN_SUBCOMMANDS: frozenset[str] = frozenset(
    {
        "tur-ac",
        "brief-doctor",
        "denetim",
        "sentez",
        "motor",
        "katman1",
        "katman2",
        "hazirlik-onayla",
        "duzeltme-baslat",
        "yazim",
        "duzeltme-yaz",
        "onay",
        "aktive-et",
        "deaktive-et",
        "olay-plani",
        "olay-onayla",
        "olay-geri-al",
        "vade-bildirimi",
    }
)
"""Resmî koşu başlatan alt komutlar — pin kapısı bunların HEPSİNE uygulanır.

Küme AÇIKÇA sayılır; "mutasyon yapıyor mu" diye türetilmez. Türetme, yeni bir
alt komutun kapıya sessizce girmemesi riskini taşırdı — kapı listesi kodun
okunabilir bir parçası olmalıdır.

Dışarıda kalan ikisi SALT-OKUNURDUR ve koşu başlatmaz: `etki-analizi` · `durum`.
"""


class CliError(RuntimeError):
    """Operatöre gösterilecek, kimlik bilgisi taşımayan hata."""


def _uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except (ValueError, AttributeError, TypeError):
        raise argparse.ArgumentTypeError(f"geçerli bir UUID değil: {value!r}") from None


# ─── Argüman ayrıştırıcı ────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Komut ailesinin TEK ayrıştırıcısı — alt komut kümesi burada kapanır."""
    parser = argparse.ArgumentParser(
        prog="sector_pipeline_cli",
        description=(
            "Sektör bilgi paketi işletim hattının operatör komutları. "
            "Bağlantı dizesi AÇIKÇA verilir, ortamdan miras alınmaz."
        ),
    )
    # Bağlantı dizesi argv'ye YAZILMAZ (2026-09-12 güvenlik review'ı, S-3):
    # kanal ya 0600 bir dosya ya da ADI açıkça verilen bir ortam değişkenidir.
    # "Ortamdan sessiz miras YOK" tasarım kararı korunur — değişken adlandırılır.
    _dsn_channel.kanal_argumanlarini_ekle(parser)
    alt = parser.add_subparsers(dest="komut", required=True, metavar="<alt komut>")

    def _ekle(ad: str, yardim: str) -> argparse.ArgumentParser:
        return alt.add_parser(ad, help=yardim, description=yardim)

    # ── Koşu yaşam döngüsü ──────────────────────────────────────────────
    p = _ekle("tur-ac", "Yeni koşu satırı açar ve koşu kimliğini basar.")
    p.add_argument("--sector-id", required=True, type=_uuid)
    p.add_argument("--kosu-turu", required=True, choices=("ilk", "periyodik"))

    p = _ekle("duzeltme-baslat", "Reddedilmiş koşudan düzeltme turu açar (K-72).")
    p.add_argument("--parent-run-id", required=True)
    p.add_argument("--actor", required=True)

    # ── Hattın adımları ─────────────────────────────────────────────────
    p = _ekle("brief-doctor", "Mekanik eleme raporunu üretir ve artefakt yazar.")
    p.add_argument("--run-id", required=True)
    p.add_argument("--kaynak-dosya", required=True, type=Path)
    p.add_argument("--kaynak-adi", required=True)
    p.add_argument("--sektor-slug", required=True)
    p.add_argument(
        "--damga",
        required=True,
        help=(
            "K-80 tekrar-üretilebilirlik damgası — "
            "'model=<...>; surum=<...>; tarih=YYYY-MM-DD; girdi_ozeti=<...>'. "
            "Operatör verir; komut TARİH ÜRETMEZ (deterministik çıktı)."
        ),
    )

    p = _ekle("denetim", "İki kör denetçiyi sırayla koşturur (K-78/K-79).")
    p.add_argument("--run-id", required=True)
    p.add_argument(
        "--zaman-asimi-sn",
        required=True,
        type=float,
        help=(
            "Denetçi alt süreçlerinin dış zaman aşımı. VARSAYILANI YOKTUR: "
            "CLI'ların kendi zaman aşımı bayrağı yok ve ölçülmemiş bir saniye "
            "değeri sabit yazılmaz."
        ),
    )
    p.add_argument("--sektor-slug", required=True)
    p.add_argument(
        "--arac-surumu",
        required=True,
        help="K-80 damgasının `surum` alanı — koşan aracın sürümü, operatör verir.",
    )
    p.add_argument(
        "--tarih",
        required=True,
        help="K-80 damgasının `tarih` alanı (YYYY-MM-DD). Komut TARİH ÜRETMEZ.",
    )

    p = _ekle("sentez", "Sentez turunu koşturur; adayı ve karar günlüğünü üretir.")
    p.add_argument("--run-id", required=True)
    p.add_argument("--zaman-asimi-sn", required=True, type=float)
    p.add_argument("--sektor-slug", required=True)
    p.add_argument(
        "--arac-surumu",
        required=True,
        help="K-80 damgasının `surum` alanı — koşan aracın sürümü, operatör verir.",
    )
    p.add_argument(
        "--tarih",
        required=True,
        help="K-80 damgasının `tarih` alanı (YYYY-MM-DD). Komut TARİH ÜRETMEZ.",
    )

    p = _ekle("motor", "Politika motorunu koşturur ve koşu sonucunu yazar.")
    p.add_argument("--run-id", required=True)
    p.add_argument(
        "--politika-ayari",
        type=Path,
        default=None,
        help=(
            "Motor ayar dosyası (JSON). Verilmezse eşikler PASİF kalır — K-24: "
            "eşikler pilot kanıtından sonra belirlenir, uydurulmaz."
        ),
    )

    # ── Yazım kapısı (arayüz eki R10) ───────────────────────────────────
    p = _ekle("yazim", "Doğrulanmış koşudan YENİ taslak sürümü yazar.")
    p.add_argument("--run-id", required=True)
    p.add_argument("--actor", required=True)

    p = _ekle("duzeltme-yaz", "Düzeltme koşusunu AYNI taslağa yazar (K-106).")
    p.add_argument("--run-id", required=True)
    p.add_argument("--actor", required=True)

    # ── Tasdikler (F18) ─────────────────────────────────────────────────
    p = _ekle("katman1", "Katman-1 tam sweep tasdiği.")
    p.add_argument("--run-id", required=True)
    p.add_argument("--kosum-kimligi", required=True)
    p.add_argument("--sonuc", required=True, choices=("PASS", "FAIL"))
    p.add_argument("--actor", required=True)

    p = _ekle("katman2", "Katman-2 kör örneklem — koşuldu + SUNULDU tasdiği.")
    p.add_argument("--run-id", required=True)
    p.add_argument("--kosum-kimligi", required=True)
    p.add_argument("--ozet", required=True)
    p.add_argument("--actor", required=True)

    p = _ekle(
        "hazirlik-onayla",
        "İşletime hazırlık listesini sunar; --onayla ile operatörün TEK onayını yazar.",
    )
    p.add_argument("--run-id", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument(
        "--onayla",
        action="store_true",
        help="Listeyi ONAYLAR ve tasdiki yazar. Verilmezse yalnız rapor basılır.",
    )

    # ── Onay ve aktivasyon ──────────────────────────────────────────────
    p = _ekle("onay", "Onay görüntüsünü dondurur; kararla çağrılırsa kaydeder.")
    p.add_argument("--run-id", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--karar", choices=("onay", "ret"))
    p.add_argument("--saniye", type=int)
    p.add_argument("--snapshot-sha")

    p = _ekle("aktive-et", "Onaylanmış görüntüden aktivasyon (tek üretim yolu).")
    p.add_argument("--run-id", required=True)
    p.add_argument("--actor", required=True)

    p = _ekle("deaktive-et", "Aktif paketi indirir — K-38 acil kolu, kanıt İSTEMEZ.")
    p.add_argument("--package-id", required=True, type=_uuid)
    p.add_argument("--actor", required=True)

    # ── K-145 olay zinciri ──────────────────────────────────────────────
    def _dortlu(hedef: argparse.ArgumentParser) -> None:
        """Kural sürümünü adlandıran DÖRTLÜ — dördü de zorunludur."""
        hedef.add_argument("--engine-version", required=True)
        hedef.add_argument("--engine-config-sha", required=True)
        hedef.add_argument("--kural-kimligi", required=True)
        hedef.add_argument("--kural-surumu", required=True)

    p = _ekle("etki-analizi", "Bir kural sürümünün etkilediği paket kümesi.")
    _dortlu(p)

    p = _ekle("olay-plani", "Olay planı YAZAR; --incident-id ile üyeliği DEĞİŞTİRİR.")
    _dortlu(p)
    p.add_argument("--actor", required=True)
    p.add_argument("--incident-id")

    p = _ekle("olay-onayla", "Olayın bekleyen plan satırlarını damgalar.")
    p.add_argument("--incident-id", required=True)
    p.add_argument("--actor", required=True)

    p = _ekle("olay-geri-al", "Olay planını paket paket yürütür.")
    p.add_argument("--incident-id", required=True)
    p.add_argument("--actor", required=True)

    # ── Bildirim + okuma ────────────────────────────────────────────────
    p = _ekle("vade-bildirimi", "Periyodu dolan paketler için yönetici bildirimi (K-26).")
    p.add_argument("--actor", required=True)

    p = _ekle("durum", "Koşunun salt-okunur durum görünümü.")
    p.add_argument("--run-id", required=True)

    return parser


# ─── Alt komut gövdeleri ────────────────────────────────────────────────────
#
# Her gövde `(satırlar, çıkış kodu)` döner. Basım TEK yerde (`main`) yapılır:
# gövdeler `print` çağırmaz, böylece testler onları doğrudan çağırabilir ve
# çıktının deterministikliği tek noktadan ölçülür.
#
# ÇIKIŞ KODU EŞLEMESİ `dispatch`TEDİR (gövdelerde DEĞİL). İki yerde olsaydı bir
# gövde kendi eşlemesini yazar ve alan hatası sessizce RC_USAGE'a düşerdi;
# operatör "ortam bozuk" sanıp yanlış yere bakardı.

Sonuc = tuple[list[str], int]

VADE_AYI = 6
"""K-26 — Faz 1'de TEK değer: 6 ay (karar metni birebir).

Sektör başına alan K-26'nın nihai biçimidir; Faz 1'de tek değer geçerli olduğu
için burada sabittir. Alan doğduğu gün bu sabit ONUN varsayılanı olur."""

VADE_OLAYI = "sektor_paketi.vade_doldu"
"""K-26 bildiriminin outbox türü — K-45 ile AYNI altyapı, ayrı `kind`."""


async def _kos_tur_ac(conn, args) -> Sonuc:
    run_id = runs.new_run_id()
    await runs.open_run(
        conn, sector_id=args.sector_id, run_id=run_id, kosu_turu=args.kosu_turu
    )
    return ([f"run_id: {run_id}", f"kosu_turu: {args.kosu_turu}"], RC_OK)


async def _kos_duzeltme_baslat(conn, args) -> Sonuc:
    run_id = await runs.open_correction_run(
        conn, parent_run_id=args.parent_run_id, actor=args.actor
    )
    return ([f"run_id: {run_id}", f"duzeltilen_run_id: {args.parent_run_id}"], RC_OK)


async def _kos_brief_doctor(conn, args) -> Sonuc:
    """Mekanik eleme raporunu üretir ve ham artefakt katmanına yazar.

    Yerel arıza SESSİZ KALMAZ: adım düşerse koşu `tamamlanmadi` işaretlenir ve
    AYNI işlemde yönetici bildirimi yazılır (K-82). n8n `errorWorkflow` bu hattı
    göremez — orada yalnız workflow'un kendi arızası görünür.
    """
    try:
        metin = Path(args.kaynak_dosya).read_text(encoding="utf-8")
        rapor = brief_doctor.run(metin, source_name=args.kaynak_adi)
    except Exception as hata:
        await runs.mark_incomplete(
            conn,
            run_id=args.run_id,
            asama="brief-doctor",
            sebep=f"{type(hata).__name__}",
        )
        return ([f"brief-doctor yarım kaldı: {type(hata).__name__}"], RC_REFUSED)

    await runs.record_artifact(
        conn,
        run_id=args.run_id,
        sector_slug=args.sektor_slug,
        kind="brief-doctor-raporu",
        source=args.damga,
        content_md=rapor.metin if hasattr(rapor, "metin") else str(rapor),
    )
    return (
        [f"run_id: {args.run_id}", f"kaynak: {args.kaynak_adi}", "artefakt: yazildi"],
        RC_OK,
    )


# ─── Hattın adımları — devir aracı KOŞU KLASÖRÜ + ham artefakt katmanı ─────
#
# Spec-input §7.5 ("Çıktıların saklanması — iki katman") bağlayıcıdır: dosya
# çalışma kopyası, veri tabanı kalıcı kanıt katmanıdır; ekler klasör yolundan
# toplanır. Adımlar AYRI süreçlerde koşar (Task 19 Step 6-8: motor, sentezden
# SONRA ve operatörün kör yargısı kaydedildikten sonra koşar), bu yüzden bir
# adımın bellekteki sonucu bir sonrakine ELDEN verilemez — her adım kendi
# çıktısını yazar, sonraki adım onu OKUR.

KAYNAK_KALIBI = "KAYNAK-{}.md"
BRIEF_DOSYASI = "brief.md"
SENTEZ_ARTEFAKTI = "synthesis"
DENETIM_ARTEFAKTI = "review"
"""Ham artefakt TÜRLERİ — değerler şemanın kapalı kümesinden gelir.

`sector_research_artifacts.kind` migration 032'de `research` · `review` ·
`synthesis` ile KISITLIDIR. Sabitlerin adı Türkçe kalır (hattın adımlarını
adlandırır), DEĞERİ şemanın kabul ettiğidir; 2026-09-11'e dek Türkçe değerler
yazılıyordu ve ilk gerçek koşumda her ham artefakt yazımı düşerdi.
"""

SEMA_DISI_ARTEFAKT_TURLERI: frozenset[str] = frozenset({"brief-doctor-raporu"})
"""Şemanın kabul ETMEDİĞİ, bilinen ve EVİ OLAN artefakt türleri.

**Dürüst etiket: ÇÖZÜLMEDİ.** Mekanik kapı raporu şemanın üç türünden hiçbirine
oturmuyor — `research` ham araştırma çıktısıdır, `review` kör hakem raporudur
(hazırlık listesinin "iki hakem raporu" maddesi o türü SAYAR; mekanik rapor
oraya yazılırsa o ölçüm kirlenir), `synthesis` sentez çıktısıdır. Türü eklemek
şema değişikliği ister.

**Ev: Task 18 (ön-pilot dağıtım — şema ayağı), Eray kararı 2026-09-11.** Orada
ya yeni tür migration ile eklenir ya da bu yazım kaldırılıp rapor koşu klasörüne
alınır. O güne dek `brief-doctor` alt komutu ham artefakt yazımında düşer.
"""


def _kosu_klasoru_koku() -> Path:
    """`build_packet(dest=...)` ve `synthesis.run(dest=...)` AYNI kökü ister.

    İkisi de `<dest>/<run_id>` kurar; kök `runs.run_folder`'ın ürettiği yolun
    ebeveynidir ve ikinci bir yol kuralı YAZILMAZ."""
    return runs.ARASTIRMA_DEPOSU_KOKU / "kosu"


async def _kosu_satiri(conn, run_id: str):
    satir = await conn.fetchrow(
        "SELECT sector_id, kosu_turu, katman1_attestation "
        "FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    if satir is None:
        raise CliError(f"koşu satırı yok: {run_id}")
    return satir


async def _aktif_paket(conn, sector_id):
    """Sektörün aktif paketi + karar birimleri görüntüsü (R6 tek üretici)."""
    satir = await conn.fetchrow(
        "SELECT content, decision_log, schema_version FROM social.sector_packages "
        "WHERE sector_id = $1 AND status = 'active'",
        sector_id,
    )
    if satir is None:
        return None, {}, None
    icerik = _coz(satir["content"])
    gunluk = _coz(satir["decision_log"]) or []
    return icerik, identity.decision_units(icerik, gunluk), satir["schema_version"]


def _coz(deger):
    """asyncpg jsonb kodeki kurulu değilse metin döner — TEK çözme noktası."""
    return json.loads(deger) if isinstance(deger, (str, bytes)) else deger


def _kaynaklari_oku(kok: Path) -> tuple[str, list[str], list[str]]:
    """Koşu klasöründen brief ve kör adlandırılmış kaynakları toplar.

    Kör adlandırma DOSYA ADINDA başlar: araç kimliği ek toplama sırasında da
    açılmaz (spec-input §7.4).
    """
    brief_yolu = kok / BRIEF_DOSYASI
    if not brief_yolu.is_file():
        raise CliError(f"koşu klasöründe {BRIEF_DOSYASI} yok: {kok}")
    kaynaklar, adlar = [], []
    for sira in range(1, auditors.AZAMI_KAYNAK + 1):
        yol = kok / KAYNAK_KALIBI.format(sira)
        if yol.is_file():
            kaynaklar.append(yol.read_text(encoding="utf-8"))
            adlar.append(yol.stem)
    if not kaynaklar:
        raise CliError(f"koşu klasöründe hiç KAYNAK-n.md yok: {kok}")
    return brief_yolu.read_text(encoding="utf-8"), kaynaklar, adlar


class WebProbeUnavailable(RuntimeError):
    """Erişim ölçümü KURULAMADI — meydan okuma değeri alınamadı.

    `preflight` bunu ÖLÇÜM ARIZASI sayar. `False` dönmekten FARKLIDIR ve fark
    bilinçlidir: `False` "ölçtüm, erişim yok" demektir ve K-14'ün muafiyet
    kolunu meşrulaştırır; ölçüm arızası hiçbir muafiyet üretmez."""


WEB_PROB_KAYNAGI = "https://api.github.com/repos/torvalds/linux/commits?per_page=1"
"""Meydan okumanın kaynağı — TAZE ve ÖNCEDEN BİLİNEMEZ bir değer üretir.

Neden bu biçim: en üstteki commit kimliği saatler içinde değişir, yani hiçbir
modelin eğitim verisinde bugünkü değeri BULUNMAZ; ama tek bir koşum boyunca
sabit kalır, yani TAM EŞİTLİKLE karşılaştırılabilir ve tolerans penceresi
uydurmak gerekmez (ölçülmemiş sayı yazılmaz).

Kendi sunucumuzu gerektirmemesi bilinçli: bu görev yeni bir uç kuramaz.
"""


def _meydan_okuma_degeri(zaman_asimi_sn: float) -> str:
    """Beklenen değeri KONTROLÖR kendisi getirir — modele sorulmaz."""
    import json as _json
    import urllib.request

    with urllib.request.urlopen(
        WEB_PROB_KAYNAGI, timeout=zaman_asimi_sn
    ) as yanit:  # noqa: S310 — sabit https URL, kullanıcı girdisi yok
        yuk = _json.loads(yanit.read().decode("utf-8"))
    return str(yuk[0]["sha"])


def _web_probu(zaman_asimi_sn: float, *, getirici=None, kosucu=None):
    """K-14 ön kontrolünün ÜRETİM probu — TAZE MEYDAN OKUMA ile ölçer.

    **Neden meydan okuma (hakem turu 13, yüksek bulgu).** İlk yazım aracı kendi
    komut satırıyla koşturuyor, `example.com`'un H1 metnini istiyor ve stdout'ta
    o alt dizeyi arıyordu. O metin statiktir ve yaygın biçimde bilinir: ağa HİÇ
    çıkmayan bir model onu eğitim bilgisinden üretebilir, yani erişimi OLMAYAN
    denetçi resmî turu başlatabilirdi. İlk düzeltme bunu "ölçemiyorum" diyerek
    kapattı; kapanış turu haklı olarak itiraz etti — o da OLUMLU YOLU tümden
    siliyordu, yani araç erişim kazandığı gün bile tur başlayamazdı.

    **Bugünkü sözleşme — üç yol, üçü de ayrı:**

    * Beklenen değer ALINAMAZSA (kontrolörün kendi getirişi düşerse) ölçüm
      KURULAMAMIŞTIR → `WebProbeUnavailable` → ölçüm arızası, muafiyet YOK.
    * Araç koşamazsa (zaman aşımı, alt süreç arızası) yine ölçüm arızasıdır.
    * Araç koşar ama TAM değeri basamazsa → `False` → ölçülmüş erişimsizlik.
    * Araç TAM değeri basarsa → `True`.

    Karşılaştırma TAM EŞİTLİKTİR, alt dize değil: alt dize eşleşmesi, değeri
    başka bir metnin içine gömen bir cevabı da geçirirdi.

    **ÖLÇÜLMEMİŞ AYAK — dürüst etiket:** olumlu yol CANLI olarak koşulmadı.
    Bugünkü denetçi-2 komut satırında web arama bayrağı YOKTUR (bu kod tabanında
    daha önce ölçülüp yazılı), dolayısıyla bugün beklenen sonuç `False`'tur.
    Olumlu yolun canlı ilk ölçümü Task 19'dur.
    """
    import subprocess

    getirici = getirici or _meydan_okuma_degeri
    kosucu = kosucu or subprocess.run

    def prob(tool: str) -> bool:
        spec = auditors.ARAC_KOMUTLARI[tool]
        try:
            beklenen = getirici(zaman_asimi_sn)
        except Exception as hata:  # noqa: BLE001 — ölçüm kurulamadı
            raise WebProbeUnavailable(
                f"{tool}: meydan okuma değeri alınamadı ({type(hata).__name__}) — "
                "erişim ÖLÇÜLEMEDİ; tur başlamaz ve muafiyet üretilmez"
            ) from hata
        if not beklenen or not str(beklenen).strip():
            raise WebProbeUnavailable(
                f"{tool}: meydan okuma değeri BOŞ — erişim ölçülemedi"
            )

        istem = (
            f"Fetch {WEB_PROB_KAYNAGI} over the network. Reply with ONLY the "
            "value of the first element's \"sha\" field, nothing else. If you "
            "cannot reach the network, reply with the single word UNREACHABLE."
        )
        try:
            sonuc = kosucu(  # noqa: S603 — argv DONMUŞ, kabuk YOK
                list(spec.argv),
                input=istem,
                capture_output=True,
                text=True,
                timeout=zaman_asimi_sn,
            )
        except Exception as hata:  # noqa: BLE001 — araç koşturulamadı
            raise WebProbeUnavailable(
                f"{tool}: prob koşturulamadı ({type(hata).__name__}) — "
                "erişim ÖLÇÜLEMEDİ"
            ) from hata
        if sonuc.returncode != 0:
            # SIFIRDAN FARKLI ÇIKIŞ ÖLÇÜM DEĞİLDİR (kapanış turu 3, yüksek).
            # Önceki yazım burada `False` dönüyordu; `preflight` her `False`'u
            # `ERISIM_YOK` sayar ve o durumun `muafiyet_mesru`su DOĞRUdur —
            # yani eksik bir kimlik bilgisi, çöken bir CLI ya da sinyalle biten
            # bir süreç "ölçtüm, ağ yok" diye kaydediliyor ve K-14'ün muafiyet
            # yetkisini taşıyordu. Ölçüldü: rc=1 → `muafiyet_mesru=True`.
            # Bu fonksiyonun KENDİ vaadi de zaten "araç çökerse ölçüm arızası"
            # diyordu; kod o vaadi tutmuyordu.
            raise WebProbeUnavailable(
                f"{tool}: prob sıfırdan farklı çıktı (rc={sonuc.returncode}) — "
                "erişim ÖLÇÜLMEDİ; muafiyet üretilmez"
            )
        # `False` YALNIZ şuna ayrılmıştır: araç temiz çıktı ama taze meydan
        # okumanın karşılığını basamadı. Ölçülmüş erişimsizlik budur.
        return sonuc.stdout.strip() == str(beklenen).strip()

    return prob


async def _kos_denetim(conn, args) -> Sonuc:
    """İki kör denetçiyi SIRAYLA koşturur; raporları klasöre ve DB'ye yazar."""
    satir = await _kosu_satiri(conn, args.run_id)
    kok = runs.run_folder(args.run_id)
    brief, kaynaklar, adlar = _kaynaklari_oku(kok)
    raporlar = [
        brief_doctor.run(metin, source_name=ad)
        for metin, ad in zip(kaynaklar, adlar, strict=True)
    ]
    aktif, birimler, _surum = await _aktif_paket(conn, satir["sector_id"])

    paket = auditors.build_packet(
        brief=brief,
        sources=kaynaklar,
        doctor_reports=raporlar,
        active_package=aktif,
        unit_snapshot=birimler,
        run_id=args.run_id,
        sector_id=satir["sector_id"],
        dest=_kosu_klasoru_koku(),
    )
    tur = await auditors.run_audit_round(
        conn,
        paket,
        runner=auditors.SubprocessRunner(zaman_asimi_sn=args.zaman_asimi_sn),
        run_id=args.run_id,
        web_prob=_web_probu(args.zaman_asimi_sn),
    )
    if not tur.gecerli:
        return ([f"denetim turu GEÇERSİZ: {tur.sebep}"], RC_REFUSED)

    # Kalıcı kanıt katmanı: aynı içerik ham artefakt tablosuna da iner.
    for rapor in tur.reports:
        await runs.record_artifact(
            conn,
            run_id=args.run_id,
            sector_slug=args.sektor_slug,
            kind=DENETIM_ARTEFAKTI,
            source=runs.build_stamp(
                model=rapor.denetci,
                surum=args.arac_surumu,
                tarih=args.tarih,
                girdi_ozeti=paket.unit_snapshot_sha,
            ),
            content_md=rapor.ham_metin,
        )
    return (
        [
            f"run_id: {args.run_id}",
            f"denetci_sayisi: {len(tur.reports)}",
            f"unit_snapshot_sha: {paket.unit_snapshot_sha}",
            f"kaynak_seti_sha: {paket.kaynak_seti_sha}",
        ],
        RC_OK,
    )


async def _klasor_girdileri(conn, run_id: str, birimler: dict):
    """Koşu klasöründen mekanik eleme raporlarını ve DOĞRULANMIŞ çifti kurar.

    İki şey birlikte döner çünkü ikisi de AYNI kaynak kümesinden türer ve
    ayrı ayrı toplanırlarsa ayrışabilirler: `kaynak_seti_sha` mekanik eleme
    raporlarından, mutabakat kapısı ise denetçi raporlarından hesaplanır ve
    motor ikisinin AYNI koşuya ait olduğunu yapımda ölçer.

    Doğrulanmış çift yalnız `check_snapshot_agreement` tarafından kurulabilir;
    bu yol onu ATLAMAZ, raporları o kapıdan yeniden geçirir. `brief_doctor.run`
    saf bir fonksiyondur, yeniden koşması maliyet üretmez ve aynı baytlardan
    aynı raporu verir.
    """
    kok = runs.run_folder(run_id)
    _brief, kaynaklar, adlar = _kaynaklari_oku(kok)
    doktor = [
        brief_doctor.run(metin, source_name=ad)
        for metin, ad in zip(kaynaklar, adlar, strict=True)
    ]
    dogrulanmis = []
    for rol in auditors.DENETCI_ROLLERI:
        yol = kok / rol / auditors.RAPOR_DOSYA_KALIBI.format(rol)
        if not yol.is_file():
            raise CliError(f"denetçi raporu yok: {yol} — önce `denetim` koş")
        dogrulanmis.append(
            auditors.validate_report(
                yol.read_text(encoding="utf-8"),
                unit_snapshot=birimler,
                denetci=rol,
            )
        )
    anlasma = auditors.check_snapshot_agreement(
        tuple(dogrulanmis),
        expected_snapshot_sha=identity.canonical_sha(birimler),
        expected_kaynak_sha=brief_doctor.kaynak_seti_sha(doktor),
    )
    return doktor, anlasma


async def _kos_sentez(conn, args) -> Sonuc:
    """Sentez turunu koşturur ve sonucu MAKİNE-OKUNUR artefakt olarak yazar.

    Motor AYRI bir süreçte ve operatörün kör yargısından SONRA koşar (K-134);
    bu yüzden sonuç burada kalıcı katmana yazılır, elden verilmez.
    """
    satir = await _kosu_satiri(conn, args.run_id)
    aktif, birimler, _surum = await _aktif_paket(conn, satir["sector_id"])
    _doktor, anlasma = await _klasor_girdileri(conn, args.run_id, birimler)
    if not anlasma.gecerli:
        return ([f"mutabakat kapısı: {' · '.join(anlasma.errors)}"], RC_REFUSED)

    tur = auditors.AuditRound((anlasma.cift.birinci, anlasma.cift.ikinci), True, None)
    sonuc = await synthesis.run(
        conn,
        tur,
        run_id=args.run_id,
        active_package=aktif,
        removed_history=await _cikarma_gecmisi(conn, satir["sector_id"]),
        holiday_keys=set(await _takvim(conn)),
        runner=auditors.SubprocessRunner(zaman_asimi_sn=args.zaman_asimi_sn),
        dest=_kosu_klasoru_koku(),
    )
    await runs.record_artifact(
        conn,
        run_id=args.run_id,
        sector_slug=args.sektor_slug,
        kind=SENTEZ_ARTEFAKTI,
        source=runs.build_stamp(
            model=auditors.SENTEZ_ARACI,
            surum=args.arac_surumu,
            tarih=args.tarih,
            girdi_ozeti=anlasma.cift.unit_snapshot_sha,
        ),
        content_md=json.dumps(
            {
                "aday_json": identity.cozulmus(sonuc.aday_json),
                "karar_gunlugu": identity.cozulmus(sonuc.karar_gunlugu),
                "acik_sorular": list(sonuc.acik_sorular),
                "onay_ozeti": sonuc.onay_ozeti,
                "tasma": sonuc.tasma,
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )
    return (
        [
            f"run_id: {args.run_id}",
            f"acik_soru: {len(sonuc.acik_sorular)}",
            f"karar_satiri: {len(sonuc.karar_gunlugu)}",
            f"tasma: {'evet' if sonuc.tasma else 'hayir'}",
        ],
        RC_OK,
    )


async def _cikarma_gecmisi(conn, sector_id):
    """Son turların çıkarmaları — arşiv güvencesinin senteze giren ayağı."""
    satirlar = await conn.fetch(
        "SELECT decision_log FROM social.sector_packages "
        "WHERE sector_id = $1 AND status = 'archived' "
        "ORDER BY version DESC LIMIT 4",
        sector_id,
    )
    cikarmalar: list[dict] = []
    for satir in satirlar:
        for kayit in _coz(satir["decision_log"]) or []:
            if kayit.get("karar") in ("cikar", "kirp"):
                cikarmalar.append(kayit)
    return tuple(cikarmalar)


async def _takvim(conn) -> dict[str, str]:
    """Sistem özel günleri: NORMALİZE anahtar → kategori (boş olabilir).

    Normalizasyon kuralı KOPYALANMAZ: `sector_packages.normalize_special_day_key`
    tek kaynaktır ve taslak yazımı da onu kullanır. Erişilemez takvim
    FAIL-CLOSED'dır (K-112 (b)): doğrulanmamış anahtar hatta giremez.

    **Kategori 2026-09-11'de eklendi** — K-03'ün tür↔kategori ayağı motorda
    bununla çalışır (spec §11.2). Anahtar kümesi ile kategori eşlemesi AYNI
    sorgudan gelir: ikisi ayrı ayrı toplansaydı ayrışabilirlerdi ve motor
    kategorisi olmayan bir anahtarı "kategorisiz" mi yoksa "hiç yok" mu
    sayacağını bilemezdi.
    """
    try:
        satirlar = await conn.fetch(
            "SELECT name_tr, category FROM social.public_holidays "
            "WHERE name_tr IS NOT NULL"
        )
    except Exception as hata:  # noqa: BLE001 — K-112 (b)
        raise CliError(
            "sistem takvimi okunamadı — özel gün anahtarları doğrulanamaz"
        ) from hata
    takvim: dict[str, str] = {}
    for satir in satirlar:
        anahtar = sector_packages.normalize_special_day_key(satir["name_tr"])
        if anahtar:
            takvim[anahtar] = satir["category"] or ""
    return takvim


async def _kos_motor(conn, args) -> Sonuc:
    """Politika motorunu koşturur ve koşu sonucunu yazar (K-22=A).

    Girdiler kalıcı katmandan OKUNUR: sentez artefaktı, denetçi çifti, mekanik
    eleme ve otomatik kapılar. Motor `active`'e geçirme yetkisi TAŞIMAZ (K-28).
    """
    satir = await _kosu_satiri(conn, args.run_id)
    aktif, birimler, aktif_surum = await _aktif_paket(conn, satir["sector_id"])
    doktor, anlasma = await _klasor_girdileri(conn, args.run_id, birimler)
    if not anlasma.gecerli:
        return ([f"mutabakat kapısı: {' · '.join(anlasma.errors)}"], RC_REFUSED)

    ham = await conn.fetchval(
        "SELECT content_md FROM social.sector_research_artifacts "
        "WHERE run_id = $1 AND kind = $2 ORDER BY id DESC LIMIT 1",
        args.run_id,
        SENTEZ_ARTEFAKTI,
    )
    if ham is None:
        return (["sentez artefaktı yok — önce `sentez` koş"], RC_REFUSED)
    yuk = json.loads(ham)
    sentez = synthesis.SynthesisResult(
        aday_json=yuk["aday_json"],
        karar_gunlugu=tuple(yuk["karar_gunlugu"]),
        acik_sorular=tuple(yuk["acik_sorular"]),
        onay_ozeti=yuk["onay_ozeti"],
        tasma=yuk["tasma"],
    )

    tasdik = satir["katman1_attestation"]
    tasdik = _coz(tasdik) if tasdik is not None else None
    tek_aktif_ihlali = (
        await conn.fetchval(
            "SELECT count(*) FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'active'",
            satir["sector_id"],
        )
        > 1
    )
    takvim = await _takvim(conn)
    ayar = policy_config.PolicyConfig()
    if args.politika_ayari is not None:
        ayar = policy_config.PolicyConfig(
            **json.loads(args.politika_ayari.read_text(encoding="utf-8"))
        )

    girdiler = engine.EngineInputs(
        sentez=sentez,
        aktif_paket=aktif,
        aktif_schema_version=aktif_surum,
        aktif_birimler=birimler,
        mevcut_birim_sayisi=len(birimler),
        ilk_kosu=aktif is None,
        son_turlarin_cikarmalari=await _cikarma_gecmisi(conn, satir["sector_id"]),
        denetci_envanterleri=anlasma.cift,
        mekanik_eleme=brief_doctor.gate_round(doktor),
        takvim_anahtarlari=frozenset(takvim),
        takvim_kategorileri=takvim,
        otomatik_kapilar=engine.GateResults(
            katman1_passed=bool(tasdik and tasdik.get("sonuc") == "PASS"),
            tek_aktif_ihlali=tek_aktif_ihlali,
        ),
    )
    sonuc = engine.decide(girdiler, ayar)
    await runs.record_result(conn, run_id=args.run_id, result=sonuc)
    return (
        [f"run_id: {args.run_id}", f"sonuc: {sonuc.sonuc}"],
        RC_OK,
    )


async def _kos_yazim(conn, args) -> Sonuc:
    package_id = await writeback.write_draft_from_run(
        conn, run_id=args.run_id, actor=args.actor
    )
    return ([f"package_id: {package_id}"], RC_OK)


async def _kos_duzeltme_yaz(conn, args) -> Sonuc:
    await writeback.update_draft_from_run(
        conn, run_id=args.run_id, actor=args.actor
    )
    return ([f"run_id: {args.run_id}", "taslak: yerinde guncellendi"], RC_OK)


async def _kos_katman1(conn, args) -> Sonuc:
    await runs.attest_katman1(
        conn,
        run_id=args.run_id,
        kosum_kimligi=args.kosum_kimligi,
        sonuc=args.sonuc,
        actor=args.actor,
    )
    return ([f"katman1: {args.sonuc}", f"kosum: {args.kosum_kimligi}"], RC_OK)


async def _kos_katman2(conn, args) -> Sonuc:
    """Katman-2 KAPI DEĞİLDİR: koşulduğu ve SUNULDUĞU tasdiklenir, sonucu değil."""
    await runs.attest_katman2(
        conn,
        run_id=args.run_id,
        kosum_kimligi=args.kosum_kimligi,
        ozet=args.ozet,
        actor=args.actor,
    )
    return (
        ["katman2: kosuldu+sunuldu", f"kosum: {args.kosum_kimligi}"],
        RC_OK,
    )


async def _kos_hazirlik_onayla(conn, args) -> Sonuc:
    """İşletime hazırlık listesi — K-69 kapısı, K-70 TEK onay.

    Bayraksız çağrı YALNIZ rapordur: ön-kontrol kendi kendini onaylamaz.
    `--onayla` verildiğinde önce otomatik ölçümü DÜŞEN kapı maddeleri aranır;
    bir tanesi bile varsa tasdik YAZILMAZ (fail-closed) — operatör yanlış
    zemine imza atmış olurdu.

    `onaylandi` burada ÜRETİLMEZ: `runs.attest_readiness` onu kapı kümesinden
    TÜRETİR. Komut yalnız kimlik kümesini ve aktörü taşır.

    **DEĞERLENDİRME ve YAZIM TEK İŞLEMDE, koşu satırı KİLİTLİ** (hakem turu 1,
    yüksek). Ayrı autocommit ifadeleriyken iki operatör aynı anda onaylayabilir
    ve değerlendirme ile yazım arasında koşu satırı değişebilirdi; yazılan
    tasdik o an ARTIK DOĞRU OLMAYAN bir değerlendirmeyi belgelerdi.
    """
    async with conn.transaction():
        kilit = await conn.fetchval(
            "SELECT run_id FROM social.sector_package_runs WHERE run_id = $1 "
            "FOR UPDATE",
            args.run_id,
        )
        if kilit is None:
            raise runs.RunNotVerified(f"koşu satırı yok: {args.run_id!r}")

        rapor = await readiness.evaluate(conn, run_id=args.run_id)
        satirlar = [
            f"{satir.madde_id} [{satir.sinif}/{satir.olcum}] {satir.durum}: "
            f"{satir.baslik} — {satir.detay}"
            for satir in rapor.satirlar
        ]
        bloklayan = rapor.bloklayan_kapi_maddeleri
        satirlar.append(
            "bloklayan kapi maddeleri: "
            + (" · ".join(bloklayan) if bloklayan else "yok")
        )
        satirlar.append(
            "elle beyan bekleyen maddeler: "
            + (" · ".join(rapor.elle_bekleyen_maddeler) or "yok")
        )

        if not args.onayla:
            satirlar.append("onay YAZILMADI — yazmak icin --onayla")
            return (satirlar, RC_OK)

        if bloklayan:
            satirlar.append(
                "onay REDDEDILDI — otomatik olcumu dusen kapi maddesi var: "
                + " · ".join(bloklayan)
            )
            return (satirlar, RC_REFUSED)

        taze = await readiness.kanit_parmakizi(conn, run_id=args.run_id)
        if taze != rapor.kanit_parmakizi:
            # Degerlendirmeden sonra kanit kumesi DEGISTI: yazilacak tasdik artik
            # dogru olmayan bir olcumu belgelerdi (hakem turu 2, F1).
            satirlar.append(
                "onay REDDEDILDI — degerlendirmeden SONRA kanit kumesi degisti; "
                "komutu yeniden kosun"
            )
            return (satirlar, RC_REFUSED)

        await runs.attest_readiness(
            conn,
            run_id=args.run_id,
            kapi_maddeleri=tuple(sorted(readiness_items.KAPI_MADDELERI)),
            sinyal_maddeleri=tuple(sorted(readiness_items.SINYAL_MADDELERI)),
            actor=args.actor,
        )
        satirlar.append("hazirlik tasdiki: yazildi")
        return (satirlar, RC_OK)


async def _kos_onay(conn, args) -> Sonuc:
    """Kararsız çağrı görüntüyü DONDURUR ve özeti basar; kararlı çağrı kaydeder.

    İki adım bilinçlidir: operatör kararını, onayladığı baytların hash'ine
    bağlar. `--snapshot-sha` geri verilmeden karar yazılmaz.
    """
    if args.karar is None:
        await approval.build_and_freeze_from_run(
            conn, run_id=args.run_id, actor=args.actor
        )
        satir = await conn.fetchrow(
            "SELECT approval_snapshot, snapshot_sha FROM social.sector_package_runs "
            "WHERE run_id = $1",
            args.run_id,
        )
        goruntu = satir["approval_snapshot"]
        satirlar = [f"snapshot_sha: {satir['snapshot_sha']}"]
        satirlar += approval.render_summary(goruntu).splitlines()
        satirlar += approval.render_removals_detail(goruntu).splitlines()
        satirlar.append("karar YAZILMADI — --karar ve --snapshot-sha ile tekrar çağır")
        return (satirlar, RC_OK)

    if args.saniye is None or args.snapshot_sha is None:
        return (
            ["--karar verildiğinde --saniye ve --snapshot-sha de ZORUNLUDUR"],
            RC_USAGE,
        )
    await approval.record_decision(
        conn,
        run_id=args.run_id,
        karar=args.karar,
        actor=args.actor,
        seconds=args.saniye,
        snapshot_sha=args.snapshot_sha,
    )
    return ([f"karar: {args.karar}", f"run_id: {args.run_id}"], RC_OK)


async def _kos_aktive_et(conn, args) -> Sonuc:
    try:
        await writeback.activate_from_snapshot(
            conn, run_id=args.run_id, actor=args.actor
        )
    except lifecycle.GateNotSatisfied as hata:
        if "checklist_approved" not in str(hata):
            raise
        # F1 (Eray karari, 2026-09-11): kapi "dursun ve YENIDEN ONAY ISTESIN"
        # diye kuruldu. `checklist_approved` tek basina IKI ayri sebebi
        # ortuyor -- tasdik hic yok/eksik madde VEYA onaydan sonra kanit
        # degisti. Operatore hangisi oldugu SOYLENMEZSE karar yarim kalir:
        # "kapi kapali" der ama ne yapacagini soylemez.
        tasdik = await conn.fetchval(
            "SELECT readiness_attestation FROM social.sector_package_runs "
            "WHERE run_id = $1",
            args.run_id,
        )
        yazili = (tasdik or {}).get("kanit_parmakizi")
        taze = await runs.kanit_parmakizi(conn, run_id=args.run_id)
        if yazili is not None and yazili != taze:
            return (
                [
                    f"run_id: {args.run_id}",
                    "aktivasyon REDDEDILDI — hazirlik onayindan SONRA kanit "
                    "kumesi degisti",
                    "yapilacak: `hazirlik-onayla` komutunu YENIDEN kosun",
                ],
                RC_REFUSED,
            )
        raise
    return ([f"run_id: {args.run_id}", "paket: aktive edildi"], RC_OK)


async def _kos_deaktive_et(conn, args) -> Sonuc:
    await lifecycle.deactivate_package(
        conn, package_id=args.package_id, actor=args.actor
    )
    return ([f"package_id: {args.package_id}", "paket: deaktive edildi"], RC_OK)


# ─── K-145 olay zinciri ─────────────────────────────────────────────────────


async def _etkilenen_kume(conn, args):
    """Kural sürümünü adlandıran DÖRTLÜDEN etkilenen kümeyi kurar."""
    return await runs.affected_packages(
        conn,
        engine_version=args.engine_version,
        engine_config_sha=args.engine_config_sha,
        kural_kimligi=args.kural_kimligi,
        kural_surumu=args.kural_surumu,
    )


def _kume_raporu(kume) -> list[str]:
    """Deterministik küme raporu — sıralı kimlikler, zaman damgası YOK.

    `genisletildi` AÇIKÇA basılır: ayrım yapılamadığında davranış koşulsuz
    toplu geri almayla aynıdır ve operatörün bunu raporda GÖRMESİ gerekir.
    """
    satirlar = [
        f"engine_version: {kume.engine_version}",
        f"kural: {kume.kural_kimligi}@{kume.kural_surumu}",
        f"aday_kume: {len(kume.aday_kume)}",
        f"genisletildi: {'evet' if kume.genisletildi else 'hayir'}",
        f"geri_alinacak: {len(kume.geri_alinacaklar)}",
    ]
    for sinif in ("kanitli", "kanitli_etkilenmemis", "ayrilamaz"):
        kimlikler = sorted(str(pid) for pid in getattr(kume, sinif))
        satirlar.append(f"{sinif}: {len(kimlikler)}")
        satirlar += [f"  - {pid}" for pid in kimlikler]
    satirlar.append("geri_alinacaklar:")
    satirlar += [f"  - {pid}" for pid in sorted(str(p) for p in kume.geri_alinacaklar)]
    return satirlar


async def _kos_etki_analizi(conn, args) -> Sonuc:
    return (_kume_raporu(await _etkilenen_kume(conn, args)), RC_OK)


async def _kos_olay_plani(conn, args) -> Sonuc:
    """`--incident-id` YOKSA olay AÇAR, VARSA üyeliği DEĞİŞTİRİR (AÇIK-1/A1(a)).

    İkinci bir alt komut adı AÇILMAZ: R10'un "her operatör adımının CLI girişi
    olur" hükmü bu parametreyle karşılanır.
    """
    kume = await _etkilenen_kume(conn, args)
    if args.incident_id is None:
        incident_id = await runs.build_rollback_plan(
            conn, affected=kume, actor=args.actor
        )
        return (
            [f"incident_id: {incident_id}", *_kume_raporu(kume)],
            RC_OK,
        )

    eklenen, daraltilan = await runs.amend_rollback_plan(
        conn, incident_id=args.incident_id, affected=kume, actor=args.actor
    )
    return (
        [
            f"incident_id: {args.incident_id}",
            f"eklenen: {eklenen}",
            f"daraltilan: {daraltilan}",
            *_kume_raporu(kume),
        ],
        RC_OK,
    )


async def _kos_olay_onayla(conn, args) -> Sonuc:
    damgalanan = await runs.approve_incident_rollback(
        conn, incident_id=args.incident_id, actor=args.actor
    )
    if damgalanan == 0:
        # Sıfır satır damgalamak "onaylandı" DEĞİLDİR: bilinmeyen olay, tamamen
        # onaylanmış olay ve bekleyen satırı olmayan olay aynı sonucu verir ve
        # otomasyon onayın gerçekleştiğini sanıp sonraki adıma geçerdi.
        return (
            [
                f"incident_id: {args.incident_id}",
                "damgalanan: 0 — bekleyen satır yok; onay YAZILMADI",
            ],
            RC_REFUSED,
        )
    return (
        [f"incident_id: {args.incident_id}", f"damgalanan: {damgalanan}"],
        RC_OK,
    )


def _yurutme_raporu(rapor) -> tuple[list[str], int]:
    """`hedefsiz` ve `hata` AYRI BAŞLIK altında; sessizce başarı sayılmazlar.

    Çıkış kodu bunu izler: yalnız tamamlanan ve zaten-tamamlanan satırlar varsa
    `RC_OK`; bir tek `hedefsiz` ya da `hata` satırı bile rc≠0 üretir. Operatörün
    ekranda göreceği "bitti" ile kabuğun gördüğü kod AYRIŞMAZ.
    """
    satirlar = [f"incident_id: {rapor.incident_id}"]
    for baslik in ("tamamlandi", "zaten_tamamlandi", "hedefsiz", "hata"):
        kimlikler = sorted(str(pid) for pid in getattr(rapor, baslik))
        satirlar.append(f"{baslik}: {len(kimlikler)}")
        satirlar += [f"  - {pid}" for pid in kimlikler]
    if rapor.sebepler:
        satirlar.append("sebepler:")
        satirlar += [
            f"  - {anahtar}: {rapor.sebepler[anahtar]}"
            for anahtar in sorted(rapor.sebepler)
        ]
    if rapor.hedefsiz:
        satirlar.append(
            "NOT: `hedefsiz` satırların TEK çıkışı `deaktive-et`'tir — bu komut "
            "onları kendiliğinden indirmez (K-38)."
        )
    rc = RC_OK if not (rapor.hedefsiz or rapor.hata) else RC_REFUSED
    return satirlar, rc


async def _kos_olay_geri_al(conn, args) -> Sonuc:
    rapor = await runs.execute_rollback_plan(
        conn, incident_id=args.incident_id, actor=args.actor
    )
    return _yurutme_raporu(rapor)


# `geri-al` alt komutu YOKTUR — KALDIRILDI (Eray kararı, 2026-09-11).
#
# Arayüz eki AÇIK-2 üç seçenek arasından **A**'yı seçmişti: komut kalsın, yalnız
# olay kimliği istesin. Uygulamada o seçenek kapanmadı. Ölçüldü (hakem turu 13
# + kapanış turu): komut olayın üyeliğini doğruladıktan SONRA, paket filtresi
# ALMAYAN olay-kapsamlı yürütücüyü çağırıyor; doğrulama ile yürütmenin kilidi
# arasında bir pencere kalıyor ve o pencerede üyeliği değiştiren ikinci bir
# operatör, adlandırılmayan paketin geri alınmasına yol açabiliyor.
#
# Pencereyi kapatmak, olay kilidini baştan sona tutan PAKET-HEDEFLİ bir
# yürütücü ister; o yüzey servis katmanındadır ve bu görevin beyan ettiği dosya
# kümesinin DIŞINDADIR. Kullanıcı kararı: komutu kapat, olay yolunu tek yol yap.
#
# **Yetenek kaybolmuyor:** tek paketlik geri alma da `olay-plani` ile tek
# satırlık bir olay açılarak yapılır; `olay-onayla` ve `olay-geri-al` aynen
# koşar. Kaybolan şey kısayoldur, kanıt zinciri değil.
#
# **AÇIK-2 METNİ HÂLÂ "A" DİYOR** — arayüz eki bu kararla ıraksadı ve
# düzeltilmesi tasarım katmanının işidir; yürütücü bağlayıcı eki kendi başına
# yeniden yazmaz.


# ─── K-26 vade bildirimi + salt-okunur görünüm ──────────────────────────────


async def _kos_vade_bildirimi(conn, args) -> Sonuc:
    """Periyodu dolan her aktif paket için yönetici bildirimi yazar (K-26).

    Elle vade takibi kalmaz. `idempotency_key` paket kimliği ve aktivasyon anını
    taşır: aynı sürüm için ikinci bir satır doğmaz, komut güvenle tekrar koşar.
    """
    satirlar = await conn.fetch(
        "SELECT p.id, p.sector_id, p.version, p.activated_at "
        "FROM social.sector_packages AS p "
        "WHERE p.status = 'active' AND p.activated_at IS NOT NULL "
        f"  AND p.activated_at < now() - interval '{VADE_AYI} months' "
        "ORDER BY p.id"
    )
    rapor = [f"vade_ayi: {VADE_AYI}", f"vadesi_dolan: {len(satirlar)}"]
    for satir in satirlar:
        await notifications.record_admin_event(
            conn,
            kind=VADE_OLAYI,
            payload={
                "package_id": str(satir["id"]),
                "sector_id": str(satir["sector_id"]),
                "version": satir["version"],
                "vade_ayi": VADE_AYI,
            },
            idempotency_key=f"vade:{satir['id']}:{satir['activated_at'].isoformat()}",
        )
        rapor.append(f"  - {satir['id']} v{satir['version']}")
    return (rapor, RC_OK)


async def _kos_durum(conn, args) -> Sonuc:
    """Koşunun SALT-OKUNUR görünümü — yazma yok, koşu başlatmaz."""
    satir = await conn.fetchrow(
        "SELECT run_id, sector_id, package_id, kosu_turu, durum, sonuc, "
        "       katman1_attestation IS NOT NULL AS katman1_var, "
        "       katman2_attestation IS NOT NULL AS katman2_var, "
        "       approval_karar, snapshot_sha "
        "FROM social.sector_package_runs WHERE run_id = $1",
        args.run_id,
    )
    if satir is None:
        return ([f"koşu yok: {args.run_id}"], RC_REFUSED)
    return ([f"{ad}: {satir[ad]}" for ad in satir.keys()], RC_OK)


# ─── Bağlama ────────────────────────────────────────────────────────────────

GOVDELER = {
    "tur-ac": _kos_tur_ac,
    "duzeltme-baslat": _kos_duzeltme_baslat,
    "brief-doctor": _kos_brief_doctor,
    "denetim": _kos_denetim,
    "sentez": _kos_sentez,
    "motor": _kos_motor,
    "yazim": _kos_yazim,
    "duzeltme-yaz": _kos_duzeltme_yaz,
    "katman1": _kos_katman1,
    "katman2": _kos_katman2,
    "hazirlik-onayla": _kos_hazirlik_onayla,
    "onay": _kos_onay,
    "aktive-et": _kos_aktive_et,
    "deaktive-et": _kos_deaktive_et,
    "etki-analizi": _kos_etki_analizi,
    "olay-plani": _kos_olay_plani,
    "olay-onayla": _kos_olay_onayla,
    "olay-geri-al": _kos_olay_geri_al,
    "vade-bildirimi": _kos_vade_bildirimi,
    "durum": _kos_durum,
}
"""Alt komut → gövde. Ayrıştırıcıdaki küme ile BİREBİR aynı olmak zorundadır."""

ALAN_HATALARI: tuple[type[BaseException], ...] = (
    runs.RunNotVerified,
    runs.CorrectionRunRefused,
    runs.ArtifactStampMissing,
    runs.RollbackEvidenceUnavailable,
    runs.ReadinessAttestationRefused,
    lifecycle.LifecycleError,
    lifecycle.GateNotSatisfied,
    lifecycle.CalendarUnavailable,
    lifecycle.EvidenceMintRefused,
    lifecycle.EvidenceProvenanceInvalid,
    writeback.WritebackRefused,
    writeback.ActivationRefused,
    approval.ApprovalRefused,
    synthesis.SynthesisFailed,
    engine.EngineInputError,
    ValueError,
)
"""ALAN kuralının reddi — `RC_REFUSED`. Altyapı hatası bu kümeye GİRMEZ.

Ayrım operatör içindir: `RC_REFUSED` "kural izin vermedi, girdiyi düzelt"
demektir; `RC_USAGE` "ortam/çağrı bozuk, başka yere bak" demektir. Tek kod
kullanılsaydı operatör her iki durumda da yanlış yere bakardı.

`ValueError` kümededir çünkü kanonik kimlik kapısı (`require_actor`) boş aktörü
onunla reddeder — kapının TÜRÜ değil, davranışı sözleşmedir.
"""


async def dispatch(conn, args) -> Sonuc:
    """Ayrıştırılmış argümanı gövdesine bağlar; bağlantıyı AÇMAZ.

    Testler bu yüzeyi doğrudan çağırır: kendi işlemlerindeki bağlantıyı verip
    gövdeyi ölçerler, ikinci bir veritabanı oturumu açılmaz.
    """
    try:
        govde = GOVDELER[args.komut]
    except KeyError:  # pragma: no cover — ayrıştırıcı kapalı kümeyi zaten zorlar
        raise CliError(f"tanınmayan alt komut: {args.komut!r}") from None

    try:
        return await govde(conn, args)
    except runs.IncidentMembershipLocked as hata:
        # SIRA BAĞLAYICI: `RuntimeError` alt sınıfı olduğu için genel alan
        # dalından ÖNCE yakalanır; kendi çıkış kodunu taşır (AÇIK-1/A3).
        return ([f"olay üyeliği kilitli: {hata}"], RC_LOCKED)
    except ALAN_HATALARI as hata:
        return ([f"{type(hata).__name__}: {hata}"], RC_REFUSED)


def require_contract_pin() -> None:
    """Pin kapısı — sürüklenmede `ContractDriftError` fırlatır.

    Ayrı bir fonksiyon olmasının sebebi ölçülebilirliktir: kapının koştuğu
    testlerde bu yüzey tek noktadan gözlenir.
    """
    contracts.require_pin(PIN_PATH, PIN_DEPO_KOKU)


async def _baglan_ve_kos(args, dsn: str) -> Sonuc:
    connection = await asyncpg.connect(dsn)
    try:
        return await dispatch(connection, args)
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # SIRA BAĞLAYICI: pin kapısı BAĞLANTIDAN ÖNCE. Sürüklenmiş sözleşmeyle
    # açılmış bir oturum bile istenmez; kapı ayrıca veritabanına erişimi
    # olmayan bir ortamda da ölçülebilir kalır.
    if args.komut in RUN_SUBCOMMANDS:
        try:
            require_contract_pin()
        except contracts.ContractDriftError as exc:
            sys.stderr.write(f"sözleşme pini sürüklenmiş — koşu başlamadı: {exc}\n")
            return RC_USAGE

    # DSN kanalı pin kapısından SONRA çözülür: sürüklenmiş sözleşmede sırrı hiç
    # okumaya gerek yok, koşu zaten başlamayacak.
    dsn = dsn_coz(args, parser)

    try:
        satirlar, rc = asyncio.run(_baglan_ve_kos(args, dsn))
    except CliError as exc:
        sys.stderr.write(f"{exc}\n")
        return RC_REFUSED
    except Exception as exc:  # noqa: BLE001 — ham metin BASILMAZ (parola sızabilir)
        sys.stderr.write(f"komut koşulamadı ({type(exc).__name__})\n")
        return RC_USAGE

    for satir in satirlar:
        sys.stdout.write(f"{satir}\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
