# -*- coding: utf-8 -*-
"""صيّاد الأسعار — Price Hunter Egypt  |  v3.0
مقارنة أسعار المنتجات في 11 متجر مصري.
© 2026 Tarek Abozaid — All rights reserved.
"""
import asyncio
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

import config
from scrapers import engine
from scrapers.net import describe_error
from scrapers.stores import ALL_STORES, IMAGE_HOSTS, public_list
from demo_data import search_demo, SUGGESTIONS

BASE_DIR = Path(__file__).parent
VERSION = "3.0.0"
OWNER = "Tarek Abozaid"

app = FastAPI(title="صيّاد الأسعار | Price Hunter", version=VERSION)

IP_ECHO_URL = "https://api.ipify.org?format=json"

# سقف التوازي — 11 متجر في نفس الوقت بيرفع فرصة الحظر، فبنقسّمهم مجموعات
MAX_PARALLEL_STORES = 6

# أقصى وقت لأي متجر — بعد كده بنكمّل بباقي النتائج
HARD_TIMEOUT = 9.0

# ------------------------------------------------------------------ الصلة
# كلمات عامة بتتشال قبل حساب الصلة (عشان "سماعات هواوي" يطابق "هواوي")
_STOP = {"سماعة", "سماعات", "هيدفون", "بلوتوث", "لاسلكية", "وايرلس", "earbuds",
         "headphones", "wireless", "من", "في", "على", "the", "for", "with", "and"}

# مرادفات عربي ↔ إنجليزي — بتخلي البحث بالعربي يطابق عناوين إنجليزية والعكس
_SYNONYMS = (
    ("ساوند كور", "soundcore"), ("ساوندكور", "soundcore"), ("ساوندكور", "soundcore"),
    ("فري بادز", "freebuds"), ("فري بودز", "freebuds"), ("فري بود", "freebuds"),
    ("أنكر", "anker"), ("انكر", "anker"), ("هواوي", "huawei"), ("شاومي", "xiaomi"),
    ("ريدمي", "redmi"), ("سامسونج", "samsung"), ("جالاكسي", "galaxy"), ("جلاكسي", "galaxy"),
    ("ابل", "apple"), ("آبل", "apple"), ("ايربودز", "airpods"), ("إيربودز", "airpods"),
    ("بادز", "buds"), ("بودز", "buds"), ("ليبرتي", "liberty"), ("سماعات", "earbuds"),
    ("سماعة", "earbuds"), ("عزل", "anc"), ("بلوتوث", "bluetooth"), ("شاحن", "charger"),
    ("كفر", "cover"), ("جراب", "case"), ("موبايل", "mobile"), ("لاب توب", "laptop"),
)

DIGIT = set("0123456789")


def _norm(text: str) -> str:
    """توحيد النص: حروف صغيرة + مرادفات + بدون رموز (بيحافظ على الأرقام)."""
    t = (text or "").lower()
    for ar, en in _SYNONYMS:
        t = t.replace(ar, f" {en} ")
    t = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in t)
    return " ".join(t.split())


def _tokens(text: str) -> set[str]:
    # بنسمح بالأرقام المفردة (3 / 4) لأنها بتفرّق بين الموديلات
    return {w for w in _norm(text).split()
            if (len(w) > 1 or w.isdigit()) and w not in _STOP}


def _relevance(query: str, items: list) -> set:
    """بيرجّع ids المنتجات القريبة من البحث.

    الترتيب في الصعوبة:
      1) منتجات عنوانها فيه كل كلمات البحث (بعد توحيد المرادفات) — دي الأدق.
      2) لو مفيش، منتجات فيها رقم موديل مطابق (r50i / 6i / p40i).
      3) لو مفيش، أي منتج فيه كلمة من البحث.
    الحسبة على نتائج كل المتاجر مع بعض عشان المتجر الضعيف ميجيبش حاجات ملهاش علاقة.
    """
    q = _tokens(query)
    if not q or not items:
        return {id(it) for it in items}

    scored = []
    for it in items:
        title = _norm(it.title)
        hits = sum(1 for w in q if w in title)
        scored.append((hits, it))

    full = {id(it) for hits, it in scored if hits == len(q)}
    if full:
        return full

    models = {w for w in q if any(ch in DIGIT for ch in w) and len(w) >= 2}
    if models:
        by_model = {id(it) for hits, it in scored
                    if hits > 0 and all(m in _norm(it.title) for m in models)}
        if by_model:
            return by_model

    return {id(it) for hits, it in scored if hits > 0} or {id(it) for it in items}


MAX_PARALLEL_STORES = 6

