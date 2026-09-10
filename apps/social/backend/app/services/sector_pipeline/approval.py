"""Onay yüzeyi (Plan 2 Task 14) — değişmez anlık görüntü · sinyal sıralaması.

Üç sözleşme bu modülde pinlidir:

1. **F18 — anlık görüntü ÇAĞIRANDAN alınmaz, BASILIR.** `build_and_freeze_from_run`
   içeriği KİLİTLİ KOŞU SATIRINDAN ve sektörün önceki koşu satırlarından okur.
   Çağıranın kurduğu bir görüntüyü kabul eden yol YOKTUR: olsaydı bir görüntü
   üzerinden onay alıp başka bir koşuyu aktive etmek mümkün olurdu.

   **Taslak satırı OKUNMAZ ve K-94 taban durumu görüntüye YAZILMAZ.** Planın
   Task 14 metni ikisini de sayıyordu; ölçüldü ki gerek yok ve zararlı olurdu:
   aktivasyon kanıtını Task 15 kilitli satırlardan KENDİSİ türetir (arayüz eki
   R8), aynı gerçeği görüntüye de yazmak onu iki kaynaklı yapardı (R2'nin
   yasakladığı desen) ve ikisi ayrışabilirdi. Spec §9.6'nın ekran listesinde de
   taban durumu YOKTUR — orada K-94, aktivasyon anının kuralı olarak durur.
   Görüntüden okunan tek paket bağı `package_id`'dir ve onu `record_decision`
   OLAY için kullanır (R3).
2. **K-98 — görüntü DEĞİŞMEZDİR.** İlk yazım serbesttir, ikincisi veritabanı
   tetikleyicisiyle reddedilir; bu modül dolu bir görüntüyü EZMEYE ÇALIŞMAZ,
   olanı döner (fikirsiz tekrar = aynı sonuç).
3. **K-42 — riskli sınıflar nötr sayıların ÖNÜNDE.** Sıra sabittir ve test
   edilir; eşik YOKTUR (İlke 9: ölçülmemiş sayı kapı yapılmaz).

**Bu modülde `ActivationGateEvidence` KURULMAZ, import bile edilmez** (arayüz eki
R8). Planın `to_activation_evidence` kalemi SİLİNDİ: çağıranın verdiği sözlükten
kanıt üreten ikinci bir kurucu, "kanıt veritabanından okunur" doktrininde açılan
deliğin kendisiydi. Kanıtın tek kurulum yeri aktivasyon yolunun içidir (Task 15).
"""

from __future__ import annotations

from typing import Any, Mapping

from ..package_events import log_package_event
from . import identity, runs

KARARLAR: tuple[str, ...] = ("onay", "ret")
"""Onay kararları — KAPALI küme (036 CHECK'iyle birebir)."""

SNAPSHOT_SEMA: int = 1
"""Görüntü şeması sürümü — okuyucu bilinmeyen şemada DURUR."""


class ApprovalRefused(RuntimeError):
    """Onay yüzeyi çalışmayı reddetti (fail-closed)."""


def _kapi_sonuclari(run: runs.VerifiedRun) -> dict:
    """İki kapı tasdikinin GÖRÜNTÜ temsili — kilitli satırdan okunur.

    Katman-2'nin SONUCU kapı DEĞİLDİR (spec §10.2): koşulmuş ve sunulmuş olması
    ön koşuldur, sonucu okunmaz. Bu yüzden görüntü ona "PASS/FAIL" YAZMAZ —
    yazsaydı okunmayan bir sonucu kapıymış gibi gösterirdi.
    """
    for ad, tasdik in (
        ("katman1", run.katman1_attestation),
        ("katman2", run.katman2_attestation),
    ):
        if tasdik is None:
            raise ApprovalRefused(
                f"{ad} tasdiki YOK — kapı sonucu uydurulmaz. Yedi kapı tasdikleri "
                "KAPSAMAZ: koşu doğrulanmış olsa da bu kapı hiç koşmamış olabilir"
            )
    return {
        "katman1": run.katman1_attestation["sonuc"],
        "katman2": {"sunuldu": run.katman2_attestation["sunuldu"]},
    }


