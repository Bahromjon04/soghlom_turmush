from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from datetime import date, timedelta

from .models import UserProfile, Food, DiaryEntry, WeightRecord, WaterIntake, PhysicalActivity, FoodLike
from .forms import (RegisterForm, LoginForm, ProfileForm, DiaryEntryForm,
                    WeightRecordForm, WaterIntakeForm, PhysicalActivityForm, FoodFilterForm)


def get_or_create_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


# ==================== AUTH VIEWS ====================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        user = User.objects.create_user(
            username=cd['email'],
            email=cd['email'],
            password=cd['password1'],
            first_name=cd['first_name'],
            last_name=cd['last_name'],
        )
        profile = UserProfile.objects.create(
            user=user,
            age=cd['age'],
            height=cd['height'],
            weight=cd['weight'],
            gender=cd['gender'],
            activity_level=cd['activity_level'],
            goal=cd['goal'],
        )
        login(request, user)
        messages.success(request, f"Xush kelibsiz, {user.first_name}! Profil muvaffaqiyatli yaratildi.")
        return redirect('home')
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, "Email yoki parol noto'g'ri.")
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ==================== HOME VIEW ====================

@login_required
def home_view(request):
    profile = get_or_create_profile(request.user)
    today = timezone.now().date()

    # Today's diary
    today_entries = DiaryEntry.objects.filter(user=request.user, date=today).select_related('food')

    # Calculate today totals
    total_calories = sum(e.get_calories() for e in today_entries)
    total_protein = sum(e.get_protein() for e in today_entries)
    total_fat = sum(e.get_fat() for e in today_entries)
    total_carbs = sum(e.get_carbs() for e in today_entries)

    # Today's activities
    today_activities = PhysicalActivity.objects.filter(user=request.user, date=today)
    burned_calories = today_activities.aggregate(total=Sum('calories_burned'))['total'] or 0

    # Net calories
    net_calories = total_calories - burned_calories
    remaining_calories = profile.daily_calorie_goal - net_calories

    # Water
    water_obj, _ = WaterIntake.objects.get_or_create(user=request.user, date=today)

    # Calorie progress percentage
    cal_percent = min(100, round(net_calories / profile.daily_calorie_goal * 100)) if profile.daily_calorie_goal > 0 else 0

    # Group by meal type
    meals = {}
    for meal_type, label in DiaryEntry.MEAL_TYPE_CHOICES:
        entries = [e for e in today_entries if e.meal_type == meal_type]
        meal_cals = sum(e.get_calories() for e in entries)
        meals[meal_type] = {'label': label, 'entries': entries, 'calories': meal_cals}

    # Recommendations
    liked_food_ids = FoodLike.objects.filter(user=request.user).values_list('food_id', flat=True)
    eaten_food_ids = [e.food_id for e in today_entries]

    recommendations = []
    if remaining_calories > 100:
        # Find foods fitting remaining calories
        suitable = Food.objects.filter(is_active=True).exclude(id__in=eaten_food_ids)
        if liked_food_ids:
            liked = suitable.filter(id__in=liked_food_ids)[:3]
            recommendations = list(liked)
        if len(recommendations) < 3:
            others = suitable.exclude(id__in=[f.id for f in recommendations])[:3 - len(recommendations)]
            recommendations += list(others)

    # Last weight
    last_weight = WeightRecord.objects.filter(user=request.user).first()

    context = {
        'profile': profile,
        'today': today,
        'today_entries': today_entries,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs,
        'burned_calories': burned_calories,
        'net_calories': net_calories,
        'remaining_calories': remaining_calories,
        'cal_percent': cal_percent,
        'meals': meals,
        'water_obj': water_obj,
        'recommendations': recommendations,
        'last_weight': last_weight,
        'today_activities': today_activities,
    }
    return render(request, 'core/home.html', context)


# ==================== DIARY VIEWS ====================