# أقصى وقت لأي متجر — بعد كده بنكمّل بباقي النتائج
HARD_TIMEOUT = 9.0



@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=2, max_length=120),
                     stores: str | None = Query(None, description="قائمة مفاتيح متاجر مفصولة بفاصلة")):
    started = time.time()
    wanted = {s.strip() for s in (stores or "").split(",") if s.strip()}
    profiles = [p for p in ALL_STORES if not wanted or p.key in wanted]

    semaphore = asyncio.Semaphore(MAX_PARALLEL_STORES)

    async def run(profile):
        async with semaphore:
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(engine.search_one, profile, q), timeout=HARD_TIMEOUT)
            except asyncio.TimeoutError:
                raise TimeoutError("انتهت المهلة")

    results = await asyncio.gather(*[run(p) for p in profiles], return_exceptions=True)

    stores_payload = []
    per_store = []          # [(store_payload, items)]
    all_items = []
    for profile, sr in zip(profiles, results):
        if isinstance(sr, Exception):
            stores_payload.append({
                "store": profile.key, "name": profile.ar, "name_en": profile.en,
                "color": profile.color, "status": "error",
                "message": describe_error(sr), "elapsed_ms": 0, "count": 0,
                "via": "direct", "proxy": "", "site": profile.base,
            })
            continue
        stores_payload.append({
            "store": sr.store, "name": profile.ar, "name_en": profile.en,
            "color": profile.color, "status": sr.status, "message": sr.message,
            "elapsed_ms": sr.elapsed_ms, "count": len(sr.items),
            "via": sr.via, "proxy": sr.proxy, "site": profile.base,
        })
        if sr.status == "ok":
            per_store.append((stores_payload[-1], sr.items))

    # فلترة الصلة مرة واحدة على نتائج كل المتاجر
    if per_store:
        keep = _relevance(q, [it for _, items in per_store for it in items])
        for payload, items in per_store:
            kept = [it for it in items if id(it) in keep][:12]
            payload["count"] = len(kept)
            all_items.extend(kept)

    mode = "live" if all_items else "demo"
    proxy_status = config.public_status()

    demo_note = ""
    matched_names = []
    if not all_items:
        demo_items, matched_names = search_demo(q)
        all_items = demo_items
        route = "عبر البروكسي" if proxy_status["enabled"] else "المباشر"
        if demo_items:
            demo_note = (f"تعذر الوصول {route} إلى المتاجر من هذا الخادم — "
                         "يتم عرض بيانات تجريبية من رصد أكتوبر 2026")
        else:
            demo_note = (f"تعذر الوصول {route} إلى المتاجر، "
                         "ولا توجد بيانات تجريبية مطابقة لهذا البحث")

    items = [it.to_dict() for it in all_items if it.price]
    items.sort(key=lambda x: x["price"])

    best = items[0] if items else None
    avg = round(sum(i["price"] for i in items) / len(items)) if items else None
    live_stores = len({i["store"] for i in items})

    return JSONResponse({
        "query": q,
        "mode": mode,
        "version": VERSION,
        "owner": OWNER,
        "demo_note": demo_note,
        "matched_products": matched_names,
        "suggestions": SUGGESTIONS if (mode == "demo" and not items) else [],
        "proxy": proxy_status,
        "stores": stores_payload,
        "summary": {
            "count": len(items),
            "stores_count": live_stores,
            "best_price": best["price"] if best else None,
            "best_store": best["store"] if best else None,
            "avg_price": avg,
            "took_ms": int((time.time() - started) * 1000),
        },
        "items": items,
    })


@app.get("/api/stores")
async def api_stores():
    """قائمة المتاجر المدعومة (الاسم بالعربي والإنجليزي + اللون + الموقع)."""
    return {"count": len(ALL_STORES), "stores": public_list()}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": VERSION,
        "owner": OWNER,
        "stores": len(ALL_STORES),
        "proxy": config.public_status(),
        "time": int(time.time()),
    }


