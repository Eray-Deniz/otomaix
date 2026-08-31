"""Kalıp kimliği + karar günlüğü şeması (Plan 2 Task 3).

Ölçülen sözleşme TEK cümleyle: **içerik şeması DEĞİŞMEZ, birim kümesi karar
günlüğünden TÜRETİLİR.** Yapısal yazım kapısı (`sector_content_schema.py`) CTA
öğesinin anahtar kümesini, özel gün girdisinin beş yuvasını ve diğer liste
öğelerinin düz metin oluşunu EŞİTLİK olarak doğrular; içeriğe `unit_id`
eklemek bu kapıdan geçemez. Bu yüzden kimlik karar günlüğünde yaşar ve
içeriğe **kanonik yolu** (sıra ordinali dâhil) üzerinden bağlanır.

Bu dosyanın kanıtlamak zorunda olduğu iki zor nokta:

* **İki yönlü bütünlük.** Yalnız "her günlük satırının içerikte karşılığı var"
  demek yetmez (sahipsiz öğe kaçar), yalnız "her içerik öğesinin satırı var"
  demek de yetmez (hayalet birim kaçar). Her iki yön AYRI testle ölçülür ve
  tek yönlü bir uygulama ikisini birden geçemez.
* **Çokluk.** Aynı listede birebir aynı metin iki kez geçebilir; iki öğenin
  hash'i AYNIdır. Eşlemeyi yapan şey hash değil, yoldaki SIRA ORDİNALİDİR.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

import pytest

from app.services.sector_packages import structural_errors
from app.services.sector_pipeline import identity

from .test_sector_packages_service import CUMHURIYET_KEY, _valid_content

UNIT_ID_RE = re.compile(r"^ku-[0-9a-f]{12}$")

# `_valid_content()`'in ürettiği kanonik yol sayısı. Dökümü: 3 düz metin alanı
# (kapsam · ton_ve_dil · gorsel_kodlar) + 4 liste alanının birer öğesi + 4 video
# havuzu öğesi (2 hareket + 2 sahne) + 1 özel günün 5 yuvası = 16.
#
# Adı olmadan dört testte çıplak `16` duruyordu: `_valid_content` değişince
# dördü birden opak bir sayıyla kırılırdı.
BEKLENEN_BIRIM_SAYISI = 16


# ─── Ortak kurgu ────────────────────────────────────────────────────────────


def _karar_row(**overrides) -> dict:
    """Şemayı GEÇEN asgari karar satırı — testler tek alanını bozar."""
    row = {
        "tur": "karar",
        "alan": "kanca_kaliplari",
        "oge_yolu": "kanca_kaliplari[0]",
        "unit_id": "ku-0123456789ab",
        "oge_sha": "a" * 64,
        "karar": "koru",
        "gerekce": "Kalıp sektörde hâlâ karşılık buluyor.",
        "kanit": "",
        "aktor": "sentez",
    }
    row.update(overrides)
    return row


def _not_row(**overrides) -> dict:
    row = {
        "tur": "not",
        "sinif": "reddedilen-aday",
        "gerekce": "Kaynak pinlenmemiş, aday pakete alınmadı.",
    }
    row.update(overrides)
    return row


def _log_for(content: dict, *, karar: str = "koru") -> list[dict]:
    """İçeriğin HER kanonik yolu için bir yaşayan karar satırı üretir."""
    return [
        _karar_row(
            alan=unit["alan"],
            oge_yolu=path,
            unit_id=identity.new_unit_id(),
            oge_sha=unit["oge_sha"],
            karar=karar,
        )
        for path, unit in identity.enumerate_content_units(content).items()
    ]


# ─── 1. Kimlik biçimi ───────────────────────────────────────────────────────


def test_new_unit_id_format_and_uniqueness():
    """`ku-` + 12 onaltılık, rastgele — metin özetinden TÜRETİLMEZ."""
    ids = [identity.new_unit_id() for _ in range(200)]
    for value in ids:
        assert UNIT_ID_RE.match(value), f"biçim ihlali: {value!r}"
    assert len(set(ids)) == 200, "kimlikler çakıştı — rastgelelik yok"


def test_unit_id_format_violation_is_rejected():
    """Biçim kapısı: kimlik metin özetinden türetilemez, dayatılır."""
    errors = identity.validate_decision_log([_karar_row(unit_id="kanca-1")])
    assert any("unit_id biçimi" in e for e in errors), errors


# ─── 2. Karar günlüğü şeması ────────────────────────────────────────────────


def test_decision_log_accepts_valid_rows():
    """POZİTİF KONTROL — geçerli karar + not satırı hiç hata üretmez."""
    assert identity.validate_decision_log([_karar_row(), _not_row()]) == []


def test_rejects_sixth_enum_value():
    """Karar enum'u BEŞ değer — altıncısı yok (K-107 düzeltmesi)."""
    errors = identity.validate_decision_log([_karar_row(karar="birlestir")])
    assert any("karar değeri kapalı kümenin dışında" in e for e in errors), errors


def test_rejects_cikar_without_evidence():
    """`cikar` POZİTİF KANIT olmadan GEÇERSİZ (spec §3.5)."""
    errors = identity.validate_decision_log([_karar_row(karar="cikar", kanit="")])
    assert any("pozitif kanıt" in e for e in errors), errors


