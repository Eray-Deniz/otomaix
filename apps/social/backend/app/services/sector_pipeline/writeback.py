"""Doğrulanmış koşudan pakete YAZIM — taslak · yerinde güncelleme · aktivasyon.

Kanonik sıra bağlayıcıdır: **sentez → motor → draft**. Bu modül o zincirin son
halkasıdır ve tek girdisi KİLİTLİ, DOĞRULANMIŞ bir koşu satırıdır.

**Kanıt veritabanından OKUNUR, çağırandan alınmaz (arayüz eki R8).** Bu modülün
hiçbir public fonksiyonu `EngineResult` · `evidence` · `snapshot` ya da herhangi
bir `dict` parametresi ALMAZ; imzalarda yalnız `run_id` ve `actor` vardır. İlk
tasarım çağıranın verdiği bir sonuç nesnesini kabul ediyordu — elle kurulmuş bir
nesneyle motor hiç koşmadan yazım yapılabilirdi.

**Koşu satırının TEK okuma kapısı `runs.load_verified_run`'dır** (yedi kapı).
Yazım · güncelleme · aktivasyon üçü de ondan geçer; ikinci bir kapı listesi
YAZILMAZ. Yapısal kilidi:
`tests/test_pipeline_writeback.py::test_writeback_cannot_read_run_row_outside_loader`.

**KÜRESEL KİLİT SIRASI — koşu satırları → sektör → paket satırları.** Bu
modülün üç public yolu da (yazım · güncelleme · aktivasyon) ve ham yaşam
döngüsü tüketicisi bu tek sırayı izler. Tek sıra = döngü yok; iki farklı sıra
kullanan iki meşru işlem, düşman girdi olmadan kilitlenir.

Sıra iki hakem turunda İKİ AYRI döngüyle sınandı ve ikisi de bu tek kuralla
kapandı: aktivasyon aktif paketi sektörden önce kilitliyordu (tur 1), ve
düzeltme jeton yakmasını paket mutasyonundan SONRA yapıyordu (tur 2). Ölçüm
yapısaldır — yokluğu koşarak kanıtlamak zamanlamaya bağlı olurdu.

**Bu sıra fix turu 1'de DÜZELTİLDİ (hakem bulgusu, yüksek).** Önceki yazım
taslak satırını sektör kilidinden ÖNCE alıyordu ve buradaki açıklama "döngü
üretmez" diyordu. Hakem somut bir sarmalama gösterdi ve ÖLÇÜLDÜ ki iddia
YANLIŞTI: aktivasyon aktif paketi tutup sektörü beklerken, geri alma sektörü
tutup `_active_row`'da AYNI aktif paketi bekler — kapalı bir döngü. İki meşru
işlem, düşman girdi gerekmiyor. Artık her iki uç da sektör kilidini herhangi
bir paket satırından ÖNCE alır.
"""

from __future__ import annotations

from uuid import UUID

from app.services import sector_package_lifecycle as lifecycle
from app.services.sector_pipeline import identity, readiness_items, runs

SCHEMA_SURUMU = 1
"""Yazılan taslağın içerik şema sürümü.

Sabittir ve ARTIRILMAZ: `identity` modülünün açılış hükmü Plan 1 doğrulayıcısına
dokunulmamasını bağlar, yani Plan 2 boyunca içerik şeması sürüm 1'de kalır.
Değer bir çağıran parametresi DEĞİLDİR — olsaydı doğrulayıcının kapsamadığı bir
sürüm numarası taslağa yazılabilirdi.
"""


class WritebackRefused(RuntimeError):
    """Taslak yazımı ya da yerinde güncelleme REDDEDİLDİ."""


class ActivationRefused(RuntimeError):
    """Aktivasyon zinciri REDDEDİLDİ — F18 kanıt zinciri kilitli satırdan düştü."""


def _cozulmus_aday(run: runs.VerifiedRun) -> dict:
    """Koşunun adayını yazılabilir yapıya ÇÖZER — içerik DEĞİŞMEZ.

    `record_result` yükü DONDURUR (R6(e)): eşlemeler `mappingproxy`, diziler
    demet olur. Paket şeması `list`/`dict` üzerinden tanımlıdır ve asyncpg'nin
    jsonb kodlayıcısı `mappingproxy`yi serileştiremez, o yüzden yazım sınırında
    çözme ZORUNLUDUR. Kural `identity.cozulmus`'ta TEK yerdedir; ikinci bir
    çözme kopyası yazılsaydı dondurma ile çözme sürüm sürüm ayrışırdı.
    """
    return identity.cozulmus(run.final_candidate)


