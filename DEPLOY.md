# Sog'lom Turmush deploy qo'llanmasi

Bu loyiha uchta hostingga moslab tayyorlandi: Render, Railway va Koyeb.

Muhim billing eslatma:

- Render: free web service mavjud, ishlatilmaganda uxlab qolishi mumkin.
- Railway: free/trial kredit asosida ishlaydi, resurs tugasa to'lov so'rashi mumkin.
- Koyeb: bitta free web service beradi, lekin account validatsiyasi/billing tekshiruvi so'ralishi mumkin.

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

## 3. Koyeb

Koyeb GitHub orqali Django app deploy qila oladi. Bu loyiha `start.sh` orqali ishga tushadi.

1. Koyeb dashboard -> Create Web Service.
2. GitHub repository'ni tanlang:

```text
Bahromjon04/soghlom_turmush
```

3. Branch:

```text
main
```

4. Builder/Runtime qismida Python yoki Docker tanlansa ham loyiha ishlashi mumkin. Oddiyroq yo'l:

```text
Build command:
pip install -r requirements.txt && python manage.py collectstatic --no-input
```

```text
Run command:
bash start.sh
```

5. Port:

```text
8000
```

6. Environment variables:

```text
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.koyeb.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.koyeb.app
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SEED_DATA=True
DJANGO_SECRET_KEY=<secret>
PORT=8000
```

7. Instance tanlashda free instance tanlang.
8. Deploy tugagach, Koyeb `*.koyeb.app` domen beradi.

## Eslatma

Render, Railway va Koyeb GitHub orqali deploy qilishga qulay. Uchala variant ham demo va portfolio uchun yaxshi. Production uchun doimiy database, maxfiy sozlamalar, custom domain va backup kerak bo'ladi.