def test_cikar_with_evidence_is_accepted():
    """POZİTİF KONTROL — kanıtlı `cikar` geçer; kapı `cikar`'ı topyekûn yasaklamaz."""
    assert (
        identity.validate_decision_log(
            [_karar_row(karar="cikar", kanit="TDK 2025 yazım kılavuzu s.14")]
        )
        == []
    )


def test_rejects_duplicate_unit_id_decisions():
    """Aynı `unit_id` bir günlükte İKİ karar satırı taşıyamaz."""
    errors = identity.validate_decision_log(
        [
            _karar_row(unit_id="ku-0123456789ab", oge_yolu="kanca_kaliplari[0]"),
            _karar_row(unit_id="ku-0123456789ab", oge_yolu="kanca_kaliplari[1]"),
        ]
    )
    assert any("birden fazla karar satırı" in e for e in errors), errors


def test_rejects_unknown_actor():
    """`aktor` ∈ {sentez, motor, insan} — kapalı."""
    errors = identity.validate_decision_log([_karar_row(aktor="robot")])
    assert any("aktor değeri kapalı kümenin dışında" in e for e in errors), errors


def test_note_row_classes_are_closed():
    """`sinif` İKİ değer taşır; üçüncüsü RED."""
    errors = identity.validate_decision_log([_not_row(sinif="uydurma-sinif")])
    assert any("sinif değeri kapalı kümenin dışında" in e for e in errors), errors


def test_kismi_tur_tasima_as_note_rejected():
    """K-107 kapısı: kısmi tür taşıması NOT olarak yazılamaz.

    Geçseydi doğrulayıcıdan çıkardı ama motorun birim-başına kapsam kontrolünü
    karşılamazdı — sessiz taşıma geri gelirdi.
    """
    errors = identity.validate_decision_log([_not_row(sinif="kismi-tur-tasima")])
    assert any("kismi-tur-tasima" in e and "K-107" in e for e in errors), errors


def test_kismi_tur_tasima_as_koru_field_accepted():
    """POZİTİF KONTROL — doğru temsil: `koru` satırında `kapsam` ek alanı."""
    assert (
        identity.validate_decision_log(
            [_karar_row(karar="koru", kapsam="kismi-tur-tasima")]
        )
        == []
    )


def test_motor_row_without_rule_id_rejected():
    """K-145 damgası: `motor` satırı kural kimliği TAŞIMAK ZORUNDA."""
    errors = identity.validate_decision_log(
        [_karar_row(aktor="motor", kural_surumu="2026-08-27")]
    )
    assert any("kural_kimligi" in e for e in errors), errors


def test_motor_row_without_rule_version_rejected():
    errors = identity.validate_decision_log(
        [_karar_row(aktor="motor", kural_kimligi="K-130")]
    )
    assert any("kural_surumu" in e for e in errors), errors


def test_motor_row_with_full_stamp_accepted():
    """POZİTİF KONTROL — damgalı motor satırı geçer."""
    assert (
        identity.validate_decision_log(
            [_karar_row(aktor="motor", kural_kimligi="K-130", kural_surumu="2026-08-27")]
        )
        == []
    )


def test_non_motor_row_carrying_rule_stamp_rejected():
    """Damga YALNIZ motor satırında; sentez satırı kural provenansı uyduramaz."""
    errors = identity.validate_decision_log(
        [_karar_row(aktor="sentez", kural_kimligi="K-130", kural_surumu="2026-08-27")]
    )
    assert any("kural damgası TAŞIYAMAZ" in e for e in errors), errors


def test_ekle_row_may_carry_yerine_gecer():
    """POZİTİF KONTROL — K-154 `cikar`+`ekle` çifti bağı `ekle` satırında yaşar."""
    assert (
        identity.validate_decision_log(
            [
                _karar_row(
                    karar="ekle",
                    unit_id="ku-aaaaaaaaaaaa",
                    yerine_gecer="ku-bbbbbbbbbbbb",
                )
            ]
        )
        == []
    )


# ─── 3. Yaşayan birim kümesi ────────────────────────────────────────────────


def test_decision_units_derived_from_living_log_rows():
    """Yaşayan küme = `koru` + `guncelle` + `ekle`.

    Kurgu KAPSAYICIDIR: günlük içeriğin HER yolunu sahiplenir ve her satırın
    `alan`'ı yolunun alanıyla uyuşur. Eski kurgu üç satırı üç ayrı yola
    bağlıyor ama `alan`'ı `_karar_row` varsayılanında (`kanca_kaliplari`)
    bırakıyordu — yani F3'ün kusurunu SERGİLİYORDU (hakem yakaladı).
    """
    content = _valid_content()
    rows = _log_for(content)
    paths = [row["oge_yolu"] for row in rows]
    rows[0].update(unit_id="ku-000000000001", karar="koru")
    rows[1].update(unit_id="ku-000000000002", karar="guncelle")
    rows[2].update(unit_id="ku-000000000003", karar="ekle")

    units = identity.decision_units(content, rows)
    assert len(units) == BEKLENEN_BIRIM_SAYISI
    assert {"ku-000000000001", "ku-000000000002", "ku-000000000003"} <= set(units)
    assert units["ku-000000000002"]["oge_yolu"] == paths[1]
    assert units["ku-000000000002"]["karar"] == "guncelle"
    for unit in units.values():
        assert unit["alan"] == unit["oge_yolu"].split("/")[0].split("[")[0]


