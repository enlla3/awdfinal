# accounts/urls.py
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('search/', views.search_users, name='search_users'),  # New search view
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
]
