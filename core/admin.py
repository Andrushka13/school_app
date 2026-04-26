from django.contrib import admin
from .models import (
    Position, Contract, ControlForm, Direction, Teacher, Student, Group, Subject, StudyPlan, Shedule, Attendance, Grade, EnrollmentRequest,
)
# Register your models here.
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ControlForm)
class ControlFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status')
    list_filter = ('status',)
    search_fields = ('name',)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'contract_number', 'conclusion_date')
    search_fields = ('contract_number',)
    raw_id_fields = ('student',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'phone', 'email', 'status', 'max_weekly_hours')
    list_filter = ('status', 'position')
    search_fields = ('last_name', 'first_name', 'email' 'phone')
    readonly_fields = ('hire_date',)
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'phone', 'email', 'status', 'group')
    list_filter = ('status', 'group')
    search_fields = ('last_name', 'first_name', 'phone', 'email')
    raw_id_fields = ('group',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'direction', 'study_form', 'start_date', 'end_date', 'status')
    list_filter = ('study_form', 'status', 'direction')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'direction', 'hours','control_form', 'description')
    list_filter = ('control_form', 'direction')
    search_fields = ('name',)

@admin.register(StudyPlan)
class StudyPlan(admin.ModelAdmin):
    list_display = ('id', 'group', 'subject', 'teacher')
    list_filter = ('group', 'subject')
    raw_id_fields = ('group', 'subject', 'teacher')

@admin.register(Shedule)
class SheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'start_time', 'end_time', 'group', 'subject', 'teacher', 'format')
    list_filter = ('format', 'date', 'group')
    raw_id_fields = ('group', 'subject', 'teacher')
    search_fields = ('classroom', 'video_link')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'shedule', 'student', 'is_present')
    list_filter = ('is_present',)
    raw_id_fields = ('shedule', 'student')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'score', 'control_type', 'date')
    list_filter = ('control_type', 'subject')
    raw_id_fields = ('student', 'subject', 'group', 'shedule')

@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'phone', 'email', 'direction', 'status')
    list_filter = ('direction', 'status')
    search_fields = ('last_name', 'first_name', 'email', 'phone')