def test_cikar_row_drops_unit_from_set():
    """`cikar` birimi yaşayan kümeden DÜŞÜRÜR — çıkarılan öğe içerikte YOKTUR.

    Çıkarılan birim aday pakete girmediği için yolu da içerikte bulunmaz;
    kurgu bu yüzden kapsayıcı günlüğün ÜSTÜNE bir `cikar` satırı ekler.
    """
    content = _valid_content()
    rows = _log_for(content)
    rows.append(
        _karar_row(
            alan="kanca_kaliplari",
            oge_yolu="kanca_kaliplari[9]",
            unit_id="ku-000000000009",
            karar="cikar",
            oge_sha="e" * 64,
            kanit="Mevzuat 2026-01-01'de yürürlükten kalktı.",
        )
    )
    units = identity.decision_units(content, rows)
    assert len(units) == BEKLENEN_BIRIM_SAYISI  # boş küme bu testi kandırırdı
    assert "ku-000000000009" not in units


def test_kirp_row_is_not_a_living_unit():
    """Kanonik kayıt: kırpma **paketten çıkarır, kayıttan çıkarmaz**.

    Kırpılan öğe aday pakete GİRMEZ; yalnız karar günlüğünde durur. `kirp`
    yaşayan sayılsaydı her gerçek kırpma zorunlu olarak hayalet birim üretirdi
    — aşağıdaki bütünlük kontrolü o hâlde hata verirdi.
    """
    content = _valid_content()
    rows = _log_for(content)
    rows.append(
        _karar_row(
            alan="kanca_kaliplari",
            oge_yolu="kanca_kaliplari[7]",
            unit_id="ku-000000000077",
            karar="kirp",
            oge_sha="b" * 64,
        )
    )
    yasayanlar = identity.decision_units(content, rows)
    assert len(yasayanlar) == BEKLENEN_BIRIM_SAYISI, sorted(yasayanlar)  # boş küme kandırırdı
    assert "ku-000000000077" not in yasayanlar
    assert identity.check_unit_integrity(content, rows) == []


def test_decision_units_refuses_an_inconsistent_pair():
    """F2: TEK ÜRETİCİ içerik konusunda da fail-closed'dur.

    R6(b) bu dönüşü denetçi zincirinin `unit_snapshot` girdisi yapıyor.
    Hayalet yol taşıyan bir çift sessizce `deger=None` ile akarsa, "çağıran
    önce bütünlüğü koşturur" cümlesi bir KAPI değil bir RİCA olur — planın her
    yerde reddettiği kalıp (K-145'in saldırdığı üretici/tüketici ayrışması).
    """
    content = _valid_content()
    rows = _log_for(content)
    rows.append(
        _karar_row(
            alan="kanca_kaliplari",
            oge_yolu="kanca_kaliplari[42]",
            unit_id="ku-00000000feed",
            oge_sha="f" * 64,
        )
    )
    with pytest.raises(ValueError, match="içerik ile karar günlüğü tutarsız"):
        identity.decision_units(content, rows)


def test_decision_units_refuses_a_log_that_leaves_content_unowned():
    """F2: eksik yön de kapalı — sahipsiz öğe de görüntü ÜRETTİRMEZ."""
    content = _valid_content()
    rows = [r for r in _log_for(content) if r["oge_yolu"] != "kapsam"]
    with pytest.raises(ValueError, match="içerik ile karar günlüğü tutarsız"):
        identity.decision_units(content, rows)


def test_decision_units_names_the_content_gate_when_content_is_malformed():
    """Mesaj DÜŞEN KAPIYI adlandırır: bozuk içerik "tutarsızlık" diye anılmaz.

    `check_unit_integrity` Plan 1 yazım kapısını da koşturduğu için şekil
    hataları "içerik ile karar günlüğü tutarsız" başlığı altında çıkıyordu —
    okuyucu günlüğü suçlardı. (Öz-inceleme, fix turu 1.)
    """
    bozuk = _valid_content()
    del bozuk["kapsam"]
    with pytest.raises(ValueError, match="içerik yazım kapısını geçmedi"):
        identity.decision_units(bozuk, [])


def test_decision_units_refuses_an_invalid_log():
    """Fail-closed: şemayı geçmeyen günlükten anlık görüntü TÜRETİLMEZ.

    R6 bu eşlemeyi Task 9'un `validate_report(unit_snapshot=...)` girdisi
    yapıyor; geçersiz günlükten üretilmiş bir görüntü sessizce oraya akardı.
    """
    with pytest.raises(ValueError, match="karar günlüğü şemayı geçmedi"):
        identity.decision_units(_valid_content(), [_karar_row(karar="birlestir")])


# ─── 4. Kanonik yol grameri + çokluk ────────────────────────────────────────


def test_enumerate_covers_every_content_shape():
    """Yol grameri Plan 1 doğrulayıcısının izin verdiği HER şekli karşılar."""
    content = _valid_content()
    paths = set(identity.enumerate_content_units(content))
    assert "kapsam" in paths
    assert "cta_kaliplari[0]" in paths
    assert "kanca_kaliplari[0]" in paths
    assert "video_kodlar/hareket[0]" in paths
    assert "video_kodlar/sahne[1]" in paths
    assert f"ozel_gun/{CUMHURIYET_KEY}/mesaj_ekseni" in paths
    assert len(paths) == BEKLENEN_BIRIM_SAYISI, sorted(paths)


