# صيّاد الأسعار 🎯 — Price Hunter Egypt

موقع لمقارنة أسعار المنتجات في **11 متجر مصري**.
اكتب اسم المنتج → الموقع يبحث في المتاجر كلها في نفس الوقت → يطلعلك تقرير مرتب بالأسعار
مع **صورة صغيرة لكل منتج** وأرخص عرض ورابط مباشر للمتجر.

**الإصدار:** `3.0.0` — © 2026 **Tarek Abozaid** — All Rights Reserved ™

---

## ✨ الجديد في 3.0

| الميزة | التفاصيل |
|---|---|
| 🏪 **8 متاجر جديدة** | فونتكس • دريم 2000 • 2B • اتصال ستور • دبي فون • بي تك • ميامي سنترز • رنين |
| 🖼️ **صورة لكل منتج** | مصغّرة 64 بكسل + `lazy loading` + بروكسي صور `/api/img` + بديل SVG لو الصورة مش متاحة |
| 🌐 **عربي / إنجليزي** | زرار لغة فوق على الشمال، بيقلب اتجاه الصفحة ويحفظ الاختيار |
| 📱 **متوافق مع الموبايل والكمبيوتر** | تصميم متجاوب بالكامل — الكروت بتتحول تلقائيًا على الشاشات الصغيرة |
| 🤖 **أدوات ذكاء اصطناعي** | أزرار Gemini / ChatGPT / Claude بسؤال جاهز عن نفس المنتج |
| ⚡ **أسرع** | 6 متاجر بالتوازي + قاطع دائرة بيتخطى المتجر الفاشل مؤقتًا |
| 🛡️ **بروكسي محسّن** | دعم `<KEY>_PROXY` لأي متجر + بروكسي صور + اختبار جاهز |
| © **حقوق** | Trademark & Copyright في الفوتر بكل اللغات |

---

## 🏪 المتاجر المدعومة

| # | المتجر | الموقع | المحرك |
|---|---|---|---|
| 1 | جوميا | jumia.com.eg | سكرابر مخصص |
| 2 | نون | noon.com | سكرابر مخصص (`__NEXT_DATA__`) |
| 3 | أمازون مصر | amazon.eg | سكرابر مخصص |
| 4 | فونتكس | vontx.com | Shopify |
| 5 | دريم 2000 | dream2000.com | Shopify |
| 6 | 2B | 2b.com.eg | Magento |
| 7 | اتصال ستور | etisalstore.com | Generic |
| 8 | دبي فون | dubaiphone.net | Magento |
| 9 | بي تك | btech.com | Generic |
| 10 | ميامي سنترز | miamicenters.com | WooCommerce |
| 11 | رنين | raneen.com | Magento |

> بعض المتاجر بتحظر IP السيرفرات (Cloudflare) — بتظهر «محجوب» وبتشتغل تلقائيًا أول ما تضيف بروكسي سكني.
> **4 متاجر على الأقل** (فونتكس، دريم 2000، ميامي، اتصال) بتشتغل حية بدون بروكسي.

---

## 🚀 التشغيل محليًا

```bash
pip install -r requirements.txt
python app.py
# افتح http://localhost:8000
```

مع بروكسي:

```bash
cp .env.example .env      # املأ PROXY_URL
python app.py
```

---

## 📘 دليل GitHub والبروكسي

دليل عربي كامل خطوة بخطوة — **`static/guide.html`** (بيتفتح من الفوتر في الموقع، أو من المسار `/static/guide.html`):

1. تعديل ملف موجود على GitHub من المتصفح (✏️ → Commit).
2. رفع ملفات جديدة (صور المنتجات).
3. التعديل من الكمبيوتر بأوامر `git`.
4. إضافة متجر جديد في 3 خطوات.
5. تشغيل البروكسي على Render واختباره وقراءة النتيجة.
6. أخطاء شائعة وحلولها.

وفيه كمان دليل النشر المصوّر القديم في **`deploy-guide.html`** (GitHub + Render + البروكسي).

---

## 🌐 النشر على Render (مجانًا)

