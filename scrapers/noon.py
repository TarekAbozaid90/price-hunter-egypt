# -*- coding: utf-8 -*-
"""سكرابر نون مصر — يعتمد على بيانات __NEXT_DATA__ المضمّنة في صفحة البحث
ملاحظة: نون بيغيّر هيكل البيانات من وقت للتاني، لو اتكسر راجع المفاتيح هنا.
"""
import json
import time

from bs4 import BeautifulSoup

from .base import HEADERS, Item, StoreResult, parse_price
from .net import describe_error, http_get

STORE = "noon"
STORE_NAME = "نون"


def _res(status, message="", items=None, t0=None, net=None):
    return StoreResult(
        STORE, STORE_NAME, status, message, items or [],
        elapsed_ms=_ms(t0),
        via=getattr(net, "via", "direct"),
        proxy=getattr(net, "proxy", ""),
    )


def search(query: str) -> StoreResult:
    t0 = time.time()
    try:
        r = http_get(
            "https://www.noon.com/egypt-ar/search/",
            params={"q": query},
            headers={**HEADERS, "Accept-Language": "ar-EG,ar;q=0.9"},
            store=STORE,
        )
    except Exception as e:  # noqa: BLE001
        return _res("error", f"تعذر الاتصال: {describe_error(e)}", t0=t0, net=e)

    if r.status_code in (401, 403, 429):
        return _res(
            "blocked",
            "الموقع حظر الطلب (Cloudflare) — محتاج بروكسي سكني من إعدادات Render "
            "(PROXY_URL) أو سيرفر داخل مصر",
            t0=t0, net=r,
        )
    if r.status_code != 200:
        return _res("error", f"HTTP {r.status_code}", t0=t0, net=r)

    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return _res(
            "error",
            "لم يتم العثور على بيانات الصفحة — ربما تغيّر هيكل الموقع أو إن الصفحة رجعت تحقق",
            t0=t0, net=r,
        )

    try:
        data = json.loads(script.string)
        hits = _find_hits(data)
    except Exception as e:  # noqa: BLE001
        return _res("error", f"فشل تحليل البيانات: {e}", t0=t0, net=r)

    items = []
    for h in hits:
        try:
            title = h.get("name") or h.get("title") or ""
            price = h.get("sale_price") or h.get("price")
            old = h.get("mrp") or h.get("regular_price")
            sku = h.get("sku") or h.get("url_key") or ""
            url = h.get("url") or (f"https://www.noon.com/egypt-ar/{sku}/p/" if sku else "")
            if url.startswith("/"):
                url = "https://www.noon.com" + url
            image = None
            img = h.get("image_key") or h.get("image")
            if img:
                image = img if str(img).startswith("http") else f"https://f.nooncdn.com/p/pnsku/{img}/45.jpg"
            if not title:
                continue
            items.append(Item(
                store=STORE,
                title=str(title),
                price=float(price) if price else None,
                old_price=float(old) if old else None,
                url=url,
                image=image,
            ))
        except Exception:
            continue

    status = "ok" if items else "empty"
    return _res(status, "" if items else "لا توجد نتائج مطابقة", items, t0, r)


def _find_hits(data):
    """يدور بشكل متكرر على قائمة المنتجات داخل شجرة JSON"""
    candidates = []

    def walk(node):
        if isinstance(node, dict):
            # شكل النتيجة في نون: dict فيه name + price أو hits
            for key in ("hits", "products", "items"):
                v = node.get(key)
                if isinstance(v, list) and v and isinstance(v[0], dict) and (
                    "price" in v[0] or "sale_price" in v[0]
                ):
                    candidates.append(v)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return max(candidates, key=len) if candidates else []


def _ms(t0):
    return int((time.time() - t0) * 1000)
