# -*- coding: utf-8 -*-
"""إعدادات البروكسي — بتتقرأ من متغيرات البيئة (Render) أو من ملف .env محليًا.

الفكرة: مفيش أي بيانات بروكسي في الكود. كل حاجة بتتضاف كـ Environment Variable
في Render، وبمجرد الحفظ الخدمة بتعمل restart والبروكسي يشتغل على طول.

المتغيرات المدعومة (كلها اختيارية):
    PROXY_URL               بروكسي واحد لكل المتاجر
    PROXY_LIST              أكتر من بروكسي مفصولين بفاصلة أو سطر جديد (تدوير تلقائي)
    JUMIA_PROXY / NOON_PROXY / AMAZON_PROXY / BTECH_PROXY / VONTX_PROXY ...
                            بروكسي مخصص لمتجر معين (أو "off" لتعطيله)
                            أي متجر في سجل المتاجر بيقبل <KEY>_PROXY
    PROXY_HOST + PROXY_PORT (+ PROXY_USERNAME / PROXY_PASSWORD / PROXY_SCHEME)
                            بديل لو بياناتك مش في رابط واحد
    PROXY_ROTATE            round (افتراضي) | random | sticky
    PROXY_FALLBACK_DIRECT   لو 1 (افتراضي) يجرّب اتصال مباشر بعد فشل البروكسي
    SCRAPER_TIMEOUT         مهلة الطلب بالثواني (افتراضي 15)
    SCRAPER_RETRIES         عدد محاولات البروكسي في الطلب الواحد (افتراضي 2)
"""
from __future__ import annotations

import os
import random
import re
import threading
from urllib.parse import quote, urlsplit

# ملف .env محلي (اختياري) — في Render الاعتماد على Environment Variables
try:  # pragma: no cover
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # python-dotenv مش منصّب — عادي
    pass

STORES = (
    "jumia", "noon", "amazon",
    "vontx", "dream2000", "2b", "etisal",
    "dubaiphone", "btech", "miami", "raneen",
)

_OFF_VALUES = {"off", "none", "direct", "no", "false", "0", "disabled"}
_lock = threading.Lock()
_rotation_counter = 0


# ---------------------------------------------------------------- أدوات عامة
def _clean(value) -> str:
    return (value or "").strip().strip('"').strip("'")


def _is_off(value: str | None) -> bool:
    return _clean(value).lower() in _OFF_VALUES


def _valid_host(host: str | None) -> bool:
    if not host or " " in host:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9._:\-[\]]{1,253}", host))


def normalize_proxy(raw: str | None) -> str | None:
    """يحوّل أشكال البروكسي الشائعة لصيغة موحّدة صالحة لـ httpx.

    المدعوم:
        http://user:pass@host:port
        https://user:pass@host:port
        socks5://user:pass@host:port
        host:port
        user:pass@host:port
        host:port:user:pass        (شكل شائع عند بعض المزودين)
    """
    value = _clean(raw)
    if not value or _is_off(value):
        return None

    # host:port:user:pass  ← بنعيد بناء الرابط مع ترميز آمن لبيانات الدخول
    if "://" not in value:
        parts = value.split(":", 3)
        if len(parts) == 4 and parts[1].isdigit() and parts[2] and parts[3]:
            host, port, user, password = parts
            if not _valid_host(host) or not (0 < int(port) < 65536):
                return None
            auth = f"{quote(user, safe='')}:{quote(password, safe='')}"
            return f"http://{auth}@{host}:{int(port)}"

    if "://" not in value:
        value = "http://" + value

    scheme = value.split("://", 1)[0].lower()
    if scheme not in ("http", "https", "socks5", "socks5h"):
        return None
    try:
        parsed = urlsplit(value)
        port = parsed.port  # ممكن يرفع ValueError لو المنفذ غلط
    except ValueError:
        return None
    if not _valid_host(parsed.hostname):
        return None
    if port is not None and not (0 < port < 65536):
        return None
    return value


def mask_proxy(url: str | None) -> str:
    """يخفي اسم المستخدم والباسورد قبل عرض البروكسي في أي واجهة أو API."""
    if not url:
        return ""
    try:
        parts = urlsplit(url)
        auth = ""
        if parts.username:
            auth = f"{parts.username}:***@"
        elif parts.password:
            auth = "***@"
        port = f":{parts.port}" if parts.port else ""
        return f"{parts.scheme}://{auth}{parts.hostname or '?'}{port}"
    except Exception:
        return "***"


def _split_list(raw: str | None) -> list[str]:
    return [p.strip() for p in re.split(r"[,\n;]+", raw or "") if p.strip()]


