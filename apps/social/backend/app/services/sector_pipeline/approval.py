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
from .engine import KONTROL_ADLARI

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
        atif = bulgu.get("kontrol")
        if type(atif) is not str or atif not in KONTROL_ADLARI:
            raise ApprovalRefused(
                f"bulgu atfı KAYITLI bir kontrol adı DEĞİL ({atif!r}, "
                f"sınıf={bulgu.get('sinif')!r}) — riskli sınıf ayrımı yapılamaz. "
                "Anahtarın VARLIĞI kimlik doğrulaması değildir: boş varsayılan "
                "ya da yazım hatası riskli sınıfı sessizce nötr uyarıya düşürürdü"
            )
        if atif == RISKLI_ATIF_GERI_EKLEME:
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


GORUNTU_KOSU_DISI: frozenset[str] = frozenset({"actor", "son_dort_tur_cikarmalari"})
"""Görüntünün KOŞU DURUMUNDAN türemeyen alanları — mutasyon kapısından muaf.

`actor` görüntüyü KİM gördüğüdür (karar başka bir yöneticiden gelebilir);
`son_dort_tur_cikarmalari` sektörün BAŞKA koşularından türer ve donmadan sonra
yeni bir tur inince meşru olarak değişir. Kalan her alan koşu satırının
kendisinden gelir ve dondurmadan sonra DEĞİŞMEMELİDİR.
"""


def _cekirdek(goruntu: Mapping[str, Any]) -> dict:
    """Görüntünün KOŞUDAN türeyen çekirdeği — muaf alanlar düşürülür."""
    coz = identity.cozulmus(goruntu)
    return {ad: deger for ad, deger in coz.items() if ad not in GORUNTU_KOSU_DISI}


async def build_and_freeze_from_run(db, *, run_id: str, actor: str) -> dict:
    """Görüntüyü kilitli koşudan BASAR ve AYNI işlemde DONDURUR (F18/K-98).

    Çağıranın kurduğu bir görüntüyü kabul eden parametre YOKTUR: olsaydı bir
    görüntü üzerinden onay alıp başka bir koşuyu aktive etmek mümkün olurdu.

    **İŞLEM SARMALI ZORUNLUDUR** (hakem turu 11, yüksek): `FOR UPDATE` kilidi
    işlem-ömürlüdür. Otomatik-commit altında kilit KENDİ ifadesinin sonunda
    düşerdi — yani "kilitli satırdan okundu ve donduruldu" vaadi, okuma ile
    yazma arasında satır değişebildiği için YANLIŞ olurdu.
    """
    async with db.transaction():
        run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
        # Paket bağı DONDURMADA da zorunludur (kapanış turu 2, yüksek): bağsız
        # dondurulan bir görüntü sonradan HERHANGİ bir pakete bağlanabilir ve
        # operatörün hiç görmediği bir pakete kalıcı onay yazılırdı.
        if run.package_id is None:
            raise ApprovalRefused(
                f"koşu {run_id!r} bir paket taslağına bağlı DEĞİL — bağsız görüntü "
                "basılmaz; sonradan bağlanan herhangi bir paket onaylanmış görünürdü"
            )
        goruntu = await _goruntu_kur(db, run, actor=actor)
        return await _dondur(db, run_id=run.run_id, goruntu=goruntu)


