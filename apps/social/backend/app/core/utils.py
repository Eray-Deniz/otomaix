"""Shared helpers used by multiple routers/services."""

from __future__ import annotations

import json


def parse_brand_kit(raw) -> dict:
    """asyncpg bazen JSONB kolonunu string olarak döndürür — her ikisini de handle et."""
    if not raw:
        return {}
    if isinstance(raw, str):
        return json.loads(raw)
    return dict(raw)
