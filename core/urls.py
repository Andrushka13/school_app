from django.urls import path
from . import views



app_name = 'core'

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
