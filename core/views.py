from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import LoginForm

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
    role = 'unknown'
    template = 'dashboard_unknown.html'  # Заглушка
    
    if hasattr(user, 'student_profile') and user.student_profile:
        role = 'student'
        template = 'dashboard_student.html'
    elif hasattr(user, 'teacher_profile') and user.teacher_profile:
        role = 'teacher'
        template = 'dashboard_teacher.html'
    elif user.is_staff or user.is_superuser:
        role = 'admin'
        template = 'dashboard_admin.html'
    
    context = {
        'role': role,
        'username': user.get_full_name() or user.username
    }
    
    return render(request, template, context)


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return redirect('core:login')
