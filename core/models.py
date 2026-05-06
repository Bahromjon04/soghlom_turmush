from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    GENDER_CHOICES = [('male', 'Erkak'), ('female', 'Ayol')]
    ACTIVITY_CHOICES = [
        ('sedentary', 'Kam harakatli (ofis ishi)'),
        ('light', 'Engil faol (haftada 1-3 kun sport)'),
        ('moderate', 'O\'rtacha faol (haftada 3-5 kun sport)'),
        ('very_active', 'Juda faol (haftada 6-7 kun sport)'),
        ('extra_active', 'Jismoniy mehnat / professional sport'),
    ]
    GOAL_CHOICES = [
        ('lose', 'Vazn yo\'qotish'),
        ('maintain', 'Vaznni saqlash'),
        ('gain', 'Vazn orttirish'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(default=25, verbose_name="Yosh")
    height = models.FloatField(default=170, verbose_name="Bo'y (sm)")
    weight = models.FloatField(default=70, verbose_name="Vazn (kg)")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name="Jins")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='moderate', verbose_name="Faollik darajasi")
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default='maintain', verbose_name="Maqsad")
    target_weight = models.FloatField(null=True, blank=True, verbose_name="Maqsad vazn (kg)")
    daily_calorie_goal = models.IntegerField(default=2000, verbose_name="Kunlik kaloriya maqsadi")
    daily_water_goal = models.IntegerField(default=8, verbose_name="Kunlik suv maqsadi (stakan)")

    def calculate_bmr(self):
        """Mifflin-St Jeor formula"""
        if self.gender == 'male':
            return 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            return 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

    def calculate_tdee(self):
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9,
        }
        bmr = self.calculate_bmr()
        multiplier = activity_multipliers.get(self.activity_level, 1.55)
        return bmr * multiplier

    def calculate_goal_calories(self):
        tdee = self.calculate_tdee()
        if self.goal == 'lose':
            return round(tdee * 0.85)
        elif self.goal == 'gain':
            return round(tdee * 1.15)
        else:
            return round(tdee)

    def save(self, *args, **kwargs):
        self.daily_calorie_goal = self.calculate_goal_calories()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} profili"

    class Meta:
        verbose_name = "Foydalanuvchi profili"
        verbose_name_plural = "Foydalanuvchi profillari"


class Food(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Nonushta'),
        ('lunch', 'Tushlik'),
        ('dinner', 'Kechki ovqat'),
        ('snack', 'Gazak'),
        ('any', 'Istalgan vaqt'),
    ]
    REGION_CHOICES = [
        ('toshkent', 'Toshkent'),
        ('samarqand', 'Samarqand'),
        ('buxoro', 'Buxoro'),
        ('fargona', 'Farg\'ona'),
        ('xorazm', 'Xorazm'),
        ('umumiy', 'Umumiy O\'zbek'),
    ]

    name = models.CharField(max_length=200, verbose_name="Taom nomi")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='any', verbose_name="Taom turi")
    calories_per_100g = models.FloatField(verbose_name="Kaloriya (100g uchun)")
    protein_per_100g = models.FloatField(default=0, verbose_name="Oqsil (g/100g)")
    fat_per_100g = models.FloatField(default=0, verbose_name="Yog' (g/100g)")
    carbs_per_100g = models.FloatField(default=0, verbose_name="Uglevod (g/100g)")
    default_portion_g = models.IntegerField(default=200, verbose_name="Standart porsiya (g)")
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='umumiy', verbose_name="Mintaqa")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    recipe_url = models.URLField(blank=True, verbose_name="Retsept havolasi")
    image = models.ImageField(upload_to='foods/', blank=True, null=True, verbose_name="Rasm")
    is_active = models.BooleanField(default=True)

    def calories_per_portion(self):
        return round(self.calories_per_100g * self.default_portion_g / 100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taom"
        verbose_name_plural = "Taomlar"
        ordering = ['name']


class FoodLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_likes')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'food')
        verbose_name = "Taom like"


class DiaryEntry(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Nonushta'),
        ('lunch', 'Tushlik'),
        ('dinner', 'Kechki ovqat'),
        ('snack', 'Gazak'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='diary_entries')
    date = models.DateField(default=timezone.now, verbose_name="Sana")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, verbose_name="Ovqat vaqti")
    amount_g = models.FloatField(verbose_name="Miqdor (g)")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_calories(self):
        return round(self.food.calories_per_100g * self.amount_g / 100, 1)

    def get_protein(self):
        return round(self.food.protein_per_100g * self.amount_g / 100, 1)

    def get_fat(self):
        return round(self.food.fat_per_100g * self.amount_g / 100, 1)

    def get_carbs(self):
        return round(self.food.carbs_per_100g * self.amount_g / 100, 1)

    def __str__(self):
        return f"{self.user.username} - {self.food.name} - {self.date}"

    class Meta:
        verbose_name = "Ovqat jurnali"
        verbose_name_plural = "Ovqat jurnallari"
        ordering = ['-date', 'meal_type']


class WeightRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_records')
    weight = models.FloatField(verbose_name="Vazn (kg)")
    date = models.DateField(default=timezone.now, verbose_name="Sana")
    notes = models.TextField(blank=True, verbose_name="Eslatma")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.weight}kg - {self.date}"

    class Meta:
        verbose_name = "Vazn yozuvi"
        verbose_name_plural = "Vazn yozuvlari"
        ordering = ['-date']
        unique_together = ('user', 'date')


class WaterIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_intakes')
    date = models.DateField(default=timezone.now, verbose_name="Sana")
    glasses = models.PositiveIntegerField(default=0, verbose_name="Stakan soni")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.glasses} stakan - {self.date}"

    class Meta:
        verbose_name = "Suv iste'moli"
        verbose_name_plural = "Suv iste'mollari"
        unique_together = ('user', 'date')


class PhysicalActivity(models.Model):
    ACTIVITY_TYPES = [
        ('walking', 'Yurish'),
        ('running', 'Yugurish'),
        ('cycling', 'Velosiped'),
        ('swimming', 'Suzish'),
        ('gym', 'Sport zali'),
        ('football', 'Futbol'),
        ('basketball', 'Basketbol'),
        ('yoga', 'Yoga'),
        ('other', 'Boshqa'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name="Faoliyat turi")
    duration_minutes = models.PositiveIntegerField(verbose_name="Davomiyligi (daqiqa)")
    calories_burned = models.IntegerField(verbose_name="Yoqilgan kaloriya")
    date = models.DateField(default=timezone.now, verbose_name="Sana")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.date}"

    class Meta:
        verbose_name = "Jismoniy faollik"
        verbose_name_plural = "Jismoniy faolliklar"
        ordering = ['-date']
