# -*- coding: utf-8 -*-
"""سجل المتاجر — كل متجر بوصف واحد (اسم عربي/إنجليزي، لون، محرك السكرابينج، رابط البحث).

إضافة متجر جديد = سطر واحد هنا + (اختياري) محرك جديد في generic.py.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoreProfile:
    key: str            # المفتاح في الـ API والواجهة
    ar: str             # الاسم بالعربي
    en: str             # الاسم بالإنجليزي
    color: str          # لون الشارة في الواجهة
    engine: str         # shopify / woocommerce / magento / generic
    search: str         # رابط البحث — {q} بيتعوّض بالكلمة
    base: str           # أصل الموقع (لتحويل الروابط النسبية)
    host: str           # دومين الصور المسموح بيها في بروكسي الصور
    currency: str = "EGP"

    @property
    def search_url(self) -> str:
        return self.search

    def url_for(self, query: str) -> str:
        from urllib.parse import quote_plus

        return self.search.replace("{q}", quote_plus(query))


# المتاجر الأصلية (سكرابرز مخصصة موجودة في jumia.py / noon.py / amazon.py)
CORE_STORES: list[StoreProfile] = [
    StoreProfile("jumia", "جوميا", "Jumia", "#f68b1e", "jumia",
                 "https://www.jumia.com.eg/catalog/?q={q}",
                 "https://www.jumia.com.eg", "jumia.com.eg"),
    StoreProfile("noon", "نون", "Noon", "#feee00", "noon",
                 "https://www.noon.com/egypt-ar/search/?q={q}",
                 "https://www.noon.com", "noon.com"),
    StoreProfile("amazon", "أمازون مصر", "Amazon Egypt", "#ff9900", "amazon",
                 "https://www.amazon.eg/s?k={q}",
                 "https://www.amazon.eg", "amazon.eg"),
]

# المتاجر المضافة — كلها بتشتغل على المحرك العام (generic.py)
EXTRA_STORES: list[StoreProfile] = [
    StoreProfile("vontx", "فونتكس", "Vontx", "#12b8a6", "shopify",
                 "https://vontx.com/search?q={q}&type=product",
                 "https://vontx.com", "vontx.com"),
    StoreProfile("dream2000", "دريم 2000", "Dream 2000", "#e4002b", "shopify",
                 "https://dream2000.com/search?q={q}&type=product",
                 "https://dream2000.com", "dream2000.com"),
    StoreProfile("2b", "2B", "2B", "#f7a600", "magento",
                 "https://2b.com.eg/catalogsearch/result/?q={q}",
                 "https://2b.com.eg", "2b.com.eg"),
    StoreProfile("etisal", "اتصال ستور", "Etisal Store", "#c8102e", "generic",
                 "https://etisalstore.com/en/products?search={q}",
                 "https://etisalstore.com", "etisalstore.com"),
    StoreProfile("dubaiphone", "دبي فون", "Dubai Phone", "#009fe3", "magento",
                 "https://www.dubaiphone.net/catalogsearch/result/?q={q}",
                 "https://www.dubaiphone.net", "dubaiphone.net"),
    StoreProfile("btech", "بي تك", "B.TECH", "#e30613", "generic",
                 "https://btech.com/ar/search?q={q}",
                 "https://btech.com", "btech.com"),
    StoreProfile("miami", "ميامي سنترز", "Miami Centers", "#f7941d", "woocommerce",
                 "https://miamicenters.com/?s={q}&post_type=product",
                 "https://miamicenters.com", "miamicenters.com"),
    StoreProfile("raneen", "رنين", "Raneen", "#8e44ad", "magento",
                 "https://raneen.com/catalogsearch/result/?q={q}",
                 "https://raneen.com", "raneen.com"),
]

ALL_STORES: list[StoreProfile] = CORE_STORES + EXTRA_STORES

BY_KEY: dict[str, StoreProfile] = {p.key: p for p in ALL_STORES}

# دومينات إضافية مسموح بيها في بروكسي الصور (CDNs المتاجر)
IMAGE_HOSTS: tuple[str, ...] = tuple(p.host for p in ALL_STORES) + (
    "jumia.com.eg", "noon.com", "amazon.eg", "media.flixcart.com", "f.nooncdn.com",
    "m.media-amazon.com", "vontx.com", "dream2000.com", "2b.com.eg", "etisalstore.com",
    "dubaiphone.net", "btech.com", "miamicenters.com", "raneen.com", "cdn.shopify.com",
    "cdn.supercommerce.io", "supercommerce.io", "images.ctfassets.net", "salla.sa",
)


def public_list() -> list[dict]:
    """قائمة المتاجر للواجهة (بدون أي بيانات داخلية)."""
    return [
        {
            "key": p.key,
            "ar": p.ar,
            "en": p.en,
            "color": p.color,
            "engine": p.engine,
            "search": p.search,
            "site": p.base,
            "host": p.host,
        }
        for p in ALL_STORES
    ]
