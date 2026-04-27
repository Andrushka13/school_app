from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .managers import ActiveTeacherManager, ActiveStudentManager
from .validators import validate_phone
from .utils import check_teacher_workload, get_available_groups_for_direction
from django.contrib.auth.models import User

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
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_profile',
        verbose_name="Пользователь (аутентификация)"
    )
    
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
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile',
        verbose_name="Пользователь (аутентификация)"
    )
        
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


class Subject(models.Model):
    """Предмет"""
    
    name = models.CharField(max_length=200, unique=True, verbose_name="Название предмета")
    hours = models.PositiveSmallIntegerField(verbose_name="Количество часов")
    description = models.TextField(blank=True, verbose_name="Описание")
    control_form = models.ForeignKey(ControlForm, on_delete=models.PROTECT, related_name="subject", verbose_name="Форма контроля")
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name="subjects", verbose_name="Направление")
    
    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
    
    def __str__(self):
        return self.name
    

class StudyPlan(models.Model):
    """Учебный план (связь группы, предмета и преподавателя)"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="study_plans", verbose_name="Группа")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="study_plans", verbose_name="Предмет")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="study_plans", verbose_name="Преподаватель")
    
    class Meta:
        unique_together = [['group', 'subject']]
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"
        
    def __str__(self):
        return f"{self.group} - {self.subject}"


class Schedule(models.Model):
    """Расписание занятий (с поддержкой истории изменений)"""
    FORMAT_CHOICES = [
        ('offline', 'Очно'),
        ('online', 'Дистанционно'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="Shedules", verbose_name="Группа")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="Shedules", verbose_name="Предмет")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="Shedules", verbose_name="Преподаватель")
    date = models.DateField(verbose_name="Дата проведения")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='offline', verbose_name="Формат")
    classroom = models.CharField(max_length=50, blank=True, null=True, verbose_name="Аудитория") # для очников
    video_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на видеоконференцию") # для дистанта
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="next_versions", verbose_name="Предыдущая версия")
    change_reason = models.TextField(blank=True, verbose_name="Причина изменения")
    
    class Meta:
        verbose_name = "Занятие в расписании"
        verbose_name_plural = "Расписание"
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['date', 'group']),
            models.Index(fields=['teacher', 'date']),
        ]
    
    def __str__(self):
        return f"{self.date} {self.start_time}: {self.group} - {self.subject}"
    
    def clean(self):
        """Валидация: время, формат, нагрузка преподавателя"""
        if self.start_time >= self.end_time:
            raise ValidationError("Время окончания должно быть позже времени начала")
        if self.format == 'offline' and not self.classroom:
            raise ValidationError("Для очного занятия укажите аудиторию")
        if self.format == 'online' and not self.video_link:
            raise ValidationError("Для проведения занятия укажите ссылку на видеоконференцию")
        # Проверка нагрузки преподавателя за неделю
        if not check_teacher_workload(self.teacher, self.date, self.start_time, self.end_time, exclude_shedule_id=self.id):
            raise ValidationError(f"Превышена максимальная недельная нагрузка преподавателя ({self.teacher.max_weekly_hours} часов)")


class Attendance(models.Model):
    """Посещаемость занятия"""
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, related_name='attendances', verbose_name="Занятие")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name="Ученик")
    is_present = models.BooleanField(default=True, verbose_name="Присутствовал")
    comment = models.TextField(blank=True, verbose_name="Примечание")
    
    class Meta:
        unique_together = [['schedule', 'student']]
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"
    
    def __str__(self):
        return f"{self.student} - {self.schedule} - {'Присутствовал' if self.is_present else 'Отсутствовал'}"
    
    
class Grade(models.Model):
    """Оценка успеваемости"""
    CONROL_TYPES = [
        ('current', 'Текущий'),
        ('intermediate', 'Промежуточные'),
        ('final', 'Итоговые'),
    ]
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='grades', verbose_name="Ученик")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades', verbose_name="Предмет")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='grades', verbose_name="Группа")
    control_type = models.CharField(max_length=12, choices=CONROL_TYPES, default='current', verbose_name="Тип контроля")
    date = models.DateField(auto_now_add=True, verbose_name="Дата выставления")
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Балл 1 - 5")
    comment = models.TextField(blank=True, verbose_name="Комментарий преподавателя")
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades', verbose_name="Связанное занятие")
    
    class Meta:
        # УникльностьЖ ученик + предмет + тип контроля. Только для итоговой оценки,
        # для простоты оставим для всех. Можно доработать через проверку в save.
        unique_together = [['student', 'subject', 'control_type']]
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
    
    def __str__(self):
        student_name = self.student.last_name if self.student else "Удалён"
        return f"{student_name} - {self.subject.name}: {self.score}"


class EnrollmentRequest(models.Model):
    """Заявка на поступление"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    phone = models.CharField(max_length=20, unique=True, validators=[validate_phone], verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='requests', verbose_name="Желаемое направление")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    suggested_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollment_request', verbose_name="Предложенная группа")
    
        
    class Meta:
        verbose_name = "Заявка на поступление"
        verbose_name_plural = "Заявки на поступление"
    
    def save(self, *args, **kwargs):
        """Автоматический подбор подходящей группы при создании заявки"""
        if not self.suggested_group and self.direction:
            available = get_available_groups_for_direction(self.direction)
            if available:
                self.suggested_group = available[0]
        super().save(*args, **kwargs)


class Contract(models.Model):
    """Договор с учеником"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='contract', verbose_name="Ученик")
    conclusion_date = models.DateField(auto_now_add=True, verbose_name="Дата заключения")
    contract_number = models.CharField(max_length=50, unique=True, verbose_name="Номер договора")
    file_link = models.URLField(blank=True, verbose_name="Ссылка на файл договора")
    
    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
    
    def __str__(self):
        return f"Договор №{self.contract_number} - {self.student}"
