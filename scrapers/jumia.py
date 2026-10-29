# -*- coding: utf-8 -*-
"""سكرابر جوميا مصر — يعمل بصفحات البحث HTML العادية"""
import time
import httpx
from bs4 import BeautifulSoup
from .base import HEADERS, Item, StoreResult, parse_price

STORE = "jumia"
STORE_NAME = "جوميا"


def search(query: str) -> StoreResult:
    t0 = time.time()
    try:
        r = httpx.get(
            "https://www.jumia.com.eg/catalog/",
            params={"q": query},
            headers=HEADERS,
            timeout=8,
            follow_redirects=True,
        )
    except Exception as e:
        return StoreResult(STORE, STORE_NAME, "error", f"تعذر الاتصال: {e.__class__.__name__}",
                           elapsed_ms=_ms(t0))

    if r.status_code == 403:
        return StoreResult(STORE, STORE_NAME, "blocked",
                           "الموقع حظر الطلب (حماية ضد الروبوتات) — جرّب من سيرفر داخل مصر أو استخدم بروكسي",
                           elapsed_ms=_ms(t0))
    if r.status_code != 200:
        return StoreResult(STORE, STORE_NAME, "error", f"HTTP {r.status_code}", elapsed_ms=_ms(t0))

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
    return StoreResult(STORE, STORE_NAME, status,
                       "" if items else "لا توجد نتائج مطابقة",
                       items, elapsed_ms=_ms(t0))


def _ms(t0):
    return int((time.time() - t0) * 1000)
