# -*- coding: utf-8 -*-
"""موزّع البحث: بيوجّه كل متجر لسكرابره المناسب + قاطع دائرة بسيط.

قاطع الدائرة: لو متجر رفض الاتصال أو خد timeout، بنتخطاه لمدة قصيرة
عشان البحث اللي بعده يبقى سريع بدل ما يستنى نفس المهلة كل مرة.
"""
from __future__ import annotations

import time

from . import amazon, jumia, noon
from .base import StoreResult
from .generic import search as generic_search
from .stores import ALL_STORES, BY_KEY, StoreProfile

BESPOKE = {
    "jumia": jumia.search,
    "noon": noon.search,
    "amazon": amazon.search,
}

# مدة التخطي بالثواني حسب نوع الفشل
COOLDOWN_BLOCKED = 90
COOLDOWN_ERROR = 45

_cooldown: dict[str, tuple[float, str]] = {}


def _skip(profile: StoreProfile, seconds_left: int) -> StoreResult:
    return StoreResult(
        profile.key, profile.ar, "blocked",
        f"تم تخطي المتجر مؤقتًا بعد فشل سابق — هيتم إعادة المحاولة بعد ~{seconds_left} ثانية "
        f"(لو عندك بروكسي شغّله من PROXY_URL أو {profile.key.upper()}_PROXY)",
        elapsed_ms=0,
    )


def search_one(profile: StoreProfile, query: str) -> StoreResult:
    now = time.time()
    until, last_status = _cooldown.get(profile.key, (0.0, ""))
    if until > now:
        return _skip(profile, int(until - now))

    fn = BESPOKE.get(profile.key)
    try:
        result = fn(query) if fn is not None else generic_search(profile, query)
    except Exception as exc:  # noqa: BLE001
        _cooldown[profile.key] = (now + COOLDOWN_ERROR, "error")
        raise exc

    if result.status == "blocked":
        _cooldown[profile.key] = (now + COOLDOWN_BLOCKED, "blocked")
    elif result.status == "error":
        _cooldown[profile.key] = (now + COOLDOWN_ERROR, "error")
    else:
        _cooldown.pop(profile.key, None)
    return result


def reset_cooldowns() -> None:
    _cooldown.clear()


def cooldown_state() -> dict:
    now = time.time()
    return {k: int(v[0] - now) for k, v in _cooldown.items() if v[0] > now}


def search_all(query: str):
    """يرجع [(profile, StoreResult | Exception)] بالترتيب."""
    out = []
    for profile in ALL_STORES:
        try:
            out.append((profile, search_one(profile, query)))
        except Exception as exc:  # noqa: BLE001
            out.append((profile, exc))
    return out


__all__ = ["search_one", "search_all", "reset_cooldowns", "cooldown_state",
           "BESPOKE", "ALL_STORES", "BY_KEY"]
