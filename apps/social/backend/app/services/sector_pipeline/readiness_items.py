"""İşletime hazırlık kontrol listesinin KANONİK madde kümesi (arayüz eki R9).

**Yalnız kimlik + sınıflandırma.** Değerlendirme mantığı burada YOKTUR (o Task
17'nindir), veritabanı YOKTUR. Modülün Task 8'de doğmasının sebebi R9'dur:
`runs.attest_readiness` (Task 8) `onaylandi`'yı bu kümeden TÜRETİR ve
`writeback.activate_from_snapshot` (Task 15) `MADDE_KUMESI_SHA`'ya karşı
karşılaştırır. Küme sonraki bir görevde doğsaydı iki tüketici de ileri-bağımlı
olurdu.

**Maddeler ÖLÇÜLEREK dolduruldu, uydurulmadı (İlke 9).** Kaynak: spec girdisi
`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` satır 2051-2078 —
"İşletime hazırlık kontrol listesi" tablosu, yirmi numaralı satır. `madde_id`
o tablodaki SIRA numarasından türetilir (`md-01` … `md-20`); metin tablodaki
madde başlığının kısaltılmış hâlidir ve tabloya karşı okunabilir.

**Sınıflandırma (plan Task 17, "KATMAN-2 AYRIMI" hükmü):** sonuç İDDİA EDEN
maddeler `sinyal`dir ve tamamlanma kapısına GİRMEZ. Ölçülen sayı: bugün TEK
madde bu sınıftadır — 15. madde (*"kör çıktı değerlendirmesinde sektörel
ayrışma gözlendi"*), çünkü spec girdisi onun için açıkça *"bu belgede kapıya
çevrilmez"* der. Kalan on dokuz madde `kapi` sınıfındadır.

**`otomatik` alanının dürüst etiketi.** Bu bayrak "otomatik ön-kontrolle
ölçülebilir mi" sorusunun BEYANIDIR ve Task 17'nin değerlendiricisi onu tüketir.
Bugün ÖLÇÜLMEMİŞTİR — çalışan bir değerlendirici henüz yoktur. Bayrak, maddenin
cevabını Plan 2'nin ürettiği bir artefakttan (koşu satırı · rapor · tasdik)
doğrudan okunabilenler için `True`, operatör beyanına dayananlar için `False`
kondu. Task 17 bir maddeyi ölçemediğini görürse bayrağı ORADA düzeltir; burada
"ölçüldü" diye sunulmaz.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.sector_pipeline import identity

MADDE_SINIFLARI: tuple[str, ...] = ("kapi", "sinyal")
"""Madde sınıfı — KAPALI, iki değer."""


@dataclass(frozen=True)
class ChecklistItem:
    """Kanonik hazırlık maddesi — kimlik + sınıf + ölçülebilirlik beyanı."""

    madde_id: str
    sinif: str
    otomatik: bool
    baslik: str

    def __post_init__(self) -> None:
        if type(self.madde_id) is not str or not self.madde_id.strip():
            raise ValueError("madde_id zorunlu")
        if self.sinif not in MADDE_SINIFLARI:
            raise ValueError(
                f"ChecklistItem.sinif kapalı kümenin dışında: {self.sinif!r} — "
                f"kabul edilenler: {list(MADDE_SINIFLARI)}"
            )
        if type(self.otomatik) is not bool:
            raise TypeError("otomatik bool olmalı — doğru-görünen değer kabul edilmez")
        if type(self.baslik) is not str or not self.baslik.strip():
            raise ValueError("baslik zorunlu")


MADDELER: tuple[ChecklistItem, ...] = (
    ChecklistItem("md-01", "kapi", False, "Alt sektör kapsamı ve kök sektörü onaylandı"),
    ChecklistItem("md-02", "kapi", False, "Bloklayıcı politika/teknik kararlar kapatıldı"),
    ChecklistItem("md-03", "kapi", True, "Güncel brief üç araçta aynı metinle çalıştırıldı"),
    ChecklistItem("md-04", "kapi", False, "Mekanik kapı raporu üretildi"),
    ChecklistItem("md-05", "kapi", True, "İki bağımsız ve kör hakem raporu üretildi"),
    ChecklistItem("md-06", "kapi", False, "URL örneklem kısıtları dürüstçe raporlandı"),
    ChecklistItem("md-07", "kapi", True, "Alan bazlı sentez ve karar günlüğü üretildi"),
    ChecklistItem("md-08", "kapi", False, "Aktif paketteki bütün kalıplar için karar kapsamı tam"),
    ChecklistItem("md-09", "kapi", True, "Motor şema/kanıt/mutabakat/fallback kontrollerini tamamladı"),
    ChecklistItem("md-10", "kapi", True, "Canonical diff, değişim oranları ve bariyer sonuçları üretildi"),
    ChecklistItem("md-11", "kapi", True, "Koşu sonucu activation_eligible"),
    ChecklistItem("md-12", "kapi", True, "Aday paket şema ve boyut doğrulamasından geçti"),
    ChecklistItem("md-13", "kapi", True, "Paketsiz prompt regresyonu byte-exact geçti"),
    ChecklistItem("md-14", "kapi", True, "Paketli prompt yapısal kontrolleri geçti"),
    ChecklistItem("md-15", "sinyal", False, "Kör çıktı değerlendirmesinde sektörel ayrışma gözlendi"),
    ChecklistItem("md-16", "kapi", True, "Bloklayıcı mevzuat/güvenlik uyuşmazlığı veya eksik karar yok"),
    ChecklistItem("md-17", "kapi", False, "Post sürüm damgası doğrulandı"),
    ChecklistItem("md-18", "kapi", False, "Aktivasyon ve geri alma prosedürü test edildi"),
    ChecklistItem("md-19", "kapi", True, "Yönetici koşu özetini ve anlık görüntüyü görerek onayladı"),
    ChecklistItem("md-20", "kapi", False, "Onay anındaki aktif sürüm motorun değerlendirdiği sürümle aynı"),
)
"""Spec §13.4'ün YİRMİ maddesi — KAPALI küme."""

