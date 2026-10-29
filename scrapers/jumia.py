# -*- coding: utf-8 -*-
"""سكرابر جوميا مصر — يعمل بصفحات البحث HTML العادية"""
import time

from bs4 import BeautifulSoup

import config
from .base import HEADERS, Item, StoreResult, parse_price
from .net import describe_error, http_get

STORE = "jumia"
STORE_NAME = "جوميا"


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
            "https://www.jumia.com.eg/catalog/",
            params={"q": query},
            headers=HEADERS,
            store=STORE,
        )
    except Exception as e:  # noqa: BLE001
        return _res("error", f"تعذر الاتصال: {describe_error(e)}", t0=t0, net=e)

    if r.status_code in (403, 429):
        return _res(
            "blocked",
            "الموقع حظر الطلب (حماية ضد الروبوتات) — ضيف بروكسي من إعدادات Render "
            "عبر المتغير PROXY_URL أو من سيرفر داخل مصر",
            t0=t0, net=r,
        )
    if r.status_code != 200:
        return _res("error", f"HTTP {r.status_code}", t0=t0, net=r)

    soup = BeautifulSoup(r.text, "lxml")
    items = []
    for card in soup.select("article.prd"):
        try:
            name_el = card.select_one("h3.name") or card.select_one(".name")
            price_el = card.select_one("div.prc")
            old_el = card.select_one("div.s-prc-was") or card.select_one(".prc-was")
            link_el = card.select_one("a.core") or card.select_one("a[href]")
            img_el = card.select_one("img.img") or card.select_one("img")
            if not (name_el and price_el):
                continue
            href = link_el.get("href", "") if link_el else ""
            if href.startswith("/"):
                href = "https://www.jumia.com.eg" + href
            items.append(Item(
                store=STORE,
                title=name_el.get_text(strip=True),
                price=parse_price(price_el.get_text()),
                old_price=parse_price(old_el.get_text()) if old_el else None,
                url=href,
                image=(img_el.get("data-src") or img_el.get("src")) if img_el else None,
            ))
        except Exception:
            continue

    status = "ok" if items else "empty"
    return _res(status, "" if items else "لا توجد نتائج مطابقة", items, t0, r)


def _ms(t0):
    return int((time.time() - t0) * 1000)