def test_duplicate_identical_text_gets_distinct_paths():
    """ÇOKLUK: iki özdeş metin AYNI hash'i taşır; ayıran şey SIRA ORDİNALİDİR."""
    content = _valid_content(kanca_kaliplari=["Aynı metin", "Aynı metin"])
    units = identity.enumerate_content_units(content)
    assert "kanca_kaliplari[0]" in units and "kanca_kaliplari[1]" in units
    assert (
        units["kanca_kaliplari[0]"]["oge_sha"] == units["kanca_kaliplari[1]"]["oge_sha"]
    ), "iki özdeş metin farklı hash aldı — kurgu bozuk"

    # Ordinal olmasaydı iki satır AYNI yola bağlanırdı: bir öğe sahipsiz kalır.
    rows = _log_for(content)
    for row in rows:
        if row["oge_yolu"] == "kanca_kaliplari[1]":
            row["oge_yolu"] = "kanca_kaliplari[0]"
    errors = identity.check_unit_integrity(content, rows)
    assert any("kanca_kaliplari[1]" in e for e in errors), errors


def test_two_special_days_with_identical_body_do_not_collide():
    """İki özel gün gövdesi birebir aynı olsa bile yollar ANAHTARLA ayrışır."""
    body = {
        "tur": "kutlama",
        "mesaj_ekseni": "Ortak sevinç",
        "kanca": "Bayram vitrinimiz hazır",
        "cta": "Mağazada görün",
        "gorsel_vurgu": "Warm accents",
    }
    content = _valid_content(
        ozel_gun={CUMHURIYET_KEY: dict(body), "ramazan-bayrami": dict(body)}
    )
    units = identity.enumerate_content_units(content)
    special = [p for p in units if p.startswith("ozel_gun/")]
    assert len(special) == 10, sorted(special)
    assert f"ozel_gun/{CUMHURIYET_KEY}/kanca" in units
    assert "ozel_gun/ramazan-bayrami/kanca" in units
    assert (
        units[f"ozel_gun/{CUMHURIYET_KEY}/kanca"]["oge_sha"]
        == units["ozel_gun/ramazan-bayrami/kanca"]["oge_sha"]
    ), "kurgu bozuk: gövdeler özdeş değil"


# ─── 5. İki yönlü bütünlük ──────────────────────────────────────────────────


def test_integrity_passes_on_consistent_package():
    """POZİTİF KONTROL — tutarlı paket hiç hata üretmez."""
    content = _valid_content()
    rows = _log_for(content)
    assert len(rows) == BEKLENEN_BIRIM_SAYISI, rows  # boş günlük bu testi kandırırdı
    assert identity.check_unit_integrity(content, rows) == []


def test_integrity_rejects_orphan_content_item():
    """İÇERİK → GÜNLÜK yönü: sahipsiz öğe kapsam kaçağıdır.

    Tek yönlü (yalnız günlük → içerik) bir kontrol bunu GÖREMEZ.
    """
    content = _valid_content()
    rows = [r for r in _log_for(content) if r["oge_yolu"] != "kanca_kaliplari[0]"]
    errors = identity.check_unit_integrity(content, rows)
    assert any(
        "sahipsiz öğe" in e and "kanca_kaliplari[0]" in e for e in errors
    ), errors


def test_integrity_rejects_ghost_unit():
    """GÜNLÜK → İÇERİK yönü: içerikte karşılığı olmayan birim hayalettir.

    Tek yönlü (yalnız içerik → günlük) bir kontrol bunu GÖREMEZ.
    """
    content = _valid_content()
    rows = _log_for(content)
    rows.append(
        _karar_row(
            alan="kanca_kaliplari",
            oge_yolu="kanca_kaliplari[42]",
            unit_id="ku-00000000dead",
            oge_sha="c" * 64,
        )
    )
    errors = identity.check_unit_integrity(content, rows)
    assert any(
        "hayalet birim" in e and "kanca_kaliplari[42]" in e for e in errors
    ), errors


def test_integrity_rejects_row_claiming_the_wrong_field():
    """F3: satır bir alanı iddia edip BAŞKA alanın yolunu sahiplenemez.

    `alan` zorunlu, dışa verilen ve denetçi anlık görüntüsüne kopyalanan bir
    alandır; yolla uzlaştırılmazsa satır `kanca_kaliplari` der, `kapsam`'ı
    sahiplenir ve bu uyuşmazlık envantere olduğu gibi geçerdi.
    """
    content = _valid_content()
    rows = _log_for(content)
    hedef = next(r for r in rows if r["oge_yolu"] == "kapsam")
    hedef["alan"] = "kanca_kaliplari"
    errors = identity.check_unit_integrity(content, rows)
    assert any("alan uyuşmazlığı" in e and "kapsam" in e for e in errors), errors


