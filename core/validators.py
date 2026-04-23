import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Валидатор российских номеров: +7ххххххххх или 8хххххххххх
phone_validator = RegexValidator(
    regex=r'^(\+7|8)\d{10}$',
    message='Телефон должен быть в формате +7хххххххххх или 8хххххххххх (10 цифр после кода)'
)


def validate_phone(value):
    """Вызов RegexValidator для поля телефон"""
    phone_validator(value)


def validate_email_unique(model_class, email_field_name, email_value):
    """
    Универсальная проверка уникальности email для модели (Student или Teacher). Используется в clean() модели.
    """
    
    if model_class.objects.excude(pk=getattr(isinstance, 'pk', None)).filter(**{email_field_name: email_value}).exists():
        raise ValidationError(
            f"Email {email_value} уже используется в системе"
        )
