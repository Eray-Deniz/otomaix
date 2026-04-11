"""Paddle ödeme ve abonelik yönetimi endpoint'leri.

GET  /billing/current          → mevcut abonelik bilgisi + kullanım istatistikleri
POST /billing/checkout         → Paddle checkout URL oluştur
POST /billing/portal           → Paddle customer portal URL oluştur
POST /webhooks/paddle          → Paddle webhook olaylarını işle
GET  /billing/plans            → tüm planlar ve limitleri döndür
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone

import asyncpg
import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/billing", tags=["billing"])


# ─── Plan tanımları (frontend için statik) ────────────────────────────────────

PLANS = [
    {
        "id": "starter",
        "name": "Starter",
        "price_try": 499,
        "max_brands": 1,
        "max_posts_per_month": 50,
        "max_storage_gb": 1,
        "can_use_video": False,
        "can_use_avatar": False,
        "features": [
            "1 marka",
            "Aylık 50 içerik",
            "2 platform",
            "Temel şablonlar",
        ],
    },
    {
        "id": "pro",
        "name": "Pro",
        "price_try": 999,
        "max_brands": 3,
        "max_posts_per_month": 200,
        "max_storage_gb": 5,
        "can_use_video": True,
        "can_use_avatar": False,
        "features": [
            "3 marka",
            "Aylık 200 içerik",
            "5 platform",
            "Faceless Video",
            "Rakip analizi",
        ],
        "popular": True,
    },
    {
        "id": "business",
        "name": "Business",
        "price_try": 2499,
        "max_brands": 10,
        "max_posts_per_month": None,
        "max_storage_gb": 20,
        "can_use_video": True,
        "can_use_avatar": True,
        "features": [
            "10 marka",
            "Sınırsız içerik",
            "10 platform",
            "Faceless Video + AI Avatar",
            "Öncelikli destek",
        ],
    },
    {
        "id": "agency",
        "name": "Agency",
        "price_try": 4999,
        "max_brands": None,
        "max_posts_per_month": None,
        "max_storage_gb": 50,
        "can_use_video": True,
        "can_use_avatar": True,
        "features": [
            "Sınırsız marka",
            "Sınırsız içerik",
            "Sınırsız platform",
            "White-label",
            "Dedicated destek",
        ],
    },
]

PADDLE_PRICE_IDS: dict[str, str] = {
    # Coolify env'e eklenecek: PADDLE_PRICE_STARTER, PADDLE_PRICE_PRO vb.
    "starter":  getattr(settings, "PADDLE_PRICE_STARTER", ""),
    "pro":      getattr(settings, "PADDLE_PRICE_PRO", ""),
    "business": getattr(settings, "PADDLE_PRICE_BUSINESS", ""),
    "agency":   getattr(settings, "PADDLE_PRICE_AGENCY", ""),
}


# ─── Yardımcı fonksiyonlar ────────────────────────────────────────────────────

async def _get_or_create_account(user: dict, db: asyncpg.Connection) -> dict:
    """JWT'den account kaydını bul veya oluştur."""
    user_id = user["sub"]
    email = user.get("email", "")
    row = await db.fetchrow("SELECT * FROM social.accounts WHERE id = $1", user_id)
    if not row:
        row = await db.fetchrow(
            """
            INSERT INTO social.accounts (id, email, plan_id)
            VALUES ($1, $2, 'starter')
            ON CONFLICT (email) DO UPDATE SET last_login_at = now()
            RETURNING *
            """,
            user_id,
            email,
        )
    return dict(row)


async def _get_subscription(account_id: str, db: asyncpg.Connection) -> dict | None:
    row = await db.fetchrow(
        "SELECT * FROM social.subscriptions WHERE account_id = $1 ORDER BY created_at DESC LIMIT 1",
        account_id,
    )
    return dict(row) if row else None


async def _get_plan_limits(plan_id: str, db: asyncpg.Connection) -> dict:
    row = await db.fetchrow(
        "SELECT * FROM social.plan_limits WHERE plan_id = $1",
        plan_id,
    )
    if row:
        return dict(row)
    # Varsayılan: starter
    return {
        "plan_id": "starter",
        "max_brands": 1,
        "max_posts_per_month": 50,
        "max_storage_gb": 1,
        "can_use_video": False,
        "can_use_avatar": False,
    }


async def _get_this_month_post_count(account_id: str, db: asyncpg.Connection) -> int:
    row = await db.fetchrow(
        """
        SELECT COUNT(*) as cnt
        FROM social.posts p
        JOIN social.brands b ON b.id = p.brand_id
        JOIN social.workspaces w ON w.id = b.workspace_id
        WHERE w.account_id = $1
          AND p.created_at >= date_trunc('month', now())
        """,
        account_id,
    )
    return int(row["cnt"]) if row else 0


