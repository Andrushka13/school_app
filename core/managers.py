from django.db import models


class ActiveTeacherManager(models.Manager):
    """Менеджер для получения только работающих преподавателей"""
    def get_queryset(self):
        return super().get_queryset().filter(status='active')
    

class ActiveStudentManager(models.Manager):
    """Менеджер для получения только работающих преподавателей"""
    def get_queryset(self):
        return super().get_queryset().filter(status='studiyng')