def _cozulmus_gunluk(run: runs.VerifiedRun) -> list[dict]:
    """Koşunun karar günlüğünü yazılabilir listeye ÇÖZER — içerik DEĞİŞMEZ."""
    return [identity.cozulmus(satir) for satir in run.final_decision_log]


async def write_draft_from_run(db, *, run_id: str, actor: str) -> UUID:
    """Doğrulanmış koşudan YENİ bir taslak sürümü yazar; `package_id` döner.

    Yedi kapının tamamı `runs.load_verified_run`'da, KİLİTLİ satıra karşı koşar.
    Yazılan karar günlüğü MOTORUNKİDİR: Plan 1'in `draft_created` yer tutucusu
    verilmezse yazılır ve K-84 kimlik zincirini boş bırakırdı (F19).

    **Düzeltme koşusu REDDEDİLİR (K-106).** Düzeltmenin ikinci bir sürüm
    yakması, K-106'nın tam olarak yasakladığı sonuçtur; düzeltmenin yolu
    `update_draft_from_run`'dır.

    **Tekrar oynatma yeni sürüm YAKMAZ.** Koşu zaten bir taslağa bağlıysa o
    taslak döner. Eşzamanlı iki yazım koşu satırının kilidinde serileşir;
    ikinci taraf kilidi aldığında bağı GÖRÜR ve aynı taslağı döndürür.
    """
    async with db.transaction():
        run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
        if run.kosu_turu == "duzeltme":
            raise runs.CorrectionRunRefused(
                f"koşu {run_id!r} bir DÜZELTME turudur — düzeltme ikinci bir sürüm "
                "yakamaz (K-106); yolu update_draft_from_run'dır"
            )
        if run.package_id is not None:
            return run.package_id

        package_id = await lifecycle.insert_draft(
            db,
            sector_id=run.sector_id,
            content=_cozulmus_aday(run),
            schema_version=SCHEMA_SURUMU,
            run_id=run.run_id,
            actor=actor,
            decision_log=_cozulmus_gunluk(run),
        )
        bagli = await db.fetchval(
            "UPDATE social.sector_package_runs SET package_id = $2 "
            "WHERE run_id = $1 AND package_id IS NULL RETURNING package_id",
            run_id,
            package_id,
        )
        if bagli is None:  # pragma: no cover — satır yukarıda kilitlendi
            raise WritebackRefused(
                f"koşu {run_id!r} bu işlem sırasında BAŞKA bir taslağa bağlandı — "
                "iki taslak yazılmaz"
            )
        return package_id


async def update_draft_from_run(db, *, run_id: str, actor: str) -> None:
    """K-106 — düzeltme koşusunun çıktısını AYNI taslak satırına yazar.

    **Hedef parametreden GELMEZ.** Güncellenecek taslak, koşunun ana turdan
    devraldığı `package_id`'dir; imzada `package_id` olsaydı yanlış taslağı
    güncellemek mümkün olurdu.

    **Soyağacı ŞARTTIR:** `duzeltilen_run_id` boşsa bu yol çalışmaz. Sıradan bir
    tur yerinde güncelleme yapamaz — onun yolu yeni sürümdür.

    **Bekleyen kanıt YAKILIR (bayat kanıtla aktivasyon yok).** Güncellemeden
    ÖNCE basılmış ve henüz harcanmamış her köken jetonu bu işlemde harcanmış
    sayılır; aksi hâlde operatörün onayladığı baytlar değiştikten sonra o eski
    jetonla aktivasyon yapılabilirdi. İçerik hash'i bağı (aktivasyon yolunda)
    aynı senaryoyu İKİNCİ ve bağımsız bir kapıyla kapatır; biri diğerinin
    yerine geçmez.
    """
    # Aktör KANONİK KAPIDAN geçer (fix turu 1, hakem bulgusu). Önceki yazım
    # parametreyi alıyor ama HİÇ kullanmıyordu: boş ya da yalnız-boşluk bir
    # aktör sessizce kabul ediliyordu, yani imza tutulmayan bir söz veriyordu.
    #
    # DÜRÜST SINIR — bu doğrulama KALICI ATIF DEĞİLDİR. Aktörün nereye
    # yazılacağı bugün YOK: `sector_packages` tablosunda aktör kolonu, olay türü
    # kümesinde bir taslak olayı bulunmuyor. Borç TASK.md'de EŞLİ yükümlülük
    # olarak kayıtlı (Task 6 olay türünü açar, Task 15 çağrıyı ekler) ve Task
    # 6'nın ayağı İNMEDİ — ölçüldü: depoda `draft_created`/`draft_updated`
    # diye bir olay türü yok. Burada kapatılan şey yalnız "geçersiz aktör
    # sessizce kabul ediliyor" ayağıdır.
    owner = lifecycle._require_actor(actor)
    del owner  # kalıcı taşıyıcı henüz YOK; değer bilerek kullanılmıyor

    async with db.transaction():
        run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
        if run.duzeltilen_run_id is None:
            raise WritebackRefused(
                f"koşu {run_id!r} bir düzeltme turu DEĞİL (duzeltilen_run_id boş) — "
                "yerinde güncelleme yalnız düzeltme soyağacıyla yapılır (K-106)"
            )
        if run.package_id is None:
            raise WritebackRefused(
                f"koşu {run_id!r} bir taslağa bağlı DEĞİL — güncellenecek hedef yok"
            )

        # KÜRESEL KİLİT SIRASI: koşu satırları → sektör → paket satırları.
        # Jeton yakma BAŞKA koşu satırlarına dokunur ve bu yüzden paket
        # satırından ÖNCE gelmek ZORUNDADIR. Ters sırada — fix turu 1'in
        # yazımında öyleydi — bu yol paketi tutup başka bir koşu satırını
        # beklerken, önceden basılmış kanıtla koşan bir aktivasyon o koşu
        # satırını tutup paketi bekliyordu: kapalı bir döngü (hakem turu 2,
        # yüksek). İlk turda kapatılan aktivasyon↔geri-alma döngüsünden AYRI
        # bir döngüydü; kapatılan şey artık sıranın KENDİSİDİR, tek varyant değil.
        #
        # İşlem geri alınırsa yakma da geri alınır; anlam DEĞİŞMEZ.
        await db.execute(
            "UPDATE social.sector_package_runs SET kanit_jetonu_harcandi_at = now() "
            "WHERE package_id = $1 AND kanit_jetonu IS NOT NULL "
            "  AND kanit_jetonu_harcandi_at IS NULL",
            run.package_id,
        )
        await lifecycle._lock_sector(db, run.sector_id)
        await lifecycle._update_draft_row(
            db,
            package_id=run.package_id,
            sector_id=run.sector_id,
            content=_cozulmus_aday(run),
            decision_log=_cozulmus_gunluk(run),
        )


