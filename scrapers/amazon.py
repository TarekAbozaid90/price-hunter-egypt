# -*- coding: utf-8 -*-
"""سكرابر أمازون مصر — يحلل بطاقات نتائج البحث
ملاحظة: أمازون أشرس موقع في الحماية، وغالبًا هيحتاج كوكيز/بروكسي سكني أو Playwright.
"""
import time

from bs4 import BeautifulSoup

from .base import HEADERS, Item, StoreResult, parse_price
from .net import describe_error, http_get

STORE = "amazon"
STORE_NAME = "أمازون"


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
            "https://www.amazon.eg/s",
            params={"k": query, "language": "ar_AE"},
            headers={**HEADERS, "Accept-Language": "ar-EG,ar;q=0.9"},
            store=STORE,
        )
    except Exception as e:  # noqa: BLE001
        return _res("error", f"تعذر الاتصال: {describe_error(e)}", t0=t0, net=e)

    if r.status_code in (401, 403, 429, 503):
        return _res(
            "blocked",
            "أمازون حظر الطلب (حماية ضد الروبوتات) — محتاج بروكسي سكني من إعدادات Render "
            "(PROXY_URL) أو Playwright بمتصفح حقيقي",
            t0=t0, net=r,
        )
    if r.status_code != 200:
        return _res("error", f"HTTP {r.status_code}", t0=t0, net=r)

    soup = BeautifulSoup(r.text, "lxml")

    # صفحة التحقق (captcha)
    if soup.select_one("form#captcha") or "Enter the characters you see below" in r.text:
        return _res("blocked", "أمازون طلب تحقق (Captcha) — جرّب بروكسي تاني", t0=t0, net=r)

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
    return _res(status, "" if items else "لا توجد نتائج مطابقة", items, t0, r)


def _ms(t0):
    return int((time.time() - t0) * 1000)