def test_integrity_rejects_stale_sha_on_correct_path():
    """Yol doğru, içerik kaymış: `oge_sha` taze hash'le eşleşmek ZORUNDA."""
    content = _valid_content()
    rows = _log_for(content)
    rows[0]["oge_sha"] = "d" * 64
    errors = identity.check_unit_integrity(content, rows)
    assert any("bayat oge_sha" in e and rows[0]["oge_yolu"] in e for e in errors), errors


def test_integrity_rejects_two_units_claiming_one_path():
    """Eşleme BİRE BİRDİR — iki birim aynı yolu sahiplenemez."""
    content = _valid_content()
    rows = _log_for(content)
    rows.append(
        _karar_row(
            alan=rows[0]["alan"],
            oge_yolu=rows[0]["oge_yolu"],
            unit_id="ku-00000000beef",
            oge_sha=rows[0]["oge_sha"],
        )
    )
    errors = identity.check_unit_integrity(content, rows)
    assert any("aynı yolu iki yaşayan birim" in e for e in errors), errors


def test_integrity_refuses_a_log_that_fails_the_schema():
    """Fail-closed: geçersiz günlükte bütünlük ÖLÇÜLMEZ, şema hatası döner."""
    content = _valid_content()
    rows = _log_for(content)
    rows[0]["aktor"] = "robot"
    errors = identity.check_unit_integrity(content, rows)
    assert any("aktor değeri kapalı kümenin dışında" in e for e in errors), errors


def test_first_package_assigns_new_id_to_every_enumerated_unit():
    """İlk paket: her sayılan birim YENİ kimlik alır, hiçbiri boşta kalmaz."""
    content = _valid_content()
    units = identity.enumerate_content_units(content)
    assert len(units) == BEKLENEN_BIRIM_SAYISI, sorted(units)  # boş sayım kandırırdı
    rows = _log_for(content, karar="ekle")
    derived = identity.decision_units(content, rows)
    assert len(derived) == len(units)
    assert {u["oge_yolu"] for u in derived.values()} == set(units)
    assert all(UNIT_ID_RE.match(uid) for uid in derived)
    assert identity.check_unit_integrity(content, rows) == []


# ─── 6. Şema göçü YOK ───────────────────────────────────────────────────────


def test_content_schema_unchanged_plan1_validator_still_passes():
    """Kimlik NEDEN günlükte yaşıyor: içeriğe yazılamıyor da ondan.

    Plan 1 doğrulayıcısı CTA öğesinin anahtar kümesini EŞİTLİK ile ölçer;
    `unit_id` eklenmiş öğe REDDEDİLİR. Bu test hem şemanın değişmediğini
    (pozitif kontrol) hem de değiştirilemeyeceğini (negatif kontrol) ölçer.
    """
    assert structural_errors(_valid_content()) == []

    kirli = _valid_content()
    kirli["cta_kaliplari"][0]["unit_id"] = identity.new_unit_id()
    errors = structural_errors(kirli)
    assert any("anahtar kümesi" in e for e in errors), errors


# ─── 7. Kanonik hash (K-92) ─────────────────────────────────────────────────


def test_canonical_sha_is_key_order_and_whitespace_independent():
    """Sıralı anahtar · boşluksuz — aynı değer AYNI hash."""
    a = identity.canonical_sha({"b": "iki", "a": "bir"})
    b = identity.canonical_sha({"a": "bir", "b": "iki"})
    assert a == b
    assert re.match(r"^[0-9a-f]{64}$", a), a


def test_canonical_sha_normalises_unicode_to_nfc():
    """NFC: aynı görünen iki kodlama AYNI hash üretir."""
    nfc = "\u00e7"  # tek kod noktası: ç
    nfd = "c\u0327"  # c + birleşen çengel
    assert nfc != nfd
    assert identity.canonical_sha(nfc) == identity.canonical_sha(nfd)


def test_canonical_sha_separates_different_values():
    """Negatif kontrol — farklı değer farklı hash."""
    assert identity.canonical_sha("a") != identity.canonical_sha("b")


# ─── 8. `donmus` — donmuş dataclass alanlarının TEK normalizasyon kuralı ────


@dataclass(frozen=True)
class _DonmusOge:
    """R6(e)'nin tuzağı: donmuş dataclass öğesi `donmus`'un KAPALI kümesinde YOK."""

    unit_id: str
    sebep: str


def test_donmus_returns_read_only_mapping():
    donduruldu = identity.donmus({"a": 1})
    with pytest.raises(TypeError):
        donduruldu["a"] = 2


def test_donmus_freezes_nested_values():
    donduruldu = identity.donmus({"dis": {"ic": [1, 2]}})
    assert donduruldu["dis"]["ic"] == (1, 2)
    with pytest.raises(TypeError):
        donduruldu["dis"]["ic2"] = 3


def test_donmus_does_not_alias_caller_object():
    """Takma ad kapanır: çağıranın nesnesi sonradan değişince dönen değer DEĞİŞMEZ."""
    kaynak = {"a": [1]}
    donduruldu = identity.donmus(kaynak)
    kaynak["a"].append(2)
    kaynak["b"] = 3
    assert donduruldu == {"a": (1,)}


def test_donmus_rejects_unknown_type():
    """Kapalı kümenin dışı → `TypeError` (fail-closed, sessiz geçiş YOK)."""
    with pytest.raises(TypeError):
        identity.donmus(object())


