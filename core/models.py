from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .managers import ActiveTeacherManager, ActiveStudentManager
from .validators import validate_phone
from .utils import check_teacher_workload, get_available_groups_for_direction

# Create your models here.
#---------Справочник------------
class Position(models.Model):
    """Должность преподавателя (справочник)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название должности")
    
    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
    
    def __str__(self):
        return self.name


class ControlForm(models.Model):
    """Форма итогового контроля (зачёт/экзамен)"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    
    class Meta:
        verbose_name = "форма контроля"
        verbose_name_plural = "Формы конроля"
    
    def __str__(self):
        return self.name


#----------------Основные сущности--------------------
class Direction(models.Model):
    """Направление обучения"""
    STATUS_CHOICES = [
        ('open', 'Открыто'),
        ('closed', 'Закрыто'),
    ]
    name = models.CharField(max_length=200, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open", verbose_name="Статус")
    
    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
    
    def __str__(self):
        return self.name


class Teacher(models.Model):
    """Преподаватель"""
    STATUS_CHOICES = [
        ('active', 'Работает'),
        ('fired', 'Уволен'),
    ]
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    phone = models.CharField(max_length=20, unique=True, validators=[validate_phone], verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Email")
    specialization = models.CharField(max_length=200, verbose_name="Специализация")
    max_weekly_hours = models.PositiveSmallIntegerField(default=40, verbose_name="Макс. нагрузка (часов в нежедю)")
    hire_date = models.DateField(default=timezone.now, verbose_name="Дата приёма на работу")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active", verbose_name="Статус")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name="teachers", verbose_name="Должность")
    
    # Менеджеры
    objects = models.Manager()
    active = ActiveTeacherManager()
    
    class Meta:
        verbose_name = "Преподаватели"
        verbose_name_plural = "Преподаватели"
        ordering = [
            'last_name', 'first_name'
        ]
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    
class Student(models.Model):
    """Ученик"""
    STATUS_CHOICES = [
        ('studying', 'Обучается'),
        ('expelled', 'Отчислен'),
        ('graduated', 'Выпущен'),
    ]
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    phone = models.CharField(max_length=20, unique=True, validators=[validate_phone], verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Email")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="studying", verbose_name="Статус обучения")
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name="students", verbose_name="Группа")
        
    # Менеджеры
    objects = models.Manager()
    active = ActiveStudentManager()
        
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
            
        
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
        
    def delete(self, using = None, keep_parents = False):
        """
        Переопределяем метод delete, чтобы вместо физического удаления обезличивать данные
        """
        self.last_name = f"Deleted_{self.id}"
        self.first_name = "Anonymous"
        self.patronymic = ""
        self.phone = f"0{self.id}"
        self.email = f"deleted_{self.id}#example.com"
        self.status = "expelled"
        self.save()
        # Не вызываем super().delete(), чтобы не удалить запись из БД


class Group(models.Model):
    """Группа обучения"""
    FORM_CHOICES = [
        ('fulltime', 'Очная'),
        ('distance', 'Дистанционная'),
    ]
    STATUS_CHOICES = [
        ('forming', 'Формируется'),
        ('studying', 'Обучается'),
        ('graduated', 'Выпущена'),
    ]
    name = models.CharField(max_length=100, unique=True, verbose_name="Название группы")
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name="groups", verbose_name="Направление")
    study_form = models.CharField(max_length=10, choices=FORM_CHOICES, default="fulltime", verbose_name="Форма обучения")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="forming", verbose_name="Статус")
    
    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
    
    def __str__(self):
        return self.name
    
    def get_max_students(self):
        return 12 if self.study_form == "fulltime" else 15
    
    def clean(self):
        """Валидация на уровне модели"""
        if self.start_date >= self.end_date:
            raise ValidationError("Дата окончания обучения должна быть позже даты начала")
        if self.status == "studying" and self.students.count() > self.get_max_students():
            raise ValidationError(f"В группе не может быть больше {self.get_max_students()} учеников")


    
