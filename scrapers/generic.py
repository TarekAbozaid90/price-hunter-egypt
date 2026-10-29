# -*- coding: utf-8 -*-
"""محرّك سكرابينج عام — بيغطي أغلب منصّات المتاجر المصرية بأربع استراتيجيات:

    shopify     : صفحات /search + بيانات JSON مضمّنة في الكارت (أدق حاجة)
    woocommerce : ووردبريس/وودمارت (.product-grid-item / li.product)
    magento     : ماجنتو 2 (li.product-item + data-price-amount)
    generic     : JSON-LD + __NEXT_DATA__ + كشف تلقائي للكروت (لأي منصة تانية)

كل استراتيجية بترجع قائمة Item، ولو فشلت بيرجع سبب واضح بالعربي.
"""
from __future__ import annotations

import json
import re
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .base import HEADERS, Item, StoreResult, parse_price
from .net import describe_error, http_get
from .stores import StoreProfile

BLOCK_MARKERS = (
    "just a moment", "attention required", "cf-error", "cloudflare",
    "access denied", "captcha", "are you a human", "request blocked",
    "غير مصرح", "تم حظر",
)

PRICE_RE = re.compile(
    r"(?:LE|EGP|E£|ج\.م|جنيه|ج)\s*([0-9][0-9,\.]*)", re.IGNORECASE
)


# ------------------------------------------------------------------ أدوات عامة
def _ms(t0: float) -> int:
    return int((time.time() - t0) * 1000)


def _abs(url: str, base: str) -> str:
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http"):
        return url
    return urljoin(base, url)


def _thumb(url: str | None) -> str | None:
    """يطلب نسخة صغيرة من الصورة (Shopify بيدعم width=) لتسريع التحميل.

    مهم: بعض الثيمات بتحط width=1 (صورة 1 بكسل للـ lazy load) — بنستبدلها بـ 160.
    """
    if not url:
        return None
    if "cdn.shopify.com" in url or "/cdn/shop/" in url:
        if re.search(r"[?&]width=\d+", url):
            url = re.sub(r"([?&])width=\d+", r"\1width=160", url)
        else:
            url += ("&" if "?" in url else "?") + "width=160"
    return url


def _money(text: str | None) -> float | None:
    if not text:
        return None
    m = PRICE_RE.search(text.replace("\u200f", "").replace("\xa0", " "))
    if m:
        return parse_price(m.group(1))
    return parse_price(text)


