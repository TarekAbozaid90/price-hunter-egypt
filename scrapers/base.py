# -*- coding: utf-8 -*-
"""أدوات مشتركة للسكرابرز"""
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
}


@dataclass
class Item:
    store: str            # jumia / noon / amazon
    title: str
    price: Optional[float]
    old_price: Optional[float] = None
    currency: str = "EGP"
    url: str = ""
    image: Optional[str] = None

    def discount_pct(self):
        if self.price and self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return None

    def to_dict(self):
        d = asdict(self)
        d["discount"] = self.discount_pct()
        return d


@dataclass
class StoreResult:
    store: str
    store_name: str
    status: str           # ok / blocked / error / empty
    message: str = ""
    items: list = field(default_factory=list)
    elapsed_ms: int = 0


def parse_price(text: str) -> Optional[float]:
    """يستخرج الرقم من نص زي 'EGP 1,299.00' أو '1,299 جنيه'"""
    if not text:
        return None
    m = re.search(r"([\d,]+(?:\.\d+)?)", text.replace("٬", ","))
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None