@login_required
def diary_view(request, diary_date=None):
    profile = get_or_create_profile(request.user)
    if diary_date:
        try:
            selected_date = date.fromisoformat(str(diary_date))
        except:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    entries = DiaryEntry.objects.filter(user=request.user, date=selected_date).select_related('food')
    total_calories = sum(e.get_calories() for e in entries)
    total_protein = sum(e.get_protein() for e in entries)
    total_fat = sum(e.get_fat() for e in entries)
    total_carbs = sum(e.get_carbs() for e in entries)

    activities = PhysicalActivity.objects.filter(user=request.user, date=selected_date)
    burned = activities.aggregate(total=Sum('calories_burned'))['total'] or 0

    net_calories = total_calories - burned
    remaining = profile.daily_calorie_goal - net_calories
    cal_percent = min(100, round(net_calories / profile.daily_calorie_goal * 100)) if profile.daily_calorie_goal > 0 else 0

    meals = {}
    for meal_type, label in DiaryEntry.MEAL_TYPE_CHOICES:
        meal_entries = [e for e in entries if e.meal_type == meal_type]
        meal_cals = sum(e.get_calories() for e in meal_entries)
        meals[meal_type] = {'label': label, 'entries': meal_entries, 'calories': meal_cals}

    water_obj, _ = WaterIntake.objects.get_or_create(user=request.user, date=selected_date)

    form = DiaryEntryForm(initial={'date': selected_date})

    # Week navigation
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    today = timezone.now().date()

    # Week dates for mini calendar
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    context = {
        'profile': profile,
        'selected_date': selected_date,
        'entries': entries,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs,
        'burned_calories': burned,
        'net_calories': net_calories,
        'remaining_calories': remaining,
        'cal_percent': cal_percent,
        'meals': meals,
        'water_obj': water_obj,
        'form': form,
        'prev_date': prev_date,
        'next_date': next_date,
        'today': today,
        'week_dates': week_dates,
        'activities': activities,
    }
    return render(request, 'core/diary.html', context)


@login_required
def add_diary_entry(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, f"{entry.food.name} jurnalga qo'shildi.")
            return redirect('diary_date', diary_date=entry.date)
        else:
            messages.error(request, "Ma'lumotlarni to'g'ri kiriting.")
    return redirect('diary')


@login_required
def delete_diary_entry(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    entry_date = entry.date
    entry.delete()
    messages.success(request, "Yozuv o'chirildi.")
    return redirect('diary_date', diary_date=entry_date)


# ==================== FOOD VIEWS ====================

@login_required
def food_list_view(request):
    form = FoodFilterForm(request.GET or None)
    foods = Food.objects.filter(is_active=True)
    liked_ids = set(FoodLike.objects.filter(user=request.user).values_list('food_id', flat=True))

    if form.is_valid():
        cd = form.cleaned_data
        if cd.get('search'):
            foods = foods.filter(name__icontains=cd['search'])
        if cd.get('meal_type'):
            foods = foods.filter(Q(meal_type=cd['meal_type']) | Q(meal_type='any'))
        if cd.get('cal_min') is not None:
            foods = foods.filter(calories_per_100g__gte=cd['cal_min'])
        if cd.get('cal_max') is not None:
            foods = foods.filter(calories_per_100g__lte=cd['cal_max'])
        if cd.get('region'):
            foods = foods.filter(region=cd['region'])

    context = {'foods': foods, 'form': form, 'liked_ids': liked_ids}
    return render(request, 'core/food_list.html', context)


@login_required
def food_detail_view(request, pk):
    food = get_object_or_404(Food, pk=pk, is_active=True)
    liked = FoodLike.objects.filter(user=request.user, food=food).exists()
    liked_count = food.likes.count()
    context = {'food': food, 'liked': liked, 'liked_count': liked_count}
    return render(request, 'core/food_detail.html', context)


@login_required
@require_POST
def toggle_like(request, pk):
    food = get_object_or_404(Food, pk=pk)
    like, created = FoodLike.objects.get_or_create(user=request.user, food=food)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': food.likes.count()})


# ==================== WEIGHT VIEWS ====================

@login_required
def progress_view(request):
    profile = get_or_create_profile(request.user)
    weight_records = WeightRecord.objects.filter(user=request.user).order_by('date')

    # Chart data
    chart_labels = [str(w.date) for w in weight_records]
    chart_data = [w.weight for w in weight_records]

    # Current weight change
    weight_change = None
    if weight_records.count() >= 2:
        first = weight_records.first().weight
        last = weight_records.last().weight
        weight_change = round(last - first, 1)

    # Weekly calorie summary (last 7 days)
    today = timezone.now().date()
    week_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        entries = DiaryEntry.objects.filter(user=request.user, date=day)
        cals = sum(e.get_calories() for e in entries)
        week_data.append({'date': day.strftime('%d-%b'), 'calories': cals})

    week_labels = [d['date'] for d in week_data]
    week_cals = [d['calories'] for d in week_data]

    # BMR/TDEE info
    bmr = round(profile.calculate_bmr())
    tdee = round(profile.calculate_tdee())

    # Add weight record form
    wform = WeightRecordForm(initial={'date': today})
    if request.method == 'POST' and 'add_weight' in request.POST:
        wform = WeightRecordForm(request.POST)
        if wform.is_valid():
            rec = wform.save(commit=False)
            rec.user = request.user
            try:
                rec.save()
                messages.success(request, "Vazn yozildi!")
            except:
                WeightRecord.objects.filter(user=request.user, date=rec.date).update(weight=rec.weight, notes=rec.notes)
                messages.success(request, "Vazn yangilandi!")
            return redirect('progress')

    context = {
        'profile': profile,
        'weight_records': weight_records,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'weight_change': weight_change,
        'week_labels': json.dumps(week_labels),
        'week_cals': json.dumps(week_cals),
        'bmr': bmr,
        'tdee': tdee,
        'wform': wform,
    }
    return render(request, 'core/progress.html', context)


# ==================== RECOMMENDATIONS ====================

@login_required
def recommendations_view(request):
    profile = get_or_create_profile(request.user)
    today = timezone.now().date()

    today_entries = DiaryEntry.objects.filter(user=request.user, date=today)
    total_today_cals = sum(e.get_calories() for e in today_entries)
    remaining = profile.daily_calorie_goal - total_today_cals

    liked_ids = set(FoodLike.objects.filter(user=request.user).values_list('food_id', flat=True))
    eaten_ids = set(e.food_id for e in today_entries)

    # Liked but not eaten today
    liked_foods = Food.objects.filter(id__in=liked_ids, is_active=True).exclude(id__in=eaten_ids)

    # Meal-specific recommendations
    eaten_meal_types = set(e.meal_type for e in today_entries)
    missing_meals = [m for m, _ in DiaryEntry.MEAL_TYPE_CHOICES if m not in eaten_meal_types]

    meal_recommendations = {}
    for meal_type in missing_meals:
        foods = Food.objects.filter(is_active=True).filter(
            Q(meal_type=meal_type) | Q(meal_type='any')
        ).exclude(id__in=eaten_ids).order_by('?')[:3]
        if foods:
            meal_recommendations[meal_type] = {
                'label': dict(DiaryEntry.MEAL_TYPE_CHOICES)[meal_type],
                'foods': foods,
            }

    # Daily menu suggestion
    daily_menu = {}
    for meal_type, label in DiaryEntry.MEAL_TYPE_CHOICES:
        food = Food.objects.filter(
            Q(meal_type=meal_type) | Q(meal_type='any'),
            is_active=True
        ).order_by('?').first()
        if food:
            daily_menu[meal_type] = {'label': label, 'food': food}

    # Variety suggestion (foods not eaten this week)
    week_ago = today - timedelta(days=7)
    this_week_food_ids = set(DiaryEntry.objects.filter(
        user=request.user, date__gte=week_ago
    ).values_list('food_id', flat=True))
    variety_foods = Food.objects.filter(is_active=True).exclude(id__in=this_week_food_ids).order_by('?')[:6]

    context = {
        'profile': profile,
        'remaining_calories': remaining,
        'total_today_cals': total_today_cals,
        'liked_foods': liked_foods,
        'meal_recommendations': meal_recommendations,
        'daily_menu': daily_menu,
        'variety_foods': variety_foods,
        'liked_ids': liked_ids,
    }
    return render(request, 'core/recommendations.html', context)


# ==================== PROFILE VIEWS ====================

@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    form = ProfileForm(instance=profile, initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    })

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        if form.is_valid():
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            form.save()
            messages.success(request, "Profil yangilandi!")
            return redirect('profile')

    bmr = round(profile.calculate_bmr())
    tdee = round(profile.calculate_tdee())

    context = {'profile': profile, 'form': form, 'bmr': bmr, 'tdee': tdee}
    return render(request, 'core/profile.html', context)


