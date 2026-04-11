import asyncpg
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse, UserMe

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=OkResponse)
async def me(user: dict = Depends(get_current_user)):
    """Return the authenticated user's id and email."""
    return OkResponse(data=UserMe(id=user["sub"], email=user.get("email", "")))


@router.get("/init", response_model=OkResponse)
async def init(
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    Uygulama başlangıcında tek çağrı ile tüm init verisini döndür:
    - Kullanıcı bilgileri
    - Workspace
    - Markalar

    Account yoksa oluşturur, workspace yoksa oluşturur.
    """
    user_id = user["sub"]
    email = user.get("email", "")
    name = user.get("user_metadata", {}).get("full_name") or email.split("@")[0]

    # Account al veya oluştur
    account = await db.fetchrow(
        """
        INSERT INTO social.accounts (id, email, name, last_login_at)
        VALUES ($1, $2, $3, now())
        ON CONFLICT (id) DO UPDATE SET last_login_at = now()
        RETURNING *
        """,
        user_id,
        email,
        name,
    )

    # Workspace al veya oluştur
    workspace = await db.fetchrow(
        "SELECT * FROM social.workspaces WHERE account_id = $1 ORDER BY created_at LIMIT 1",
        user_id,
    )
    if not workspace:
        workspace = await db.fetchrow(
            """
            INSERT INTO social.workspaces (account_id, name)
            VALUES ($1, $2)
            RETURNING *
            """,
            user_id,
            f"{name}'in Workspace'i",
        )
        # workspace_members'a ekle
        await db.execute(
            """
            INSERT INTO social.workspace_members (workspace_id, account_id, role)
            VALUES ($1, $2, 'owner')
            ON CONFLICT DO NOTHING
            """,
            workspace["id"],
            user_id,
        )

    # Markalar
    brands = await db.fetch(
        """
        SELECT id, name, sector, logo_light_url, logo_dark_url, is_active
        FROM social.brands
        WHERE workspace_id = $1 AND is_active = true
        ORDER BY created_at
        """,
        workspace["id"],
    )

    trial_ends_at = account.get("trial_ends_at")

    return OkResponse(
        data={
            "user": {
                "id": str(account["id"]),
                "email": account["email"],
                "name": account["name"] or email.split("@")[0],
                "plan_id": account.get("plan_id", "starter"),
                "trial_ends_at": trial_ends_at.isoformat() if trial_ends_at else None,
            },
            "workspace": {
                "id": str(workspace["id"]),
                "name": workspace["name"],
            },
            "brands": [dict(b) for b in brands],
        }
    )