async def build_activation_evidence(db, *, run_id: str) -> lifecycle.ActivationGateEvidence:
    """`ActivationGateEvidence`'ın TEK kurulum yeri (arayüz eki R8(c)).

    Hiçbir alan parametreden gelmez: hepsi aynı işlemde kilitlenmiş satırlardan
    TÜRETİLİR. İmzada `evidence`, `snapshot` ya da herhangi bir `dict` parametre
    YOKTUR — olsaydı uydurulmuş bir sözlükten kanıt kurulabilirdi.

    Yük türetmesi `lifecycle.activation_evidence_payload`'dadır ve jetonu BASAN
    taraf (`runs.mint_evidence_token`) da AYNI yardımcıyı çağırır. İki yerde iki
    türetme yazılsaydı basılan parmak izi ile kurulan kanıtın parmak izi
    sessizce ayrışır ve köken kapısı hiçbir zaman açılmazdı.
    """
    run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
    # Sektör kilidi AKTİF PAKET satırından ÖNCE (fix turu 1, kilitlenme
    # döngüsü). Bu fonksiyon `activate_from_snapshot` DIŞINDAN da çağrılabildiği
    # için sırayı kendisi kurar; iki kez almak aynı işlemde zararsızdır.
    await lifecycle._lock_sector(db, run.sector_id)
    aktif = await db.fetchrow(
        "SELECT id, version FROM social.sector_packages "
        "WHERE sector_id = $1 AND status = 'active' FOR UPDATE",
        run.sector_id,
    )
    payload = lifecycle.activation_evidence_payload(
        run,
        aktif,
        beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
    )
    jeton = await runs.mint_evidence_token(
        db,
        table="sector_package_runs",
        run_id=run_id,
        incident_id=None,
        package_id=None,
    )
    return lifecycle.ActivationGateEvidence(**payload, provenance_token=jeton)


