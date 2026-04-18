"""Phase 7 — GET /templates endpoint'i.

Public endpoint (JWT gerekmez) — şablon listesi hassas bilgi içermez.
1 saatlik HTTP cache (Cache-Control: public, max-age=3600) ile frontend/CDN cache'ine dostane.
"""
from fastapi import APIRouter, Query, Response

from app.core.templates_data import get_all_templates, get_template_by_id
from app.models.schemas import OkResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=OkResponse)
async def list_templates(
    response: Response,
    sector: str | None = Query(None, description="Sektör slug (ör. e-ticaret-perakende). None → tüm şablonlar."),
    content_type: str | None = Query(None, description="İçerik tipi filtresi (image | carousel | video)."),
):
    """Sektör + içerik tipine göre filtrelenmiş şablon listesi."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    templates = get_all_templates(sector=sector, content_type=content_type)
    return OkResponse(
        data={
            "templates": [t.model_dump() for t in templates],
            "version": "1.0",
            "count": len(templates),
        }
    )


@router.get("/{template_id}", response_model=OkResponse)
async def get_template(template_id: str, response: Response):
    """Tekil şablon detayı."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    tpl = get_template_by_id(template_id)
    if not tpl:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Template not found")
    return OkResponse(data=tpl.model_dump())