def test_donmus_rejects_a_frozen_dataclass_element():
    """Donmuş dataclass öğeli alanlar `donmus`'a VERİLMEZ — kural 5 düşürür."""
    with pytest.raises(TypeError):
        identity.donmus((_DonmusOge("ku-0123456789ab", "sebep"),))


def test_donmus_rejects_uncomparable_mapping_keys():
    """Hata KURALIN kendisinden gelir, `sorted`'ın iç mesajından değil."""
    with pytest.raises(TypeError, match="anahtarları karşılaştırılamıyor"):
        identity.donmus({1: "a", "b": "c"})


def test_donmus_is_idempotent():
    """POZİTİF KONTROL — iki kez çağrılması hata DEĞİLDİR."""
    deger = {"a": [1, {"b": {2, 3}}]}
    bir = identity.donmus(deger)
    assert identity.donmus(bir) == bir


def test_donmus_accepts_the_closed_scalar_set():
    """POZİTİF KONTROL — kapalı skaler kümesi olduğu gibi döner."""
    from datetime import date, datetime
    from decimal import Decimal
    from pathlib import Path
    from uuid import uuid4

    for value in (None, True, 3, 1.5, "x", b"x", Decimal("1.5"), uuid4(),
                  Path("/tmp"), datetime(2026, 1, 1), date(2026, 1, 1)):
        assert identity.donmus(value) == value


# ─── 9. Kanonik hash — ÖN-SERİLEŞTİRME kuralı (ekin bağladığı girdiler) ─────
#
# Ek (`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`) `canonical_sha`'ya
# iki girdi sınıfı BAĞLIYOR ve ikisi de düz `json.dumps`'tan geçmez:
#   * ek satır 1901 — `MADDE_KUMESI_SHA: str = identity.canonical_sha(MADDELER)`;
#     `MADDELER` donmuş `ChecklistItem` veri sınıflarından oluşan bir demettir
#     (ek satır 1884-1890);
#   * ek satır 1450-1464 — kanıt parmak izi yardımcıları `UUID` alanı taşıyan yükleri
#     aynı kurala verir (`package_id: UUID`, ek satır 1442).


@dataclass(frozen=True)
class _MaddeBenzeri:
    """Ekin `ChecklistItem`'ıyla AYNI şekil (ek satır 1884-1888): üç alan, donmuş."""

    madde_id: str
    sinif: str
    otomatik: bool


def test_canonical_sha_hashes_a_frozen_dataclass_tuple():
    """Ek satır 1901'in ta kendisi: donmuş veri sınıflarından oluşan demet."""
    maddeler = (
        _MaddeBenzeri("m-01", "kapi", True),
        _MaddeBenzeri("m-15", "sinyal", False),
    )
    sha = identity.canonical_sha(maddeler)
    assert re.match(r"^[0-9a-f]{64}$", sha), sha


def test_canonical_sha_of_a_dataclass_reads_field_names_not_positions():
    """Alan ADI kanonik dizinin parçasıdır — alan yeniden adlandırılırsa hash DEĞİŞİR."""

    @dataclass(frozen=True)
    class _BaskaAd:
        madde_kimligi: str
        sinif: str
        otomatik: bool

    assert identity.canonical_sha(
        _MaddeBenzeri("m-01", "kapi", True)
    ) != identity.canonical_sha(_BaskaAd("m-01", "kapi", True))


def test_canonical_sha_hashes_a_uuid_bearing_payload():
    """Ek satır 1442'nin kanıt yükü: `package_id: UUID` taşır."""
    from uuid import UUID as _UUID

    pid = _UUID("11111111-2222-3333-4444-555555555555")
    sha = identity.canonical_sha({"package_id": pid, "manager_approved": True})
    assert sha == identity.canonical_sha(
        {"package_id": str(pid), "manager_approved": True}
    )


def test_canonical_sha_hashes_path_decimal_and_temporal_scalars():
    """Kapalı kümenin geri kalanı: `Path` · `Decimal` · `date` · `datetime`."""
    from datetime import date as _date, datetime as _datetime
    from decimal import Decimal as _Decimal
    from pathlib import Path as _Path

    yuk = {
        "yol": _Path("/tmp/x"),
        "tutar": _Decimal("1.50"),
        "gun": _date(2026, 8, 31),
        "an": _datetime(2026, 8, 31, 12, 0, 0),
    }
    assert identity.canonical_sha(yuk) == identity.canonical_sha(
        {
            "yol": "/tmp/x",
            "tutar": "1.50",
            "gun": "2026-08-31",
            "an": "2026-08-31T12:00:00",
        }
    )


def test_canonical_sha_rejects_non_finite_numbers():
    """`nan`/`inf` geçerli JSON DEĞİLDİR — `json.dumps` onları sessizce yazardı."""
    for deger in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(TypeError):
            identity.canonical_sha({"x": deger})


def test_canonical_sha_rejects_outside_the_closed_set():
    """Fail-closed KORUNUR: kapalı kümenin dışı `TypeError` (docstring vaadi)."""
    for deger in (object(), b"bayt", {1, 2}, frozenset({1, 2})):
        with pytest.raises(TypeError):
            identity.canonical_sha(deger)


