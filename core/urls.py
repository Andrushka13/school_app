from django.urls import path
from . import views



app_name = 'core'

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Студенческие страницы
    path('student/account', views.student_account, name='student_account'),
    path('student/schedule', views.student_schedule, name='student_schedule'),
    path('student/grades', views.student_grades, name='student_grades'),
]