1. ارفع المشروع على GitHub — لازم `app.py` في جذر المستودع.
2. في [render.com](https://render.com): **New + → Web Service** واربط المستودع.
3. الإعدادات:

   | الإعداد | القيمة |
   |---|---|
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | `Free` |

4. **Create Web Service** → رابطك: `https://your-app.onrender.com`.

> الخطة المجانية بتنام بعد 15 دقيقة بدون زيارات. استخدم [cron-job.org](https://cron-job.org)
> يعمل ping لـ `/api/health` كل 10 دقايق.

---

## 🌐 البروكسي (مهم للسكرابينج الحي)

في Render: **Environment → Add Environment Variable**

```
PROXY_URL = http://USERNAME:PASSWORD@HOST:PORT
```

Save → استنى الـ redeploy → افتح `/api/proxy-info`.

### المتغيرات المدعومة

| المتغير | الوظيفة |
|---|---|
| `PROXY_URL` | بروكسي واحد لكل المتاجر |
| `PROXY_LIST` | أكتر من بروكسي (فاصلة أو سطر جديد) — تدوير تلقائي |
| `JUMIA_PROXY` / `NOON_PROXY` / `AMAZON_PROXY` / `VONTX_PROXY` / `DREAM2000_PROXY` / `2B_PROXY` / `ETISAL_PROXY` / `DUBAIPHONE_PROXY` / `BTECH_PROXY` / `MIAMI_PROXY` / `RANEEN_PROXY` | بروكسي مخصص لمتجر (`off` لتعطيله) |
| `PROXY_HOST` + `PROXY_PORT` (+ `PROXY_USERNAME` / `PROXY_PASSWORD` / `PROXY_SCHEME`) | بيانات مقسّمة بدل الرابط |
| `PROXY_ROTATE` | `round` (افتراضي) / `random` / `sticky` |
| `PROXY_FALLBACK_DIRECT` | `1` (افتراضي) يجرّب اتصال مباشر بعد فشل البروكسي |
| `SCRAPER_TIMEOUT` | مهلة الطلب بالثواني (افتراضي 8) |
| `SCRAPER_RETRIES` | محاولات البروكسي لكل طلب (افتراضي 2) |

### الصيغ المقبولة

```
http://user:pass@host:port      https://user:pass@host:port
socks5://user:pass@host:port    host:port
host:port:user:pass             user:pass@host:port
```

### اختبار البروكسي

```
GET /api/proxy-info
```

```json
{
  "verdict": "proxy_ok",
  "note": "البروكسي شغال ✅ — كل بحث جديد هيعدي من البروكسي تلقائيًا.",
  "direct": { "exit_ip": "51.x.x.x", "reachable": true },
  "servers": [{ "masked": "http://user:***@proxy:8000", "exit_ip": "185.x.x.x", "reachable": true }]
}
```

> بيانات الدخول مقنّعة دايمًا (`user:***`) ومبتظهرش في أي رد API.

---

## 🔌 الـ API

```
GET /api/search?q=سماعات هواوي            # بحث في كل المتاجر
GET /api/search?q=iphone&stores=btech,2b  # بحث في متاجر محددة
GET /api/stores                            # قائمة المتاجر (عربي/إنجليزي)
GET /api/img?u=<image-url>                 # بروكسي صور (allowlist لدومينات المتاجر)
GET /api/proxy-info                        # اختبار البروكسي
GET /api/health                            # الحالة + الإصدار
```

كل رد `/api/search` فيه: حالة كل متجر (`ok` / `blocked` / `empty` / `error`) وسببها،
قائمة العروض مرتبة بالسعر، أقل سعر ومتوسطه، وحالة البروكسي.

---

## 🖼️ صور المنتجات

- **وضع حي:** الصور بتتجيب من المتجر نفسه، ومصغّرة (Shopify `width=160`)، ومعاها
  `onerror` بيجرّب `/api/img` وبعدها بديل نصي بلون المتجر.
- **وضع تجريبي:** صور محلية صغيرة في `static/img/products/` (~3 كيلوبايت للصورة)
  عشان الصفحة تشتغل حتى بدون إنترنت.

عايز تضيف صورة لمنتج؟ ارفعها في `static/img/products/` وأضف المسار في `demo_data.py`:

```python
{"name": "Huawei FreeBuds SE 2", "image": "/static/img/products/freebuds-se-2.jpg", ...}
```

---

## 🧩 المكونات

| الملف | الوظيفة |
|---|---|
| `app.py` | سيرفر FastAPI: البحث، المتاجر، بروكسي الصور، اختبار البروكسي |
| `config.py` | إعدادات البروكسي من متغيرات البيئة + التدوير + الإخفاء |
| `scrapers/stores.py` | **سجل المتاجر** — إضافة متجر = سطر واحد |
| `scrapers/generic.py` | المحرك العام (Shopify / WooCommerce / Magento / JSON-LD / Next.js) |
| `scrapers/engine.py` | التوجيه + قاطع الدائرة |
| `scrapers/net.py` | طبقة HTTP: بروكسي + إعادة محاولة + رسائل عربية |
| `scrapers/jumia.py` `noon.py` `amazon.py` | سكرابرز مخصصة للمتاجر التلاتة الكبار |
| `demo_data.py` | بيانات تجريبية (رصد أكتوبر 2026) + صور محلية |
| `static/index.html` | الواجهة: عربي/إنجليزي، متجاوبة، صور، أدوات AI |
| `static/guide.html` | دليل GitHub + البروكسي |
| `deploy-guide.html` | دليل النشر المصوّر (GitHub + Render) |

---

## 🧪 اختبار سريع

```bash
curl "http://localhost:8000/api/health"
curl "http://localhost:8000/api/search?q=soundcore%20r50i"
curl "http://localhost:8000/api/search?q=iphone&stores=2b,raneen"   # وضع تجريبي
curl "http://localhost:8000/api/proxy-info"
```

---

## ⚖️ الترخيص والحقوق

**© 2026 Tarek Abozaid — All Rights Reserved.**
«صيّاد الأسعار / Price Hunter» علامة تجارية ™.
الأسعار المعروضة ملك المتاجر أصحابها، والموقع بيستخدمها لغرض العرض والمقارنة فقط.
احترم شروط استخدام كل موقع وخلّي بين الطلبات مسافة معقولة (Rate limiting).
