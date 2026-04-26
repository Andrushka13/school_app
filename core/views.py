from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# Create your views here.
def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        # усли авторизован, перенапрвляем на главную
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('passwod')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Неверный логин или пароль")
        else:
            messages.error(request, "Ошибка ввода")
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, "Вы вышли из системы")
    return redirect('login')


@login_required(login_url='login')
def home_view(request):
    """
    Гдавная страница после входа.
    Тут будет разветвление по ролям пользователя.
    """
    context = {
        'user': request.user,
        'is_student': request.user.groups.filter(name='Sudents').exists(),
        'is_teacher': request.user.groups.filter(name='Teachers').exists(),
        'is_admin': request.user.groups.filter(name='Admins').exists(),
    }
    return render(request, 'core/home.html', context)
