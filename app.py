# -*- coding: utf-8 -*-
"""صيّاد الأسعار — Price Hunter Egypt
موقع مقارنة أسعار المنتجات في مواقع التسوق المصرية
"""
import asyncio
import time
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from scrapers import jumia, noon, amazon
from demo_data import search_demo, SUGGESTIONS

BASE_DIR = Path(__file__).parent

app = FastAPI(title="صيّاد الأسعار")

SCRAPERS = [jumia.search, noon.search, amazon.search]


@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=2, max_length=120)):
    started = time.time()
    tasks = [asyncio.to_thread(fn, q) for fn in SCRAPERS]
    store_results = await asyncio.gather(*tasks, return_exceptions=True)

    stores = []
    all_items = []
    live_count = 0
    for sr in store_results:
        if isinstance(sr, Exception):
            continue
        stores.append({
            "store": sr.store,
            "name": sr.store_name,
            "status": sr.status,
            "message": sr.message,
            "elapsed_ms": sr.elapsed_ms,
            "count": len(sr.items),
        })
        if sr.status == "ok":
            live_count += 1
            all_items.extend(sr.items)

    mode = "live" if all_items else "demo"

    # وضع العرض التجريبي: لو مفيش نتائج حية خالص
    demo_note = ""
    matched_names = []
    if not all_items:
        demo_items, matched_names = search_demo(q)
        all_items = demo_items
        if demo_items:
            demo_note = "تعذر الوصول المباشر للمتاجر من هذا الخادم — يتم عرض بيانات تجريبية من رصد أكتوبر 2026"
        else:
            demo_note = "تعذر الوصول للمتاجر، ولا توجد بيانات تجريبية مطابقة لهذا البحث"

    items = [it.to_dict() for it in all_items if it.price]
    items.sort(key=lambda x: x["price"])

    best = items[0] if items else None
    avg = round(sum(i["price"] for i in items) / len(items)) if items else None

    return JSONResponse({
        "query": q,
        "mode": mode,
        "demo_note": demo_note,
        "matched_products": matched_names,
        "suggestions": SUGGESTIONS if (mode == "demo" and not items) else [],
        "stores": stores,
        "summary": {
            "count": len(items),
            "best_price": best["price"] if best else None,
            "best_store": best["store"] if best else None,
            "avg_price": avg,
            "took_ms": int((time.time() - started) * 1000),
        },
        "items": items,
    })


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
