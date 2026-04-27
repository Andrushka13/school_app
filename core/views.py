from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import LoginForm
from .models import Student, Schedule, Grade

# Create your views here.
class CustomLoginView(LoginView):
    """Представление входа с кастомной формой и шаблоном"""
    authentication_form = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True  # если залогинен и дёт на дашборд
    
    def get_success_url(self):
        """после входа перенапраляем на дашборд, где будет определена роль"""
        return reverse_lazy('core:dashboard')
    

def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('core:login')

@login_required
def dashboard(request):
    """Определяем роль пользователя и рендерим соответствующий шаблон"""
    user = request.user
    # Заглушка
    
    if hasattr(user, 'student_profile') and user.student_profile:
        return redirect('core:student_account')
    elif hasattr(user, 'teacher_profile') and user.teacher_profile:
        return render(request, 'dashboard_teacher.html', {'username': user.get_full_name()})
    elif user.is_staff or user.is_superuser:
        return render(request, 'dashboard_admin.html', {'username': user.get_full_name()})
    else:
        return render(request, 'dashboard_unknown.html', {'username': user.get_full_name()})


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return redirect('core:login')


@login_required
def student_account(request):
    """Страница профиля студента"""
    student = get_object_or_404(Student, user=request.user)
    context = {
        'student': student,
        'full_name': f"{student.last_name} {student.first_name} {student.patronymic or ''}".strip(),
    }
    return render(request, 'student_account.html', context)


@login_required
def student_schedule(request):
    """Расписание группы студента на текущую неделю"""
    student = get_object_or_404(Student, user=request.user)
    group = student.group
    if not group:
        # если студент без группы
        return render(request, 'student_schedule.html', {'error': 'Вы не прикреплены ни к одной группе'})
    
    # Определяем начало недели
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4) # Пятнца
    
    schedules = Schedule.objects.filter(
        group=group,
        date__gte=start_of_week,
        date__lte=end_of_week
    ).order_by('date', 'start_time')
    
    # Сортируем по дням
    week_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    schedule_by_day = {day: [] for day in week_days}
    for s in schedules:
        day_index = s.date.weekday() # 0=пн, 4=пт
        if day_index < 5:
            schedule_by_day[week_days[day_index]].append(s)

    context = {
        'schedule_by_day': schedule_by_day,
        'week_days': week_days,
        'start_of_week': start_of_week
    }
    return render(request, 'student_schedule.html', context)


@login_required
def student_grades(request):
    """Оценки студента по направлениям группы"""
    student = get_object_or_404(Student, user=request.user)
    group = student.group
    if not group:
        # если студент без группы
        return render(request, 'student_schedule.html', {'error': 'Вы не прикреплены ни к одной группе'})
    
    # Получаем все оценки студента
    grades = Grade.objects.filter(student=student, group=group).select_related('subject')
    # Сгруппируем по предметам
    grades_by_subjects = {}
    for g in grades:
        subject_name = g.subject.name
        if subject_name not in grades_by_subjects:
            grades_by_subjects[subject_name] = []
        grades_by_subjects[subject_name].append(g)
    
    context = {
        'grades_by_subjects': grades_by_subjects,
        'group': group
    }
    return render(request, 'student_grades.html', context)
        
