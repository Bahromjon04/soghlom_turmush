# 🥗 Sog'lom Turmush – Kaloriya va Ovqat Nazorat Tizimi

Django asosida qurilgan to'liq funksional veb-ilova. Mahalliy taomlar bazasi, kunlik ovqat jurnali, kaloriya hisoblash va vazn monitoringi.

## 🚀 O'rnatish va ishga tushirish

### 1. Python virtual muhitini yaratish (tavsiya etiladi)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Kerakli paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Ma'lumotlar bazasini tayyorlash
```bash
python manage.py migrate
```

### 4. Test ma'lumotlarini yuklash (30 ta taom + demo foydalanuvchi)
```bash
python manage.py seed_data
```

### 5. Superuser yaratish (admin panel uchun)
```bash
python manage.py createsuperuser
```

### 6. Serverni ishga tushirish
```bash
python manage.py runserver
```

### 7. Brauzerda ochish
- **Asosiy sahifa:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

---

## 🔑 Demo kirish ma'lumotlari
| Maydon | Qiymat |
|--------|--------|
| Email | test@demo.com |
| Parol | demo123 |

---

## 📱 Sahifalar
| URL | Tavsif |
|-----|--------|
| `/` | Bosh sahifa – bugungi kaloriya va ovqat |
| `/kundalik/` | Ovqat jurnali (kun/hafta) |
| `/taomlar/` | Mahalliy taomlar bazasi (filtr/qidiruv) |
| `/tavsiyalar/` | Shaxsiylashtirilgan tavsiyalar |
| `/taraqqiyot/` | Vazn grafigi, haftalik statistika |
| `/faollik/` | Jismoniy faollik yozuvi |
| `/profil/` | Foydalanuvchi profili va sozlamalar |
| `/admin/` | Admin panel |

---

## ⚙️ Asosiy funksiyalar
- **BMR/TDEE hisoblash** – Mifflin-St Jeor formulasi
- **Kunlik kaloriya maqsadi** – Vazn yo'qotish (−15%), saqlash, orttirish (+15%)
- **30+ mahalliy taom** – Osh, Manti, Shashlik, Lag'mon va boshqalar
- **Porsiya kalkulyatori** – Har bir taom uchun kaloriya/makronutrient hisoblash
- **Ovqat jurnali** – Nonushta, tushlik, kechki ovqat, gazak
- **Vazn monitoringi** – Grafik va maqsadga progress
- **Suv iste'moli** – Kunlik nazorat
- **Jismoniy faollik** – Kaloriya sarfi hisoblash
- **Tavsiya tizimi** – Like qilingan taomlar asosida
- **Chart.js grafiklar** – Vazn va kaloriya vizualizatsiyasi

---

## 🗃️ Loyiha tuzilmasi
```
soghlom_turmush/
├── manage.py
├── requirements.txt
├── README.md
├── soghlom_turmush/          # Django loyiha sozlamalari
│   ├── settings.py
│   └── urls.py
└── core/                     # Asosiy ilova
    ├── models.py             # Ma'lumotlar modellari
    ├── views.py              # Ko'rinishlar
    ├── urls.py               # URL yo'nalishlari
    ├── forms.py              # Formalar
    ├── admin.py              # Admin panel
    ├── management/commands/
    │   └── seed_data.py      # Test ma'lumotlar
    └── templates/core/       # HTML shablonlar
```
