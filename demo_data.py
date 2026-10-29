# -*- coding: utf-8 -*-
"""بيانات تجريبية واقعية (من رصد أسعار السوق المصري — أكتوبر 2026).

بتُستخدم فقط لما المتاجر ترفض الاتصال (وضع العرض التجريبي).
كل منتج له صورة صغيرة محلية في static/img/products (بمقاس صغير ~160px)
عشان الصفحة تفضل سريعة وتشتغل حتى بدون إنترنت في المعاينة.
"""
from __future__ import annotations

import hashlib

from scrapers.base import Item
from scrapers.stores import BY_KEY, EXTRA_STORES

IMG = "/static/img/products/{}.jpg"

# ---------------------------------------------------------------------------
#  المنتجات: عروض مرصودة فعليًا من جوميا/نون/أمازون + توليد ثابت لباقي المتاجر
# ---------------------------------------------------------------------------
DEMO_PRODUCTS = [
    {
        "keywords": ["هواوي", "huawei", "freebuds", "فري", "بودز", "se 2", "se2", "سماعة", "سماعات", "earbuds"],
        "name": "Huawei FreeBuds SE 2",
        "image": IMG.format("freebuds-se-2"),
        "base": 1090,
        "offers": [
            ("jumia", "Huawei Freebuds SE 2 Earbuds - Noise Canceling with 40 Hour Battery Life - White", 1222, 1592),
            ("noon", "هواوي سماعات FreeBuds SE 2 لاسلكية - بطارية 40 ساعة - أسود", 1299, None),
            ("amazon", "HUAWEI FreeBuds SE 2, 40-Hour Battery Life, IP54 - Ceramic White", 1090, None),
        ],
    },
    {
        "keywords": ["هواوي", "huawei", "freebuds", "فري", "6i", "سماعة", "سماعات", "earbuds"],
        "name": "Huawei FreeBuds 6i",
        "image": IMG.format("freebuds-6i"),
        "base": 2888,
        "offers": [
            ("jumia", "Huawei FreeBuds 6i - Black", 2888, 3355),
            ("noon", "هواوي FreeBuds 6i - عزل ضوضاء ANC 3.0 - أسود", 4099, 4999),
            ("amazon", "HUAWEI FreeBuds 6i, Dynamic ANC 3.0, 35H Battery - Black", 2950, 3499),
        ],
    },
    {
        "keywords": ["هواوي", "huawei", "freebuds", "فري", "7i", "سماعة", "سماعات", "earbuds"],
        "name": "Huawei FreeBuds 7i",
        "image": IMG.format("freebuds-7i"),
        "base": 3699,
        "offers": [
            ("vontx", "Huawei FreeBuds 7i Intelligent Dynamic ANC 4.0 - أسود", 3699, None),
            ("dream2000", "هواوي فري بادز 7i سماعات لاسلكية", 5160, 5800),
            ("jumia", "Huawei فري بودز 7i - أبيض", 4370, 5244),
            ("noon", "هواوي FreeBuds 7i - 6 ميكروفونات - بطارية 35 ساعة", 4700, 5000),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "r50i", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore R50i",
        "image": IMG.format("r50i"),
        "base": 699,
        "offers": [
            ("jumia", "Soundcore سماعة لاسلكية R50i - بلوتوث 5.3 - 30 ساعة - أسود", 855, 1245),
            ("noon", "أنكر ساوند كور R50i - أسود", 699, 999),
            ("amazon", "Soundcore by Anker R50i True Wireless Earbuds - Black", 731, 889),
            ("dream2000", "أنكر ساوندكور R50i VI سماعات - A3969D11", 1120, None),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "r50i", "nc", "عزل", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore R50i NC",
        "image": IMG.format("r50i-nc"),
        "base": 1025,
        "offers": [
            ("jumia", "Soundcore R50i NC باللون الأسود - A3959H11 - عزل ضوضاء", 1431, 2200),
            ("noon", "أنكر ساوند كور R50i NC - عزل ضوضاء - بطارية 45 ساعة", 1025, None),
            ("amazon", "Soundcore R50I NC - Noise Cancelling - 45H - 18 Months Warranty", 1599, None),
            ("dream2000", "ساوند كور انكر R50I NC موديل A3959H11", 1850, None),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "p40i", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore P40i",
        "image": IMG.format("p40i"),
        "base": 1990,
        "offers": [
            ("noon", "Soundcore P40i - عزل ضوضاء تكيفي - بطارية 60 ساعة - أبيض", 1990, None),
            ("amazon", "Soundcore P40i by Anker, Adaptive ANC, 60H Playtime - White", 2999, None),
            ("dream2000", "ساوندكور من أنكر P41i سماعات أذن لاسلكية مع شاحن - A3937H11", 2599, 2999),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "liberty", "ليبرتي", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore Liberty 4 NC",
        "image": IMG.format("liberty-4-nc"),
        "base": 2570,
        "offers": [
            ("jumia", "Soundcore Liberty 4 NC - عزل تكيفي - LDAC", 2570, None),
            ("amazon", "Soundcore by Anker Liberty 4 NC Wireless Noise Cancelling Earbuds", 2688, 3500),
            ("miami", "ANKER SOUNDCORE LIBERTY 4 NC WHITE", 3350, None),
        ],
    },
    {
        "keywords": ["ايربودز", "ايربود", "airpods", "ابل", "آبل", "apple", "سماعة", "سماعات", "earbuds"],
        "name": "Apple AirPods 4",
        "image": IMG.format("airpods-4"),
        "base": 6744,
        "offers": [
            ("jumia", "Apple سماعات ايربودز 4 - بلوتوث - أبيض", 7799, 9000),
            ("noon", "ابل سماعات أذن لاسلكية AirPods 4 - أبيض", 6744, 7999),
            ("dream2000", "آبل AirPods 4 ANC سماعات أذن لاسلكية", 13499, None),
        ],
    },
    {
        "keywords": ["ايربودز", "ايربود", "airpods", "ابل", "آبل", "apple", "برو", "pro", "سماعة", "سماعات", "earbuds"],
        "name": "Apple AirPods Pro 3",
        "image": IMG.format("airpods-pro-3"),
        "base": 12555,
        "offers": [
            ("jumia", "Apple سماعات AirPods Pro 3 اللاسلكية - إلغاء ضوضاء - أبيض", 12555, 18744),
            ("noon", "ابل AirPods Pro 3 - أبيض", 13799, 14489),
            ("dream2000", "أبل إيربودز برو 3", 16800, None),
        ],
    },
    {
        "keywords": ["شاومي", "xiaomi", "redmi", "ريدمي", "buds", "سماعة", "سماعات", "earbuds"],
        "name": "Xiaomi Redmi Buds 6 Active",
        "image": IMG.format("redmi-buds-6"),
        "base": 745,
        "offers": [
            ("jumia", "Xiaomi Redmi Buds 6 Active - أزرق", 745, 999),
            ("noon", "شاومي ريدمي بادز 6 أكتيف - أسود", 799, 1100),
            ("dream2000", "شاومي ريدمي 6 أكتيف ايربودز", 1350, None),
        ],
    },
    {
        "keywords": ["سامسونج", "samsung", "galaxy", "buds", "جالاكسي", "سماعة", "سماعات", "earbuds"],
        "name": "Samsung Galaxy Buds 3 Pro",
        "image": IMG.format("galaxy-buds-3-pro"),
        "base": 6300,
        "offers": [
            ("jumia", "Samsung Galaxy Buds 3 Pro - فضي", 6300, 7499),
            ("noon", "سامسونج جالاكسي بادز 3 برو", 6899, 7999),
            ("dream2000", "سامسونج جلاكسي بدز 3 برو", 14230, None),
        ],
    },
]

GENERIC_WORDS = {"سماعة", "سماعات", "earbuds", "headphones", "هيدفون", "بلوتوث", "لاسلكية", "وايرلس"}

# معامل السعر النسبي لكل متجر (بيستخدم لتوليد عروض المتاجر اللي مش مرصودة)
STORE_FACTOR = {
    "jumia": 1.00, "noon": 1.03, "amazon": 0.97,
    "vontx": 1.05, "dream2000": 0.99, "2b": 1.02, "etisal": 1.08,
    "dubaiphone": 1.01, "btech": 1.06, "miami": 1.04, "raneen": 1.07,
}


def _seeded(name: str, store: str) -> int:
    return int(hashlib.md5(f"{name}|{store}".encode()).hexdigest()[:8], 16)


def _generated_offer(prod: dict, store: str) -> Item:
    """عرض مولَّد بشكل ثابت (نفس الرقم كل مرة) لتغطية المتاجر غير المرصودة."""
    h = _seeded(prod["name"], store)
    jitter = 1 + ((h % 15) - 7) / 100.0          # ±7%
    raw = prod["base"] * STORE_FACTOR.get(store, 1.03) * jitter
    price = max(49, int(round(raw / 10.0)) * 10 - 1)   # الأسعار بتنتهي بـ 9
    old = None
    if h % 3 == 0:
        old = int(round(price * (1.15 + (h % 9) / 100.0) / 10.0)) * 10
    url = BY_KEY[store].url_for(prod["name"]) if store in BY_KEY else ""
    return Item(store, prod["name"], price, old, url=url, image=prod["image"])


def _offers_for(prod: dict) -> list[Item]:
    items: list[Item] = []
    seen_stores = set()
    for store, title, price, old in prod["offers"]:
        url = BY_KEY[store].url_for(prod["name"]) if store in BY_KEY else ""
        items.append(Item(store, title, price, old, url=url, image=prod["image"]))
        seen_stores.add(store)
    # نكمّل باقي المتاجر بعروض مولّدة (عشان كل المتاجر تظهر في وضع العرض)
    for profile in EXTRA_STORES:
        if profile.key in seen_stores:
            continue
        if len(seen_stores) >= 7:      # مش لازم كل الـ 11 في نفس المنتج
            break
        items.append(_generated_offer(prod, profile.key))
        seen_stores.add(profile.key)
    return items


def search_demo(query: str):
    """يبحث في البيانات التجريبية ويرجع (items, matched_names).

    الكلمات العامة (سماعات...) بتطابق كل حاجة، والكلمات المحددة (ماركة/موديل)
    لازم تتطابق — والترتيب حسب قوة التطابق.
    """
    q = (query or "").lower().strip()
    q_tokens = [t for t in q.split() if t]
    specific_q = [t for t in q_tokens if t not in GENERIC_WORDS]

    scored = []
    for prod in DEMO_PRODUCTS:
        specific_kws = {k.lower() for k in prod["keywords"] if k not in GENERIC_WORDS}
        if not specific_q:
            score = 1
        else:
            score = 0
            for k in specific_kws:
                if k in q or any(k in t or t in k for t in specific_q):
                    score += 1
        if score > 0:
            scored.append((score, prod))

    if not scored:
        return [], []

    max_score = max(s for s, _ in scored)
    threshold = max_score if max_score >= 2 else 1

    items, matched = [], []
    for score, prod in scored:
        if score >= threshold or (score >= 2 and score >= max_score - 1):
            items.extend(_offers_for(prod))
            matched.append(prod["name"])

    seen, unique = set(), []
    for it in items:
        key = (it.store, it.title)
        if key not in seen:
            seen.add(key)
            unique.append(it)
    return unique, matched


SUGGESTIONS = ["Huawei FreeBuds SE 2", "Huawei FreeBuds 6i", "Huawei FreeBuds 7i",
               "Soundcore R50i", "Soundcore R50i NC", "Soundcore P40i", "Liberty 4 NC",
               "AirPods 4", "AirPods Pro 3", "Redmi Buds 6", "Galaxy Buds 3 Pro"]
