"""Phase 6 — Sektör listesi endpoint'i.

Frontend (onboarding, marka oluşturma, marka ayarları) artık sektör listesini
hardcoded const yerine bu endpoint'ten çeker. Tek doğruluk kaynağı: social.sectors.
"""

import asyncpg
from fastapi import APIRouter, Depends

from app.core.cache import get_cached, set_cached
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/sectors", tags=["sectors"])

# v2: liste YALNIZ kök sektörleri döndürür (R-02); sürüm artışı eski
# filtresiz değeri devre dışı bırakır.
_CACHE_KEY = "otomaix:social:sectors:list:v2"
_TTL = 3600  # 1 saat — sektörler neredeyse hiç değişmez


@router.get("", response_model=OkResponse)
async def list_sectors(db: asyncpg.Connection = Depends(get_db)):
    """Kök sektörleri döndürür (auth gerekmez — onboarding'de de kullanılır).

    R-02: alt sektör satırları bu listeye GİRMEZ. Üç frontend tüketicisi
    (onboarding, marka oluşturma, marka ayarları) bugünkü listeyi aynen görür;
    alt sektör ataması ayrı bir akıştır.
    """
    cached = await get_cached(_CACHE_KEY)
    if cached is not None:
        return OkResponse(data=cached)

    rows = await db.fetch(
        """
        SELECT id::text, slug, display_name, parent_sector_id::text, keywords
        FROM social.sectors
        WHERE parent_sector_id IS NULL
        ORDER BY display_name
        """
    )
    data = [dict(r) for r in rows]
    await set_cached(_CACHE_KEY, data, _TTL)
    return OkResponse(data=data)


# Aday kümesinin KANONİK sorgusu (spec §7.2). Tek doğruluk kaynağı burasıdır:
# ayrı görünüm, materyalize kopya ya da önbellek TUTULMAZ — paket deaktive
# olduğu an satır listeden düşmelidir. Kök liste (`_CACHE_KEY`) önbellekli
# kalır çünkü orada bayatlayan şey taksonomi, burada bayatlayacak olan ise
# paketin canlı durumudur.
_SUB_SECTOR_CANDIDATES_SQL = """
    SELECT s.id::text, s.slug, s.display_name
    FROM social.sectors s
    WHERE s.parent_sector_id IS NOT NULL
      AND EXISTS (
          SELECT 1 FROM social.sector_packages p
          WHERE p.sector_id = s.id AND p.status = 'active'
      )
    ORDER BY s.display_name
"""


async def fetch_sub_sector_candidates(db: asyncpg.Connection) -> list[dict]:
    """Aday alt sektörler — aktif paketi olanlar (spec §7.2).

    İki tüketici vardır ve kümesi KAPALIDIR: bu modüldeki açılır-liste ucu ve
    `ai.py`'deki öneri çağrısı. Üretim akışı buraya HİÇ uğramaz (spec §7.1
    sürtünme yasağı) — yapısal olarak `tests/test_assignment_flow.py`
    taranır.
    """
    rows = await db.fetch(_SUB_SECTOR_CANDIDATES_SQL)
    return [dict(r) for r in rows]


@router.get("/sub-sector-candidates", response_model=OkResponse)
async def list_sub_sector_candidates(
    db: asyncpg.Connection = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Atama açılır listesinin beslendiği aday küme.

    Kök liste (`GET /sectors`) aksine kimlik ISTER: bu uç, hangi sektörlerde
    aktif paket bulunduğunu — yani ürünün yayılma durumunu — söyler ve iki
    tüketici yüzeyi de (onboarding, marka ayarları) oturum açmış kullanıcıya
    aittir. Dar olan taraf seçilir.

    Aday yoksa yanıt BOŞ LİSTEdir; bileşen o durumda pasif kalır.
    """
    return OkResponse(data=await fetch_sub_sector_candidates(db))