def _num(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cents(value) -> float | None:
    """Shopify بيحط الأسعار بالقروش (23999.00 → 2399900)."""
    n = _num(value)
    if n is None or n <= 0:
        return None
    return round(n / 100, 2) if n >= 1000 else n


def _first_img(card, attrs=("data-src", "data-lazy-src", "data-original", "src")) -> str | None:
    for img in card.select("img"):
        for a in attrs:
            v = img.get(a)
            if v and not v.startswith("data:"):
                return v
        srcset = img.get("srcset") or img.get("data-srcset")
        if srcset:
            first = srcset.split(",")[0].strip().split(" ")[0]
            if first and not first.startswith("data:"):
                return first
    return None


def _text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def _clean_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()[:220]


def _push(items: list, seen: set, item: Item):
    if not item.title or not item.price:
        return
    key = (item.store, item.title.lower()[:70], round(item.price))
    if key in seen:
        return
    seen.add(key)
    items.append(item)


def _is_blocked(status: int, html: str) -> bool:
    if status in (401, 403, 407, 429, 503):
        return True
    low = (html or "")[:6000].lower()
    return any(m in low for m in BLOCK_MARKERS)


# --------------------------------------------------------------- Shopify
def _shopify(soup: BeautifulSoup, profile: StoreProfile, query: str) -> list[Item]:
    items: list[Item] = []
    seen: set = set()

    # 1) ثيمات T4S / Haravan
    for el in soup.select("[data-product-options]"):
        try:
            data = json.loads(el.get("data-product-options") or "{}")
        except json.JSONDecodeError:
            continue
        title = _clean_title(data.get("alt") or _text(el.select_one("h3, h2, .t4s-product-title")))
        price = _cents(data.get("price"))
        old = _cents(data.get("compare_at_price"))
        href = ""
        link = el.select_one('a[href*="/products/"]')
        if link:
            href = _abs(link.get("href", ""), profile.base)
        image = data.get("image2") or _first_img(el)
        _push(items, seen, Item(profile.key, title, price,
                                old if old and price and old > price else None,
                                url=href, image=_thumb(_abs(image, profile.base)) if image else None))

    # 2) ثيمات حديثة بتحط JSON في x-labels-data
    for el in soup.select("[x-labels-data]"):
        try:
            data = json.loads(el.get("x-labels-data") or "{}")
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        title = _clean_title(data.get("title") or "")
        price = _cents(data.get("price"))
        old = _cents(data.get("compare_at_price"))
        card = el
        for _ in range(6):
            if card is None:
                break
            if card.select_one('a[href*="/products/"]'):
                break
            card = card.parent
        href, image = "", None
        if card is not None:
            link = card.select_one('a[href*="/products/"]')
            href = _abs(link.get("href", ""), profile.base) if link else ""
            image = _first_img(card)
        _push(items, seen, Item(profile.key, title, price,
                                old if old and price and old > price else None,
                                url=href, image=_thumb(_abs(image, profile.base)) if image else None))

    # 3) أي كارت منتج عادي
    if not items:
        for link in soup.select('a[href*="/products/"]'):
            card = link
            for _ in range(4):
                if card.parent is None:
                    break
                card = card.parent
                if card.select_one("img") and (card.select_one(".price, [class*=price]") or PRICE_RE.search(_text(card))):
                    break
            title = _clean_title(_text(link) or (link.get("aria-label") or "") or
                                 _text(card.select_one("h2, h3, [class*=title]")))
            price_el = card.select_one(".price, [class*=price]")
            price = _money(_text(price_el)) or _money(_text(card))
            old_el = card.select_one("del, s, .old-price, [class*=compare]")
            old = _money(_text(old_el)) if old_el else None
            image = _first_img(card)
            _push(items, seen, Item(profile.key, title, price,
                                    old if old and price and old > price else None,
                                    url=_abs(link.get("href", ""), profile.base),
                                    image=_thumb(_abs(image, profile.base)) if image else None))
    return items


# ------------------------------------------------------------ WooCommerce
WOO_CARDS = ("div.product-grid-item", "li.product", ".wd-product", ".product-small",
             ".product-wrapper", ".type-product")


def _woocommerce(soup: BeautifulSoup, profile: StoreProfile, query: str) -> list[Item]:
    items: list[Item] = []
    seen: set = set()
    cards = []
    for sel in WOO_CARDS:
        cards = soup.select(sel)
        if len(cards) >= 1:
            break
    for card in cards:
        title_el = (card.select_one(".wd-entities-title a") or card.select_one("h3 a")
                    or card.select_one("h2") or card.select_one(".woocommerce-loop-product__title"))
        title = _clean_title(_text(title_el))
        price_box = card.select_one(".price")
        price = None
        old = None
        if price_box is not None:
            ins = price_box.select_one("ins .amount") or price_box.select_one("ins")
            del_el = price_box.select_one("del .amount") or price_box.select_one("del")
            price = _money(_text(ins)) if ins is not None else _money(_text(price_box))
            old = _money(_text(del_el)) if del_el is not None else None
        link = card.select_one('a[href*="/product"]') or card.select_one("a[href]")
        image = _first_img(card)
        _push(items, seen, Item(profile.key, title, price,
                                old if old and price and old > price else None,
                                url=_abs(link.get("href", ""), profile.base) if link else "",
                                image=_thumb(_abs(image, profile.base)) if image else None))
    return items


# --------------------------------------------------------------- Magento
MAGENTO_CARDS = ("li.product-item", ".product-item-info", "li.item.product",
                 ".product-item", ".item.product.product-item")


def _magento(soup: BeautifulSoup, profile: StoreProfile, query: str) -> list[Item]:
    items: list[Item] = []
    seen: set = set()
    cards = []
    for sel in MAGENTO_CARDS:
        cards = soup.select(sel)
        if cards:
            break
    for card in cards:
        title_el = (card.select_one(".product-item-link") or card.select_one("a.product-item-link")
                    or card.select_one("h3 a") or card.select_one("h2 a"))
        title = _clean_title(_text(title_el))
        # ماجنتو 2 بيحط السعر النهائي في data-price-amount
        price = None
        old = None
        final = card.select_one(".price-box .special-price [data-price-amount], "
                                ".price-box .price-wrapper[data-price-amount], [data-price-amount]")
        if final is not None:
            price = _num(final.get("data-price-amount"))
        if price is None:
            price = _money(_text(card.select_one(".price-box .price, .price")))
        old_el = card.select_one(".old-price [data-price-amount]")
        if old_el is not None:
            old = _num(old_el.get("data-price-amount"))
        if old is None:
            old = _money(_text(card.select_one(".old-price .price")))
        link = card.select_one("a.product-item-link") or card.select_one("a[href]")
        img = card.select_one("img.product-image-photo") or card.select_one("img")
        image = None
        if img is not None:
            for a in ("data-src", "data-original", "src"):
                v = img.get(a)
                if v and not v.startswith("data:"):
                    image = v
                    break
        _push(items, seen, Item(profile.key, title, price,
                                old if old and price and old > price else None,
                                url=_abs(link.get("href", ""), profile.base) if link else "",
                                image=_thumb(_abs(image, profile.base)) if image else None))
    return items


# --------------------------------------------------------------- Generic
def _jsonld(soup: BeautifulSoup, profile: StoreProfile) -> list[Item]:
    items: list[Item] = []
    seen: set = set()

    def walk(node):
        if isinstance(node, dict):
            kind = str(node.get("@type", "")).lower()
            if "product" in kind and node.get("name"):
                offers = node.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price = _num(offers.get("price") or offers.get("lowPrice") or node.get("price"))
                image = node.get("image")
                if isinstance(image, list):
                    image = image[0] if image else None
                url = node.get("url") or (offers.get("url") if isinstance(offers, dict) else "")
                _push(items, seen, Item(profile.key, _clean_title(str(node.get("name"))), price,
                                        url=_abs(str(url or ""), profile.base),
                                        image=_abs(str(image), profile.base) if image else None))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            walk(json.loads(script.string or "{}"))
        except Exception:  # noqa: BLE001
            continue
    return items


def _next_data(soup: BeautifulSoup, profile: StoreProfile) -> list[Item]:
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return []
    try:
        data = json.loads(script.string)
    except json.JSONDecodeError:
        return []

    buckets: list[list] = []

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    keys = set(v[0].keys())
                    if (keys & {"price", "sale_price", "priceValue", "final_price"}) and \
                       (keys & {"name", "title", "productName"}):
                        buckets.append(v)
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    if not buckets:
        return []
    best = max(buckets, key=len)
    items: list[Item] = []
    seen: set = set()
    for h in best[:40]:
        title = h.get("name") or h.get("title") or h.get("productName") or ""
        price = _num(h.get("sale_price") or h.get("price") or h.get("final_price") or h.get("priceValue"))
        old = _num(h.get("mrp") or h.get("regular_price") or h.get("compare_at_price"))
        image = h.get("image") or h.get("thumbnail") or h.get("imageUrl")
        if isinstance(image, dict):
            image = image.get("url")
        url = h.get("url") or h.get("link") or h.get("slug") or ""
        _push(items, seen, Item(profile.key, _clean_title(str(title)), price,
                                old if old and price and old > price else None,
                                url=_abs(str(url), profile.base) if url else "",
                                image=_abs(str(image), profile.base) if image else None))
    return items


def _heuristic(soup: BeautifulSoup, profile: StoreProfile) -> list[Item]:
    """آخر حل: يدور على أي عنصر متكرر فيه لينك منتج + سعر."""
    items: list[Item] = []
    seen: set = set()
    candidates = soup.select('[class*="product"], [class*="Product"], article, li')
    for card in candidates:
        if len(card.select("a[href]")) == 0 or card.select_one("img") is None:
            continue
        txt = _text(card)
        if len(txt) > 700 or len(txt) < 8:
            continue
        price = _money(txt)
        if not price or price < 5:
            continue
        link = card.select_one("a[href]")
        href = _abs(link.get("href", ""), profile.base)
        if not href or urlparse(href).netloc.endswith(("javascript", "")):
            continue
        title = _clean_title(_text(card.select_one("h2, h3, h4, [class*=title], [class*=name]")) or _text(link))
        image = _first_img(card)
        _push(items, seen, Item(profile.key, title, price, url=href,
                                image=_abs(image, profile.base) if image else None))
        if len(items) >= 24:
            break
    return items


ENGINES = {
    "shopify": _shopify,
    "woocommerce": _woocommerce,
    "magento": _magento,
}


# ------------------------------------------------------------------ الواجهة
def search(profile: StoreProfile, query: str, limit: int = 20) -> StoreResult:
    t0 = time.time()
    url = profile.url_for(query)
    headers = dict(HEADERS)
    headers["Referer"] = profile.base + "/"

    try:
        resp = http_get(url, headers=headers, store=profile.key)
    except Exception as exc:  # noqa: BLE001
        return StoreResult(profile.key, profile.ar, "error",
                           f"تعذر الاتصال: {describe_error(exc)}",
                           elapsed_ms=_ms(t0), via=getattr(exc, "via", "direct"),
                           proxy=getattr(exc, "proxy", ""))

    via = resp.via
    proxy = resp.proxy
    html = resp.text or ""

    if _is_blocked(resp.status_code, html):
        return StoreResult(
            profile.key, profile.ar, "blocked",
            "الموقع رفض الطلب (حماية ضد الروبوتات) — محتاج بروكسي سكني/مصري "
            f"(PROXY_URL أو {profile.key.upper()}_PROXY)",
            elapsed_ms=_ms(t0), via=via, proxy=proxy,
        )
    if resp.status_code != 200:
        return StoreResult(profile.key, profile.ar, "error", f"HTTP {resp.status_code}",
                           elapsed_ms=_ms(t0), via=via, proxy=proxy)

    soup = BeautifulSoup(html, "lxml")
    items: list[Item] = []
    try:
        engine = ENGINES.get(profile.engine)
        if engine:
            items = engine(soup, profile, query)
        if len(items) < 2:
            merged = items[:]
            keys = {(i.title.lower()[:60], round(i.price or 0)) for i in merged}
            for extra in (_jsonld(soup, profile), _next_data(soup, profile), _heuristic(soup, profile)):
                for it in extra:
                    k = (it.title.lower()[:60], round(it.price or 0))
                    if k not in keys:
                        keys.add(k)
                        merged.append(it)
            items = merged
    except Exception as exc:  # noqa: BLE001
        return StoreResult(profile.key, profile.ar, "error", f"فشل تحليل الصفحة: {exc}",
                           elapsed_ms=_ms(t0), via=via, proxy=proxy)

    items = [i for i in items if i.price][:limit]
    for it in items:
        it.store = profile.key
    status = "ok" if items else "empty"
    msg = "" if items else "لا توجد نتائج مطابقة (أو الصفحة بتتحمّل بجافاسكريبت)"
    return StoreResult(profile.key, profile.ar, status, msg, items,
                       elapsed_ms=_ms(t0), via=via, proxy=proxy)