KAPI_MADDELERI: frozenset[str] = frozenset(
    item.madde_id for item in MADDELER if item.sinif == "kapi"
)
SINYAL_MADDELERI: frozenset[str] = frozenset(
    item.madde_id for item in MADDELER if item.sinif == "sinyal"
)

MADDE_KIMLIKLERI: frozenset[str] = frozenset(item.madde_id for item in MADDELER)

MADDE_KUMESI_SHA: str = identity.canonical_sha(
    [
        {"madde_id": item.madde_id, "sinif": item.sinif, "otomatik": item.otomatik}
        for item in MADDELER
    ]
)
"""Kanonik madde kümesinin BUGÜNKÜ parmak izi — modül yüklenirken BİR KEZ hesaplanır.

Hem `runs.attest_readiness` bunu YAZAR, hem `writeback.activate_from_snapshot`
(Task 15) buna karşı KARŞILAŞTIRIR; iki yerde iki hesap YAZILMAZ. Madde
eklenince/çıkınca ya da bir maddenin sınıfı değişince değer değişir ve eski
tasdikler kendiliğinden GEÇERSİZLEŞİR.

`baslik` hash'e GİRMEZ: başlık bir insan etiketidir, bir yazım düzeltmesi eski
tasdikleri geçersizleştirmemelidir. Kimlik · sınıf · ölçülebilirlik ise kapının
anlamını değiştirir ve hash'e girer.
"""


def sinif(madde_id: str) -> str:
    """Maddenin sınıfı; tanınmayan kimlikte `KeyError` (fail-closed)."""
    for item in MADDELER:
        if item.madde_id == madde_id:
            return item.sinif
    raise KeyError(f"tanınmayan hazırlık maddesi: {madde_id!r}")