RISKLI_ATIF_GERI_EKLEME = "geri_ekleme_celiskisi"
"""Geri-ekleme çelişkisini üreten kontrolün ADI (`BulguIzi.kontrol`).

Sınıf `acik_soru`'dur ve onu BEŞ ayrı kontrol üretir; ayrım ATIFTAN yapılır.
`detay` metnini eşleştirmek referans bütünlüğü olmayan bir bağ olurdu (İlke 1).
"""


def _cikarmalar(run: runs.VerifiedRun) -> dict:
    """K-41 — sayı + tam liste. EŞİK YOKTUR.

    Kalem METNİ taşınmaz: yönetici kalıp listesi görmez (spec §9.6). Taşınan
    şey kimlik · alan · öğe yolu · gerekçedir.
    """
    kalemler = [
        {
            "unit_id": satir["unit_id"],
            "alan": satir["alan"],
            "oge_yolu": satir["oge_yolu"],
            "gerekce": satir["gerekce"],
        }
        for satir in run.final_decision_log
        if satir.get("karar") == "cikar"
    ]
    return {"sayi": len(kalemler), "kalemler": kalemler}


def _sayilar(run: runs.VerifiedRun) -> dict:
    """Alan-bazlı + toplam — karar günlüğünden TÜRETİLİR."""
    alan_bazli: dict[str, int] = {}
    for satir in run.final_decision_log:
        alan = satir.get("alan")
        if alan is None:
            continue
        alan_bazli[alan] = alan_bazli.get(alan, 0) + 1
    return {"alan_bazli": alan_bazli, "toplam": sum(alan_bazli.values())}


def _bulgu_ayrimi(run: runs.VerifiedRun) -> tuple[list[dict], list[dict]]:
    """Bulguları ATFA göre ikiye ayırır: geri-ekleme çelişkileri · uyarılar."""
    geri_ekleme: list[dict] = []
    uyarilar: list[dict] = []
    for bulgu in run.policy_report["bulgular"]:
        # FAIL-CLOSED: atfı OLMAYAN bulgu ayrıştırılamaz. `.get(...) == ...`
        # ile geçiştirmek, atfı olmayan bir geri-ekleme çelişkisini sessizce
        # NÖTR "uyarı"ya düşürürdü — riskli sınıfın sessiz kaybı. Atıf
        # `run_checks` damgasıdır; taşımayan satır bu şemadan ESKİdir.
        if "kontrol" not in bulgu:
            raise ApprovalRefused(
                f"bulgu atıf TAŞIMIYOR (sınıf={bulgu.get('sinif')!r}) — riskli "
                "sınıf ayrımı yapılamaz; bu koşu atıf damgasından ÖNCEKİ şemayla "
                "yazılmış, görüntü sınıf uydurmaz"
            )
        if bulgu["kontrol"] == RISKLI_ATIF_GERI_EKLEME:
            geri_ekleme.append(
                {"unit_id": bulgu["unit_id"], "detay": bulgu["detay"]}
            )
            continue
        uyarilar.append(
            {
                "sinif": bulgu["sinif"],
                "unit_id": bulgu["unit_id"],
                "detay": bulgu["detay"],
            }
        )
    return geri_ekleme, uyarilar