def test_canonical_sha_rejects_a_mutable_dataclass():
    """Donmamış veri sınıfı REDDEDİLİR — hash'lendikten sonra içi değişebilirdi."""

    @dataclass
    class _Degisken:
        a: str

    with pytest.raises(TypeError):
        identity.canonical_sha(_Degisken("x"))


# Bugünkü (HEAD 3d08db6) uygulamanın ÜRETTİĞİ özetler — ölçülerek alındı:
#   python -c "from app.services.sector_pipeline import identity; print(identity.canonical_sha(...))"
# Ön-serileştirme kuralı bunları DEĞİŞTİREMEZ; değiştirirse depodaki her
# `oge_sha` bir gecede bayatlar.
_PINLI_OZETLER = (
    (
        {"b": "iki", "a": ["bir", 2, True, None], "c": {"ic": "ç"}},
        "cc74e37e3b888e805b7fe689687a454036b6203b0bcd1f6640c89de9573d7972",
    ),
    ("kapsam", "18e70e0f8e727313a629dcc1a2671c5f0caf4c06fde1e33e902efea05061c019"),
    (["a", "b"], "0473ef2dc0d324ab659d3580c1134e9d812035905c4781fdd6d529b0c6860e13"),
)


@pytest.mark.parametrize("deger,beklenen", _PINLI_OZETLER)
def test_canonical_sha_keeps_existing_digests_byte_for_byte(deger, beklenen):
    """GERİLEME KAPISI — bugün çalışan girdiler için hash BİREBİR aynı kalır."""
    assert identity.canonical_sha(deger) == beklenen


# ─── Tamsayı büyüklüğü: ön-serileştirme kuralının AÇTIĞI gerileme (fix turu 2, F1)
#
# Ortak `isinstance(value, (int, float))` dalı `math.isfinite`'ı TAMSAYIYA da
# uyguluyordu. `math.isfinite` argümanını float'a çevirir, yani `10**309`
# `OverflowError` ile patlıyordu — ölçüldü:
#     10**308 -> OK          10**309 -> OverflowError    10**400 -> OverflowError
# Bu iki sözleşmeyi birden kırıyordu:
#   (1) **uyumluluk:** eski kural `10**309` için özet ÜRETİYORDU
#       (`7fe8362b13128003…`), yani depodaki bir `oge_sha` bir gecede
#       hesaplanamaz hâle gelirdi;
#   (2) **istisna tipi:** `canonical_sha` docstring'i "JSON'a çevrilemeyen bir
#       değer `TypeError` ile düşer (fail-closed)" der. `OverflowError`
#       `TypeError` DEĞİLDİR (`ArithmeticError` soyundandır) — fail-closed vaadi
#       sessizce başka bir istisna sınıfına kaydı.
# Kural: `bool` dalından sonra TAMSAYI değiştirilmeden geçer; sonluluk ölçüsü
# YALNIZ `float`'a uygulanır.

# `10**309` ve `10**400` için ön-serileştirme kuralından ÖNCEKİ (f15e640^)
# uygulamanın ürettiği özetler — ölçülerek alındı:
#   json.dumps(v, sort_keys=True, separators=(",",":"), ensure_ascii=False)
#   → NFC → sha256
_BUYUK_TAMSAYI_PINLERI = (
    (10**309, "7fe8362b13128003e89ec608904a096e71fefbfca5387afea114bd8f865f2dc6"),
    (10**400, "397fc6671f9e77a223078bf9d335b890a1f4cabb25d4aec954f70ef3a84788ee"),
)


@pytest.mark.parametrize("deger,beklenen", _BUYUK_TAMSAYI_PINLERI)
def test_canonical_sha_keeps_big_integer_digests_byte_for_byte(deger, beklenen):
    """GERİLEME KAPISI — float'a sığmayan tamsayı için özet ESKİSİYLE aynı."""
    assert identity.canonical_sha(deger) == beklenen


# KABUL EDİLEN tamsayı büyüklükleri × onları taşıyan KAPSAYICILAR — üretilmiş
# çarpım. Elle seçilmiş tek bir örnek tam da bu sınıfı kaçırmıştı: `10**308`
# geçiyor, `10**309` patlıyordu ve tek örnek yanlış tarafa düşebilirdi.
#
# **Büyüklük SINIRSIZ DEĞİLDİR.** Python'un süreç düzeyindeki ondalık dönüşüm
# sınırı (`sys.get_int_max_str_digits()`) aşıldığında tamsayı metne
# çevrilemez — ölçüldü (3.12.3, sınır 4300): 4300 basamaklı `10**4299` özet
# üretir, 4301 basamaklı `10**4300` düşer. Buradaki büyüklüklerin HEPSİ
# sınırın altındadır (en büyüğü 401 basamak) ve aşağıdaki kapsam testi bunu
# ölçerek bağlar; sınırın kendisi ayrı bir testle yoklanır.
_BUYUKLUKLER = (
    0,
    -1,
    2**53,
    10**308,
    10**309,
    -(10**309),
    10**400,
    2**1024,
)


def _kapsayicilar(deger):
    """Bir değeri her özyineleme yolundan geçiren KAPSAYICI biçimleri."""

    @dataclass(frozen=True)
    class _Donmus:
        x: object

    return {
        "ciplak": deger,
        "liste": [deger],
        "demet": (deger,),
        "esleme": {"a": deger},
        "donmus-veri-sinifi": _Donmus(deger),
        "ic-ice": {"a": [{"b": (deger,)}]},
    }