# ==================== WATER & ACTIVITY ====================

@login_required
@require_POST
def update_water(request):
    today = timezone.now().date()
    action = request.POST.get('action', 'add')
    water_obj, _ = WaterIntake.objects.get_or_create(user=request.user, date=today)
    if action == 'add':
        water_obj.glasses = min(20, water_obj.glasses + 1)
    elif action == 'remove' and water_obj.glasses > 0:
        water_obj.glasses -= 1
    water_obj.save()
    return JsonResponse({'glasses': water_obj.glasses})


@login_required
def activity_view(request):
    profile = get_or_create_profile(request.user)
    today = timezone.now().date()
    activities = PhysicalActivity.objects.filter(user=request.user).order_by('-date')[:20]
    form = PhysicalActivityForm(initial={'date': today})

    if request.method == 'POST':
        form = PhysicalActivityForm(request.POST)
        if form.is_valid():
            act = form.save(commit=False)
            act.user = request.user
            act.save()
            messages.success(request, "Faollik qo'shildi!")
            return redirect('activity')

    # Calorie burn estimates per minute
    calorie_rates = {
        'walking': 4, 'running': 10, 'cycling': 8, 'swimming': 9,
        'gym': 7, 'football': 8, 'basketball': 8, 'yoga': 3, 'other': 5
    }

    context = {'activities': activities, 'form': form, 'calorie_rates': json.dumps(calorie_rates)}
    return render(request, 'core/activity.html', context)


@login_required
def delete_activity(request, pk):
    act = get_object_or_404(PhysicalActivity, pk=pk, user=request.user)
    act.delete()
    messages.success(request, "Faollik o'chirildi.")
    return redirect('activity')