def _from_parts() -> str | None:
    host = _clean(os.getenv("PROXY_HOST"))
    port = _clean(os.getenv("PROXY_PORT"))
    if not (host and port):
        return None
    user = _clean(os.getenv("PROXY_USERNAME") or os.getenv("PROXY_USER"))
    password = _clean(os.getenv("PROXY_PASSWORD") or os.getenv("PROXY_PASS"))
    scheme = (_clean(os.getenv("PROXY_SCHEME")) or "http").lower()
    auth = f"{user}:{password}@" if user else ""
    return normalize_proxy(f"{scheme}://{auth}{host}:{port}")


def _order(candidates: list[tuple[str, str]], source: str) -> list[tuple[str, str]]:
    """ترتيب المرشحين حسب وضع التدوير المطلوب."""
    global _rotation_counter
    mode = (_clean(os.getenv("PROXY_ROTATE")) or "round").lower()

    if mode in ("sticky", "fixed", "static"):
        return candidates
    if mode == "random":
        shuffled = candidates[:]
        random.shuffle(shuffled)
        return shuffled
    # round-robin
    with _lock:
        start = _rotation_counter % len(candidates)
        _rotation_counter += 1
    return candidates[start:] + candidates[:start]


def proxy_candidates(store: str | None = None) -> list[tuple[str, str]]:
    """كل البروكسيات اللي ممكن تُجرَّب للطلب ده بالترتيب.

    بيرجع list من (proxy_url, source). قائمة فاضية = اتصال مباشر.
    """
    # بروكسي مخصص لمتجر معين (+ إمكانية تعطيله بـ off)
    if store:
        raw = os.getenv(f"{store.upper()}_PROXY")
        if raw is not None and _clean(raw):
            if _is_off(raw):
                return []
            specific = normalize_proxy(raw)
            if specific:
                return [(specific, f"{store.upper()}_PROXY")]

    proxies: list[str] = []
    for item in _split_list(os.getenv("PROXY_LIST")):
        normalized = normalize_proxy(item)
        if normalized:
            proxies.append(normalized)
    if proxies:
        ordered = _order([(p, "PROXY_LIST") for p in proxies], "PROXY_LIST")
        return ordered

    single = normalize_proxy(os.getenv("PROXY_URL"))
    if single:
        return [(single, "PROXY_URL")]

    parts = _from_parts()
    if parts:
        return [(parts, "PROXY_HOST")]

    # متغيرات البيئة القياسية (بتفيد لو استخدمت مزود بيحطها تلقائيًا)
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        standard = normalize_proxy(os.getenv(key))
        if standard:
            return [(standard, key)]

    return []


def unique_proxies(limit: int = 3) -> list[tuple[str, str]]:
    """بروكسيات فريدة لاختبار الاتصال من /api/proxy-info."""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    pools = [proxy_candidates(store) for store in (None, *STORES)]
    for pool in pools:
        for url, source in pool:
            if url in seen:
                continue
            seen.add(url)
            result.append((url, source))
            if len(result) >= limit:
                return result
    return result


# ------------------------------------------------------------------ إعدادات
def timeout() -> float:
    try:
        return max(3.0, float(_clean(os.getenv("SCRAPER_TIMEOUT")) or 8))
    except (TypeError, ValueError):
        return 8.0


def retries() -> int:
    try:
        return max(1, min(5, int(_clean(os.getenv("SCRAPER_RETRIES")) or 2)))
    except (TypeError, ValueError):
        return 2


def fallback_direct() -> bool:
    raw = _clean(os.getenv("PROXY_FALLBACK_DIRECT")) or "1"
    return raw.lower() not in ("0", "false", "no", "off")


def proxy_enabled(store: str | None = None) -> bool:
    return bool(proxy_candidates(store))


def configured_env_keys() -> dict:
    """أي متغيرات البروكسي متواجدة فعلًا (بدون قيم) — مفيدة للتشخيص."""
    keys = (
        "PROXY_URL", "PROXY_LIST", "PROXY_HOST", "PROXY_PORT",
        "PROXY_USERNAME", "PROXY_PASSWORD", "PROXY_ROTATE",
    )
    return {key: bool(_clean(os.getenv(key))) for key in keys}


def public_status() -> dict:
    """حالة البروكسي بشكل آمن للعرض (من غير أي بيانات دخول)."""
    stores: dict[str, dict] = {}
    for store in STORES:
        pool = proxy_candidates(store)
        stores[store] = {
            "enabled": bool(pool),
            "masked": mask_proxy(pool[0][0]) if pool else "",
            "source": pool[0][1] if pool else "",
        }

    for_test = unique_proxies()
    return {
        "enabled": any(info["enabled"] for info in stores.values()),
        "masked": mask_proxy(for_test[0][0]) if for_test else "",
        "source": for_test[0][1] if for_test else "",
        "count": len({url for url, _ in for_test}) if for_test else 0,
        "rotation": (_clean(os.getenv("PROXY_ROTATE")) or "round").lower(),
        "fallback_direct": fallback_direct(),
        "timeout_sec": timeout(),
        "stores": stores,
    }