_BUYUKLUK_MATRISI = [
    (f"{ad}-{sira}", ad, sira, kap)
    for sira, deger in enumerate(_BUYUKLUKLER)
    for ad, kap in _kapsayicilar(deger).items()
]


@pytest.mark.parametrize(
    "kimlik,kapsayici_adi,sira,deger",
    _BUYUKLUK_MATRISI,
    ids=[h[0] for h in _BUYUKLUK_MATRISI],
)
def test_canonical_sha_accepts_integers_below_the_process_digit_limit(
    kimlik, kapsayici_adi, sira, deger
):
    """Süreç basamak sınırının ALTINDAKİ tamsayı hiçbir yolda REDDEDİLMEZ."""
    ozet = identity.canonical_sha(deger)
    assert re.fullmatch(r"[0-9a-f]{64}", ozet), (kimlik, ozet)


def test_the_integer_magnitude_matrix_covers_the_full_product():
    """Bir büyüklük ya da bir kapsayıcı sessizce düşerse burası DÜŞER."""
    assert len(_BUYUKLUK_MATRISI) == len(_BUYUKLUKLER) * 6 == 48
    assert {h[1] for h in _BUYUKLUK_MATRISI} == {
        "ciplak",
        "liste",
        "demet",
        "esleme",
        "donmus-veri-sinifi",
        "ic-ice",
    }
    # Matrisin adı "sınırın ALTI" diyor — ölç, iddia etme.
    sinir = sys.get_int_max_str_digits()
    assert all(len(f"{deger:d}".lstrip("-")) <= sinir for deger in _BUYUKLUKLER)


def test_canonical_sha_integer_digit_limit_is_the_process_setting():
    """Sınır SÜREÇ ayarından okunur (sabit gömülmez); iki yanı da ölçülür.

    Eşik `sys.get_int_max_str_digits()` BASAMAK sayısıdır: tam o kadar
    basamaklı tamsayı özet üretir, bir fazlası `TypeError` ile düşer. Sınır
    CPU/bellek korumasıdır ve YÜKSELTİLMEZ — test onu değiştirmeden yoklar.
    """
    sinir = sys.get_int_max_str_digits()

    tam_sinirda = 10 ** (sinir - 1)
    assert len(str(tam_sinirda)) == sinir
    ozet = identity.canonical_sha(tam_sinirda)
    assert re.fullmatch(r"[0-9a-f]{64}", ozet), ozet

    # Bir basamak fazlası: `str()` bile düşer, o yüzden basamak sayısı
    # doğrudan ölçülemez — üsten TÜRETİLİR (10**n → n+1 basamak).
    bir_ustu = 10**sinir
    with pytest.raises(TypeError):
        identity.canonical_sha(bir_ustu)


# ─── İstisna tipi SÖZLEŞMESİ — reddedilen her girdi sınıfı `TypeError` verir ──
#
# `canonical_sha` docstring'i tek bir istisna sınıfı vadeder. Vaat elle seçilmiş
# bir örnekle değil, ret yollarının ÜRETİLMİŞ listesiyle sınanır: `OverflowError`
# gerilemesi tam da "başka bir istisna sınıfına sessiz kayma"ydı ve tek örnek
# onu görmezdi.


def _reddedilen_degerler():
    """Bugünkü RET yollarının üretilmiş listesi: (ad, değer)."""

    @dataclass
    class _Degisken:
        a: str

    return [
        ("nan", float("nan")),
        ("inf", float("inf")),
        ("-inf", float("-inf")),
        ("kume", {1, 2}),
        ("donmus-kume", frozenset({1, 2})),
        ("donmamis-veri-sinifi", _Degisken("x")),
        ("bayt", b"bayt"),
        ("taninmayan-nesne", object()),
        ("karmasik-sayi", complex(1, 2)),
        # Süreç basamak sınırını AŞAN tamsayı: `json.dumps` bunu `ValueError`
        # ile düşürür ve `ValueError` `TypeError` DEĞİLDİR — vaat o yolda
        # sessizce başka bir istisna sınıfına kayıyordu.
        ("basamak-sinirini-asan-tamsayi", 10 ** sys.get_int_max_str_digits()),
    ]


_RET_MATRISI = [
    (f"{deger_adi}-icinde-{kap_adi}", kap)
    for deger_adi, deger in _reddedilen_degerler()
    for kap_adi, kap in _kapsayicilar(deger).items()
]


@pytest.mark.parametrize(
    "kimlik,deger", _RET_MATRISI, ids=[h[0] for h in _RET_MATRISI]
)
def test_canonical_sha_rejection_paths_raise_typeerror_and_nothing_else(kimlik, deger):
    """Fail-closed vaadi TİP düzeyinde: her ret yolu `TypeError`, başkası DEĞİL."""
    with pytest.raises(TypeError):
        identity.canonical_sha(deger)


def test_the_rejection_matrix_covers_the_full_product():
    """Bir ret sınıfı ya da bir kapsayıcı sessizce düşerse burası DÜŞER."""
    assert len(_RET_MATRISI) == 10 * 6 == 60
    assert len({h[0].split("-icinde-")[0] for h in _RET_MATRISI}) == 10
