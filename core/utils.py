from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone


def check_teacher_workload(
    teacher,
    date,
    start_time,
    end_time,
    exclude_shedule_id=None
):
    """
    Провкряет, не превысит ли преподаватель максимальную недельную нагрузку. Возвращает True, если нагрузка допустима. Иначе - False.
    """
    # определяем неделю (пн - вс)
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    shedules = teacher.shedules.filter(date__gte=week_start, date__lte=week_end)
    if exclude_shedule_id:
        schedules = shedules.exclude(id=exclude_shedule_id)
    
    # суммируем длительность занятий в часах
    total_hours = 0
    for sh in schedules:
        duration = (sh.end_time.hour + sh.end_time.minute/60) - (sh.start_time.hour + sh.start_time.minute/60)
        total_hours += duration
    
    # длительность нового занятия
    new_duration = (end_time.hour + end_time.minute/60) - (start_time.hour + start_time.minute/60)
    return (total_hours + new_duration) <= teacher.max_weekly_hours

def get_available_groups_for_direction(direction):
    """
    Возвращает QuerySet групп направления, которые езё не заполнены и находятся в статусе "formong".
    """
    from .models import Group # локальный импорт для избежания циклических ссылок
    groups = Group.objects.filter(direction=direction, status='forming')
    available = []
    for group in groups:
        max_students = 12 if group.study_form == 'fulltime' else 15
        if group.students.count() < max_students:
            available.append(group)
    return available