async def _goruntu_kur(db, run: runs.VerifiedRun, *, actor: str) -> dict:
    """Görüntünün TEK kurucusu — dondurma ve mutasyon kapısı AYNI kuralı kullanır.

    İki kurucu olsaydı mutasyon kapısı kendi türetimiyle dondurulmuşu
    karşılaştırır ve fark ÜRETİRDİ (kuralların ayrışması yanlış-pozitif).
    """
    acik_sorular = list(run.policy_report["acik_soru_kimlikleri"])
    geri_ekleme, uyarilar = _bulgu_ayrimi(run)
    kapilar = _kapi_sonuclari(run)
    goruntu: dict[str, Any] = {
        "sema": SNAPSHOT_SEMA,
        "run_id": run.run_id,
        # HEDEF KİMLİĞİ ÇEKİRDEKTE (kapanış turu 2, yüksek). Şema bu ikisini
        # bağımsız ve GÜNCELLENEBİLİR yabancı anahtar bırakıyor; tetikleyici
        # yalnız görüntüyü koruyor. Kimlik çekirdekte olmasaydı donmadan sonra
        # paket A→B ya da sektör A→B kaydırılır, çekirdek karşılaştırması geçer
        # ve olay CANLI değerlerle yazılırdı — operatörün gördüğünden başka bir
        # pakete kalıcı onay. Değerler METİN olarak yazılır: jsonb'den `UUID`
        # değil `str` döner ve iki yandaki karşılaştırma tip yüzünden yalan
        # söylemesin.
        "paket_id": str(run.package_id),
        "sektor_id": str(run.sector_id),
        "sonuc": run.sonuc,
        "sebep": run.sebep,
        "actor": actor,
        "icerik_hashleri": {
            "content_sha": run.content_sha,
            "decision_log_sha": run.decision_log_sha,
        },
        "acik_sorular": acik_sorular,
        # K-71 + spec §10.2. Motor açık soruyu zaten `blocked` yapar; bu İKİNCİ
        # katmandır. Kapılar da OKUNUR: Katman-1 yedi kapının İÇİNDE DEĞİLDİR,
        # yani doğrulanmış bir koşunun tasdiki `FAIL` olabilir — görüntü onu
        # gösteriyor ama "onaylanabilir" demeye devam ederdi.
        # Karşılaştırma NORMALİZASYONSUZDUR (strip/lower YOK — A4 disiplini).
        "onaylanabilir": (
            run.sonuc == "activation_eligible"
            and not acik_sorular
            and kapilar["katman1"] == "PASS"
            and kapilar["katman2"]["sunuldu"] is True
        ),
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
        "kapi_sonuclari": kapilar,
        "motor_kosu_raporu": {
            "engine_version": run.engine_version,
            "engine_config_sha": run.engine_config_sha,
            "barrier_report": identity.cozulmus(run.barrier_report),
        },
    }
    return goruntu


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
    # K-42(b) EŞİK koymaz ama anlamsız değeri de kaydetmez. `bool` AYRICA
    # reddedilir: `True` bir `int` alt sınıfıdır ve "1 saniyede onaylandı" diye
    # kalıcılaşırdı.
    if type(seconds) is not int or seconds < 0:
        raise ApprovalRefused(
            f"saniye değeri anlamsız: {seconds!r} — negatif olmayan tam sayı olmalı"
        )

    # İŞLEM SARMALI ZORUNLUDUR (hakem turu 11, yüksek): kapılar kilitli satıra
    # bakar, olay ve karar yazımı AYNI işlemde iner. Otomatik-commit altında
    # karar commit edilir, sonra olay düşerse onay İZSİZ kalırdı.
    async with db.transaction():
        run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
        if run.package_id is None:
            raise ApprovalRefused(
                f"koşu {run_id!r} bir paket taslağına bağlı DEĞİL — yaşam döngüsü "
                "olayı paket kimliği ister (R3); onay yazılamadan patlardı"
            )
        # Hash'in VARLIĞI görüntünün gösterildiğinin kanıtı DEĞİLDİR (hakem
        # turu 11, yüksek): 036'da görüntü ile hash kolonunu birbirine bağlayan
        # bir kısıt YOK, yani hash dolu / görüntü boş satır MÜMKÜNDÜR.
        if run.approval_snapshot is None:
            raise ApprovalRefused(
                f"koşu {run_id!r} için dondurulmuş görüntü YOK — hash'in varlığı "
                "ekranın gösterildiğini kanıtlamaz"
            )
        goruntu = run.approval_snapshot
        _sema_kapisi(goruntu)
        if goruntu.get("run_id") != run_id:
            raise ApprovalRefused(
                f"dondurulmuş görüntü BAŞKA koşuya ait: {goruntu.get('run_id')!r}"
            )
        beklenen = identity.canonical_sha(identity.cozulmus(goruntu))
        if run.snapshot_sha != beklenen:
            raise ApprovalRefused(
                f"satırdaki hash, satırdaki görüntünün hash'i DEĞİL: "
                f"{run.snapshot_sha!r} != {beklenen!r} — iki kolon ayrışmış"
            )
        if snapshot_sha != run.snapshot_sha:
            raise ApprovalRefused(
                "karar BAŞKA bir görüntüye ait: verilen hash "
                f"{snapshot_sha!r}, satırdaki {run.snapshot_sha!r} — onay yalnız "
                "gösterilen görüntüye verilir (F18)"
            )
        # F18'in ASIL iddiası: dondurmadan sonra koşu satırı değiştiyse
        # gösterilen ekran artık koşuyu ANLATMIYOR. Çekirdek YENİDEN türetilir
        # ve birebir karşılaştırılır (muaf alanlar `GORUNTU_KOSU_DISI`).
        taze = await _goruntu_kur(db, run, actor=goruntu.get("actor", actor))
        if _cekirdek(taze) != _cekirdek(goruntu):
            raise ApprovalRefused(
                f"koşu {run_id!r} dondurmadan SONRA değişti — gösterilen görüntü "
                "artık koşuyu anlatmıyor; karar verilmez"
            )
        if karar == "onay" and goruntu.get("onaylanabilir") is not True:
            raise ApprovalRefused(
                f"görüntü onaylanabilir DEĞİL (onaylanabilir="
                f"{goruntu.get('onaylanabilir')!r}) — ekranda reddedileni kayıtta "
                "kabul etmek denetim izini yalan yapardı. Ret yazılabilir."
            )

        # OLAY ÖNCE (yaşam döngüsünün F24 deseni): `log_package_event` altyapı
        # hatasında `None` DÖNER ve çağıranı düşürmez — o dönüş BURADA hatadır.
        # İzsiz bir onay sessiz bir yalandır.
        olay_id = await log_package_event(
            db,
            event_type="approval" if karar == "onay" else "rejection",
            sector_id=run.sector_id,
            package_id=run.package_id,
            actor=actor,
            detail={
                "run_id": run_id,
                "seconds": seconds,
                "snapshot_sha": snapshot_sha,
            },
        )
        if olay_id is None:
            raise ApprovalRefused(
                f"{karar!r} olayı YAZILAMADI — izsiz karar kaydedilmez (K-99)"
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
