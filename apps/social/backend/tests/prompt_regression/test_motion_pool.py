"""Katman-1: kamera hareketi havuzu (plan Task 7).

Havuz Claude'a gitmez — fal.ai'ye giden metnin bir parçasıdır. Yine de Katman-1
setinde: sektör paketi (K-02 `video_kodlar`) ileride BU havuzun yerine geçmeye
aday, o yüzden bugünkü içerik bayt-bayt pinlenir ve seçimin havuzdan geldiği
davranış olarak kanıtlanır.
"""

from __future__ import annotations

import random

from app.services import short_video

from .capture import assert_matches_fixture


def _render_pool(pool: list[str]) -> str:
    """Havuzu deterministik, sıra-duyarlı metne çevirir."""
    return "".join(f"[{index}] {item}\n" for index, item in enumerate(pool))


def test_motion_pool_bytes_pinned():
    """Havuzun İÇERİĞİ ve SIRASI dondurulur — ikisi de davranışı etkiler."""
    assert_matches_fixture(
        "short_video__motion_pool", _render_pool(short_video._MOTION_PROMPTS)
    )


def test_motion_pick_draws_from_pool(monkeypatch):
    """Seçim havuzdan yapılır — sabit bir metin dönmez.

    `random.choice`'a verilen dizinin havuzun KENDİSİ olduğu doğrulanır; sonucun
    havuzda olmasını sınamak yetmezdi (sabit bir eleman döndüren bir bozulma
    o testten geçerdi).
    """
    seen: list[list[str]] = []
    original_choice = random.choice

    def _spy(sequence):
        seen.append(list(sequence))
        return original_choice(sequence)

    monkeypatch.setattr(random, "choice", _spy)

    picks = [short_video._pick_motion_prompt() for _ in range(20)]

    assert len(seen) == 20, "seçim `random.choice` üzerinden yapılmadı"
    assert all(sequence == short_video._MOTION_PROMPTS for sequence in seen)
    assert all(pick in short_video._MOTION_PROMPTS for pick in picks)
