from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Grade, Schedule, Student


@receiver(post_save, sender=Grade)
def notify_unsatisfactory_grade(sender, instance, created, **kwargs):
    """
    при создании оценки 1 или 2 отправляем уведомление администратору и методисту
    """
    if created and instance.score <= 2:
        subject = f"Неудовлетворительная оценка у {instance.student}"
        message = f"Ученик {instance.student.last_name} {instance.student.first_name} получил {instance.score} по предмету {instance.subject.name}"
        send_mail(
            subject=subject,
            message=message,
            from_email='no-reply@unikron.ru',
            recipient_list=['admin@unikron.ru', 'methodist@unikron.ru'],
            fail_silently=True,
        )
        

@receiver(pre_delete, sender=Schedule)
def handle_shedule_deletion(sender, instance, **kwargs):
    """
    при удалении занятия обнуляем связи в посещаемости и оценках (согдасно ТЗ данные не удаляются, но теряют привязку к дате).
    """
    instance.attendances.update(shedule=None)
    instance.grades.uodate(shedule=None)

@receiver(pre_delete, sender=Student)
def anonymize_student_before_delete(sender, instance, **kwargs):
    """
    Обезличивание персональных данных ученика перед удалением (ФЗ-152).
    Вместо реального удаления переопределим метод delete в модели.
    Этот сигнал только для дополнительной логики, но реальное удаление блокируем.
    """
    # Помечаем как удалённого и сохраняем обезличенные данные
    instance.last_name = f"Deleted_{instance.id}"
    instance.first_name = "Anonymous"
    instance.patronymic = ""
    instance.phone = f"0{instance.id}"
    instance.email = f"deleted_{instance.id}@example.com"
    instance.status = 'expelled'
    instance.save()
    # Чтобы объект не удалился физически, можно вызвать исключение,
    # но лучше переопределить delete() в модели (см. модель Student)
    raise Exception("Ученик обезличен, физическое удаление отменено. Используйте мягкое удаление.")
