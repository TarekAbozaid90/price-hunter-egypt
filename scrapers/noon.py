# -*- coding: utf-8 -*-
"""سكرابر نون مصر — يعتمد على بيانات __NEXT_DATA__ المضمّنة في صفحة البحث
ملاحظة: نون بيغيّر هيكل البيانات من وقت للتاني، لو اتكسر راجع المفاتيح هنا.
"""
import json
import time
import httpx
from bs4 import BeautifulSoup
from .base import HEADERS, Item, StoreResult, parse_price

STORE = "noon"
STORE_NAME = "نون"


def search(query: str) -> StoreResult:
    t0 = time.time()
    try:
        r = httpx.get(
            "https://www.noon.com/egypt-ar/search/",
            params={"q": query},
            headers={**HEADERS, "Accept-Language": "ar-EG,ar;q=0.9"},
            timeout=8,
            follow_redirects=True,
        )
    except Exception as e:
        return StoreResult(STORE, STORE_NAME, "error", f"تعذر الاتصال: {e.__class__.__name__}",
                           elapsed_ms=_ms(t0))

    if r.status_code in (401, 403):
        return StoreResult(STORE, STORE_NAME, "blocked",
                           "الموقع حظر الطلب (Cloudflare) — يحتاج سيرفر داخل مصر أو بروكسي سكني",
                           elapsed_ms=_ms(t0))
    if r.status_code != 200:
        return StoreResult(STORE, STORE_NAME, "error", f"HTTP {r.status_code}", elapsed_ms=_ms(t0))

    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return StoreResult(STORE, STORE_NAME, "error",
                           "لم يتم العثور على بيانات الصفحة — ربما تغيّر هيكل الموقع",
                           elapsed_ms=_ms(t0))

    try:
        data = json.loads(script.string)
        hits = _find_hits(data)
    except Exception as e:
        return StoreResult(STORE, STORE_NAME, "error", f"فشل تحليل البيانات: {e}",
                           elapsed_ms=_ms(t0))

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
    return StoreResult(STORE, STORE_NAME, status,
                       "" if items else "لا توجد نتائج مطابقة",
                       items, elapsed_ms=_ms(t0))


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
