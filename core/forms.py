from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, DiaryEntry, WeightRecord, WaterIntake, PhysicalActivity, Food


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="Ism", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ismingiz'}))
    last_name = forms.CharField(max_length=50, label="Familiya", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Familiyangiz'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))
    password1 = forms.CharField(label="Parol", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'}))
    password2 = forms.CharField(label="Parolni tasdiqlash", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parolni takrorlang'}))
    age = forms.IntegerField(label="Yosh", min_value=10, max_value=100, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    height = forms.FloatField(label="Bo'y (sm)", min_value=100, max_value=250, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
    weight = forms.FloatField(label="Vazn (kg)", min_value=30, max_value=300, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
    gender = forms.ChoiceField(label="Jins", choices=UserProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    activity_level = forms.ChoiceField(label="Faollik darajasi", choices=UserProfile.ACTIVITY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    goal = forms.ChoiceField(label="Maqsad", choices=UserProfile.GOAL_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Parollar mos kelmadi.")
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label="Parol", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'}))


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, label="Ism", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, label="Familiya", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['age', 'height', 'weight', 'gender', 'activity_level', 'goal', 'target_weight', 'phone', 'daily_water_goal']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'activity_level': forms.Select(attrs={'class': 'form-select'}),
            'goal': forms.Select(attrs={'class': 'form-select'}),
            'target_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'daily_water_goal': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'age': 'Yosh',
            'height': "Bo'y (sm)",
            'weight': 'Vazn (kg)',
            'gender': 'Jins',
            'activity_level': 'Faollik darajasi',
            'goal': 'Maqsad',
            'target_weight': 'Maqsad vazn (kg)',
            'phone': 'Telefon',
            'daily_water_goal': 'Kunlik suv maqsadi (stakan)',
        }


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ['food', 'date', 'meal_type', 'amount_g']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'amount_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '1'}),
        }
        labels = {
            'food': 'Taom',
            'date': 'Sana',
            'meal_type': 'Ovqat vaqti',
            'amount_g': 'Miqdor (g)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['food'].queryset = Food.objects.filter(is_active=True).order_by('name')


class WeightRecordForm(forms.ModelForm):
    class Meta:
        model = WeightRecord
        fields = ['weight', 'date', 'notes']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'weight': 'Vazn (kg)',
            'date': 'Sana',
            'notes': 'Eslatma',
        }


class WaterIntakeForm(forms.ModelForm):
    class Meta:
        model = WaterIntake
        fields = ['glasses']
        widgets = {
            'glasses': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '20'}),
        }
        labels = {'glasses': 'Stakan soni'}


class PhysicalActivityForm(forms.ModelForm):
    class Meta:
        model = PhysicalActivity
        fields = ['activity_type', 'duration_minutes', 'calories_burned', 'date', 'notes']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'calories_burned': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'activity_type': 'Faoliyat turi',
            'duration_minutes': 'Davomiyligi (daqiqa)',
            'calories_burned': 'Yoqilgan kaloriya',
            'date': 'Sana',
            'notes': 'Eslatma',
        }


class FoodFilterForm(forms.Form):
    search = forms.CharField(required=False, label="Qidirish", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Taom nomini kiriting...'}))
    meal_type = forms.ChoiceField(
        required=False,
        label="Taom turi",
        choices=[('', 'Barchasi')] + Food.MEAL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cal_min = forms.IntegerField(required=False, label="Min kaloriya", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    cal_max = forms.IntegerField(required=False, label="Max kaloriya", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1000'}))
    region = forms.ChoiceField(
        required=False,
        label="Mintaqa",
        choices=[('', 'Barchasi')] + Food.REGION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
