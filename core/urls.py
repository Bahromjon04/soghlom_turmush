from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Diary
    path('kundalik/', views.diary_view, name='diary'),
    path('kundalik/<str:diary_date>/', views.diary_view, name='diary_date'),
    path('kundalik/add/', views.add_diary_entry, name='add_diary_entry'),
    path('kundalik/delete/<int:pk>/', views.delete_diary_entry, name='delete_diary_entry'),

    # Foods
    path('taomlar/', views.food_list_view, name='food_list'),
    path('taomlar/<int:pk>/', views.food_detail_view, name='food_detail'),
    path('taomlar/<int:pk>/like/', views.toggle_like, name='toggle_like'),

    # Progress
    path('taraqqiyot/', views.progress_view, name='progress'),

    # Recommendations
    path('tavsiyalar/', views.recommendations_view, name='recommendations'),

    # Profile
    path('profil/', views.profile_view, name='profile'),

    # Water & Activity
    path('suv-yangilash/', views.update_water, name='update_water'),
    path('faollik/', views.activity_view, name='activity'),
    path('faollik/delete/<int:pk>/', views.delete_activity, name='delete_activity'),
]
