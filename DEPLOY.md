# Sog'lom Turmush deploy qo'llanmasi

Bu loyiha uchta hostingga moslab tayyorlandi: Render, Railway va Fly.io.

Muhim billing eslatma:

- Render: free web service mavjud, ishlatilmaganda uxlab qolishi mumkin.
- Railway: free/trial kredit asosida ishlaydi, resurs tugasa to'lov so'rashi mumkin.
- Fly.io: yangi accountlarda odatda pay-as-you-go, karta talab qilishi mumkin.

## 0. Umumiy tayyorgarlik

1. Git repository yarating:

```bash
git init
git add .
git commit -m "Prepare Django project for deployment"
```

2. GitHub'ga yangi repository oching va push qiling.

3. Muhim environment variable'lar:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<uzun-maxfiy-kalit>
DJANGO_ALLOWED_HOSTS=<hostlar-vergul-bilan>
DJANGO_CSRF_TRUSTED_ORIGINS=<https-originlar-vergul-bilan>
```

Demo uchun SQLite ishlaydi. Lekin bepul web instance diskini doimiy saqlashga kafolat bermaydi, shuning uchun jiddiy foydalanishda Postgres qo'shish kerak bo'ladi.

## 1. Render

Render bepul web service beradi, lekin bepul servis ishlatilmaganda uxlab qolishi mumkin.

1. GitHub repository'ni Render'ga ulang.
2. New -> Web Service tanlang.
3. Agar `render.yaml` orqali deploy qilsangiz, Render sozlamalarni o'zi o'qiydi.
4. Manual sozlash kerak bo'lsa:

```text
Build command: bash build.sh
Start command: bash start.sh
```

5. Environment variables:

```text
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.onrender.com
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECRET_KEY=<secret>
PYTHON_VERSION=3.12.8
DJANGO_SEED_DATA=True
```

6. `DJANGO_SEED_DATA=True` bo'lsa demo taomlar start paytida avtomatik yaratiladi.

## 2. Railway

Railway GitHub yoki CLI orqali Python app deploy qila oladi. Bu repo ichida `railway.json` bor, shuning uchun Railway build/start komandalarini o'zi oladi.

1. Railway dashboard -> New Project.
2. Deploy from GitHub repo tanlang.
3. Repository'ni ulang.
4. Variables bo'limiga kiriting:

```text
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.up.railway.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.up.railway.app
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECRET_KEY=<secret>
DJANGO_SEED_DATA=True
```

5. Deploy tugagach, Railway public domain beradi. Odatda `*.up.railway.app` ko'rinishida bo'ladi.

Eslatma: Railway uchun majburiy healthcheck o'chirilgan. Django app ishga tushgach public domain orqali qo'lda tekshiriladi.

CLI orqali deploy qilish:

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

## 3. Fly.io

Fly.io Dockerfile orqali deploy qiladi. Bu repo ichida `Dockerfile` va `fly.toml` tayyor.

1. Fly CLI o'rnating va login qiling.
2. Birinchi marta app yaratish:

```bash
fly auth login
fly launch --no-deploy
```

3. `fly.toml` ichidagi `app = "soghlom-turmush"` nomi band bo'lsa, boshqa unikal nom qo'ying.
4. Secret key qo'ying:

```bash
fly secrets set DJANGO_SECRET_KEY="<secret>"
```

5. Deploy qiling:

```bash
fly deploy
```

Sayt URL'i:

```text
https://<app-name>.fly.dev
```

## Eslatma

Render va Railway GitHub orqali deploy qilishga qulay. Fly.io CLI/Docker orqali ancha nazorat beradi. Uchala variant ham demo va portfolio uchun yaxshi. Production uchun doimiy database, maxfiy sozlamalar, custom domain va backup kerak bo'ladi.
