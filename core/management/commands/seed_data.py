from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import UserProfile, Food, DiaryEntry, WeightRecord, WaterIntake
from datetime import date, timedelta


FOODS_DATA = [
    # name, meal_type, cal/100g, protein, fat, carbs, portion_g, region, description
    ("Osh (Palov)", "lunch", 210, 7.5, 10.5, 23.0, 350, "toshkent", "O'zbekistonning milliy taomi. Guruch, go'sht, sabzi, piyoz va ziravorlardan tayyorlanadi."),
    ("Manti", "lunch", 185, 11.0, 8.5, 18.0, 300, "umumiy", "Qo'y go'shtidan tayyorlangan, bug'da pishirilgan xomirli taom."),
    ("Shashlik", "lunch", 215, 18.5, 14.5, 2.0, 200, "umumiy", "Ko'mirda qovirilgan go'sht kabob. Ko'pincha qo'y yoki mol go'shtidan."),
    ("Lag'mon", "lunch", 155, 9.0, 6.5, 16.0, 400, "fargona", "Qo'lda cho'zilgan makaron, sabzavot va go'sht bilan tayyorlanadi."),
    ("Somsa", "snack", 280, 10.0, 14.0, 28.0, 150, "umumiy", "Tandirda pishirilgan yoki qovirilgan go'shtli yoki qovoqli pishiriq."),
    ("Dimlama", "lunch", 120, 8.0, 7.0, 8.0, 300, "umumiy", "Sabzavot va go'sht bir idishda dim qilinadi."),
    ("Shorva", "lunch", 65, 5.5, 3.5, 4.0, 400, "umumiy", "Go'sht va sabzavotli milliy sho'rva."),
    ("Non (Tandirda)", "breakfast", 265, 8.5, 3.0, 52.0, 150, "umumiy", "Tandirda yopilgan o'zbek noni."),
    ("Chuchvara", "lunch", 175, 9.5, 7.0, 19.0, 300, "toshkent", "Mayda go'shtli xomirli taom, sho'rva yoki qovurilgan holda beriladi."),
    ("Qozon kabob", "lunch", 240, 16.0, 16.5, 8.0, 250, "umumiy", "Qozonda yog'da qovirilgan go'sht va sabzavot."),
    ("Mastava", "lunch", 85, 5.0, 3.5, 9.0, 400, "samarqand", "Guruch, sabzavot va go'shtdan tayyorlangan qalin sho'rva."),
    ("Xonim", "lunch", 190, 10.0, 9.0, 17.0, 280, "umumiy", "Yupqa xamir ichiga go'sht yoki qovoq solib o'ralgan va bug'da pishirilgan taom."),
    ("Naryn", "lunch", 195, 12.0, 9.5, 16.0, 300, "buxoro", "Qaynatilgan go'sht va qo'lda kesilgan makaron bilan tayyorlanadi."),
    ("Tuxum barak", "lunch", 200, 11.5, 10.0, 18.0, 280, "xorazm", "Tuxum va go'shtdan tayyorlangan xomirli taom."),
    ("Qatiq (Yogurt)", "breakfast", 55, 3.5, 2.5, 5.0, 200, "umumiy", "Mahalliy fermentlangan sut mahsuloti, probiotikka boy."),
    ("Ko'k choy", "any", 2, 0.0, 0.0, 0.3, 250, "umumiy", "Yashil choy, antioxidantga boy."),
    ("Samsa (qovoqli)", "snack", 220, 5.0, 10.0, 28.0, 150, "umumiy", "Qovoq bilan to'ldirilgan tandirda pishirilgan pishiriq."),
    ("Shivit oshi", "lunch", 180, 8.0, 7.5, 21.0, 350, "xorazm", "Ukrop qo'shilgan maxsus rangdor osh."),
    ("Beshbarmaq", "lunch", 220, 14.0, 10.0, 20.0, 350, "umumiy", "Go'sht va yupqa xomirdan tayyorlangan taom."),
    ("Qovurma", "lunch", 250, 17.0, 18.0, 5.0, 200, "umumiy", "Yog'da qovirilgan go'sht."),
    ("Uzum (Tokay)", "snack", 65, 0.6, 0.2, 16.5, 150, "samarqand", "O'zbekistonning mashhur tokay uzumi."),
    ("Tarvuz", "snack", 30, 0.6, 0.1, 7.5, 300, "umumiy", "Yozda juda mashhur, suvli meva."),
    ("Qovun", "snack", 35, 0.9, 0.1, 8.0, 250, "umumiy", "Xushbo'y o'zbek qovuni."),
    ("Non-qovoq bo'tmasi", "breakfast", 95, 2.5, 3.5, 14.0, 200, "umumiy", "Qovoq va undan tayyorlangan bo'tma."),
    ("Halim", "breakfast", 150, 9.0, 5.5, 18.0, 300, "umumiy", "Bug'doy va go'shtdan tayyorlangan qalin bo'tma."),
    ("Qovoqli sho'rva", "lunch", 45, 2.0, 1.5, 6.5, 350, "umumiy", "Qovoq va sabzavotli yengil sho'rva."),
    ("Somsa (go'shtli)", "snack", 290, 12.0, 15.0, 27.0, 160, "umumiy", "Go'sht va piyozdan tayyorlangan somsa."),
    ("Sut bo'tma", "breakfast", 85, 3.5, 3.0, 11.0, 250, "umumiy", "Sut va un yoki guruchdan tayyorlangan nonushta."),
    ("Tandirda pishirilgan tovuq", "lunch", 165, 20.0, 8.5, 2.0, 200, "umumiy", "Tandirda pishirilgan to'liq tovuq."),
    ("Anor", "snack", 83, 1.2, 1.2, 18.7, 150, "samarqand", "Vitaminlarga boy anor meyvasi."),
]