async def _get_brand_count(account_id: str, db: asyncpg.Connection) -> int:
    row = await db.fetchrow(
        """
        SELECT COUNT(*) as cnt
        FROM social.brands b
        JOIN social.workspaces w ON w.id = b.workspace_id
        WHERE w.account_id = $1 AND b.is_active = true
        """,
        account_id,
    )
    return int(row["cnt"]) if row else 0


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/plans", response_model=OkResponse)
async def get_plans():
    """Tüm plan bilgilerini döndür (auth gerekmez)."""
    return OkResponse(data=PLANS)


@router.get("/current", response_model=OkResponse)
async def get_current_subscription(
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Mevcut abonelik + kullanım istatistikleri."""
    account = await _get_or_create_account(user, db)
    account_id = str(account["id"])
    plan_id = account.get("plan_id") or "starter"

    subscription = await _get_subscription(account_id, db)
    limits = await _get_plan_limits(plan_id, db)
    post_count = await _get_this_month_post_count(account_id, db)
    brand_count = await _get_brand_count(account_id, db)

    return OkResponse(
        data={
            "plan_id": plan_id,
            "subscription": subscription,
            "limits": limits,
            "usage": {
                "posts_this_month": post_count,
                "brands": brand_count,
            },
            "upgrade_url": f"{settings.APP_URL}/fiyatlandirma",
        }
    )


class CheckoutRequest(BaseModel):
    plan_id: str


@router.post("/checkout", response_model=OkResponse)
async def create_checkout(
    payload: CheckoutRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Paddle checkout URL oluştur."""
    if not settings.PADDLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Ödeme sistemi henüz yapılandırılmadı. Lütfen destek ile iletişime geçin.",
        )

    price_id = PADDLE_PRICE_IDS.get(payload.plan_id)
    if not price_id:
        raise HTTPException(status_code=400, detail=f"Geçersiz plan: {payload.plan_id}")

    account = await _get_or_create_account(user, db)
    email = account.get("email") or user.get("email", "")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.paddle.com/transactions",
                headers={
                    "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "items": [{"price_id": price_id, "quantity": 1}],
                    "customer": {"email": email},
                    "custom_data": {"account_id": str(account["id"]), "plan_id": payload.plan_id},
                    "checkout": {
                        "url": f"{settings.APP_URL}/faturalandirma?success=1",
                    },
                },
            )
            data = resp.json()
            checkout_url = data.get("data", {}).get("checkout", {}).get("url")
            if not checkout_url:
                raise HTTPException(status_code=502, detail="Paddle checkout URL alınamadı")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Ödeme servisi ile bağlantı kurulamadı")

    return OkResponse(data={"checkout_url": checkout_url})


@router.post("/portal", response_model=OkResponse)
async def get_customer_portal(
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Paddle müşteri portalı URL'si döndür (fatura geçmişi, iptal vb.)."""
    if not settings.PADDLE_API_KEY:
        raise HTTPException(status_code=503, detail="Ödeme sistemi yapılandırılmadı")

    account = await _get_or_create_account(user, db)
    subscription = await _get_subscription(str(account["id"]), db)

    if not subscription or not subscription.get("paddle_customer_id"):
        raise HTTPException(status_code=404, detail="Aktif abonelik bulunamadı")

    customer_id = subscription["paddle_customer_id"]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"https://api.paddle.com/customers/{customer_id}/auth-token",
                headers={"Authorization": f"Bearer {settings.PADDLE_API_KEY}"},
            )
            data = resp.json()
            token = data.get("data", {}).get("customer_auth_token")
            if not token:
                raise HTTPException(status_code=502, detail="Portal token alınamadı")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Ödeme servisi ile bağlantı kurulamadı")

    portal_url = f"https://customer.paddle.com?customerAuthToken={token}"
    return OkResponse(data={"portal_url": portal_url})


# ─── Paddle Webhook ───────────────────────────────────────────────────────────

def _verify_paddle_signature(body: bytes, signature_header: str | None) -> bool:
    """Paddle webhook imzasını doğrula (h1 scheme)."""
    if not settings.PADDLE_WEBHOOK_SECRET or not signature_header:
        return True  # Secret yoksa doğrulamayı atla (geliştirme)

    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(";"))
        ts = parts.get("ts", "")
        h1 = parts.get("h1", "")
        signed_payload = f"{ts}:{body.decode()}"
        expected = hmac.new(
            settings.PADDLE_WEBHOOK_SECRET.encode(),
            signed_payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, h1)
    except Exception:
        return False