async def _son_dort_tur(db, *, sector_id, run_id: str) -> list[dict]:
    """Sektörün SON DÖRT tamamlanmış turunun çıkarma özeti (bu tur HARİÇ).

    Soru çağırana sorulmaz, koşu tablosundan okunur (F18). Kendi turu sayılmaz:
    özet "önceki turlarda ne çıkarıldı" sorusuna cevaptır.

    **Sıralamanın ÖLÇÜLMÜŞ sınırı:** `created_at` transaction zaman damgasıdır
    (`now()`), yani AYNI transaction'da açılan koşular onu PAYLAŞIR. Üretimde
    her koşu kendi transaction'ındadır ve sıra doğrudur; eşitlik hâlinde sıra
    `run_id` ile deterministik kılınır — anlamlı bir sıra DEĞİL, yalnız keyfi
    olmayan bir sıradır. Bu ayrım testte de kurulur (eşit damgayla değil, AYRI
    damgalarla ölçülür).
    """
    satirlar = await db.fetch(
        "SELECT run_id, final_decision_log FROM social.sector_package_runs "
        "WHERE sector_id = $1 AND run_id <> $2 AND durum = 'tamamlandi' "
        "AND final_decision_log IS NOT NULL "
        "ORDER BY created_at DESC, run_id DESC LIMIT 4",
        sector_id,
        run_id,
    )
    return [
        {
            "run_id": satir["run_id"],
            "sayi": sum(
                1 for kayit in satir["final_decision_log"]
                if kayit.get("karar") == "cikar"
            ),
        }
        for satir in satirlar
    ]


async def build_and_freeze_from_run(db, *, run_id: str, actor: str) -> dict:
    """Görüntüyü kilitli koşudan BASAR ve aynı işlemde DONDURUR (F18/K-98).

    Çağıranın kurduğu bir görüntüyü kabul eden parametre YOKTUR: olsaydı bir
    görüntü üzerinden onay alıp başka bir koşuyu aktive etmek mümkün olurdu.
    """
    run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
    acik_sorular = list(run.policy_report["acik_soru_kimlikleri"])
    geri_ekleme, uyarilar = _bulgu_ayrimi(run)
    goruntu: dict[str, Any] = {
        "sema": SNAPSHOT_SEMA,
        "run_id": run.run_id,
        "sonuc": run.sonuc,
        "sebep": run.sebep,
        "actor": actor,
        "icerik_hashleri": {
            "content_sha": run.content_sha,
            "decision_log_sha": run.decision_log_sha,
        },
        "acik_sorular": acik_sorular,
        # K-71: açık soru varsa onaylanabilir sonuç SUNULMAZ. Motor böyle bir
        # koşuyu zaten `blocked` yapar; bu İKİNCİ katmandır.
        "onaylanabilir": run.sonuc == "activation_eligible" and not acik_sorular,
        "geri_ekleme_celiskileri": geri_ekleme,
        "kararsizlar": [
            {"unit_id": madde["unit_id"], "sebep": madde["sebep"]}
            for madde in run.policy_report["kararsizlar"]
        ],
        "cikarmalar": _cikarmalar(run),
        "son_dort_tur_cikarmalari": await _son_dort_tur(
            db, sector_id=run.sector_id, run_id=run.run_id
        ),
        "sayilar": _sayilar(run),
        "oranlar": identity.cozulmus(run.barrier_report.get("oranlar", {})),
        "uyarilar": uyarilar,
        "kapi_sonuclari": _kapi_sonuclari(run),
        "motor_kosu_raporu": {
            "engine_version": run.engine_version,
            "engine_config_sha": run.engine_config_sha,
            "barrier_report": identity.cozulmus(run.barrier_report),
        },
    }
    return await _dondur(db, run_id=run.run_id, goruntu=goruntu)