class Command(BaseCommand):
    help = "Test ma'lumotlarini yaratish"

    def handle(self, *args, **options):
        self.stdout.write("Taomlar yaratilmoqda...")
        for item in FOODS_DATA:
            food, created = Food.objects.get_or_create(
                name=item[0],
                defaults={
                    'meal_type': item[1],
                    'calories_per_100g': item[2],
                    'protein_per_100g': item[3],
                    'fat_per_100g': item[4],
                    'carbs_per_100g': item[5],
                    'default_portion_g': item[6],
                    'region': item[7],
                    'description': item[8],
                }
            )
            if created:
                self.stdout.write(f"  + {food.name}")

        self.stdout.write("Demo foydalanuvchi yaratilmoqda...")
        user, created = User.objects.get_or_create(
            username='test@demo.com',
            defaults={
                'email': 'test@demo.com',
                'first_name': 'Ali',
                'last_name': 'Valiyev',
            }
        )
        if created:
            user.set_password('demo123')
            user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'age': 28,
                'height': 175,
                'weight': 78,
                'gender': 'male',
                'activity_level': 'moderate',
                'goal': 'lose',
                'target_weight': 72,
            }
        )
        profile.weight = 78
        profile.save()

        # 3 kunlik jurnal
        today = date.today()
        foods = list(Food.objects.all())
        if len(foods) >= 8:
            entries = [
                (today, 'breakfast', foods[14], 200),  # Qatiq
                (today, 'breakfast', foods[7], 100),   # Non
                (today, 'lunch', foods[0], 350),       # Osh
                (today, 'snack', foods[4], 150),       # Somsa
                (today - timedelta(1), 'breakfast', foods[7], 100),
                (today - timedelta(1), 'lunch', foods[1], 300),
                (today - timedelta(1), 'dinner', foods[6], 400),
                (today - timedelta(2), 'breakfast', foods[14], 200),
                (today - timedelta(2), 'lunch', foods[3], 400),
                (today - timedelta(2), 'dinner', foods[2], 200),
            ]
            for entry_date, meal_type, food, amount in entries:
                DiaryEntry.objects.get_or_create(
                    user=user,
                    food=food,
                    date=entry_date,
                    meal_type=meal_type,
                    defaults={'amount_g': amount}
                )

        # Vazn yozuvlari
        WeightRecord.objects.get_or_create(user=user, date=today - timedelta(14), defaults={'weight': 79.5})
        WeightRecord.objects.get_or_create(user=user, date=today - timedelta(7), defaults={'weight': 78.8})
        WeightRecord.objects.get_or_create(user=user, date=today, defaults={'weight': 78.0})

        self.stdout.write(self.style.SUCCESS("\n✅ Test ma'lumotlari muvaffaqiyatli yaratildi!"))
        self.stdout.write("  Email: test@demo.com")
        self.stdout.write("  Parol: demo123")
