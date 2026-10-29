# -*- coding: utf-8 -*-
"""طبقة HTTP مشتركة للسكرابرز: بروكسي تلقائي + إعادة محاولة + رسائل خطأ عربية."""
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

import config

# رسائل عربية مفهومة لأشهر أخطاء الشبكة
ERRORS = {
    "ProxyError": "تعذر الاتصال بالبروكسي — راجع العنوان والمنفذ وبيانات الدخول",
    "ConnectError": "تعذر الوصول للسيرفر",
    "ConnectTimeout": "انتهت مهلة الاتصال",
    "ReadTimeout": "انتهت مهلة قراءة الرد",
    "PoolTimeout": "زحمة اتصالات — جرب تاني",
    "WriteTimeout": "انتهت مهلة إرسال الطلب",
    "TimeoutException": "انتهت المهلة",
    "TooManyRedirects": "تحويلات كتير جدًا",
    "UnsupportedProtocol": "بروتوكول غير مدعوم — لو socks5 تأكد من تثبيت httpx[socks]",
    "RemoteProtocolError": "رد غير متوقع من السيرفر",
    "DecodingError": "فشل فك ترميز الرد",
}


class ProxyConnectError(Exception):
    """فشل الاتصال عبر البروكسي (أو عبر الاتصال المباشر بعد فشل البروكسي)."""

    def __init__(self, message: str, via: str = "direct", proxy: str = ""):
        super().__init__(message)
        self.via = via
        self.proxy = proxy


@dataclass
class NetResponse:
    """رد HTTP مع معلومات عن طريقة الاتصال (مباشر / عبر بروكسي)."""

    status_code: int
    text: str
    url: str = ""
    via: str = "direct"          # direct | proxy
    proxy: str = ""              # مقنّع دايمًا
    elapsed_ms: int = 0
    attempts: int = 1
    error: str = ""

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


def describe_error(exc: BaseException) -> str:
    if isinstance(exc, ProxyConnectError):
        return str(exc)
    name = type(exc).__name__
    hint = ERRORS.get(name, "خطأ في الاتصال")
    return f"{hint} ({name})"


def _get_once(url: str, *, params, headers, timeout: float, proxy: str | None):
    common = {
        "params": params,
        "headers": headers,
        "timeout": timeout,
        "follow_redirects": True,
        "trust_env": False,
    }
    try:
        return httpx.get(url, proxy=proxy, **common)
    except TypeError:  # إصدارات httpx قديمة بتستخدم proxies=
        return httpx.get(url, proxies=proxy, **common)


def http_get(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    store: str | None = None,
    timeout: float | None = None,
) -> NetResponse:
    """GET بيجرّب البروكسيات المضبوطة بالترتيب ويرجع الرد أول ما ينجح.

    لو كل البروكسيات فشلت والـ PROXY_FALLBACK_DIRECT مفعّل، بيجرّب اتصال مباشر.
    لو كله فشل، بيرفع آخر استثناء عشان السكرابر يحوّله لرسالة واضحة.
    """
    started = time.time()
    candidates = config.proxy_candidates(store)
    using_proxy = bool(candidates)
    if not candidates:
        candidates = [(None, "direct")]

    # عدد المحاولات = SCRAPER_RETRIES (بحد أقصى عدد البروكسيات المتاحة)
    plan = candidates[: config.retries()]
    if using_proxy and config.fallback_direct():
        plan = plan + [(None, "direct")]

    # حالات بيعيد المحاولة على بروكسي مختلف (حظر مؤقت / بروكسي رافض / تحقق)
    retry_statuses = {403, 407, 429, 503}

    last_error: BaseException | None = None
    last_response = None
    for attempt, (proxy, _source) in enumerate(plan, start=1):
        try:
            response = _get_once(
                url,
                params=params,
                headers=headers,
                timeout=timeout or config.timeout(),
                proxy=proxy,
            )
        except Exception as exc:  # noqa: BLE001 — بنجرب البروكسي اللي بعده
            last_error = exc
            continue

        if response.status_code in retry_statuses and attempt < len(plan):
            last_response = response
            continue

        return NetResponse(
            status_code=response.status_code,
            text=response.text,
            url=str(response.url),
            via="direct" if proxy is None else "proxy",
            proxy=config.mask_proxy(proxy),
            elapsed_ms=int((time.time() - started) * 1000),
            attempts=attempt,
        )

    # كل المحاولات رجعت حظر → نرجّع آخر رد عشان السكرابر يشرح السبب
    if last_response is not None:
        return NetResponse(
            status_code=last_response.status_code,
            text=last_response.text,
            url=str(last_response.url),
            via="direct" if plan[-1][0] is None else "proxy",
            proxy=config.mask_proxy(plan[-1][0]),
            elapsed_ms=int((time.time() - started) * 1000),
            attempts=len(plan),
        )

    assert last_error is not None
    if not using_proxy:
        raise last_error

    tried_proxy = any(proxy is not None for proxy, _ in plan)
    tried_direct = any(proxy is None for proxy, _ in plan)
    parts = []
    if tried_proxy:
        parts.append("تعذر الاتصال بالبروكسي")
    if tried_direct:
        parts.append("وتعذر الاتصال المباشر كمان")
    raise ProxyConnectError(
        "، ".join(parts) + f" ({type(last_error).__name__})",
        via="proxy" if tried_proxy else "direct",
        proxy=config.mask_proxy(plan[0][0]) if plan and plan[0][0] else "",
    ) from last_error
