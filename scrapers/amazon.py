# -*- coding: utf-8 -*-
"""سكرابر أمازون مصر — يحلل بطاقات نتائج البحث
ملاحظة: أمازون أشرس موقع في الحماية، وغالبًا هيحتاج كوكيز/بروكسي سكني أو Playwright.
"""
import time
import httpx
from bs4 import BeautifulSoup
from .base import HEADERS, Item, StoreResult, parse_price

STORE = "amazon"
STORE_NAME = "أمازون"


def search(query: str) -> StoreResult:
    t0 = time.time()
    try:
        r = httpx.get(
            "https://www.amazon.eg/s",
            params={"k": query, "language": "ar_AE"},
            headers={**HEADERS, "Accept-Language": "ar-EG,ar;q=0.9"},
            timeout=8,
            follow_redirects=True,
        )
    except Exception as e:
        return StoreResult(STORE, STORE_NAME, "error", f"تعذر الاتصال: {e.__class__.__name__}",
                           elapsed_ms=_ms(t0))

    if r.status_code in (401, 403, 503):
        return StoreResult(STORE, STORE_NAME, "blocked",
                           "أمازون حظر الطلب (حماية ضد الروبوتات) — يحتاج بروكسي سكني أو Playwright",
                           elapsed_ms=_ms(t0))
    if r.status_code != 200:
        return StoreResult(STORE, STORE_NAME, "error", f"HTTP {r.status_code}", elapsed_ms=_ms(t0))

    soup = BeautifulSoup(r.text, "lxml")

    # صفحة التحقق (captcha)
    if soup.select_one("form#captcha") or "Enter the characters you see below" in r.text:
        return StoreResult(STORE, STORE_NAME, "blocked", "أمازون طلب تحقق (Captcha)", elapsed_ms=_ms(t0))

    items = []
    for card in soup.select('div[data-component-type="s-search-result"]'):
        try:
            title_el = card.select_one("h2 span") or card.select_one("h2")
            price_el = card.select_one(".a-price .a-offscreen")
            old_el = card.select_one(".a-price.a-text-price .a-offscreen")
            link_el = card.select_one("a.a-link-normal.s-no-outline") or card.select_one("h2 a") or card.select_one("a.a-link-normal")
            img_el = card.select_one("img.s-image")
            if not (title_el and price_el):
                continue
            href = link_el.get("href", "") if link_el else ""
            if href.startswith("/"):
                href = "https://www.amazon.eg" + href
            items.append(Item(
                store=STORE,
                title=title_el.get_text(strip=True),
                price=parse_price(price_el.get_text()),
                old_price=parse_price(old_el.get_text()) if old_el else None,
                url=href,
                image=img_el.get("src") if img_el else None,
            ))
        except Exception:
            continue

    status = "ok" if items else "empty"
    return StoreResult(STORE, STORE_NAME, status,
                       "" if items else "لا توجد نتائج مطابقة",
                       items, elapsed_ms=_ms(t0))


def _ms(t0):
    return int((time.time() - t0) * 1000)