async def _dondur(db, *, run_id: str, goruntu: dict) -> dict:
    """İLK yazım serbesttir; dolu satırda OLAN görüntü döner (K-98).

    Dolu görüntüyü EZMEYE ÇALIŞMAK yanlış olurdu: tetikleyici onu zaten
    reddeder, ama denemenin KENDİSİ çağıranın transaction'ını abort ederdi
    (ölçüldü). Fikirsiz tekrar aynı sonucu vermelidir.
    """
    sha = identity.canonical_sha(goruntu)
    yazildi = await db.fetchval(
        "UPDATE social.sector_package_runs "
        "SET approval_snapshot = $2, snapshot_sha = $3 "
        "WHERE run_id = $1 AND approval_snapshot IS NULL "
        "RETURNING id",
        run_id,
        goruntu,
        sha,
    )
    if yazildi is not None:
        return goruntu
    mevcut = await db.fetchval(
        "SELECT approval_snapshot FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    return dict(mevcut)


async def record_decision(
    db,
    *,
    run_id: str,
    karar: str,
    actor: str,
    seconds: int,
    snapshot_sha: str,
) -> None:
    """Kararı DONDURULMUŞ görüntünün hash'ine bağlar ve olayı yazar (F18/R3).

    İmzada çağıran-taraflı `package_id`/`sector_id` YOKTUR: olay paket kimliğini
    TAŞIR ama onu KİLİTLİ KOŞUDAN okur. Çağıranın verdiği bir paket kimliği
    koşununkiyle çelişebilirdi ve TEK KAPI doktrini bunu yasaklar.
    """
    if karar not in KARARLAR:
        raise ApprovalRefused(
            f"karar kapalı kümenin dışında: {karar!r} — kabul edilenler: "
            f"{list(KARARLAR)}"
        )
    run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
    if run.package_id is None:
        raise ApprovalRefused(
            f"koşu {run_id!r} bir paket taslağına bağlı DEĞİL — yaşam döngüsü "
            "olayı paket kimliği ister (R3); onay yazılamadan patlardı"
        )
    if not run.snapshot_sha:
        raise ApprovalRefused(
            f"koşu {run_id!r} için dondurulmuş görüntü YOK — karar bağlanacağı "
            "hash'i olmayan bir görüntüye verilemez"
        )
    if snapshot_sha != run.snapshot_sha:
        raise ApprovalRefused(
            "karar BAŞKA bir görüntüye ait: verilen hash "
            f"{snapshot_sha!r}, satırdaki {run.snapshot_sha!r} — onay yalnız "
            "gösterilen görüntüye verilir (F18)"
        )

    yazildi = await db.fetchval(
        "UPDATE social.sector_package_runs "
        "SET approval_karar = $2, approval_seconds = $3, approved_at = now() "
        "WHERE run_id = $1 AND approval_karar IS NULL "
        "RETURNING id",
        run_id,
        karar,
        seconds,
    )
    if yazildi is None:
        raise ApprovalRefused(
            f"koşu {run_id!r} için karar ZATEN verilmiş — ikinci karar yazılmaz"
        )
    await log_package_event(
        db,
        event_type="approval" if karar == "onay" else "rejection",
        sector_id=run.sector_id,
        package_id=run.package_id,
        actor=actor,
        detail={"run_id": run_id, "seconds": seconds, "snapshot_sha": snapshot_sha},
    )


# ─── Gösterim ───────────────────────────────────────────────────────────────
#
# K-42 SIRASI BAĞLAYICIDIR: riskli sınıflar nötr sayıların ÖNÜNDE ve kendi
# içlerinde sabit sırada. Sıra bir görsel tercih değil, sinyal-odaklı diff
# tasarımının kendisidir — nötr sayılar önce gelseydi riskli sinyal, göz
# gezdiren bir okuyucu için gürültünün arkasına düşerdi.

RISKLI_SIRA: tuple[str, ...] = (
    "Geri-ekleme çelişkileri",
    "Motor kararsızları",
    "Çıkarılanlar",
)
NOTR_SIRA: tuple[str, ...] = (
    "Alan bazlı sayılar",
    "Değişim oranları",
    "İçerik hash'leri",
)


def _sema_kapisi(snapshot: Mapping[str, Any]) -> None:
    """Bilinmeyen şemada DURUR — iki gösterici için TEK kapı.

    İki kopya, sürüm sürüm ayrışan iki kural demekti; kapı tek yerde yaşar.
    """
    if snapshot.get("sema") != SNAPSHOT_SEMA:
        raise ApprovalRefused(
            f"bilinmeyen görüntü şeması: {snapshot.get('sema')!r} — okunmaz"
        )


def _satirlar(baslik: str, kalemler: list) -> list[str]:
    if not kalemler:
        return [f"{baslik}: yok"]
    return [f"{baslik}: {len(kalemler)}"] + [f"  - {kalem}" for kalem in kalemler]


def render_summary(snapshot: Mapping[str, Any]) -> str:
    """Operatörün gördüğü metin — KALIP LİSTESİ İÇERMEZ (spec §9.6)."""
    _sema_kapisi(snapshot)
    satirlar: list[str] = [f"Koşu: {snapshot['run_id']} · sonuç: {snapshot['sonuc']}"]
    if snapshot["onaylanabilir"]:
        satirlar.append("ONAYLANABİLİR — aktivasyon ayrı ve elle yapılır.")
    else:
        satirlar.append(
            "ONAYLANAMAZ — açık sorular kapanmadan onay verilemez (K-71)."
        )
    if snapshot["acik_sorular"]:
        satirlar += _satirlar("Açık sorular", list(snapshot["acik_sorular"])[:10])

    satirlar.append("")
    satirlar += _satirlar(
        RISKLI_SIRA[0],
        [f"{k['unit_id']}: {k['detay']}" for k in snapshot["geri_ekleme_celiskileri"]],
    )
    satirlar += _satirlar(
        RISKLI_SIRA[1],
        [f"{k['unit_id']}: {k['sebep']}" for k in snapshot["kararsizlar"]],
    )
    # K-41: SAYI verilir, eşik YOKTUR; tam liste `render_removals_detail`'de.
    satirlar.append(f"{RISKLI_SIRA[2]}: {snapshot['cikarmalar']['sayi']}")
    satirlar.append(
        "Son 4 tur çıkarmaları: "
        + (
            ", ".join(
                f"{kayit['run_id']}={kayit['sayi']}"
                for kayit in snapshot["son_dort_tur_cikarmalari"]
            )
            or "yok"
        )
    )

    satirlar.append("")
    satirlar.append(
        f"{NOTR_SIRA[0]}: "
        + (
            ", ".join(
                f"{alan}={sayi}"
                for alan, sayi in snapshot["sayilar"]["alan_bazli"].items()
            )
            or "yok"
        )
        + f" (toplam {snapshot['sayilar']['toplam']})"
    )
    satirlar.append(
        f"{NOTR_SIRA[1]}: "
        + (
            ", ".join(f"{ad}={oran}" for ad, oran in snapshot["oranlar"].items())
            or "ölçülmedi"
        )
    )
    satirlar.append(
        f"{NOTR_SIRA[2]}: içerik={snapshot['icerik_hashleri']['content_sha']} · "
        f"karar günlüğü={snapshot['icerik_hashleri']['decision_log_sha']}"
    )
    kapilar = snapshot["kapi_sonuclari"]
    satirlar.append(
        f"Kapı sonuçları: Katman-1={kapilar['katman1']} · "
        f"Katman-2 sunuldu={kapilar['katman2']['sunuldu']} (sonucu kapı DEĞİL)"
    )
    satirlar += _satirlar(
        "Uyarılar", [f"{k['sinif']}: {k['detay']}" for k in snapshot["uyarilar"]]
    )
    motor = snapshot["motor_kosu_raporu"]
    satirlar.append(
        f"Motor koşu raporu: {motor['engine_version']} · "
        f"yapılandırma={motor['engine_config_sha']}"
    )
    return "\n".join(satirlar)


def render_removals_detail(snapshot: Mapping[str, Any]) -> str:
    """K-41 tam listesi — bir tık derin. Kalıp METNİ yine GÖRÜNMEZ."""
    _sema_kapisi(snapshot)
    cikarmalar = snapshot["cikarmalar"]
    satirlar = [f"Çıkarılanlar — tam liste ({cikarmalar['sayi']})"]
    for kalem in cikarmalar["kalemler"]:
        satirlar.append(
            f"  - {kalem['unit_id']} · {kalem['alan']} · {kalem['oge_yolu']} "
            f"· {kalem['gerekce']}"
        )
    return "\n".join(satirlar)