router_webhooks = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router_webhooks.post("/paddle", response_model=OkResponse)
async def paddle_webhook(
    request: Request,
    db: asyncpg.Connection = Depends(get_db),
    paddle_signature: str | None = Header(default=None, alias="Paddle-Signature"),
):
    """Paddle webhook olaylarını işle."""
    body = await request.body()

    if not _verify_paddle_signature(body, paddle_signature):
        raise HTTPException(status_code=401, detail="Geçersiz webhook imzası")

    event = json.loads(body)
    event_type: str = event.get("event_type", "")
    data: dict = event.get("data", {})

    if event_type in ("subscription.created", "subscription.updated"):
        custom_data = data.get("custom_data") or {}
        account_id = custom_data.get("account_id")
        plan_id = custom_data.get("plan_id", "starter")

        if not account_id:
            # customer_id üzerinden account bul
            customer_id = data.get("customer_id")
            row = await db.fetchrow(
                "SELECT account_id FROM social.subscriptions WHERE paddle_customer_id = $1",
                customer_id,
            )
            account_id = str(row["account_id"]) if row else None

        if account_id:
            period_end = None
            current_period = data.get("current_billing_period", {})
            if current_period.get("ends_at"):
                try:
                    period_end = datetime.fromisoformat(current_period["ends_at"].replace("Z", "+00:00"))
                except ValueError:
                    pass

            await db.execute(
                """
                INSERT INTO social.subscriptions
                    (account_id, paddle_subscription_id, paddle_customer_id,
                     plan_id, status, current_period_end)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (paddle_subscription_id) DO UPDATE SET
                    plan_id = EXCLUDED.plan_id,
                    status = EXCLUDED.status,
                    current_period_end = EXCLUDED.current_period_end,
                    updated_at = now()
                """,
                account_id,
                data.get("id"),
                data.get("customer_id"),
                plan_id,
                data.get("status", "active"),
                period_end,
            )

            await db.execute(
                "UPDATE social.accounts SET plan_id = $2 WHERE id = $1",
                account_id,
                plan_id,
            )

    elif event_type == "subscription.cancelled":
        sub_id = data.get("id")
        if sub_id:
            await db.execute(
                """
                UPDATE social.subscriptions
                SET status = 'cancelled', updated_at = now()
                WHERE paddle_subscription_id = $1
                """,
                sub_id,
            )
            row = await db.fetchrow(
                "SELECT account_id FROM social.subscriptions WHERE paddle_subscription_id = $1",
                sub_id,
            )
            if row:
                await db.execute(
                    "UPDATE social.accounts SET plan_id = 'starter' WHERE id = $1",
                    row["account_id"],
                )

    return OkResponse(data={"received": True, "event_type": event_type})


# ─── Plan limit kontrolü ──────────────────────────────────────────────────────

async def check_plan_limit(
    account_id: str,
    feature: str,  # "post" | "brand" | "video" | "avatar"
    db: asyncpg.Connection,
) -> None:
    """
    Plan limitini kontrol et.
    Limit aşılmışsa HTTP 402 döner.
    """
    account = await db.fetchrow(
        "SELECT plan_id FROM social.accounts WHERE id = $1", account_id
    )
    plan_id = account["plan_id"] if account else "starter"
    limits = await _get_plan_limits(plan_id, db)

    upgrade_url = f"{settings.APP_URL}/fiyatlandirma"

    if feature == "post":
        max_posts = limits.get("max_posts_per_month")
        if max_posts is not None:
            count_row = await db.fetchrow(
                """
                SELECT COUNT(*) as cnt FROM social.posts p
                JOIN social.brands b ON b.id = p.brand_id
                JOIN social.workspaces w ON w.id = b.workspace_id
                WHERE w.account_id = $1
                  AND p.created_at >= date_trunc('month', now())
                """,
                account_id,
            )
            used = int(count_row["cnt"]) if count_row else 0
            if used >= max_posts:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "plan_limit_reached",
                        "message": f"Bu ay {max_posts} içerik limitine ulaştınız.",
                        "upgrade_url": upgrade_url,
                        "current_plan": plan_id,
                    },
                )

    elif feature == "brand":
        max_brands = limits.get("max_brands")
        if max_brands is not None:
            count_row = await db.fetchrow(
                """
                SELECT COUNT(*) as cnt FROM social.brands b
                JOIN social.workspaces w ON w.id = b.workspace_id
                WHERE w.account_id = $1 AND b.is_active = true
                """,
                account_id,
            )
            used = int(count_row["cnt"]) if count_row else 0
            if used >= max_brands:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "plan_limit_reached",
                        "message": f"Planınız en fazla {max_brands} marka destekler.",
                        "upgrade_url": upgrade_url,
                        "current_plan": plan_id,
                    },
                )

    elif feature == "video" and not limits.get("can_use_video"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "plan_limit_reached",
                "message": "Video özelliği Pro planında mevcut.",
                "upgrade_url": upgrade_url,
                "current_plan": plan_id,
            },
        )

    elif feature == "avatar" and not limits.get("can_use_avatar"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "plan_limit_reached",
                "message": "AI Avatar özelliği Business planında mevcut.",
                "upgrade_url": upgrade_url,
                "current_plan": plan_id,
            },
        )