async def activate_from_snapshot(db, *, run_id: str, actor: str) -> None:
    """Onaylanmış görüntüye bağlı aktivasyon — F18 kanıt zinciri DB'den doğrulanır.

    Plan 1'in kanıt sınıfı boolean'ları OLDUĞU GİBİ kabul eder; yani bir adaptör
    onları uydurabilseydi motor çıktısı yönetici onayı olmadan aktive edilirdi
    (K-69/K-28 atlatılırdı). Burada doğrulananlar AYNI işlemde kilitli koşu
    satırından okunur:

      * koşu → paket bağı VAR ve satır çözülüyor;
      * dondurulmuş görüntü VAR (hash'in varlığı ekranın gösterildiğini
        kanıtlamaz — o kapı Task 14'te ölçüldü, burada görüntünün KENDİSİ aranır);
      * `approval_karar == 'onay'` (karar yoksa ya da 'ret' ise RED);
      * Katman-2 KOŞULMUŞ ve SUNULMUŞ (SONUCU okunmaz — spec §10.2);
      * taslağın O ANKİ içeriği ve karar günlüğü, onaylanan görüntüdeki
        hash'lerle BİREBİR eşleşiyor.

    Katman-1, hazırlık listesi (A4) ve K-94 taban durumu ayrıca kanıt yükünden
    türer ve `activate_package`'ın kendi kapısında `GateNotSatisfied` üretir;
    burada ikinci bir kopya YAZILMAZ.

    **İçerik bağı neden burada (tur 5).** Onaydan sonra taslağı değiştiren
    herhangi bir yol — düzeltme turu, elle müdahale — yöneticinin GÖRMEDİĞİ
    baytların aktive edilmesine yol açardı. Kapı, kaç yazıcı olduğundan bağımsız
    olarak burada kapanır.
    """
    async with db.transaction():
        run = await runs.load_verified_run(db, run_id=run_id, for_update=True)
        # SEKTÖR KİLİDİ, HER PAKET KİLİDİNDEN ÖNCE (fix turu 1). Yaşam döngüsü
        # katmanı da aynı sırayı kullanır ve kilidi yeniden almak aynı işlemde
        # zararsızdır; kazanılan şey, bu yolun aşağıda alacağı taslak ve aktif
        # paket kilitlerinin sektör kilidinin ARDINDA kalmasıdır.
        await lifecycle._lock_sector(db, run.sector_id)
        if run.package_id is None:
            raise ActivationRefused(
                f"koşu {run_id!r} bir taslağa bağlı DEĞİL — aktive edilecek hedef yok"
            )
        # SIRA ANLAMLIDIR ve ölçülür: görüntü kapısı karar kapısından ÖNCEDİR.
        # İkisi de düşmüş bir koşuda operatöre söylenmesi gereken şey "karar
        # yok" değil, "ekran hiç gösterilmedi"dir — ikincisi birincinin sebebi
        # olabilir ve yanlış sırayla operatör var olmayan bir kararı arar.
        if run.approval_snapshot is None:
            raise ActivationRefused(
                f"koşu {run_id!r} için dondurulmuş GÖRÜNTÜ YOK — onay yüzeyi bu koşu "
                "için hiç koşmamış; karar aranmadan önce ekran gösterilmiş olmalı"
            )
        # TEK kapı, iki hâl: karar YOK ve karar 'ret'. Ayrı iki kapı yazılmıştı;
        # mutasyon ölçümü İKİSİNİN DE BAĞIMSIZ OLARAK KANITLANAMADIĞINI gösterdi
        # — `None != "onay"` zaten ikinci kapıdan geçmez, yani birincisi hiçbir
        # davranış eklemiyordu. Kanıtlanamayan kapı, gereksiz kapıdır (aynı
        # tespit `approval._paket_kapisi`'nde de yapılmıştı).
        if run.approval_karar != "onay":
            raise ActivationRefused(
                f"koşunun KARARI aktivasyona izin vermiyor ({run.approval_karar!r}) — "
                "karar yoksa dondurulmuş görüntü tek başına onay değildir, 'ret' "
                "verilmiş bir aday da aktive edilemez (F18)"
            )

        katman2 = run.katman2_attestation
        if katman2 is None or katman2.get("sunuldu") is not True:
            raise ActivationRefused(
                "Katman-2 tasdiki YOK ya da 'sunuldu' değil — koşulmuş ve sunulmuş "
                "olması ÖN KOŞULDUR (sonucu okunmaz, spec §10.2)"
            )

        taslak = await db.fetchrow(
            "SELECT content, decision_log FROM social.sector_packages "
            "WHERE id = $1 FOR UPDATE",
            run.package_id,
        )
        if taslak is None:
            raise ActivationRefused(
                f"koşunun paket bağı bir satıra çözülmüyor ({run.package_id})"
            )
        hashler = run.approval_snapshot.get("icerik_hashleri") or {}
        if identity.canonical_sha(taslak["content"]) != hashler.get("content_sha"):
            raise ActivationRefused(
                "taslağın içeriği onaydan SONRA değişti — yöneticinin görmediği "
                "baytlar aktive edilemez"
            )
        if identity.canonical_sha(
            identity.cozulmus(taslak["decision_log"])
        ) != hashler.get("decision_log_sha"):
            raise ActivationRefused(
                "taslağın karar günlüğü onaydan SONRA değişti — yöneticinin "
                "görmediği gerekçeler aktive edilemez"
            )

        evidence = await build_activation_evidence(db, run_id=run_id)
        await lifecycle.activate_package(
            db, package_id=run.package_id, evidence=evidence, actor=actor
        )
