from django.contrib import admin
from .models import UserProfile, Food, DiaryEntry, WeightRecord, WaterIntake, PhysicalActivity, FoodLike


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'height', 'weight', 'gender', 'goal', 'daily_calorie_goal')
    list_filter = ('gender', 'goal', 'activity_level')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal_type', 'calories_per_100g', 'protein_per_100g', 'fat_per_100g', 'carbs_per_100g', 'region', 'is_active')
    list_filter = ('meal_type', 'region', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'date', 'meal_type', 'amount_g')
    list_filter = ('meal_type', 'date')
    search_fields = ('user__email', 'food__name')
    date_hierarchy = 'date'


@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'date')
    list_filter = ('date',)
    search_fields = ('user__email',)


@admin.register(WaterIntake)
class WaterIntakeAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'glasses')


@admin.register(PhysicalActivity)
class PhysicalActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'duration_minutes', 'calories_burned', 'date')
    list_filter = ('activity_type', 'date')


@admin.register(FoodLike)
class FoodLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'created_at')