@app.get("/api/proxy-info")
async def proxy_info():
    """اختبار سريع للبروكسي: بيقارن IP الاتصال المباشر بـ IP الخروج من البروكسي.

    آمن للعرض: مفيش أي بيانات دخول بترجع، والبروكسيات بتظهر مقنّعة.
    """
    started = time.time()
    status = config.public_status()
    targets = config.unique_proxies(limit=3)

    async def probe(proxy: str | None) -> dict:
        t0 = time.time()
        try:
            kwargs = {"timeout": 8.0, "follow_redirects": True, "trust_env": False}
            try:
                client = httpx.AsyncClient(proxy=proxy, **kwargs)
            except TypeError:  # httpx قديم
                client = httpx.AsyncClient(proxies=proxy, **kwargs)
            async with client:
                resp = await client.get(IP_ECHO_URL)
                resp.raise_for_status()
                try:
                    ip = resp.json().get("ip", "")
                except Exception:
                    ip = resp.text.strip()[:64]
            return {"reachable": True, "exit_ip": ip,
                    "latency_ms": int((time.time() - t0) * 1000), "error": ""}
        except Exception as e:  # noqa: BLE001
            return {"reachable": False, "exit_ip": "",
                    "latency_ms": int((time.time() - t0) * 1000), "error": describe_error(e)}

    direct, *proxied = await asyncio.gather(probe(None), *[probe(url) for url, _ in targets])

    servers = []
    for index, ((url, source), result) in enumerate(zip(targets, proxied), start=1):
        label = f"{source} #{index}" if len(targets) > 1 else source
        servers.append({"label": label, "masked": config.mask_proxy(url), **result})

    if not servers:
        verdict = "no_proxy"
        note = "مفيش بروكسي متظبط — السكرابينج بيشتغل اتصال مباشر من IP السيرفر."
    elif any(s["reachable"] for s in servers):
        verdict = "proxy_ok"
        note = "البروكسي شغال ✅ — كل بحث جديد هيعدي من البروكسي تلقائيًا."
    else:
        verdict = "proxy_failed"
        note = "البروكسي متظبط بس مش واصل — راجع العنوان/البيانات/الاشتراك."

    same_ip = bool(direct.get("exit_ip") and
                   any(s.get("exit_ip") == direct["exit_ip"] for s in servers))
    if same_ip:
        note += " تنبيه: IP الخروج نفس IP السيرفر — غالبًا البروكسي مش شغال فعلًا."

    return JSONResponse({
        "verdict": verdict, "note": note,
        "took_ms": int((time.time() - started) * 1000),
        "proxy": status, "direct": direct, "servers": servers,
        "env_keys": config.configured_env_keys(),
    })


# ------------------------------------------------------------ بروكسي الصور
_IMG_CACHE: dict[str, tuple[bytes, str]] = {}
_IMG_CACHE_MAX = 240


def _host_ok(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    if not host:
        return False
    return any(host == h or host.endswith("." + h) for h in IMAGE_HOSTS)


@app.get("/api/img")
async def api_img(u: str = Query(..., max_length=800)):
    """بروكسي صور صغير: بيحل مشكلة الـ hotlink والحجب ويصغّر الصور.

    بيقبل دومينات المتاجر المعروفة بس (allowlist) — مفيش استخدام كبروكسي مفتوح.
    """
    if not u.startswith(("http://", "https://")) or not _host_ok(u):
        return JSONResponse({"error": "domain not allowed"}, status_code=400)
    if u in _IMG_CACHE:
        data, ctype = _IMG_CACHE[u]
        return Response(data, media_type=ctype,
                        headers={"Cache-Control": "public, max-age=86400"})
    candidates = config.proxy_candidates()
    plan = [candidates[0][0]] if candidates else []
    plan.append(None)  # اتصال مباشر كخطة بديلة

    for proxy in plan:
        try:
            kwargs = {"timeout": 12.0, "follow_redirects": True, "trust_env": False}
            try:
                client = httpx.AsyncClient(proxy=proxy, **kwargs)
            except TypeError:
                client = httpx.AsyncClient(proxies=proxy, **kwargs)
            async with client:
                resp = await client.get(u, headers={"User-Agent": "Mozilla/5.0", "Referer": u})
            if resp.status_code != 200 or not resp.content:
                continue
            ctype = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip().lower()
            # بعض CDNs بترجّع octet-stream — بنتأكد من امتداد الصورة
            if not ctype.startswith("image/"):
                ext_ok = any(u.lower().split("?")[0].endswith(e) for e in
                             (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"))
                if not ext_ok:
                    continue
                guess = next(e for e in (".webp", ".png", ".jpg", ".jpeg", ".avif", ".gif")
                             if u.lower().split("?")[0].endswith(e))
                ctype = {".webp": "image/webp", ".png": "image/png", ".avif": "image/avif",
                         ".gif": "image/gif"}.get(guess, "image/jpeg")
            if len(resp.content) > 2_500_000:
                continue
            if len(_IMG_CACHE) > _IMG_CACHE_MAX:
                _IMG_CACHE.clear()
            _IMG_CACHE[u] = (resp.content, ctype)
            return Response(resp.content, media_type=ctype,
                            headers={"Cache-Control": "public, max-age=86400"})
        except Exception:  # noqa: BLE001
            continue
    return JSONResponse({"error": "image unavailable"}, status_code=502)


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
