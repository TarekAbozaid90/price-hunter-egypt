# -*- coding: utf-8 -*-
"""بيانات تجريبية واقعية (من رصد أسعار السوق المصري - أكتوبر 2026)
تُستخدم فقط عندما يتعذر الوصول المباشر للمتاجر (وضع العرض التجريبي)
"""
from scrapers.base import Item

# كل منتج: (كلمات مفتاحية للمطابقة, قائمة العروض من المتاجر)
DEMO_PRODUCTS = [
    {
        "keywords": ["هواوي", "huawei", "freebuds", "فري", "بودز", "se 2", "se2", "سماعة", "سماعات", "earbuds"],
        "name": "Huawei FreeBuds SE 2",
        "offers": [
            Item("jumia", "Huawei Freebuds SE 2 Earbuds - Noise Canceling with 40 Hour Battery Life - White", 1222, 1592,
                 url="https://www.jumia.com.eg/catalog/?q=huawei+freebuds+se+2"),
            Item("noon", "هواوي سماعات FreeBuds SE 2 لاسلكية - بطارية 40 ساعة - أسود", 1299, None,
                 url="https://www.noon.com/egypt-ar/search/?q=huawei+freebuds+se+2"),
            Item("amazon", "HUAWEI FreeBuds SE 2, 40-Hour Battery Life, IP54 - Ceramic White", 1090, None,
                 url="https://www.amazon.eg/s?k=huawei+freebuds+se+2"),
        ],
    },
    {
        "keywords": ["هواوي", "huawei", "freebuds", "فري", "6i", "سماعة", "سماعات", "earbuds"],
        "name": "Huawei FreeBuds 6i",
        "offers": [
            Item("jumia", "Huawei FreeBuds 6i - Black", 2888, 3355,
                 url="https://www.jumia.com.eg/catalog/?q=huawei+freebuds+6i"),
            Item("noon", "هواوي FreeBuds 6i - عزل ضوضاء ANC 3.0 - أسود", 4099, 4999,
                 url="https://www.noon.com/egypt-ar/search/?q=huawei+freebuds+6i"),
            Item("amazon", "HUAWEI FreeBuds 6i, Dynamic ANC 3.0, 35H Battery - Black", 2950, 3499,
                 url="https://www.amazon.eg/s?k=huawei+freebuds+6i"),
        ],
    },
    {
        "keywords": ["هواوي", "huawei", "freebuds", "فري", "7i", "سماعة", "سماعات", "earbuds"],
        "name": "Huawei FreeBuds 7i",
        "offers": [
            Item("jumia", "Huawei فري بودز 7i - أبيض", 4370, 5244,
                 url="https://www.jumia.com.eg/catalog/?q=huawei+freebuds+7i"),
            Item("noon", "هواوي FreeBuds 7i - 6 ميكروفونات - بطارية 35 ساعة", 4700, 5000,
                 url="https://www.noon.com/egypt-ar/search/?q=huawei+freebuds+7i"),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "r50i", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore R50i",
        "offers": [
            Item("jumia", "Soundcore سماعة لاسلكية R50i - بلوتوث 5.3 - 30 ساعة - أسود", 855, 1245,
                 url="https://www.jumia.com.eg/catalog/?q=soundcore+r50i"),
            Item("noon", "أنكر ساوند كور R50i - أسود", 699, 999,
                 url="https://www.noon.com/egypt-ar/search/?q=soundcore+r50i"),
            Item("amazon", "Soundcore by Anker R50i True Wireless Earbuds - Black", 731, 889,
                 url="https://www.amazon.eg/s?k=soundcore+r50i"),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "r50i", "nc", "عزل", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore R50i NC",
        "offers": [
            Item("jumia", "Soundcore R50i NC باللون الأسود - A3959H11 - عزل ضوضاء", 1431, 2200,
                 url="https://www.jumia.com.eg/catalog/?q=soundcore+r50i+nc"),
            Item("noon", "أنكر ساوند كور R50i NC - عزل ضوضاء - بطارية 45 ساعة", 1025, None,
                 url="https://www.noon.com/egypt-ar/search/?q=soundcore+r50i+nc"),
            Item("amazon", "Soundcore R50I NC - Noise Cancelling - 45H - 18 Months Warranty", 1599, None,
                 url="https://www.amazon.eg/s?k=soundcore+r50i+nc"),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "p40i", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore P40i",
        "offers": [
            Item("noon", "Soundcore P40i - عزل ضوضاء تكيفي - بطارية 60 ساعة - أبيض", 1990, None,
                 url="https://www.noon.com/egypt-ar/search/?q=soundcore+p40i"),
            Item("amazon", "Soundcore P40i by Anker, Adaptive ANC, 60H Playtime - White", 2999, None,
                 url="https://www.amazon.eg/s?k=soundcore+p40i"),
        ],
    },
    {
        "keywords": ["انكر", "أنكر", "anker", "soundcore", "ساوند", "liberty", "ليبرتي", "سماعة", "سماعات", "earbuds"],
        "name": "Anker Soundcore Liberty 4 NC",
        "offers": [
            Item("jumia", "Soundcore Liberty 4 NC - عزل تكيفي - LDAC", 2570, None,
                 url="https://www.jumia.com.eg/catalog/?q=soundcore+liberty+4+nc"),
            Item("amazon", "Soundcore by Anker Liberty 4 NC Wireless Noise Cancelling Earbuds", 2688, 3500,
                 url="https://www.amazon.eg/s?k=soundcore+liberty+4+nc"),
        ],
    },
    {
        "keywords": ["ايربودز", "ايربود", "airpods", "ابل", "آبل", "apple", "سماعة", "سماعات", "earbuds"],
        "name": "Apple AirPods 4",
        "offers": [
            Item("jumia", "Apple سماعات ايربودز 4 - بلوتوث - أبيض", 7799, 9000,
                 url="https://www.jumia.com.eg/catalog/?q=airpods+4"),
            Item("noon", "ابل سماعات أذن لاسلكية AirPods 4 - أبيض", 6744, 7999,
                 url="https://www.noon.com/egypt-ar/search/?q=airpods+4"),
        ],
    },
    {
        "keywords": ["ايربودز", "ايربود", "airpods", "ابل", "آبل", "apple", "برو", "pro", "سماعة", "سماعات", "earbuds"],
        "name": "Apple AirPods Pro 3",
        "offers": [
            Item("jumia", "Apple سماعات AirPods Pro 3 اللاسلكية - إلغاء ضوضاء - أبيض", 12555, 18744,
                 url="https://www.jumia.com.eg/catalog/?q=airpods+pro+3"),
            Item("noon", "ابل AirPods Pro 3 - أبيض", 13799, 14489,
                 url="https://www.noon.com/egypt-ar/search/?q=airpods+pro+3"),
        ],
    },
    {
        "keywords": ["شاومي", "xiaomi", "redmi", "ريدمي", "buds", "سماعة", "سماعات", "earbuds"],
        "name": "Xiaomi Redmi Buds 6 Active",
        "offers": [
            Item("jumia", "Xiaomi Redmi Buds 6 Active - أزرق", 745, 999,
                 url="https://www.jumia.com.eg/catalog/?q=redmi+buds+6+active"),
            Item("noon", "شاومي ريدمي بادز 6 أكتيف - أسود", 799, 1100,
                 url="https://www.noon.com/egypt-ar/search/?q=redmi+buds+6"),
        ],
    },
    {
        "keywords": ["سامسونج", "samsung", "galaxy", "buds", "جالاكسي", "سماعة", "سماعات", "earbuds"],
        "name": "Samsung Galaxy Buds 3 Pro",
        "offers": [
            Item("jumia", "Samsung Galaxy Buds 3 Pro - فضي", 6300, 7499,
                 url="https://www.jumia.com.eg/catalog/?q=galaxy+buds+3+pro"),
            Item("noon", "سامسونج جالاكسي بادز 3 برو", 6899, 7999,
                 url="https://www.noon.com/egypt-ar/search/?q=galaxy+buds+3+pro"),
        ],
    },
]

GENERIC_WORDS = {"سماعة", "سماعات", "earbuds", "headphones", "هيدفون", "بلوتوث", "لاسلكية", "وايرلس"}


def search_demo(query: str):
    """يبحث في البيانات التجريبية ويرجع (items, matched_names)
    منطق المطابقة: الكلمات العامة (سماعات...) بتطابق كل حاجة،
    والكلمات المحددة (ماركة/موديل) لازم تتطابق — ونرتب حسب قوة التطابق.
    """
    q = query.lower().strip()
    q_tokens = [t for t in q.split() if t]
    specific_q = [t for t in q_tokens if t not in GENERIC_WORDS]

    scored = []  # (score, product)
    for prod in DEMO_PRODUCTS:
        specific_kws = {k.lower() for k in prod["keywords"] if k not in GENERIC_WORDS}
        if not specific_q:
            score = 1  # بحث عام زي "سماعات" → كل المنتجات
        else:
            score = 0
            for k in specific_kws:
                if k in q or any(k in t or t in k for t in specific_q):
                    score += 1
        if score > 0:
            scored.append((score, prod))

    if not scored:
        return [], []

    # نحتفظ بالأعلى تطابقًا، ونسمح باللي أقل بدرجة واحدة بس لو تطابقه قوي (كلمتين+)
    max_score = max(s for s, _ in scored)
    threshold = max_score if max_score >= 2 else 1

    items, matched = [], []
    for score, prod in scored:
        if score >= threshold or (score >= 2 and score >= max_score - 1):
            items.extend(prod["offers"])
            matched.append(prod["name"])

    # إزالة التكرار
    seen = set()
    unique = []
    for it in items:
        key = (it.store, it.title)
        if key not in seen:
            seen.add(key)
            unique.append(it)
    return unique, matched


SUGGESTIONS = ["Huawei FreeBuds SE 2", "Huawei FreeBuds 6i", "Soundcore R50i", "Soundcore R50i NC",
               "Soundcore P40i", "Liberty 4 NC", "AirPods 4", "AirPods Pro 3",
               "Redmi Buds 6", "Galaxy Buds 3 Pro"]
